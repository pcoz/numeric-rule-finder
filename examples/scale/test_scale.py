import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
for _root in HERE.parents:
    if (_root / "numeric_rule_finder").is_dir():
        sys.path.insert(0, str(_root)); break

import scale_demo
from numeric_rule_finder.invariants import (
    discover_invariants, build_incidence, _nullspace, _modular_rank, _row_integerize, _RANK_PRIMES)


def test_fast_path_honest_stops_exactly():
    """Dense unstructured incidence: fast path certifies full rank -> 0 laws,
    and agrees with the exact rational null space."""
    rows = scale_demo.unstructured(40, 50)
    entities, events, S = build_incidence(rows, "entity", "event", "amount")
    ne = len(entities)
    ST = [[S[e][v] for e in entities] for v in events]
    irows = [_row_integerize(r) for r in ST]

    assert _modular_rank(irows, ne, _RANK_PRIMES[0]) == ne          # full rank certified
    assert discover_invariants(rows, "entity", "event", "amount").n_laws == 0
    assert len(_nullspace(ST, ne)) == 0                             # exact agrees


def test_laws_still_found_exactly():
    """When laws exist (conserved pairs), the fast path must NOT fire and the
    exact count is returned."""
    disc = discover_invariants(scale_demo.paired(8, 200), "entity", "event", "amount")
    assert disc.n_laws == 8
