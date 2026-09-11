# AGENTS.md — data/

`data/` holds reviewed, version-controlled claim registrations for `agentic_os_security` (private deep-review + prospectus project on agentic security & OS security).

1. **Purpose of `claim_ledger.yaml`.** Every numeric claim that appears in manuscript prose, figure captions, or reports and is not directly a registry constant must be registered here: claim_id, what it asserts, where it comes from, and which artifact backs it. The ledger is the bridge between code-generated artifacts and prose claims; tests and review use it to trace numbers.
2. **Schema.** Top-level `claims:` list; each entry:
   - `claim_id` — unique, kebab-case.
   - `kind` — `number` (the only kind currently registered).
   - `value` — the numeric value.
   - `source` — where the value comes from (file/module + location).
   - `source_tier` — one of `project_source` (a constant/behavior of this codebase), `generated_metric` (computed by the analysis pipeline), `manuscript_claim` (asserted in manuscript prose), `official_source` (traces to a `references.bib` key / `evidence.SOURCES` entry).
   - `freshness` — `active` (or `retired` with a note if superseded; never delete history).
   - `artifact_path` — the backing artifact or file (`output/figures/...`, `output/data/...`, `manuscript/...`).
3. **Rules.** Kebab-case ids, unique; `artifact_path` must exist after a successful analysis run; if a regeneration changes a value, update the entry (`freshness` note) in the same change; never register a claim without a real source line. Source constants from `evidence.py` (30 targeted entities, 122 AISI runs, 10 unsanctioned runs, 2027 capability horizon) register with `source_tier: official_source` pointing at their bib keys.
4. **No new file types here.** Datasets live as generated artifacts in `output/data/`; `data/` is for ledgers and reviewed inputs only.
