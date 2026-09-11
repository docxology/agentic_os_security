# troubleshooting.md

Symptom-first guide. Run `uv run python scripts/00_preflight.py` first — it catches most environment causes.

## Preflight fails: missing dependency or wrong Python

- `uv sync` from the project root (standalone repo; Python ≥ 3.10).
- Do **not** try to resolve this project inside a template uv workspace; it is deliberately standalone.

## `10_evaluation_analysis.py` fails: `ExperimentConfigError`

- `manuscript/config.yaml` is missing or missing required keys. Compare against `manuscript/config.yaml.example`; the `experiment:` block must satisfy `src/agentic_os_security/experiment_config.py`.

## `z_generate_manuscript_variables.py` fails: analysis outputs missing

- The variables script requires `output/data/evaluation_matrix.csv` (and the other analysis artifacts) to exist. Run `uv run python scripts/10_evaluation_analysis.py` first, then retry.
- If you intentionally want a draft without analysis outputs, use `--allow-draft` (the draft output is not render-grade).

## Tests fail: token unresolved / invented token

- A `{{TOKEN}}` in `manuscript/*.md` is not in the token plan (`docs/syntax_guide.md`) or has no value from `generate_variables()`. Either replace the token with prose or add it to `manuscript_variables.py` *and* the plan — never one without the other.

## Tests fail: bib parity

- A key exists in `manuscript/references.bib` but not in `evidence.SOURCES`, or vice versa. The 65 source-derived keys must match exactly on both sides (plus the 6 scholarly entries). Fix the registry, not the test.

## Tests fail: figures not byte-identical

- Wall-clock or random data leaked into a figure. Generators must use the deterministic rcParams in `figures/_common.py` and take all inputs from the registry modules. Check for `datetime.now()` — there should be none; timestamps come from `build_clock.py` (`SOURCE_DATE_EPOCH`-aware).

## Tests fail: mermaid fence or raw `\cite{` in manuscript

- Remove the mermaid fence (no diagram prerequisites are permitted) or convert to a pandoc citation `[@key]` with a key from `references.bib`.

## Render fails from the template repo

- Rendering happens **only** from the template repo root: `uv run python scripts/pipeline/stage_03_render.py --project working/agentic_os_security`, with this project linked under `projects/working/`.
- Ensure the variables script ran in the template environment (injection step) and no `{{TOKEN}}` remains in the resolved tree.

## Figure looks wrong / numbers look wrong

- Do not edit the PNG or CSV. Fix the generator or the registry constant, rerun the analysis script, and if a prose-backed number changed, update `data/claim_ledger.yaml`.

## Still stuck

- Check `output/data/validation_report.json` — the self-checks name the broken invariant.
- Then check `docs/agent_instructions.md` anti-patterns; most failures are one of them.
