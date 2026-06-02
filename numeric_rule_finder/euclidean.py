"""
euclidean.py — the coefficient substrate: Euclidean domains
===========================================================

Everything in this project is linear algebra over a ring. The natural level of
generality for *exact* null spaces and Smith Normal Form is a **Euclidean
domain**: a ring with an exact `divmod` whose remainder strictly shrinks. This
module provides four instances, all exact:

    ZZ        integers              -> integer + modular (torsion) conservation
    QQ        rationals (a field)   -> the baseline additive laws
    GF(p)     finite field F_p      -> mod-p conservation laws
    QQ[t]     polynomials over Q    -> PARAMETRIC conservation (laws vs. t)

A domain is a small object exposing: zero/one, is_zero/eq, add/sub/mul/neg,
divmod (Euclidean), norm (for pivot choice), canonical_unit (to normalise a
pivot: sign for ZZ, monic for polynomials, inverse for a field), and—for
fields—inv. The generic engine in `generic_linalg.py` is written against this
interface, so the same null-space / SNF code runs over every substrate.
"""

from __future__ import annotations
from fractions import Fraction


class ZZ:
    name = "Z"
    is_field = False
    zero = 0
    one = 1

    @staticmethod
    def is_zero(a): return a == 0
    @staticmethod
    def eq(a, b): return a == b
    @staticmethod
    def add(a, b): return a + b
    @staticmethod
    def sub(a, b): return a - b
    @staticmethod
    def mul(a, b): return a * b
    @staticmethod
    def neg(a): return -a
    @staticmethod
    def divmod(a, b):
        q = a // b
        return q, a - q * b
    @staticmethod
    def norm(a): return abs(a)
    @staticmethod
    def canonical_unit(a): return -1 if a < 0 else 1   # multiply pivot to make it positive
    @staticmethod
    def from_int(n): return int(n)
    @staticmethod
    def to_str(a): return str(a)


class QQ:
    name = "Q"
    is_field = True
    zero = Fraction(0)
    one = Fraction(1)

    @staticmethod
    def is_zero(a): return a == 0
    @staticmethod
    def eq(a, b): return a == b
    @staticmethod
    def add(a, b): return a + b
    @staticmethod
    def sub(a, b): return a - b
    @staticmethod
    def mul(a, b): return a * b
    @staticmethod
    def neg(a): return -a
    @staticmethod
    def divmod(a, b): return a / b, Fraction(0)
    @staticmethod
    def inv(a): return Fraction(1) / a
    @staticmethod
    def norm(a): return 0 if a == 0 else 1
    @staticmethod
    def canonical_unit(a): return Fraction(1) / a     # normalise pivot to 1
    @staticmethod
    def from_int(n): return Fraction(n)
    @staticmethod
    def to_str(a): return str(a)


def GF(p):
    """The finite field F_p (p prime)."""
    class _GF:
        name = f"F{p}"
        is_field = True
        mod = p
        zero = 0
        one = 1 % p

        @staticmethod
        def is_zero(a): return a % p == 0
        @staticmethod
        def eq(a, b): return (a - b) % p == 0
        @staticmethod
        def add(a, b): return (a + b) % p
        @staticmethod
        def sub(a, b): return (a - b) % p
        @staticmethod
        def mul(a, b): return (a * b) % p
        @staticmethod
        def neg(a): return (-a) % p
        @staticmethod
        def inv(a): return pow(a % p, p - 2, p)
        @staticmethod
        def divmod(a, b): return (a * pow(b % p, p - 2, p)) % p, 0
        @staticmethod
        def norm(a): return 0 if a % p == 0 else 1
        @staticmethod
        def canonical_unit(a): return pow(a % p, p - 2, p)
        @staticmethod
        def from_int(n): return n % p
        @staticmethod
        def to_str(a): return str(a % p)
    return _GF


class QQPoly:
    """Univariate polynomials over Q, as tuples of Fraction coeffs (low->high),
    trimmed of trailing zeros. A Euclidean domain (not a field)."""
    name = "Q[t]"
    is_field = False
    zero = ()
    one = (Fraction(1),)

    @staticmethod
    def _trim(c):
        c = list(c)
        while c and c[-1] == 0:
            c.pop()
        return tuple(c)
    @staticmethod
    def is_zero(a): return len(a) == 0
    @staticmethod
    def eq(a, b): return tuple(a) == tuple(b)
    @staticmethod
    def add(a, b):
        n = max(len(a), len(b))
        return QQPoly._trim(tuple((a[i] if i < len(a) else 0) + (b[i] if i < len(b) else 0)
                                  for i in range(n)))
    @staticmethod
    def sub(a, b):
        n = max(len(a), len(b))
        return QQPoly._trim(tuple((a[i] if i < len(a) else 0) - (b[i] if i < len(b) else 0)
                                  for i in range(n)))
    @staticmethod
    def neg(a): return tuple(-x for x in a)
    @staticmethod
    def mul(a, b):
        if not a or not b:
            return ()
        out = [Fraction(0)] * (len(a) + len(b) - 1)
        for i, x in enumerate(a):
            if x:
                for j, y in enumerate(b):
                    out[i + j] += x * y
        return QQPoly._trim(out)
    @staticmethod
    def divmod(a, b):
        if not b:
            raise ZeroDivisionError("polynomial division by zero")
        r = list(a)
        q = [Fraction(0)] * max(0, len(a) - len(b) + 1)
        db = len(b) - 1
        lead = b[-1]
        while len(r) - 1 >= db and any(x != 0 for x in r):
            dr = len(r) - 1
            coeff = r[dr] / lead
            shift = dr - db
            q[shift] = coeff
            for i in range(len(b)):
                r[shift + i] -= coeff * b[i]
            while r and r[-1] == 0:
                r.pop()
        return QQPoly._trim(q), QQPoly._trim(r)
    @staticmethod
    def norm(a): return len(a) - 1            # degree (>= 0 for nonzero)
    @staticmethod
    def canonical_unit(a): return (Fraction(1) / a[-1],)   # make monic
    @staticmethod
    def from_int(n):
        return () if n == 0 else (Fraction(n),)
    @staticmethod
    def to_str(a):
        if not a:
            return "0"
        terms = []
        for i, c in enumerate(a):
            if c == 0:
                continue
            mon = "" if i == 0 else ("t" if i == 1 else f"t^{i}")
            terms.append(f"{c}{('*' + mon) if mon else ''}" if (c != 1 or not mon) else mon)
        return " + ".join(reversed(terms)) if terms else "0"
