# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/), and the project adheres to
[Semantic Versioning](https://semver.org/).

## [0.1.5] — 2026-06-02

### Added
- PEP 561 `py.typed` marker so downstream type-checkers honour the package's type
  hints.
- A test-CI workflow (`tests`) running the suite on Python 3.10–3.13.
- This changelog.

## [0.1.4] — 2026-06-02

### Changed
- No code change. Released to validate the tag-triggered **trusted-publishing**
  pipeline (the `publish.yml` GitHub Action now publishes via OIDC, no token).

## [0.1.3] — 2026-06-02

### Changed
- No code change. Refreshed the README so the PyPI long-description (project page)
  is current.

## [0.1.2] — 2026-06-02

### Added
- `groups` CLI subcommand — the exact independent groups of a CSV from the command
  line (no amount column needed).
- A modular-rank fast path in `discover_invariants`: full column rank over a finite
  field certifies full rank over ℚ, so the "no conservation structure" honest-stop
  is decided in machine integers, skipping the exact rational solve. Same exact
  verdict, ~15× faster on dense data; exact generators unchanged when laws exist.
- Worked examples `scale/` (the speedup) and `cli_groups/` (the CLI), plus tests
  for `substrate/`.
- Ebook chapter 9, "One engine, many number systems" (substrate generality and
  parametric ℚ[t]); appendix A.6 moved into it.

## [0.1.1] — 2026-06-02

### Added
- `Reconciler.independent_groups()` — the exact independent groups (connected
  components) of the data in one linear union-find pass: no clustering, no `k`.

## [0.1.0] — 2026-06-02

### Added
- Initial release: exact, dependency-light discovery of conservation/balance laws,
  with break localisation and typing, modular (Smith-Normal-Form) escalation,
  cohomological residual typing, multi-source `H¹` consistency, and Euclidean-domain
  substrate generality. Plain-language `Reconciler` facade and CLI.

[0.1.5]: https://github.com/pcoz/numeric-rule-finder/releases/tag/v0.1.5
[0.1.4]: https://github.com/pcoz/numeric-rule-finder/releases/tag/v0.1.4
[0.1.3]: https://github.com/pcoz/numeric-rule-finder/releases/tag/v0.1.3
[0.1.2]: https://github.com/pcoz/numeric-rule-finder/releases/tag/v0.1.2
[0.1.1]: https://github.com/pcoz/numeric-rule-finder/releases/tag/v0.1.1
[0.1.0]: https://github.com/pcoz/numeric-rule-finder/releases/tag/v0.1.0
