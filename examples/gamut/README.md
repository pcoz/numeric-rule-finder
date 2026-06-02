# Demo — the same engine across many domains

> **Run:** `python examples/gamut/gamut_demo.py`

One facade, many domains — only the column names change. Runs balance checks,
hidden-structure discovery, modular escalation, and cross-system comparison over
the sample datasets in [`data/`](data/):

| domain | dataset | what it shows |
|---|---|---|
| Energy / utilities | `energy_grid.csv` | an unaccounted grid loss |
| Clinical trials | `clinical_trial.csv` | patients unaccounted for |
| Data engineering | `etl_rows.csv` | silently dropped rows |
| Elections | `ballots.csv` | ballots that don't reconcile |
| Supply chain | `supply_chain.csv` | two independent product lines |
| Inventory / packaging | `stock_pairs.csv` | auto-escalation to parity / case sizes |
| Two warehouse systems | `warehouse_a.csv`, `warehouse_b.csv` | cross-system disagreement |
