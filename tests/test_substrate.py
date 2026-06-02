"""
Tests for the broadened coefficient substrate: generic SNF / null space over
Euclidean domains, F_p conservation, the cross-substrate identity, and
parametric (Q[t]) conservation.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fractions import Fraction

from numeric_rule_finder import euclidean as E
from numeric_rule_finder.generic_linalg import smith_normal_form, invariant_factors, nullspace_field
from numeric_rule_finder import substrate as S
from numeric_rule_finder import datasets as D


def test_generic_snf_matches_integer_snf():
    for A, facs in [([[2, 0], [0, 3]], [1, 6]), ([[2, 0], [0, 2]], [2, 2])]:
        Smat, U, V = smith_normal_form(A, E.ZZ)
        assert invariant_factors(Smat, E.ZZ) == facs


def test_snf_over_polynomial_ring():
    one = (Fraction(1),)
    t = (Fraction(0), Fraction(1))
    mt = (Fraction(0), Fraction(-1))
    m1 = (Fraction(-1),)
    Smat, U, V = smith_normal_form([[one, t], [mt, m1]], E.QQPoly)
    facs = invariant_factors(Smat, E.QQPoly)
    assert [E.QQPoly.to_str(f) for f in facs] == ["1", "t^2 + -1"]


def test_fp_conservation_sees_parity():
    d = D.parity_pairs()
    dim2, _ = S.conservation_mod_p(d["records"], 2, d["entity_key"], d["event_key"], d["qty_key"])
    dim3, _ = S.conservation_mod_p(d["records"], 3, d["entity_key"], d["event_key"], d["qty_key"])
    assert dim2 == 2 and dim3 == 0


def test_cross_substrate_identity():
    for make in (D.parity_pairs, D.crt_mod6, D.michaelis_menten,
                 D.ledger_two_books, D.inventory_two_skus, D.no_structure):
        d = make()
        sp = S.substrate_spectrum(d["records"], [2, 3, 5, 7],
                                  d["entity_key"], d["event_key"], d["qty_key"])
        assert sp.identity_holds, f"{d['name']} {sp.per_prime} {sp.torsion}"


def test_parametric_degeneracy_locus():
    ents, evs = ["a", "b"], ["e1", "e2"]
    M = [[S.poly(1), S.poly(0, 1)], [S.poly(0, -1), S.poly(-1)]]
    res = S.parametric_conservation(ents, evs, M)
    assert res.generic_laws == 0
    assert res.degeneracy_values == [Fraction(-1), Fraction(1)]
