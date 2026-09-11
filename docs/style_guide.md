# style_guide.md — RASP + attribution discipline

Manuscript prose style for `agentic_os_security`.

## RASP

- **R**elevant — every paragraph earns its place in a deep review; one idea per paragraph; no filler, no "In summary" / "In conclusion" closers.
- **A**ctive — active voice, concrete subjects ("Qubes qrexec mediates…", not "It is believed that…").
- **S**pecific — concrete paths, module names, table/figure references; no vague hedging where a stance is taken.
- **P**recise — claim exactly what the evidence supports; label the epistemic status.

## Attribution discipline (mirrors the source's stance)

- Assessments are **analytical judgments from documented designs** — not penetration-test results. Never imply hands-on offensive validation.
- **Vendor findings are labeled as vendor findings.** The Anthropic campaign report is the investigating vendor's report; AISI results come from its own incident report. Attribute accordingly.
- **Forecast ≠ measurement.** Forecast claims carry confidence (`high | moderate | low`) and a horizon (2028–2031); measurements carry a source tier.
- **No numeric security scores.** Candidates are assessed qualitatively (`strong | partial | weak | n_a`); never "Qubes 9.4"-style numbers.
- Distinguish: reproducible deployment vs verified reproducible builds; rollback vs full-state recovery; authenticity vs provenance; anonymity vs credential protection. Do not blur these.
- Two failure paths are always distinct: **exploitation** (needs a kernel/implementation flaw) vs **authorized misuse** (needs no exploit — the agent abuses legitimate access).

## Structure conventions

- H1 per file with its pinned `{#sec:...}` label (registry in `docs/output_inventory.md` and `manuscript/AGENTS.md`).
- Tables use pandoc-crossref `{#tbl:...}` labels; figures use the `![caption](../output/figures/...){#fig:...}` pattern.
- Citations only from `manuscript/references.bib`; cross-refs only to defined labels.
- No mermaid blocks in `manuscript/`.
- Sections are substantial standalone modules (deep review, not summary); extend the source's evidence base with architecture detail, implications for agents, and cross-domain synthesis.

## What "done" looks like

A reader can trace every claim: to a bib source, a registry constant, a computed artifact, or an explicitly labeled forecast — and no sentence overstates the epistemic basis of its claim.
