# Finding the Laws Your Data Already Obeys

### A short book on *numeric-rule-finder* — what it is, where it fits, and what it does

Most tools that touch a table of numbers either **summarise** them, **optimise**
them, or **learn patterns** from them. This library does something narrower and,
in its niche, more powerful: it finds the **conservation laws** your data is
*supposed* to obey — the quantities that should stay balanced — **discovers**
them when nobody wrote them down, and then tells you, exactly, where and how they
break. When there is no such structure to lean on, it says so and stops, rather
than inventing an answer.

This book explains the tool space it occupies, walks through how it works, and
then takes you through its runnable worked examples — a month-end close, a
rules-free fraud catch, a five-rung investigation, two machine-learning
head-to-heads, and a raw-XML showcase — each shown with its **actual output**.

---

## Contents

| # | Chapter |
|---|---|
| 1 | [The tool space: what this is, and what it isn't](chapters/00_introduction.md) |
| 2 | [How it works: one idea, five depths](chapters/01_how_it_works.md) |
| 3 | [Worked example — Closing the month at Northwind Retail *(for analysts)*](chapters/02_example_ba_close.md) |
| 4 | [Worked example — Rules-free integrity of a points economy *(a new approach)*](chapters/03_example_points_integrity.md) |
| 5 | [Worked example — The Meridian Tontine: five rungs to a verdict *(the machinery)*](chapters/04_example_meridian.md) |
| 6 | [Where it fits, and how to use it on your own data](chapters/05_where_it_fits.md) |
| 7 | [This method vs. machine learning](chapters/06_vs_ml.md) *(two head-to-heads, real results)* |
| 8 | [Showcase — raw XML in, hidden laws out](chapters/07_xml_showcase.md) |
| A | [Appendix — The mathematics](chapters/A_appendix_mathematics.md) *(the hard maths, in full)* |

---

## The examples are runnable

Each worked example lives in its own subfolder of the repository's
[`examples/`](../examples/) directory — self-contained (script + data + a
README), and runnable as-is from the repository root:

| chapter | example | run it |
|---|---|---|
| 3 — Northwind month-end close | [`examples/northwind_close/`](../examples/northwind_close/README.md) | `python examples/northwind_close/close_the_books.py` |
| 4 — Points-economy integrity | [`examples/points_integrity/`](../examples/points_integrity/README.md) | `python examples/points_integrity/detect.py` |
| 5 — The Meridian Tontine | [`examples/meridian/`](../examples/meridian/README.md) | `python examples/meridian/investigate.py` |
| 7 — conservation beats a forest | [`examples/fraud_vs_ml/`](../examples/fraud_vs_ml/README.md) | `python examples/fraud_vs_ml/compare.py` |
| 7 — conservation feeds a forest | [`examples/ml_assist/`](../examples/ml_assist/README.md) | `python examples/ml_assist/pipeline.py` |
| 8 — raw-XML showcase | [`examples/xml_moieties/`](../examples/xml_moieties/README.md) | `python examples/xml_moieties/discover_moieties.py` |

> Every output quoted in the chapters is the **actual** output of these scripts.
> The repository's [`examples/`](../examples/) folder holds several more runnable
> demos (cross-domain, integer/modular, cohomology, substrate), each in its own
> subfolder with a README.

---

[Begin reading → *The tool space*](chapters/00_introduction.md)
