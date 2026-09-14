---
name: authority-ladder
description: Classify an agent action on the six-rung authority ladder and flag exercise without external authorization.
---
# Authority Ladder

Agent authority is a total order over six rungs — propose < stage < authorize < exercise < audit < revoke — where an agent may propose and stage freely but must never exercise a consequential action whose authorization was granted inside its own hierarchy ([@eq:authority_ladder_order]; [@def:authority_ladder_order] in [@sec:agentic_authority]). The failure this closes: the confused deputy — an agent using legitimate authority as directed by hostile content is indistinguishable from an attacker holding that authority, so the review's axis is held authority rather than exploit difficulty, and the rung order descends directly from the separation of proposal from authorization [@saltzer1975]. One of nine concept skills shipped by this review under the CogSecSkills registry doctrine [@cogsecskills2026].

## Apply

1. For the action in question, name its rung: propose, stage, authorize, exercise, audit, or revoke.
2. Check who holds the rung above it: exercise requires an authorize decision made outside the acting agent.
3. Flag agent-exercised consequential actions whose authorization was granted by the same agent or its peers — that is the unauthorized-exercise pattern.
4. Close the loop by naming who audits the ladder and who can revoke a grant.

## Evidence in this repository

- Manuscript: [@sec:agentic_authority] (manuscript/09_agentic_authority_architecture.md)
- Data: src/agentic_os_security/threat_model.py::AUTHORITY_LADDER
- Conformance: tests/test_threat_model.py::test_authority_ladder_is_pinned_six_rung_sequence
