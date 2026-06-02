[🏠 Home](../index.md) · [← Previous: This method vs. ML](06_vs_ml.md) · [Next: One engine, many number systems →](08_substrate.md)

---

# 8 · Showcase — raw XML in, hidden laws out

> **Example:** [`examples/xml_moieties/`](../../examples/xml_moieties/README.md) ·
> **Run:** `python examples/xml_moieties/discover_moieties.py`

The earlier examples fed the library tidy spreadsheet rows. This one feeds it a
**real file format, untouched**, from a field the library knows nothing about —
and gets back something nobody put in the file. It is the clearest demonstration
that the idea travels: point it at *anything* that records how quantities move,
and it reads off the rules.

## The person, and what they want to know

Picture a researcher who studies how a cell switches a protein "on" and "off". She
has a **model** of the little machine that does it: two enzymes (one flips the
switch on, the other flips it off), the protein in its on- and off-states, and the
short-lived pairings that form while an enzyme is mid-flip. She wants to answer a
very practical question before she runs any simulations:

> **What in this system never changes?** Which totals are fixed no matter how busy
> the machine gets?

She needs that for ordinary reasons: to sanity-check the model, to simplify it (a
quantity that never changes is one fewer thing to track), and to make sure a
simulation that *reports* one of those totals drifting has a bug, not a discovery.

## The data she already has

She doesn't have a spreadsheet. She has an **SBML file** — the standard XML format
biologists use to share these models. It is just a list: *here are the parts, and
here are the reactions that convert them into one another.* Nothing in the file
says what is conserved; it only says what reacts with what.

```xml
<reaction id="R1_bind_kinase" reversible="true">
  <listOfReactants>
    <speciesReference species="K" stoichiometry="1"/>   <!-- an enzyme -->
    <speciesReference species="S" stoichiometry="1"/>   <!-- the switch, "off" -->
  </listOfReactants>
  <listOfProducts>
    <speciesReference species="KS" stoichiometry="1"/>  <!-- the two, paired up -->
  </listOfProducts>
</reaction>
...
```

## How it's normally done

To find the unchanging totals, an expert does a chunk of linear algebra **by
hand**: lay the reactions out as a matrix of who-consumes-and-produces-what, then
compute its *null space* — the combinations that every reaction cancels out. It's
a standard exercise, but it's fiddly, easy to get wrong, and has to be redone from
scratch every time the model changes. Most people reach for a specialist tool or a
page of algebra.

## What we can do instead

Point the library at the raw XML. A few lines of standard parsing turn each
reaction into signed movements (what it uses up, what it makes), and the same
engine from the rest of this book reads off the answer:

```text
Parsed SBML: 6 species, 4 reactions -- and nothing else.

>>> It found 3 conserved quantities (moieties) in the network:

    K + KS                    is conserved   ( kinase + kinase:substrate complex )
    P + PSp                   is conserved   ( phosphatase + phosphatase:phospho-substrate complex )
    KS + PSp + S + Sp         is conserved   ( ...complexes + substrate + phospho-substrate )
```

In plain terms, the three fixed totals are:

* **every "on"-enzyme is somewhere** — either free, or busy in a pairing;
* **every "off"-enzyme is somewhere** — likewise;
* **every copy of the switch is somewhere** — on, off, or momentarily held inside
  one of the two pairings. None are created or destroyed; they just move around.

Obvious once stated — which is the point. The library *recovered them from the raw
file*, with no rates, no labels, and no configuration.

## Why this is useful, and what it demonstrates

* **It read a foreign file format and found structure that wasn't written down.**
  The three conserved totals are nowhere in the XML; they are a consequence of the
  reactions, and the library deduced them exactly. That is the work the researcher
  would otherwise do by hand, returned in milliseconds and re-runnable the instant
  the model changes.
* **Nothing about it is biology-specific.** Swap "enzymes and a switch" for
  "loaders and pallets", "accounts and transactions", or "stages and rows", and it
  is the *same* computation — signed movements in, conserved totals out. The
  example just happens to start from a file a biologist already has.
* **Only the front door changed.** The discovery engine is identical to the one
  that closed the books in Chapter 3 and caught the exploit in Chapter 4; here a
  ten-line XML reader points it at a new world. Any format that records how things
  move — XML, CSV, a database export — is a few lines of parsing away from the same
  result.

> The takeaway: the conservation laws were always sitting inside the data. The
> library's job is simply to read them off — whatever shape the data arrives in.

This chapter changed the *front door* — the file format. The next one goes
deeper and changes the *number system* the laws live in, running the very same
engine over whole numbers, finite fields, and even a tunable parameter. The
mathematics behind "unchanging total = null space of the movements" is in the
[Appendix](A_appendix_mathematics.md).

---

[🏠 Home](../index.md) · [← Previous: This method vs. ML](06_vs_ml.md) · [Next: One engine, many number systems →](08_substrate.md)
