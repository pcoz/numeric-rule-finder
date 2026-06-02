"""
Tests for the plain-language analyst facade.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fractions import Fraction
from numeric_rule_finder.analyst import Reconciler, _num


def test_number_parsing():
    assert _num("1,234.50") == Fraction(2469, 2)
    assert _num("(75.00)") == Fraction(-75)
    assert _num("$40") == Fraction(40)
    assert _num("") is None and _num(None) is None


CLEAN = [
    {"txn_id": "1001", "account": "cash", "amount": "100"},
    {"txn_id": "1001", "account": "revenue", "amount": "-100"},
    {"txn_id": "2001", "account": "inventory", "amount": "60"},
    {"txn_id": "2001", "account": "cogs", "amount": "-60"},
]

BROKEN = [
    {"txn_id": "1002", "account": "cash", "amount": "250"},                      # missing counter
    {"txn_id": "1003", "account": "expense", "amount": "75"},
    {"txn_id": "1003", "account": "cash", "amount": "-75"},
    {"txn_id": "1003", "account": "expense", "amount": "75"},                    # duplicate
]


def test_balance_check_clean():
    rep = Reconciler.from_records(CLEAN).balance_check(group="txn_id", amount="amount")
    assert rep.all_balanced
    assert "balance" in rep.summary().lower()


def test_balance_check_finds_and_explains_breaks():
    rep = Reconciler.from_records(BROKEN).balance_check(group="txn_id", amount="amount")
    assert not rep.all_balanced
    byg = {b.group: b for b in rep.breaks}
    assert byg["1002"].off_by == Fraction(250)
    assert "missing" in byg["1002"].hint
    assert byg["1003"].off_by == Fraction(75)
    assert "duplicat" in byg["1003"].hint


def test_separate_books_discovered():
    rep = Reconciler.from_records(CLEAN).what_balances(
        account="account", group="txn_id", amount="amount")
    books = sorted(sorted(b) for b in rep.separate_books)
    assert books == [["cash", "revenue"], ["cogs", "inventory"]]


def test_honest_stop_in_plain_words():
    rows = [
        {"g": "1", "acct": "a", "amt": "1"},
        {"g": "2", "acct": "b", "amt": "1"},
        {"g": "3", "acct": "c", "amt": "1"},
    ]
    rep = Reconciler.from_records(rows).what_balances(account="acct", group="g", amount="amt")
    assert rep.honest_stop
    assert "could not find" in rep.summary().lower()


def test_intelligent_escalation_to_modular():
    # goods only ever move in pairs: nothing balances over ordinary arithmetic,
    # but the facade should auto-escalate and report the parity structure.
    rows = [
        {"move": "m1", "bin": "a", "qty": "2"},
        {"move": "m2", "bin": "a", "qty": "-4"},
        {"move": "m3", "bin": "b", "qty": "6"},
        {"move": "m4", "bin": "b", "qty": "2"},
    ]
    rep = Reconciler.from_records(rows).what_balances(account="bin", group="move", amount="qty")
    assert not rep.honest_stop                       # did NOT give up
    assert rep.modular_findings                       # found hidden structure
    assert "parity" in rep.summary().lower()


def test_compare_two_systems():
    a = Reconciler.from_records([{"g": "x", "amt": "100"}, {"g": "y", "amt": "50"}])
    b = Reconciler.from_records([{"g": "x", "amt": "100"}, {"g": "y", "amt": "40"}])
    diffs = a.compare(b, group="g", amount="amt")
    assert len(diffs) == 1 and "y" in diffs[0]


def test_from_csv(tmp_path):
    p = tmp_path / "led.csv"
    p.write_text("txn_id,account,amount\n1,cash,10\n1,revenue,-10\n", encoding="utf-8")
    rep = Reconciler.from_csv(str(p)).balance_check(group="txn_id", amount="amount")
    assert rep.all_balanced
