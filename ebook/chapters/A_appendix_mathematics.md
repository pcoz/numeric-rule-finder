[🏠 Home](../index.md) · [← Previous: One engine, many number systems](08_substrate.md) · Next →

---

# Appendix · The mathematics

This appendix states, exactly, what the engine computes. The chapters deliberately
kept it off-screen; here it is in full. Everything is exact — integer and rational
arithmetic, never floating point — and each construction maps to a module in the
codebase.

## A.1 The model: the incidence matrix

Index the **buckets** (accounts, locations, …) by `i` and the **events**
(transactions, transfers, …) by `j`. The data is the **incidence matrix**

$$ S_{ij} = \text{net change of bucket } i \text{ caused by event } j. $$

(`invariants.build_incidence`.) Every question below is linear algebra on `S`.

## A.2 Conservation laws = the left null space

A **conservation law** is a weighting `y` of buckets left unchanged by every
event — exactly a vector with

$$ y^{\mathsf T} S = 0, $$

i.e. an element of the **left null space** of `S`. Over `ℚ` this is a vector
space; its dimension is the number of independent laws (`invariants.discover_invariants`).

- **Interpretable generators.** The nonnegative laws — *"this combination of
  buckets is conserved"* — are the **minimal semipositive invariants**, computed
  by the **Farkas algorithm** (the same objects known elsewhere as the
  P-invariants of a Petri net, or the conserved totals of a reaction network).
- **Separate books.** Buckets that never co-occur in an event form disconnected
  components; disjoint-support laws reveal independent sub-systems
  (`Reconciler.what_balances`).
- **Honest stop.** Left null space `= {0}` ⟹ no additive law ⟹ the tool refuses
  (and then escalates, A.3).

## A.3 Integer and modular structure: Smith Normal Form

"Nothing over `ℚ`" is not "no structure." Compute the **Smith Normal Form**
`U S V = D = diag(d₁, …, d_r)` with `d₁ | d₂ | … | d_r` (`snf.smith_normal_form`,
exact integer transforms). Then

$$ \operatorname{coker}(S) \;=\; \mathbb Z^{\text{buckets}} / \operatorname{im}(S)
\;\cong\; \mathbb Z^{\,\text{buckets}-r} \ \oplus\ \bigoplus_i \mathbb Z/d_i . $$

- The **free part** `ℤ^{buckets−r}` gives the exact integer laws; its rank equals
  the `ℚ`-dimension from A.2 (a built-in cross-check).
- Each **torsion summand** `ℤ/dᵢ` with `dᵢ > 1` is a law that holds **only modulo
  dᵢ** — e.g. parity (`d=2`), or "moves only in cases of 12" (`d=12`). The row of
  `U` for that factor is the conserved functional (`integer_invariants.integer_conservation`).

This torsion is the **Smith-Normal-Form / critical-group invariant** of the
incidence map — the canonical home of the modular structure, and the same `5`
that surfaces three times in the Meridian example.

## A.4 Typing the residual: the cokernel class

Take a reference model `S` and an **observed** net-change vector `b`. Its typed
residual is the class

$$ [b] \in \operatorname{coker}(S), \qquad \text{coordinates } (y_i^{\mathsf T} b)_i $$

against the conservation-law basis `{yᵢ}` (`cohomology.ConservationComplex.type_observation`).

| case | meaning | verdict |
|---|---|---|
| `[b] = 0` (every `yᵢ·b = 0`) | `b ∈ im(S)`: some event-flow `x` reproduces it (`Sx = b`) | **coboundary** — re-attributable; the witness `x` is returned |
| `[b] ≠ 0` | no event reconfiguration yields `b` | **obstruction** — a genuine hole, naming the violated law `yᵢ` and the amount `yᵢ·b` |

This is the *re-attribution vs. genuine loss* verdict, made exact (the
fundamental theorem of linear algebra: `im(S) = (\ker S^{\mathsf T})^\perp`).

## A.5 Multi-source consistency: H¹ of the discrepancy sheaf

Pairwise reconciliation reports `d_{uv}` (source `u`'s figure minus source `v`'s)
form a 1-cochain `ω` on the graph of sources. Its class in

$$ H^1 = \operatorname{coker}(\delta^0) $$

is the obstruction to a single global reconciliation (`cohomology.discrepancy_cohomology`).

- `[ω] = 0` ⟹ **coboundary**: per-source offsets `p_v` with `d_{uv} = p_u − p_v`
  reconcile everything at once.
- `[ω] ≠ 0` ⟹ an **irreducible cycle**: `d_{AB} + d_{BC} + d_{CA} ≠ 0`, so *no*
  choice of per-source corrections satisfies all reports. The reports cannot all
  be true. (Generalises, via the nerve of the overlap cover, to genuine higher
  cohomology — `homology.py`.)

## A.6 Broadening the substrate: any Euclidean domain

**Moved to [Chapter 9 · One engine, many number systems](08_substrate.md),** so the
formal core sits beside its worked example. There you'll find the Euclidean-domain
table (ℚ, 𝔽ₚ, ℤ, ℚ[t]), the 𝔽ₚ dimension identity
`dim_𝔽ₚ = dim_ℚ + #{ dᵢ : p | dᵢ }`, and parametric conservation over ℚ[t] (laws as
polynomials in a parameter; their roots are the degeneracy loci) — run end to end
in `examples/substrate/`.

## A.7 Map of the code

| concept | module |
|---|---|
| incidence, `ℚ` laws, Farkas | `invariants.py` |
| Smith Normal Form (engine) | `snf.py` |
| integer + modular laws | `integer_invariants.py` |
| residual typing, discrepancy `H¹` | `cohomology.py` |
| homology with torsion (nerve) | `homology.py` |
| Euclidean-domain substrate | `euclidean.py`, `generic_linalg.py` |
| `𝔽ₚ`, parametric `ℚ[t]` | `substrate.py` |
| plain-language facade | `analyst.py` |

---

[🏠 Home](../index.md) · [← Previous: One engine, many number systems](08_substrate.md) · Next →
