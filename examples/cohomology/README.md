# Demo — typing the residual as a cohomology obstruction

> **Run:** `python examples/cohomology/cohomology_demo.py`

Types a reconciliation residual exactly:

- **conservation complex** — an imbalance is a *coboundary* (re-attributable, with
  a witness flow) or a genuine *obstruction* in `coker(S)`, naming the violated law;
- **discrepancy sheaf** — pairwise reconciliations are mutually consistent, or form
  an irreducible cycle in `H¹` that no per-source correction can fix.

An optional section runs against a real `petra-nn` net if you pass a petra-nn
`examples/` path as an argument.
