"""Threat model constants: failure paths, adversary assumptions, authority ladder.

The source assessment's threat model ("two ways to lose") pins the
ground rules this module carries:

- Exactly two failure paths — **exploitation** and **authorized
  misuse** — and authorized misuse needs no kernel exploit.
- The baseline adversary can supply hostile content or code but does
  not already control firmware, hypervisor, trusted administrator, or
  signing infrastructure.
- Offensive automation makes probing, exploit adaptation,
  configuration examination, and chaining cheaper; it does not make
  all isolation boundaries equally penetrable or grant unlimited
  computation and perfect information.
- No numeric security scores; qualitative stances only.

The :data:`AUTHORITY_LADDER` and :data:`AGENT_CAPABILITY_CLASSES`
catalogs extend the source into the manuscript's analytical domains
(agentic authority architecture, orchestration security): they give
the analysis a shared vocabulary for distinguishing what an agent can
*propose* from what it can *authorize* and *exercise*.

No I/O at import time; the module is a pure constant surface.
"""

from __future__ import annotations

from dataclasses import dataclass

__all__ = [
    "FailurePath",
    "AuthorityRung",
    "FAILURE_PATHS",
    "ADVERSARY_ASSUMPTIONS",
    "AUTHORITY_LADDER",
    "AGENT_CAPABILITY_CLASSES",
    "CapabilityLink",
    "CAPABILITY_LINKAGE",
]


@dataclass(frozen=True)
class FailurePath:
    """One of the two ways to lose: its definition and boundary implication."""

    failure_path_id: str
    name: str
    definition: str
    boundary_implication: str


#: The two failure paths pinned by the source assessment.
FAILURE_PATHS: tuple[FailurePath, ...] = (
    FailurePath(
        "exploitation",
        "Exploitation",
        "An attacker compromises a browser, parser, dependency, agent tool, or service, then "
        "tries to cross a security boundary, acquire credentials, move laterally, or persist.",
        "Isolation after initial compromise is the relevant property: a prevention failure "
        "should not automatically become whole-machine compromise, so evaluate what remains "
        "protected once the exposed component is fully controlled.",
    ),
    FailurePath(
        "authorized_misuse",
        "Authorized misuse",
        "An attacker persuades an agent to use its existing access to read secrets, upload "
        "files, change infrastructure, publish code, or authorize a transaction. No kernel "
        "exploit is necessary in this scenario.",
        "Excessive legitimate authority bypasses the need for an exploit, so the boundary "
        "that matters is delegation: distinguish what the agent can propose from what it can "
        "authorize, and mediate consequential operations outside the agent.",
    ),
)

#: Baseline adversary assumptions (pinned by the source assessment).
ADVERSARY_ASSUMPTIONS: tuple[str, ...] = (
    "The attacker can supply hostile content or code that reaches exposed components: "
    "websites, downloads, email attachments, dependencies, agent-generated code, and documents.",
    "The attacker does not already control the machine's firmware, hypervisor, trusted "
    "administrator, or signing infrastructure.",
    "Offensive automation makes repeated probing, adapting known exploits, examining "
    "configurations, and chaining opportunities cheaper.",
    "Offensive automation does not make all isolation boundaries equally penetrable and does "
    "not grant the attacker unlimited computation or perfect information.",
    "Fully automated, end-to-end advanced attacks are not assumed established: the NCSC "
    "considers them unlikely through its 2027 horizon, and vendor incident reports carry "
    "attribution caveats.",
    "Defensive engineering is not frozen: DARPA's AIxCC results show automated systems "
    "discovering and patching real flaws, so exploit capability and patch speed improve "
    "together.",
    "The primary scenario is a technically capable person using a workstation for browsing, "
    "development, sensitive accounts, documents, and AI-assisted work; server and "
    "autonomous-agent execution environments are considered separately.",
)

#: The agentic authority ladder. Each rung is a distinct grant of authority
#: an agent may hold over a system; analysis and controls must state which
#: rungs an agent may occupy:
#:
#: - ``propose`` — generate a configuration, policy, command, or change for
#:   review. Reading hostile material and drafting output; no effect until a
#:   later rung.
#: - ``stage`` — prepare a change in a location that can later activate it:
#:   write build outputs, upload artifacts, enqueue updates. Staged changes
#:   remain inert but concentrated and inspectable.
#: - ``authorize`` — approve a staged or proposed change: sign, approve a
#:   policy or deployment, hold the approving identity. The control surface
#:   for configuration authorization: an agent that can both write policy
#:   and approve it defeats the ladder.
#: - ``exercise`` — execute an authorized change against a live system:
#:   deploy, restart, transfer funds, publish. The rung where consequences
#:   land.
#: - ``audit`` — reconstruct what happened from records outside the
#:   execution environment: tool use, permission grants, policy changes,
#:   deployment decisions. An audit trail an agent can rewrite is not an
#:   audit rung it may occupy.
#: - ``revoke`` — terminate authority: invalidate credentials, roll back
#:   deployments, disable grants. Recovery's terminal rung; must sit beyond
#:   the destructive authority of the daily workstation and its agent.
AUTHORITY_LADDER: tuple[str, ...] = (
    "propose",
    "stage",
    "authorize",
    "exercise",
    "audit",
    "revoke",
)



