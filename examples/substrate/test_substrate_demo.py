import sys
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
for _root in HERE.parents:
    if (_root / "numeric_rule_finder").is_dir():
        sys.path.insert(0, str(_root)); break

import substrate_demo as sd
from numeric_rule_finder import datasets as D
from numeric_rule_finder.substrate import substrate_spectrum, parametric_conservation, poly


def test_parametric_degenerates_exactly_at_pm1():
    M = [[poly(1), poly(0, 1)],
         [poly(0, -1), poly(-1)]]
    res = parametric_conservation(["a", "b"], ["e1", "e2"], M)
    assert res.generic_laws == 0                                  # no law for generic t
    # extra conservation only at the roots of t^2 - 1
    assert sd._qq_conservation_dim(M, Fraction(1), 2) == 1
    assert sd._qq_conservation_dim(M, Fraction(-1), 2) == 1
    assert sd._qq_conservation_dim(M, Fraction(0), 2) == 0
    assert sd._qq_conservation_dim(M, Fraction(2), 2) == 0


def test_substrate_spectrum_identity_and_hidden_parity():
    d = D.parity_pairs()
    sp = substrate_spectrum(d["records"], [2, 3, 5], d["entity_key"],
                            d["event_key"], d["qty_key"])
    assert sp.identity_holds          # dim_Fp = dim_Q + #{torsion factors div by p}
    assert sp.q_dim == 0              # nothing conserved over Q
    assert sp.per_prime[2] == 2       # but F_2 sees the two parities
