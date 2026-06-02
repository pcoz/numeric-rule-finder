"""
depth_demo.py — the integer/topological depth layer
===================================================

One Smith Normal Form engine (snf.py) drives two things:

  A. MODULAR conservation laws — the torsion of coker(S). Structure that is
     invisible over Q (parity, CRT-fused residues) but present over Z.

  B. INTEGRAL HOMOLOGY — Betti numbers + torsion of a chain complex / the
     reconciliation overlap nerve, the higher-cohomology home of the residual.

Run:  python depth_demo.py
"""

import sys as _sys
from pathlib import Path as _Path
for _root in _Path(__file__).resolve().parents:
    if (_root / "numeric_rule_finder").is_dir():
        _sys.path.insert(0, str(_root)); break

from numeric_rule_finder.integer_invariants import integer_conservation, cross_check_free_rank
from numeric_rule_finder.homology import SimplicialComplex, chain_homology, nerve
from numeric_rule_finder import datasets as D


def part_a_modular():
    print("#" * 70)
    print("# A. MODULAR CONSERVATION LAWS (torsion of coker S, via SNF)")
    print("#" * 70)
    for make in D.INTEGER_DATASETS:
        d = make()
        idisc = integer_conservation(d["records"], d["entity_key"],
                                     d["event_key"], d["qty_key"])
        print(f"\n=== {d['name']} ===")
        print(f"  conservation laws over Q: {idisc.free_rank}    "
              f"torsion of coker(S): {idisc.torsion}")
        if idisc.has_hidden_structure:
            print("  >>> NOTHING is conserved over Q, but Z reveals hidden structure:")
        for ml in idisc.modular_laws:
            print(f"    modular:  {ml.render()}")
        for el in idisc.exact_laws:
            print(f"    exact  :  {el.render()}")

    print("\n-- cross-check: integer free rank == Q-dimension on every additive dataset --")
    for make in D.ALL_DATASETS:
        d = make()
        q, z, ok = cross_check_free_rank(d["records"], d["entity_key"],
                                         d["event_key"], d["qty_key"])
        print(f"    {d['name']:18s}  Q={q}  Z_free={z}  {'OK' if ok else 'MISMATCH'}")


def part_b_homology():
    print("\n" + "#" * 70)
    print("# B. INTEGRAL HOMOLOGY (Betti + torsion, same SNF engine)")
    print("#" * 70)

    print("\n-- known spaces (validation) --")
    for name, facets in [
        ("circle S^1", [(0, 1), (1, 2), (0, 2)]),
        ("sphere S^2 (H_2!)", [(0, 1, 2), (0, 1, 3), (0, 2, 3), (1, 2, 3)]),
        ("filled triangle (disk)", [(0, 1, 2)]),
    ]:
        print(f"  {name}:")
        print(SimplicialComplex.from_facets(facets).homology().render())

    print("\n  Moore space M(Z/2,1) -- torsion, built from raw boundaries d2=[[2]]:")
    print(chain_homology([1, 1, 1], [[[0]], [[2]]]).render())

    print("\n-- the reconciliation OVERLAP NERVE (constant-sheaf cohomology) --")
    cases = {
        "pairwise-only overlaps (cycle)":
            {"A": {"g1", "g2"}, "B": {"g2", "g3"}, "C": {"g1", "g3"}},
        "all share one group (filled)":
            {"A": {"g"}, "B": {"g"}, "C": {"g"}},
        "every triple overlaps, no common-to-four (hollow sphere)":
            {"A": {"gABC", "gABD", "gACD"}, "B": {"gABC", "gABD", "gBCD"},
             "C": {"gABC", "gACD", "gBCD"}, "D": {"gABD", "gACD", "gBCD"}},
    }
    for name, cover in cases.items():
        hom = nerve(cover).homology()
        h1 = hom.betti[1] if len(hom.betti) > 1 else 0
        h2 = hom.betti[2] if len(hom.betti) > 2 else 0
        note = ("H_1 -> reconciliation cycle" if h1 else
                "H_2 -> hollow-sphere overlap" if h2 else "contractible -> no obstruction")
        print(f"\n  {name}:  ({note})")
        print(nerve(cover).homology().render())


if __name__ == "__main__":
    part_a_modular()
    part_b_homology()
    print("\nDone.")
