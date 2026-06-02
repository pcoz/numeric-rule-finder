# Numeric Rule Finder

An exact, dependency-light library that **discovers** the conservation laws latent
in structured movement/transaction data, instead of making you declare one.

You declare nothing. It recovers the **complete lattice of independent
conservation laws the data actually obeys** — including laws nobody wrote down —
finds where they break, types each break (a re-attributable slip vs. a genuine
hole), and **honest-stops** when there is no structure to exploit.

## Two front doors

**Just want answers? (no maths).**

* **See it in action** — the headline walkthrough, *Closing the month at Northwind
  Retail*, in
  [`BUSINESS_GUIDE.md`](BUSINESS_GUIDE.md#headline-walkthrough--closing-the-month-at-northwind-retail):
  six plain-English checks, each ending in an action (run it:
  [`examples/northwind_close/`](examples/northwind_close/)).
* **On your own data** — `python -m numeric_rule_finder.cli` (or
  `from numeric_rule_finder import Reconciler`); hand it a CSV and two column names.
* **What you get** — what balances, where it breaks and probably why, and any
  hidden *separate sub-systems*.
* **It's intelligent** — when ordinary balancing finds nothing, it silently
  escalates to the deeper maths (e.g. modular/parity structure) and reports it in
  plain words.
* **Across domains** — accounting, energy, supply chain, ETL, clinical trials,
  elections, …: `python examples/gamut/gamut_demo.py`.

**Want the mathematics?** — read the ebook
**[Appendix — The mathematics](ebook/chapters/A_appendix_mathematics.md)**. The
engine lives in the `numeric_rule_finder/` package.

## How it works (in brief)

Numeric Rule Finder treats your data as signed **movements** — a *group*, a
*bucket*, an *amount* — and finds the weighted combinations of buckets that every movement leaves
unchanged (the conservation laws), then measures exactly where they break. It
climbs only as far as it needs:

* **balance & structure** — which groups don't net out; which buckets form hidden
  *separate books*;
* **modular laws** — patterns invisible to ordinary arithmetic ("moves only in
  cases of 12", parity), via Smith Normal Form;
* **typed residuals** — is a break re-attributable (a *coboundary*) or a genuine
  hole (an *obstruction* that names the violated law)?
* **multi-source consistency** — whether independent reconciliations can all be
  true at once (an `H¹` obstruction);
* **substrate generality** — the same engine over ℤ, ℚ, 𝔽ₚ, and ℚ[t]
  (parametric, rate-dependent laws).

Everything is exact (integer/rational arithmetic, never floating point). **The
actual mathematics** — definitions, theorems, the `coker(S)` / `H¹` residual
typing, Smith Normal Form, and a map of the code — is in the ebook
**[Appendix — The mathematics](ebook/chapters/A_appendix_mathematics.md)**.

## Real data carries more than one law

Point it at a dataset and it reports how many *independent* conservation laws
hold. Real data routinely has several — separate books, conserved moieties,
per-SKU stock — not just the one obvious balance:

| the data | laws found | what that means |
|---|---|---|
| a clean double-entry ledger | **1** | every transaction nets to zero |
| two ledgers that never share a transaction | **2** | they are really **separate books** — nobody had declared that |
| a stock network with two products | **2** | each product's stock is conserved on its own |
| an enzyme reaction network | **2** | two conserved quantities (the enzyme, and total substrate) |
| a shared-resource / mutex process | **3** | each client's work-item **plus** the resource invariant |
| data with no balancing structure | **0** | **honest stop** — it refuses to invent a reconciliation |

And it goes further than ML where the signal is an exact law: it beats an
Isolation Forest outright on skim fraud, and *feeds* a Random Forest as an exact
pre-filter + feature — see [`examples/fraud_vs_ml/`](examples/fraud_vs_ml/) and
[`examples/ml_assist/`](examples/ml_assist/).

`numeric_rule_finder` has **no third-party dependencies**; `petra_adapter` uses
`petra-nn` *only* to read Petri nets, and the ML examples use `scikit-learn`.

## Run

```bash
pip install -e .                                      # optional (pure-stdlib core)
python -m numeric_rule_finder.cli check data.csv --group txn_id --amount amount
python examples/northwind_close/close_the_books.py    # a worked example
python examples/gamut/gamut_demo.py                   # the same engine across domains
python -m pytest tests examples -q                    # the suite
```

## License

MIT-with-attribution — see [`LICENSE`](LICENSE).
