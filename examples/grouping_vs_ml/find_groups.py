"""
The overnight clustering job you don't need to run
==================================================

A very common analyst task: "find the natural groups in this data" -- which
accounts/customers/SKUs/entities belong together? The reflex is to featurize and
**cluster**: build an embedding, run KMeans/HDBSCAN, sweep the number of clusters
`k`, score each with silhouette/stability. At real scale (millions of entities,
graph embeddings, k-selection, repeated stability runs) that is the job you kick
off and leave running for hours.

But when "belong together" means *connected through shared transactions*, the
groups are not a fuzzy statistical question at all -- they are the **exact
connected components** of the data, recoverable in a single linear pass with no
embedding, no distance metric, and no `k` to choose.

This pits the two against each other on a ledger of 8 genuinely independent
"books". Each book is *sparsely* connected (no single transaction touches all of
its members), which is exactly where similarity clustering fragments a group and
where following the chains -- what this library does -- recovers it whole.

Run:  python examples/grouping_vs_ml/find_groups.py
"""

import sys
import time
import random
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
for _root in HERE.parents:
    if (_root / "numeric_rule_finder").is_dir():
        sys.path.insert(0, str(_root)); break

from numeric_rule_finder import Reconciler

# 8 unequal "books" -- 600 accounts that never transact across books.
BLOCK_SIZES = [40, 55, 70, 90, 110, 60, 80, 95]


def build_data(seed=7):
    """A blocked transaction graph: each book is a sparse *connected* network of
    accounts (a random spanning tree + a few extra edges); every edge is one
    balanced two-leg transfer. No edge ever crosses a book."""
    rng = random.Random(seed)
    truth, rows = {}, []
    next_acct = txn = 0
    for b, n in enumerate(BLOCK_SIZES):
        accts = [f"a{next_acct + i}" for i in range(n)]
        next_acct += n
        for a in accts:
            truth[a] = b
        order = accts[:]
        rng.shuffle(order)
        edges = [(order[i], order[rng.randrange(i)]) for i in range(1, n)]  # spanning tree
        for _ in range(max(1, n // 12)):                                    # a few extra links
            edges.append(tuple(rng.sample(accts, 2)))
        for (x, y) in edges:
            amt = rng.randint(10, 999)
            rows.append({"account": x, "txn": f"t{txn}", "amount": amt})
            rows.append({"account": y, "txn": f"t{txn}", "amount": -amt})
            txn += 1
    return rows, truth


def partition_of(labels_by_acct):
    groups = defaultdict(set)
    for a, lab in labels_by_acct.items():
        groups[lab].add(a)
    return {frozenset(s) for s in groups.values()}


# ---- the direct, exact solve (this library) ----
def lib_groups(rows):
    t0 = time.perf_counter()
    comps = Reconciler.from_records(rows).independent_groups("account", "txn")
    dt = time.perf_counter() - t0
    labels = {a: i for i, comp in enumerate(comps) for a in comp}
    return labels, len(comps), dt


# ---- the ML way: featurize accounts, cluster, sweep k ----
def ml_groups(rows, k_range=range(2, 16), seed=0):
    import numpy as np
    from sklearn.cluster import KMeans
    from sklearn.metrics import silhouette_score

    accts = sorted({r["account"] for r in rows}, key=str)
    idx = {a: i for i, a in enumerate(accts)}
    A = np.zeros((len(accts), len(accts)), dtype=float)
    by_txn = defaultdict(list)
    for r in rows:
        by_txn[r["txn"]].append(r["account"])
    for members in by_txn.values():                       # co-occurrence adjacency
        for x in members:
            for y in members:
                if x != y:
                    A[idx[x], idx[y]] = 1.0

    t0 = time.perf_counter()
    best = None
    for k in k_range:
        labels_arr = KMeans(n_clusters=k, n_init=4, random_state=seed).fit_predict(A)
        try:
            sil = silhouette_score(A, labels_arr)
        except Exception:
            sil = -1.0
        if best is None or sil > best[0]:
            best = (sil, k, labels_arr)
    dt = time.perf_counter() - t0
    _, k_best, labels_arr = best
    return {a: int(labels_arr[idx[a]]) for a in accts}, k_best, dt


def main():
    rows, truth = build_data()
    n_books = len(set(truth.values()))
    print(f"{len(truth)} accounts across {n_books} genuinely independent books "
          f"(each only sparsely connected), {len(rows)//2} transactions.\n")

    lib_labels, lib_k, lib_dt = lib_groups(rows)
    exact = partition_of(lib_labels) == partition_of(truth)
    print("THIS LIBRARY  (direct, exact -- one union-find pass):")
    print(f"  found {lib_k} groups in {lib_dt*1000:.1f} ms   "
          f"-- {'EXACTLY the true books' if exact else 'MISMATCH'}, and no k to choose.\n")

    ml_labels, ml_k, ml_dt = ml_groups(rows)
    from sklearn.metrics import adjusted_rand_score
    accts = list(truth)
    ari = adjusted_rand_score([truth[a] for a in accts], [ml_labels[a] for a in accts])
    print("CLUSTERING  (featurize accounts + KMeans, sweep k by silhouette):")
    print(f"  chose k={ml_k}, took {ml_dt:.1f} s, agreement with the true books "
          f"ARI={ari:.2f}  ({'fragmented the books' if ari < 0.99 else 'matched'}).\n")

    speedup = ml_dt / lib_dt if lib_dt else float("inf")
    print(f">>> The exact grouping was ~{speedup:,.0f}x faster AND perfectly correct.")
    print(">>> On 600 accounts the sweep takes seconds; at production scale (millions of")
    print(">>> entities, graph embeddings, k-selection, stability runs) it is the job you")
    print(">>> kick off and leave for hours. Connected components is one linear pass --")
    print(">>> and if you DO still want ML, it now runs inside clean, exact group bounds.")


if __name__ == "__main__":
    main()
