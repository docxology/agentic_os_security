# output_conventions.md — artifact conventions

`output/` is **disposable**: everything regenerates from scripts. Never hand-edit, never commit. Conventions:

## Naming

- Figures: `<label_name>.png`, lowercase snake_case, one per registry label, 300 dpi, colorblind-safe, deterministic bytes.
- Data: CSVs are snake_case with a header row and stable column order; JSON is UTF-8, sorted keys where the writer controls it.
- Reports: dated only via `build_clock.py` (honors `SOURCE_DATE_EPOCH`); never wall-clock.

## Determinism

- Identical inputs → byte-identical artifacts. Figures run under matplotlib Agg with the deterministic rcParams in `src/agentic_os_security/figures/_common.py`; no network; no wall-clock.
- `uv run python scripts/10_evaluation_analysis.py` is the single regeneration entry point; `uv run python scripts/z_generate_manuscript_variables.py` writes `output/data/manuscript_variables.json` on top of a prior analysis run (it requires the analysis outputs).

## Claims

Any number that appears in manuscript prose or a figure caption and is not a registry constant must be registered in `data/claim_ledger.yaml` with its `artifact_path`. If you change an artifact that backs a ledger claim, update the ledger.

See `output_inventory.md` for the exact inventory and regeneration commands.
