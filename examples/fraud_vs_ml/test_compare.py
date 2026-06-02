import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
for _root in HERE.parents:
    if (_root / "numeric_rule_finder").is_dir():
        sys.path.insert(0, str(_root)); break

import compare


def test_conservation_beats_isolation_forest():
    res = compare.main()
    assert res["rule_f1"] == 1.0          # exact: catches every fraud, no false alarms
    assert res["rule_f1"] > res["ml_f1"]  # and beats the anomaly detector outright
