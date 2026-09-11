"""Evaluation analysis pipeline: data artifacts + all nine figures.

``run_analysis(project_root)`` is idempotent: every run rewrites the six data
artifacts and the figure registry from the pinned registry and regenerates all
nine figures.  Reports
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
    generate_agent_surface,
    generate_authority_ladder,
    generate_defensive_stack,
    generate_evidence_timeline,
    generate_forecast_horizon,
    generate_orchestration_boundaries,
    generate_property_matrix,
    generate_trust_domains,
    generate_update_windows,
)
from ..project_paths import data_dir, figures_dir
from ..registry import (
    CANDIDATES,
    PROPERTIES,
    SCENARIOS,
    UPDATE_WINDOWS,
    defensive_stack_rows,
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
    "defensive_stack.png": generate_defensive_stack,
    "trust_domains.png": generate_trust_domains,
    "authority_ladder.png": generate_authority_ladder,
    "orchestration_boundaries.png": generate_orchestration_boundaries,
    "agent_surface.png": generate_agent_surface,
    "forecast_horizon.png": generate_forecast_horizon,
    "update_windows.png": generate_update_windows,
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
            "Evidence timeline for the offensive-AI baseline, 2024–2026, in two "
            "lanes: offensive capability and governance evidence (NCSC 2024 and "
            "2025 assessments, the 2025 Anthropic campaign investigations and "
            "OWASP agentic publications, MCP registry and spec milestones, the "
            "CISA-led Five Eyes adoption guidance, and the 2026 AISI incident "
            "report) and platform incidents and releases (Qubes OS 4.3.0, Nix "
            "2.34/2.35 and its advisories, the hardened-profile removal, "
            "secureblue, OpenBSD 7.9, seL4 16.0.0, QSB advisories, and the "
            "OpenAI-Hugging Face incident report)."
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
    "defensive_stack": {
        "figure_id": "figure_003",
        "filename": "defensive_stack.png",
        "label": "fig:defensive_stack",
        "section": "Evaluation Framework",
        "caption": (
            "Defensive stack coverage: the candidate x mitigation-class matrix "
            "(24 candidates x 8 mitigation classes = 192 cells) rendered from "
            "registry.DEFENSIVE_STACK with the same colorblind-safe "
            "strong/partial/weak/n_a encoding as the property matrix, grouped "
            "into the eight candidate categories with per-class coverage "
            "marginals."
        ),
    },
    "trust_domains": {
        "figure_id": "figure_004",
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
        "figure_id": "figure_005",
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
        "figure_id": "figure_006",
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
    "agent_surface": {
        "figure_id": "figure_007",
        "filename": "agent_surface.png",
        "label": "fig:agent_surface",
        "section": "Securing Agent Orchestration",
        "caption": (
            "Agent surface: which of the ten orchestration mediation points "
            "(orchestration.MEDIATION_POINTS, numbered) governs each agent "
            "capability class. Filled, numbered cells mark a mediation point "
            "that constrains the class - sandbox primitives, proxy-mediated "
            "egress, OAuth audience binding, classifier escalation, and the "
            "external human gate each cover distinct authority surfaces."
        ),
    },
    "forecast_horizon": {
        "figure_id": "figure_008",
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
    "update_windows": {
        "figure_id": "figure_009",
        "filename": "update_windows.png",
        "label": "fig:update_windows",
        "section": "Servers and Agent-Execution Infrastructure",
        "caption": (
            "Stated update and support windows for all 24 candidates, colored by "
            "candidate category; hatched bars mark projects whose documented "
            "policy is rolling or lifecycle-based without a fixed support window "
            "(registry.UPDATE_WINDOWS carries the per-candidate policy detail)."
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


def _write_defensive_stack_csv(path: Path) -> int:
    names = {candidate.candidate_id: candidate.name for candidate in CANDIDATES}
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = defensive_stack_rows()
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["candidate_id", "candidate_name", "class_id", "stance"])
        for candidate_id, class_id, stance in rows:
            writer.writerow([candidate_id, names[candidate_id], class_id, stance])
    return len(rows)


def _write_update_windows_csv(path: Path) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["candidate_id", "policy", "months"])
        for candidate in CANDIDATES:
            window = UPDATE_WINDOWS[candidate.candidate_id]
            writer.writerow([candidate.candidate_id, window.policy, window.months if window.months is not None else ""])
    return len(UPDATE_WINDOWS)


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
        len(urls) == len(set(urls)),
        f"{len(set(urls))} unique URLs across {len(urls)} sources",
    )

    record("scenario_count", len(SCENARIOS) == 8, f"{len(SCENARIOS)} scenarios")
    record("trust_domain_count", len(TRUST_DOMAINS) == 7, f"{len(TRUST_DOMAINS)} trust domains")
    record("control_count", len(CONTROLS) == 9, f"{len(CONTROLS)} controls")
    record("invariant_count", len(CONFIGURATION_INVARIANTS) == 9, f"{len(CONFIGURATION_INVARIANTS)} invariants")
    record("authority_ladder", len(AUTHORITY_LADDER) == 6, " -> ".join(AUTHORITY_LADDER))
    stack_rows = defensive_stack_rows()
    record(
        "defensive_stack_rows",
        len(stack_rows) == 192,
        f"{len(stack_rows)} stack rows (expected 192 = 24 x 8)",
    )
    bad_stack_stances = sorted({stance for _, _, stance in stack_rows} - _STANCE_VOCAB)
    record(
        "defensive_stack_vocabulary",
        not bad_stack_stances,
        "all stack stances in strong|partial|weak|n_a" if not bad_stack_stances else f"invalid: {bad_stack_stances}",
    )
    record(
        "update_windows_count",
        len(UPDATE_WINDOWS) == 24,
        f"{len(UPDATE_WINDOWS)} update windows (expected 24)",
    )

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
    """Run the full analysis: 6 data artifacts, then all 9 figures.

    Returns a summary dict with artifact paths and row/figure counts.
    """
    root = Path(project_root)
    data_path = data_dir(root) / "evaluation_matrix.csv"

    matrix_rows_written = _write_matrix_csv(data_path)
    scenario_rows_written = _write_scenario_csv(data_dir(root) / "scenario_recommendations.csv")
    stack_rows_written = _write_defensive_stack_csv(data_dir(root) / "defensive_stack.csv")
    update_rows_written = _write_update_windows_csv(data_dir(root) / "update_windows.csv")
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
        "defensive_stack_rows": stack_rows_written,
        "update_window_rows": update_rows_written,
        "figures_generated": len(figures),
        "figures": figures,
        "figure_registry_entries": registry_entries,
        "figure_files_on_disk": [p.name for p in figure_files],
        "data_artifacts": [
            "evaluation_matrix.csv",
            "scenario_recommendations.csv",
            "defensive_stack.csv",
            "update_windows.csv",
            "evidence_summary.json",
            "figure_registry.json",
            "validation_report.json",
        ],
        "validation_all_green": report["all_green"],
        "generated_at": build_timestamp(),
    }
