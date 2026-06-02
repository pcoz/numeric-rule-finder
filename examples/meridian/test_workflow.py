"""
Locks the worked-example workflow: each rung must produce its intended number,
and the '5' must interlock across rungs 1, 3 and 4.
"""

import sys
from pathlib import Path
from fractions import Fraction

HERE = Path(__file__).resolve().parent
for _root in HERE.parents:
    if (_root / "numeric_rule_finder").is_dir():
        sys.path.insert(0, str(_root)); break

from numeric_rule_finder.analyst import Reconciler
from numeric_rule_finder.integer_invariants import integer_conservation
from numeric_rule_finder.cohomology import ConservationComplex, discrepancy_cohomology

LEDGER = HERE / "data" / "ledger.csv"


def test_rung1_break_is_five_with_no_culprit():
    bc = Reconciler.from_csv(LEDGER).balance_check(group="payout_run", amount="amount")
    breaks = {b.group: b for b in bc.breaks}
    assert set(breaks) == {"C3"}
    assert breaks["C3"].off_by == Fraction(5)
    assert breaks["C3"].suspect is None        # structural, no single line


def test_rung2_two_books_only_pool_a_conserved():
    wb = Reconciler.from_csv(LEDGER).what_balances(
        account="account", group="payout_run", amount="amount")
    sets = sorted(sorted(s) for s in wb.separate_books)
    assert sets == [["chip_reserve", "vault_chips"], ["member_escrow", "payout_bank"]]
    conserved = sorted(sorted(g) for g in wb.conserved_groups)
    assert conserved == [["member_escrow", "payout_bank"]]   # Pool B has no Q-law


def test_rung3_pool_b_conserves_mod_5():
    rows = Reconciler.from_csv(LEDGER).rows
    pool_b = [r for r in rows if r["account"] in ("vault_chips", "chip_reserve")]
    idisc = integer_conservation(pool_b, "account", "payout_run", "amount")
    assert idisc.free_rank == 0
    assert idisc.torsion == [5, 5]
    assert all(ml.modulus == 5 for ml in idisc.modular_laws)


def test_rung4_residual_is_genuine_obstruction_off_by_5():
    clean = [
        {"account": "vault_chips", "payout_run": "tick", "amount": "5"},
        {"account": "chip_reserve", "payout_run": "tick", "amount": "-5"},
    ]
    cx = ConservationComplex.from_records(clean, "account", "payout_run", "amount")
    # a clean re-attribution is resolvable ...
    assert cx.type_observation({"vault_chips": 15, "chip_reserve": -15}).is_coboundary
    # ... the real observed net is a genuine obstruction, off by 5
    typed = cx.type_observation({"vault_chips": 135, "chip_reserve": -130})
    assert not typed.is_coboundary
    assert [v for _, v in typed.obstruction] == [Fraction(5)]


def test_rung5_audit_memos_are_irreducible():
    dc = discrepancy_cohomology(
        {("AuditX", "AuditY"): 120, ("AuditY", "Ledger"): -50, ("Ledger", "AuditX"): -40})
    assert not dc.consistent
    assert dc.cycle_rank == 1
    assert abs(dc.obstruction[0][1]) == Fraction(30)
