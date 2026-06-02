"""
Tests for the integer/topological depth layer: SNF, modular conservation laws,
and integral homology (Betti + torsion).
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from numeric_rule_finder.snf import smith_normal_form, matmul, invariant_factors
from numeric_rule_finder.integer_invariants import integer_conservation, cross_check_free_rank
from numeric_rule_finder.homology import SimplicialComplex, chain_homology, nerve
from numeric_rule_finder import datasets as D


# ---- SNF ----------------------------------------------------------------

def test_snf_reconstructs_and_normalizes():
    for A, factors in [
        ([[2, 0], [0, 2]], [2, 2]),
        ([[2, 0], [0, 3]], [1, 6]),
        ([[1, 2, 3], [4, 5, 6], [7, 8, 9]], [1, 3]),
        ([[2, 0, 0], [0, 2, 0]], [2, 2]),
    ]:
        D_, U, V = smith_normal_form(A)
        assert matmul(matmul(U, A), V) == D_
        assert invariant_factors(D_) == factors
        f = invariant_factors(D_)
        assert all(f[i + 1] % f[i] == 0 for i in range(len(f) - 1))


# ---- modular conservation laws ------------------------------------------

def test_parity_is_invisible_over_Q_but_present_over_Z():
    d = D.parity_pairs()
    idisc = integer_conservation(d["records"], d["entity_key"], d["event_key"], d["qty_key"])
    assert idisc.free_rank == 0                  # nothing over Q
    assert idisc.torsion == [2, 2]               # Z/2 (+) Z/2
    assert idisc.has_hidden_structure
    moduli = sorted(ml.modulus for ml in idisc.modular_laws)
    assert moduli == [2, 2]


def test_crt_fuses_into_single_Z6_law():
    d = D.crt_mod6()
    idisc = integer_conservation(d["records"], d["entity_key"], d["event_key"], d["qty_key"])
    assert idisc.free_rank == 0
    assert idisc.torsion == [6]
    assert len(idisc.modular_laws) == 1 and idisc.modular_laws[0].modulus == 6


def test_integer_free_rank_matches_Q_dimension():
    for make in D.ALL_DATASETS:
        d = make()
        q, z, ok = cross_check_free_rank(d["records"], d["entity_key"], d["event_key"], d["qty_key"])
        assert ok, f"{d['name']}: Q={q} Z_free={z}"


# ---- homology -----------------------------------------------------------

def test_homology_known_spaces():
    assert SimplicialComplex.from_facets([(0, 1), (1, 2), (0, 2)]).homology().betti == [1, 1]
    assert SimplicialComplex.from_facets(
        [(0, 1, 2), (0, 1, 3), (0, 2, 3), (1, 2, 3)]).homology().betti == [1, 0, 1]
    assert SimplicialComplex.from_facets([(0, 1, 2)]).homology().betti == [1, 0, 0]


def test_homology_detects_torsion():
    hom = chain_homology([1, 1, 1], [[[0]], [[2]]])
    assert hom.betti == [1, 0, 0]
    assert hom.torsion[1] == [2]                 # H_1 = Z/2


def test_nerve_cohomology():
    # pairwise-only overlaps -> a cycle in the nerve (S^1)
    cyc = nerve({"A": {"g1", "g2"}, "B": {"g2", "g3"}, "C": {"g1", "g3"}}).homology()
    assert cyc.betti[:2] == [1, 1]
    # all share a group -> contractible
    full = nerve({"A": {"g"}, "B": {"g"}, "C": {"g"}}).homology()
    assert full.betti == [1, 0, 0]
    # every triple overlaps but not all four -> hollow sphere (H_2)
    cover4 = {"A": {"gABC", "gABD", "gACD"}, "B": {"gABC", "gABD", "gBCD"},
              "C": {"gABC", "gACD", "gBCD"}, "D": {"gABD", "gACD", "gBCD"}}
    sph = nerve(cover4).homology()
    assert sph.betti == [1, 0, 1]
