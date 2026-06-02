[🏠 Home](../index.md) · [← Previous: The Meridian Tontine](04_example_meridian.md) · [Next: This method vs. ML →](06_vs_ml.md)

---

# 6 · Where it fits, and how to use it on your own data

Three examples, three audiences: an analyst closing a month, a platform team
catching exploits with no rules, and an architect watching the full machinery run.
All three are the same engine, pointed at different data and asked different
questions.

## It travels across domains

The column names change; the questions do not. Anywhere a signed quantity should
net out within a group, the tool applies directly:

| domain | group | amount | what a break means |
|---|---|---|---|
| **Accounting** | transaction | debit/credit | unbalanced entry, duplicate, missing leg |
| **Energy / utilities** | interval | kWh (gen +, use/loss −) | unaccounted loss or a mis-read meter |
| **Supply chain / inventory** | transfer | units in/out | shrinkage, miscount, or separate stock pools |
| **Data engineering (ETL)** | pipeline run | rows in/out/rejected | silently dropped rows |
| **Clinical trials** | site | patients (enrolled +, exited −) | patients unaccounted for |
| **Elections** | precinct | ballots issued/cast/spoiled | ballots that don't reconcile |
| **Manufacturing** | batch | mass in/out/scrap | yield loss / mass-balance error |
| **Loyalty / gaming** | event | points earned/spent | duplication exploits, mis-reporting |

## Using it on your own data

You need a table — a CSV or a spreadsheet export — with at least:

- a **group** column (what each line belongs to and should balance within);
- a signed **amount** column (in is positive, out is negative);
- optionally an **account / category / location** column.

Then, from the command line:

```bash
python -m numeric_rule_finder.cli check    yourdata.csv --group txn_id --amount amount
python -m numeric_rule_finder.cli books    yourdata.csv --group txn_id --amount amount --account account
python -m numeric_rule_finder.cli report   yourdata.csv --group txn_id --amount amount --account account
python -m numeric_rule_finder.cli compare  system_a.csv system_b.csv --group txn_id --amount amount
```

Or from a notebook, where every result is a plain sentence you can print or log:

```python
from numeric_rule_finder import Reconciler, cross_check, account_for_movement

r = Reconciler.from_csv("yourdata.csv")
print(r.balance_check(group="txn_id", amount="amount").summary())
print(r.what_balances(account="account", group="txn_id", amount="amount").summary())
print(r.diagnose_breaks(group="txn_id", amount="amount", account="account").summary())
```

## Two promises, restated

- **Exact.** Amounts are exact numbers; `100.00` really is `100.00`, with no
  floating-point drift to explain away.
- **Honest.** If the data carries no quantity that should stay balanced, the tool
  says so and stops. It will never invent a reconciliation that isn't there.

## And when you want the proof

Everything in this book — the discovery, the modular invariants, the
re-attribution-versus-loss verdict, the multi-source consistency check — is exact
mathematics, and it is all available to inspect rather than take on faith. The
[Appendix](A_appendix_mathematics.md) lays out the machinery: conservation laws as
null spaces, modular structure via Smith Normal Form, residual typing through the
cokernel and `H¹`, and the parametric extension over `ℚ[t]`.

---

[🏠 Home](../index.md) · [← Previous: The Meridian Tontine](04_example_meridian.md) · [Next: This method vs. ML →](06_vs_ml.md)
