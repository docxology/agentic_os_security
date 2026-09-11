# AGENTS.md — src/

Rules for agents editing `src/` in `agentic_os_security` (private deep-review + prospectus project on agentic security & OS security).

1. **Pure layer.** `src/` is pure Python + matplotlib. **No `infrastructure` imports anywhere in `src/`.** No network, no subprocesses, no shell-outs, no filesystem writes except into `output/` (via `project_paths.py`) or explicit tmp dirs in tests.
2. **Determinism.** No wall-clock in artifact-writing code — `build_clock.py` (`SOURCE_DATE_EPOCH`-aware) is the only clock. Figures byte-identical across runs given identical inputs (Agg backend, deterministic rcParams from `figures/_common.py`).
3. **Single-sourced constants.** The 9 properties, 24 candidates, 8 scenarios, 7 trust domains, 9 controls, 9 invariants, 65 sources, and forecast set live in the registry modules. Never duplicate a count or an id list in another module, a script, or a test — import it.
4. **API stability.** Public functions/dataclasses are a contract consumed by scripts, tests, and the token pipeline: `registry.matrix_rows()`, `evidence.SOURCES`, `threat_model.AUTHORITY_LADDER`, `trust_domains.TRUST_DOMAINS/CONTROLS/CONFIGURATION_INVARIANTS`, `forecasts.counts_by_confidence()`, `manuscript_variables.generate_variables()`, `analysis.pipeline.run_analysis()`, `figures.*.generate_<name>()`. Changing signatures is a cross-layer change — update scripts and tests in the same edit.
5. **Style.** Type hints on all public API, docstrings on public functions/modules, no `print()` (raise or return), no side effects at import time. Details: `STYLE.md`.
6. **No numeric security scores.** Stances are `strong | partial | weak | n_a`; forecast confidence is `high | moderate | low`. Never introduce scoring numerics.

## Module map

`registry.py` · `evidence.py` · `threat_model.py` · `trust_domains.py` · `forecasts.py` · `build_clock.py` · `project_paths.py` · `experiment_config.py` · `manuscript_variables.py` · `figures/` (6 generators + `_common.py`) · `analysis/` (`pipeline.run_analysis`).

Verification: `uv run pytest tests/ --cov=src --cov-fail-under=90`.
