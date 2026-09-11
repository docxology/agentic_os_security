# CONVENTIONS.md — scripts/

## Orchestration stance

Scripts are the **only** sanctioned entry points for side effects. They must stay thin: argparse → validate → call `src/` → exit. If a script grows a loop, a dataclass, or a second code path, move it into `src/agentic_os_security/` and re-export the entry point.

## Exit codes

- `0` — success.
- `1` — any failure. Print one diagnostic line (what failed, where); let `--verbose` add detail. Never continue past a failed check.

## Determinism contract

- Artifacts are byte-reproducible for identical inputs. No wall-clock, no randomness, no network in artifact paths.
- Timestamps: exclusively via `src/agentic_os_security/build_clock.py` (`build_timestamp()` / `build_date()` / `build_epoch()`), which honors `SOURCE_DATE_EPOCH` with fallback to the review date (2026-09-10, noon UTC).
- Figure determinism comes from `figures/_common.py` rcParams; scripts never tweak matplotlib state directly.

## The z-script template-env injection pattern

`z_generate_manuscript_variables.py`:

1. `generate_variables(project_root, require_analysis_outputs=True)` — `--allow-draft` sets `require_analysis_outputs=False` for draft iteration (draft output is not render-grade).
2. `save_variables(variables, output/data/manuscript_variables.json)` — always written.
3. `_template_repo_root()`: walk **up** from the project root; a parent containing both `infrastructure/` and `pyproject.toml` is the template repo.
4. Template mode → `infrastructure.rendering.manuscript_injection.write_resolved_manuscript_tree(project_root, variables)`; standalone mode → skip, print the JSON path. There is no third mode; standalone rendering is performed from the template repo against the `projects/working/` link.

## Naming & numbering

- `NN_name.py` prefix = execution order; `z_` prefix = runs last, after all analysis stages.
- One script, one job. New capabilities become new numbered scripts (and get added to `README.md` + `docs/quickstart.md`), not new flags on old scripts.

## Prohibited in scripts/

- `infrastructure` imports outside the guarded z-script injection call.
- Business logic, registry constants inline, file-path literals outside `project_paths.py`.
- Wall-clock reads, network calls, interactive prompts.
