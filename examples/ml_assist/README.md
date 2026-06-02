# Example — feeding this method *into* machine learning

> **Run it:** `python examples/ml_assist/pipeline.py`

The companion to [`fraud_vs_ml/`](../fraud_vs_ml/README.md). Here the two
compose, and the library makes the ML job easy rather than doing it itself.

The task splits cleanly into an exact part and a fuzzy part:

- **exact** — *"which entries don't balance?"* is conservation; the library
  answers it perfectly (no ML can beat exact).
- **fuzzy** — *"of the broken ones, which are fraud vs. an honest typo?"* is a
  judgement call — exactly what ML is good at.

We find fraud two ways with the **same** Random Forest:

- **ML alone** — raw features over *all* transactions.
- **Lib → ML** — the library (a) exactly filters to the broken entries (shrinking
  the ML's universe and dropping every clean entry with zero false negatives), and
  (b) hands ML the **residual** it computed as a feature; the forest then only
  separates fraud from error.

## Result (actual output)

```text
3300 transactions; 150 fraudulent (4.5%), mixed in with honest errors and clean entries.

Library pre-filter: 300 of 3300 entries don't balance (ML's universe shrinks 3300->300).
   exact: it retained 150/150 frauds and 0 clean entries.

RESULTS on the held-out test set (detecting FRAUD):
  ML alone (raw features)            precision=0.77  recall=0.32  f1=0.45
  Lib -> ML (filter + residual)      precision=0.95  recall=1.00  f1=0.97
```

## Why composing wins

Raw amounts barely distinguish a skim from a normal sale, so the forest alone
hunts rare fraud in a big clean haystack and mostly misses it (recall 0.32). The
library removes every clean entry **exactly** — guaranteeing no clean
false-positives and losing no fraud — and contributes the residual it computed as
a feature. The forest is left with a small, well-posed problem (fraud vs. error on
a few hundred candidates) and nails it. The exact method and the learned method
each do what they are best at, and together they beat either alone.
