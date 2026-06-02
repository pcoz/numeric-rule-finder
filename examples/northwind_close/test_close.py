"""
Locks the BA worked example: every check yields its intended plain finding,
through the facade only (no math-layer imports here).
"""

import sys
from pathlib import Path
from fractions import Fraction

HERE = Path(__file__).resolve().parent
for _root in HERE.parents:
    if (_root / "numeric_rule_finder").is_dir():
        sys.path.insert(0, str(_root)); break

from numeric_rule_finder.analyst import Reconciler, cross_check, account_for_movement

GL = HERE / "data" / "gl.csv"
STOCK = HERE / "data" / "stock.csv"


def test_check1_ledger_break():
    bc = Reconciler.from_csv(GL).balance_check(group="journal", amount="amount")
    assert {b.group: b.off_by for b in bc.breaks} == {"J7": Fraction(250)}


def test_check2_two_books():
    wb = Reconciler.from_csv(GL).what_balances(account="account", group="journal", amount="amount")
    sets = sorted(sorted(s) for s in wb.separate_books)
    assert sets == [["cash", "refunds", "sales"], ["ic_due_from", "ic_due_to"]]


def test_check3_genuine_shortfall_named():
    rep = Reconciler.from_csv(GL).diagnose_breaks(group="journal", amount="amount", account="account")
    d = rep.items[0]
    assert d.verdict == "shortfall"
    assert "cash" in d.book and "sales" in d.book


def test_check4_stock_moves_in_cases():
    wb = Reconciler.from_csv(STOCK).what_balances(account="bin", group="move", amount="units")
    assert not wb.honest_stop and wb.modular_findings
    assert any("12" in f for f in wb.modular_findings)


def test_check5_shrink_vs_relocation():
    assert "UNACCOUNTED" in account_for_movement({"DC": -200, "StoreA": 150, "StoreB": 30})
    assert "nothing is missing" in account_for_movement({"DC": -200, "StoreA": 150, "StoreB": 50})


def test_check6_signoffs_inconsistent():
    msg = cross_check({("North", "South"): 120, ("South", "East"): -50, ("East", "North"): -40})
    assert "CANNOT all be correct" in msg
