"""Manuscript token generation: ``{{TOKEN}}`` substitution map.

Implements the pinned token plan (``docs/syntax_guide.md``):

- ``CONFIG_*`` from the identity/constants in :mod:`agentic_os_security.registry`,
  :mod:`agentic_os_security.trust_domains`, and the config identity block;
- ``RESULT_*`` from the registry and :mod:`agentic_os_security.forecasts`;
- ``ARTIFACT_*`` from the ``output/figures`` + ``output/data`` inventory (or,
  in draft mode, from the declared figure registry);
- ``GENERATION_TIMESTAMP`` via :mod:`agentic_os_security.build_clock`
  (honors ``SOURCE_DATE_EPOCH`` — never the wall clock);
- ``PYTHON_VERSION`` / ``NUMPY_VERSION`` / ``PLATFORM`` / ``CONFIG_HASH``.

All values are strings; render requires a prior analysis run unless
``require_analysis_outputs=False`` (draft mode).
"""

from __future__ import annotations

import hashlib
import json
import platform
from pathlib import Path

import yaml

from .build_clock import build_timestamp
from .evidence import SOURCES
from .experiment_config import ExperimentConfigError, load_experiment_config
from .forecasts import counts_by_confidence
from .project_paths import data_dir, figures_dir
from .registry import CANDIDATES, PROPERTIES, SCENARIOS, matrix_rows, stance_counts
from .trust_domains import CONFIGURATION_INVARIANTS, CONTROLS, TRUST_DOMAINS

__all__ = ["ManuscriptVariablesError", "generate_variables", "save_variables"]

_EVALUATION_MATRIX = "evaluation_matrix.csv"
_NUMPY_VERSION_FALLBACK = "unavailable"


class ManuscriptVariablesError(RuntimeError):
    """Raised when required analysis outputs are missing or config is invalid."""


def _load_identity(project_root: Path) -> dict:
    config_path = project_root / "manuscript" / "config.yaml"
    if not config_path.is_file():
        raise ManuscriptVariablesError(f"missing manuscript config: {config_path}")
    with config_path.open("r", encoding="utf-8") as handle:
        try:
            return yaml.safe_load(handle) or {}
        except yaml.YAMLError as exc:
            raise ManuscriptVariablesError(f"invalid manuscript config: {exc}") from exc


def _config_keywords(identity: dict) -> str:
    keywords = identity.get("keywords")
    if isinstance(keywords, list) and keywords:
        return ", ".join(str(item) for item in keywords)
    # Fallback to the pinned identity block from the brief.
    return (
        "agentic security, operating systems, compartmentalization, Qubes OS, "
        "NixOS, threat modeling, cognitive security, operational security, "
        "agent orchestration, offensive AI, capability mediation, reproducible builds"
    )


def _config_hash(project_root: Path) -> str:
    config_path = project_root / "manuscript" / "config.yaml"
    return hashlib.sha256(config_path.read_bytes()).hexdigest()


def _declared_figure_files() -> list[str]:
    return [
        "evidence_timeline.png",
        "property_matrix.png",
        "trust_domains.png",
        "authority_ladder.png",
        "orchestration_boundaries.png",
        "forecast_horizon.png",
    ]


def _declared_data_files() -> list[str]:
    return [
        "evaluation_matrix.csv",
        "scenario_recommendations.csv",
        "evidence_summary.json",
        "validation_report.json",
    ]


def _artifact_inventory(project_root: Path) -> tuple[int, int, int]:
    """Count figures and data files on disk; fall back to declared inventories."""
    fig_dir = figures_dir(project_root)
    data_path = data_dir(project_root)
    figures = sorted(fig_dir.glob("*.png")) if fig_dir.is_dir() else []
    data_files = sorted(p for p in data_path.glob("*") if p.is_file()) if data_path.is_dir() else []
    if not figures:
        figures_count = len(_declared_figure_files())
    else:
        figures_count = len(figures)
    if not data_files:
        data_count = len(_declared_data_files())
    else:
        data_count = len(data_files)
    return figures_count, data_count, figures_count + data_count


