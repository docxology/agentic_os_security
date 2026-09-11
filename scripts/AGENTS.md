# AGENTS.md — scripts/

`scripts/` contains **thin orchestrators** for `agentic_os_security` (private deep-review + prospectus project on agentic security & OS security). No business logic lives here.

## Rules

1. **Thin only.** Parse args, call into `src/agentic_os_security/`, translate failures to exit codes. Any logic worth testing lives in `src/` where tests can reach it without subprocesses.
2. **Imports.** Import from `src/` only. **No `infrastructure` imports** — except that `z_generate_manuscript_variables.py` may call the template repo's `infrastructure.rendering.manuscript_injection.write_resolved_manuscript_tree(...)` **only after** it detects a template-repo parent.
3. **Determinism.** No wall-clock in anything a script writes; artifacts get time from `src/agentic_os_security/build_clock.py` (`SOURCE_DATE_EPOCH`-aware). Never `datetime.now()`.
4. **output/ is written, never read as truth.** Scripts regenerate it; they never branch on hand-edited content.

## Exit codes

| Code | Meaning |
|---|---|
| 0 | success |
| 1 | check/execution failure (preflight failure, analysis error, generation error) |

Scripts print a single-line cause on failure and exit non-zero; no tracebacks as UX.

## The z-script template-env injection pattern

`z_generate_manuscript_variables.py` is the one script that touches the template world:

1. Generate variables via `manuscript_variables.generate_variables(project_root)` (requires analysis outputs; `--allow-draft` relaxes this for draft iteration).
2. Write `output/data/manuscript_variables.json` via `save_variables(...)` — always, in both modes.
3. Detect a template-repo parent by **walking up** from the project root for a directory containing both `infrastructure/` and `pyproject.toml` (`_template_repo_root()`).
4. **Template mode:** call `infrastructure.rendering.manuscript_injection.write_resolved_manuscript_tree(project_root, variables)` to hydrate the manuscript tree in the template environment.
5. **Standalone mode:** skip injection, print the variables path — rendering happens separately from the template env (`projects/working/` link + `scripts/pipeline/stage_03_render.py --project working/agentic_os_security`).

## Current scripts

| Script | Purpose |
|---|---|
| `00_preflight.py` | environment/dependency/directory checks |
| `10_evaluation_analysis.py` | runs `analysis.pipeline.run_analysis` (6 figures + 4 data artifacts) |
| `z_generate_manuscript_variables.py` | token pipeline → `manuscript_variables.json` (+ template injection when detected) |

Numbering is order-of-execution (`00` → `10` → `z` last). Adding a script: keep it thin, follow the exit-code table, and update `scripts/README.md` + `docs/quickstart.md`.
