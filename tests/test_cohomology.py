"""
Tests for cohomological residual typing:
  * conservation complex — coboundary (with witness) vs obstruction in coker(S),
  * discrepancy sheaf — coboundary vs irreducible H^1 cycle.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fractions import Fraction

from numeric_rule_finder.cohomology import ConservationComplex, discrepancy_cohomology
from numeric_rule_finder import datasets as D


def _ledger_complex():
    ref = D.ledger_connected()
    return ConservationComplex.from_records(ref["records"], D.ENTITY, D.EVENT, D.QTY)


def test_coboundary_has_zero_class_and_a_valid_witness():
    cx = _ledger_complex()
    tr = cx.type_observation({"cash": 30, "revenue": -30})
    assert tr.is_coboundary
    assert all(v == 0 for _, v in tr.coordinates)
    # the witness flow must actually reproduce the observed change: S x = b
    produced = {e: Fraction(0) for e in cx.entities}
    for ev, x in tr.witness_flow.items():
        for e in cx.entities:
            produced[e] += cx.S[e][ev] * x
    assert produced["cash"] == 30 and produced["revenue"] == -30
    assert produced["expense"] == 0


def test_obstruction_names_the_violated_law():
    cx = _ledger_complex()
    tr = cx.type_observation({"cash": 250})
    assert not tr.is_coboundary
    assert tr.witness_flow is None
    assert len(tr.obstruction) == 1
    law, val = tr.obstruction[0]
    assert val == Fraction(250)
    assert set(law.coeffs) == {"cash", "expense", "revenue"}


def test_petrinet_complex_typing():
    import pytest
    pytest.importorskip("petri_net_nn")
    toml = Path(r"C:\Temp\petri-net-nn\examples\resource_lock\scenario.toml")
    if not toml.exists():
        pytest.skip("resource_lock scenario not present")
    from numeric_rule_finder.petra_adapter import petrinet_from_scenario
    cx = ConservationComplex.from_petrinet(petrinet_from_scenario(toml))
    # a single legal firing of t_serve_a is a coboundary
    legal = cx.type_observation({"p_a_pending": -1, "p_a_done": 1, "p_resource_busy": 1})
    assert legal.is_coboundary
    # a served token from nowhere violates >= 1 conservation law
    illegal = cx.type_observation({"p_a_done": 1})
    assert not illegal.is_coboundary
    assert len(illegal.obstruction) >= 1


def test_discrepancy_consistent_is_coboundary():
    coh = discrepancy_cohomology({("A", "B"): 5, ("B", "C"): -3, ("A", "C"): 2})
    assert coh.consistent
    p = coh.offsets
    # offsets must reproduce every reported discrepancy
    assert p["A"] - p["B"] == 5
    assert p["B"] - p["C"] == -3
    assert p["A"] - p["C"] == 2


def test_discrepancy_inconsistent_has_nonzero_h1():
    coh = discrepancy_cohomology({("A", "B"): 5, ("B", "C"): 5, ("C", "A"): 5})
    assert not coh.consistent
    assert coh.cycle_rank == 1
    assert coh.obstruction and coh.obstruction[0][1] == Fraction(15)
