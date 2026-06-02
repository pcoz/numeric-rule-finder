[🏠 Home](../index.md) · [← Previous: The tool space](00_introduction.md) · [Next: Northwind close →](02_example_ba_close.md)

---

# 2 · How it works: one idea, five depths

## The one idea

Everything the library does is built on one intuitive observation. A great deal
of operational data is a record of **movements**: money between accounts, stock
between locations, energy across a meter, rows through a pipeline, points between
members. Each record has three things:

- a **group** it belongs to (a transaction, a transfer, an interval, a run);
- a **bucket** it touches (an account, a location, a meter, a stage);
- a **signed amount** (in is positive, out is negative).

A **conservation law** is simply a weighted combination of buckets whose total is
left *unchanged* by every movement. Double-entry bookkeeping is the famous case —
each transaction's amounts net to zero — but the same shape appears wherever
something is conserved: units in equal units out plus what's on hand, energy
generated equals energy consumed plus losses, rows in equal rows loaded plus rows
rejected.

The library's core move is to **compute these laws directly from the data** and
then measure, exactly, the **residual** — the amount by which any group fails to
obey them. The residual is both the proof that something is wrong and, through
its shape, the clue to *why*.

## The five depths

What makes the tool more than a clever `GROUP BY` is that it does not stop at the
first layer. It climbs a ladder, and — this is the important part — it **only
climbs when the simpler layer comes up short**. Each rung answers a sharper
question than the last.

| depth | the question it answers | what it returns |
|---|---|---|
| **1 · Balance** | Does each group balance, and if not, where? | the breaks, each with a likely cause |
| **2 · Structure** | What stays balanced — and is this really one system? | the conserved groups; hidden *separate* books |
| **3 · Modular** | Nothing balances normally — is there *still* a pattern? | invariants like "moves only in cases of 12" / parity |
| **4 · Typing** | Is this break a real hole, or just mis-booked? | *genuine loss* vs *re-attribution*, named precisely |
| **5 · Consistency** | Can these independent reports all be true? | a proof that a set of reconciliations cannot all hold |

A useful way to read the ladder:

- **Depth 1** is what an analyst does by hand today, made instant and exact.
- **Depth 2** catches the expensive structural mistakes — for instance,
  reconciling two feeds as one when they were never connected.
- **Depth 3** is the tool being *intelligent*: when ordinary balancing finds
  nothing, it looks deeper (in modular arithmetic) rather than giving up, and
  reports what it finds in plain words.
- **Depth 4** replaces a gut call — *reclassify, or chase missing value?* — with
  an exact verdict that even names the relationship that broke.
- **Depth 5** judges *evidence*: three teams can each be internally tidy yet
  jointly impossible, and the tool proves it.

## The guiding principle: escalate, don't invent

Running through every depth is one discipline: an **honest stop that escalates
instead of inventing**. If a layer cannot find structure, it does not guess — it
hands the question up to the next layer, and only the next layer. If *no* layer
finds anything, the tool says so plainly. You are never handed a confident answer
that the data did not actually support.

## Two front doors

The same engine is reached two ways, and you choose by audience:

- **Plain-language facade** — for analysts. You hand it a CSV and a couple of
  column names; every answer comes back as a sentence and, often, an action. The
  mathematics never has to surface.
- **The mathematics** — for power users. Underneath sit conservation-law
  discovery, integer/modular (Smith-Normal-Form) analysis, cohomological residual
  typing, and multi-source consistency. It is exact, and it is there when you want
  a proof rather than a sentence. The full treatment is in the
  [Appendix](A_appendix_mathematics.md).

The chapters that follow show both doors in action. We begin at the plain end,
with an analyst closing the month.

---

[🏠 Home](../index.md) · [← Previous: The tool space](00_introduction.md) · [Next: Northwind close →](02_example_ba_close.md)
