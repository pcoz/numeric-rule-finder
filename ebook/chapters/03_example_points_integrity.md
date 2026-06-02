[🏠 Home](../index.md) · [← Previous: Northwind close](02_example_ba_close.md) · [Next: The Meridian Tontine →](04_example_meridian.md)

---

# 4 · Worked example — Rules-free integrity of a points economy

> **Example folder:** [`examples/points_integrity/`](../../examples/points_integrity/README.md)
> **Run it:** `python examples/points_integrity/detect.py`

This example shows the library *unlocking a new approach*, not merely doing an old
job faster.

## The problem, and how it's fought today

Loyalty programs, in-game economies, and marketplace-credit systems bleed money
to two failures:

- **points duplication** — a bug or exploit that creates currency from nothing,
- **partner mis-reporting** — statements between programs that don't add up.

The standard defence is a growing pile of hand-written anomaly rules: *"alert if a
member gains more than X per hour," "flag accounts that redeem within N minutes
of earning."* These rules are brittle, need constant tuning, and are blind to any
exploit nobody thought to write a rule for.

## The reframe

A points economy obeys one thing: **conservation.** Every legitimate event merely
*moves* points between buckets — a mint authority, members, a redemption sink.
Points never appear or vanish; they only flow. That single invariant is stronger
than any rule list, and **nobody has to write it down** — the library learns it
from the log. Once the law is known, the categories of problem become
*deductions*, not rules.

## The run, step by step

### Step 1 — Learn the law nobody wrote

```text
your buckets split into 2 INDEPENDENT sets that never share an event:
  set 1: member_amy, member_ben, na_burn, na_mint
  set 2: eu_mint, member_eva, member_uwe
```

No rule was authored. The tool has worked out that the log is two **closed**
economies (NA and EU never mix), each conserving its total points.

### Step 2 — Screen new events against the learned law

```text
1 of 4 event(s) do NOT balance:
  - event 'm3' is off by 200.
      look at: {event: m3, bucket: member_ben, points: 200}
```

Nothing said "member_ben may not gain 200." The *law* — points cannot appear from
nowhere — flagged it.

### Step 3 — Type it: a real exploit, or just a transfer?

```text
event 'm3' net = {member_ben: 200}
VERDICT: DUPLICATION EXPLOIT -- 200 points were created from nothing
         (no transfer reproduces this). Not a re-attribution.

control -- a genuine transfer {member_amy:-25, member_ben:+25}:
         harmless transfer, no points created
```

This is the false-positive killer: the tool distinguishes *200 points materialised
out of thin air* (escalate) from *two members traded points* (ignore), exactly.

### Step 4 — Learn the grant granularity, flag off-tier grants

```text
learned (no rule): awards are issued only in multiples of 50 (per-member moduli [50, 50, 100]).
    a proposed grant of 200: valid (on-tier)
    a proposed grant of 30: ANOMALOUS -- not a whole tier; reject/review
```

The "valid grant sizes" rule, too, is *learned* from the data rather than coded.

### Step 5 — Are the partners' statements even mutually possible?

```text
Airline vs Hotel: 120 ; Hotel vs Card: -50 ; Card vs Airline: -40
These reconciliations CANNOT all be correct: going around the loop, the
differences add up to 30 instead of zero ... at least one source must be re-measured.
```

A mis-reporting partner is caught with **no global ledger** — purely from the fact
that the three statements cannot simultaneously hold.

## Why this is genuinely new

- **Zero rules.** No fraud heuristic was written anywhere above. A brand-new
  exploit is caught the instant it runs, because it breaks the *law* rather than a
  pattern someone guessed.
- **Exploit vs. noise, decided exactly.** The "created vs. transferred" test is
  precisely the distinction rule-based systems struggle to draw.
- **No source of truth required.** Cross-partner consistency is judged structurally,
  with no master ledger to maintain.

> **The payoff:** the conservation law was *learned* from normal activity, and
> every problem then fell out of it — a duplication exploit typed as genuine
> minting, an off-tier grant caught by the learned granularity, and a set of
> partner statements proven impossible. New exploits need no new rules.

The same shape applies to in-game gold and items, marketplace wallet credits,
carbon-credit registries, and token systems. The next chapter pulls back the
curtain and shows the full machinery driving one investigation end to end.

---

[🏠 Home](../index.md) · [← Previous: Northwind close](02_example_ba_close.md) · [Next: The Meridian Tontine →](04_example_meridian.md)
