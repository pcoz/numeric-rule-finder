# Roadmap

Numeric Rule Finder is a working, published library (`pip install
numeric-rule-finder`). This file tracks where it's going. It is a statement of
intent, not a promise of dates.

## Recently shipped

- **`Reconciler.independent_groups()`** — the exact independent groups (connected
  components) of the data in one linear union-find pass; no clustering, no `k`.
- **`groups` CLI subcommand** — the same, from the command line, on a CSV.
- **Modular-rank fast path in `discover_invariants`** — full column rank over a
  finite field certifies full rank over ℚ, so the common "no conservation
  structure" verdict (honest-stop) is reached in machine-integer arithmetic,
  skipping the exact rational RREF. Same exact answer, ~15× faster on dense data.
- **New worked examples** — `grouping_vs_ml`, `xml_moieties`, `scale`,
  `cli_groups` — plus ebook chapters for the ML head-to-heads, the raw-XML
  showcase, and substrate generality.
- **PyPI trusted publishing** — tag-triggered `publish.yml` now auto-publishes via
  OIDC (no token), verified green on `v0.1.4`.

## Near-term (housekeeping)

- **Test CI.** The repo runs only `publish.yml`; add a pytest workflow across
  Python 3.10–3.13 so the suite runs on every push.
- **`CHANGELOG.md`** and a **`py.typed`** marker (the package has type hints but
  ships no marker, so downstream type-checkers ignore them).

## Capability

- **First-class input readers.** SBML and PNML parsing currently live as example
  glue. A small `readers/` module (CSV core + XML/SBML/PNML/database) would make
  "any format that records movements" a real entry point.
- **Exact generators at scale.** The modular fast path accelerates the honest-stop
  case; extracting the actual law *vectors* on large matrices still uses the exact
  rational RREF. A fraction-free (Bareiss) or CRT-lifted null space would scale the
  has-laws case too.
- **Uniform facade for the deeper layers.** Surface modular laws, residual typing,
  and the multi-source `H¹` check through the plain-language facade and CLI as
  cleanly as balance and structure already are.

## Reach

- An expanded cross-domain example set (kept general; industry-specific prototypes
  belong in separate consumer repos that call this library).
- Tighter integration points for using the exact layer as a guardrail/pre-filter
  in front of ML pipelines (the composition shown in ebook Chapter 7).
