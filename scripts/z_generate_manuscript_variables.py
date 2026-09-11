#!/usr/bin/env python3
"""Generate manuscript variables and (optionally) inject the manuscript tree.

Writes ``output/data/manuscript_variables.json`` from
:func:`agentic_os_security.manuscript_variables.generate_variables`.  When the
project lives inside a template repo (detected by walking up parent
directories for a directory containing both ``infrastructure/`` and
``pyproject.toml``), also calls
``infrastructure.rendering.manuscript_injection.write_resolved_manuscript_tree``
to produce resolved copies under ``output/manuscript/``.  In standalone mode,
injection is skipped and only the JSON path is printed.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from agentic_os_security.manuscript_variables import (  # noqa: E402
    ManuscriptVariablesError,
    generate_variables,
    save_variables,
)


def _template_repo_root(start: Path) -> Path | None:
    """Walk up from *start* looking for the template repo (infrastructure/ + pyproject.toml)."""
    for candidate in (start, *start.parents):
        if (candidate / "infrastructure").is_dir() and (candidate / "pyproject.toml").is_file():
            return candidate
    return None


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate manuscript variables JSON; inject manuscript tree when template repo present.",
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
        help="Project root (default: this script's parent directory).",
    )
    parser.add_argument(
        "--allow-draft",
        action="store_true",
        help="Draft mode: do not require prior analysis outputs (artifact tokens come from the declared registry).",
    )
    args = parser.parse_args()
    project_root: Path = args.project_root.resolve()

    try:
        variables = generate_variables(project_root, require_analysis_outputs=not args.allow_draft)
    except ManuscriptVariablesError as exc:
        print(f"[variables] FAILED: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # noqa: BLE001 - report and exit non-zero
        print(f"[variables] FAILED: {exc}", file=sys.stderr)
        return 1

    out_path = project_root / "output" / "data" / "manuscript_variables.json"
    written = save_variables(variables, out_path)
    print(f"[variables] wrote {written}")

    template_root = _template_repo_root(project_root)
    if template_root is not None:
        try:
            from infrastructure.rendering.manuscript_injection import write_resolved_manuscript_tree
        except ImportError:
            print(
                f"[variables] template repo detected at {template_root} but infrastructure "
                "unavailable on sys.path; skipping injection",
                file=sys.stderr,
            )
            return 0
        resolved = write_resolved_manuscript_tree(project_root, variables)
        print(f"[variables] injected manuscript tree at {resolved}")
    else:
        print("[variables] standalone mode: injection skipped (no template repo detected)")
    print(f"[variables] {written}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
