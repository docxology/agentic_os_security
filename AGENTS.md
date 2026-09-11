# AGENTS.md — agentic_os_security

Operating contract for any agent working in this repository. Read this file and `docs/agent_instructions.md` before editing.

## Identity

Standalone, **private** research project producing the manuscript *"Agentic Security and Operating Systems: A Deep Review and Prospectus of OpSec, Cognitive Security, and Agentic Cyber Security in the Emerging Present and Future"* (v0.1.0, MIT, author Daniel Ari Friedman). The authoritative content constants live in the section registries under `src/agentic_os_security/registry.py` (9 properties, 24 candidates, 8 scenarios), `evidence.py` (65 sources + capability baseline), `threat_model.py`, `trust_domains.py` (7 domains, 9 controls, 9 invariants), and `forecasts.py` (2028–2031 horizon).

## Layer contract

| Layer | Rule |
|---|---|
| `src/agentic_os_security/` | **Pure Python + matplotlib only.** No `infrastructure` imports anywhere in `src/`. Deterministic, importable, testable in isolation. |
| `scripts/` | Thin orchestrators: argparse, exit codes, imports from `src/`. No business logic. Template-repo detection for manuscript-variable injection only (see `scripts/CONVENTIONS.md`). |
| `manuscript/` | Pandoc markdown. Citations `[@key]` from `references.bib` only; cross-refs `[@sec:...]`/`[@fig:...]`/`[@tbl:...]`; `{{TOKEN}}` markers only from the token plan in `docs/syntax_guide.md`; **no mermaid blocks**. |
| `output/` | **Disposable.** Everything here regenerates from scripts; never hand-edit, never commit. |
| `data/` | Small, reviewed, version-controlled inputs and ledgers (`claim_ledger.yaml`). |
| `tests/` | Zero-mock, behavior-targeted tests against the real modules and real `manuscript/` files. |

The `infrastructure` package belongs to the sibling template repository, never to this one. Scripts may *detect* a template-repo parent solely to inject manuscript variables; `src/` must not reference it at all.

## Deterministic-artifact rule

Every generated artifact (figures, CSVs, JSON reports, resolved manuscripts) must be byte-reproducible for identical inputs:

- Never call `datetime.now()` (or any wall-clock read) in artifact-writing code.
- Timestamps come from `src/agentic_os_security/build_clock.py`, which honors `SOURCE_DATE_EPOCH` and falls back to the configured review date (2026-09-10, noon UTC).
- Figures use the deterministic rcParams in `src/agentic_os_security/figures/_common.py`; matplotlib Agg backend; no network access.

## Editing rules by directory

- `src/` — type hints everywhere, docstrings on public API, no `print()` (raise or return), no side effects at import time. Style details in `src/STYLE.md`.
- `scripts/` — keep thin; exit codes per `scripts/CONVENTIONS.md`; no logic that tests cannot reach via `src/`.
- `manuscript/` — follow the `{{VARIABLE}}` protocol and figure protocol in `manuscript/AGENTS.md`. Never edit `output/`-derived resolved trees; edit section sources and re-run the pipeline.
- `data/` — every numeric claim that appears in prose or figures must be registered in `data/claim_ledger.yaml`.
- `docs/` — keep honest and current; purge stale references when the project changes.

## Verification commands

```bash
uv run python scripts/00_preflight.py
uv run python scripts/10_evaluation_analysis.py
uv run python scripts/z_generate_manuscript_variables.py
uv run pytest tests/ --cov=src --cov-fail-under=90
```

## Private posture

Do not publish, deposit, archive, upload, or announce anything from this project without the owner's explicit ask: no DOI, no Zenodo, no PyPI/HF/IPFS artifacts, no public repository actions. `publication.github_repository: docxology/agentic_os_security` is recorded as private metadata only.

## Decision memory

Surprising local choices get a `WHY:` comment at the decision site (one or two lines: the constraint that forced the choice). If a choice affects other agents, also note it in `docs/agent_instructions.md`.
