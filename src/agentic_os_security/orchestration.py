"""Orchestration security: mediation points and multi-agent patterns.

This module is the single source of truth for the orchestration-layer
taxonomy consumed by figures, the manuscript's orchestration section,
and the tests. A ``MediationPoint`` is one place where an agent's
authority can be narrowed by a documented mechanism — an OS sandbox
primitive, a protocol-level guarantee, a classifier gate, or a human
approval. Each point carries exactly one citation key; the paired
mechanism text is grounded in that source, not inferred.

``ORCHESTRATION_PATTERNS`` records recurring multi-agent orchestration
shapes together with where authority concentrates — the property the
review tracks because concentration determines who must be trusted when
an agent (or the orchestrator itself) misbehaves.

No I/O and no wall-clock: the module is a pure constant surface.
"""

from __future__ import annotations

from dataclasses import dataclass

__all__ = ["MediationPoint", "MEDIATION_POINTS", "ORCHESTRATION_PATTERNS"]


@dataclass(frozen=True)
class MediationPoint:
    """One documented place where agent authority is mediated."""

    point_id: str
    name: str
    boundary: str
    mechanism: str
    citation_key: str


#: The 10 pinned mediation points (ids and citation keys pinned by the
#: v0.2.0 research contract; mechanisms grounded in the cited sources).
MEDIATION_POINTS: tuple[MediationPoint, ...] = (
    MediationPoint(
        "sandbox_primitives",
        "OS sandbox primitives",
        "agent process to host filesystem and device surface",
        "Bubblewrap, seatbelt, and Landlock namespaces confine the agent's "
        "filesystem and device reach before any tool runs.",
        "anthropic_sandboxing",
    ),
    MediationPoint(
        "egress_proxy",
        "Proxy-mediated egress",
        "agent process to network destinations",
        "All network traffic routes through a proxy with allowlists, so "
        "reachable destinations are policy objects rather than process "
        "capabilities.",
        "anthropic_sandboxing",
    ),
    MediationPoint(
        "tool_annotations",
        "Tool annotations as review hints",
        "agent to tool grant surface",
        "MCP tool annotations (readOnlyHint, destructiveHint) shape review "
        "and UX but are advisory hints, never security guarantees.",
        "mcp_tools_annotations",
    ),
    MediationPoint(
        "oauth_resource_server",
        "OAuth resource-server binding",
        "agent to protected MCP resources",
        "MCP servers act as OAuth Resource Servers (RFC 9728) requiring "
        "audience-bound tokens (RFC 8707) and OAuth 2.1 with PKCE.",
        "mcp_spec_changelog",
    ),
    MediationPoint(
        "url_mode_elicitation",
        "URL-mode elicitation",
        "agent client to user credentials",
        "SEP-1036 moves user OAuth to a browser flow so the client never "
        "handles user credentials; SEP-1024 and SEP-835 add local-install "
        "security and default scopes.",
        "mcp_spec_2025_11",
    ),
    MediationPoint(
        "a2a_tls_auth",
        "Agent-to-agent transport security",
        "agent to agent",
        "A2A mandates TLS and standard HTTP authentication schemes while "
        "keeping agents opaque to one another.",
        "a2a_protocol",
    ),
    MediationPoint(
        "agent_identity_exchange",
        "Agent identity exchange",
        "agent identity to relying services",
        "Draft IETF work composes SPIFFE/WIMSE identity with OAuth 2.0 "
        "token exchange (RFC 8693) and transaction tokens; no ratified "
        "standard yet.",
        "ietf_agent_identity",
    ),
    MediationPoint(
        "classifier_escalation",
        "Classifier escalation",
        "autonomous action to user decision",
        "Auto-mode classifiers gate execution and escalate consequential "
        "actions to explicit approval — a two-stage review boundary.",
        "claude_code_auto_mode",
    ),
    MediationPoint(
        "sandbox_observability",
        "Sandbox observability",
        "sandbox internals to independent audit",
        "SecCheck event sourcing and audit trails make sandbox behavior "
        "inspectable after the fact rather than trusted in advance.",
        "gvisor_seccheck",
    ),
    MediationPoint(
        "external_approval",
        "External human approval",
        "agent-proposed action to operator authority",
        "Consequential actions require an explicit human gate as an "
        "assurance practice of the generative-AI risk profile.",
        "nist_ai_600_1",
    ),
)

#: Recurring multi-agent orchestration patterns paired with where authority
#: concentrates — the property the review tracks because concentration
#: determines who must be trusted when an agent or the orchestrator
#: misbehaves.
ORCHESTRATION_PATTERNS: tuple[tuple[str, str], ...] = (
    ("single_gateway",
     "All tool and network traffic funnels through one mediation gateway; "
     "authority concentrates at the gateway, so gateway compromise is agent-"
     "authority compromise."),
    ("policy_as_code",
     "Grants and egress rules live in versioned declarative policy; authority "
     "concentrates in the policy repository and its merge/approval path."),
    ("brokered_credentials",
     "A broker issues short-lived, audience-bound credentials instead of "
     "handing out long-lived secrets; authority concentrates in the broker's "
     "issuance policy."),
    ("hierarchical_delegation",
     "A planner agent delegates to scoped subagents; authority concentrates in "
     "the delegation contract the planner issues and can widen."),
    ("zero_trust_swarm",
     "Short-lived identities and no persistent credentials between agents "
     "(AegisSwarm model); authority stays with the per-interaction issuance "
     "boundary rather than any long-lived agent."),
    ("monitor_and_escalate",
     "Classifiers monitor execution and escalate consequential actions to a "
     "human; authority concentrates in the classifier thresholds and the "
     "escalation channel."),
    ("registry_governed_discovery",
     "Agent/tool discovery goes through a governed registry; authority "
     "concentrates in registry admission decisions and their governance."),
)