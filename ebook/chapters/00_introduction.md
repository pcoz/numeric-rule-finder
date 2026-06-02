[🏠 Home](../index.md) · ← Previous · [Next: How it works →](01_how_it_works.md)

---

# 1 · The tool space: what this is, and what it isn't

Before reaching for any tool, it helps to know which shelf it belongs on. So
picture the tools that touch a table of numbers. Broadly, they fall into four
families:

- **Spreadsheets and BI dashboards** — they *summarise* the numbers: totals,
  trends, pivots, charts.
- **Solvers and optimisers** — they *find the best* numbers: the cheapest
  schedule, the optimal allocation.
- **ML and anomaly-detection systems** — they *learn patterns* in the numbers
  and score what looks unusual.
- **Enterprise platforms** — reconciliation suites, process-mining tools,
  data-observability products — which do a little of all of the above, wrapped
  in workflow, connectors, and integration.

This library sits in a gap that none of those quite fills. Its question is not
*"what's the total?"*, *"what's optimal?"*, or *"what looks unusual?"* It is:

> **What quantity is this data *supposed* to keep balanced, and exactly where
> and how does that break?**

That is a *structural* question, and — unlike "what looks unusual?" — it has an
exact answer. The library is a **conservation-law engine**. It works out which
combinations of your categories stay invariant under every transaction, finds
those laws even when nobody declared them, and then classifies any imbalance
precisely: is value genuinely missing, or merely mis-attributed? Are two ledgers
secretly independent? Do three reports contradict one another in a way that no
single correction can resolve?

## What it *is*

- **A discoverer of invariants.** Hand it a log of movements and it tells you
  what stays balanced — including structure nobody wrote down, such as the fact
  that your data is really *two* independent books, or that stock only ever
  moves in cases of twelve.
- **An exact diagnostician.** Every answer is computed in exact arithmetic —
  there is no floating-point fuzz — and is a *deduction*, not an estimate or a
  score.
- **Honest by design.** If there is no conserved quantity to check, it says so
  and stops. It will never manufacture a reconciliation that isn't there.

## What it is *not*

- **Not a solver or optimiser.** It will not find the cheapest schedule or the
  best allocation; it checks and explains *balance* and *structure*.
- **Not ML, and not anomaly rules.** It writes no heuristics and learns no
  thresholds. A violation is caught because it breaks a *law*, not because it
  matches a pattern someone trained.
- **Not a BI tool or an enterprise platform.** It ships no dashboards,
  connectors, or close-workflow. It is a small, exact engine you point at a
  table — quick to start, and easy to wrap inside something larger.

## Where it earns its place

Its honest home is the **mid-structure zone**: data that genuinely carries a
conservation law — ledgers, inventory, meters, pipelines, headcount, points
economies, reaction networks — but that is too small, too generic, or too novel
to have spawned its own dedicated tool. There, three of its abilities are hard
to find elsewhere:

1. **Discovery.** It finds the invariant for you, instead of making you declare
   it up front.
2. **Typing.** It tells you *what kind* of imbalance you have — a genuine loss
   versus a mere re-attribution — rather than only flagging that one exists.
3. **Cross-source judgement.** It can prove that a set of independent
   reconciliations *cannot all be true* — without anyone maintaining a master
   ledger.

The next chapter shows the single idea that makes all of this possible, and the
five depths at which it operates.

---

[🏠 Home](../index.md) · ← Previous · [Next: How it works →](01_how_it_works.md)
