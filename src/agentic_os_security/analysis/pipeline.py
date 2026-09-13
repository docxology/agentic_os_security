"""Evaluation analysis pipeline: data artifacts, eleven registry figures,
and the cover graphical abstract.

``run_analysis(project_root)`` is idempotent: every run rewrites the eleven
data artifacts plus the figure registry and the validation report from the
pinned registry, regenerates all eleven registry figures plus the cover
graphical abstract (which is not a registry figure).  Reports
carry timestamps from :mod:`agentic_os_security.build_clock` (which honors
``SOURCE_DATE_EPOCH``), never the wall clock.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from ..basis import CANDIDATE_BASIS
from ..build_clock import build_timestamp
from ..evidence import (
    CAPABILITY_BASELINE,
    INCIDENTS,
    LESSON_TAXONOMY,
    SOURCES,
    sources_by_tier,
)
from ..forecasts import FORECASTS, counts_by_confidence
from ..figures import (
    generate_agent_surface,
    generate_authority_ladder,
    generate_defensive_stack,
    generate_evidence_timeline,
    generate_forecast_horizon,
    generate_graphical_abstract,
    generate_incidents,
    generate_orchestration_boundaries,
    generate_os_stack,
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
from ..orchestration import CIF_CONCEPTS, MEDIATION_POINTS
from ..threat_model import AGENT_CAPABILITY_CLASSES, AUTHORITY_LADDER, CAPABILITY_LINKAGE
from ..formal import FORMAL_DEFINITIONS, FormalDefinition
from ..stack import ARCHETYPE_LABELS, STACK_LAYERS
from ..stack import stack_rows as coverage_rows
from ..trust_domains import CONFIGURATION_INVARIANTS, CONTROLS, TRUST_DOMAINS


#: The six CIF concept ids pinned by the v0.3.0 dossier (source of truth:
#: ``orchestration.CIF_CONCEPTS``); the pipeline validates coverage.
_CIF_CONCEPT_IDS: frozenset[str] = frozenset(
    {
        "delta_bounded_delegation",
        "defense_composition_algebra",
        "belief_integrity",
        "trust_boundedness",
        "goal_preservation",
        "stealth_impact_bounds",
    }
)

__all__ = ["run_analysis"]

_STANCE_VOCAB: frozenset[str] = frozenset({"strong", "partial", "weak", "n_a"})

_FAILURE_PATH_VOCAB: frozenset[str] = frozenset({"exploitation", "authorized_misuse"})

_FIGURE_GENERATORS: dict[str, Any] = {
    "incident_lessons.png": generate_incidents,
    "evidence_timeline.png": generate_evidence_timeline,
    "property_matrix.png": generate_property_matrix,
    "defensive_stack.png": generate_defensive_stack,
    "trust_domains.png": generate_trust_domains,
    "authority_ladder.png": generate_authority_ladder,
    "orchestration_boundaries.png": generate_orchestration_boundaries,
    "agent_surface.png": generate_agent_surface,
    "forecast_horizon.png": generate_forecast_horizon,
    "update_windows.png": generate_update_windows,
    "os_stack.png": generate_os_stack,
    # The cover graphical abstract: generated like a figure but NOT a
    # registry entry and NOT counted in RESULT_NUM_FIGURES (stays 11).
    "graphical_abstract.png": generate_graphical_abstract,
}

_FIGURE_REGISTRY: dict[str, dict[str, str]] = {
    # Keys are the registry short names from manuscript/config.yaml
    # ``experiment.figure_registry``; order is manuscript appearance order
    # (section numbers in comments). Captions are the manuscript image alt
    # text, with {{TOKENS}} resolved to their pinned values.
    "incidents": {
        "figure_id": "figure_001",
        "filename": "incident_lessons.png",
        "label": "fig:incidents",
        "section": "Threat Model",
        "caption": (
            "Fourteen documented incidents and advisories placed against five "
            "boundary-lesson classes; each cell links the event to the "
            "architectural lesson it demonstrates, and marker color encodes "
            "evidentiary tier."
        ),
    },
    "evidence_timeline": {
        "figure_id": "figure_002",
        "filename": "evidence_timeline.png",
        "label": "fig:evidence_timeline",
        "section": "Threat Model",
        "caption": (
            "Two lanes of primary evidence, January 2024 through August 2026: "
            "offensive capability and governance milestones above, platform "
            "incident and release milestones below; marker color encodes "
            "evidentiary tier, and each callout names the primary source."
        ),
    },
    "property_matrix": {
        "figure_id": "figure_003",
        "filename": "property_matrix.png",
        "label": "fig:property_matrix",
        "section": "Evaluation Framework",
        "caption": (
            "All 216 candidate-by-property stances, with candidates grouped "
            "into eight category bands (left strip) and per-property stance "
            "distributions (right marginals); glyphs mark strong (S), partial "
            "(P), weak (W), and not-assessed cells."
        ),
    },
    "defensive_stack": {
        "figure_id": "figure_004",
        "filename": "defensive_stack.png",
        "label": "fig:defensive_stack",
        "section": "Evaluation Framework",
        "caption": (
            "Defensive-stack coverage across eight mitigation classes: weak "
            "cells cluster on conventional desktops while compartmentalized, "
            "server, and high-assurance candidates concentrate strong stances "
            "in sandboxing, verified boot, and update operations."
        ),
    },
    "trust_domains": {
        "figure_id": "figure_005",
        "filename": "trust_domains.png",
        "label": "fig:trust_domains",
        "section": "Agentic Authority Architecture",
        "caption": (
            "Seven trust domains for AI-assisted work, arranged from hostile "
            "intake to protected assets; numbered arrows mark the control "
            "catalog entries that mediate each crossing."
        ),
    },
    "authority_ladder": {
        "figure_id": "figure_006",
        "filename": "authority_ladder.png",
        "label": "fig:authority_ladder",
        "section": "Agentic Authority Architecture",
        "caption": (
            "The six-rung authority ladder as a swimlane across human "
            "principal, orchestrator and agent, and tool broker; hatched "
            "cells mark exercise paths an agent must never hold without "
            "external authorization."
        ),
    },
    "update_windows": {
        "figure_id": "figure_007",
        "filename": "update_windows.png",
        "label": "fig:update_windows",
        "section": "Servers and Agent-Execution Infrastructure",
        "caption": (
            "Documented support windows for all twenty-four candidates; "
            "hatched bars mark rolling or lifecycle-based policies with no "
            "fixed window, and color encodes the candidate category."
        ),
    },
    "os_stack": {
        "figure_id": "figure_008",
        "filename": "os_stack.png",
        "label": "fig:os_stack",
        "section": "Servers and Agent-Execution Infrastructure",
        "caption": (
            "Eight layers of the operating-system security stack, from "
            "hardware and firmware to the agent runtime and its tool "
            "bridge; annotations name representative mechanisms per layer "
            "and the right-hand columns record how strongly each candidate "
            "class covers each layer."
        ),
    },
    "orchestration_boundaries": {
        "figure_id": "figure_009",
        "filename": "orchestration_boundaries.png",
        "label": "fig:orchestration_boundaries",
        "section": "Securing Agent Orchestration",
        "caption": (
            "A reference orchestration: one orchestrator delegating through "
            "an MCP-style tool broker to three disposable workers, with the "
            "ten mediation points numbered at each trust-boundary crossing."
        ),
    },
    "agent_surface": {
        "figure_id": "figure_010",
        "filename": "agent_surface.png",
        "label": "fig:agent_surface",
        "section": "Securing Agent Orchestration",
        "caption": (
            "Which mediation point constrains which agent capability class; "
            "filled numbered cells mark the primary control, and the right "
            "marginal counts how many distinct controls cover each capability."
        ),
    },
    "forecast_horizon": {
        "figure_id": "figure_011",
        "filename": "forecast_horizon.png",
        "label": "fig:forecast_horizon",
        "section": "Forecast",
        "caption": (
            "Fourteen forecasts placed on the 2026–2031 horizon by confidence "
            "tier; dashed guides mark the pinned 2028–2031 window, and the "
            "official-posture markers place the May 2025 NCSC 2027-horizon "
            "assessment and the May 2026 Five-Eyes adoption guidance."
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


def _write_os_stack_coverage_csv(path: Path) -> int:
    """Write the archetype x layer stance coverage (64 rows) from ``stack``."""
    layer_names = {layer.layer_id: layer.name for layer in STACK_LAYERS}
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = coverage_rows()
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["archetype_id", "archetype", "layer_id", "layer", "stance"])
        for archetype_id, layer_id, stance in rows:
            writer.writerow(
                [
                    archetype_id,
                    ARCHETYPE_LABELS[archetype_id],
                    layer_id,
                    layer_names[layer_id],
                    stance,
                ]
            )
    return len(rows)

def _write_formal_definitions(path: Path) -> dict[str, Any]:
    """Write the eight pinned formal definitions (deterministic).

    Byte-deterministic: fixed key order inside each entry, sorted top-level
    keys, fixed indent, trailing newline, no timestamps.
    """
    definitions: list[dict[str, Any]] = []
    for definition in FORMAL_DEFINITIONS:
        definitions.append(
            {
                "definition_id": definition.definition_id,
                "name": definition.name,
                "formal_latex": definition.formal_latex,
                "informal": definition.informal,
                "surface": definition.surface,
                "citation_keys": list(definition.citation_keys),
            }
        )
    payload = {
        "definitions": definitions,
        "num_definitions": len(definitions),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload

def _write_evidence_summary(path: Path) -> dict[str, Any]:
    payload = {
        "generated_at": build_timestamp(),
        "source_tier_counts": dict(sorted(sources_by_tier().items())),
        "num_sources": len(SOURCES),
        "capability_baseline": dict(sorted(CAPABILITY_BASELINE.items())),
        "lesson_taxonomy": {
            lesson_id: {
                "name": lesson_class.name,
                "description": lesson_class.description,
            }
            for lesson_id, lesson_class in LESSON_TAXONOMY.items()
        },
        "num_lesson_classes": len(LESSON_TAXONOMY),
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


def _write_incident_register(path: Path) -> int:
    """Write the incident register CSV from ``evidence.INCIDENTS``."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(
            [
                "incident_id",
                "date",
                "actor_class",
                "vector",
                "boundary_lesson",
                "lesson_class",
                "citation",
            ]
        )
        for incident in INCIDENTS:
            writer.writerow(
                [
                    incident.incident_id,
                    incident.date,
                    incident.actor_class,
                    incident.vector,
                    incident.boundary_lesson,
                    incident.lesson_class,
                    incident.citation_key,
                ]
            )
    return len(INCIDENTS)


