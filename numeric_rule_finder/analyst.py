"""
analyst.py — the plain-language front door
==========================================

You have a table: rows of line items, each with a *group* it belongs to (a
transaction id, an order number, a batch), a signed *amount*, and usually an
*account* / category. You want to know three things, in plain English:

  1. "Does each group balance — and if not, where and why?"      -> .balance_check
  2. "What actually stays balanced across all my data, and are
      there hidden separate books I didn't know about?"          -> .what_balances
  3. "Do these two reports/systems agree?"                       -> .compare

No matrices, no jargon. Feed it a CSV path or a list of dict rows:

    from .analyst import Reconciler
    r = Reconciler.from_csv("ledger.csv")
    print(r.report(group="txn_id", amount="amount", account="account"))

Everything is exact (no rounding surprises) and it tells you honestly when your
data has nothing to balance, instead of inventing an answer. The heavy
mathematics lives in the other modules; you never have to touch it.
"""

from __future__ import annotations
import csv
from collections import defaultdict
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from fractions import Fraction


# --------------------------------------------------------------------------
# loading
# --------------------------------------------------------------------------

def _num(x):
    """Parse a money/amount cell exactly. Returns a Fraction or None."""
    if x is None:
        return None
    if isinstance(x, (int, float, Decimal, Fraction)):
        return Fraction(str(x))
    s = str(x).strip().replace(",", "").replace("$", "").replace("£", "")
    if s in ("", "-", "—"):
        return None
    if s.startswith("(") and s.endswith(")"):       # accounting negatives
        s = "-" + s[1:-1]
    try:
        return Fraction(s)
    except (InvalidOperation, ValueError, ZeroDivisionError):
        return None


def _money(frac):
    """Render a Fraction as a tidy decimal string for humans."""
    if frac == int(frac):
        return str(int(frac))
    return str(round(float(frac), 4))


# --------------------------------------------------------------------------
# reports
# --------------------------------------------------------------------------

@dataclass
class Break:
    group: object
    off_by: Fraction
    hint: str
    suspect: dict | None = None


@dataclass
class BalanceReport:
    group_col: str
    amount_col: str
    n_groups: int
    breaks: list = field(default_factory=list)

    @property
    def all_balanced(self):
        return not self.breaks

    def summary(self):
        if self.all_balanced:
            return (f"All {self.n_groups} {self.group_col}(s) balance. "
                    f"Every group's {self.amount_col} adds up to zero.")
        lines = [f"{len(self.breaks)} of {self.n_groups} {self.group_col}(s) "
                 f"do NOT balance:"]
        for b in self.breaks:
            lines.append(f"  - {self.group_col} {b.group!r} is off by {_money(b.off_by)}.")
            lines.append(f"      likely: {b.hint}")
            if b.suspect is not None:
                lines.append(f"      look at: {b.suspect}")
        return "\n".join(lines)


@dataclass
class Diagnosis:
    group: object
    off_by: Fraction
    verdict: str          # "shortfall" | "reattribution" | "review"
    book: list            # accounts of the violated relationship
    message: str
    action: str


@dataclass
class DiagnoseReport:
    items: list = field(default_factory=list)

    def summary(self):
        if not self.items:
            return "Nothing to diagnose -- everything balances."
        lines = []
        for d in self.items:
            lines.append(f"  - {d.group!r} (off by {_money(d.off_by)}): {d.message}")
            lines.append(f"      ACTION: {d.action}")
        return "\n".join(lines)


