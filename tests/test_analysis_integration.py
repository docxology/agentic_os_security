"""Analysis pipeline integration: run_analysis writes the four data
artifacts plus all six figures, with row-count/tier-sum/verdict contracts,
and reruns are idempotent in validation verdicts.
"""

from __future__ import annotations

import csv
import json

from agentic_os_security import project_paths
from agentic_os_security.analysis.pipeline import run_analysis

TIER_VOCAB = {"official", "advisory", "incident_report", "research", "community"}


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
    assert (data_dir / "evidence_summary.json").exists()
    assert (data_dir / "validation_report.json").exists()

    expected_figures = {
        "evidence_timeline.png",
        "property_matrix.png",
        "trust_domains.png",
        "authority_ladder.png",
        "orchestration_boundaries.png",
        "forecast_horizon.png",
    }
    assert {p.name for p in figures_dir.glob("*.png")} == expected_figures


def test_evaluation_matrix_has_216_data_rows_plus_header(tmp_project):
    run_analysis(tmp_project)
    matrix_path = project_paths.data_dir(tmp_project) / "evaluation_matrix.csv"
    with matrix_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.reader(handle)
        header = next(reader)
        rows = list(reader)
    assert header == ["candidate_id", "candidate_name", "property_id", "stance"]
    assert len(rows) == 216
    assert len({(row[0], row[2]) for row in rows}) == 216
    assert all(row[3] in {"strong", "partial", "weak", "n_a"} for row in rows)


def test_scenario_recommendations_has_eight_rows(tmp_project):
    run_analysis(tmp_project)
    path = project_paths.data_dir(tmp_project) / "scenario_recommendations.csv"
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.reader(handle))
    assert len(rows) == 9  # header + 8 scenarios
    assert len({row[0] for row in rows[1:]}) == 8


def test_evidence_summary_tier_counts_sum_to_65(tmp_project):
    run_analysis(tmp_project)
    summary = json.loads(
        (project_paths.data_dir(tmp_project) / "evidence_summary.json").read_text(
            encoding="utf-8"
        )
    )
    tier_counts = summary.get("tier_counts") or _find_int_mapping_with_sum(summary, 65)
    assert tier_counts is not None, "no tier-count mapping summing to 65"
    assert set(tier_counts) == TIER_VOCAB
    assert sum(tier_counts.values()) == 65
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