def _write_candidate_basis(path: Path) -> int:
    """Write the candidate-basis CSV (24 rows) from ``basis.CANDIDATE_BASIS``."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["basis_id", "summary", "primary_sources"])
        for basis in CANDIDATE_BASIS:
            writer.writerow(
                [
                    basis.basis_id,
                    basis.summary,
                    ";".join(basis.primary_sources),
                ]
            )
    return len(CANDIDATE_BASIS)


def _write_capability_mediation_map(path: Path) -> int:
    """Write the capability x failure-path x mediation map (6 rows) from
    ``threat_model.CAPABILITY_LINKAGE``."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["capability_id", "failure_paths", "mediation_points", "residual_risk"])
        for link in CAPABILITY_LINKAGE:
            writer.writerow(
                [
                    link.capability_id,
                    ";".join(link.failure_paths),
                    ";".join(link.mediation_points),
                    link.residual_risk,
                ]
            )
    return len(CAPABILITY_LINKAGE)


def _write_cognitive_defenses(path: Path) -> dict[str, Any]:
    """Write the CIF concept -> project-surface mapping (deterministic).

    Byte-deterministic: sorted keys, fixed indent, trailing newline, no
    timestamps.
    """
    control_ids = {control.control_id for control in CONTROLS}
    concepts: list[dict[str, Any]] = []
    for concept in CIF_CONCEPTS:
        concepts.append(
            {
                "concept_id": concept.concept_id,
                "concept": concept.concept,
                "summary": concept.summary,
                "surface": concept.surface,
                "surface_kind": "control" if concept.surface in control_ids else "section",
                "citation_key": concept.citation_key,
            }
        )
    concepts.sort(key=lambda entry: entry["concept_id"])
    payload = {
        "concepts": concepts,
        "num_concepts": len(concepts),
        "mapped_surfaces": sorted({entry["surface"] for entry in concepts}),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload


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

    incident_ids = [incident.incident_id for incident in INCIDENTS]
    bad_lesson_classes = sorted(
        {str(incident.lesson_class) for incident in INCIDENTS} - set(LESSON_TAXONOMY)
    )
    record(
        "incident_register_rows",
        len(INCIDENTS) == 14 and len(incident_ids) == len(set(incident_ids)),
        f"{len(INCIDENTS)} incidents (expected 14, unique ids)",
    )
    record(
        "incident_lesson_vocabulary",
        not bad_lesson_classes and len(LESSON_TAXONOMY) == 5,
        f"{len(LESSON_TAXONOMY)} lesson classes, all incidents in vocabulary"
        if not bad_lesson_classes and len(LESSON_TAXONOMY) == 5
        else f"invalid classes: {bad_lesson_classes}",
    )

    basis_ids = [basis.basis_id for basis in CANDIDATE_BASIS]
    record(
        "candidate_basis_rows",
        len(CANDIDATE_BASIS) == 24 and basis_ids == [c.candidate_id for c in CANDIDATES],
        f"{len(CANDIDATE_BASIS)} candidate bases (expected 24, registry order)",
    )

    concept_ids = {concept.concept_id for concept in CIF_CONCEPTS}
    unmapped = sorted(concept.concept_id for concept in CIF_CONCEPTS if not concept.surface)
    record(
        "cognitive_defense_coverage",
        concept_ids == _CIF_CONCEPT_IDS and not unmapped,
        f"{len(CIF_CONCEPTS)}/6 CIF concepts mapped to project surfaces"
        if concept_ids == _CIF_CONCEPT_IDS and not unmapped
        else f"missing={sorted(_CIF_CONCEPT_IDS - concept_ids)} unmapped={unmapped}",
    )

    coverage = coverage_rows()
    unique_coverage = len({(archetype, layer) for archetype, layer, _ in coverage})
    bad_coverage_stances = sorted({stance for _, _, stance in coverage} - _STANCE_VOCAB)
    record(
        "os_stack_coverage_rows",
        len(coverage) == 64
        and unique_coverage == 64
        and not bad_coverage_stances,
        f"{len(coverage)} archetype x layer rows, 8 archetypes x 8 layers, unique pairs, full stance vocabulary"
        if len(coverage) == 64 and unique_coverage == 64 and not bad_coverage_stances
        else f"rows={len(coverage)} unique={unique_coverage} invalid={bad_coverage_stances}",
    )

    record(
        "formal_definitions",
        len(FORMAL_DEFINITIONS) == 8,
        f"{len(FORMAL_DEFINITIONS)} formal definitions (expected 8)",
    )

    record(
        "figure_registry_entries",
        len(_FIGURE_REGISTRY) == 11,
        f"{len(_FIGURE_REGISTRY)} registry figures (cover excluded)",
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

    # Capability x failure-path x mediation linkage (v0.6.0): 6 rows, ids
    # matching the capability catalog, vocabularies pinned, residual note.
    linkage = CAPABILITY_LINKAGE
    capability_ids = {link.capability_id for link in linkage}
    catalog_ids = {entry.split(":", 1)[0] for entry in AGENT_CAPABILITY_CLASSES}
    mediation_ids = {point.point_id for point in MEDIATION_POINTS}
    bad_failure_paths = sorted(
        {fp for link in linkage for fp in link.failure_paths} - set(_FAILURE_PATH_VOCAB)
    )
    bad_mediation_ids = sorted(
        {mp for link in linkage for mp in link.mediation_points} - mediation_ids
    )
    linkage_ok = (
        len(linkage) == 6
        and capability_ids == catalog_ids
        and not bad_failure_paths
        and not bad_mediation_ids
        and all(link.residual_risk for link in linkage)
    )
    record(
        "capability_mediation_linkage",
        linkage_ok,
        f"{len(linkage)} capability linkage rows, ids match catalog, failure-path and mediation-point vocabularies"
        if linkage_ok
        else f"rows={len(linkage)} catalog-mismatch={sorted(capability_ids ^ catalog_ids)} "
        f"bad-paths={bad_failure_paths} bad-mediation={bad_mediation_ids}",
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
    """Run the full analysis: 11 data artifacts, the 11 registry figures,
    and the cover graphical abstract.

    Returns a summary dict with artifact paths and row/figure counts.
    """
    root = Path(project_root)
    data_path = data_dir(root) / "evaluation_matrix.csv"

    matrix_rows_written = _write_matrix_csv(data_path)
    scenario_rows_written = _write_scenario_csv(data_dir(root) / "scenario_recommendations.csv")
    stack_rows_written = _write_defensive_stack_csv(data_dir(root) / "defensive_stack.csv")
    update_rows_written = _write_update_windows_csv(data_dir(root) / "update_windows.csv")
    _write_evidence_summary(data_dir(root) / "evidence_summary.json")
    incident_rows_written = _write_incident_register(data_dir(root) / "incident_register.csv")
    cognitive_defenses = _write_cognitive_defenses(data_dir(root) / "cognitive_defenses.json")
    coverage_rows_written = _write_os_stack_coverage_csv(data_dir(root) / "os_stack_coverage.csv")
    formal_defs = _write_formal_definitions(data_dir(root) / "formal_definitions.json")
    registry_entries = _write_figure_registry(figures_dir(root) / "figure_registry.json")
    basis_rows_written = _write_candidate_basis(data_dir(root) / "candidate_basis.csv")
    linkage_rows_written = _write_capability_mediation_map(
        data_dir(root) / "capability_mediation_map.csv"
    )
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
        "matrix_rows": matrix_rows_written,
        "scenario_rows": scenario_rows_written,
        "defensive_stack_rows": stack_rows_written,
        "candidate_basis_rows": basis_rows_written,
        "capability_mediation_rows": linkage_rows_written,
        "incident_register_rows": incident_rows_written,
        "cif_concepts_mapped": cognitive_defenses["num_concepts"],
        "os_stack_coverage_rows": coverage_rows_written,
        "formal_definitions": formal_defs["num_definitions"],
        "figures_generated": len(figures),
        "figures": figures,
        "figure_registry_entries": registry_entries,
        "figure_files_on_disk": [p.name for p in figure_files],
        "candidate_basis_rows": basis_rows_written,
        "data_artifacts": [
            "evaluation_matrix.csv",
            "scenario_recommendations.csv",
            "evidence_summary.json",
            "cognitive_defenses.json",
            "os_stack_coverage.csv",
            "candidate_basis.csv",
            "capability_mediation_map.csv",
            "figure_registry.json",
            "validation_report.json",
        ],
        "validation_all_green": report["all_green"],
        "generated_at": build_timestamp(),
    }
