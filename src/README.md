# src/

`src/agentic_os_security/` — the pure-Python core of **agentic_os_security**, a private deep review + prospectus of agentic security and operating systems (OpSec, cognitive security, agentic cyber security). Import name: `agentic_os_security`.

## Module map

| Module | Role |
|---|---|
| `registry.py` | 9 properties × 24 candidates × 8 scenarios; `matrix_rows()` → 216 stance rows (`strong \| partial \| weak \| n_a`) |
| `evidence.py` | 65 documented sources (tiered: official/advisory/incident_report/research/community) + capability baseline constants |
| `threat_model.py` | Failure paths (exploitation vs authorized misuse), adversary assumptions, authority ladder (propose→stage→authorize→exercise→audit→revoke), agent capability classes |
| `trust_domains.py` | 7 trust domains, 9 controls, 9 configuration invariants |
| `forecasts.py` | Confidence-tiered forecasts, horizon 2028–2031 |
| `build_clock.py` | Deterministic timestamps (`SOURCE_DATE_EPOCH`-aware; fallback review date 2026-09-10) |
| `project_paths.py` | Project-root discovery + canonical output paths |
| `experiment_config.py` | Loads/validates the `experiment:` block of `manuscript/config.yaml` |
| `manuscript_variables.py` | `generate_variables()` — every `{{TOKEN}}` in the manuscript as a string |
| `figures/` | 6 deterministic 300-dpi PNG generators (Agg, colorblind-safe, byte-reproducible) |
| `analysis/` | `pipeline.run_analysis()` — evaluation matrix CSV, scenario CSV, evidence summary JSON, validation report JSON + all 6 figures |

## Layer rule

Pure Python + matplotlib only. **No `infrastructure` imports.** No wall-clock in artifact code (use `build_clock.py`). No `print()` in library code. Single-sourced constants: import from the registry modules; never restate counts.

## Usage

```bash
uv run python scripts/00_preflight.py
uv run python scripts/10_evaluation_analysis.py
uv run pytest tests/ --cov=src --cov-fail-under=90
```

Consume the API directly:

```python
from agentic_os_security.registry import matrix_rows
from agentic_os_security.analysis.pipeline import run_analysis
```

Style: `STYLE.md`; agent rules: `AGENTS.md`.
