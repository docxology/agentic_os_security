# TODO — agentic_os_security

Forward-only; completed items move to `Done`.

## Open

## Done

- [x] v0.4.0 delivered (2026-09-11): cover DOI + auto date, taller zero-code cover, formalisms, OS stack
- [x] v0.3.0 delivered (2026-09-11): graphical abstract cover, extended titles, incident register, CIF mapping, author-work citations
- [x] Scaffold project from `template_code_project` exemplar (v0.1.0, 2026-09-10)
- [x] v0.1.0: 18-section modular manuscript, 24×9 matrix, 6 figures, 92.30% coverage
- [x] v0.1.0: template pipeline render + stage_04 validation green, private remote pushed
- [x] v0.2.0 research round: six-scout deep web research (2026-09-11), consolidated dossier
- [x] v0.2.0: bibliography 71→156 entries (85 web-verified sources)
- [x] v0.2.0: evidence registry 65→150 sources; defensive-stack (24×8), update-window, and orchestration mediation data layers
- [x] v0.2.0: six figures redesigned (category bands, marginals, two-lane timeline, swimlanes) + three new figures (defensive_stack, update_windows, agent_surface)
- [x] v0.2.0: manuscript +49–60% technical depth; QSB-118 direction corrected; NCSC/AISI/AIxCC dates corrected
- [x] v0.2.0: typography — extarticle 9pt, 0.15in margins; version bumps across metadata
- [x] v0.2.0: sidecar hydration path fixed (TEMPLATE_REPO_ROOT honored by z script; resolved-tree injection from pipeline env)
- [x] v0.2.0: 87 tests, 94.70% coverage; stage_03/04/05 green; token-literal and LaTeX-corruption defects fixed

## Workflowz review — 2026-11-10

- [ ] AOS-001 — P1: Make the Python contract and lockfile self-consistent. Pin `.python-version` from `3.15` to `3.15.2`; retain the declared floor `>=3.11` in `pyproject.toml:16`, regenerate `uv.lock` so its root `requires-python` is no longer stale at `>=3.10` (`uv.lock:3`), change `check_python_version()` from 3.10 to 3.11 (`scripts/00_preflight.py:48-53`), and correct the 3.10 installation guidance (`docs/troubleshooting.md:7`). No dependency has been identified that requires a different target. **Acceptance:** `uv sync --locked && uv run python -c 'import sys; assert sys.version_info[:3] == (3, 15, 2)'` succeeds without changing `uv.lock`, and `uv run python scripts/00_preflight.py` reports the pinned interpreter as supported. **Dependencies:** none; lock regeneration must use the existing constraints, not blanket upgrades.

- [ ] AOS-002 — P1: Fail manuscript hydration when a detected template cannot provide the injector. `scripts/z_generate_manuscript_variables.py:85-93` currently catches `ImportError`, prints “skipping injection,” and returns 0 even though template mode requires `write_resolved_manuscript_tree`; this contradicts the failure exit-code rule in `scripts/CONVENTIONS.md:8-12`. Return nonzero with the original import diagnostic, while preserving intentional standalone success. Add a real subprocess regression test using a temporary template layout with `infrastructure/` and `pyproject.toml` but no injector module. **Acceptance:** `uv run pytest tests/test_scripts_smoke.py::test_template_injection_import_failure_is_fatal -q` passes, with the fixture asserting exit 1 and an injection diagnostic; `uv run python scripts/z_generate_manuscript_variables.py` still exits 0 in this standalone checkout after analysis outputs exist. **Dependencies:** none.

- [ ] AOS-003 — P1: Prevent failed analysis validation from leaving apparently usable artifacts. `run_analysis()` writes the matrix, ten other data artifacts, and `figure_registry.json` before calling `_run_checks()` (`src/agentic_os_security/analysis/pipeline.py:654-682`), despite `AnalysisValidationError` being documented to block artifact emission (`src/agentic_os_security/analysis/pipeline.py:234-236`). Run all registry checks before publishing outputs, or stage and atomically publish a complete artifact set; also remove the duplicate `candidate_basis_rows` summary key at `src/agentic_os_security/analysis/pipeline.py:693-700`. Add a regression proving invalid registry state raises without creating/replacing output artifacts. **Acceptance:** `uv run pytest tests/test_analysis_integration.py -q` passes, including a failure-case assertion that no declared data artifact or figure registry is emitted after `AnalysisValidationError`; the success case still produces 12 data files and 12 PNGs. **Dependencies:** none; preserve zero-mock tests and deterministic bytes.

