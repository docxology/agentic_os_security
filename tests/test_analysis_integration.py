"""Analysis pipeline integration: run_analysis writes the ten data
artifacts, the ten registry figures plus the cover graphical abstract,
with row-count/tier-sum/verdict contracts and pinned caption assertions,
and reruns are idempotent in validation verdicts.
"""

from __future__ import annotations

import csv
import json

from agentic_os_security import project_paths
from agentic_os_security.analysis.pipeline import run_analysis

TIER_VOCAB = {"official", "advisory", "incident_report", "research", "community"}

EXPECTED_FIGURES = {
    "evidence_timeline.png",
    "property_matrix.png",
    "defensive_stack.png",
    "trust_domains.png",
    "authority_ladder.png",
    "orchestration_boundaries.png",
    "agent_surface.png",
    "forecast_horizon.png",
    "update_windows.png",
    "os_stack.png",
    # Cover graphical abstract: on disk with the figures, but NOT a
    # manuscript figure registry entry (RESULT_NUM_FIGURES stays 10).
    "graphical_abstract.png",
}

# Registry short names whose caption/alt_text must equal the v0.4.0 pinned
# strings verbatim (spot-check subset; all ten carry pinned captions).
PINNED_CAPTION_SPOT_CHECKS = {
    "fig:evidence_timeline": (
        "Two lanes of primary evidence, January 2024 through August 2026: "
        "offensive capability and governance milestones above, platform "
        "incident and release milestones below; marker color encodes "
        "evidentiary tier, and each callout names the primary source."
    ),
    "fig:update_windows": (
        "Documented support windows for all twenty-four candidates; hatched "
        "bars mark rolling or lifecycle-based policies with no fixed window, "
        "and color encodes the candidate category."
    ),
    "fig:agent_surface": (
        "Which mediation point constrains which agent capability class; "
        "filled numbered cells mark the primary control, and the right "
        "marginal counts how many distinct controls cover each capability."
    ),
    "fig:os_stack": (
        "Eight layers of the operating-system security stack, from "
        "hardware and firmware to the agent runtime and its tool "
        "bridge; annotations name representative mechanisms per layer "
        "and the right-hand columns record how strongly each candidate "
        "class covers each layer."
    ),
}


def _find_int_mapping_with_sum(obj, total):
    """Locate a dict of ints summing to `total`, whatever key names the
    implementation chose (the brief pins content, not JSON schema)."""
    if isinstance(obj, dict):
        if obj and all(isinstance(v, int) for v in obj.values()):
            if sum(obj.values()) == total:
                return obj
        for value in obj.values():
            found = _find_int_mapping_with_sum(value, total)
            if found is not None:
                return found
    elif isinstance(obj, list):
        for value in obj:
            found = _find_int_mapping_with_sum(value, total)
            if found is not None:
                return found
    return None


def test_run_analysis_writes_data_artifacts_and_figures(tmp_project):
    summary = run_analysis(tmp_project)
    assert isinstance(summary, dict)
    data_dir = project_paths.data_dir(tmp_project)
    figures_dir = project_paths.figures_dir(tmp_project)

    assert (data_dir / "evaluation_matrix.csv").exists()
    assert (data_dir / "scenario_recommendations.csv").exists()
    assert (data_dir / "defensive_stack.csv").exists()
    assert (data_dir / "update_windows.csv").exists()
    assert (data_dir / "evidence_summary.json").exists()
    assert (data_dir / "validation_report.json").exists()
    assert (data_dir / "incident_register.csv").exists()
    assert (data_dir / "cognitive_defenses.json").exists()
    assert (project_paths.figures_dir(tmp_project) / "figure_registry.json").exists()

    produced = {p.name for p in figures_dir.glob("*.png")}
    assert produced == EXPECTED_FIGURES
    assert summary["figures_generated"] == 11
    assert summary["figure_registry_entries"] == 10

    registry = json.loads(
        (project_paths.figures_dir(tmp_project) / "figure_registry.json").read_text(
            encoding="utf-8"
        )
    )
    assert len(registry) == 10
    assert "graphical_abstract.png" not in {entry["filename"] for entry in registry.values()}
    assert all("section" in entry and "filename" in entry for entry in registry.values())


def test_registry_captions_match_pinned_strings(tmp_project):
    run_analysis(tmp_project)
    registry = json.loads(
        (project_paths.figures_dir(tmp_project) / "figure_registry.json").read_text(
            encoding="utf-8"
        )
    )
    for label, pinned in PINNED_CAPTION_SPOT_CHECKS.items():
        entry = registry[label]
        assert entry["caption"] == pinned, f"caption for {label} drifts from the pinned string"
        assert entry["metadata"]["alt_text"] == pinned, f"alt_text for {label} drifts from the pinned string"