@dataclass
class DiscoveryReport:
    group_col: str
    amount_col: str
    account_col: str
    all_accounts_balance: bool         # one relationship ties ALL accounts to zero
    conserved_groups: list             # list of (list-of-accounts) that net to zero together
    separate_books: list               # list of account-sets that never share a group
    honest_stop: bool
    modular_findings: list = field(default_factory=list)   # hidden mod-N structure (auto-escalated)

    def summary(self):
        if self.honest_stop:
            return ("I could not find any quantity that should stay balanced in "
                    f"this data: across the {self.account_col}s, nothing reliably "
                    f"nets out per {self.group_col} -- not even in modular "
                    "arithmetic. That usually means you picked the wrong "
                    "amount/group columns, or this data simply has no balancing "
                    "structure to check. (Nothing was invented.)")
        if self.modular_findings:
            lines = ["Nothing stays EXACTLY balanced here -- but ordinary "
                     "balancing would miss this, so I looked deeper and found "
                     "hidden modular structure:"]
            for f in self.modular_findings:
                lines.append(f"  - {f}")
            return "\n".join(lines)
        lines = []
        if len(self.separate_books) > 1:
            lines.append(f"Heads up: your {self.account_col}s split into "
                         f"{len(self.separate_books)} INDEPENDENT sets that never "
                         f"share a {self.group_col} -- an entry in one can never "
                         f"offset an entry in another (separate books / pools / "
                         f"sub-systems):")
            for i, book in enumerate(self.separate_books, 1):
                lines.append(f"  set {i}: {', '.join(map(str, book))}")
        elif self.all_accounts_balance:
            lines.append(f"All your {self.account_col}s net to zero together in "
                         f"every {self.group_col} -- one closed, fully balanced system.")
        if self.conserved_groups and len(self.separate_books) <= 1 \
                and not self.all_accounts_balance:
            lines.append("These accounts always move together (their combined "
                         f"total never changes within a {self.group_col}):")
            for grp in self.conserved_groups:
                lines.append(f"  - {', '.join(map(str, grp))}")
        return "\n".join(lines) if lines else "No notable balancing structure found."


# --------------------------------------------------------------------------
# the facade
# --------------------------------------------------------------------------

