# scripts/

Thin orchestrators for **agentic_os_security** — a private deep review + prospectus of agentic security and operating systems (OpSec, cognitive security, agentic cyber security). All logic lives in `src/agentic_os_security/`; these scripts parse arguments, call into `src/`, and map failures to exit codes.

## Scripts

| Script | What it does |
|---|---|
| `00_preflight.py` | Verifies Python version, dependencies, and expected directories. Run first. |
| `10_evaluation_analysis.py` | Runs the evaluation analysis: 6 registered figures (`output/figures/`) + 4 data artifacts (`output/data/`) + all-green validation report. |
| `z_generate_manuscript_variables.py` | Resolves every `{{TOKEN}}` from the manuscript token plan into `output/data/manuscript_variables.json`; injects the resolved manuscript tree when a template-repo environment is detected (standalone mode skips injection). Requires the analysis outputs unless `--allow-draft`. |

## Run order

```bash
uv run python scripts/00_preflight.py
uv run python scripts/10_evaluation_analysis.py
uv run python scripts/z_generate_manuscript_variables.py
uv run pytest tests/ --cov=src --cov-fail-under=90
```

All commands run from the project root. Conventions (exit codes, determinism, the template-env injection pattern): `CONVENTIONS.md`. Editing rules: `AGENTS.md`.