- [ ] AOS-004 — P1: Make preflight actually validate manuscript configuration. Its docstring promises configuration and registry validation (`scripts/00_preflight.py:3-6`), but `main()` only checks interpreter/imports/layout/package imports (`scripts/00_preflight.py:103-116`) and never calls `load_experiment_config()`. Add the existing validator to preflight and test a complete temporary checkout whose `experiment.candidate_ids` is invalid. **Acceptance:** `uv run pytest tests/test_scripts_smoke.py -q` passes, including exit 1 and an `experiment.candidate_ids` diagnostic for the malformed checkout; `uv run python scripts/00_preflight.py` exits 0 on the repository configuration. **Dependencies:** coordinate the interpreter assertion with AOS-001, but configuration validation is independently closable.

- [ ] AOS-005 — P2: Repair the fork configuration example so it passes the repository’s own loader. The file calls itself a reference copy to keep synchronized (`manuscript/config.yaml.example:1-2`), yet supplies only 2 candidates, 2 categories, 1 scenario, 1 trust domain, 1 control, and 1 figure (`manuscript/config.yaml.example:63-76`), while `REQUIRED_KEY_SHAPES` requires 24/8/8/7/9/11 (`src/agentic_os_security/experiment_config.py:37-48`). Populate the complete canonical registries (with fork-safe identity/publication fields retained) and add a test that loads the example from an isolated project root. **Acceptance:** `uv run python - <<'PY'
from pathlib import Path
from tempfile import TemporaryDirectory
from agentic_os_security.experiment_config import load_experiment_config
with TemporaryDirectory() as d:
    root = Path(d); (root / 'manuscript').mkdir()
    (root / 'manuscript/config.yaml').write_bytes(Path('manuscript/config.yaml.example').read_bytes())
    load_experiment_config(root)
print('example config valid')
PY` prints `example config valid`. **Dependencies:** none; do not relax canonical registry lengths to accommodate the example.

- [ ] AOS-006 — P2: Enforce the documented coverage gate in CI. The repository requires branch coverage of at least 90% (`pyproject.toml:43-50` and `README.md` quickstart), but CI runs only `pytest -q` (`.github/workflows/ci.yml:14-16`), allowing coverage regressions to merge. Change the CI test command to `uv run --no-progress --extra dev pytest --cov=src --cov-fail-under=90 -q`. **Acceptance:** `uv run --no-progress --extra dev pytest --cov=src --cov-fail-under=90 -q` exits 0 and reports branch coverage at least 90%; the workflow contains that same gate. **Dependencies:** none; no new coverage exclusions.

- [ ] AOS-007 — P2: Stop versioning disposable generated output. The layer contract says everything under `output/` is regenerated and must never be committed (`AGENTS.md:16`; `docs/agent_instructions.md:18`), but this base contains rendered manuscripts, PDFs/build logs, slides, web output, reports, figures, and data under `output/`, and `.gitignore:1-20` has no `output/` rule. Remove the generated tree from tracking, add `/output/`, and update the README inventory wording so local regeneration—not committed build products—is the source of these files; preserve the published Zenodo release and its DOI. **Acceptance:** `test -z "$(git ls-files output)" && git check-ignore output/data/evaluation_matrix.json 2>/dev/null || git check-ignore output/data/evaluation_matrix.csv` succeeds, followed by `uv run python scripts/10_evaluation_analysis.py` regenerating the expected local artifacts without creating tracked files. **Dependencies:** perform after AOS-003 so failed validation cannot leave a misleading regenerated set; no publication/deposit action.