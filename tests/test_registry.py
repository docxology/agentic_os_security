"""Structural invariants of the candidate x property registry.

Contract (brief): 9 properties, 24 candidates, 8 scenarios, 8 categories,
stance vocabulary {strong, partial, weak, n_a}, 24x9 = 216 matrix cells.
"""

from __future__ import annotations

import re
from collections import Counter

from agentic_os_security import registry

PROPERTY_IDS = [
    "containment",
    "authority",
    "trusted_computing_base",
    "application_confinement",
    "integrity",
    "persistence_recovery",
    "update_operations",
    "supply_chain_trust",
    "human_usability",
]

CANDIDATE_IDS = [
    "qubes_os",
    "nixos",
    "secureblue",
    "fedora_atomic",
    "fedora_workstation",
    "debian_stable",
    "ubuntu_lts",
    "kicksecure",
    "opensuse_aeon",
    "opensuse_microos",
    "alpine_linux",
    "talos_linux",
    "bottlerocket",
    "fedora_coreos",
    "rhel",
    "ubuntu_core",
    "whonix",
    "tails",
    "openbsd",
    "sel4",
    "genode_sculpt",
    "grapheneos",
    "kali_linux",
    "parrot_security",
]

SCENARIO_IDS = [
    "high_risk_workstation",
    "conventional_hardened_desktop",
    "auditable_operator",
    "autonomous_agent_hosting",
    "kubernetes_fleet",
    "enterprise_server",
    "anonymity_traces",
    "high_assurance_research",
]

CATEGORY_VOCAB = [
    "compartmentalized",
    "reproducible",
    "desktop",
    "server",
    "anonymity",
    "high_assurance",
    "mobile",
    "offensive_toolkit",
]

STANCE_VOCAB = {"strong", "partial", "weak", "n_a"}

MITIGATION_CLASS_IDS = {
    "memory_safety",
    "allocator_hardening",
    "sandboxing_primitives",
    "mac_framework",
    "verified_boot",
    "reproducible_deployment",
    "disposable_execution",
    "update_automation",
}


def test_nine_properties_with_unique_ids():
    ids = [p.property_id for p in registry.PROPERTIES]
    assert len(registry.PROPERTIES) == 9
    assert ids == PROPERTY_IDS
    for prop in registry.PROPERTIES:
        assert prop.name.strip()
        assert prop.question.strip()
        assert prop.significance.strip()


def test_24_candidates_with_pinned_unique_ids():
    ids = [c.candidate_id for c in registry.CANDIDATES]
    assert len(registry.CANDIDATES) == 24
    assert len(set(ids)) == 24
    assert set(ids) == set(CANDIDATE_IDS)


def test_every_candidate_stance_covers_all_properties_with_valid_vocab():
    for candidate in registry.CANDIDATES:
        assert set(candidate.property_stance) == set(PROPERTY_IDS), candidate.candidate_id
        for property_id, stance in candidate.property_stance.items():
            assert stance in STANCE_VOCAB, (candidate.candidate_id, property_id, stance)


def test_every_candidate_has_substantive_narrative_fields():
    for candidate in registry.CANDIDATES:
        assert candidate.name.strip(), candidate.candidate_id
        assert candidate.design_summary.strip(), candidate.candidate_id
        assert candidate.limitation.strip(), candidate.candidate_id
        assert candidate.assessment.strip(), candidate.candidate_id


def test_matrix_rows_are_exactly_216_cells_matching_registry():
    rows = registry.matrix_rows()
    assert len(rows) == 216
    expected = {
        (candidate.candidate_id, property_id, stance)
        for candidate in registry.CANDIDATES
        for property_id, stance in candidate.property_stance.items()
    }
    assert set(rows) == expected
    assert len(set(rows)) == 216


