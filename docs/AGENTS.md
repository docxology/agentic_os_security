# AGENTS.md — docs/

Rules for agents editing `docs/` in `agentic_os_security` (a private deep-review + prospectus project on agentic security and operating systems).

1. **Accuracy over polish.** Every command, filename, and count in these docs must match the tree: scripts are `00_preflight.py`, `10_evaluation_analysis.py`, `z_generate_manuscript_variables.py`; data artifacts are the four analysis outputs in `output/data/`; figures are the six registered PNGs.
2. **No stale content.** This project is a review + prospectus: it contains no numeric-optimization experiments, live status pages, or staged performance runs. If such template-era references appear, delete them on sight.
3. **Constants are pinned.** 9 properties, 24 candidates, 8 scenarios, 7 trust domains, 9 controls, 9 configuration invariants, 6 figures, 18 manuscript sections, 216 matrix cells, 65 + 6 = 71 bib keys. Quote these numbers only from the registry modules or the brief — never from memory of a previous doc revision.
4. **Private posture.** Never add publication metadata, DOI placeholders, or "available at" claims. No publishing instructions without an owner ask.
5. **Attribution discipline.** When describing assessments, keep the framing: analytical judgments from documented designs; vendor findings labeled as vendor findings; forecasts distinguished from measurements; no numeric security scores.
6. **Determinism.** Any doc that shows timestamp or reproducibility behavior must describe the `SOURCE_DATE_EPOCH`-honoring `build_clock.py` path, not wall-clock behavior.
7. **Scope.** Edit only files under `docs/` unless the task explicitly grants more. Root-level contracts live in the root `README.md` / `AGENTS.md` / `STANDALONE.md`.
