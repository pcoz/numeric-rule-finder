"""
Locks the rules-free points-integrity workflow.
"""

import sys
from pathlib import Path
from fractions import Fraction
from functools import reduce
from math import gcd

HERE = Path(__file__).resolve().parent
for _root in HERE.parents:
    if (_root / "numeric_rule_finder").is_dir():
        sys.path.insert(0, str(_root)); break

from numeric_rule_finder.analyst import Reconciler, cross_check
from numeric_rule_finder.cohomology import ConservationComplex
from numeric_rule_finder.integer_invariants import integer_conservation

DATA = HERE / "data"


def test_step1_learns_two_closed_economies():
    wb = Reconciler.from_csv(DATA / "clean_log.csv").what_balances(
        account="bucket", group="event", amount="points")
    assert len(wb.separate_books) == 2
    assert not wb.honest_stop


def test_step2_flags_the_minting_event():
    bc = Reconciler.from_csv(DATA / "monitor_batch.csv").balance_check(
        group="event", amount="points")
    assert {b.group: b.off_by for b in bc.breaks} == {"m3": Fraction(200)}


def test_step3_exploit_is_obstruction_transfer_is_coboundary():
    clean = Reconciler.from_csv(DATA / "clean_log.csv").rows
    cx = ConservationComplex.from_records(clean, "bucket", "event", "points")
    exploit = cx.type_observation({"member_ben": 200})
    assert not exploit.is_coboundary
    assert exploit.obstruction[0][1] == Fraction(200)
    transfer = cx.type_observation({"member_amy": -25, "member_ben": 25})
    assert transfer.is_coboundary


def test_step4_learns_granularity_and_flags_off_tier():
    rows = Reconciler.from_csv(DATA / "tier_bonuses.csv").rows
    idisc = integer_conservation(rows, "bucket", "grant", "points")
    grain = reduce(gcd, [ml.modulus for ml in idisc.modular_laws])
    assert grain == 50
    assert 200 % grain == 0
    assert 30 % grain != 0


def test_step5_partner_statements_impossible():
    msg = cross_check({("Airline", "Hotel"): 120, ("Hotel", "Card"): -50, ("Card", "Airline"): -40})
    assert "CANNOT all be correct" in msg
