# forking_guide.md

`agentic_os_security` is a **private, standalone** repository. This guide covers making a derived copy that stays honest.

## Before you fork

1. Read the root `README.md` and `AGENTS.md` — the layer contract, determinism rules, and private posture apply to any fork.
2. Understand the claim boundaries: analytical judgments from documented designs; no penetration testing; no numeric security scores. A fork that starts assigning scores has left this project's epistemic frame.

## Making the copy

- Preferred: the template repository's exemplar mechanism — see `STANDALONE.md` for the `copy_exemplar` command and required post-fork edits.
- Plain git clone also works: the repo is self-contained (`uv sync` from the root, then the quickstart sequence).

## Required post-fork edits

1. Identity: `pyproject.toml`, `CITATION.cff`, `codemeta.json`, `manuscript/config.yaml` — change name/author/version to the fork's; **keep the private posture** unless you own the publication decision.
2. Re-run the full validation chain and make it green *before* content edits:
   ```bash
   uv sync
   uv run python scripts/00_preflight.py
   uv run python scripts/10_evaluation_analysis.py
   uv run python scripts/z_generate_manuscript_variables.py
   uv run pytest tests/ --cov=src --cov-fail-under=90
   ```
3. If you extend the evidence base, extend `references.bib` + `evidence.py` together and update `data/claim_ledger.yaml` — the parity tests enforce it.
4. Update the docs (`docs/`, `README.md`, skill stubs) to describe the fork, not this project. Purge references to capabilities the fork does not have.

## Render setup for a fork

Forks that want PDF/HTML rendering need the same relationship to a template render environment: link the fork under the template repo's `projects/working/` and render with `uv run python scripts/pipeline/stage_03_render.py --project working/<fork>` from the template root. Keep the manuscript free of mermaid fences.

## What not to claim in a fork

- No publication/DOI/Zenodo claims without the owner's explicit ask.
- No claim that assessments are empirically validated (they are analytical judgments from documented designs).
- No numeric security scores.
- No new "staged performance run" or "live status page" framing — this project is a review + prospectus, and its outputs are the matrix, figures, and manuscript.
