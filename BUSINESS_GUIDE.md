# Reconciliation, in plain English

**No maths required.** You have a spreadsheet of line items that are *supposed*
to add up. This tool tells you whether they do, where they don't and probably
why, whether your data is quietly split into separate books, and whether stock
actually went missing — and it tells you honestly when there's nothing to
check, instead of making something up.

The fastest way to see what it does is to watch a real month-end.

---

## Headline walkthrough — closing the month at *Northwind Retail*

Maya is a finance-ops business analyst. It's month-end. She has the general
ledger, a stockroom export, a warehouse physical count, and three regional
controllers' sign-offs. She runs **six checks; each ends with an action she can
take today.** She never sees a matrix.

Run it yourself:

```
python examples/northwind_close/close_the_books.py
```

### Check 1 — Do the journal entries balance?

```
1 of 7 journal(s) do NOT balance:
  - journal 'J7' is off by 250.
      likely: a missing counter-entry for this line
      look at: {journal: J7, account: cash, amount: 250}
```
**Action:** chase J7 before anything else.
*Why it matters:* it points you at the one line most likely responsible, instead
of you scrolling the whole sheet.

### Check 2 — Am I even looking at one set of books?

```
your accounts split into 2 INDEPENDENT sets that never share a journal:
  set 1: cash, refunds, sales
  set 2: ic_due_from, ic_due_to
```
**Action:** reconcile the operating book and the intercompany book **separately**
— an entry in one can never offset the other.
*Why it matters:* catches the classic, expensive mistake of reconciling two
feeds as if they were one.

### Check 3 — Real money missing, or just booked oddly?

```
- 'J7' (off by 250): a GENUINE shortfall in the cash/refunds/sales balance
    ACTION: value is missing or duplicated -- raise a correcting journal
```
*Why it matters:* it makes the journal-vs-rebook decision for you, and names the
book that's short. (If it were just a mis-posting that nets out elsewhere, it
would say *"reclassify; no value is actually missing"* instead.)

### Check 4 — The stockroom won't tie to the unit. Is the data junk?

```
Nothing stays EXACTLY balanced here -- but ... I looked deeper and found
hidden structure:
  - the bin 'dispatch_dock' only ever changes in steps of 12 ...
  - the bin 'returns_bay'  only ever changes in steps of 12 ...
```
**Action:** don't chase single units — reconcile at the **case (12)** level; any
count that isn't a whole number of cases is the error.
*Why it matters:* this is the tool being **intelligent** — ordinary balancing
found nothing, so instead of giving up it looked deeper and found the real
pattern, in plain words.

### Check 5 — Physical count vs books: did stock move, or go missing?

```
net change by location: {DC: -200, StoreA: 150, StoreB: 30}
20 unit(s) are UNACCOUNTED FOR -- not explained by any relocation. Likely
shrinkage or loss; investigate.
```
**Action:** open a loss investigation and write down 20 units — stop hunting for
a transfer that doesn't exist. *(Had the numbers netted out, it would say "all
explained by transfers — nothing is missing.")*

### Check 6 — Three regions signed off. Can they all be right?

```
North vs South: differ by 120 ; South vs East: differ by -50 ; East vs North: -40
These reconciliations CANNOT all be correct: going around the loop the
differences add up to 30 instead of zero ... at least one source must be
re-measured.
```
**Action:** stop reconciling them pairwise — send one region back to re-measure;
no set of adjustments can make all three agree.

> **Maya's whole close, in one pass:** one real shortfall to journal, two books
> to split, a stockroom to reconcile by the case, 20 units of genuine shrink to
> write down, and three regional sign-offs that are mutually impossible — every
> answer a decision, no maths on screen.

The full annotated script is [`examples/northwind_close/`](examples/northwind_close/).

---

## Run it on your own data

You need a table (CSV or spreadsheet export) with, at minimum:

| you need | example column | what it is |
|---|---|---|
| a **group** | `journal`, `txn_id`, `order_no`, `batch` | what each line belongs to and should balance within |
| an **amount** | `amount` | a signed number (in is +, out is −) |
| *(optional)* an **account** | `account`, `category`, `location`, `stage` | which bucket the line hits |

From the command line:

```
python -m numeric_rule_finder.cli check    ledger.csv --group journal --amount amount
python -m numeric_rule_finder.cli books     ledger.csv --group journal --amount amount --account account
python -m numeric_rule_finder.cli report    ledger.csv --group journal --amount amount --account account
python -m numeric_rule_finder.cli compare   system_a.csv system_b.csv --group txn_id --amount amount
```

Or from a notebook:

```python
from numeric_rule_finder import Reconciler, cross_check, account_for_movement

r = Reconciler.from_csv("ledger.csv")          # or Reconciler.from_dataframe(df)
print(r.balance_check(group="journal", amount="amount").summary())
print(r.what_balances(account="account", group="journal", amount="amount").summary())
print(r.diagnose_breaks(group="journal", amount="amount", account="account").summary())
print(account_for_movement({"DC": -200, "StoreA": 150, "StoreB": 30}))
print(cross_check({("North", "South"): 120, ("South", "East"): -50, ("East", "North"): -40}))
```

---

## This is not just for accounting

Anything where a signed quantity should net out within a group is fair game.
Same tool, same checks — only your column names change:

| domain | group | amount | what a break means |
|---|---|---|---|
| **Accounting** | transaction | debit/credit | unbalanced entry, duplicate, missing leg |
| **Energy / utilities** | time interval | kWh (gen +, use/loss −) | unaccounted loss or a mis-read meter |
| **Supply chain / inventory** | transfer | units in/out | shrinkage, miscount, or two separate stock pools |
| **Data engineering (ETL)** | pipeline run | rows in/out/rejected | silently dropped rows |
| **Clinical trials** | site | patients (enrolled +, exited −) | patients unaccounted for |
| **Elections** | precinct | ballots issued/cast/spoiled | ballots that don't reconcile |
| **Manufacturing** | batch | mass in/out/scrap | yield loss / mass-balance error |
| **Networking** | flow | packets sent/recv/dropped | packet loss |
| **HR / headcount** | period | start + hires − exits | headcount that doesn't tie out |

See `python examples/gamut/gamut_demo.py` for many of these running through the one tool.

---

## Two promises

- **Exact.** Amounts are handled as exact numbers, so there are no rounding
  surprises (`100.00` really is `100.00`).
- **Honest.** If your data has no quantity that should stay balanced, it says so
  and stops — it will never invent a reconciliation that isn't there.

That's the whole tool. The mathematics under the hood (conservation laws,
finite-field and parametric analysis, cohomology) is real and powerful — and it
**doesn't have to surface**. For the answers above, it never does.
