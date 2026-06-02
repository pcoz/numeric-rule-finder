"""
petra_adapter.py — conservation-law (P-invariant) discovery on petra-nn nets
============================================================================

This is the bridge that lets the pure-stdlib discovery in `invariants.py`
run directly on real Petri nets built with `petra-nn`
(`pip install petra-nn`). It reuses petra-nn's own incidence machinery —
the `PetriNet` flow relation and per-arc `weight()` — to build the
incidence matrix; nothing about the linear algebra is re-implemented here.

A **P-invariant** of a Petri net is exactly a conservation law: a weighting
of places whose weighted token total is unchanged by *every* transition
firing. It is the left null space of the incidence matrix C, where

    C[place][transition] = tokens produced - tokens consumed
                         = weight(transition, place) - weight(place, transition).

Inhibitor arcs are (correctly) ignored: they are guards, not part of the
flow relation, so they cannot change what is conserved.

petra-nn is an OPTIONAL dependency — only the functions that load/convert a
petra-nn `PetriNet` import it (lazily). The discovery itself is dependency-free.
"""

from __future__ import annotations
import tomllib
from pathlib import Path

from .invariants import discover_invariants, check_conservation


def incidence_records(net):
    """Convert a petra-nn `PetriNet` into (place, transition, delta) records.

    Reuses `net.places`, `net.transitions`, `net.flow`, and `net.weight()` —
    petra-nn's own structural representation — so the incidence is exactly
    what the framework's token game uses.
    """
    records = []
    for t in sorted(net.transitions):
        for p in sorted(net.places):
            produced = net.weight(t, p) if (t, p) in net.flow else 0
            consumed = net.weight(p, t) if (p, t) in net.flow else 0
            delta = produced - consumed
            if delta != 0:
                records.append({"place": p, "transition": t, "delta": delta})
    return records


def discover_petrinet_invariants(net):
    """Discover every conservation law (P-invariant) of a petra-nn `PetriNet`."""
    return discover_invariants(incidence_records(net), "place", "transition", "delta")


def petrinet_from_scenario(toml_path):
    """Build a petra-nn `PetriNet` from an example `scenario.toml`.

    Honours the scenario's `net.source`:
      * "inline"   — build from the TOML place/transition/arc tables via
                     petra-nn's PetriNet API,
      * "sif_file" — parse a Pathway Commons SIF file via petra-nn's parser,
      * anything else — fall back to petra-nn's full `load_scenario(...).net`.
    """
    toml_path = Path(toml_path)
    with open(toml_path, "rb") as fh:
        cfg = tomllib.load(fh)
    source = cfg.get("net", {}).get("source", "inline")

    if source == "inline":
        from petri_net_nn import PetriNet
        net_cfg = cfg["net"]
        net = PetriNet()
        for pl in net_cfg.get("places", []):
            net.add_place(pl["id"], label=pl.get("label"),
                          tokens=int(pl.get("tokens", 0)))
        for tr in net_cfg.get("transitions", []):
            net.add_transition(tr["id"], label=tr.get("label"))
        for arc in net_cfg.get("arcs", []):
            net.add_arc(arc["src"], arc["dst"], weight=int(arc.get("weight", 1)))
        return net

    if source == "sif_file":
        from petri_net_nn.sif import parse_sif
        return parse_sif(toml_path.parent / cfg["net"]["path"])

    from petri_net_nn import load_scenario
    return load_scenario(toml_path).net
