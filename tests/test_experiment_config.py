"""Experiment config loading: pinned key set and consistent lengths from the
real project config; failure behavior on a mutated config in a tmp project.
"""

from __future__ import annotations

import pytest

from agentic_os_security import experiment_config

EXPECTED_KEYS = {
    "review_date",
    "forecast_horizon",
    "property_ids",
    "matrix_stance_vocab",
    "candidate_ids",
    "candidate_categories",
    "scenario_ids",
    "trust_domain_ids",
    "control_ids",
    "figure_registry",
}

EXPECTED_LENGTHS = {
    "property_ids": 9,
    "candidate_ids": 24,
    "candidate_categories": 8,
    "scenario_ids": 8,
    "trust_domain_ids": 7,
    "control_ids": 9,
    "figure_registry": 11,
}


def test_load_experiment_config_returns_pinned_keys(project_root):
    config = experiment_config.load_experiment_config(project_root)
    assert EXPECTED_KEYS <= set(config)
    assert config["review_date"] == "2026-09-10"
    assert config["forecast_horizon"] == [2028, 2031]
    assert config["matrix_stance_vocab"] == ["strong", "partial", "weak", "n_a"]


def test_config_list_lengths_match_canonical_constants(project_root):
    config = experiment_config.load_experiment_config(project_root)
    for key, length in EXPECTED_LENGTHS.items():
        assert len(config[key]) == length, (key, len(config[key]))


def test_config_ids_are_unique_within_each_list(project_root):
    config = experiment_config.load_experiment_config(project_root)
    for key in EXPECTED_LENGTHS:
        assert len(set(config[key])) == len(config[key]), key


def test_missing_key_raises_experiment_config_error(tmp_project):
    config_path = tmp_project / "manuscript" / "config.yaml"
    text = config_path.read_text(encoding="utf-8")
    # Drop the trust_domain_ids block (lines '  trust_domain_ids:' through
    # the next non-indented-or-less-indented key).
    lines = text.splitlines(keepends=True)
    kept = []
    skipping = False
    for line in lines:
        stripped = line.rstrip("\n")
        if stripped.startswith("  trust_domain_ids:"):
            skipping = True
            continue
        if skipping and stripped.startswith("  ") and not stripped.startswith("   "):
            skipping = False
        if not skipping:
            kept.append(line)
    config_path.write_text("".join(kept), encoding="utf-8")

    with pytest.raises(experiment_config.ExperimentConfigError):
        experiment_config.load_experiment_config(tmp_project)


def test_config_consistent_with_registry_constants(project_root):
    """Config id lists must agree with the src registry module."""
    from agentic_os_security import registry

    config = experiment_config.load_experiment_config(project_root)
    assert config["property_ids"] == [p.property_id for p in registry.PROPERTIES]
    assert config["candidate_ids"] == [c.candidate_id for c in registry.CANDIDATES]
    assert config["scenario_ids"] == [s.scenario_id for s in registry.SCENARIOS]
    assert config["matrix_stance_vocab"] == ["strong", "partial", "weak", "n_a"]
