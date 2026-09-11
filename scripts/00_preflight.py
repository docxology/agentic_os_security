#!/usr/bin/env python3
"""Preflight checks for the ``agentic_os_security`` project.

Verifies the Python version, required third-party imports, the ``src/``
package layout, manuscript configuration, and expected data/figure
registries.  Exits ``0`` when every check passes, ``1`` otherwise.
"""

from __future__ import annotations

import argparse
import importlib
import sys
from pathlib import Path

REQUIRED_DIRS: tuple[str, ...] = (
    "src/agentic_os_security",
    "manuscript",
    "scripts",
    "tests",
    "data",
)
REQUIRED_FILES: tuple[str, ...] = (
    "manuscript/config.yaml",
    "manuscript/references.bib",
    "src/agentic_os_security/registry.py",
    "src/agentic_os_security/evidence.py",
    "src/agentic_os_security/threat_model.py",
    "src/agentic_os_security/trust_domains.py",
    "src/agentic_os_security/forecasts.py",
    "src/agentic_os_security/manuscript_variables.py",
    "src/agentic_os_security/figures/_common.py",
    "src/agentic_os_security/analysis/pipeline.py",
)
REQUIRED_MODULES: tuple[str, ...] = ("yaml", "numpy", "matplotlib", "defusedxml")
REQUIRED_SUBMODULES: tuple[str, ...] = (
    "registry",
    "evidence",
    "threat_model",
    "trust_domains",
    "forecasts",
    "manuscript_variables",
    "figures",
    "analysis",
)


def check_python_version() -> bool:
    ok = sys.version_info >= (3, 10)
    status = "ok" if ok else f"unsupported ({sys.version.split()[0]})"
    print(f"[preflight] python {sys.version.split()[0]}: {status}")
    return ok


def check_imports() -> bool:
    ok = True
    for module_name in REQUIRED_MODULES:
        try:
            importlib.import_module(module_name)
            print(f"[preflight] import {module_name}: ok")
        except Exception as exc:  # noqa: BLE001 - report every import failure
            print(f"[preflight] import {module_name}: FAILED ({exc})")
            ok = False
    return ok


def check_layout(project_root: Path) -> bool:
    ok = True
    for rel in REQUIRED_DIRS:
        path = project_root / rel
        exists = path.is_dir()
        print(f"[preflight] dir {rel}: {'ok' if exists else 'MISSING'}")
        ok = ok and exists
    for rel in REQUIRED_FILES:
        path = project_root / rel
        exists = path.is_file()
        print(f"[preflight] file {rel}: {'ok' if exists else 'MISSING'}")
        ok = ok and exists
    return ok


def check_package(project_root: Path) -> bool:
    src_path = project_root / "src"
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    ok = True
    for submodule in REQUIRED_SUBMODULES:
        dotted = f"agentic_os_security.{submodule}"
        try:
            importlib.import_module(dotted)
            print(f"[preflight] module {dotted}: ok")
        except Exception as exc:  # noqa: BLE001
            print(f"[preflight] module {dotted}: FAILED ({exc})")
            ok = False
    return ok


def main() -> int:
    parser = argparse.ArgumentParser(description="Preflight checks for agentic_os_security.")
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
        help="Project root (default: this script's parent directory).",
    )
    args = parser.parse_args()
    project_root: Path = args.project_root.resolve()

    print(f"[preflight] project root: {project_root}")
    results = [
        check_python_version(),
        check_imports(),
        check_layout(project_root),
        check_package(project_root),
    ]
    if all(results):
        print("[preflight] all checks passed")
        return 0
    print("[preflight] checks FAILED", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
