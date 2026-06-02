"""
cohomology.py — type the reconciliation residual as a cohomology obstruction
============================================================================

`invariants.py` answers "what is conserved?". This module answers, for a
*specific observed imbalance*, "is this break resolvable, or is it a genuine
obstruction — and of what type?". It does so with two honest, exact (over Q),
computable cohomologies.

--------------------------------------------------------------------------
1. The conservation complex   R^events --S--> R^entities
--------------------------------------------------------------------------
S is the incidence matrix of a *reference* model (a clean period, or a Petri
net): column v = the net change of every entity when event v fires once. So

    im(S)        = the changes ACHIEVABLE by some pattern of event firings
                   ("coboundaries"),
    coker(S)     = R^entities / im(S),  and (FTLA)  coker(S) ≅ ker(S^T)
                 = the conservation laws.

Given an OBSERVED net-change vector b (from possibly-dirty data), its
**typed residual is the class  [b] ∈ coker(S)**. Concretely the coordinates
of [b] are the per-law violations  y_i^T b :

  * [b] = 0  (every y_i^T b = 0)  ⟺  b ∈ im(S)  ⟺  b is a COBOUNDARY:
        some event-flow x reproduces it (S x = b). The imbalance is
        explainable by re-attributing how often the modeled events fired —
        i.e. resolvable by a fold / regroup / correction. We return the
        witness flow x.

  * [b] ≠ 0  ⟺  b ∉ im(S)  ⟺  a genuine OBSTRUCTION: NO reconfiguration of
        the modeled events can produce b. It violates the conservation
        law(s) y_i with y_i^T b ≠ 0, by exactly that amount. This is the
        matching-boundary residual, now identified by *which* conserved
        quantity it offends and by how much.

--------------------------------------------------------------------------
2. The discrepancy sheaf   (multi-source reconciliation, genuine H^1)
--------------------------------------------------------------------------
When N ledgers are reconciled PAIRWISE — "A and B differ by d_AB on their
shared total" — the discrepancies form a 1-cochain omega on the ledger graph
(constant sheaf, R coefficients). Its class in

    H^1 = C^1 / im(delta^0)       (a graph has no C^2, so H^1 = coker delta^0)

is the obstruction to a global reconciliation:

  * [omega] = 0  ⟺  omega is a coboundary  ⟺  there exist per-ledger offsets
        p_v with d_uv = p_u - p_v for every edge: a single global correction
        (each ledger carries a fixed bias) reconciles everything.

  * [omega] ≠ 0  ⟺  some cycle of ledgers has nonzero net discrepancy
        (d_AB + d_BC + d_CA ≠ 0): NO choice of per-ledger values satisfies all
        pairwise reports simultaneously. An irreducible inconsistency — the
        true matching boundary of multi-source reconciliation. The nonzero
        defects are the coordinates of [omega] in a fundamental-cycle basis.

Everything is exact rational arithmetic; no floats, no evalf.
"""

from __future__ import annotations
from fractions import Fraction
from collections import defaultdict, deque
from dataclasses import dataclass, field

from .invariants import (
    build_incidence, discover_invariants, _rref, ConservationLaw,
)


# ======================================================================
# 1. conservation complex: residual as a class in coker(S)
# ======================================================================

def _solve(A, b):
    """A particular solution x of A x = b over Q, or None if inconsistent.

    A: m x n list of Fraction rows; b: length-m list of Fraction.
    """
    m = len(A)
    n = len(A[0]) if A else 0
    aug = [list(A[i]) + [b[i]] for i in range(m)]
    R, pivots = _rref(aug)
    if n in pivots:            # a pivot in the RHS column => 0 = 1 => no solution
        return None
    x = [Fraction(0)] * n
    for row_i, pc in enumerate(pivots):
        if pc < n:
            x[pc] = R[row_i][n]   # free vars = 0, so pivot var = reduced RHS
    return x


@dataclass
class TypedResidual:
    observed: dict                 # entity -> observed net change b[e]
    coordinates: list              # [(law, y^T b)] -- coords of [b] in coker S
    is_coboundary: bool            # True: b in im(S) -> resolvable by event reconfiguration
    witness_flow: dict | None      # event -> net firings x with S x = b (when coboundary)
    obstruction: list = field(default_factory=list)  # [(law, value)] for nonzero coords

    def render(self):
        if self.is_coboundary:
            flow = ", ".join(f"{v} x {ev}" for ev, v in self.witness_flow.items() if v != 0)
            return ("RESOLVABLE (coboundary, [b]=0): explainable by the event-flow "
                    f"[{flow or 'none'}] -- a fold/regroup/correction can absorb it; "
                    "no conservation law is violated.")
        parts = "; ".join(f"{law.render().replace('  =  const','')} off by {val}"
                          for law, val in self.obstruction)
        return ("OBSTRUCTION (nonzero class in coker S): no event reconfiguration "
                f"explains it. Violated conserved quantities -- {parts}. "
                "This is a true matching-boundary residual.")


