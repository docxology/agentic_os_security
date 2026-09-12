"""Manuscript variable generation: every token-plan key present as a string,
key-count contract, timestamp presence, JSON round-trip, and the
require_analysis_outputs gate.
"""

from __future__ import annotations

import hashlib
import json

import pytest

from agentic_os_security import forecasts
from agentic_os_security import manuscript_variables
from agentic_os_security import registry

# Token-plan keys pinned in the brief.
CONFIG_TOKENS = [
    "CONFIG_VERSION",
    "CONFIG_REVIEW_DATE",
    "CONFIG_FORECAST_HORIZON",
    "CONFIG_NUM_CANDIDATES",
    "CONFIG_NUM_PROPERTIES",
    "CONFIG_NUM_SCENARIOS",
    "CONFIG_NUM_TRUST_DOMAINS",
    "CONFIG_NUM_CONTROLS",
    "CONFIG_NUM_INVARIANTS",
    "CONFIG_NUM_SOURCES",
    "CONFIG_KEYWORDS",
]
RESULT_TOKENS = [
    "RESULT_MATRIX_CELLS",
    "RESULT_MATRIX_COVERAGE_PCT",
    "RESULT_STANCE_STRONG_COUNT",
    "RESULT_STANCE_PARTIAL_COUNT",
    "RESULT_STANCE_WEAK_COUNT",
    "RESULT_STANCE_NA_COUNT",
    "RESULT_NUM_FIGURES",
    "RESULT_FORECAST_TOTAL",
    "RESULT_FORECAST_HIGH",
    "RESULT_FORECAST_MODERATE",
    "RESULT_FORECAST_LOW",
]
ARTIFACT_TOKENS = [
    "ARTIFACT_FIGURES",
    "ARTIFACT_DATA_FILES",
    "ARTIFACT_TOTAL",
]
ENVIRONMENT_TOKENS = [
    "GENERATION_TIMESTAMP",
    "PYTHON_VERSION",
    "NUMPY_VERSION",
    "PLATFORM",
    "CONFIG_HASH",
]

ALL_TOKENS = CONFIG_TOKENS + RESULT_TOKENS + ARTIFACT_TOKENS + ENVIRONMENT_TOKENS

EXPECTED_KEYWORDS = [
    "agentic security",
    "operating systems",
    "compartmentalization",
    "Qubes OS",
    "NixOS",
    "threat modeling",
    "cognitive security",
    "operational security",
    "agent orchestration",
    "offensive AI",
]


def test_generate_variables_returns_all_token_plan_keys_as_strings(tmp_project):
    variables = manuscript_variables.generate_variables(
        tmp_project, require_analysis_outputs=False
    )
    missing = [token for token in ALL_TOKENS if token not in variables]
    assert not missing, f"missing tokens: {missing}"
    for token in ALL_TOKENS:
        assert isinstance(variables[token], str), token
        assert variables[token] != "", token


def test_config_tokens_match_canonical_constants(tmp_project):
    variables = manuscript_variables.generate_variables(
        tmp_project, require_analysis_outputs=False
    )
    assert variables["CONFIG_VERSION"] == "0.4.0"
    assert variables["CONFIG_REVIEW_DATE"] == "2026-09-10"
    assert variables["CONFIG_FORECAST_HORIZON"] == "2028–2031"
    assert variables["CONFIG_NUM_CANDIDATES"] == "24"
    assert variables["CONFIG_NUM_PROPERTIES"] == "9"
    assert variables["CONFIG_NUM_SCENARIOS"] == "8"
    assert variables["CONFIG_NUM_TRUST_DOMAINS"] == "7"
    assert variables["CONFIG_NUM_CONTROLS"] == "9"
    assert variables["CONFIG_NUM_INVARIANTS"] == "9"
    assert variables["CONFIG_NUM_SOURCES"] == "155"
    for keyword in EXPECTED_KEYWORDS:
        assert keyword in variables["CONFIG_KEYWORDS"], keyword


def test_result_tokens_derived_from_registry_and_forecasts(tmp_project):
    variables = manuscript_variables.generate_variables(
        tmp_project, require_analysis_outputs=False
    )
    assert variables["RESULT_MATRIX_CELLS"] == "216"
    assert variables["RESULT_MATRIX_COVERAGE_PCT"] == "100.0"
    assert variables["RESULT_NUM_FIGURES"] == "10"

    stance_counts = registry.stance_counts()
    assert variables["RESULT_STANCE_STRONG_COUNT"] == str(stance_counts["strong"])
    assert variables["RESULT_STANCE_PARTIAL_COUNT"] == str(stance_counts["partial"])
    assert variables["RESULT_STANCE_WEAK_COUNT"] == str(stance_counts["weak"])
    assert variables["RESULT_STANCE_NA_COUNT"] == str(stance_counts["n_a"])

    forecast_counts = forecasts.counts_by_confidence()
    assert variables["RESULT_FORECAST_TOTAL"] == str(len(forecasts.FORECASTS))
    assert variables["RESULT_FORECAST_HIGH"] == str(forecast_counts["high"])
    assert variables["RESULT_FORECAST_MODERATE"] == str(forecast_counts["moderate"])
    assert variables["RESULT_FORECAST_LOW"] == str(forecast_counts["low"])


def test_generation_timestamp_present_and_config_hash_is_sha256(tmp_project):
    variables = manuscript_variables.generate_variables(
        tmp_project, require_analysis_outputs=False
    )
    assert variables["GENERATION_TIMESTAMP"].strip()
    assert variables["CONFIG_HASH"] == hashlib.sha256(
        (tmp_project / "manuscript" / "config.yaml").read_bytes()
    ).hexdigest()


def test_save_variables_round_trips_json(tmp_project):
    variables = manuscript_variables.generate_variables(
        tmp_project, require_analysis_outputs=False
    )
    target = tmp_project / "output" / "data" / "manuscript_variables.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    manuscript_variables.save_variables(variables, target)
    loaded = json.loads(target.read_text(encoding="utf-8"))
    assert loaded == variables


def test_require_analysis_outputs_raises_without_evaluation_matrix(tmp_project):
    with pytest.raises(Exception) as excinfo:
        manuscript_variables.generate_variables(
            tmp_project, require_analysis_outputs=True
        )
    message = str(excinfo.value).lower()
    assert "evaluation_matrix" in message or "output" in message


def test_require_analysis_outputs_satisfied_after_matrix_present(tmp_project):
    matrix = tmp_project / "output" / "data" / "evaluation_matrix.csv"
    matrix.parent.mkdir(parents=True, exist_ok=True)
    matrix.write_text(
        "candidate_id,candidate_name,property_id,stance\n", encoding="utf-8"
    )
    variables = manuscript_variables.generate_variables(
        tmp_project, require_analysis_outputs=True
    )
    assert variables["RESULT_MATRIX_CELLS"] == "216"