def test_stance_counts_agree_with_matrix():
    counts = registry.stance_counts()
    assert set(counts) == STANCE_VOCAB
    assert sum(counts.values()) == 216
    from_matrix = Counter(stance for _, _, stance in registry.matrix_rows())
    assert counts == dict(from_matrix)


def test_every_category_in_eight_way_vocab_has_at_least_one_candidate():
    for candidate in registry.CANDIDATES:
        assert candidate.category in CATEGORY_VOCAB, candidate.candidate_id
    for category in CATEGORY_VOCAB:
        matches = registry.candidates_by_category(category)
        assert matches, f"no candidate in category {category!r}"
        assert all(c.category == category for c in matches)
    counts = registry.category_counts()
    assert counts == dict(Counter(c.category for c in registry.CANDIDATES))


def test_eight_unique_scenarios_with_narrative_fields():
    ids = [s.scenario_id for s in registry.SCENARIOS]
    assert len(registry.SCENARIOS) == 8
    assert set(ids) == set(SCENARIO_IDS)
    assert len(set(ids)) == 8
    for scenario in registry.SCENARIOS:
        assert scenario.situation.strip(), scenario.scenario_id
        assert scenario.recommendation.strip(), scenario.scenario_id
        assert scenario.change_condition.strip(), scenario.scenario_id


def test_registry_ids_are_slug_like():
    slug = re.compile(r"^[a-z][a-z0-9_]*$")
    for prop in registry.PROPERTIES:
        assert slug.match(prop.property_id), prop.property_id
    for candidate in registry.CANDIDATES:
        assert slug.match(candidate.candidate_id), candidate.candidate_id
    for scenario in registry.SCENARIOS:
        assert slug.match(scenario.scenario_id), scenario.scenario_id


def test_eight_mitigation_classes_with_pinned_unique_ids():
    ids = [m.class_id for m in registry.MITIGATION_CLASSES]
    assert len(ids) == 8
    assert len(set(ids)) == 8
    assert set(ids) == set(MITIGATION_CLASS_IDS)
    for mitigation in registry.MITIGATION_CLASSES:
        assert mitigation.name.strip(), mitigation.class_id
        assert mitigation.description.strip(), mitigation.class_id


def test_defensive_stack_covers_24_candidates_by_8_classes_with_valid_vocab():
    candidate_ids = {c.candidate_id for c in registry.CANDIDATES}
    assert set(registry.DEFENSIVE_STACK) == candidate_ids
    for candidate_id, row in registry.DEFENSIVE_STACK.items():
        assert set(row) == set(MITIGATION_CLASS_IDS), candidate_id
        for class_id, stance in row.items():
            assert stance in STANCE_VOCAB, (candidate_id, class_id, stance)


def test_defensive_stack_rows_are_exactly_192_cells_matching_registry():
    rows = registry.defensive_stack_rows()
    assert len(rows) == 192
    assert len(set(rows)) == 192
    by_candidate = {c.candidate_id for c in registry.CANDIDATES}
    assert {candidate_id for candidate_id, _, _ in rows} == by_candidate
    assert {class_id for _, class_id, _ in rows} == set(MITIGATION_CLASS_IDS)
    for candidate_id, class_id, stance in rows:
        assert registry.DEFENSIVE_STACK[candidate_id][class_id] == stance


def test_update_windows_cover_all_candidates_with_nonempty_policy():
    candidate_ids = {c.candidate_id for c in registry.CANDIDATES}
    assert set(registry.UPDATE_WINDOWS) == candidate_ids
    for candidate_id, window in registry.UPDATE_WINDOWS.items():
        assert window.candidate_id == candidate_id, candidate_id
        assert window.policy.strip(), candidate_id
        assert window.months is None or window.months > 0, candidate_id
    # Fixed windows only where documented: months must be None elsewhere.
    documented = registry.UPDATE_WINDOWS["ubuntu_lts"].months
    assert documented == 60, documented
    assert registry.UPDATE_WINDOWS["qubes_os"].months is None
