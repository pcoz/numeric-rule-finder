import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
for _root in HERE.parents:
    if (_root / "numeric_rule_finder").is_dir():
        sys.path.insert(0, str(_root)); break

import discover_moieties
from numeric_rule_finder.invariants import discover_invariants


def test_three_moieties_from_sbml():
    names, records = discover_moieties.read_sbml(discover_moieties.SBML)
    assert len(names) == 6
    disc = discover_invariants(records, "species", "reaction", "stoich")
    assert disc.n_laws == 3
    supports = {frozenset(law.coeffs) for law in disc.minimal_semipositive}
    assert frozenset({"K", "KS"}) in supports                       # kinase pool
    assert frozenset({"P", "PSp"}) in supports                      # phosphatase pool
    assert frozenset({"S", "Sp", "KS", "PSp"}) in supports          # total substrate
