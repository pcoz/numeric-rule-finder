[🏠 Home](../index.md) · [← Previous: Points-economy integrity](03_example_points_integrity.md) · [Next: Where it fits →](05_where_it_fits.md)

---

# 5 · Worked example — The Meridian Tontine: five rungs to a verdict

> **Example folder:** [`examples/meridian/`](../../examples/meridian/README.md)
> **Run it:** `python examples/meridian/investigate.py`
> **The mathematics behind each rung:** [Appendix — The mathematics](A_appendix_mathematics.md)

The two earlier examples kept the mathematics off-screen. This one turns it face
up: a single investigation that climbs all five depths of the ladder, where each
rung is forced by the previous one *withholding confirmation*. It is the
architect's view — proof that the plain answers elsewhere rest on something solid.

## The setting

A treasury analyst inherits the books of the *Meridian Tontine*, a savings club
whose payouts are alleged to be one closed money pool. Her only job is to confirm
the books balance. They don't — run `C3` is off by a trivial-looking **5** — and
every time she pushes deeper, the data refuses to confirm what the previous level
assumed.

## The climb

### Rung 1 — Plain balance

```text
1 of 6 payout_run(s) do NOT balance:
  - payout_run 'C3' is off by 5.
      likely: no single line explains it -- worth a manual look
```

A break with **no line-level culprit**. A typo would point at a line; this
doesn't. → escalate.

### Rung 2 — Structure: is it even one pool?

```text
your buckets split into 2 INDEPENDENT sets ...
  set 1: member_escrow, payout_bank
  set 2: chip_reserve, vault_chips
(conserved over Q = [['member_escrow', 'payout_bank']]; independent sets = 2)
```

The "single pool" premise is **false** — two non-communicating books, and the
broken one (the chips book) has **no rational conservation law**. → drill it over
the integers.

### Rung 3 — Integer / modular law

```text
conservation over Q: 0    hidden torsion: [5, 5]
    modular law:  (chip_reserve + vault_chips)  mod 5  =  const
```

The chips book conserves nothing in ordinary arithmetic, yet it is governed by a
law **modulo 5**. So `C3`'s break isn't random noise; it lives *inside* a real
law. → type the residual precisely.

### Rung 4 — Cohomological typing: re-attribution, or a genuine hole?

```text
a candidate re-attribution {vault_chips:+15, chip_reserve:-15}:
    RESOLVABLE (coboundary): explainable by re-attributing existing movements.
the real observed net:
    OBSTRUCTION: no event reconfiguration explains it. Violated conserved
    quantities -- chip_reserve + vault_chips off by 5.
```

A **genuine obstruction**: no re-attribution reproduces it, and it names the exact
law it violates — off by **5**. → check the external evidence.

### Rung 5 — Multi-source consistency

```text
IRREDUCIBLE (in H^1): the discrepancies do not close around the loop -- net 30.
No per-ledger correction reconciles them; this is the matching boundary.
```

The three auditors' statements **cannot all be true** — their loop nets to a
nonzero amount, so the external evidence is self-contradictory.

## The verdict, and the number that ties it together

> *"C3 is off by 5"* is **not a typo and not a fold error.** It is a genuine
> conservation obstruction inside a hidden second pool that moves only in fives —
> and the audit memos meant to resolve it are mutually impossible.

The elegance is numeric, and it is the point of the whole climb:

- the **5** that Rung 1 reports as an opaque gap,
- is the **same 5** that Rung 3 shows is the preserved step modulo 5,
- and the **same 5** that Rung 4 names as the violation of the
  `vault_chips + chip_reserve` law.

Rungs 1 → 3 → 4 are one fact, seen at three depths. No single call delivers that
verdict; the *chain* does, because each rung escalates only when the one below it
comes up short.

For the definitions and theorems underneath — null spaces, Smith Normal Form,
the cokernel and `H¹`, and the parametric extension — see the
[Appendix](A_appendix_mathematics.md).

---

[🏠 Home](../index.md) · [← Previous: Points-economy integrity](03_example_points_integrity.md) · [Next: Where it fits →](05_where_it_fits.md)
