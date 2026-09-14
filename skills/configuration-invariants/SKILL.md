---
name: configuration-invariants
description: Review a proposed configuration or policy change against the nine invariants an agent must not be able to violate.
---
# Configuration Invariants

Nine invariants state what a deployed configuration must guarantee regardless of what the agent proposes — the agent must not add an unrestricted credential provider, disable isolation, widen its own network policy, replace the trusted update signer, alter the approving identity, mount unrelated user data, expand its own tool grants, rewrite the audit trail, or approve its own policy changes ([@tbl:invariants]; [@eq:invariant_predicate]; [@def:invariant_predicate] in [@sec:configuration_authorization]). Formally, for every agent-reachable generation g and each invariant, the violating state must be unreachable. The failure this closes: treating generation as authorization — an agent that can emit valid configuration is not thereby authorized to deploy it, and the reviewer/enforcer must be independent of the constrained agent ([@saltzer1975]). One of nine concept skills shipped by this review under the CogSecSkills registry doctrine [@cogsecskills2026].

## Apply

1. Treat the proposed change as untrusted input, whatever produced it.
2. Check it against each of the nine invariants — not against the agent's own validation.
3. Require the review and the enforcement to run outside the agent's authority.
4. Deploy only through the path the invariant enforcer authorizes, and keep the audit trail beyond the agent's write authority.

## Evidence in this repository

- Manuscript: [@sec:configuration_authorization] (manuscript/13_configuration_authorization.md)
- Data: src/agentic_os_security/trust_domains.py::CONFIGURATION_INVARIANTS
- Conformance: tests/test_trust_domains.py::test_nine_configuration_invariants_are_nonempty_and_unique
