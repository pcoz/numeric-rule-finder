# Numeric Rule Finder

An exact, dependency-light library that **discovers** the conservation laws latent
in structured movement/transaction data, instead of making you declare one.

You declare nothing. It recovers the **complete lattice of independent
conservation laws the data actually obeys** — including laws nobody wrote down —
finds where they break, types each break (a re-attributable slip vs. a genuine
hole), and **honest-stops** when there is no structure to exploit.

## Two front doors

* **Just want answers? (no maths)** — start with the headline walkthrough,
  *Closing the month at Northwind Retail*, in
  [`BUSINESS_GUIDE.md`](BUSINESS_GUIDE.md#headline-walkthrough--closing-the-month-at-northwind-retail)
  (run it: [`examples/northwind_close/`](examples/northwind_close/)). Six
  plain-English checks, each ending in an action. Then use
  `python -m numeric_rule_finder.cli` (or `from numeric_rule_finder import Reconciler`)
  on your own data: hand it a CSV and two column names; it tells you what balances,
  where it breaks and probably why, finds hidden separate sub-systems, and — being
  *intelligent* — silently escalates to the deeper maths (e.g. modular/parity
  structure) when ordinary balancing finds nothing, reporting it in plain words.
  Works across domains (accounting, energy, supply chain, ETL, clinical trials,
  elections, …): `python examples/gamut/gamut_demo.py`.
* **Want the mathematics?** — read the ebook
  **[Appendix — The mathematics](ebook/chapters/A_appendix_mathematics.md)**. The
  engine lives in the `numeric_rule_finder/` package.

## How it works (in brief)

It treats your data as signed **movements** — a *group*, a *bucket*, an *amount* —
and finds the weighted combinations of buckets that every movement leaves
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

## What it finds — more than one law

If real data only ever had the single obvious balance, "discover the laws" would
add nothing. It doesn't:

| dataset | kind | independent laws | what was discovered |
|---|---|---|---|
| `ledger_connected` | synthetic | **1** | the one nets-to-zero law |
| `ledger_two_books` | synthetic | **2** | two disjoint books — *structure nobody declared* |
| `michaelis_menten` | synthetic | **2** | enzyme moiety `E + ES` and substrate-matter `S + ES + P` |
| `inventory_two_skus` | synthetic | **2** | per-SKU stock conserved across locations |
| `no_structure` | synthetic | **0** | **honest stop** — refuses to reconcile |
| `resource_lock` | **real petra-nn net** | **3** | each client token **plus** the mutex/resource invariant |
| `mapk_pathway` | **real Pathway Commons SIF** | **1** | total molecule count over the cascade |

And it goes further than ML where the signal is an exact law: it beats an
Isolation Forest outright on skim fraud, and *feeds* a Random Forest as an exact
pre-filter + feature — see [`examples/fraud_vs_ml/`](examples/fraud_vs_ml/) and
[`examples/ml_assist/`](examples/ml_assist/).

## Layout

```
numeric_rule_finder/   the library (analyst + cli + the math layers)
examples/              one self-contained subfolder per example/demo, each with a README
ebook/                 the book: seven chapters + a mathematics appendix
tests/                 the test suite (59 passing)
```

`numeric_rule_finder.invariants` has **no third-party dependencies**;
`petra_adapter` uses `petra-nn` *only* to read Petri nets; the ML examples use
`scikit-learn`.

## Run

```bash
pip install -e .                                      # optional (pure-stdlib core)
python -m numeric_rule_finder.cli check data.csv --group txn_id --amount amount
python examples/northwind_close/close_the_books.py    # a worked example
python examples/gamut/gamut_demo.py                   # the same engine across domains
python -m pytest tests examples -q                    # the suite
```

## Roadmap

* **Stoichiometry-aware SIF/BioPAX** — recover atom/mass conservation where the
  source carries reaction stoichiometry.
* **Multivariate `ℚ[t₁,…,t_k]` parameters** — degeneracy *varieties* (Gröbner bases).
* **Polynomial / toric invariants** — multiplicative conserved quantities via the
  lattice ideal of the stoichiometric matrix.
* **Cellular sheaves with non-constant stalks** — full sheaf Laplacian over the nerve.

## License

MIT-with-attribution — see [`LICENSE`](LICENSE).
