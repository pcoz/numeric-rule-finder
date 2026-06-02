"""
substrate.py — conservation over many coefficient substrates
============================================================

Built on the Euclidean-domain engine (`generic_linalg.py`), this exposes
conservation discovery over:

  * a finite field F_p       -> `conservation_mod_p` : mod-p linear laws,
  * the rationals Q          -> the additive baseline (for comparison),
  * the polynomial ring Q[t] -> `parametric_conservation` : laws as a function
                                of a parameter t, with the exact parameter
                                values where conservation degenerates.

It also verifies the cross-substrate identity tying the three views together:

    dim_{F_p} (laws) = dim_Q (laws) + #{ torsion factors d of coker(S) : p | d }.
"""

from __future__ import annotations
from fractions import Fraction
from dataclasses import dataclass, field
from math import gcd

from . import euclidean as E
from .generic_linalg import nullspace_field, smith_normal_form, invariant_factors
from .invariants import build_incidence, discover_invariants
from .integer_invariants import integer_conservation


def _to_field(val, F):
    """Map a Fraction into the field F (identity for Q; reduce mod p for F_p)."""
    if F is E.QQ:
        return val
    num = F.from_int(val.numerator)
    den = F.from_int(val.denominator)
    if F.is_zero(den):
        raise ValueError(f"denominator {val.denominator} not invertible in {F.name}")
    return F.mul(num, F.inv(den))


def conservation_over_field(records, F, entity_key, event_key, qty_key):
    """Left null space of the incidence over a field F: the conservation laws
    valid over F. Returns (dim, laws) with laws as entity->coeff dicts."""
    entities, events, S = build_incidence(records, entity_key, event_key, qty_key)
    ne = len(entities)
    ST = [[_to_field(S[e][v], F) for e in entities] for v in events]  # events x entities
    basis = nullspace_field(ST, ne, F)
    laws = []
    for vec in basis:
        laws.append({entities[i]: vec[i] for i in range(ne) if not F.is_zero(vec[i])})
    return len(basis), laws


def conservation_mod_p(records, p, entity_key, event_key, qty_key):
    """Conservation laws over F_p (p prime)."""
    return conservation_over_field(records, E.GF(p), entity_key, event_key, qty_key)


@dataclass
class SubstrateSpectrum:
    q_dim: int                       # laws over Q
    torsion: list                    # torsion factors of coker(S) over Z
    per_prime: dict                  # p -> dim of laws over F_p
    identity_holds: bool             # the cross-substrate identity check


def substrate_spectrum(records, primes, entity_key, event_key, qty_key):
    """Compare conservation across Q, Z-torsion, and several F_p, and verify
    the identity  dim_{F_p} = dim_Q + #{torsion factors divisible by p}."""
    q_dim = discover_invariants(records, entity_key, event_key, qty_key).n_laws
    tors = integer_conservation(records, entity_key, event_key, qty_key).torsion
    per_prime, ok = {}, True
    for p in primes:
        dim_p, _ = conservation_mod_p(records, p, entity_key, event_key, qty_key)
        per_prime[p] = dim_p
        predicted = q_dim + sum(1 for d in tors if d % p == 0)
        ok = ok and (dim_p == predicted)
    return SubstrateSpectrum(q_dim, tors, per_prime, ok)


# --------------------------- parametric (Q[t]) ------------------------------

def poly(*coeffs):
    """Build a Q[t] element from low->high integer/Fraction coefficients."""
    return E.QQPoly._trim(tuple(Fraction(c) for c in coeffs))


def _rational_roots(p_coeffs):
    """Rational roots of a Q[t] polynomial via the rational-root theorem."""
    coeffs = list(p_coeffs)
    if not coeffs:
        return []
    # clear denominators to integers
    L = 1
    for c in coeffs:
        L = L * c.denominator // gcd(L, c.denominator)
    ic = [int(c * L) for c in coeffs]
    while ic and ic[0] == 0:               # factor out t (root 0)
        ic.pop(0)
    roots = set()
    if len(p_coeffs) and p_coeffs[0] == 0:
        roots.add(Fraction(0))
    if len(ic) >= 2:
        a0, an = ic[0], ic[-1]
        def divisors(n):
            n = abs(n)
            return [d for d in range(1, n + 1) if n % d == 0] or [1]
        for pnum in divisors(a0):
            for qden in divisors(an):
                for cand in (Fraction(pnum, qden), Fraction(-pnum, qden)):
                    val = sum(c * cand**i for i, c in enumerate(ic))
                    if val == 0:
                        roots.add(cand)
    return sorted(roots)


@dataclass
class ParametricResult:
    entities: list
    events: list
    generic_laws: int                # conservation laws holding for ALL t (over Q(t))
    degeneracy_factors: list         # non-unit invariant-factor polynomials (Q[t] tuples)
    degeneracy_values: list          # rational t where conservation rank drops (extra laws)

    def render(self):
        lines = [f"  generic conservation laws (all t): {self.generic_laws}"]
        for f in self.degeneracy_factors:
            lines.append(f"  rank drops on the locus {E.QQPoly.to_str(f)} = 0")
        if self.degeneracy_values:
            vals = ", ".join(f"t={v}" for v in self.degeneracy_values)
            lines.append(f"  => extra conservation appears at: {vals}")
        else:
            lines.append("  => no rational degeneracy values")
        return "\n".join(lines)


def parametric_conservation(entities, events, poly_incidence):
    """Conservation of a parameter-dependent system. `poly_incidence` is the
    entities x events matrix with Q[t] entries (S[e][v] = net change of e by v,
    as a polynomial in t). Computes the generic law count and the parameter
    values where conservation degenerates (rank drops)."""
    S, U, V = smith_normal_form(poly_incidence, E.QQPoly)
    facs = invariant_factors(S, E.QQPoly)
    ne = len(entities)
    generic = ne - len(facs)                 # nonzero invariant factors all invertible in Q(t)
    deg_factors = [f for f in facs if len(f) > 1]   # degree >= 1 -> a real locus
    values = sorted(set(r for f in deg_factors for r in _rational_roots(f)))
    return ParametricResult(entities, events, generic, deg_factors, values)
