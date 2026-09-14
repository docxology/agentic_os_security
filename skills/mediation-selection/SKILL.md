---
name: mediation-selection
description: Select mediation points for each agent capability class so every consequential call is a checked decision.
---
# Mediation Selection

The six agent capability classes — content intake, tool-bridge use, credential touch, external communications, state mutation, self-modification — each map to the mediation points that bound them, out of the ten defined boundaries where an agent tool call becomes a checked decision: operation, artifact, destination, scope, expiry ([@fig:agent_surface]; the capability x mediation map of [@sec:orchestration]). The failure this closes: incomplete mediation [@saltzer1975] — any unchecked path (a container runtime socket, the user's own shell, a direct model-provider channel) is not a shortcut but the attack path, because the agent routes around every point that is not enforced. One of nine concept skills shipped by this review under the CogSecSkills registry doctrine [@cogsecskills2026].

## Apply

1. Enumerate the agent's capability classes and, for each, the resources it can reach.
2. Pick the mediation point per class where the call is checked, with the decision outside the agent and the policy separate from the task.
3. Verify complete mediation: no bypass channel from the agent to the resource, including ambient credentials and shared sockets.
4. Scope every grant — artifact, destination, expiry — and review the grant as authority, not as configuration.

## Evidence in this repository

- Manuscript: [@sec:orchestration] (manuscript/12_orchestration_security.md)
- Data: output/data/capability_mediation_map.csv
- Conformance: tests/test_orchestration.py::test_ten_mediation_points_with_pinned_unique_ids
