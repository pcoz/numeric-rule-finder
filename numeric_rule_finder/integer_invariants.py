"""
integer_invariants.py — conservation laws over Z, and MODULAR laws over Z/d
===========================================================================

`invariants.py` works over Q: it finds the additive conservation laws and
honest-stops when there are none. But "none over Q" does not mean "no
structure". Consider a warehouse that only ever moves goods in cases of two:
the bin counts grow without bound (nothing is conserved over Q), yet the
**parity** of every bin is conserved forever. That is a Z/2 conservation law,
invisible to rational linear algebra.

This module recovers the full integer picture from one Smith Normal Form of
the incidence matrix S (entities × events). With U S V = D = diag(d_1..d_r):

    coker(S) = Z^entities / im(S)  ≅  Z^{entities - r}  ⊕  ⊕_i Z/d_i .

  * the FREE part (Z^{entities-r}) gives the **exact integer conservation
    laws** — rows r.. of U; their count equals the Q-dimension from
    `invariants.py` (a built-in cross-check);
  * each torsion summand **Z/d_i with d_i > 1 is a conservation law that holds
    only modulo d_i** — row i of U is a functional with  (row_i · b) ≡ 0
    (mod d_i)  for every achievable change b, but not exactly.

The torsion subgroup ⊕ Z/d_i is exactly the Smith-Normal-Form / critical-group
invariant of the incidence map: the canonical home of the modular structure.
"""

from __future__ import annotations
from dataclasses import dataclass, field

from .invariants import build_incidence, ConservationLaw, discover_invariants
from .snf import smith_normal_form, invariant_factors


@dataclass
class ModularLaw:
    modulus: int                 # d_i > 1
    coeffs: dict                 # entity -> integer weight

    def render(self):
        terms = []
        for e in sorted(self.coeffs, key=str):
            w = self.coeffs[e]
            terms.append(f"{e}" if w == 1 else (f"-{e}" if w == -1 else f"{w}*{e}"))
        body = " + ".join(terms).replace("+ -", "- ")
        return f"({body})  mod {self.modulus}  =  const"


@dataclass
class IntegerDiscovery:
    entities: list
    events: list
    invariant_factors: list           # d_1 | d_2 | ... | d_r  (the SNF diagonal)
    free_rank: int                    # # exact integer conservation laws (= Q-dim)
    exact_laws: list = field(default_factory=list)      # ConservationLaw (integer basis)
    modular_laws: list = field(default_factory=list)    # ModularLaw (the torsion)

    @property
    def torsion(self):
        """The torsion coefficients ⊕ Z/d_i (d_i > 1) of coker(S)."""
        return [d for d in self.invariant_factors if d > 1]

    @property
    def has_hidden_structure(self):
        """True iff there are modular laws but no exact ones — structure that
        is invisible over Q yet present over Z (e.g. pure parity)."""
        return bool(self.modular_laws) and self.free_rank == 0


def integer_conservation(records, entity_key, event_key, qty_key):
    """Discover exact (Z) and modular (Z/d) conservation laws via SNF."""
    entities, events, S = build_incidence(records, entity_key, event_key, qty_key)
    ne, nv = len(entities), len(events)

    A = []
    for e in entities:
        row = []
        for v in events:
            val = S[e][v]
            if val.denominator != 1:
                raise ValueError(
                    "integer conservation needs integer net changes; got "
                    f"{val} for ({e!r}, {v!r}). Scale the data to integers first.")
            row.append(int(val))
        A.append(row)

    D, U, V = smith_normal_form(A)
    factors = invariant_factors(D)
    rank = len(factors)

    exact, modular = [], []
    for i in range(ne):
        coeffs = {entities[j]: U[i][j] for j in range(ne) if U[i][j] != 0}
        if i >= rank:
            # row i annihilates im(S): an exact integer conservation law
            semipos = all(w >= 0 for w in coeffs.values()) or all(w <= 0 for w in coeffs.values())
            exact.append(ConservationLaw(coeffs, semipos))
        else:
            d = D[i][i]
            if d > 1:
                modular.append(ModularLaw(d, coeffs))

    return IntegerDiscovery(
        entities=entities,
        events=events,
        invariant_factors=factors,
        free_rank=ne - rank,
        exact_laws=exact,
        modular_laws=modular,
    )


def cross_check_free_rank(records, entity_key, event_key, qty_key):
    """The integer free rank must equal the Q-dimension from invariants.py."""
    q = discover_invariants(records, entity_key, event_key, qty_key).n_laws
    z = integer_conservation(records, entity_key, event_key, qty_key).free_rank
    return q, z, (q == z)
