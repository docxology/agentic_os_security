"""Orchestration-layer invariants: 10 pinned mediation points, valid
citation keys, at least six orchestration patterns, and the six
author-work CIF concepts mapped onto project surfaces. Every
mediation point pairs one boundary with one grounded mechanism and one
bibliography key; every CIF concept maps to a control id or section
label with a bibliography key.
"""

from __future__ import annotations

from agentic_os_security import orchestration

PINNED_POINT_IDS = {
    "sandbox_primitives",
    "egress_proxy",
    "tool_annotations",
    "oauth_resource_server",
    "url_mode_elicitation",
    "a2a_tls_auth",
    "agent_identity_exchange",
    "classifier_escalation",
    "sandbox_observability",
    "external_approval",
}

PINNED_CITATION_KEYS = {
    "sandbox_primitives": "anthropic_sandboxing",
    "egress_proxy": "anthropic_sandboxing",
    "tool_annotations": "mcp_tools_annotations",
    "oauth_resource_server": "mcp_spec_changelog",
    "url_mode_elicitation": "mcp_spec_2025_11",
    "a2a_tls_auth": "a2a_protocol",
    "agent_identity_exchange": "ietf_agent_identity",
    "classifier_escalation": "claude_code_auto_mode",
    "sandbox_observability": "gvisor_seccheck",
    "external_approval": "nist_ai_600_1",
}


def test_ten_mediation_points_with_pinned_unique_ids():
    ids = [m.point_id for m in orchestration.MEDIATION_POINTS]
    assert len(ids) == 10
    assert len(set(ids)) == 10
    assert set(ids) == PINNED_POINT_IDS


def test_mediation_points_carry_substantive_boundary_and_mechanism():
    for point in orchestration.MEDIATION_POINTS:
        assert point.name.strip(), point.point_id
        assert point.boundary.strip(), point.point_id
        assert point.mechanism.strip(), point.point_id
        assert point.mechanism != point.boundary, point.point_id


def test_mediation_citation_keys_match_pinned_contract(project_root):
    for point in orchestration.MEDIATION_POINTS:
        assert point.citation_key == PINNED_CITATION_KEYS[point.point_id], point.point_id
    bib_text = (project_root / "manuscript" / "references.bib").read_text(
        encoding="utf-8"
    )
    for point in orchestration.MEDIATION_POINTS:
        assert f"{{{point.citation_key}," in bib_text, point.point_id


def test_orchestration_patterns_carry_at_least_six_distinct_notes():
    patterns = orchestration.ORCHESTRATION_PATTERNS
    assert len(patterns) >= 6
    names = [name for name, _ in patterns]
    assert len(set(names)) == len(names)
    for name, note in patterns:
        assert name.strip(), name
        assert note.strip(), name


PINNED_CIF_IDS = {
    "delta_bounded_delegation",
    "defense_composition_algebra",
    "belief_integrity",
    "trust_boundedness",
    "goal_preservation",
    "stealth_impact_bounds",
}

SECTION_LABELS = {
    "sec:abstract",
    "sec:introduction",
    "sec:threat_model",
    "sec:evaluation_framework",
    "sec:qubes",
    "sec:nixos",
    "sec:desktops",
    "sec:servers",
    "sec:comparators",
    "sec:agentic_authority",
    "sec:cognitive_security",
    "sec:opsec",
    "sec:orchestration",
    "sec:configuration_authorization",
    "sec:forecast",
    "sec:scenarios",
    "sec:conclusion",
    "sec:references",
}

CIF_AUTHOR_WORK_KEYS = {"cif_formal_2026", "cif_validation_2026", "cif_practitioner_2026"}


def test_six_cif_concepts_with_pinned_unique_ids():
    ids = [c.concept_id for c in orchestration.CIF_CONCEPTS]
    assert len(ids) == 6
    assert len(set(ids)) == 6
    assert set(ids) == PINNED_CIF_IDS


def test_cif_concepts_map_to_a_control_or_section_label():
    from agentic_os_security.trust_domains import CONTROLS

    control_ids = {control.control_id for control in CONTROLS}
    for concept in orchestration.CIF_CONCEPTS:
        assert concept.surface in control_ids or concept.surface in SECTION_LABELS, (
            concept.concept_id,
            concept.surface,
        )
        assert concept.summary.strip(), concept.concept_id


def test_cif_concept_citation_keys_are_author_work_bib_entries(project_root):
    bib_text = (project_root / "manuscript" / "references.bib").read_text(
        encoding="utf-8"
    )
    for concept in orchestration.CIF_CONCEPTS:
        assert concept.citation_key in CIF_AUTHOR_WORK_KEYS, concept.concept_id
        assert f"{{{concept.citation_key}," in bib_text, concept.concept_id