def test_incident_register_has_at_least_twelve_rows_plus_header(tmp_project):
    run_analysis(tmp_project)
    with (project_paths.data_dir(tmp_project) / "incident_register.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        rows = list(csv.reader(handle))
    assert rows[0] == ["incident_id", "date", "actor_class", "vector", "boundary_lesson", "citation"]
    assert len(rows) - 1 >= 12
    assert len({row[0] for row in rows[1:]}) == len(rows) - 1, "incident ids not unique"
    assert all(row[5] for row in rows[1:]), "every incident carries a citation key"


def test_cognitive_defenses_maps_all_six_cif_concepts(tmp_project):
    run_analysis(tmp_project)
    payload = json.loads(
        (project_paths.data_dir(tmp_project) / "cognitive_defenses.json").read_text(
            encoding="utf-8"
        )
    )
    concepts = {c["concept_id"]: c for c in payload["concepts"]}
    assert set(concepts) == {
        "delta_bounded_delegation",
        "defense_composition_algebra",
        "belief_integrity",
        "trust_boundedness",
        "goal_preservation",
        "stealth_impact_bounds",
    }
    assert all(c["surface"] for c in concepts.values()), "every concept maps to a project surface"
    assert all(c["surface_kind"] in {"control", "section"} for c in concepts.values())
    assert all(c["citation_key"] for c in concepts.values())


def test_validation_report_covers_new_v030_checks(tmp_project):
    run_analysis(tmp_project)
    report = json.loads(
        (project_paths.data_dir(tmp_project) / "validation_report.json").read_text(
            encoding="utf-8"
        )
    )
    checks = {entry["check"]: entry for entry in report["checks"]}
    assert checks["incident_register_rows"]["status"] == "green"
    assert checks["os_stack_coverage_rows"]["status"] == "green"
    assert checks["formal_definitions"]["status"] == "green"
    assert checks["figure_registry_entries"]["status"] == "green"
    cognitive = checks["cognitive_defense_coverage"]
    assert cognitive["status"] == "green"
    assert "6/6" in cognitive["detail"]


def test_evaluation_matrix_has_216_data_rows_plus_header(tmp_project):
    run_analysis(tmp_project)
    path = project_paths.data_dir(tmp_project) / "evaluation_matrix.csv"
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.reader(handle))
    assert len(rows) == 217
    assert rows[0] == ["candidate_id", "candidate_name", "property_id", "stance"]
    assert all(row[3] in {"strong", "partial", "weak", "n_a"} for row in rows[1:])


def test_defensive_stack_has_192_data_rows_plus_header(tmp_project):
    run_analysis(tmp_project)
    path = project_paths.data_dir(tmp_project) / "defensive_stack.csv"
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.reader(handle))
    assert len(rows) == 193
    assert rows[0] == ["candidate_id", "candidate_name", "class_id", "stance"]
    assert all(row[3] in {"strong", "partial", "weak", "n_a"} for row in rows[1:])
    assert len({(row[0], row[2]) for row in rows[1:]}) == 192


def test_os_stack_coverage_has_64_data_rows_plus_header(tmp_project):
    run_analysis(tmp_project)
    path = project_paths.data_dir(tmp_project) / "os_stack_coverage.csv"
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.reader(handle))
    assert len(rows) == 65
    assert rows[0] == ["archetype_id", "archetype", "layer_id", "layer", "stance"]
    assert all(row[4] in {"strong", "partial", "weak", "n_a"} for row in rows[1:])
    assert len({(row[0], row[2]) for row in rows[1:]}) == 64
    # Full-word archetype labels, never codes.
    assert {row[1] for row in rows[1:]} == {
        "Compartmentalized",
        "Reproducible",
        "Desktop",
        "Server",
        "Anonymity",
        "High assurance",
        "Mobile",
        "Offensive toolkit",
    }
    assert {row[3] for row in rows[1:]} == {
        "Hardware and firmware",
        "Hypervisor",
        "Kernel and LSM",
        "Sandbox runtime",
        "Container and microVM runtime",
        "Update and provisioning",
        "Application framework",
        "Agent runtime and tool bridge",
    }


