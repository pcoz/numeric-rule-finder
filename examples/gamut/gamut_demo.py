"""
gamut_demo.py — the same engine, many domains (none of them accounting-specific)
================================================================================

Conservation/balance reconciliation applies wherever a signed quantity must net
out within a group, or where hidden sub-systems / modular invariants lurk. Every
case below runs through the SAME `Reconciler` facade — only the column names and
the framing change.

Run:  python gamut_demo.py
"""

from pathlib import Path
import sys as _sys
from pathlib import Path as _Path
for _root in _Path(__file__).resolve().parents:
    if (_root / "numeric_rule_finder").is_dir():
        _sys.path.insert(0, str(_root)); break

from numeric_rule_finder.analyst import Reconciler

EX = Path(__file__).resolve().parent / "data"


def show(title, framing, text):
    print("\n" + "=" * 70)
    print(title)
    print("  " + framing)
    print("-" * 70)
    print(text)


def main():
    # --- per-group BALANCE checks across domains -------------------------
    show("ENERGY GRID (utilities metering)",
         "generation should equal consumption + losses each interval",
         Reconciler.from_csv(EX / "energy_grid.csv")
         .balance_check(group="interval", amount="kwh").summary())

    show("CLINICAL TRIAL (patient accountability)",
         "enrolled should equal completed + withdrawn + ongoing per site",
         Reconciler.from_csv(EX / "clinical_trial.csv")
         .balance_check(group="site", amount="patients").summary())

    show("DATA PIPELINE (ETL row-count conservation)",
         "rows ingested should equal rows loaded + rows rejected per run",
         Reconciler.from_csv(EX / "etl_rows.csv")
         .balance_check(group="run", amount="rows").summary())

    show("ELECTION (ballot reconciliation)",
         "ballots issued should equal cast + spoiled + unused per precinct",
         Reconciler.from_csv(EX / "ballots.csv")
         .balance_check(group="precinct", amount="ballots").summary())

    # --- hidden-structure DISCOVERY --------------------------------------
    show("SUPPLY CHAIN (find independent product lines)",
         "which locations never exchange stock? (separate sub-networks)",
         Reconciler.from_csv(EX / "supply_chain.csv")
         .what_balances(account="node", group="move", amount="units").summary())

    show("INVENTORY / PACKAGING (auto-escalates to modular structure)",
         "goods only ever move in pairs -> nothing balances, but parity does",
         Reconciler.from_csv(EX / "stock_pairs.csv")
         .what_balances(account="bin", group="move_id", amount="qty").summary())

    # --- cross-system COMPARE --------------------------------------------
    a = Reconciler.from_csv(EX / "warehouse_a.csv")
    b = Reconciler.from_csv(EX / "warehouse_b.csv")
    diffs = a.compare(b, group="sku", amount="qty")
    show("TWO WAREHOUSE SYSTEMS (cross-system reconciliation)",
         "do system A and system B agree on per-SKU quantities?",
         "They agree." if not diffs else "\n".join("  - " + d for d in diffs))


if __name__ == "__main__":
    main()
    print("\nDone.")
