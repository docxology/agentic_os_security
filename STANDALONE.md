# STANDALONE.md — agentic_os_security

This repository is a **standalone, self-versioned** project (v0.1.0). It is developed inside the docxology template ecosystem but owns its own `pyproject.toml`, git history, and virtual environment; it is not a member of any template uv workspace.

## Purpose of this file

Tell a future maintainer (human or agent) exactly what this project needs from its surroundings, how to take a clean copy elsewhere, and what must never be claimed about it.

## Clean-copy command

To materialize a fresh standalone copy from the template repository's exemplar mechanism, run from the **template repo root**:

```bash
uv run python scripts/repo/copy_exemplar.py --name agentic_os_security
```

(Check the template repo for the current exemplar invocation; the copy is then customized in place per the edits below.)

## Required post-fork edits

A fresh copy of a template exemplar is not yet this project. Complete, at minimum:

1. **Identity.** `pyproject.toml` (`name = agentic_os_security`, v0.1.0, MIT, author Daniel Ari Friedman), `CITATION.cff`, `codemeta.json` (no DOI — private posture), `manuscript/config.yaml` identity block.
2. **Domain config.** `domain_profile.yaml` (domain `agentic_security_research`), `experiment_plan.yaml` (24 candidates × 9 properties × 8 scenarios; primary output = evaluation matrix; 6 expected figures).
3. **Content.** `manuscript/` sections per the label registry, `src/agentic_os_security/` modules per the brief, `data/claim_ledger.yaml`, `tests/`.
4. **Docs.** Purge any template-era references (retired experiment tooling, live status pages, staged performance runs) from `README.md`, `AGENTS.md`, `docs/`, and skill stubs.
5. **Symlink registration.** Link the project into the template repo at `projects/ongoing/Agentic/agentic_os_security` so render-time discovery works.

## Validation commands

Run from this project root after any structural change:

```bash
uv sync
uv run python scripts/00_preflight.py
uv run python scripts/10_evaluation_analysis.py
uv run python scripts/z_generate_manuscript_variables.py
uv run pytest tests/ --cov=src --cov-fail-under=90
```

## Intentional dependencies

The **only** thing this project depends on outside itself is the **template repository's render pipeline** (Pandoc + pandoc-crossref + natbib + the LaTeX toolchain, driven by `scripts/pipeline/stage_03_render.py --project working/agentic_os_security` from the template root, with this project linked under `projects/working/`). Everything else — analysis, figures, data artifacts, variables, tests — is self-contained and runnable here with `uv sync`.

The manuscript deliberately avoids mermaid blocks so rendering from the template pipeline has no extra diagram prerequisites.

## What not to claim

- Do not claim a DOI, Zenodo deposit, publication venue, or any public availability. **This project is private**; no publishing actions without the owner's explicit ask.
- Do not claim penetration-testing results, exploit capability, or measured attack outcomes. All assessments are analytical judgments from documented designs.
- Do not claim numeric security scores for any candidate system.
- Do not cite sources that are not in `manuscript/references.bib` (65 source-derived + 6 scholarly keys, enforced by tests).
- Do not attribute numbers to the manuscript that do not trace to `data/claim_ledger.yaml`, the registry constants, or computed output in `output/`.
