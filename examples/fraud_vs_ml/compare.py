"""
Conservation check vs. a machine-learning anomaly detector
===========================================================

Task: catch fraudulent ledger transactions. The fraud here is a small "skim" --
a transaction whose legs DON'T balance (money created or destroyed) but whose
amounts are otherwise completely ordinary in size.

We run two detectors on the same data and score them against the known frauds:

  * ML   -- an Isolation Forest, the standard off-the-shelf anomaly detector,
            on generic per-account features (the kind a data scientist would
            reach for). It keys on statistical oddity -- mostly magnitude.
  * Rule -- this library's exact conservation check (Reconciler.balance_check):
            a transaction is flagged iff its amounts fail to net to zero.

The point is not that ML is bad -- it is that *conservation violation is not the
same thing as a statistical outlier*. A normal-sized unbalanced entry sits in the
dense middle of feature space, invisible to the forest, while the exact law sees
it immediately. (Hand the forest the net amount as a feature and it would also
win -- but "the net should be zero" IS the conservation insight; a generic
feature set does not contain it.)

Run:  python compare.py
"""

import sys
from pathlib import Path
import random

import numpy as np
from sklearn.ensemble import IsolationForest

HERE = Path(__file__).resolve().parent
for _root in HERE.parents:
    if (_root / "numeric_rule_finder").is_dir():
        sys.path.insert(0, str(_root)); break

from numeric_rule_finder.analyst import Reconciler

ACCOUNTS = ["cash", "revenue"]
RNG = random.Random(7)
np.random.seed(7)


def make_data(n_legit=300, n_fraud=12):
    """Legit sales balance exactly; frauds skim a small, ordinary-sized amount,
    so the books no longer balance. Returns (rows, txns, labels, tids)."""
    rows, txns, labels, tids = [], [], [], []

    def emit(tid, legs, is_fraud):
        for acct, amt in legs.items():
            rows.append({"txn_id": tid, "account": acct, "amount": f"{amt:.2f}"})
        txns.append(legs); labels.append(1 if is_fraud else 0); tids.append(tid)

    for i in range(n_legit):
        p = float(np.random.lognormal(mean=5.0, sigma=0.9))      # most modest, some large
        emit(f"L{i:04d}", {"cash": p, "revenue": -p}, False)     # balances exactly
    for j in range(n_fraud):
        p = float(np.random.lognormal(mean=5.0, sigma=0.5))      # ORDINARY size
        skim = RNG.uniform(5, 40)                                # small, normal-looking
        emit(f"F{j:04d}", {"cash": p, "revenue": -(p - skim)}, True)   # net = +skim != 0
    return rows, txns, labels, tids


def featurize(txns):
    """Generic features a data scientist would build: per-account signed total,
    number of legs, gross size. Deliberately NOT the net -- that's the insight."""
    X = []
    for legs in txns:
        row = [legs.get(a, 0.0) for a in ACCOUNTS]
        row.append(len(legs))
        row.append(sum(abs(v) for v in legs.values()))
        X.append(row)
    return np.array(X, dtype=float)


def score(name, y_true, y_pred):
    tp = sum(1 for t, p in zip(y_true, y_pred) if t and p)
    fp = sum(1 for t, p in zip(y_true, y_pred) if not t and p)
    fn = sum(1 for t, p in zip(y_true, y_pred) if t and not p)
    prec = tp / (tp + fp) if tp + fp else 0.0
    rec = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
    print(f"  {name:28s} precision={prec:4.2f}  recall={rec:4.2f}  f1={f1:4.2f}  "
          f"(caught {tp}/{tp + fn} frauds, {fp} false alarms)")
    return prec, rec, f1


def main():
    rows, txns, labels, tids = make_data()
    n_fraud = sum(labels)
    print(f"{len(txns)} transactions; {n_fraud} are fraudulent "
          f"(unbalanced by an ordinary-sized amount).\n")

    # ML: Isolation Forest on generic features, given the true anomaly budget.
    X = featurize(txns)
    iso = IsolationForest(contamination=n_fraud / len(txns), random_state=7).fit(X)
    ml_pred = [1 if p == -1 else 0 for p in iso.predict(X)]

    # Rule: exact conservation check through the library.
    breaks = {b.group for b in Reconciler.from_records(rows)
              .balance_check(group="txn_id", amount="amount").breaks}
    rule_pred = [1 if tid in breaks else 0 for tid in tids]

    print("RESULTS (detecting the frauds):")
    _, _, ml_f1 = score("ML  (Isolation Forest)", labels, ml_pred)
    _, _, rule_f1 = score("Rule (conservation check)", labels, rule_pred)

    print("\nWhy: the frauds are ordinary in size, so they sit in the dense middle")
    print("of feature space -- the forest ranks genuinely large but balanced sales")
    print("as the odd ones instead. The conservation law ignores size and sees the")
    print("broken balance exactly: no training, no threshold, no false alarms.")
    return {"ml_f1": ml_f1, "rule_f1": rule_f1}


if __name__ == "__main__":
    main()
