# Example — scaling discovery to large matrices

> **Run:** `python examples/scale/scale_demo.py`

Discovering conservation laws is a null-space computation. Doing it *exactly*
over the rationals means Fraction-based row reduction — O(n³) with rational
blow-up, so on a large, dense incidence the denominators explode and it crawls.

But the most common verdict on real data is **"there is no conservation
structure here"** — the incidence has full column rank. That verdict can be
reached the fast way: if the matrix has full rank over a single finite field
𝔽ₚ, it has full rank over ℚ (reduction never raises rank), so there is
**provably no law**. `discover_invariants` now checks this in machine-integer
arithmetic and honest-stops immediately — no rational RREF at all.

## Result (actual output)

```text
Dense incidence: 120 entities x 140 events, random movements (no conservation structure).

  discover_invariants (modular fast path):  0 laws in   259.0 ms
  exact rational null space (old path)    :  0 laws in    3794 ms
  -> same verdict, ~15x faster, and still EXACT
     (full rank over F_p certifies full rank over Q -> provably no law).

And when laws DO exist they are still found exactly: a 16-entity, 8-pair network -> 8 conserved pairs.
```

## Why it's still exact

This is not a heuristic or a sampled approximation. The shortcut rests on a
theorem: rank over ℚ is always ≥ rank over 𝔽ₚ, and a matrix can have at most as
many independent columns as it has columns. So if some 𝔽ₚ already shows **full**
column rank, the rational rank is pinned to the same value — there is no room for
a null vector, and the honest-stop is certain. A prime that happens to miss the
rank simply forfeits the shortcut and the code falls through to the exact
rational path; it can never give a wrong answer.

The win lands exactly where the old code wasted the most effort: grinding a full
rational row-reduction only to discover the data had no structure to find. When
laws *do* exist, the exact generators are computed as before.
