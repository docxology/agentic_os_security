# AGENTS.md — src/agentic_os_security/

Package-level contract for agents editing this package (deep review + prospectus project: *Agentic Security and Operating Systems* — OpSec, cognitive security, agentic cyber security).

1. **Purity.** Pure Python + matplotlib. **No `infrastructure` imports — ever.** No wall-clock in artifact code (`build_clock.py` only, `SOURCE_DATE_EPOCH`-aware). No network. No `print()`.
2. **Pinned constants.** 9 properties, 24 candidates, 8 scenarios, 7 trust domains, 9 controls, 9 configuration invariants, 65 sources, 6 figures, 18 sections. The ids are pinned (e.g. candidates `qubes_os`, `nixos`, `secureblue`, … `parrot_security`; properties `containment` … `human_usability`; domains `administration` … `recovery`). Stances `strong | partial | weak | n_a`; forecast confidence `high | moderate | low`; horizon 2028–2031. Import, don't restate.
3. **Public API is a contract** consumed by scripts, tests, and the token pipeline: `matrix_rows()` (216), `SOURCES` (65, keyed to bib), `FAILURE_PATHS`, `AUTHORITY_LADDER`, `TRUST_DOMAINS`/`CONTROLS`/`CONFIGURATION_INVARIANTS`, `FORECASTS`/`counts_by_confidence()`, `generate_variables()`, `run_analysis()`, `figures/*.generate_<name>()`. Signature changes are cross-layer edits (update scripts + tests simultaneously).
4. **Determinism.** Artifacts byte-reproducible for identical inputs; figures via `figures/_common.py` (`apply_style`, `save_figure`, `DETERMINISTIC_RC`, colorblind-safe palette).
5. **Style.** Type hints, docstrings, typed exceptions, no side effects at import time — see `../STYLE.md`.

Verify: `uv run pytest tests/ --cov=src --cov-fail-under=90` from the project root.
