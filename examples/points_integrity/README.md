# Example — rules-free integrity monitoring of a points / rewards economy

**The new approach this unlocks:** stop writing fraud rules. *Learn* the
economy's conservation law from normal activity, and let every violation fall
out of it — including exploits nobody anticipated.

```
python detect.py
```

## The problem, and how it's fought today

Loyalty programs, game economies, and marketplace-credit systems bleed money to
**points duplication** (a bug or exploit that creates currency from nothing) and
to **partner mis-reporting**. The standard defence is a growing pile of
hand-written anomaly rules — "alert if a member gains more than X per hour,"
"flag accounts that redeem within N minutes of earning." These are brittle,
need constant tuning, and are blind to any exploit the rule-writer didn't
foresee.

## The reframe

A points economy obeys exactly one thing: **conservation.** Every legitimate
event merely *moves* points between buckets — a mint authority, members, a
burn/redemption sink. Points never appear or vanish; they only flow. That single
invariant is far stronger than any rule list, and **nobody has to write it
down** — the library discovers it from the log.

Once the law is known, the categories of problem are *deductions*, not rules:

| step | call | what it does | the new capability |
|---|---|---|---|
| 1 | `what_balances` | **learns** that the log is closed conserved economies (and that NA & EU never mix) | the invariant is discovered, not declared |
| 2 | `balance_check` | screens new events; flags the one that breaks conservation | no rule said "can't gain 200" — the *law* did |
| 3 | `ConservationComplex.type_observation` | **types** the violation: 200 points *minted from nothing* (a genuine obstruction) vs a legitimate transfer (a coboundary) | distinguishes an exploit from harmless activity, exactly |
| 4 | `integer_conservation` | **learns** awards are issued only in multiples of 50, and flags an off-tier grant | the "valid grant sizes" rule is learned from data |
| 5 | `cross_check` | proves three partners' pairwise statements are **mutually impossible** | catches a lying/erroring partner with no global ledger |

## Why this is genuinely new

- **Zero rules.** Steps 1–4 wrote no fraud heuristic. A brand-new exploit that
  creates or destroys points is caught the instant it runs, because it breaks
  the *law*, not a pattern someone guessed.
- **Exploit vs. noise, decided exactly.** The coboundary/obstruction test
  separates "200 points materialised" (escalate) from "members traded points"
  (ignore) — the false-positive killer that rule systems lack.
- **No global source of truth needed.** The `H¹` partner check finds that three
  independently-true-looking statements cannot all hold, pointing at a
  mis-reporting partner without anyone maintaining a master ledger.

## Files

```
detect.py              # the rules-free monitoring workflow (run this)
data/clean_log.csv     # normal activity the law is learned from
data/monitor_batch.csv # a new batch containing a duplication exploit
data/tier_bonuses.csv  # award grants, used to learn the tier granularity
```

The same pattern applies to in-game gold/items, marketplace wallet credits,
carbon-credit registries, and token systems — anywhere a quantity is supposed to
be conserved except at defined faucets and sinks.
