import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
for _root in HERE.parents:
    if (_root / "numeric_rule_finder").is_dir():
        sys.path.insert(0, str(_root)); break

import pipeline


def test_lib_feed_beats_ml_alone():
    res = pipeline.main()
    assert res["lib_f1"] > res["ml_f1"]   # composing the exact filter + feature wins
    assert res["lib_f1"] >= 0.85          # and the composed pipeline is strong
