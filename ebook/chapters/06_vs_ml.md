[🏠 Home](../index.md) · [← Previous: Where it fits](05_where_it_fits.md) · [Next: Raw XML showcase →](07_xml_showcase.md)

---

# 7 · This method vs. machine learning

These two approaches answer different questions, and confusing them wastes effort
in both directions. Machine learning learns a *statistical* notion of "normal" and
scores how far a point sits from it. This library checks an *exact* law and reports
violations as deductions. So the rule of thumb is sharp:

- Reach for **this method** when the ground truth is a conservation/balance law,
  and a violation is meaningful *by definition* — not merely unusual.
- Reach for **machine learning** when "normal" is statistical, behavioural, or
  distributional, and there is no exact law to lean on.

The two worked examples below make the boundary concrete. Both run a real
scikit-learn model for comparison; both are reproducible.

---

## 7.1 When the law beats the model

> **Example:** [`examples/fraud_vs_ml/`](../../examples/fraud_vs_ml/README.md) ·
> **Run:** `python examples/fraud_vs_ml/compare.py`

The task is to catch fraudulent ledger transactions. The fraud is a small
**skim** — an entry whose legs don't balance, but whose amounts are otherwise
ordinary in size. We pit an **Isolation Forest** (the standard off-the-shelf
anomaly detector, on generic features) against the library's exact conservation
check.

```text
312 transactions; 12 are fraudulent (unbalanced by an ordinary-sized amount).

RESULTS (detecting the frauds):
  ML  (Isolation Forest)       precision=0.00  recall=0.00  f1=0.00  (caught 0/12 frauds, 12 false alarms)
  Rule (conservation check)    precision=1.00  recall=1.00  f1=1.00  (caught 12/12 frauds, 0 false alarms)
```

Because the frauds are ordinary in size, they sit on top of normal sales in
feature space — the forest can't separate `(cash +500, revenue −480)` from
`(cash +500, revenue −500)`, and it burns its budget flagging large *balanced*
sales instead. The conservation law ignores magnitude and sees the broken balance
exactly.

This is **not** "ML is bad." A conservation violation simply isn't a statistical
outlier. If the fraud were statistically unusual, the forest would catch it; and
if you fed the forest the net amount as a feature, it would win too — but "the net
should be zero" *is* the conservation insight, which a generic feature set doesn't
contain. **When the true signal is an exact law, the exact method dominates.**

---

## 7.2 When the law feeds the model

> **Example:** [`examples/ml_assist/`](../../examples/ml_assist/README.md) ·
> **Run:** `python examples/ml_assist/pipeline.py`

Now the flip side — composition. The task is to find *fraud*, but not every broken
entry is fraud; some are honest typos. That splits cleanly:

- the **exact** part — *"which entries don't balance?"* — is conservation;
- the **fuzzy** part — *"of the broken ones, which are fraud vs. error?"* — is a
  judgement call, and that is what ML is for.

We find fraud two ways with the **same** Random Forest: alone on raw features over
the whole population, versus a pipeline where the library first filters to the
broken entries (exactly) and hands the model the residual it computed.

```text
3300 transactions; 150 fraudulent (4.5%), mixed in with honest errors and clean entries.

Library pre-filter: 300 of 3300 entries don't balance (ML's universe shrinks 3300->300).
   exact: it retained 150/150 frauds and 0 clean entries.

RESULTS on the held-out test set (detecting FRAUD):
  ML alone (raw features)            precision=0.77  recall=0.32  f1=0.45
  Lib -> ML (filter + residual)      precision=0.95  recall=1.00  f1=0.97
```

Alone, the forest hunts rare fraud in a big clean haystack and mostly misses it
(recall 0.32). The library removes every clean entry **exactly** — no clean
false-positive is possible, and no fraud is lost — and contributes its residual as
a feature. The model is left with a small, well-posed problem and nails it
(F1 0.45 → 0.97). The exact method and the learned method each do what they're best
at, and **together they beat either alone**.

