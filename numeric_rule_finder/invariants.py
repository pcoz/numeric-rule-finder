"""
invariants.py — null-space conservation-law discovery
=====================================================

The kernel under CBRC's "fold" is an *additive invariant*: a weighting of
entities whose total is unchanged by every event. CBRC makes the human
*declare* that invariant (the value_key that "should sum to zero per group").
This module *discovers* the complete lattice of such invariants from the data
itself, and types the residual of dirty data per-law.

The maths (all exact — Fraction/int, never float):

    Build the incidence matrix  S : entities x events,
        S[e][v] = net change of entity e caused by event v.
    A conservation law is a vector y over entities with  y^T S = 0
    (every event leaves the weighted total  sum_e y[e]*level[e]  unchanged).
    The set of laws is therefore the LEFT NULL SPACE of S  =  null(S^T).

This is exactly:
  * Petri-net P-invariants (left null space of the incidence matrix),
  * conserved moieties in a reaction network (left null space of the
    stoichiometric matrix),
  * Kirchhoff/flow conservation on a graph.

Two outputs:
  * `n_laws` = dim of the conservation space  = the number of *independent*
    conservation laws. This is the honest, order-independent "how much
    structure?" number. Zero -> honest stop (no conservation structure).
  * `minimal_semipositive` = the interpretable nonnegative invariants
    (the Farkas P-invariants): "this nonnegative combination of stocks is
    conserved", e.g.  E + ES  and  S + ES + P  in Michaelis-Menten.

Pure standard library. Feed it a list of dicts (e.g. csv.DictReader).
"""

from __future__ import annotations
from fractions import Fraction
from functools import reduce
from math import gcd, lcm
from collections import defaultdict
from dataclasses import dataclass, field


# ---------- build the incidence (stoichiometric) matrix -------------------

def build_incidence(records, entity_key, event_key, qty_key):
    """S[e][v] = net change of entity e by event v (summed over records).

    Returns (entities, events, S) where entities/events are sorted lists and
    S is a dict-of-dict of Fraction. Exact: qty is parsed via Fraction(str(.))
    so decimal strings like "100.00" stay exact (no binary-float drift).
    """
    entities, events = set(), set()
    S = defaultdict(lambda: defaultdict(Fraction))
    for r in records:
        e, v = r[entity_key], r[event_key]
        S[e][v] += Fraction(str(r[qty_key]))
        entities.add(e)
        events.add(v)
    return sorted(entities, key=str), sorted(events, key=str), S


# ---------- exact rational linear algebra ---------------------------------

def _rref(matrix):
    """Reduced row echelon form over Q. Returns (rref_rows, pivot_columns)."""
    M = [row[:] for row in matrix]
    n_rows = len(M)
    n_cols = len(M[0]) if M else 0
    pivots = []
    r = 0
    for c in range(n_cols):
        piv = next((i for i in range(r, n_rows) if M[i][c] != 0), None)
        if piv is None:
            continue
        M[r], M[piv] = M[piv], M[r]
        inv = M[r][c]
        M[r] = [x / inv for x in M[r]]
        for i in range(n_rows):
            if i != r and M[i][c] != 0:
                f = M[i][c]
                M[i] = [a - f * b for a, b in zip(M[i], M[r])]
        pivots.append(c)
        r += 1
        if r == n_rows:
            break
    return M, pivots


def _nullspace(matrix, n_cols):
    """Basis (list of Fraction vectors) for {x in Q^n_cols : matrix x = 0}."""
    if not matrix or all(all(x == 0 for x in row) for row in matrix):
        # zero map: the whole space is the kernel
        return [[Fraction(int(i == j)) for j in range(n_cols)] for i in range(n_cols)]
    R, pivots = _rref(matrix)
    pivot_set = set(pivots)
    free_cols = [c for c in range(n_cols) if c not in pivot_set]
    basis = []
    for f in free_cols:
        vec = [Fraction(0)] * n_cols
        vec[f] = Fraction(1)
        for row_i, pc in enumerate(pivots):
            vec[pc] = -R[row_i][f]
        basis.append(vec)
    return basis


