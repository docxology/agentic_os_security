"""Threat-model structural invariants: two failure paths with distinct ids,
authority ladder pinned to six rungs, adversary assumptions, capability
classes. Ground rule: authorized misuse needs no kernel exploit.
"""

from __future__ import annotations

import re

from agentic_os_security import orchestration, threat_model

AUTHORITY_LADDER = ("propose", "stage", "authorize", "exercise", "audit", "revoke")


def test_exactly_two_failure_paths_with_distinct_ids():
    assert len(threat_model.FAILURE_PATHS) == 2
    ids = [fp.failure_path_id for fp in threat_model.FAILURE_PATHS]
    assert len(set(ids)) == 2
    assert set(ids) == {"exploitation", "authorized_misuse"}


def test_failure_paths_carry_definition_and_boundary_implication():
    for failure_path in threat_model.FAILURE_PATHS:
        assert failure_path.name.strip(), failure_path.failure_path_id
        assert failure_path.definition.strip(), failure_path.failure_path_id
        assert failure_path.boundary_implication.strip(), failure_path.failure_path_id


def test_authorized_misuse_is_framed_as_authorization_failure():
    by_id = {fp.failure_path_id: fp for fp in threat_model.FAILURE_PATHS}
    misuse = by_id["authorized_misuse"]
    # The load-bearing claim of the source doc: this path runs through
    # authorization/policy, not through kernel compromise.
    text = (misuse.definition + " " + misuse.boundary_implication).lower()
    assert any(
        word in text for word in ("authoriz", "approval", "policy", "credential")
    ), text


def test_authority_ladder_is_pinned_six_rung_sequence():
    assert threat_model.AUTHORITY_LADDER == AUTHORITY_LADDER


def test_adversary_assumptions_are_nonempty_unique_statements():
    assumptions = threat_model.ADVERSARY_ASSUMPTIONS
    assert len(assumptions) >= 3
    assert all(a.strip() for a in assumptions)
    assert len(set(assumptions)) == len(assumptions)


def test_agent_capability_classes_cover_the_pinned_catalog():
    # Each class is written "capability_id: description"; the pinned catalog
    # uses snake_case ids covering content intake, tool/bridge use,
    # credential touch, external comms, state mutation, self-modification.
    classes = threat_model.AGENT_CAPABILITY_CLASSES
    assert len(classes) == 6
    ids = {c.split(":", 1)[0].strip() for c in classes}
    assert ids == {
        "content_intake",
        "tool_bridge_use",
        "credential_touch",
        "external_comms",
        "state_mutation",
        "self_modification",
    }


def test_no_numeric_security_scores_in_threat_model_strings():
    # Ground rule inherited from the source: qualitative stances only.
    score = re.compile(r"\b\d+\.\d+\s*(/|out of)\s*10\b", re.IGNORECASE)
    texts = [
        fp.definition + fp.boundary_implication for fp in threat_model.FAILURE_PATHS
    ] + list(threat_model.ADVERSARY_ASSUMPTIONS)
    for text in texts:
        assert not score.search(text), text


def test_capability_linkage_covers_all_six_capability_classes():
    # One linkage row per capability class, in catalog order.
    class_ids = [c.split(":", 1)[0].strip() for c in threat_model.AGENT_CAPABILITY_CLASSES]
    link_ids = [link.capability_id for link in threat_model.CAPABILITY_LINKAGE]
    assert link_ids == class_ids
    assert len(link_ids) == 6


def test_capability_linkage_failure_path_ids_are_valid():
    failure_ids = {fp.failure_path_id for fp in threat_model.FAILURE_PATHS}
    for link in threat_model.CAPABILITY_LINKAGE:
        assert link.failure_paths, link.capability_id
        assert set(link.failure_paths) <= failure_ids, link.capability_id


def test_capability_linkage_mediation_ids_exist_in_orchestration():
    mediation_ids = {mp.point_id for mp in orchestration.MEDIATION_POINTS}
    for link in threat_model.CAPABILITY_LINKAGE:
        assert link.mediation_points, link.capability_id
        assert set(link.mediation_points) <= mediation_ids, link.capability_id


def test_capability_linkage_residual_risk_is_nonempty_qualitative():
    score = re.compile(r"\b\d+\.\d+\s*(/|out of)\s*10\b", re.IGNORECASE)
    for link in threat_model.CAPABILITY_LINKAGE:
        assert link.residual_risk.strip(), link.capability_id
        assert not score.search(link.residual_risk), link.capability_id