def test_formal_definitions_json_has_eight_definitions(tmp_project):
    run_analysis(tmp_project)
    payload = json.loads(
        (project_paths.data_dir(tmp_project) / "formal_definitions.json").read_text(
            encoding="utf-8"
        )
    )
    definitions = payload["definitions"]
    assert payload["num_definitions"] == len(definitions) == 8
    assert [d["definition_id"] for d in definitions] == [
        "stance_mapping",
        "stance_order",
        "authority_ladder_order",
        "delegation_bound",
        "defense_composition",
        "invariant_predicate",
        "stack_layering",
        "update_window_semantics",
    ]
    for definition in definitions:
        assert definition["formal_latex"]
        assert definition["informal"]
        assert definition["surface"]
        assert all(definition["citation_keys"])


def test_figure_ids_match_manuscript_appearance_order(tmp_project):
    run_analysis(tmp_project)
    registry = json.loads(
        (project_paths.figures_dir(tmp_project) / "figure_registry.json").read_text(
            encoding="utf-8"
        )
    )
    assert {
        label: entry["figure_id"]
        for label, entry in registry.items()
    } == {
        "fig:evidence_timeline": "figure_001",
        "fig:property_matrix": "figure_002",
        "fig:defensive_stack": "figure_003",
        "fig:trust_domains": "figure_004",
        "fig:authority_ladder": "figure_005",
        "fig:update_windows": "figure_006",
        "fig:os_stack": "figure_007",
        "fig:orchestration_boundaries": "figure_008",
        "fig:agent_surface": "figure_009",
        "fig:forecast_horizon": "figure_010",
    }
    os_stack = registry["fig:os_stack"]
    assert os_stack["section"] == "Servers and Agent-Execution Infrastructure"


def test_update_windows_has_24_data_rows_plus_header(tmp_project):
    run_analysis(tmp_project)
    path = project_paths.data_dir(tmp_project) / "update_windows.csv"
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.reader(handle))
    assert len(rows) == 25
    assert rows[0] == ["candidate_id", "policy", "months"]
    assert len({row[0] for row in rows[1:]}) == 24
    # months is blank (no fixed window) or a positive integer
    for row in rows[1:]:
        if row[2]:
            assert int(row[2]) > 0


def test_scenario_recommendations_has_eight_rows(tmp_project):
    run_analysis(tmp_project)
    path = project_paths.data_dir(tmp_project) / "scenario_recommendations.csv"
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.reader(handle))
    assert len(rows) == 9
    assert len({row[0] for row in rows[1:]}) == 8


def test_evidence_summary_tier_counts_sum_to_155(tmp_project):
    run_analysis(tmp_project)
    summary = json.loads(
        (project_paths.data_dir(tmp_project) / "evidence_summary.json").read_text(
            encoding="utf-8"
        )
    )
    tier_counts = summary.get("tier_counts") or _find_int_mapping_with_sum(summary, 155)
    assert tier_counts is not None, "no tier-count mapping summing to 155"
    assert set(tier_counts) == TIER_VOCAB
    assert sum(tier_counts.values()) == 155
    assert "capability_baseline" in summary or any(
        "baseline" in key for key in summary
    )


def test_validation_report_all_checks_green(tmp_project):
    run_analysis(tmp_project)
    report = json.loads(
        (project_paths.data_dir(tmp_project) / "validation_report.json").read_text(
            encoding="utf-8"
        )
    )
    checks = report["checks"] if "checks" in report else report
    if isinstance(checks, dict):
        for name, value in checks.items():
            if isinstance(value, bool):
                assert value is True, f"check not green: {name}"
    elif isinstance(checks, list):
        for entry in checks:
            if isinstance(entry, dict) and "passed" in entry:
                assert entry["passed"] is True, entry
    else:
        raise AssertionError(f"unrecognized validation report shape: {type(checks)}")


def test_rerun_is_idempotent_in_validation_verdicts(tmp_project):
    run_analysis(tmp_project)
    first = json.loads(
        (project_paths.data_dir(tmp_project) / "validation_report.json").read_text(
            encoding="utf-8"
        )
    )
    matrix_first = (
        project_paths.data_dir(tmp_project) / "evaluation_matrix.csv"
    ).read_bytes()
    run_analysis(tmp_project)
    second = json.loads(
        (project_paths.data_dir(tmp_project) / "validation_report.json").read_text(
            encoding="utf-8"
        )
    )
    matrix_second = (
        project_paths.data_dir(tmp_project) / "evaluation_matrix.csv"
    ).read_bytes()
    assert first == second, "validation verdicts differ between runs"
    assert matrix_first == matrix_second, "evaluation matrix not deterministic"