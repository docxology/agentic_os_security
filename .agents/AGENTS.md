# AGENTS.md — .agents/

Rules for agents editing `.agents/` in `agentic_os_security` (private deep-review + prospectus project on agentic security & OS security).

1. **Skills describe, never override.** `skills/agentic-os-security/SKILL.md` points at the authoritative contracts (root `AGENTS.md`, `docs/`, registry modules). If the skill and a contract disagree, the contract wins — fix the skill.
2. **Accuracy bar.** Commands, filenames, and counts in skill docs must match the tree exactly (`00_preflight.py`, `10_evaluation_analysis.py`, `z_generate_manuscript_variables.py`; 9 properties, 24 candidates, 8 scenarios, 6 figures, 18 sections, 71 bib keys).
3. **No stale content.** Purge any leftover template-era experiment tooling references on sight; they belong to no version of this project.
4. **Private posture.** Skills must never instruct publishing, DOI, Zenodo, or repo-visibility actions.
5. **YAML frontmatter required** for `SKILL.md`: `name` and `description` at minimum.
