[🏠 Home](../index.md) · [← Previous: Raw XML showcase](07_xml_showcase.md) · [Next: Appendix →](A_appendix_mathematics.md)

---

# 9 · One engine, many number systems

> **Example:** [`examples/substrate/`](../../examples/substrate/README.md) ·
> **Run:** `python examples/substrate/substrate_demo.py`

The last chapter changed the *front door* — the file format the data arrives in.
This one changes something deeper: the **number system the laws are computed in**.
It is the same discovery engine throughout; we simply let it reason over richer
kinds of number, and in doing so it answers a question the earlier chapters
couldn't even phrase.

## Conservation isn't always over plain fractions

So far "conserved" has meant *a weighted total that stays fixed*, measured in
ordinary fractions (the field ℚ). But real structure shows up in other number
systems too:

- **whole numbers (ℤ).** Some laws hold only *modulo* something — "parity is
  preserved", "this only ever moves in lots of 12". Invisible over fractions;
  exact over the integers. (That's the modular escalation from Chapter 2, and the
  recurring `5` in the Meridian investigation.)
- **a finite field (𝔽ₚ).** Reading the same data "modulo a prime `p`" reveals
  exactly those modular laws whose period is divisible by `p`.
- **polynomials in a parameter (ℚ[t]).** When the data depends on a knob — a
  rate, a gain, a coupling strength — the laws become *functions of that knob*,
  and the interesting question is **at which settings does the structure change?**

One engine covers all of these because the underlying step — find the
combinations a set of movements leaves unchanged — is the same linear algebra
over any "well-behaved" number system (formally, any *Euclidean domain*). The
[example](../../examples/substrate/README.md) runs the identical code over ℚ, ℤ,
several 𝔽ₚ, and ℚ[t].

## The same data, read three ways

Point the engine at the same five datasets over ℚ, over ℤ, and over a few primes,
and the three views lock together by a single identity — *the number of laws over
𝔽ₚ equals the number over ℚ plus the modular laws whose period `p` divides*:

| dataset | over ℚ | hidden modular laws | over 𝔽₂ |
|---|---|---|---|
| `parity_pairs` | **0** | two parities (period 2) | **2** |
| `crt_mod6` | **0** | one law mod 6 | **1** (and one more over 𝔽₃) |
| `michaelis_menten` | **2** | none | **2** |

`parity_pairs` is the headline: **nothing is conserved in ordinary arithmetic**,
yet over 𝔽₂ the engine finds two laws — the two parities the data quietly obeys.
Same data, same engine; a different number system brings the hidden law into view.

## The headline: laws that depend on a parameter

Here is the question the earlier chapters couldn't ask. Picture an engineer with a
model of **two coupled flows** — think two tanks, two accounts, two reacting
pools — wired together by a single tunable **coupling `t`** (a valve setting, a
gain, a rate ratio):

> the two events are *"move 1 out of A and `t` into B"* and *"move `t` out of A
> and 1 into B".*

The practical question is: **at which settings of `t` does the system gain an
extra conserved quantity** — a special, often fragile, balance that doesn't hold
for a generic setting?

**The usual way.** Pick a grid of `t` values, solve each one numerically, and
eyeball where something special seems to happen — slow, and it silently misses any
special value that falls between your sample points.

**What the engine does instead.** It keeps `t` as a *symbol*. The conservation
laws come out as **polynomials in `t`**, and the settings where an extra law
appears are exactly the **roots** of those polynomials — found exactly, with no
sampling:

```text
Two coupled flows with tunable coupling t:
   e1: a += 1, b += -t      e2: a += t, b += -1
  generic conservation laws (all t): 0
  rank drops on the locus t^2 + -1 = 0
  => extra conservation appears at: t=-1, t=1

  confirm by substitution (conservation dim over Q at fixed t):
    t = 0:  0 law(s)
    t = 2:  0 law(s)
    t = 1:  1 law(s)  <- degenerate (extra law)
    t = -1:  1 law(s)  <- degenerate (extra law)
```

For a generic coupling the flows conserve nothing. But at exactly **`t = ±1`** —
the roots of the invariant factor `t² − 1` — a conservation law springs into
existence. The engine reports those two values precisely, having never plugged in
a single number; the substitution check at the bottom merely confirms what the
symbolic computation already proved.

## Why this is useful, and what it demonstrates

- **It finds the special settings exactly, not approximately.** Degeneracy loci —
  the parameter values where a system gains or loses a conserved quantity — are
  exactly the roots of the invariant polynomials. No grid, no sampling, nothing to
  fall between the cracks.
- **It is literally the same engine.** Nothing was specialised for biology, for
  finance, or for control theory. We swapped the coefficient ring from ℚ to ℚ[t]
  and the discovery ran unchanged — which is also why the same code reads modular
  laws over ℤ and over 𝔽ₚ.
- **It closes the loop with the modular story.** Parity over 𝔽₂, "lots of 12" over
  ℤ, and "degenerate at `t = ±1`" over ℚ[t] are the same phenomenon — structure
  that is invisible in the default number system and exact in the right one.

## The maths

*(This is the formal core of substrate generality — moved here from the appendix
so it sits beside its worked example. The rest of the machinery follows in the
[Appendix](A_appendix_mathematics.md).)*

The same null-space and Smith-Normal-Form code runs over any **Euclidean domain**
(`euclidean.py`, `generic_linalg.py`):

| domain | what conservation means there |
|---|---|
| `ℚ` | the additive baseline |
| `𝔽ₚ` | conservation modulo a prime `p` |
| `ℤ` | exact integer laws **plus** modular (torsion) laws |
| `ℚ[t]` | **parametric** conservation — laws as functions of a parameter |

The three views interlock by one identity (`substrate.substrate_spectrum`):

$$ \dim_{\mathbb F_p}(\text{laws}) \;=\; \dim_{\mathbb Q}(\text{laws})
\;+\; \#\{\, d_i : p \mid d_i \,\}, $$

where the `dᵢ` are the invariant factors (the torsion of `coker S`, Appendix A.3).

**Parametric conservation.** Let `S` depend on a parameter `t` (a rate, a coupling,
a clock). Smith Normal Form over `ℚ[t]` yields invariant **polynomials**; their
roots are exactly the parameter values where conservation degenerates
(`substrate.parametric_conservation`). For the two coupled flows above, value is
conserved only at `t = ±1` — the roots of the invariant factor `t² − 1` — computed
exactly, with no sampling.

---

[🏠 Home](../index.md) · [← Previous: Raw XML showcase](07_xml_showcase.md) · [Next: Appendix →](A_appendix_mathematics.md)
