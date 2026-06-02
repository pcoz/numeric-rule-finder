# Example — finding independent groups from the command line

> **Run:** `python -m numeric_rule_finder.cli groups examples/cli_groups/ledger.csv --group txn_id --account account`

No code, no maths — just a CSV. The `groups` subcommand returns the **exact
independent groups**: sets of accounts linked, directly or transitively, through
shared transactions. It's the fast union-find path (`Reconciler.independent_groups`),
so it needs only the linking column and the account column — no amount, no `k`,
no clustering.

[`ledger.csv`](ledger.csv) mixes three unrelated sets of books into one file.

## Result (actual output)

```text
Found 3 independent groups among 7 accounts (each a set linked, directly or transitively, through shared 'txn_id'):
  group 1: 3 accounts  [cash, expense, revenue]
  group 2: 2 accounts  [cogs, inventory]
  group 3: 2 accounts  [wage_expense, wages_payable]
```

Nobody told it there were three books — it read them off the structure.

## The other subcommands, same file

```bash
# does every transaction balance?
python -m numeric_rule_finder.cli check  examples/cli_groups/ledger.csv --group txn_id --amount amount
#   -> All 6 txn_id(s) balance. Every group's amount adds up to zero.

# full plain-language report (balance + structure + any hidden modular laws)
python -m numeric_rule_finder.cli report examples/cli_groups/ledger.csv --group txn_id --amount amount --account account
```

`groups` is the fast structural view; `books` is the same idea routed through the
full exact discovery (which also reports what stays balanced and escalates to
modular laws when nothing balances over ordinary arithmetic).
