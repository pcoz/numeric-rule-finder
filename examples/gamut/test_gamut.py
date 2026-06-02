"""
Cross-domain examples (NOT accounting) all run through the one facade.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fractions import Fraction
from numeric_rule_finder.analyst import Reconciler

EX = Path(__file__).resolve().parent / "data"


def test_energy_grid_break():
    rep = Reconciler.from_csv(EX / "energy_grid.csv").balance_check(group="interval", amount="kwh")
    off = {b.group: b.off_by for b in rep.breaks}
    assert off == {"09:00": Fraction(40)}


def test_clinical_trial_break():
    rep = Reconciler.from_csv(EX / "clinical_trial.csv").balance_check(group="site", amount="patients")
    off = {b.group: b.off_by for b in rep.breaks}
    assert off == {"SiteB": Fraction(2)}


def test_etl_dropped_rows():
    rep = Reconciler.from_csv(EX / "etl_rows.csv").balance_check(group="run", amount="rows")
    assert {b.group: b.off_by for b in rep.breaks} == {"r2": Fraction(50)}


def test_supply_chain_independent_lines():
    rep = Reconciler.from_csv(EX / "supply_chain.csv").what_balances(
        account="node", group="move", amount="units")
    sets = sorted(sorted(s) for s in rep.separate_books)
    assert sets == [["X_dc", "X_factory", "X_store"], ["Y_dc", "Y_factory", "Y_store"]]


def test_packaging_modular_escalation():
    rep = Reconciler.from_csv(EX / "stock_pairs.csv").what_balances(
        account="bin", group="move_id", amount="qty")
    assert not rep.honest_stop and rep.modular_findings


def test_warehouse_compare():
    a = Reconciler.from_csv(EX / "warehouse_a.csv")
    b = Reconciler.from_csv(EX / "warehouse_b.csv")
    diffs = a.compare(b, group="sku", amount="qty")
    assert len(diffs) == 1 and "SKU-200" in diffs[0]