@dataclass
class ConservationComplex:
    """The reference two-term complex R^events --S--> R^entities."""
    entities: list
    events: list
    S: dict                        # S[entity][event] -> Fraction
    laws: list                     # ConservationLaw (basis of coker S)

    @classmethod
    def from_records(cls, records, entity_key, event_key, qty_key):
        entities, events, S = build_incidence(records, entity_key, event_key, qty_key)
        disc = discover_invariants(records, entity_key, event_key, qty_key)
        return cls(entities, events, S, disc.laws)

    @classmethod
    def from_petrinet(cls, net):
        from .petra_adapter import incidence_records
        recs = incidence_records(net)
        return cls.from_records(recs, "place", "transition", "delta")

    def _matrix(self):
        return [[self.S[e][v] for v in self.events] for e in self.entities]

    def type_observation(self, observed):
        """Type an observed net-change vector b (dict entity -> value)."""
        b = {e: Fraction(str(observed.get(e, 0))) for e in self.entities}
        coords = []
        for law in self.laws:
            coords.append((law, sum(Fraction(w) * b[e] for e, w in law.coeffs.items())))
        is_cob = all(v == 0 for _, v in coords)
        witness = None
        if is_cob:
            A = self._matrix()
            rhs = [b[e] for e in self.entities]
            x = _solve(A, rhs)
            if x is not None:
                witness = {self.events[j]: x[j] for j in range(len(self.events))
                           if x[j] != 0}
                if not witness:
                    witness = {}
        obstruction = [(law, v) for law, v in coords if v != 0]
        return TypedResidual(b, coords, is_cob, witness, obstruction)

    def type_records(self, records, entity_key, event_key, qty_key):
        """Compute the observed net change from records, then type it."""
        net = defaultdict(Fraction)
        for r in records:
            net[r[entity_key]] += Fraction(str(r[qty_key]))
        return self.type_observation(dict(net))


# ======================================================================
# 2. discrepancy sheaf: pairwise reconciliation as an H^1 obstruction
# ======================================================================

@dataclass
class DiscrepancyCohomology:
    consistent: bool               # True: [omega] = 0 (a global reconciliation exists)
    offsets: dict | None           # ledger -> bias p_v reconciling all edges (when consistent)
    cycle_rank: int                # dim H^1 of the discrepancy graph (= #edges - #verts + #comps)
    obstruction: list = field(default_factory=list)  # [((u,v), defect)] nonzero cycle coords

    def render(self):
        if self.consistent:
            biases = ", ".join(f"{v}={p}" for v, p in sorted(self.offsets.items()))
            return ("RECONCILABLE ([omega]=0 in H^1): pairwise discrepancies are a "
                    f"coboundary. Per-ledger offsets reconcile everything -- {biases}.")
        defs = "; ".join(f"cycle through {u}-{v}: net {d}" for (u, v), d in self.obstruction)
        return (f"IRREDUCIBLE ([omega]!=0 in H^1, dim {self.cycle_rank}): the discrepancies "
                f"do not close around a cycle -- {defs}. No per-ledger correction reconciles "
                "them; this is the matching boundary.")


def discrepancy_cohomology(diffs):
    """Type a set of pairwise discrepancies by the class of omega in H^1.

    diffs: dict {(u, v): value}, meaning the reconciliation report
    "value(u) - value(v) = value" on u and v's shared quantity.
    """
    edges = [(u, v, Fraction(str(w))) for (u, v), w in diffs.items()]
    verts = set()
    for u, v, _ in edges:
        verts.add(u)
        verts.add(v)
    adj = defaultdict(list)
    for ei, (u, v, w) in enumerate(edges):
        adj[u].append((v, w, ei, +1))   # oriented u->v: omega = p[u]-p[v] = w
        adj[v].append((u, w, ei, -1))

    pot = {}
    tree = [False] * len(edges)
    comps = 0
    for s in verts:
        if s in pot:
            continue
        comps += 1
        pot[s] = Fraction(0)
        dq = deque([s])
        while dq:
            x = dq.popleft()
            for (y, w, ei, sign) in adj[x]:
                if y not in pot:
                    # tree edge: enforce p[u]-p[v] = w
                    pot[y] = pot[x] - w if sign == +1 else pot[x] + w
                    tree[ei] = True
                    dq.append(y)

    obstruction = []
    for ei, (u, v, w) in enumerate(edges):
        if not tree[ei]:
            defect = w - (pot[u] - pot[v])
            if defect != 0:
                obstruction.append(((u, v), defect))

    cycle_rank = len(edges) - len(verts) + comps
    consistent = not obstruction
    return DiscrepancyCohomology(
        consistent=consistent,
        offsets=(pot if consistent else None),
        cycle_rank=cycle_rank,
        obstruction=obstruction,
    )
