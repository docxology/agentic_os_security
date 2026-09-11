"""Evaluation analysis pipeline: data artifacts + all six figures.

``run_analysis(project_root)`` is idempotent: every run rewrites the four data
artifacts and the figure registry from the pinned registry and regenerates all
six figures.  Reports
carry timestamps from :mod:`agentic_os_security.build_clock` (which honors
``SOURCE_DATE_EPOCH``), never the wall clock.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from ..build_clock import build_timestamp
from ..evidence import CAPABILITY_BASELINE, SOURCES, sources_by_tier
from ..forecasts import FORECASTS, counts_by_confidence
from ..figures import (
    generate_authority_ladder,
    generate_evidence_timeline,
    generate_forecast_horizon,
    generate_orchestration_boundaries,
    generate_property_matrix,
    generate_trust_domains,
)
from ..project_paths import data_dir, figures_dir
from ..registry import (
    CANDIDATES,
    PROPERTIES,
    SCENARIOS,
    matrix_rows,
    stance_counts,
)
from ..threat_model import AUTHORITY_LADDER
from ..trust_domains import CONFIGURATION_INVARIANTS, CONTROLS, TRUST_DOMAINS

__all__ = ["run_analysis"]

_STANCE_VOCAB: frozenset[str] = frozenset({"strong", "partial", "weak", "n_a"})

_FIGURE_GENERATORS: dict[str, Any] = {
    "evidence_timeline.png": generate_evidence_timeline,
    "property_matrix.png": generate_property_matrix,
    "trust_domains.png": generate_trust_domains,
    "authority_ladder.png": generate_authority_ladder,
    "orchestration_boundaries.png": generate_orchestration_boundaries,
    "forecast_horizon.png": generate_forecast_horizon,
}

_FIGURE_REGISTRY: dict[str, dict[str, str]] = {
    # Keys are the registry short names from manuscript/config.yaml
    # ``experiment.figure_registry``; order is manuscript appearance order
    # (section numbers in comments). Captions are the manuscript image alt
    # text, with {{TOKENS}} resolved to their pinned values.
    "evidence_timeline": {
        "figure_id": "figure_001",
        "filename": "evidence_timeline.png",
        "label": "fig:evidence_timeline",
        "section": "Threat Model",
        "caption": (
            "Evidence timeline for the offensive-AI baseline, 2025–2026: NCSC "
            "forecast horizon through 2027, the November 2025 Anthropic campaign "
            "investigation, the April 2026 Nix symlink advisory and July 2026 AISI "
            "incident, and the 2025 DARPA AIxCC defensive results."
        ),
    },
    "property_matrix": {
        "figure_id": "figure_002",
        "filename": "property_matrix.png",
        "label": "fig:property_matrix",
        "section": "Evaluation Framework",
        "caption": (
            "The candidate–property stance matrix across 24 candidates and 9 "
            "properties, rendered from output/data/evaluation_matrix.csv with "
            "colorblind-safe encoding of the strong/partial/weak/n_a vocabulary."
        ),
    },
    "trust_domains": {
        "figure_id": "figure_003",
        "filename": "trust_domains.png",
        "label": "fig:trust_domains",
        "section": "Agentic Authority Architecture",
        "caption": (
            "The seven trust domains of the proposed agentic authority architecture "
            "and the boundaries between them. Administration, personal identity, and "
            "the credential service hold assets whose loss is not recoverable by "
            "rebuilding; agent execution and browsing/intake meet hostile input and "
            "are deliberately disposable; release/deployment mediates what leaves; "
            "recovery sits beyond the destructive authority of everything else. The "
            "architecture's objective is real separation of authority, not maximizing "
            "the number of compartments."
        ),
    },
    "authority_ladder": {
        "figure_id": "figure_004",
        "filename": "authority_ladder.png",
        "label": "fig:authority_ladder",
        "section": "Agentic Authority Architecture",
        "caption": (
            "The authority ladder from proposal to revocation. An agent may "
            "autonomously occupy the lower rungs — proposing changes and staging "
            "artifacts — while authorize marks the rung that must lie outside the "
            "agent's own control, exercised by a human principal or deterministic "
            "policy. Audit and revoke remain principal powers that survive "
            "destruction of the execution environment: the record lives outside the "
            "environment, and revocation acts on credentials the environment no "
            "longer holds."
        ),
    },
    "orchestration_boundaries": {
        "figure_id": "figure_005",
        "filename": "orchestration_boundaries.png",
        "label": "fig:orchestration_boundaries",
        "section": "Securing Agent Orchestration",
        "caption": (
            "Orchestration boundaries: a planner decomposes a task into worker "
            "assignments; executors run one isolated task environment each; a tool "
            "broker mediates every privileged filesystem, browser, CI, cloud, and "
            "messaging operation against task-scoped policy; approval for "
            "consequential actions originates outside the orchestration hierarchy; "
            "and an append-only audit trail beyond every agent's write authority "
            "records broker decisions, credential events, and approvals."
        ),
    },
    "forecast_horizon": {
        "figure_id": "figure_006",
        "filename": "forecast_horizon.png",
        "label": "fig:forecast_horizon",
        "section": "Forecast",
        "caption": (
            "The 2028–2031 forecast horizon: the registered forecast claims grouped "
            "by confidence tier — high-confidence architectural bets, moderate "
            "execution-dependent outcomes, and low-confidence claims the analysis "
            "declines to endorse — across operating-system architecture, agent "
            "authority, and supply-chain domains. The horizon bounds this review's "
            "expectations; it is not a release schedule for any project."
        ),
    },
}


class AnalysisValidationError(RuntimeError):
    """Raised when a self-check fails; blocks artifact emission."""


def _write_matrix_csv(path: Path) -> int:
    rows = matrix_rows()
    names = {candidate.candidate_id: candidate.name for candidate in CANDIDATES}
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["candidate_id", "candidate_name", "property_id", "stance"])
        for candidate_id, property_id, stance in rows:
            writer.writerow([candidate_id, names[candidate_id], property_id, stance])
    return len(rows)


def _write_scenario_csv(path: Path) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["scenario_id", "situation", "recommendation", "change_condition"])
        for scenario in SCENARIOS:
            writer.writerow(
                [
                    scenario.scenario_id,
                    scenario.situation,
                    scenario.recommendation,
                    scenario.change_condition,
                ]
            )
    return len(SCENARIOS)


def _write_evidence_summary(path: Path) -> dict[str, Any]:
    payload = {
        "generated_at": build_timestamp(),
        "source_tier_counts": dict(sorted(sources_by_tier().items())),
        "num_sources": len(SOURCES),
        "capability_baseline": dict(sorted(CAPABILITY_BASELINE.items())),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload


def _write_figure_registry(path: Path) -> int:
    """Write the figure registry consumed by the render stage.

    Byte-deterministic: sorted keys, fixed indent, trailing newline, no
    timestamps.
    """
    entries: dict[str, dict[str, Any]] = {}
    for spec in _FIGURE_REGISTRY.values():
        entries[spec["label"]] = {
            "figure_id": spec["figure_id"],
            "filename": spec["filename"],
            "caption": spec["caption"],
            "label": spec["label"],
            "section": spec["section"],
            "width": "0.9\\textwidth",
            "placement": "h",
            "generated_by": "10_evaluation_analysis.py",
            "metadata": {
                "alt_text": spec["caption"],
                "source": "agentic_os_security evaluation pipeline",
            },
        }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(entries, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return len(entries)


def _run_checks(data_path: Path) -> dict[str, Any]:
    """Self-checks; raises :class:`AnalysisValidationError` on any red check."""
    checks: list[dict[str, Any]] = []

    def record(name: str, ok: bool, detail: str) -> None:
        checks.append({"check": name, "status": "green" if ok else "red", "detail": detail})


    rows = matrix_rows()
    expected_cells = len(CANDIDATES) * len(PROPERTIES)
    record(
        "matrix_completeness",
        len(rows) == expected_cells == 216,
        f"{len(rows)} rows (expected {expected_cells} = 24 x 9)",
    )

    unique_pairs = len({(c, p) for c, p, _ in rows})
    record(
        "matrix_uniqueness",
        unique_pairs == len(rows),
        f"{unique_pairs} unique (candidate, property) pairs",
    )

    bad_stances = sorted({stance for _, _, stance in rows} - _STANCE_VOCAB)
    record(
        "stance_vocabulary",
        not bad_stances,
        "all stances in strong|partial|weak|n_a" if not bad_stances else f"invalid: {bad_stances}",
    )

    forecast_counts = counts_by_confidence()
    record(
        "forecast_counts",
        len(FORECASTS) >= 10 and set(forecast_counts) <= {"high", "moderate", "low"},
        f"{len(FORECASTS)} forecasts: {forecast_counts}",
    )

    urls = [getattr(source, "url", "") for source in SOURCES]
    record(
        "source_url_uniqueness",
        len(urls) == len(set(urls)) == 65,
        f"{len(set(urls))} unique URLs across {len(urls)} sources",
    )

    record("scenario_count", len(SCENARIOS) == 8, f"{len(SCENARIOS)} scenarios")
    record("trust_domain_count", len(TRUST_DOMAINS) == 7, f"{len(TRUST_DOMAINS)} trust domains")
    record("control_count", len(CONTROLS) == 9, f"{len(CONTROLS)} controls")
    record("invariant_count", len(CONFIGURATION_INVARIANTS) == 9, f"{len(CONFIGURATION_INVARIANTS)} invariants")
    record("authority_ladder", len(AUTHORITY_LADDER) == 6, " -> ".join(AUTHORITY_LADDER))

    stance_tallies = stance_counts()
    all_green = all(check["status"] == "green" for check in checks)
    if not all_green:
        red = [check["check"] for check in checks if check["status"] == "red"]
        raise AnalysisValidationError(f"validation failed: {', '.join(red)}")

    return {
        "generated_at": build_timestamp(),
        "all_green": True,
        "checks": checks,
        "stance_counts": stance_tallies,
        "matrix_cells": len(rows),
        "evaluation_matrix": data_path.name,
    }


def run_analysis(project_root: Path | str) -> dict[str, Any]:
    """Run the full analysis: 4 data artifacts, then all 6 figures.

    Returns a summary dict with artifact paths and row/figure counts.
    """
    root = Path(project_root)
    data_path = data_dir(root) / "evaluation_matrix.csv"

    matrix_rows_written = _write_matrix_csv(data_path)
    scenario_rows_written = _write_scenario_csv(data_dir(root) / "scenario_recommendations.csv")
    _write_evidence_summary(data_dir(root) / "evidence_summary.json")
    registry_entries = _write_figure_registry(figures_dir(root) / "figure_registry.json")

    report = _run_checks(data_path)
    report_path = data_dir(root) / "validation_report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    figures: dict[str, str] = {}
    for filename, generator in _FIGURE_GENERATORS.items():
        written = generator(root)
        figures[filename] = str(Path(written).relative_to(root)) if Path(written).is_relative_to(root) else str(written)

    figure_dir = figures_dir(root)
    figure_files = sorted(figure_dir.glob("*.png"))

    return {
        "project_root": str(root),
        "matrix_rows": matrix_rows_written,
        "scenario_rows": scenario_rows_written,
        "figures_generated": len(figures),
        "figures": figures,
        "figure_registry_entries": registry_entries,
        "figure_files_on_disk": [p.name for p in figure_files],
        "data_artifacts": [
            "evaluation_matrix.csv",
            "scenario_recommendations.csv",
            "evidence_summary.json",
            "figure_registry.json",
            "validation_report.json",
        ],
        "validation_all_green": report["all_green"],
        "generated_at": build_timestamp(),
    }
