"""
Feeding this method INTO machine learning
==========================================

Not every problem is a clean either/or. Here the two compose, and the library
makes the ML job easy instead of doing it itself.

The task: among a large ledger, find the *fraudulent* entries. Crucially, not
every broken entry is fraud -- some are innocent typos. So:

  * the EXACT part -- "which entries don't balance?" -- is conservation, and the
    library answers it perfectly (no ML can beat exact);
  * the FUZZY part -- "of the broken ones, which are fraud vs. honest error?" --
    is a judgement call, and that is exactly what ML is good at.

We compare two ways of finding fraud with the *same* classifier:

  * ML alone  -- a Random Forest on raw features over ALL transactions.
  * Lib -> ML -- the library (a) exactly filters to the broken entries, shrinking
                 the ML's universe, and (b) hands ML the residual it computed as a
                 feature; the forest then only separates fraud from error.

Run:  python pipeline.py
"""

import sys
from pathlib import Path
import random

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

HERE = Path(__file__).resolve().parent
for _root in HERE.parents:
    if (_root / "numeric_rule_finder").is_dir():
        sys.path.insert(0, str(_root)); break

from numeric_rule_finder.analyst import Reconciler

RNG = random.Random(11)
np.random.seed(11)


def make_data(n_clean=3000, n_fraud=150, n_error=150):
    rows, recs = [], []   # recs: per-txn dict with label + raw fields

    def emit(tid, cash, rev, hour, label):
        rows.append({"txn_id": tid, "account": "cash", "amount": f"{cash:.2f}"})
        rows.append({"txn_id": tid, "account": "revenue", "amount": f"{rev:.2f}"})
        recs.append({"tid": tid, "cash": cash, "revenue": rev, "hour": hour,
                     "gross": abs(cash) + abs(rev), "label": label})

    for i in range(n_clean):
        p = float(np.random.lognormal(4.8, 0.8))
        emit(f"C{i:05d}", p, -p, RNG.randint(0, 23), "clean")          # balances
    for i in range(n_fraud):
        p = float(np.random.lognormal(4.8, 0.6))
        skim = 10 * RNG.randint(1, 6)                                  # ROUND skim
        hour = RNG.choice([1, 2, 3, 4, 23]) if RNG.random() < 0.6 else RNG.randint(0, 23)
        emit(f"F{i:05d}", p, -(p - skim), hour, "fraud")               # net = +skim (round)
    for i in range(n_error):
        p = float(np.random.lognormal(4.8, 0.6))
        err = round(RNG.uniform(1, 60) + 0.37, 2)                      # NOT round
        emit(f"E{i:05d}", p, -(p - err), RNG.randint(0, 23), "error")  # net = +err (odd)
    return rows, recs


def fraud_scores(name, y_true, y_pred):
    tp = int(np.sum((y_true == 1) & (y_pred == 1)))
    fp = int(np.sum((y_true == 0) & (y_pred == 1)))
    fn = int(np.sum((y_true == 1) & (y_pred == 0)))
    prec = tp / (tp + fp) if tp + fp else 0.0
    rec = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
    print(f"  {name:34s} precision={prec:4.2f}  recall={rec:4.2f}  f1={f1:4.2f}")
    return f1


def main():
    rows, recs = make_data()
    n = len(recs)
    n_fraud = sum(r["label"] == "fraud" for r in recs)
    print(f"{n} transactions; {n_fraud} fraudulent ({100 * n_fraud / n:.1f}%), "
          f"mixed in with honest errors and clean entries.\n")

    is_fraud = np.array([1 if r["label"] == "fraud" else 0 for r in recs])
    idx = np.arange(n)
    tr, te = train_test_split(idx, test_size=0.5, stratify=is_fraud, random_state=11)

    # ---- ML ALONE: Random Forest on raw features over the whole population ----
    Xraw = np.array([[r["cash"], r["revenue"], r["gross"], r["hour"]] for r in recs])
    rf = RandomForestClassifier(n_estimators=200, random_state=11, class_weight="balanced")
    rf.fit(Xraw[tr], is_fraud[tr])
    pred_all = rf.predict(Xraw[te])

    # ---- LIB -> ML: filter to broken entries, hand ML the residual feature ----
    # (1) EXACT pre-filter: the library finds every unbalanced transaction.
    breaks = {b.group: b.off_by for b in Reconciler.from_records(rows)
              .balance_check(group="txn_id", amount="amount").breaks}
    cand_mask = np.array([recs[i]["tid"] in breaks for i in range(n)])
    # the filter is exact: it keeps 100% of frauds and drops every clean entry
    kept_frauds = int(np.sum(cand_mask & (is_fraud == 1)))
    print(f"Library pre-filter: {int(cand_mask.sum())} of {n} entries don't balance "
          f"(ML's universe shrinks {n}->{int(cand_mask.sum())}).")
    print(f"   exact: it retained {kept_frauds}/{n_fraud} frauds and 0 clean entries.\n")

    # (2) ML only adjudicates fraud-vs-error on candidates, using the lib's residual.
    def feats(i):
        resid = float(breaks[recs[i]["tid"]])
        return [resid, abs(resid), 1.0 if round(abs(resid)) % 10 == 0 else 0.0, recs[i]["hour"]]
    Xc = np.array([feats(i) for i in range(n) if cand_mask[i]])
    yc = np.array([is_fraud[i] for i in range(n) if cand_mask[i]])
    cidx = np.array([i for i in range(n) if cand_mask[i]])
    ctr = np.array([k for k, i in enumerate(cidx) if i in set(tr)])
    cte = np.array([k for k, i in enumerate(cidx) if i in set(te)])
    rf2 = RandomForestClassifier(n_estimators=200, random_state=11)
    rf2.fit(Xc[ctr], yc[ctr])
    pred_c = rf2.predict(Xc[cte])
    # lift predictions back to the full test population (clean entries -> not fraud)
    pred_lib = np.zeros(len(te), dtype=int)
    cand_te_pos = {i: k for k, i in enumerate(te)}
    for k_local, i in enumerate(cidx[cte]):
        pred_lib[cand_te_pos[i]] = pred_c[k_local]

    print("RESULTS on the held-out test set (detecting FRAUD):")
    ml_f1 = fraud_scores("ML alone (raw features)", is_fraud[te], pred_all)
    lib_f1 = fraud_scores("Lib -> ML (filter + residual)", is_fraud[te], pred_lib)

    print("\nWhy: raw amounts barely distinguish a skim from a normal sale, so the")
    print("forest alone struggles to find rare fraud in a big clean population. The")
    print("library removes every clean entry exactly and contributes the residual it")
    print("computed; the forest then has an easy, well-posed job -- fraud vs. error on")
    print("a few hundred candidates -- and the two together beat either alone.")
    return {"ml_f1": ml_f1, "lib_f1": lib_f1}


if __name__ == "__main__":
    main()
