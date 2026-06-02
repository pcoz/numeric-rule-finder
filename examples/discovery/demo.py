"""
demo.py — run conservation-law discovery and answer "more than one law?"
========================================================================

Three parts:
  1. Synthesized datasets with known law counts (ground-truth check).
  2. REAL petra-nn nets (resource-lock mutex, manufacturing cell, and a real
     Pathway Commons MAPK SIF) — discovered via the petra-nn incidence bridge.
  3. A reconciliation demo: discover the law on a clean ledger, then check a
     corrupted ledger and read off the TYPED residual (which law broke, where).

Run:  python demo.py
"""

from pathlib import Path
from copy import deepcopy

import sys as _sys
from pathlib import Path as _Path
for _root in _Path(__file__).resolve().parents:
    if (_root / "numeric_rule_finder").is_dir():
        _sys.path.insert(0, str(_root)); break

from numeric_rule_finder.invariants import discover_invariants, check_conservation
from numeric_rule_finder.datasets import ALL_DATASETS, ledger_connected, ENTITY, EVENT, QTY


def _print_discovery(name, disc, expected=None):
    tag = "HONEST STOP" if disc.honest_stop else f"{disc.n_laws} law(s)"
    exp = "" if expected is None else f"  (expected {expected})"
    print(f"\n=== {name} ===")
    print(f"  entities={len(disc.entities)}  events={len(disc.events)}  "
          f"rank={disc.rank}  ->  {tag}{exp}")
    if disc.honest_stop:
        print("  no conserved quantity on this data -- refuse to reconcile.")
        return
    for law in disc.minimal_semipositive or disc.laws:
        print(f"    conserved:  {law.render()}")


def run_synthesized():
    print("#" * 70)
    print("# 1. SYNTHESIZED DATASETS (ground-truth law counts)")
    print("#" * 70)
    for make in ALL_DATASETS:
        d = make()
        disc = discover_invariants(d["records"], d["entity_key"],
                                   d["event_key"], d["qty_key"])
        _print_discovery(d["name"], disc, d["expected_laws"])
        assert disc.n_laws == d["expected_laws"], (
            f"{d['name']}: discovered {disc.n_laws}, expected {d['expected_laws']}")


def run_petra_nets(examples_dir):
    print("\n" + "#" * 70)
    print("# 2. REAL petra-nn NETS (P-invariants via the incidence bridge)")
    print("#" * 70)
    try:
        from numeric_rule_finder.petra_adapter import petrinet_from_scenario, discover_petrinet_invariants
    except Exception as exc:  # pragma: no cover
        print(f"  [skipped] petra-nn not available: {exc}")
        return
    if not examples_dir:
        print("  [skipped] pass a petra-nn examples dir as an argument to include the Petri-net section.")
        return
    examples_dir = Path(examples_dir)
    if not examples_dir.exists():
        print(f"  [skipped] examples dir not found: {examples_dir}")
        return
    for scenario in ("resource_lock", "manufacturing_cell", "mapk_pathway"):
        toml = examples_dir / scenario / "scenario.toml"
        if not toml.exists():
            print(f"  [skipped] {scenario}: no scenario.toml")
            continue
        try:
            net = petrinet_from_scenario(toml)
            disc = discover_petrinet_invariants(net)
            _print_discovery(f"{scenario}  (real petra-nn net)", disc)
        except Exception as exc:  # pragma: no cover
            print(f"  [skipped] {scenario}: {exc}")


def run_reconciliation():
    print("\n" + "#" * 70)
    print("# 3. RECONCILIATION -- discover the law, then type the residual")
    print("#" * 70)
    clean = ledger_connected()
    disc = discover_invariants(clean["records"], ENTITY, EVENT, QTY)
    print(f"\n  Discovered {disc.n_laws} law on the clean book:")
    for law in disc.laws:
        print(f"    {law.render()}")

    # Corrupt: drop transaction t2's counter-entry (the -250 to expense).
    corrupt = [r for r in deepcopy(clean["records"])
               if not (r[EVENT] == "t2" and r[ENTITY] == "expense")]
    print("\n  Now check a corrupted book (t2 is missing its -250 counter-entry):")
    report = check_conservation(corrupt, disc.laws, ENTITY, EVENT, QTY)
    for law, total, violators in report:
        print(f"    law  [{law.render()}]")
        print(f"      total residual over the book: {total}")
        for ev, val in violators:
            print(f"      VIOLATED at event {ev!r}: residual {val}")


if __name__ == "__main__":
    import sys
    examples_dir = sys.argv[1] if len(sys.argv) > 1 else None
    run_synthesized()
    run_petra_nets(examples_dir)
    run_reconciliation()
    print("\nDone.")
