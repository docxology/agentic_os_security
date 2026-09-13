# quickstart.md — first run in 5 minutes

`agentic_os_security` is a standalone, private research project: a deep review + prospectus of agentic security and operating systems (OpSec, cognitive security, agentic cyber security). You will install, generate the evaluation artifacts, hydrate the manuscript variables, and run the test gate.

## 1. Install

From the project root (standalone repo — not part of a uv workspace):

```bash
uv sync
```

## 2. Preflight

```bash
uv run python scripts/00_preflight.py
```

Checks the Python version, dependencies, and expected directories. Exit 0 = go.

## 3. Generate artifacts

```bash
uv run python scripts/10_evaluation_analysis.py
```

Produces the 11 registered figures in `output/figures/` (plus the cover graphical abstract) and 11 data artifacts in `output/data/` — including `evaluation_matrix.csv` (216 rows) and the all-green `validation_report.json`.

## 4. Manuscript variables

```bash
uv run python scripts/z_generate_manuscript_variables.py
```

Writes `output/data/manuscript_variables.json` (every `{{TOKEN}}` in `manuscript/*.md`). Requires step 3. When run inside the template environment (a template repo parent is detected) it also injects the resolved manuscript tree for rendering; standalone, it skips injection.

## 5. Tests

```bash
uv run pytest tests/ --cov=src --cov-fail-under=90
```

Zero-mock tests covering registry invariants, bib parity, token resolution, figure determinism, and analysis integration. 90% coverage on `src/` is the gate.

## 6. (Optional) Render

Rendering happens from the **sibling template repository**, with this project linked under `projects/working/`:

```bash
uv run python scripts/pipeline/stage_03_render.py --project working/agentic_os_security   # from template repo root
```

Produces PDF + HTML. See `rendering_pipeline.md`.

## Where to look next

- `architecture.md` — module map and data flow.
- `output_inventory.md` — what step 3 produced.
- `style_guide.md` — before editing any manuscript prose.
