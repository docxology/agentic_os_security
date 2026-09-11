"""Trust-domain structural invariants: 7 domains with contents and
restrictions, 9 named controls, 9 configuration invariants.
"""

from __future__ import annotations

import re

from agentic_os_security import trust_domains

DOMAIN_IDS = [
    "administration",
    "personal_identity",
    "credential_service",
    "agent_execution",
    "browsing_intake",
    "release_deployment",
    "recovery",
]

CONTROL_IDS = [
    "scoped_credentials",
    "egress_boundary",
    "external_approvals",
    "operation_mediation",
    "minimal_shared_state",
    "environment_refresh",
    "tool_bridge_constrain",
    "independent_audit",
    "rehearsed_recovery",
]


def test_seven_unique_trust_domains_with_pinned_ids():
    ids = [d.domain_id for d in trust_domains.TRUST_DOMAINS]
    assert len(trust_domains.TRUST_DOMAINS) == 7
    assert len(set(ids)) == 7
    assert set(ids) == set(DOMAIN_IDS)


def test_every_domain_has_at_least_two_contents_and_two_restrictions():
    for domain in trust_domains.TRUST_DOMAINS:
        assert domain.name.strip(), domain.domain_id
        assert len(domain.contents) >= 2, domain.domain_id
        assert len(domain.restrictions) >= 2, domain.domain_id
        assert all(c.strip() for c in domain.contents), domain.domain_id
        assert all(r.strip() for r in domain.restrictions), domain.domain_id


def test_nine_unique_controls_with_pinned_ids():
    ids = [c.control_id for c in trust_domains.CONTROLS]
    assert len(trust_domains.CONTROLS) == 9
    assert len(set(ids)) == 9
    assert set(ids) == set(CONTROL_IDS)


def test_every_control_has_rule_and_rationale():
    for control in trust_domains.CONTROLS:
        assert control.rule.strip(), control.control_id
        assert control.rationale.strip(), control.control_id


def test_nine_configuration_invariants_are_nonempty_and_unique():
    invariants = trust_domains.CONFIGURATION_INVARIANTS
    assert len(invariants) == 9
    assert all(i.strip() for i in invariants)
    assert len(set(invariants)) == 9


def test_invariants_are_agent_negations():
    # Brief: "agent must never be able to" — each invariant bars a specific
    # agent action. Every invariant names an action verb.
    action = re.compile(
        r"\b(add|disable|widen|replace|alter|mount|expand|rewrite|approve)\b",
        re.IGNORECASE,
    )
    for invariant in trust_domains.CONFIGURATION_INVARIANTS:
        assert action.search(invariant), invariant


def test_control_ids_are_slug_like():
    slug = re.compile(r"^[a-z][a-z0-9_]*$")
    for control in trust_domains.CONTROLS:
        assert slug.match(control.control_id), control.control_id
