# rendering_pipeline.md — how the manuscript gets rendered

This project **does not own a render pipeline**. Rendering happens in the sibling template repository.

## Where rendering happens

- The project lives (via symlink) at `projects/ongoing/Agentic/agentic_os_security` inside the template repository, and is linked under `projects/working/` for render-time discovery.
- From the **template repo root**:

```bash
uv run python scripts/pipeline/stage_03_render.py --project working/agentic_os_security
```

The template pipeline (Pandoc + pandoc-crossref + natbib + LaTeX) consumes the manuscript sections and produces **PDF and HTML** (docx/epub/slides are disabled for this project).

## What this project does before rendering

```bash
uv run python scripts/10_evaluation_analysis.py           # output/figures + output/data must be current
uv run python scripts/z_generate_manuscript_variables.py  # resolves {{TOKENS}}; injects the resolved tree when the template repo is detected
```

`z_generate_manuscript_variables.py` walks up for a template-repo parent (`infrastructure/` + `pyproject.toml`). When found, it injects the resolved manuscript tree into the template environment for rendering. In standalone mode it skips injection and writes `output/data/manuscript_variables.json` only — rendering from the template env is the deliberate, single path.

## Mermaid prerequisite caveat

Some template-era pipelines required mermaid CLI preprocessing for embedded diagrams. **This project avoids mermaid entirely in `manuscript/*.md`** (enforced by `tests/test_manuscript_structure.py`), so no diagram tooling is a render prerequisite. Mermaid is permitted in `docs/` and root docs, which are not rendered through the pipeline. If a future edit adds a mermaid fence to the manuscript, the render will not be the thing that catches it — the test will.

## Render checklist

1. Analysis outputs current (`output/data/evaluation_matrix.csv` present).
2. Variables script run successfully (`manuscript_variables.json` written; no unresolved tokens — checked by tests).
3. No `{{TOKEN}}` left in any section the renderer will consume.
4. Render from the template root, not from this repo.
