"""Shared fixtures for the agentic_os_security test suite.

Zero-mock, deterministic, network-free. The matplotlib backend is forced to
Agg *before* any module imports matplotlib.pyplot, so figure generators never
touch an interactive backend or a display.
"""

from __future__ import annotations

import os
import shutil

os.environ["MPLBACKEND"] = "Agg"

import matplotlib  # noqa: E402

matplotlib.use("Agg", force=True)

from pathlib import Path  # noqa: E402

import pytest  # noqa: E402

PROJECT_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session")
def project_root() -> Path:
    """The real project root (this standalone repo)."""
    return PROJECT_ROOT


@pytest.fixture
def make_project(tmp_path):
    """Factory: an isolated project directory with manuscript/config.yaml
    copied in and an empty output/ tree. No wall-clock, no network."""

    def _make(name: str = "project") -> Path:
        root = tmp_path / name
        (root / "manuscript").mkdir(parents=True)
        shutil.copyfile(
            PROJECT_ROOT / "manuscript" / "config.yaml",
            root / "manuscript" / "config.yaml",
        )
        (root / "output").mkdir()
        return root

    return _make


@pytest.fixture
def tmp_project(make_project) -> Path:
    """A single throwaway project root mirroring the real layout."""
    return make_project()
