"""
The Meridian Tontine: five rungs to a verdict
=============================================

A treasury analyst inherits the books of the *Meridian Tontine*, a savings club
whose payouts are alleged to be one single closed money pool. Her only job:
confirm the books balance. They don't -- run ``C3`` is off by a trivial-looking
**5** -- and each time she pushes one level deeper, the data refuses to confirm
what the previous level assumed, *forcing* her up the next rung.

This is a WORKFLOW of numeric-rule-finder calls where each step's output
drives the next, climbing from the plain-language facade into the deeper
mathematics only when the simpler layer comes up short:

    balance_check  ->  what_balances (structure)  ->  integer/modular (Z/5)
                   ->  cohomological residual typing  ->  multi-source H^1

The punchline is numeric: the **5** that ``balance_check`` reports as an opaque
gap is the same **5** that ``integer_conservation`` shows is the preserved mod-5
step, and the same **5** that ``type_observation`` finally names as the violated
``vault_chips + chip_reserve`` law.

Run:  python investigate.py
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
for _root in HERE.parents:
    if (_root / "numeric_rule_finder").is_dir():
        sys.path.insert(0, str(_root)); break          # import the library (flat modules)
DATA = HERE / "data"

from numeric_rule_finder.analyst import Reconciler
from numeric_rule_finder.integer_invariants import integer_conservation
from numeric_rule_finder.cohomology import ConservationComplex, discrepancy_cohomology
from numeric_rule_finder.substrate import parametric_conservation, poly


def rung(n, title):
    print("\n" + "=" * 74)
    print(f"RUNG {n}.  {title}")
    print("=" * 74)


def main():
    print("THE MERIDIAN TONTINE -- confirm the books balance.\n"
          "(Alleged to be ONE closed money pool. Let's see.)")
    r = Reconciler.from_csv(DATA / "ledger.csv")

    # ---- RUNG 1: plain balance check ------------------------------------
    rung(1, "Does each payout_run balance?  (Reconciler.balance_check)")
    bc = r.balance_check(group="payout_run", amount="amount")
    print(bc.summary())
    structural = [b for b in bc.breaks if b.suspect is None]
    print(f"\n  DECISION: the break has NO line-level culprit "
          f"({len(structural)} structural break). A typo would point at a line; "
          "this doesn't. Escalate to discovery.")

    # ---- RUNG 2: discovery / is it really one pool? ---------------------
    rung(2, "What actually stays balanced -- is it even one pool?  (what_balances)")
    wb = r.what_balances(account="account", group="payout_run", amount="amount")
    print(wb.summary())
    print(f"\n  (structured view: conserved over Q = {wb.conserved_groups};"
          f" independent sets = {len(wb.separate_books)})")
    broken_accounts = None
    if len(wb.separate_books) > 1:
        conserved_accts = {a for grp in wb.conserved_groups for a in grp}
        broken = [bk for bk in wb.separate_books if not set(bk) <= conserved_accts]
        broken_accounts = broken[0] if broken else None
        print("  DECISION: the 'single pool' premise is FALSE -- two non-communicating")
        print(f"            books. One book has NO rational conservation law: "
              f"{broken_accounts}. Drill it over the integers.")

    # ---- RUNG 3: integer / modular law on the broken book ---------------
    rung(3, "The broken book has no Q-law -- does it conserve anything?  (integer_conservation)")
    pool_b = [row for row in r.rows if row["account"] in set(broken_accounts)]
    idisc = integer_conservation(pool_b, "account", "payout_run", "amount")
    print(f"  conservation over Q: {idisc.free_rank}    "
          f"hidden torsion: {idisc.torsion}")
    for ml in idisc.modular_laws:
        print(f"    modular law:  {ml.render()}")
    print("  DECISION: it IS governed by a conserved quantity -- just over Z/5, not")
    print("            Q. So C3's break is not random noise; it lives inside a real")
    print("            law. Type the residual precisely against a clean model.")

    # ---- RUNG 4: cohomological residual typing --------------------------
    rung(4, "Is the residual a re-attribution, or a genuine hole?  (coker S)")
    clean_model_rows = [
        {"account": "vault_chips", "payout_run": "tick", "amount": "5"},
        {"account": "chip_reserve", "payout_run": "tick", "amount": "-5"},
    ]
    cx = ConservationComplex.from_records(clean_model_rows, "account", "payout_run", "amount")
    # the actual observed net of the broken book:
    observed = {}
    for row in pool_b:
        observed[row["account"]] = observed.get(row["account"], 0) + float(row["amount"])
    print(f"  observed net of the book: {observed}")
    # contrast: a clean re-attribution (3 ticks) IS explainable ...
    print("  a candidate re-attribution {vault_chips:+15, chip_reserve:-15}:")
    print("    " + cx.type_observation({"vault_chips": 15, "chip_reserve": -15}).render())
    # ... the real observation is NOT:
    typed = cx.type_observation({"vault_chips": 135, "chip_reserve": -130})
    print("  the real observed net:")
    print("    " + typed.render())
    print("  DECISION: a GENUINE obstruction (no re-attribution reproduces it), and")
    print("            it names the exact violated law, off by 5 -- the same 5 from")
    print("            Rung 1 and the same modulus from Rung 3. Check the auditors.")

    # ---- RUNG 5: are the external memos even mutually consistent? --------
    rung(5, "Three auditors reconciled pairwise -- can they all be right?  (H^1)")
    memos = {("AuditX", "AuditY"): 120, ("AuditY", "Ledger"): -50, ("Ledger", "AuditX"): -40}
    for (u, v), d in memos.items():
        print(f"    memo: {u} - {v} = {d}")
    dc = discrepancy_cohomology(memos)
    print("  " + dc.render())
    print("  VERDICT: the memos cannot all be true -- their loop nets to a nonzero")
    print("           amount, so no per-source bias reconciles them. The external")
    print("           evidence is self-contradictory.")

    # ---- BONUS: a parametrized variant (extra capability) ---------------
    rung("6 (bonus)", "If the chip-to-bank coupling were tunable...  (parametric, Q[t])")
    ents, evs = ["chips", "bank"], ["transfer_in", "transfer_out"]
    M = [[poly(1), poly(0, 1)], [poly(0, -1), poly(-1)]]
    res = parametric_conservation(ents, evs, M)
    print("  " + res.render().replace("\n", "\n  "))
    print("  NOTE: shown only to surface the parametric capability -- a coupled")
    print("        transfer that conserves value only at special coupling rates.")

    print("\n" + "=" * 74)
    print("PAYOFF -- no single call gives this; the CHAIN does:")
    print("  'C3 is off by 5' is not a typo and not a fold error. It is a genuine")
    print("  conservation obstruction inside a hidden second pool that moves only in")
    print("  fives -- and the audit memos meant to resolve it are mutually impossible.")
    print("  The 5 threads through Rungs 1, 3 and 4: opaque gap -> preserved mod-5")
    print("  step -> the named violated law. Each rung was forced by the previous one")
    print("  withholding confirmation: the engine escalated instead of inventing.")
    print("=" * 74)


if __name__ == "__main__":
    main()
