"""Orchestration-layer invariants: 10 pinned mediation points, valid
citation keys, and at least six orchestration patterns. Every
mediation point pairs one boundary with one grounded mechanism and one
bibliography key.
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