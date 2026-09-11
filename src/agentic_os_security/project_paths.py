"""Resolve the project root and standard output paths.

The standalone project ships as ``src/agentic_os_security`` beside a
``pyproject.toml`` at the repository root. :func:`find_project_root`
walks upward from a start directory (default: current working
directory) until it reaches the directory containing both, so helpers
and scripts work from any subdirectory of a checkout. The replaced
template-repo reference is gone: this module knows only the standalone
layout and performs no template detection.

Contract (brief ``## src/ API contract``):

- :func:`find_project_root` -> repository root path.
- :func:`output_dir` -> ``<root>/output``.
- :func:`figures_dir` -> ``<root>/output/figures``.
- :func:`data_dir` -> ``<root>/output/data``.
"""

from __future__ import annotations

from pathlib import Path

__all__ = ["PACKAGE_DIR_NAME", "find_project_root", "output_dir", "figures_dir", "data_dir"]

#: Marker directory that must sit under the root holding ``pyproject.toml``.
PACKAGE_DIR_NAME: str = "src/agentic_os_security"


def find_project_root(start: Path | None = None) -> Path:
    """Walk up from ``start`` to the repository root of this project.

    The root is the first ancestor directory (starting at ``start``,
    defaulting to the current working directory) that contains
    ``pyproject.toml`` together with the ``src/agentic_os_security``
    package directory. Raises :class:`FileNotFoundError` when no
    ancestor matches, so a caller outside a checkout fails instead of
    silently targeting the wrong tree.
    """
    candidate = Path(start).resolve() if start is not None else Path.cwd().resolve()
    if not candidate.exists():
        raise FileNotFoundError(f"start path does not exist: {candidate}")
    while True:
        if (candidate / "pyproject.toml").is_file() and (candidate / PACKAGE_DIR_NAME).is_dir():
            return candidate
        parent = candidate.parent
        if parent == candidate:
            raise FileNotFoundError(
                "no ancestor of the start directory contains pyproject.toml with "
                f"{PACKAGE_DIR_NAME}; started at {start if start is not None else Path.cwd()}"
            )
        candidate = parent


def output_dir(project_root: Path) -> Path:
    """Return ``<project_root>/output`` (figures, data, and reports live below it)."""
    return Path(project_root) / "output"


def figures_dir(project_root: Path) -> Path:
    """Return ``<project_root>/output/figures`` (rendered PNG figures)."""
    return output_dir(project_root) / "figures"


def data_dir(project_root: Path) -> Path:
    """Return ``<project_root>/output/data`` (CSV/JSON analysis artifacts)."""
    return output_dir(project_root) / "data"
