# Example — conservation check vs. a machine-learning anomaly detector

> **Run it:** `python examples/fraud_vs_ml/compare.py`

A head-to-head on the same data: catch fraudulent ledger transactions, where the
fraud is a small **skim** — an entry whose legs don't balance, but whose amounts
are otherwise ordinary in size.

- **ML** — an **Isolation Forest** (the standard off-the-shelf anomaly detector)
  on generic per-account features, given the true anomaly budget.
- **Rule** — this library's exact conservation check (`Reconciler.balance_check`):
  flag any transaction whose amounts fail to net to zero.

## Result (actual output)

```text
312 transactions; 12 are fraudulent (unbalanced by an ordinary-sized amount).

RESULTS (detecting the frauds):
  ML  (Isolation Forest)       precision=0.00  recall=0.00  f1=0.00  (caught 0/12 frauds, 12 false alarms)
  Rule (conservation check)    precision=1.00  recall=1.00  f1=1.00  (caught 12/12 frauds, 0 false alarms)
```

## Why the rule wins here

The frauds are **ordinary in size**, so in feature space they sit right on top of
normal sales of the same magnitude — the forest cannot separate `(cash +500,
revenue −480)` from `(cash +500, revenue −500)`. Worse, it spends its anomaly
budget on genuinely *large but perfectly balanced* sales, producing only false
alarms. The conservation law ignores magnitude entirely and sees the broken
balance exactly: no training data, no threshold, no false positives.

**The honest boundary.** This is not "ML is bad." It is that *a conservation
violation is not the same thing as a statistical outlier*. If the fraud were also
statistically unusual, the forest would catch it. And if you handed the forest the
**net amount** as a feature, it would win too — but "the net should be zero" *is*
the conservation insight; a generic feature set doesn't contain it. When the true
signal is an exact law, the exact method dominates. The companion example
[`ml_assist/`](../ml_assist/README.md) shows the flip side: feeding that exact
signal *into* ML.
