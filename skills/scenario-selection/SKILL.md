---
name: scenario-selection
description: Map an operator situation to the eight scenario recommendations with their change conditions and confidence tiers.
---
# Scenario Selection

Eight named scenarios map operator situations to recommended platform postures, each carrying the conditions under which the recommendation changes ([@tbl:scenarios]; the scenario table of [@sec:scenarios]). The failure this closes: generic "best platform" advice ignores the operator's actual constraints — compartmentalization need, agent-exposure surface, update tolerance, maintenance budget — so recommendations drift into labels; naming the change conditions keeps every recommendation falsifiable instead of oracular. One of nine concept skills shipped by this review under the CogSecSkills registry doctrine [@cogsecskills2026].

## Apply

1. State the operator situation: workload, threat concern, agent exposure, maintenance budget.
2. Find the matching scenario and its recommended posture, plus the runner-up and what would flip it.
3. Note the change conditions: which observed change would void the recommendation.
4. Record the confidence tier with its evidence limits, and revisit when a change condition fires.

## Evidence in this repository

- Manuscript: [@sec:scenarios] (manuscript/15_scenarios_and_confidence.md)
- Data: output/data/scenario_recommendations.csv
- Conformance: tests/test_registry.py::test_eight_unique_scenarios_with_narrative_fields