@dataclass(frozen=True)
class AuthorityRung:
    """One authority-ladder rung: its id and definition."""

    rung_id: str
    name: str
    definition: str


#: Machine-readable definition of each :data:`AUTHORITY_LADDER` rung, in
#: ladder order (the docstring surface for the pinned tuple above).
AUTHORITY_LADDER_RUNGS: tuple[AuthorityRung, ...] = (
    AuthorityRung(
        "propose",
        "Propose",
        "Generate a configuration, policy, command, or change for review. Reading hostile "
        "material and drafting output; no effect until a later rung.",
    ),
    AuthorityRung(
        "stage",
        "Stage",
        "Prepare a change in a location that can later activate it: write build outputs, "
        "upload artifacts, enqueue updates. Staged changes remain inert but concentrated and "
        "inspectable.",
    ),
    AuthorityRung(
        "authorize",
        "Authorize",
        "Approve a staged or proposed change: sign, approve a policy or deployment, hold the "
        "approving identity. The control surface for configuration authorization — an agent "
        "that can both write policy and approve it defeats the ladder.",
    ),
    AuthorityRung(
        "exercise",
        "Exercise",
        "Execute an authorized change against a live system: deploy, restart, transfer funds, "
        "publish. The rung where consequences land.",
    ),
    AuthorityRung(
        "audit",
        "Audit",
        "Reconstruct what happened from records outside the execution environment: tool use, "
        "permission grants, policy changes, deployment decisions. An audit trail an agent can "
        "rewrite is not an audit rung it may occupy.",
    ),
    AuthorityRung(
        "revoke",
        "Revoke",
        "Terminate authority: invalidate credentials, roll back deployments, disable grants. "
        "Recovery's terminal rung; must sit beyond the destructive authority of the daily "
        "workstation and its agent.",
    ),
)

#: Short catalog of the capability classes that make an agent a security
#: actor; each class marks an authority surface to mediate rather than a
#: numeric risk score.
AGENT_CAPABILITY_CLASSES: tuple[str, ...] = (
    "content_intake: accepting and parsing untrusted content (web pages, downloads, "
    "attachments, documents, repository material)",
    "tool_bridge_use: holding grants to filesystem, browser, repository, CI, cloud, and "
    "messaging integrations — an isolated process with a powerful API token is still a "
    "powerful actor",
    "credential_touch: reading, holding, or requesting credentials, keys, or signing "
    "operations",
    "external_comms: transmitting to destinations outside the execution environment, "
    "including destinations that themselves accept uploads or messages",
    "state_mutation: changing persistent system or service state, including configuration "
    "generation and database writes",
    "self_modification: altering its own grants, policy, tool access, or execution "
    "environment",
)


@dataclass(frozen=True)
class CapabilityLink:
    """One capability class linked to the failure paths that exploit it,
    the mediation points that primarily bound it, and its residual risk."""

    capability_id: str
    failure_paths: tuple[str, ...]
    mediation_points: tuple[str, ...]
    residual_risk: str


#: Capability × failure-path × mediation linkage: each capability class in
#: :data:`AGENT_CAPABILITY_CLASSES` mapped to the failure path(s) that most
#: directly exploit it, the primary mediation-point ids from
#: orchestration.MEDIATION_POINTS that bound it, and a one-line residual-risk
#: note. Literal tuples by design: no cross-module import — the pinned ids
#: match the orchestration surface without depending on it.
CAPABILITY_LINKAGE: tuple[CapabilityLink, ...] = (
    CapabilityLink(
        "content_intake",
        ("exploitation", "authorized_misuse"),
        ("sandbox_primitives", "classifier_escalation"),
        "Prompt injection through hostile content remains probabilistic: mediation "
        "reduces exposure but cannot eliminate it.",
    ),
    CapabilityLink(
        "tool_bridge_use",
        ("authorized_misuse",),
        ("tool_annotations", "oauth_resource_server", "external_approval"),
        "Tool annotations are advisory hints and tokens stay powerful, so the review "
        "quality of grants bounds this surface.",
    ),
    CapabilityLink(
        "credential_touch",
        ("authorized_misuse",),
        ("agent_identity_exchange", "external_approval"),
        "Audience-bound identity shrinks stolen-credential value, but a persuaded agent "
        "still spends real credentials within its grant.",
    ),
    CapabilityLink(
        "external_comms",
        ("exploitation", "authorized_misuse"),
        ("egress_proxy", "sandbox_observability"),
        "Egress allowlists constrain destinations, not content, so exfiltration through "
        "an allowed channel remains possible.",
    ),
    CapabilityLink(
        "state_mutation",
        ("authorized_misuse",),
        ("external_approval", "classifier_escalation"),
        "Approval gates scale poorly with volume: consequential-but-routine mutations "
        "risk gating fatigue.",
    ),
    CapabilityLink(
        "self_modification",
        ("authorized_misuse",),
        ("external_approval", "sandbox_observability"),
        "Explicit approval catches visible self-grants, but incremental environment "
        "drift between reviews can accumulate.",
    ),
)
