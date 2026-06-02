[🏠 Home](../index.md) · [← Previous: How it works](01_how_it_works.md) · [Next: Points-economy integrity →](03_example_points_integrity.md)

---

# 3 · Worked example — Closing the month at Northwind Retail

> **Example folder:** [`examples/northwind_close/`](../../examples/northwind_close/README.md)
> **Run it:** `python examples/northwind_close/close_the_books.py`

This first example is deliberately at the straightforward end of the spectrum. There is no
mathematics on screen anywhere — only findings and actions — yet behind each line
sits the full machinery from the previous chapter.

## The setting

Maya is a finance-ops analyst. It is month-end, and she has the usual pile:

- the **general ledger** (journal entries),
- a **stockroom export**,
- a **warehouse physical count**, and
- three regional controllers' **reconciliation sign-offs**.

Her job is to close the books. She runs **six checks**, and crucially, *each one
ends in an action she can take today.*

## The run, check by check

### Check 1 — Do the journal entries balance?

```text
1 of 7 journal(s) do NOT balance:
  - journal 'J7' is off by 250.
      likely: a missing counter-entry for this line
      look at: {journal: J7, account: cash, amount: 250}
```

**Action:** chase J7 first. Notice the tool points at the single most likely line
rather than leaving Maya to scroll the sheet.

### Check 2 — Am I even looking at one set of books?

```text
your accounts split into 2 INDEPENDENT sets that never share a journal:
  set 1: cash, refunds, sales
  set 2: ic_due_from, ic_due_to
```

**Action:** reconcile the **operating** book and the **intercompany** book
*separately*. This is the expensive, easy-to-miss mistake — treating two feeds as
one — caught automatically.

### Check 3 — Real money missing, or just booked oddly?

```text
- 'J7' (off by 250): a GENUINE shortfall in the cash/refunds/sales balance
    ACTION: value is missing or duplicated -- raise a correcting journal
```

The tool makes the *reclassify-versus-investigate* call for her, and names the
book that is short. (Had it been a re-attribution that nets out elsewhere, it
would have said so instead.)

### Check 4 — The stockroom won't tie to the unit. Is the data junk?

```text
Nothing stays EXACTLY balanced here -- but ... I looked deeper and found
hidden structure:
  - the bin 'dispatch_dock' only ever changes in steps of 12 ...
  - the bin 'returns_bay'  only ever changes in steps of 12 ...
```

**Action:** stop chasing single units — reconcile at the **case (12)** level. This
is depth 3 in action: ordinary balancing found nothing, so the tool escalated to
modular arithmetic and surfaced the real pattern.

### Check 5 — Physical count vs books: did stock move, or vanish?

```text
net change by location: {DC: -200, StoreA: 150, StoreB: 30}
20 unit(s) are UNACCOUNTED FOR -- not explained by any relocation. Likely
shrinkage or loss; investigate.
```

**Action:** open a loss investigation and write down 20 units — and stop hunting
for a transfer that does not exist.

### Check 6 — Three regions signed off. Can they all be right?

```text
North vs South: differ by 120 ; South vs East: differ by -50 ; East vs North: -40
These reconciliations CANNOT all be correct: going around the loop the
differences add up to 30 instead of zero ... at least one source must be
re-measured.
```

**Action:** stop reconciling pairwise; send one region back to re-measure.

## The takeaway

> **Maya's whole close, in one pass:** one real shortfall to journal, two books
> to split, a stockroom to reconcile by the case, twenty units of genuine shrink
> to write down, and three regional sign-offs that are mutually impossible —
> every answer a *decision*, and not a line of mathematics in sight.

The next chapter keeps the plain language but turns the same engine to a problem
where it unlocks a genuinely new way of working.

---

[🏠 Home](../index.md) · [← Previous: How it works](01_how_it_works.md) · [Next: Points-economy integrity →](03_example_points_integrity.md)
