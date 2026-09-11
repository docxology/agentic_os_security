# STYLE.md — src/ style

## Types & signatures

- Type hints on every public function, method, and dataclass field. Use modern built-in generics (`list[str]`, `dict[str, str]`, `tuple[int, int]`); `from __future__ import annotations` where forward refs are needed.
- Dataclasses over dicts for structured records (`Property`, `Candidate`, `Scenario`, `Source`, `TrustDomain`, `Control`, `Forecast`, `FailurePath`). Tuples for immutable collections (`SOURCES`, `TRUST_DOMAINS`, `CONFIGURATION_INVARIANTS`); dict only where keyed lookup is the point (`property_stance`, `CAPABILITY_BASELINE`).
- Module-level constants are `UPPER_SNAKE`, typed, and immutable in spirit.

## Docstrings

- One-line summary on every public function and module; expand only where the contract is non-obvious (e.g., the authority-ladder rungs, the meaning of `require_analysis_outputs`).
- Docstrings state contracts, not narrate implementation.

## Errors

- Raise typed exceptions (`ExperimentConfigError`, …) with actionable messages; never `print()` in library code, never bare `except:`. Scripts translate exceptions into exit codes.

## Determinism

- No `datetime.now()`/wall-clock anywhere in artifact-writing code; time comes only from `build_clock.py` (honors `SOURCE_DATE_EPOCH`; fallback review date 2026-09-10 noon UTC).
- No randomness, no network, no locale-dependent formatting in outputs. Iterate dicts in defined order when serializing.
- Figures: Agg backend, `DETERMINISTIC_RC` from `figures/_common.py`, colorblind-safe palette constant, `save_figure()` with dpi=300; byte-identical across runs.

## Purity

- No `infrastructure` imports, no I/O outside `output/` (via `project_paths.py`), no side effects at import time, no globals mutated at runtime.

## Naming

- Files/modules: `snake_case`. Ids: `snake_case` strings pinned by the brief (`qubes_os`, `scoped_credentials`, …). Public API names are stable contracts — renaming one is a cross-layer edit (scripts + tests same commit).

## Tests expectation

- Every public behavior is reachable without mocks; if a module needs mocking to test, the module design is wrong. Coverage gate: `uv run pytest tests/ --cov=src --cov-fail-under=90`.
