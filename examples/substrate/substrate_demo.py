"""
substrate_demo.py — conservation across coefficient substrates
==============================================================

A. The substrate spectrum: the SAME data, read over Q, over Z (torsion), and
   over several F_p — tied together by one identity.
B. Parametric conservation over Q[t]: laws as a function of a parameter, and
   the exact parameter values where conservation degenerates.

Run:  python substrate_demo.py
"""

from fractions import Fraction

import sys as _sys
from pathlib import Path as _Path
for _root in _Path(__file__).resolve().parents:
    if (_root / "numeric_rule_finder").is_dir():
        _sys.path.insert(0, str(_root)); break

from numeric_rule_finder import euclidean as E
from numeric_rule_finder.generic_linalg import nullspace_field
from numeric_rule_finder.substrate import substrate_spectrum, parametric_conservation, poly
from numeric_rule_finder import datasets as D


def part_a_spectrum():
    print("#" * 70)
    print("# A. THE SUBSTRATE SPECTRUM  (Q  vs  Z-torsion  vs  F_p)")
    print("#" * 70)
    print("\nidentity:  dim_Fp = dim_Q + #{ torsion factors divisible by p }\n")
    primes = [2, 3, 5]
    header = f"  {'dataset':20s} {'Q':>3} {'torsion':>14}  " + "  ".join(f"F{p}" for p in primes)
    print(header)
    for make in (D.parity_pairs, D.crt_mod6, D.michaelis_menten,
                 D.inventory_two_skus, D.ledger_two_books):
        d = make()
        sp = substrate_spectrum(d["records"], primes, d["entity_key"],
                                d["event_key"], d["qty_key"])
        fps = "  ".join(f"{sp.per_prime[p]:>2}" for p in primes)
        flag = "OK" if sp.identity_holds else "FAIL"
        print(f"  {d['name']:20s} {sp.q_dim:>3} {str(sp.torsion):>14}  {fps}   [{flag}]")
    print("\n  parity_pairs: 0 over Q, but F_2 sees the two parities.")
    print("  crt_mod6:     Z/6 torsion splits as one law over F_2 and one over F_3.")
    print("  ledger_two_books: torsion also reflects the amount magnitudes")
    print("                    (lattice index), so F_p jumps at p | amounts.")


def _eval(cell, value):
    """Evaluate a Q[t] polynomial (coeff tuple) at t = value."""
    return sum((c * value ** i for i, c in enumerate(cell)), Fraction(0))


def _qq_conservation_dim(poly_incidence, value, ne):
    """Conservation dimension over Q after substituting t = value."""
    M = [[_eval(cell, value) for cell in row] for row in poly_incidence]
    ST = [[M[i][j] for i in range(len(M))] for j in range(len(M[0]))]  # transpose
    return len(nullspace_field(ST, ne, E.QQ))


def part_b_parametric():
    print("\n" + "#" * 70)
    print("# B. PARAMETRIC CONSERVATION over Q[t]")
    print("#" * 70)
    print("\nTwo coupled flows with tunable coupling t:")
    print("   e1: a += 1, b += -t      e2: a += t, b += -1")
    ents, evs = ["a", "b"], ["e1", "e2"]
    M = [[poly(1), poly(0, 1)],
         [poly(0, -1), poly(-1)]]
    res = parametric_conservation(ents, evs, M)
    print(res.render())

    print("\n  confirm by substitution (conservation dim over Q at fixed t):")
    for tval in (Fraction(0), Fraction(2), Fraction(1), Fraction(-1)):
        dim = _qq_conservation_dim(M, tval, len(ents))
        tag = "  <- degenerate (extra law)" if dim > res.generic_laws else ""
        print(f"    t = {tval}:  {dim} law(s){tag}")


if __name__ == "__main__":
    part_a_spectrum()
    part_b_parametric()
    print("\nDone.")
