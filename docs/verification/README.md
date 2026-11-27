# Verify the defensive assurance note

The note uses only the versioned [trust-domain registry](../../src/agentic_os_security/trust_domains.py) and its [native structural tests](../../tests/test_trust_domains.py). The replay writes a JSON inventory and a figure derived from the same category counts. These are checks on design records.

Create an isolated sparse worktree of the revision being checked. This keeps the published manuscript and its tracked generated release out of the local assurance build. From this repository, run the following commands with an absolute worktree path.

```bash
proof=/absolute/path/to/agentic_os_security
git worktree add --detach --no-checkout "$proof" HEAD
git -C "$proof" sparse-checkout set --no-cone --stdin <<'PATHS'
/*
!/*/
/docs/
/src/agentic_os_security/trust_domains.py
/tests/test_trust_domains.py
PATHS
git -C "$proof" checkout --detach HEAD
```

From that worktree, in a Python environment with matplotlib and pytest installed, replay the registry and run its scoped tests.

```bash
cd "$proof"
python docs/verification/replay_registry.py
PYTHONPATH="$PWD/src" PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 \
  python -m pytest -c /dev/null --noconftest tests/test_trust_domains.py
```

The replay writes `output/data/defensive_registry_check.json` and `output/figures/defensive_registry_inventory.png`. Use a clean checkout of [docxology/template at 87704fe](https://github.com/docxology/template/tree/87704feae0a4490ef7dad9c931d268e8c30273c2) with its Python, Pandoc, and LaTeX environment to build the note. From the template root, register the sparse worktree and run the render and validation stages.

```bash
ln -s "$proof" projects/working/agentic_os_security
uv run --no-sync python scripts/pipeline/stage_03_render.py --project working/agentic_os_security
uv run --no-sync python scripts/pipeline/stage_04_validate.py --project working/agentic_os_security
```

Read the combined PDF in `output/pdf/`, the combined HTML in `output/web/index.html`, and the report in `output/reports/validation_report.json` in the sparse worktree. The published review continues to use the versioned [standalone source](../../manuscript/) and [citation record](../../CITATION.cff).
