"""Script smoke checks: 00_preflight.py runs under the project interpreter
and exits 0. Subprocess only — no mocks of the script's logic.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.slow


def test_preflight_exits_zero(project_root):
    result = subprocess.run(
        [sys.executable, str(project_root / "scripts" / "00_preflight.py")],
        cwd=project_root,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, (
        f"preflight failed (exit {result.returncode})\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )


def test_project_pythonpath_is_src_layout(project_root):
    # The preflight script imports from src/; confirm the layout it expects.
    assert (project_root / "src" / "agentic_os_security" / "__init__.py").exists()
