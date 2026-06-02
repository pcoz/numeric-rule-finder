"""
cohomology_demo.py — type reconciliation residuals as cohomology obstructions
=============================================================================

Part A: the conservation complex. A reference model (clean ledger / a real
        petra-nn net) defines S; observed imbalances are typed by their class
        in coker(S) — coboundary (resolvable, with a witness flow) vs genuine
        obstruction (names the violated conserved quantity).

Part B: the discrepancy sheaf. Pairwise reconciliation reports are typed by
        their class in H^1 — coboundary (per-ledger offsets reconcile) vs
        irreducible cycle (the matching boundary).

Run:  python cohomology_demo.py
"""

import sys as _sys
from pathlib import Path as _Path
for _root in _Path(__file__).resolve().parents:
    if (_root / "numeric_rule_finder").is_dir():
        _sys.path.insert(0, str(_root)); break

from numeric_rule_finder.cohomology import ConservationComplex, discrepancy_cohomology
from numeric_rule_finder.datasets import ledger_connected, ENTITY, EVENT, QTY


def part_a_ledger():
    print("#" * 70)
    print("# A. CONSERVATION COMPLEX -- residual class in coker(S)")
    print("#" * 70)
    ref = ledger_connected()
    complex_ = ConservationComplex.from_records(ref["records"], ENTITY, EVENT, QTY)
    print(f"\nReference model: {len(complex_.events)} events, "
          f"{len(complex_.laws)} conservation law(s):")
    for law in complex_.laws:
        print(f"  {law.render()}")

    print("\n-- observation 1: cash +30, revenue -30 (a re-attributed amount) --")
    tr = complex_.type_observation({"cash": 30, "revenue": -30})
    print("  " + tr.render())

    print("\n-- observation 2: cash +250 with no counter-entry --")
    tr = complex_.type_observation({"cash": 250})
    print("  " + tr.render())


def part_a_petrinet(examples_dir):
    from pathlib import Path
    if not examples_dir:
        print("  [skipped] pass a petra-nn examples dir to include the Petri-net section.")
        return
    toml = Path(examples_dir) / "resource_lock" / "scenario.toml"
    if not toml.exists():
        print("\n  [skipped] resource_lock scenario not present")
        return
    try:
        from numeric_rule_finder.petra_adapter import petrinet_from_scenario
    except Exception as exc:
        print(f"\n  [skipped] petra-nn not available: {exc}")
        return
    net = petrinet_from_scenario(toml)
    complex_ = ConservationComplex.from_petrinet(net)
    print("\n-- real petra-nn net (resource_lock), "
          f"{len(complex_.laws)} P-invariants --")

    print("\n   observation A: one firing of t_serve_a "
          "(p_a_pending -1, p_a_done +1, p_resource_busy +1)")
    tr = complex_.type_observation(
        {"p_a_pending": -1, "p_a_done": 1, "p_resource_busy": 1})
    print("   " + tr.render())

    print("\n   observation B: a served token appears (p_a_done +1) with nothing consumed")
    tr = complex_.type_observation({"p_a_done": 1})
    print("   " + tr.render())


def part_b_sheaf():
    print("\n" + "#" * 70)
    print("# B. DISCREPANCY SHEAF -- class of pairwise discrepancies in H^1")
    print("#" * 70)

    print("\n-- three ledgers, consistent: A-B=5, B-C=-3, A-C=2 --")
    coh = discrepancy_cohomology({("A", "B"): 5, ("B", "C"): -3, ("A", "C"): 2})
    print("  " + coh.render())

    print("\n-- three ledgers, inconsistent: A-B=5, B-C=5, C-A=5 (cycle sums to 15) --")
    coh = discrepancy_cohomology({("A", "B"): 5, ("B", "C"): 5, ("C", "A"): 5})
    print("  " + coh.render())


if __name__ == "__main__":
    import sys
    examples = sys.argv[1] if len(sys.argv) > 1 else None
    part_a_ledger()
    part_a_petrinet(examples)
    part_b_sheaf()
    print("\nDone.")
