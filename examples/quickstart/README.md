# Quickstart data — try the CLI in ten seconds

Two tiny ledgers for kicking the tyres from the command line.

- `sample_ledger.csv` — a small balanced book with two hidden separate books.
- `sample_ledger_broken.csv` — the same, with a missing counter-entry and a
  duplicate line.

```bash
python -m numeric_rule_finder.cli check  examples/quickstart/sample_ledger_broken.csv --group txn_id --amount amount
python -m numeric_rule_finder.cli books  examples/quickstart/sample_ledger.csv        --group txn_id --amount amount --account account
python -m numeric_rule_finder.cli report examples/quickstart/sample_ledger.csv        --group txn_id --amount amount --account account
```