def generate_variables(project_root: Path | str, require_analysis_outputs: bool = True) -> dict[str, str]:
    """Build the flat ``TOKEN -> value`` map for ``{{TOKEN}}`` injection.

    With ``require_analysis_outputs=True`` (the pipeline default), a missing
    ``output/data/evaluation_matrix.csv`` raises
    :class:`ManuscriptVariablesError`.  Draft mode (``False``) fills artifact
    tokens from the declared registry instead of the filesystem.
    """
    root = Path(project_root)
    matrix_path = data_dir(root) / _EVALUATION_MATRIX
    if require_analysis_outputs and not matrix_path.is_file():
        raise ManuscriptVariablesError(
            f"missing analysis output: {matrix_path} (run scripts/10_evaluation_analysis.py first, "
            "or pass --allow-draft for draft-mode rendering)"
        )

    identity = _load_identity(root)
    try:
        load_experiment_config(root)
    except ExperimentConfigError as exc:
        raise ManuscriptVariablesError(f"experiment config invalid: {exc}") from exc

    paper = identity.get("paper") or {}
    rows = matrix_rows()
    tallies = stance_counts()
    forecast_counts = counts_by_confidence()
    figures_count, data_count, total_artifacts = _artifact_inventory(root)

    variables: dict[str, str] = {
        # CONFIG_* — identity block and pinned constants.
        "CONFIG_VERSION": str(paper.get("version", "0.1.0")),
        "CONFIG_REVIEW_DATE": str(identity.get("experiment", {}).get("review_date", paper.get("date", "2026-09-10"))),
        "CONFIG_FORECAST_HORIZON": "2028–2031",
        "CONFIG_NUM_CANDIDATES": str(len(CANDIDATES)),
        "CONFIG_NUM_PROPERTIES": str(len(PROPERTIES)),
        "CONFIG_NUM_SCENARIOS": str(len(SCENARIOS)),
        "CONFIG_NUM_TRUST_DOMAINS": str(len(TRUST_DOMAINS)),
        "CONFIG_NUM_CONTROLS": str(len(CONTROLS)),
        "CONFIG_NUM_INVARIANTS": str(len(CONFIGURATION_INVARIANTS)),
        "CONFIG_NUM_SOURCES": str(len(SOURCES)),
        "CONFIG_KEYWORDS": _config_keywords(identity),
        # RESULT_* — computed from the registry and forecasts module.
        "RESULT_MATRIX_CELLS": str(len(rows)),
        "RESULT_MATRIX_COVERAGE_PCT": f"{100.0 * len(rows) / (len(CANDIDATES) * len(PROPERTIES)):.1f}",
        "RESULT_STANCE_STRONG_COUNT": str(tallies.get("strong", 0)),
        "RESULT_STANCE_PARTIAL_COUNT": str(tallies.get("partial", 0)),
        "RESULT_STANCE_WEAK_COUNT": str(tallies.get("weak", 0)),
        "RESULT_STANCE_NA_COUNT": str(tallies.get("n_a", 0)),
        "RESULT_NUM_FIGURES": str(len(_declared_figure_files())),
        "RESULT_FORECAST_TOTAL": str(sum(forecast_counts.values())),
        "RESULT_FORECAST_HIGH": str(forecast_counts.get("high", 0)),
        "RESULT_FORECAST_MODERATE": str(forecast_counts.get("moderate", 0)),
        "RESULT_FORECAST_LOW": str(forecast_counts.get("low", 0)),
        # ARTIFACT_* — filesystem inventory (declared registry in draft mode).
        "ARTIFACT_FIGURES": str(figures_count),
        "ARTIFACT_DATA_FILES": str(data_count),
        "ARTIFACT_TOTAL": str(total_artifacts),
        # Environment tokens.
        "GENERATION_TIMESTAMP": build_timestamp(),
        "PYTHON_VERSION": platform.python_version(),
        "NUMPY_VERSION": _numpy_version(),
        "PLATFORM": platform.platform(),
        "CONFIG_HASH": _config_hash(root),
    }
    return variables


def _numpy_version() -> str:
    try:
        import numpy

        return str(numpy.__version__)
    except Exception:  # pragma: no cover - numpy is a hard dependency in practice
        return _NUMPY_VERSION_FALLBACK


def save_variables(variables: dict[str, str], path: Path | str) -> Path:
    """Write *variables* as JSON (``manuscript_variables.json``) and return the path."""
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(dict(sorted(variables.items())), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return out
