# Example — the overnight clustering job you don't need to run

> **Run:** `python examples/grouping_vs_ml/find_groups.py`
> **Needs:** `scikit-learn` (for the ML side only)

"Find the natural groups in this data" — which accounts, customers, SKUs, or
entities belong together — is one of the most common analyst asks, and the reflex
is to **cluster**: featurize, run KMeans/HDBSCAN, sweep the number of clusters
`k`, score each with silhouette or stability. At real scale (millions of entities,
graph embeddings, `k`-selection, repeated stability runs) that is a job you start
and leave running for hours.

But when "belong together" means *connected through shared transactions*, the
groups aren't a fuzzy statistical question at all — they are the **exact connected
components** of the data, recoverable in one linear pass with no embedding, no
distance metric, and no `k` to choose. This library exposes that directly as
`Reconciler.independent_groups(...)`.

## Result (actual output)

```text
600 accounts across 8 genuinely independent books (each only sparsely connected), 638 transactions.

THIS LIBRARY  (direct, exact -- one union-find pass):
  found 8 groups in 0.8 ms   -- EXACTLY the true books, and no k to choose.

CLUSTERING  (featurize accounts + KMeans, sweep k by silhouette):
  chose k=2, took 2.8 s, agreement with the true books ARI=0.00  (fragmented the books).

>>> The exact grouping was ~3,588x faster AND perfectly correct.
```

## Why clustering fails here — and the exact method doesn't

Each "book" is **sparsely** connected: no single transaction touches all of its
members, so two accounts in the same book may share no direct counterparty at all.
Similarity clustering only sees *direct* co-occurrence, so it fragments a book into
the little neighbourhoods that happen to transact together — and the silhouette
sweep, with nothing clean to latch onto, collapses to `k=2` (ARI 0.00: no
agreement with the true books).

The exact method follows the **chains**: A transacts with B, B with C, so A, B and
C are one group, however sparse the links. That is the connected-components
relation, and union-find computes it exactly in a single linear pass.

## An honest caveat

A *graph-aware* method — spectral clustering, or a node2vec/DeepWalk embedding —
would recover these components far better than raw-feature KMeans, because the
components live in the graph's structure. But that is precisely the heavy route:
eigendecompositions and learned embeddings are what turn this into the multi-hour
job at scale. Connected components is `O(transactions)` and exact. So the library
wins on **time** even against the "right" ML, and on **correctness and simplicity**
against the clustering approach analysts most commonly reach for first.

And the two compose: if you still want to cluster *behaviour within* a book, the
library hands ML clean, exactly-bounded groups to work inside — so the model never
has to rediscover the partition.
