"""
Scaling discovery to large matrices (the modular fast path)
===========================================================

Finding conservation laws is a null-space computation, and doing it *exactly*
over the rationals (Fraction RREF) is O(n^3) with rational blow-up: on a large,
dense incidence the denominators explode and it crawls.

But the most common verdict on real-world data is "there is no conservation
structure here" -- i.e. the incidence has full column rank. That verdict can be
reached the fast way: if the matrix has full rank over a single finite field
F_p, it has full rank over Q (reduction never raises rank), so there is
*provably* no law. `discover_invariants` now checks this in machine-integer
arithmetic and honest-stops immediately, skipping the rational RREF entirely.

This sizes up the difference on a dense, unstructured incidence -- and then
confirms that when laws *do* exist they are still found exactly.

Run:  python examples/scale/scale_demo.py
"""

import sys
import time
import random
from pathlib import Path

HERE = Path(__file__).resolve().parent
for _root in HERE.parents:
    if (_root / "numeric_rule_finder").is_dir():
        sys.path.insert(0, str(_root)); break

from numeric_rule_finder.invariants import (
    discover_invariants, build_incidence, _nullspace)

NE, NV = 120, 140


def unstructured(ne, nv, seed=1):
    """A dense incidence with (almost surely) NO conservation law: every event
    moves every entity by a random amount."""
    rng = random.Random(seed)
    return [{"entity": f"e{e:03d}", "event": f"v{v:03d}", "amount": rng.randint(-5, 5) or 1}
            for v in range(nv) for e in range(ne)]


def paired(n_pairs, nv, seed=2):
    """Entities in conserved pairs: each event takes x out of a_i and puts x
    into b_i, so every a_i + b_i is conserved -> exactly n_pairs laws."""
    rng = random.Random(seed)
    rows = []
    for v in range(nv):
        i = rng.randrange(n_pairs)
        x = rng.randint(1, 9)
        rows += [{"entity": f"a{i}", "event": f"v{v}", "amount": -x},
                 {"entity": f"b{i}", "event": f"v{v}", "amount": x}]
    return rows


def main():
    rows = unstructured(NE, NV)
    entities, events, S = build_incidence(rows, "entity", "event", "amount")
    ST = [[S[e][v] for e in entities] for v in events]

    t0 = time.perf_counter()
    disc = discover_invariants(rows, "entity", "event", "amount")     # modular fast path
    t_fast = time.perf_counter() - t0

    t0 = time.perf_counter()
    basis = _nullspace(ST, len(entities))                             # old exact rational path
    t_exact = time.perf_counter() - t0

    print(f"Dense incidence: {len(entities)} entities x {len(events)} events, "
          f"random movements (no conservation structure).\n")
    print(f"  discover_invariants (modular fast path):  {disc.n_laws} laws in {t_fast*1000:7.1f} ms")
    print(f"  exact rational null space (old path)    :  {len(basis)} laws in {t_exact*1000:7.0f} ms")
    print(f"  -> same verdict, ~{t_exact/t_fast:,.0f}x faster, and still EXACT")
    print(f"     (full rank over F_p certifies full rank over Q -> provably no law).\n")

    laws = discover_invariants(paired(8, 200), "entity", "event", "amount")
    print(f"And when laws DO exist they are still found exactly: a 16-entity, "
          f"8-pair network -> {laws.n_laws} conserved pairs.")


if __name__ == "__main__":
    main()
