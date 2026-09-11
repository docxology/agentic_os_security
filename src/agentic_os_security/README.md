# agentic_os_security (package)

Pure-Python core of the **agentic_os_security** project — a private deep review + prospectus of agentic security and operating systems: OpSec, cognitive security, and agentic cyber security.

## What's inside

- **Evaluation backbone** — `registry.py`: 9 properties × 24 OS candidates × 8 scenarios, qualitative stances (`strong | partial | weak | n_a`), 216-cell matrix.
- **Evidence base** — `evidence.py`: 65 tiered sources mirroring the manuscript bibliography + a pinned capability baseline.
- **Threat model** — `threat_model.py`: exploitation vs authorized misuse, authority ladder, agent capability classes.
- **Agentic architecture** — `trust_domains.py`: 7 trust domains, 9 controls, 9 configuration invariants.
- **Forecast** — `forecasts.py`: confidence-tiered claims, horizon 2028–2031.
- **Infrastructure-of-record** — `build_clock.py` (deterministic time), `project_paths.py`, `experiment_config.py`, `manuscript_variables.py` (the `{{TOKEN}}` pipeline).
- **Generators** — `figures/` (6 deterministic PNGs) and `analysis/` (`run_analysis`: 4 data artifacts + figures + validation report).

## Guarantees

- **Pure layer**: no `infrastructure` imports, no network, no wall-clock in artifacts (`build_clock.py` honors `SOURCE_DATE_EPOCH`).
- **Deterministic**: identical inputs → byte-identical figures and data artifacts.
- **Single-sourced constants**: every count and id list lives here once; scripts, tests, and manuscript tokens import it.

## Run

```bash
uv run python scripts/10_evaluation_analysis.py           # figures + data artifacts
uv run pytest tests/ --cov=src --cov-fail-under=90        # ≥90% coverage gate
```
