"""
homology.py — integral homology (Betti numbers + torsion) via the SNF engine
=============================================================================

The *same* Smith Normal Form that exposes modular conservation laws computes
the integral homology of a chain complex. For boundary maps

    ... --∂_{k+1}--> C_k --∂_k--> C_{k-1} --> ...

the homology H_k = ker ∂_k / im ∂_{k+1} has

    Betti_k   = dim C_k - rank ∂_k - rank ∂_{k+1}          (free rank)
    torsion_k = the invariant factors d > 1 of ∂_{k+1}     (⊕ Z/d)

So one routine — SNF of each boundary matrix — yields both the Betti numbers
(rank from the count of nonzero invariant factors) and the torsion (the
factors > 1). This is the higher-cohomology layer: the conservation residual
lives in H^1 of the reconciliation nerve, and that nerve can have genuine
H^2 (a hollow sphere of overlaps) or torsion.

`SimplicialComplex.from_facets` builds the oriented boundary matrices of an
abstract simplicial complex; `chain_homology` works on any integer boundary
matrices (geometric or purely algebraic).
"""

from __future__ import annotations
from dataclasses import dataclass
from itertools import combinations

from .snf import smith_normal_form, invariant_factors


def _rank(matrix):
    if not matrix or not matrix[0]:
        return 0
    D, _, _ = smith_normal_form(matrix)
    return len(invariant_factors(D))


@dataclass
class Homology:
    betti: list           # betti[k] = free rank of H_k
    torsion: list         # torsion[k] = [d_1, d_2, ...] (each > 1) of H_k

    def render(self):
        lines = []
        for k in range(len(self.betti)):
            tors = self.torsion[k] if k < len(self.torsion) else []
            tstr = "".join(f" (+) Z/{d}" for d in tors)
            free = f"Z^{self.betti[k]}" if self.betti[k] else "0"
            lines.append(f"  H_{k} = {free}{tstr}")
        return "\n".join(lines)


def chain_homology(dims, boundaries):
    """Homology of a chain complex.

    dims:        [n_0, n_1, ...] = dim C_k.
    boundaries:  [B_1, B_2, ...] where B_k = ∂_k is an (n_{k-1} x n_k) integer
                 matrix. (B_0 = 0 is implicit.)
    """
    top = len(dims)
    # rank of ∂_k for k = 0..top  (∂_0 = 0; ∂_k for k > len(boundaries) = 0)
    rank = [0] * (top + 1)
    for k in range(1, top + 1):
        if k - 1 < len(boundaries) and boundaries[k - 1]:
            rank[k] = _rank(boundaries[k - 1])

    betti, torsion = [], []
    for k in range(top):
        bk = dims[k] - rank[k] - (rank[k + 1] if k + 1 <= top else 0)
        betti.append(bk)
        # torsion of H_k comes from the invariant factors of ∂_{k+1}
        tk = []
        if k < len(boundaries):
            D, _, _ = smith_normal_form(boundaries[k]) if boundaries[k] else (None, None, None)
            if D is not None:
                tk = [d for d in invariant_factors(D) if d > 1]
        torsion.append(tk)
    return Homology(betti=betti, torsion=torsion)


@dataclass
class SimplicialComplex:
    simplices: dict        # k -> sorted list of k-simplices (tuples of vertices)

    @classmethod
    def from_facets(cls, facets):
        """Build the full complex from a list of facets (max faces). Each facet
        is a tuple/list of vertices; all sub-faces are generated."""
        by_dim = {}
        for facet in facets:
            verts = tuple(sorted(facet))
            for k in range(len(verts)):
                for combo in combinations(verts, k + 1):
                    by_dim.setdefault(k, set()).add(combo)
        simplices = {k: sorted(s) for k, s in by_dim.items()}
        return cls(simplices)

    def boundary_matrices(self):
        """List [∂_1, ∂_2, ...] with ∂_k of shape (#(k-1)-simplices x #k-simplices)."""
        dims = []
        kmax = max(self.simplices) if self.simplices else -1
        for k in range(kmax + 1):
            dims.append(len(self.simplices.get(k, [])))
        boundaries = []
        for k in range(1, kmax + 1):
            lower = self.simplices.get(k - 1, [])
            upper = self.simplices.get(k, [])
            index = {s: i for i, s in enumerate(lower)}
            B = [[0] * len(upper) for _ in range(len(lower))]
            for j, simp in enumerate(upper):
                for i in range(len(simp)):
                    face = simp[:i] + simp[i + 1:]
                    B[index[face]][j] += (-1) ** i
            boundaries.append(B)
        return dims, boundaries

    def homology(self):
        dims, boundaries = self.boundary_matrices()
        return chain_homology(dims, boundaries)


# ---------- reconciliation nerve: sheaf cohomology over the overlap cover ----

def nerve(cover, max_dim=3):
    """Nerve of a cover: vertices = sources, a k-simplex for every set of k+1
    sources with a non-empty common intersection.

    cover: dict source -> set of groups it reports.
    Returns a SimplicialComplex (the nerve), whose homology is the constant-
    sheaf cohomology of the reconciliation problem: H_1 != 0 means there are
    overlap cycles a global reconciliation must thread; H_2 != 0 means a
    hollow-sphere overlap pattern.
    """
    sources = sorted(cover, key=str)
    facets = []
    # include every simplex with non-empty common intersection, up to max_dim
    for k in range(1, min(max_dim, len(sources)) + 1):
        for combo in combinations(sources, k):
            common = set.intersection(*(set(cover[s]) for s in combo))
            if common:
                facets.append(combo)
    # also single sources (0-simplices), always present
    facets.extend((s,) for s in sources)
    return SimplicialComplex.from_facets(facets)
