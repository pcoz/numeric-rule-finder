"""
From raw SBML (XML) to the conserved laws of a reaction network
===============================================================

Hand this nothing but a reaction list in **SBML** -- the XML format systems
biologists exchange models in -- and it returns, exactly, the **conserved
moieties** of the network: the combinations of species whose total amount never
changes, no matter how the reactions fire.

Those moieties are not in the file. Nobody wrote "kinase total is conserved."
They are a *property of the stoichiometry* that a modeller normally derives by
hand (the left null space of the stoichiometric matrix) before reducing a model.
This reads the XML and hands them straight back.

Run:  python examples/xml_moieties/discover_moieties.py
"""

import sys
import xml.etree.ElementTree as ET
from pathlib import Path

HERE = Path(__file__).resolve().parent
for _root in HERE.parents:
    if (_root / "numeric_rule_finder").is_dir():
        sys.path.insert(0, str(_root)); break

from numeric_rule_finder.invariants import discover_invariants

SBML = HERE / "covalent_cycle.sbml"


def _tag(elem):
    """Local tag name, ignoring the SBML namespace."""
    return elem.tag.rsplit("}", 1)[-1]


def read_sbml(path):
    """Parse an SBML model into (species_names, movement_records).

    Each reaction becomes an 'event'; each species a 'bucket'; the signed
    stoichiometry (reactants negative, products positive) is the amount.
    """
    root = ET.parse(path).getroot()
    names, records = {}, []
    for el in root.iter():
        t = _tag(el)
        if t == "species":
            names[el.get("id")] = el.get("name", el.get("id"))
        elif t == "reaction":
            rid = el.get("id")
            for side in el:
                st = _tag(side)
                sign = -1 if st == "listOfReactants" else (+1 if st == "listOfProducts" else 0)
                if not sign:
                    continue
                for ref in side:
                    if _tag(ref) == "speciesReference":
                        coeff = sign * int(float(ref.get("stoichiometry", "1")))
                        records.append({"species": ref.get("species"),
                                        "reaction": rid, "stoich": coeff})
    return names, records


def main():
    names, records = read_sbml(SBML)
    disc = discover_invariants(records, "species", "reaction", "stoich")

    print(f"Parsed SBML: {len(names)} species, "
          f"{len({r['reaction'] for r in records})} reactions -- and nothing else.\n")
    print(f">>> It found {disc.n_laws} conserved quantities (moieties) in the network:\n")
    for law in disc.minimal_semipositive:
        ids = sorted(law.coeffs, key=str)
        pretty = " + ".join(names.get(i, i) for i in ids)
        print(f"    {' + '.join(ids):24s}  is conserved   ( {pretty} )")

    print("\nNo rate, no annotation, no hand-derivation: from the stoichiometry alone,")
    print("the kinase pool, the phosphatase pool, and the total substrate are each")
    print("invariant for all time. These are exactly the quantities a modeller uses")
    print("to reduce the system -- recovered straight from the XML.")


if __name__ == "__main__":
    main()
