# Example — raw XML in, conserved laws out

> **Run:** `python examples/xml_moieties/discover_moieties.py`

Hand the library nothing but a reaction network in **SBML** (the XML format
systems biologists exchange models in — [`covalent_cycle.sbml`](covalent_cycle.sbml),
a textbook Goldbeter–Koshland modification cycle) and it returns the network's
**conserved moieties**: the combinations of species whose total never changes,
however the reactions fire.

## Result (actual output)

```text
Parsed SBML: 6 species, 4 reactions -- and nothing else.

>>> It found 3 conserved quantities (moieties) in the network:

    K + KS                    is conserved   ( kinase + kinase:substrate complex )
    P + PSp                   is conserved   ( phosphatase + phosphatase:phospho-substrate complex )
    KS + PSp + S + Sp         is conserved   ( ...substrate complexes + substrate + phospho-substrate )
```

## Why this is striking

Those three laws are **not in the file**. Nobody annotated "the kinase pool is
conserved." They are a property of the stoichiometry — formally the left null
space of the stoichiometric matrix — that a modeller normally derives by hand
before reducing a model. The library reads the raw XML, builds the incidence
exactly, and hands the moieties straight back. No rates, no annotations, no
configuration.

The XML parsing is ten lines of stdlib `xml.etree`; the discovery is the same
engine used everywhere else in this project.
