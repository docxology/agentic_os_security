# agent_instructions.md — operating constraints for future agents

You are working in `agentic_os_security`, a standalone, **private** research project producing the manuscript *"Agentic Security and Operating Systems"* — a deep review and prospectus of OpSec, cognitive security, and agentic cyber security. These are the constraints that have bitten agents before; they are enforced by review and tests.

## Non-negotiables

1. **Layer contract.** `src/` is pure Python + matplotlib. **No `infrastructure` imports anywhere in `src/` or `scripts/`.** Scripts may detect a template-repo parent (walk up for `infrastructure/` + `pyproject.toml`) *only* to inject manuscript variables; `src/` never references it.
2. **Determinism.** Never use `datetime.now()` (or any wall-clock) in artifact-writing code. Timestamps come from `src/agentic_os_security/build_clock.py`, which honors `SOURCE_DATE_EPOCH` and falls back to the review date (2026-09-10, noon UTC). Figures must be byte-identical across runs given identical inputs.
3. **Constants are single-sourced.** The 9 properties, 24 candidates, 8 scenarios, 7 trust domains, 9 controls, 9 invariants, 216 matrix cells, 65 source keys, and 6 figures live in `src/agentic_os_security/` registry modules. Never restate them as literals in a new place; import or reference.
4. **Citation + cross-ref protocol.** Manuscript prose cites only keys in `manuscript/references.bib` (65 source-derived + 6 scholarly) and cross-references only defined `{#sec:}/{#fig:}/{#tbl:}` labels. No raw `\cite{`, no literal "Figure 3".
5. **No mermaid in the manuscript.** The render pipeline has no diagram prerequisites; keep it that way. Mermaid is allowed in `docs/` and root docs only.
6. **Private posture.** No publishing, DOI, Zenodo, PyPI/HF/IPFS, or repo-visibility actions without an explicit owner ask.
7. **Claim hygiene.** No penetration-testing claims, no vendor numbers presented as independent measurements, no numeric security scores. Every numeric claim in prose traces to `data/claim_ledger.yaml`, a registry constant, or a computed output artifact.

## Workflow rules

- **Workflow:** edit `src/` → regenerate analysis (`uv run python scripts/10_evaluation_analysis.py`) → regenerate variables (`uv run python scripts/z_generate_manuscript_variables.py`) → run tests (`uv run pytest tests/ --cov=src --cov-fail-under=90`).
- `output/` is disposable. Never hand-edit or commit it; regenerate.
- `{{TOKEN}}` markers in `manuscript/*.md` come only from the token plan (`docs/syntax_guide.md`); the unresolved-token check lives in `test_manuscript_variables.py`.
- `WHY:` comments: leave one at any surprising local choice so the next agent does not "fix" it back.
- When you find stale template-era references (retired experiment tooling, numeric-optimization sweeps, live status pages, staged performance runs), delete them in the files you own; do not preserve them "for history".

## Anti-patterns (seen in the wild)

- Hardcoding counts (e.g., `24`) in a doc or test instead of importing the registry constant.
- Adding a wall-clock timestamp to a figure caption or JSON report "for debugging".
- Writing a test that mocks the registry, then passes while the real registry drifts.
- Re-deriving the evidence baseline (30 targeted entities, 122 AISI runs, 10 unsanctioned runs, 2027 capability horizon) from memory — read `src/agentic_os_security/evidence.py`.
