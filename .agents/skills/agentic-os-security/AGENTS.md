# AGENTS.md — skill: agentic-os-security

1. `SKILL.md` is the entry point: YAML frontmatter (`name`, `description`), when-to-use, quick reference commands, pitfalls, cross-references.
2. Commands and counts must match the tree exactly (scripts: `00_preflight.py`, `10_evaluation_analysis.py`, `z_generate_manuscript_variables.py`; constants: 9/24/8/7/9/9/216/65+6/6/18). On drift, update the skill and the contract doc together.
3. Never add publishing, DOI, Zenodo, or visibility instructions — the project is private.
4. Purge any stale template-era experiment-tooling content on sight.
5. The skill points at contracts; it never overrides them. Conflicts resolve in favor of root `AGENTS.md` and `docs/`.
