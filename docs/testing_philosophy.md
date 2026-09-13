# testing_philosophy.md — how tests earn their place

`tests/` exists to defend the manuscript's claim chain, not to decorate the repo. Coverage gate: **≥90% on `src/`**, enforced with `--cov-fail-under=90`.

## Zero-mock

Tests exercise the real modules, real `manuscript/` files, and real config — no mocks, no stubs, no patched registries. A test that mocks the registry can pass while the registry drifts; that test is worse than no test. Temporary directories (`tmp_path` fixtures) are the only acceptable isolation.

## Behavior-targeted, not implementation-targeted

Assert what a consumer observes, not how the code is wired:

- **Structural invariants**: 24 unique candidate ids, 9 properties, every candidate's `property_stance` covers all 9 properties with valid vocabulary, 216 matrix rows, 8 unique scenarios, 7 trust domains, 9 controls, 9 invariants.
- **Parity**: every `evidence.SOURCES` key has a matching `@...{key,` entry in `manuscript/references.bib` (155 + 13 = 168); every citation key in prose exists in the bib.
- **Resolution**: every `{{X}}` in `manuscript/*.md` resolves via `generate_variables()`; values match the pinned constants.
- **Determinism**: two consecutive figure-generation runs are byte-identical.
- **Integration**: `run_analysis` writes the 11 data artifacts + 11 registered figures (+ the cover graphical abstract); the validation report is all-green.
- **Structure**: 18 section files, unique sec labels, all `[@fig:`/`[@tbl:` targets defined, no mermaid fences, no raw `\cite{`/`\ref{`.
- **Real errors**: `experiment_config` raises `ExperimentConfigError` on missing/invalid keys (tmp-dir fixture), not silent defaults.

## What does NOT earn a test

- Tautologies ("function exists and returns not-None"), source-text assertions, mock echoes, padding parameter rows over the same path.
- Plumbing: a test proving module A forwards to module B tests the import statement.

## Running

```bash
uv run pytest tests/ --cov=src --cov-fail-under=90
```

Deterministic and isolated by default; slow full-pipeline subprocess checks live behind the `slow` marker for release profiles.
