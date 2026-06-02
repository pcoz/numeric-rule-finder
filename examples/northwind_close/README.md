# Worked example (for analysts) — *Closing the books at Northwind Retail*

Same escalation logic as the maths-y `worked_example/`, but rebuilt for a
**garden-variety business analyst**: a real month-end story, **plain-English
output**, and **a concrete action after every check**. Maya never sees a matrix.

```
python close_the_books.py
```

## Maya's month-end, in six checks

| check | she asks | the tool says (plain) | her ACTION |
|---|---|---|---|
| 1 | Do the journals balance? | `J7` is off by 250; likely a missing counter-entry on the cash line | chase J7 |
| 2 | Is this even one set of books? | the accounts are **two independent books** (operating vs intercompany) that never share a journal | reconcile them **separately** |
| 3 | Real money missing, or just mis-booked? | J7 is a **genuine shortfall** in the cash/sales balance (not a re-attribution) | raise a correcting journal & investigate |
| 4 | The stockroom won't tie to the unit — is it junk? | not junk: **stock only moves in cases of 12** | reconcile at the **case** level; a non-multiple-of-12 is the error |
| 5 | Did stock move, or go missing? | **20 units unaccounted for** — not explained by any relocation | open a shrink investigation; write down 20 |
| 6 | Three regions signed off — can they all be right? | **No** — their differences don't close (net 30); no adjustment reconciles all three | send at least one region back to re-measure |

## Why a BA cares

Each check replaces a gut call a BA makes daily — and usually makes slowly or
wrong:

- **"Is this a typo or something structural?"** (1) — stop hunting for a cell
  that isn't there.
- **"Am I combining two things that were never one thing?"** (2) — the classic,
  expensive mistake of reconciling two feeds/entities as one.
- **"Do I reclassify, or is value actually gone?"** (3) — the journal-vs-rebook
  decision, made for you and localized to the right book.
- **"Stop balancing to the cent — it moves in lots."** (4) — fix the
  *granularity* of the reconciliation, not the data.
- **"Did it move or vanish?"** (5) — relocation vs shrink, the inventory
  question.
- **"Can my separate sign-offs all be true?"** (6) — catches mutually
  impossible reconciliations no eyeball will spot.

## It only speaks plain English — but the depth is there

Every line above is produced by the same engine as `worked_example/`
(conservation laws, integer/modular structure, cohomological residual typing,
multi-source consistency). The mathematics **doesn't have to surface** — and for
a BA it doesn't. A power user can still drop into `invariants`, `integer_invariants`,
`cohomology`, `substrate` for the proofs behind any sentence here.

## Files

```
close_the_books.py   # Maya's six checks (run this)
data/gl.csv          # general ledger (journal, account, amount)
data/stock.csv       # stockroom moves (move, bin, units)
```
The warehouse physical count and the regional sign-offs are small enough to live
inline in `close_the_books.py`.
