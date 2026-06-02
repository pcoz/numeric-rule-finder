"""
snf.py — exact integer Smith Normal Form (the shared depth engine)
==================================================================

For an integer matrix A there exist unimodular U (det ±1) and V with

    U A V = D = diag(d_1, ..., d_r, 0, ..., 0),   d_1 | d_2 | ... | d_r  (> 0),

the **invariant factors** of A. This single decomposition powers two things
in this project:

  * the TORSION of `coker(A)` = ⊕_i Z/d_i  (d_i > 1) — the modular conservation
    laws that are invisible over Q (see integer_invariants.py), and
  * the torsion of simplicial/sheaf homology (see homology.py).

We track the left transform U (its rows are the functionals we need): if
`U A V = D`, then for any b in im(A) = A·Z^n,

    (U b)_i = d_i · (V^{-1} x)_i  ∈  d_i·Z,

so **row i of U is conserved modulo d_i** on im(A) (exactly conserved when
d_i = 0). Only U is needed to read off the laws, so we return U and D; V is
available too for decoding witnesses.

Pure integer arithmetic — no floats, no fractions.
"""

from __future__ import annotations


def identity(n):
    return [[1 if i == j else 0 for j in range(n)] for i in range(n)]


def matmul(A, B):
    m, k, n = len(A), len(B), len(B[0]) if B else 0
    out = [[0] * n for _ in range(m)]
    for i in range(m):
        Ai = A[i]
        for t in range(k):
            a = Ai[t]
            if a:
                Bt = B[t]
                outi = out[i]
                for j in range(n):
                    outi[j] += a * Bt[j]
    return out


def smith_normal_form(matrix):
    """Return (D, U, V) with U @ matrix @ V == D in Smith Normal Form,
    U and V unimodular. Inputs/outputs are integer list-of-lists."""
    A = [list(map(int, row)) for row in matrix]
    m = len(A)
    n = len(A[0]) if m else 0
    U = identity(m)
    V = identity(n)

    def swap_rows(i, j):
        if i != j:
            A[i], A[j] = A[j], A[i]
            U[i], U[j] = U[j], U[i]

    def swap_cols(i, j):
        if i != j:
            for r in range(m):
                A[r][i], A[r][j] = A[r][j], A[r][i]
            for r in range(n):
                V[r][i], V[r][j] = V[r][j], V[r][i]

    def add_row(i, t, q):                 # row_i += q * row_t   (on A and U)
        if q:
            A[i] = [a + q * b for a, b in zip(A[i], A[t])]
            U[i] = [a + q * b for a, b in zip(U[i], U[t])]

    def add_col(j, t, q):                 # col_j += q * col_t   (on A and V)
        if q:
            for r in range(m):
                A[r][j] += q * A[r][t]
            for r in range(n):
                V[r][j] += q * V[r][t]

    def neg_row(i):
        A[i] = [-x for x in A[i]]
        U[i] = [-x for x in U[i]]

    t = 0
    while t < min(m, n):
        # pivot = nonzero entry of smallest absolute value in A[t:, t:]
        best = None
        for i in range(t, m):
            for j in range(t, n):
                if A[i][j] != 0 and (best is None or abs(A[i][j]) < abs(A[best[0]][best[1]])):
                    best = (i, j)
        if best is None:
            break
        swap_rows(best[0], t)
        swap_cols(best[1], t)

        # Euclidean clear of row t and column t
        while True:
            for i in range(t + 1, m):
                if A[i][t] != 0:
                    add_row(i, t, -(A[i][t] // A[t][t]))
                    if A[i][t] != 0:        # nonzero remainder -> smaller pivot
                        swap_rows(i, t)
            for j in range(t + 1, n):
                if A[t][j] != 0:
                    add_col(j, t, -(A[t][j] // A[t][t]))
                    if A[t][j] != 0:
                        swap_cols(j, t)
            if all(A[i][t] == 0 for i in range(t + 1, m)) and \
               all(A[t][j] == 0 for j in range(t + 1, n)):
                break

        # divisibility: pivot must divide every remaining entry
        bad = None
        for i in range(t + 1, m):
            for j in range(t + 1, n):
                if A[i][j] % A[t][t] != 0:
                    bad = i
                    break
            if bad is not None:
                break
        if bad is not None:
            add_row(t, bad, 1)              # fold a non-divisible row in; redo pivot t
            continue

        if A[t][t] < 0:
            neg_row(t)
        t += 1

    return A, U, V


def invariant_factors(D):
    """The positive diagonal entries d_1 | d_2 | ... | d_r of an SNF matrix."""
    out = []
    for i in range(min(len(D), len(D[0]) if D else 0)):
        if D[i][i] != 0:
            out.append(D[i][i])
    return out