def _integerize(vec):
    """Scale a rational vector to primitive integers, sign-normalized
    (first nonzero entry positive)."""
    L = reduce(lcm, (x.denominator for x in vec), 1)
    ints = [int(x * L) for x in vec]
    g = reduce(gcd, (abs(x) for x in ints), 0)
    if g > 1:
        ints = [x // g for x in ints]
    for x in ints:
        if x != 0:
            if x < 0:
                ints = [-y for y in ints]
            break
    return ints


# ---------- Farkas: minimal semipositive (P-)invariants -------------------

def _minimal_support(vectors):
    """Dedupe scalar multiples and drop non-minimal-support invariants."""
    normed = []
    for v in vectors:
        g = reduce(gcd, (abs(x) for x in v), 0)
        nv = tuple(x // g for x in v) if g > 1 else tuple(v)
        if nv not in normed:
            normed.append(nv)
    supports = [frozenset(i for i, x in enumerate(v) if x != 0) for v in normed]
    keep = []
    for i, v in enumerate(normed):
        # drop v if some *other* invariant has a strictly smaller support
        if any(j != i and supports[j] < supports[i] for j in range(len(normed))):
            continue
        keep.append(list(v))
    return keep


def _farkas(entities, events, S):
    """Minimal semipositive left invariants: y >= 0 (integer), y^T S = 0.

    The classical Farkas algorithm: carry [ S-row | unit-vector ] per entity;
    for each event column, keep zero rows and replace each (positive, negative)
    pair by the nonnegative combination that cancels that column. What remains
    (right block) are nonnegative invariants; keep the minimal-support ones.
    """
    ne, nv = len(entities), len(events)
    # integerize each event column (scaling a column does not change y^T S = 0)
    col_scale = [
        reduce(lcm, (S[e][v].denominator for e in entities), 1) for v in events
    ]
    rows = []
    for i, e in enumerate(entities):
        left = [int(S[e][events[j]] * col_scale[j]) for j in range(nv)]
        right = [1 if k == i else 0 for k in range(ne)]
        rows.append(left + right)

    for t in range(nv):
        nxt = [row for row in rows if row[t] == 0]
        pos = [row for row in rows if row[t] > 0]
        neg = [row for row in rows if row[t] < 0]
        for rp in pos:
            for rn in neg:
                a, b = rp[t], -rn[t]            # both > 0
                g = gcd(a, b)
                a2, b2 = a // g, b // g
                comb = [b2 * x + a2 * y for x, y in zip(rp, rn)]  # zeroes col t
                gg = reduce(gcd, (abs(x) for x in comb), 0)
                if gg > 1:
                    comb = [x // gg for x in comb]
                nxt.append(comb)
        rows = nxt

    invariants = [row[nv:] for row in rows if any(x != 0 for x in row[nv:])]
    out = []
    for right in _minimal_support(invariants):
        coeffs = {entities[i]: right[i] for i in range(ne) if right[i] != 0}
        out.append(ConservationLaw(coeffs, all(x >= 0 for x in right)))
    return out


# ---------- result types --------------------------------------------------

@dataclass
class ConservationLaw:
    coeffs: dict           # entity -> integer weight (nonzero entries only)
    semipositive: bool

    def render(self):
        parts = []
        for e in sorted(self.coeffs, key=str):
            w = self.coeffs[e]
            if w == 1:
                parts.append(f"{e}")
            elif w == -1:
                parts.append(f"-{e}")
            else:
                parts.append(f"{w}*{e}")
        s = " + ".join(parts).replace("+ -", "- ")
        return f"{s}  =  const"


@dataclass
class Discovery:
    entities: list
    events: list
    rank: int
    n_laws: int                       # dimension of the conservation space
    laws: list = field(default_factory=list)            # rational basis (integerized)
    minimal_semipositive: list = field(default_factory=list)  # Farkas P-invariants

    @property
    def honest_stop(self):
        return self.n_laws == 0


# ---------- the discovery entry point -------------------------------------

def discover_invariants(records, entity_key, event_key, qty_key):
    """Discover every independent conservation law in the data.

    Returns a Discovery. `n_laws` is the authoritative count (dim of the
    left null space). `minimal_semipositive` are the interpretable Farkas
    P-invariants. `honest_stop` is True iff there is no conservation
    structure at all (n_laws == 0).
    """
    entities, events, S = build_incidence(records, entity_key, event_key, qty_key)
    ne = len(entities)
    # left null space of S = null space of S^T (rows = events, cols = entities)
    ST = [[S[e][v] for e in entities] for v in events]
    basis = _nullspace(ST, ne)

    laws = []
    for vec in basis:
        ints = _integerize(vec)
        coeffs = {entities[i]: ints[i] for i in range(ne) if ints[i] != 0}
        semipos = all(x >= 0 for x in ints) or all(x <= 0 for x in ints)
        laws.append(ConservationLaw(coeffs, semipos))

    return Discovery(
        entities=entities,
        events=events,
        rank=ne - len(basis),
        n_laws=len(basis),
        laws=laws,
        minimal_semipositive=_farkas(entities, events, S),
    )


# ---------- reconciliation: type the residual per-law ---------------------

def check_conservation(records, laws, entity_key, event_key, qty_key,
                       expected=Fraction(0), tolerance=Fraction(0)):
    """Check actual data against (discovered or supplied) laws.

    For each law, returns its total residual over the whole dataset and the
    list of events that violate it (event, residual). On clean data every
    residual is 0; on dirty data the *vector* of per-law residuals says
    WHICH conservation law broke — the typed-residual upgrade over CBRC's
    single scalar.
    """
    net = defaultdict(Fraction)
    per_event = defaultdict(lambda: defaultdict(Fraction))
    for r in records:
        e, v = r[entity_key], r[event_key]
        q = Fraction(str(r[qty_key]))
        net[e] += q
        per_event[v][e] += q

    report = []
    for law in laws:
        total = sum(Fraction(w) * net.get(e, 0) for e, w in law.coeffs.items())
        violators = []
        for v, chg in per_event.items():
            val = sum(Fraction(w) * chg.get(e, 0) for e, w in law.coeffs.items())
            if abs(val - expected) > tolerance:
                violators.append((v, val))
        violators.sort(key=lambda x: abs(x[1]), reverse=True)
        report.append((law, total - expected, violators))
    return report
