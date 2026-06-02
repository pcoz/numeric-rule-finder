import io
import sys
from contextlib import redirect_stdout
from pathlib import Path

HERE = Path(__file__).resolve().parent
for _root in HERE.parents:
    if (_root / "numeric_rule_finder").is_dir():
        sys.path.insert(0, str(_root)); break

from numeric_rule_finder.cli import main

CSV = str(HERE / "ledger.csv")


def _run(argv):
    buf = io.StringIO()
    with redirect_stdout(buf):
        main(argv)
    return buf.getvalue()


def test_groups_cli_finds_three_books():
    out = _run(["groups", CSV, "--group", "txn_id", "--account", "account"])
    assert "3 independent groups" in out
    assert "cash" in out and "inventory" in out and "wages_payable" in out


def test_check_cli_balances():
    out = _run(["check", CSV, "--group", "txn_id", "--amount", "amount"])
    assert "balance" in out.lower()
