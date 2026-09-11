#!/usr/bin/env python3
"""Run the evaluation analysis pipeline (data artifacts + all six figures)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from agentic_os_security.analysis.pipeline import run_analysis  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the agentic_os_security evaluation analysis pipeline.",
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
        help="Project root (default: this script's parent directory).",
    )
    args = parser.parse_args()

    try:
        summary = run_analysis(args.project_root.resolve())
    except Exception as exc:  # noqa: BLE001 - report and exit non-zero
        print(f"[analysis] FAILED: {exc}", file=sys.stderr)
        return 1

    print(
        f"[analysis] matrix rows: {summary['matrix_rows']}  "
        f"scenarios: {summary['scenario_rows']}  "
        f"figures: {summary['figures_generated']}  "
        f"validation all green: {summary['validation_all_green']}"
    )
    print(json.dumps(summary["figures"], indent=2, sort_keys=True))
    print("[analysis] done")
    return 0


if __name__ == "__main__":
    sys.exit(main())
