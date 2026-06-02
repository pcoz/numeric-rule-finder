"""
generic_linalg.py — null space and Smith Normal Form over any Euclidean domain
==============================================================================

The same algorithms as `invariants.py` (rref/null space) and `snf.py` (Smith
Normal Form), rewritten against the `euclidean.py` domain interface so they run
over Z, Q, F_p, and Q[t] alike.

  * `nullspace_field(matrix, ncols, F)` — for a FIELD F (Q, F_p): a basis of
    {x in F^ncols : matrix x = 0}.
  * `smith_normal_form(matrix, D)` — for any Euclidean domain D (Z, Q[t]):
    U @ matrix @ V == diag(d_1, ..., d_r) with d_1 | ... | d_r.

All exact; no floats.
"""

from __future__ import annotations


# ----------------------------- field null space -----------------------------

def _rref_field(matrix, F):
    M = [[x for x in row] for row in matrix]
    n_rows = len(M)
    n_cols = len(M[0]) if M else 0
    pivots = []
    r = 0
    for c in range(n_cols):
        piv = next((i for i in range(r, n_rows) if not F.is_zero(M[i][c])), None)
        if piv is None:
            continue
        M[r], M[piv] = M[piv], M[r]
        inv = F.inv(M[r][c])
        M[r] = [F.mul(inv, x) for x in M[r]]
        for i in range(n_rows):
            if i != r and not F.is_zero(M[i][c]):
                f = M[i][c]
                M[i] = [F.sub(a, F.mul(f, b)) for a, b in zip(M[i], M[r])]
        pivots.append(c)
        r += 1
        if r == n_rows:
            break
    return M, pivots


def nullspace_field(matrix, ncols, F):
    """Basis of {x in F^ncols : matrix x = 0} over a field F."""
    if not matrix or all(all(F.is_zero(x) for x in row) for row in matrix):
        return [[F.one if i == j else F.zero for j in range(ncols)] for i in range(ncols)]
    R, pivots = _rref_field(matrix, F)
    pivot_set = set(pivots)
    free = [c for c in range(ncols) if c not in pivot_set]
    basis = []
    for f in free:
        vec = [F.zero] * ncols
        vec[f] = F.one
        for row_i, pc in enumerate(pivots):
            vec[pc] = F.neg(R[row_i][f])
        basis.append(vec)
    return basis


# ----------------------------- generic SNF -----------------------------------

def smith_normal_form(matrix, D):
    """U @ matrix @ V == Smith Normal Form, over a Euclidean domain D.
    Returns (S, U, V) with entries in D."""
    A = [[x for x in row] for row in matrix]
    m = len(A)
    n = len(A[0]) if m else 0
    U = [[D.one if i == j else D.zero for j in range(m)] for i in range(m)]
    V = [[D.one if i == j else D.zero for j in range(n)] for i in range(n)]

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

    def add_row(i, t, q):                  # row_i += q * row_t
        if not D.is_zero(q):
            A[i] = [D.add(a, D.mul(q, b)) for a, b in zip(A[i], A[t])]
            U[i] = [D.add(a, D.mul(q, b)) for a, b in zip(U[i], U[t])]

    def add_col(j, t, q):                  # col_j += q * col_t
        if not D.is_zero(q):
            for r in range(m):
                A[r][j] = D.add(A[r][j], D.mul(q, A[r][t]))
            for r in range(n):
                V[r][j] = D.add(V[r][j], D.mul(q, V[r][t]))

    def scale_row(i, u):                   # row_i *= unit u
        A[i] = [D.mul(u, x) for x in A[i]]
        U[i] = [D.mul(u, x) for x in U[i]]

    t = 0
    while t < min(m, n):
        best = None
        for i in range(t, m):
            for j in range(t, n):
                if not D.is_zero(A[i][j]) and (best is None or D.norm(A[i][j]) < D.norm(A[best[0]][best[1]])):
                    best = (i, j)
        if best is None:
            break
        swap_rows(best[0], t)
        swap_cols(best[1], t)

        while True:
            for i in range(t + 1, m):
                if not D.is_zero(A[i][t]):
                    q, _ = D.divmod(A[i][t], A[t][t])
                    add_row(i, t, D.neg(q))
                    if not D.is_zero(A[i][t]):
                        swap_rows(i, t)
            for j in range(t + 1, n):
                if not D.is_zero(A[t][j]):
                    q, _ = D.divmod(A[t][j], A[t][t])
                    add_col(j, t, D.neg(q))
                    if not D.is_zero(A[t][j]):
                        swap_cols(j, t)
            if all(D.is_zero(A[i][t]) for i in range(t + 1, m)) and \
               all(D.is_zero(A[t][j]) for j in range(t + 1, n)):
                break

        bad = None
        for i in range(t + 1, m):
            for j in range(t + 1, n):
                _, r = D.divmod(A[i][j], A[t][t])
                if not D.is_zero(r):
                    bad = i
                    break
            if bad is not None:
                break
        if bad is not None:
            add_row(t, bad, D.one)
            continue

        scale_row(t, D.canonical_unit(A[t][t]))
        t += 1

    return A, U, V


def invariant_factors(S, D):
    """Nonzero diagonal entries of an SNF matrix over D."""
    out = []
    for i in range(min(len(S), len(S[0]) if S else 0)):
        if not D.is_zero(S[i][i]):
            out.append(S[i][i])
    return out
