# Worked example — *The Meridian Tontine*: a workflow of calls

This folder shows how to **chain** `numeric-rule-finder` calls into one
investigation where each step's *output* decides the next — and the pipeline
climbs from the plain-language facade into the deeper mathematics **only when
the simpler layer comes up short**. No single call reaches the verdict; the
chain does.

```
python investigate.py
```

## The story

A treasury analyst inherits the books of the *Meridian Tontine*, a savings club
whose payouts are alleged to be **one single closed money pool**. Her only job
is to confirm the books balance. Run `C3` is off by a trivial-looking **5** —
and every time she pushes deeper, the data refuses to confirm what the last
level assumed, *forcing* her up the next rung.

## The workflow (each rung is triggered by the previous one falling short)

| rung | call | what it finds | why it escalates |
|---|---|---|---|
| **1** | `Reconciler.balance_check` | `C3` is **off by 5**, but **no single line** explains it | a typo points at a line; this doesn't → look structural |
| **2** | `Reconciler.what_balances` | the accounts are **two independent books**; only Pool A has a balancing law over ℚ | the "one pool" premise is false; the broken book has **no rational law** → go to integers |
| **3** | `integer_conservation` | Pool B conserves nothing over ℚ but carries **torsion ℤ/5 ⊕ ℤ/5** — it's conserved **mod 5** | the break isn't noise; it lives inside a real law → type it precisely |
| **4** | `ConservationComplex.type_observation` | the observed net is a **genuine obstruction** (not a re-attribution): it violates `vault_chips + chip_reserve`, **off by 5** | the hole is real and named → check the external evidence |
| **5** | `discrepancy_cohomology` | the three auditors' pairwise memos form an **irreducible cycle (H¹ ≠ 0)** | no per-source bias reconciles them — the evidence is self-contradictory |
| 6 *(bonus)* | `parametric_conservation` | a tunable coupling conserves value only at special rates (`t = ±1`) | surfaces the parametric (`ℚ[t]`) capability |

## The payoff — and the number that ties it together

> *"C3 is off by 5"* is **not a typo and not a fold error**. It is a genuine
> conservation obstruction inside a **hidden second pool that moves only in
> fives**, and the audit memos meant to resolve it are **mutually impossible**.

The elegance is numeric: the **5** that `balance_check` reports as an opaque gap
is the **same 5** that `integer_conservation` shows is the preserved mod-5 step,
and the **same 5** that `type_observation` finally names as the violation of the
`vault_chips + chip_reserve` law. Rungs 1 → 3 → 4 are the same fact, seen at
three depths.

## Why this pattern matters

Every rung uses the library's signature move: an **honest stop that escalates
instead of inventing**. Plain balancing couldn't find a culprit, so it didn't
guess — it handed the question up. Discovery showed the structure. The integers
found the law the rationals couldn't. Cohomology typed the residual. Multi-source
cohomology judged the evidence. That is how you compose these calls "to great
effect": let each layer answer what it can, and pass what it can't to the next.

## Files

```
investigate.py     # the orchestrated, branching pipeline (run this)
data/ledger.csv    # the Meridian books (payout_run, account, amount)
```

The auditor memos and the clean reference model are small enough to live inline
in `investigate.py`.
