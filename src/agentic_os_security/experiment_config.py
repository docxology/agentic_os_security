"""Load and validate the ``experiment:`` block of ``manuscript/config.yaml``.

The experiment block is the configuration contract every analysis and
validation step agrees on: 9 properties, 24 candidates, 8 candidate
categories, 8 scenarios, 7 trust domains, 9 controls, the 4-value
stance vocabulary, and the 9-entry figure registry. This module reads
that block, checks every pinned key for presence, type, shape, and
uniqueness, and raises :class:`ExperimentConfigError` on any missing
or invalid entry. No I/O happens at import time.

Contract (brief ``## src/ API contract``):

- :func:`load_experiment_config` -> the validated ``experiment:`` dict.
- :class:`ExperimentConfigError` -> raised on missing/invalid entries.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

__all__ = ["ExperimentConfigError", "CONFIG_REL_PATH", "REQUIRED_KEY_SHAPES", "load_experiment_config"]

#: Location of the configuration file relative to the project root.
CONFIG_REL_PATH: Path = Path("manuscript") / "config.yaml"

#: Pinned shapes: key -> (validator name, exact length or None).
#: Validators: ``str`` non-empty string; ``str_list`` list of non-empty
#: unique strings; ``int_list`` list of ints; ``fig_list`` list of
#: ``fig:<id> -> <name>.png`` strings.
REQUIRED_KEY_SHAPES: dict[str, tuple[str, int | None]] = {
    "review_date": ("str", None),
    "forecast_horizon": ("int_list", 2),
    "property_ids": ("str_list", 9),
    "matrix_stance_vocab": ("str_list", 4),
    "candidate_ids": ("str_list", 24),
    "candidate_categories": ("str_list", 8),
    "scenario_ids": ("str_list", 8),
    "trust_domain_ids": ("str_list", 7),
    "control_ids": ("str_list", 9),
    "figure_registry": ("fig_list", 11),
}

#: Shape of each ``figure_registry`` entry, e.g. ``fig:property_matrix -> property_matrix.png``.
_FIG_ENTRY_RE = re.compile(r"^fig:[a-z0-9_]+ -> [a-z0-9_]+\.png$")


class ExperimentConfigError(ValueError):
    """Raised when the ``experiment:`` block is missing, incomplete, or invalid."""


def _fail(key: str, message: str) -> ExperimentConfigError:
    """Build a config error naming the offending key."""
    return ExperimentConfigError(f"experiment.{key}: {message}")


def _validate_entry(key: str, value: Any, shape: tuple[str, int | None]) -> None:
    """Validate one experiment entry against its pinned shape."""
    validator, length = shape
    if validator == "str":
        if not isinstance(value, str) or not value.strip():
            raise _fail(key, f"expected a non-empty string; got {value!r}")
        return
    if not isinstance(value, list):
        raise _fail(key, f"expected a list; got {type(value).__name__}")
    if length is not None and len(value) != length:
        raise _fail(key, f"expected exactly {length} entries; got {len(value)}")
    if validator == "fig_list":
        for index, entry in enumerate(value):
            if not isinstance(entry, str) or _FIG_ENTRY_RE.match(entry) is None:
                raise _fail(key, f"entry {index} must match 'fig:<id> -> <name>.png'; got {entry!r}")
        return
    for index, entry in enumerate(value):
        if validator == "int_list" and not isinstance(entry, int) or isinstance(entry, bool):
            raise _fail(key, f"entry {index} must be an int; got {entry!r}")
        if validator == "str_list" and (not isinstance(entry, str) or not entry.strip()):
            raise _fail(key, f"entry {index} must be a non-empty string; got {entry!r}")
    if validator == "int_list":
        first, second = value  # length 2 enforced above
        if not first < second:
            raise _fail(key, f"horizon must be ascending years; got {value}")
    if len(set(value)) != len(value):
        raise _fail(key, "entries must be unique")


def load_experiment_config(project_root: Path) -> dict:
    """Read and validate the ``experiment:`` block for ``project_root``.

    Reads ``<project_root>/manuscript/config.yaml``, returns the
    ``experiment:`` mapping, and enforces every pinned key, type, and
    length from :data:`REQUIRED_KEY_SHAPES`. Raises
    :class:`ExperimentConfigError` naming the first violation when the
    file, block, or any required key is missing or invalid.
    """
    config_path = Path(project_root) / CONFIG_REL_PATH
    if not config_path.is_file():
        raise ExperimentConfigError(f"experiment config file not found: {config_path}")
    loaded = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise ExperimentConfigError(f"{config_path} must contain a top-level mapping")
    experiment = loaded.get("experiment")
    if not isinstance(experiment, dict):
        raise ExperimentConfigError(f"{config_path} has no 'experiment' mapping")
    for key, shape in REQUIRED_KEY_SHAPES.items():
        if key not in experiment:
            raise ExperimentConfigError(f"experiment config missing required key {key!r}")
        _validate_entry(key, experiment[key], shape)
    return experiment