class Reconciler:
    """Plain-language reconciliation over a table of line items."""

    def __init__(self, rows):
        self.rows = [dict(r) for r in rows]

    # ---- loading ----
    @classmethod
    def from_csv(cls, path, encoding="utf-8-sig"):
        with open(path, newline="", encoding=encoding) as fh:
            return cls(list(csv.DictReader(fh)))

    @classmethod
    def from_records(cls, rows):
        return cls(rows)

    @classmethod
    def from_dataframe(cls, df):
        """Accept a pandas DataFrame (duck-typed; pandas not required)."""
        return cls(df.to_dict("records"))

    # ---- 1. does each group balance? ----
    def balance_check(self, group, amount, expected=0, tolerance="0"):
        tol = Fraction(str(tolerance))
        exp = Fraction(str(expected))
        totals, members = defaultdict(Fraction), defaultdict(list)
        seen_any = False
        for r in self.rows:
            v = _num(r.get(amount))
            if v is None:
                continue
            g = r.get(group)
            totals[g] += v
            members[g].append(r)
            seen_any = True
        breaks = []
        for g, total in totals.items():
            resid = total - exp
            if abs(resid) > tol:
                hint, suspect = self._diagnose(resid, members[g], amount)
                breaks.append(Break(g, resid, hint, suspect))
        breaks.sort(key=lambda b: abs(b.off_by), reverse=True)
        return BalanceReport(group, amount, len(totals), breaks)

    def _diagnose(self, residual, members, amount):
        vals = [(_num(m.get(amount)), m) for m in members]
        vals = [(v, m) for v, m in vals if v is not None]
        # an exact-duplicate line equal to the gap -> a duplicated entry
        seen = {}
        for v, m in vals:
            seen.setdefault(tuple(sorted(m.items())), []).append((v, m))
        for copies in seen.values():
            if len(copies) > 1 and copies[0][0] == residual:
                return ("a duplicated line (an extra copy is in here)", copies[0][1])
        for v, m in vals:
            if v == residual:
                return ("a missing counter-entry for this line", m)
            if v == -residual:
                return ("an extra line that should not be here", m)
        if residual != 0 and (residual % 10 == 0 or residual % 100 == 0):
            return ("a units / scale / sign error (the gap is a round number)", None)
        return ("no single line explains it -- worth a manual look", None)

    # ---- 2. what stays balanced, and are there hidden books? ----
    def what_balances(self, account, group, amount):
        """Find what stays balanced. INTELLIGENT: if nothing balances over
        ordinary arithmetic, it automatically escalates to integer/modular
        analysis (the deeper maths) and reports any hidden mod-N structure in
        plain words, before ever giving up."""
        from .invariants import discover_invariants
        disc = discover_invariants(self.rows, account, group, amount)

        conserved = [sorted(law.coeffs.keys(), key=str)
                     for law in (disc.minimal_semipositive or disc.laws)]
        books = self._account_components(account, group)
        all_accounts = {r.get(account) for r in self.rows if _num(r.get(amount)) is not None}
        all_balance = any(set(c) == all_accounts for c in conserved)

        modular = []
        if disc.honest_stop:
            modular = self._modular_escalation(account, group, amount)

        return DiscoveryReport(
            group_col=group, amount_col=amount, account_col=account,
            all_accounts_balance=all_balance,
            conserved_groups=conserved,
            separate_books=books,
            honest_stop=disc.honest_stop and not modular,
            modular_findings=modular,
        )

    def _modular_escalation(self, account, group, amount):
        """Nothing balanced over Q -> try integer/modular conservation (SNF
        torsion) and translate any finding into plain language."""
        try:
            from .integer_invariants import integer_conservation
            idisc = integer_conservation(self.rows, account, group, amount)
        except Exception:
            return []
        return [self._render_modular(ml, account) for ml in idisc.modular_laws]

    def _render_modular(self, law, account):
        accts = sorted(law.coeffs, key=str)
        d = law.modulus
        if len(accts) == 1 and abs(law.coeffs[accts[0]]) == 1:
            a = accts[0]
            if d == 2:
                return (f"the {account} {a!r} only ever changes by even amounts, "
                        "so its parity (odd vs even) never changes.")
            return (f"the {account} {a!r} only ever changes in steps of {d}, so "
                    f"its remainder modulo {d} is preserved.")
        combo = " + ".join((str(a) if law.coeffs[a] == 1 else f"{law.coeffs[a]}*{a}")
                           for a in accts)
        return f"the combination ({combo}) is preserved modulo {d}."

    def _account_components(self, account, group):
        """Sets of accounts that never share a group (connected components)."""
        parent = {}

        def find(x):
            parent.setdefault(x, x)
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        def union(a, b):
            parent[find(a)] = find(b)

        by_group = defaultdict(list)
        for r in self.rows:
            a = r.get(account)
            if a is not None:
                parent.setdefault(a, a)
                by_group[r.get(group)].append(a)
        for accs in by_group.values():
            for a in accs[1:]:
                union(accs[0], a)
        comps = defaultdict(list)
        for a in parent:
            comps[find(a)].append(a)
        return [sorted(v, key=str) for v in comps.values()]

    # ---- 3. do two systems agree? ----
    def compare(self, other, group, amount, tolerance="0"):
        tol = Fraction(str(tolerance))
        a = self._fold(group, amount)
        b = other._fold(group, amount)
        diffs = []
        for g in sorted(set(a) | set(b), key=str):
            if g not in a:
                diffs.append(f"{group} {g!r}: only in the second system "
                             f"(total {_money(b[g])})")
            elif g not in b:
                diffs.append(f"{group} {g!r}: only in the first system "
                             f"(total {_money(a[g])})")
            elif abs(a[g] - b[g]) > tol:
                diffs.append(f"{group} {g!r}: differ by {_money(a[g] - b[g])} "
                             f"({_money(a[g])} vs {_money(b[g])})")
        return diffs

    def _fold(self, group, amount):
        totals = defaultdict(Fraction)
        for r in self.rows:
            v = _num(r.get(amount))
            if v is not None:
                totals[r.get(group)] += v
        return totals

    # ---- 4. is a break a real shortfall, or just mis-booked? ------------
    def diagnose_breaks(self, group, amount, account):
        """For every group that doesn't balance, say in plain words whether it
        is a GENUINE shortfall (value really missing/duplicated, and in which
        relationship) or just a re-attribution that nets out once reclassified.
        Uses the groups that DO balance as the reference of 'what's normal'."""
        from .cohomology import ConservationComplex
        bc = self.balance_check(group, amount)
        if bc.all_balanced:
            return DiagnoseReport([])
        bad = {b.group for b in bc.breaks}
        clean = [r for r in self.rows if r.get(group) not in bad]
        cx = ConservationComplex.from_records(clean, account, group, amount) if clean else None
        items = []
        for b in bc.breaks:
            net = defaultdict(Fraction)
            for r in self.rows:
                if r.get(group) == b.group:
                    v = _num(r.get(amount))
                    if v is not None and r.get(account) is not None:
                        net[r.get(account)] += v
            if cx is None:
                items.append(Diagnosis(b.group, b.off_by, "review", [],
                    "no balancing entries to compare against", "review manually"))
                continue
            typed = cx.type_observation(dict(net))
            if typed.is_coboundary:
                items.append(Diagnosis(b.group, b.off_by, "reattribution", [],
                    "the pieces all exist but are booked oddly (this nets out once "
                    "re-attributed)", "reclassify between accounts; no value is "
                    "actually missing"))
            else:
                book = sorted(typed.obstruction[0][0].coeffs, key=str) if typed.obstruction else []
                items.append(Diagnosis(b.group, b.off_by, "shortfall", book,
                    f"a GENUINE shortfall in the {'/'.join(map(str, book))} balance",
                    "value is missing or duplicated -- raise a correcting journal "
                    "and investigate"))
        return DiagnoseReport(items)

    # ---- one-call narrative (self-routing across the maths) ----
    def report(self, group, amount, account=None):
        out = ["=" * 64, "RECONCILIATION REPORT", "=" * 64, ""]
        bc = self.balance_check(group, amount)
        out.append(f"1. Does each {group} balance?")
        out.append("   " + bc.summary().replace("\n", "\n   "))
        if account:
            out.append("")
            wb = self.what_balances(account, group, amount)
            out.append("2. What stays balanced across the whole dataset?")
            out.append("   " + wb.summary().replace("\n", "\n   "))
        out.append("")
        return "\n".join(out)

    analyze = report      # friendly alias