---

## 7.3 When to *definitely* use ML — and not this method

Reach for machine learning, and leave this library out, whenever the answer you
need is a learned pattern rather than a hard invariant. Concretely:

- **There is no conserved quantity at all.** Forecasting demand, predicting churn,
  credit scoring, recommendation, ranking, pricing — nothing is supposed to "net
  to zero," so there is no law to check.
- **The data is unstructured.** Images, audio, video, free text. This method needs
  signed quantities in named buckets; ML is the only game in town here.
- **"Abnormal" is behavioural or statistical, not a violation.** Account takeover
  by login/device patterns, network intrusion by traffic shape, spending that's
  *unusual* but perfectly balanced. The fraud in §7.1 broke a law; this kind
  doesn't.
- **You must pair or resolve records fuzzily.** Matching two systems with no shared
  key by name/amount/time similarity. This method honest-stops at that boundary by
  design; fuzzy matching is exactly ML's job.
- **The relationship is nonlinear or merely correlational.** This method finds
  additive/linear and modular invariants. If the structure is a soft, nonlinear,
  or probabilistic relationship, ML captures it and this method will (correctly)
  find nothing.

If most of your problem looks like the list above, don't force this library onto
it — it will honest-stop, which is the right answer, but it isn't *your* answer.

## 7.4 When to *definitely* use this method — and not ML

Reach for this library, and skip the model, when the truth is an exact law and a
violation is meaningful by definition:

- **A conservation/balance law governs the data** — ledgers, inventory, meters,
  pipelines, headcount, points economies, reaction networks. A break *is* the
  finding.
- **You can't afford false positives or a training set.** This method needs no
  labelled data, no threshold tuning, and raises no false alarms on rare-but-valid
  cases (§7.1: 12/12 caught, 0 false alarms).
- **You must catch novel cases.** An exploit nobody anticipated is caught the
  instant it breaks the law — there is no "we never trained on that."
- **You need an exact, auditable explanation.** Regulators and finance committees
  want *"this violates the cash/sales balance by 250,"* not *"the model assigned an
  anomaly score of 0.87."*
- **Hidden structure matters.** Separate books, modular invariants ("moves only in
  cases of 12"), mutually-impossible reconciliations — ML has no notion of these.

## 7.5 When a combination is the right answer

The strongest architecture is often both, with this method **in front of** the
model. Combine them when:

- **The problem has an exact part and a fuzzy part.** "Which entries are broken?"
  is exact (this method); "which broken ones are fraud vs. honest error?" is fuzzy
  (ML). That is exactly §7.2 — F1 went from 0.45 to 0.97 by composing.
- **You want to shrink the ML problem.** The exact pre-filter dropped the model's
  universe from 3,300 rows to 300 — and guaranteed no clean row could ever be a
  false positive and no fraud could be lost before the model even ran.
- **ML needs a feature it can't derive.** The conservation residual is an exact
  cross-field quantity a generic model won't reconstruct; computed by this method
  and handed over, it transforms the model's accuracy.
- **You want a trustworthy guardrail around a black box.** The exact layer catches
  and explains every law-violating case deterministically, and passes only the
  genuinely ambiguous remainder to the model — so the black box only ever decides
  what truly needs judgement.

### At a glance

| situation | use |
|---|---|
| No conserved quantity; unstructured data; behavioural/statistical anomaly; fuzzy matching; nonlinear/correlational signal | **ML** |
| An exact balance/conservation law; no false positives tolerable; novel cases; audit-grade explanation; hidden structure | **this method** |
| An exact part *and* a fuzzy part; shrink the ML problem; supply an exact feature; guardrail a black box | **combine** (this method → ML) |

The mathematics behind the exact side — why the conservation check is complete and
the residual typing is exact — is in the [Appendix](A_appendix_mathematics.md).

---

[🏠 Home](../index.md) · [← Previous: Where it fits](05_where_it_fits.md) · [Next: Raw XML showcase →](07_xml_showcase.md)
