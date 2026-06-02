"""
Tests for the conservation-law discovery engine.

Ground-truth law counts on the synthesized datasets, the honest-stop on
structure-free data, the typed residual on a corrupted ledger, and — when
petra-nn is installed — the P-invariants of the real resource-lock net.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from fractions import Fraction

from numeric_rule_finder.invariants import discover_invariants, check_conservation
from numeric_rule_finder import datasets as D


@pytest.mark.parametrize("make", D.ALL_DATASETS, ids=lambda m: m.__name__)
def test_law_counts(make):
    d = make()
    disc = discover_invariants(d["records"], d["entity_key"], d["event_key"], d["qty_key"])
    assert disc.n_laws == d["expected_laws"]
    assert disc.honest_stop == (d["expected_laws"] == 0)


def test_michaelis_menten_moieties():
    d = D.michaelis_menten()
    disc = discover_invariants(d["records"], d["entity_key"], d["event_key"], d["qty_key"])
    # the two interpretable conserved moieties, by support
    supports = {frozenset(law.coeffs) for law in disc.minimal_semipositive}
    assert frozenset({"E", "ES"}) in supports
    assert frozenset({"S", "ES", "P"}) in supports


def test_two_books_block_structure():
    d = D.ledger_two_books()
    disc = discover_invariants(d["records"], d["entity_key"], d["event_key"], d["qty_key"])
    supports = {frozenset(law.coeffs) for law in disc.minimal_semipositive}
    assert frozenset({"cash", "revenue", "expense"}) in supports
    assert frozenset({"inventory", "cogs"}) in supports


def test_honest_stop():
    d = D.no_structure()
    disc = discover_invariants(d["records"], d["entity_key"], d["event_key"], d["qty_key"])
    assert disc.honest_stop


def test_typed_residual_localizes_break():
    clean = D.ledger_connected()
    disc = discover_invariants(clean["records"], D.ENTITY, D.EVENT, D.QTY)
    corrupt = [r for r in clean["records"]
               if not (r[D.EVENT] == "t2" and r[D.ENTITY] == "expense")]
    report = check_conservation(corrupt, disc.laws, D.ENTITY, D.EVENT, D.QTY)
    (law, total, violators) = report[0]
    assert total == Fraction(250)
    assert [ev for ev, _ in violators] == ["t2"]


def test_resource_lock_petrinet_has_three_invariants():
    pytest.importorskip("petri_net_nn")
    examples = Path(r"C:\Temp\petri-net-nn\examples\resource_lock\scenario.toml")
    if not examples.exists():
        pytest.skip("petra-nn example scenario not present")
    from numeric_rule_finder.petra_adapter import petrinet_from_scenario, discover_petrinet_invariants
    net = petrinet_from_scenario(examples)
    disc = discover_petrinet_invariants(net)
    assert disc.n_laws == 3
