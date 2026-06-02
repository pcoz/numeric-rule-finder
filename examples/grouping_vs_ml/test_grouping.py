import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
for _root in HERE.parents:
    if (_root / "numeric_rule_finder").is_dir():
        sys.path.insert(0, str(_root)); break

import find_groups


def test_lib_recovers_the_exact_books():
    """The direct solve must recover the 8 books exactly -- fast, no ML needed."""
    rows, truth = find_groups.build_data()
    labels, k, _dt = find_groups.lib_groups(rows)
    assert k == len(set(truth.values())) == 8
    assert find_groups.partition_of(labels) == find_groups.partition_of(truth)