# --------------------------------------------------------------------------
# module-level conveniences
# --------------------------------------------------------------------------

def reconcile_csv(path, group, amount, account=None):
    """One-liner: load a CSV and print the full plain-language report."""
    print(Reconciler.from_csv(path).report(group=group, amount=amount, account=account))


def cross_check(pairwise):
    """Given pairwise reconciliation differences {(source_a, source_b): value},
    say in plain words whether they can ALL be right. `value` means
    'source_a's figure minus source_b's figure'."""
    from .cohomology import discrepancy_cohomology
    dc = discrepancy_cohomology(pairwise)
    if dc.consistent:
        return ("These reconciliations are mutually consistent: a single fixed "
                "offset per source explains every reported difference, so they "
                "can all be reconciled at once.")
    net = dc.obstruction[0][1] if dc.obstruction else 0
    return ("These reconciliations CANNOT all be correct: going around the loop, "
            f"the reported differences add up to {_money(abs(net))} instead of zero. "
            "No single set of corrections reconciles them -- at least one source "
            "must be re-measured.")


def account_for_movement(observed):
    """Given the NET change by location/bucket {name: net_change}, say whether
    it's fully explained by transfers between them (nothing lost) or whether
    some quantity is genuinely unaccounted for (shrinkage / loss)."""
    from .cohomology import ConservationComplex
    locs = list(observed)
    if len(locs) < 2:
        total = sum(Fraction(str(v)) for v in observed.values())
        return ("Nothing is missing." if total == 0 else
                f"{_money(abs(total))} unit(s) unaccounted for.")
    base = locs[0]
    ref_rows = []
    for i, loc in enumerate(locs[1:], 1):
        ev = f"transfer_{i}"
        ref_rows.append({"loc": base, "ev": ev, "q": -1})
        ref_rows.append({"loc": loc, "ev": ev, "q": 1})
    cx = ConservationComplex.from_records(ref_rows, "loc", "ev", "q")
    typed = cx.type_observation({k: observed[k] for k in locs})
    if typed.is_coboundary:
        return ("All of this net movement is explained by transfers between "
                "locations -- nothing is missing.")
    short = sum(Fraction(str(v)) for v in observed.values())
    return (f"{_money(abs(short))} unit(s) are UNACCOUNTED FOR -- not explained by "
            "any relocation between these locations. Likely shrinkage or loss; "
            "investigate.")
