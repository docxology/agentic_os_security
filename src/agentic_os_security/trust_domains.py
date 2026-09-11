"""Trust-domain architecture: 7 domains, 9 controls, 9 configuration invariants.

The source assessment's "practical architecture for AI-assisted work"
pins the governing rule: a component exposed to untrusted input should
not simultaneously hold broad authority over valuable assets. This
module carries its three constant surfaces:

- :data:`TRUST_DOMAINS` — the 7 domains separating intent, execution,
  credentials, and deployment, each with its intended contents and the
  restrictions to preserve.
- :data:`CONTROLS` — the 9 controls that matter regardless of the host
  distribution.
- :data:`CONFIGURATION_INVARIANTS` — the 9 invariants an agent must
  never be able to violate, extending the source's listed invariants
  (add unrestricted credential provider; disable isolation; widen own
  network policy; replace trusted update signer; alter approving
  identity; mount unrelated user data) with the manuscript's
  orchestration-domain additions (expand own tool grants; rewrite
  audit trail; approve own policy changes).

No I/O at import time; the module is a pure constant surface.
"""

from __future__ import annotations

from dataclasses import dataclass

__all__ = [
    "TrustDomain",
    "Control",
    "TRUST_DOMAINS",
    "CONTROLS",
    "CONFIGURATION_INVARIANTS",
]


@dataclass(frozen=True)
class TrustDomain:
    """One trust domain: intended contents and the restrictions to preserve."""

    domain_id: str
    name: str
    contents: tuple[str, ...]
    restrictions: tuple[str, ...]


@dataclass(frozen=True)
class Control:
    """One distribution-independent control: its rule and rationale."""

    control_id: str
    name: str
    rule: str
    rationale: str


#: The 7 trust domains (ids pinned; contents/restrictions mirror the source's
#: trust-domain table).
TRUST_DOMAINS: tuple[TrustDomain, ...] = (
    TrustDomain(
        "administration",
        "Administration",
        ("OS management", "policy changes", "trusted update operations"),
        (
            "No routine browsing",
            "no repository builds",
            "no document parsing",
            "no agent-generated commands without independent review",
        ),
    ),
    TrustDomain(
        "personal_identity",
        "Personal identity",
        ("Sensitive browser sessions", "personal accounts"),
        (
            "Do not colocate with untrusted development dependencies",
            "do not colocate with a general-purpose autonomous agent",
        ),
    ),
    TrustDomain(
        "credential_service",
        "Credential/signing service",
        (
            "Non-exportable keys where feasible",
            "narrowly scoped signing or credential issuance",
        ),
        (
            "Expose specific operations rather than raw secrets or an unrestricted shell",
            "require approval outside the agent for consequential operations",
        ),
    ),
    TrustDomain(
        "agent_execution",
        "Agent execution",
        (
            "One task or repository",
            "temporary working files",
            "tightly scoped tools",
        ),
        (
            "Disposable VM or comparable isolation",
            "no host home",
            "no broad credential directory",
            "no privileged container socket",
            "no ambient production session",
        ),
    ),
    TrustDomain(
        "browsing_intake",
        "Browsing and intake",
        ("Untrusted websites", "downloads", "email attachments"),
        (
            "Keep separate from administration and signing",
            "explicitly review what crosses into trusted work",
        ),
    ),
    TrustDomain(
        "release_deployment",
        "Release/deployment",
        ("Reviewed build outputs", "narrowly authorized deployment actions"),
        (
            "The agent may propose a change",
            "the agent must not be able to alter the approval policy and approve its own "
            "release",
        ),
    ),
    TrustDomain(
        "recovery",
        "Recovery",
        ("Known-good configuration", "independent backups", "recovery credentials"),
        (
            "Keep beyond the destructive authority of the daily workstation and its agent",
            "Restored only from known-good verified media, independent of "
            "workstation-held credentials",
        ),
    ),
)

#: The 9 controls that matter regardless of the host distribution (ids pinned;
#: rules/rationales mirror the source's controls list).
CONTROLS: tuple[Control, ...] = (
    Control(
        "scoped_credentials",
        "Scope credentials to a task",
        "Prefer short-lived, repository- or service-specific credentials; do not hand the "
        "agent an owner's general cloud identity merely because a task sometimes needs a "
        "deployment.",
        "Excessively broad legitimate access is dangerous independently of exploit resistance.",
    ),
    Control(
        "egress_boundary",
        "Control egress at a boundary the agent cannot rewrite",
        "Allow only required destinations where practical, and account for permitted "
        "destinations that themselves accept uploads or messages.",
        "A hostname allowlist alone is not a complete data-loss policy.",
    ),
    Control(
        "external_approvals",
        "Keep approvals outside the agent",
        "Require an independent human or deterministic policy check for production changes, "
        "secret access, account administration, publishing, and other high-impact actions.",
        "A second AI instance reading the same hostile material is not automatically an "
        "independent security boundary.",
    ),
    Control(
        "operation_mediation",
        "Mediate operations, not vague intentions",
        "Constrain services to specific operations — artifact, destination, scope, and "
        "expiration in the approval context — rather than broad delegations such as use the "
        "signing key responsibly.",
        "A service that permits sign-this-exact-artifact-for-this-release is easier to "
        "constrain than a vague responsibility grant.",
    ),
    Control(
        "minimal_shared_state",
        "Minimize shared state",
        "Transfer only the files a task needs, and treat returned code, documents, and build "
        "artifacts as untrusted until checked; avoid automatically promoting an agent's entire "
        "home directory or development image into a trusted environment.",
        "Colocated state silently widens the authority a compromised task can reach.",
    ),
    Control(
        "environment_refresh",
        "Refresh execution environments",
        "Destroy task environments when work ends, and apply updates before creating the next "
        "ones; distinguish deletion of an environment from revocation of any credentials it "
        "could have accessed.",
        "A refreshed environment without credential revocation leaves the exfiltration channel "
        "open.",
    ),
    Control(
        "tool_bridge_constrain",
        "Constrain tool bridges",
        "Review filesystem, browser, repository, CI, cloud, and messaging integrations as "
        "explicit grants of authority.",
        "An isolated process with a powerful API token is still a powerful actor.",
    ),
    Control(
        "independent_audit",
        "Preserve an independent audit trail",
        "Record tool use, permission grants, policy changes, and deployment decisions outside "
        "the execution environment; make the record useful for reconstructing what happened, "
        "not just collecting agent prose.",
        "An audit trail inside the agent's writable state can be rewritten by the actor it "
        "records.",
    ),
    Control(
        "rehearsed_recovery",
        "Rehearse recovery",
        "Test rebuilding the environment, revoking credentials, recovering keys, and restoring "
        "data.",
        "A rebuild cannot undo data already exfiltrated or remote changes already accepted, so "
        "recovery must be rehearsed against revocation and restoration paths, not just "
        "reconstruction.",
    ),
)

#: The 9 configuration invariants (agent must never be able to; ids pinned by
#: the brief and ``manuscript/config.yaml``).
CONFIGURATION_INVARIANTS: tuple[str, ...] = (
    "add an unrestricted credential provider",
    "disable isolation",
    "widen its own network policy",
    "replace the trusted update signer",
    "alter the approving identity",
    "mount unrelated user data",
    "expand its own tool grants",
    "rewrite the audit trail",
    "approve its own policy changes",
)
