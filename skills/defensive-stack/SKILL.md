---
name: defensive-stack
description: Assess a platform's coverage across the eight ordered mitigation classes of the operating-system defensive stack.
---
# Defensive Stack

The operating-system defensive stack is eight ordered mitigation classes — hardware/firmware, hypervisor, kernel/LSM, sandbox runtime, container/microVM runtime, update/provisioning, application framework, agent runtime/tool bridge — scored per archetype with the stance vocabulary ([@fig:defensive_stack]; the stack matrix of [@sec:evaluation_framework]). The layering rule is composition, not accumulation: a compromise at layer i must not grant authority at layer i+1 ([@eq:stack_layering] in [@sec:servers]). The failure this closes: mitigation lists read as checklists hide whether the layers actually compose — a hardened kernel behind an unmediated agent tool bridge is one failed layer granting authority at the next. One of nine concept skills shipped by this review under the CogSecSkills registry doctrine [@cogsecskills2026].

## Apply

1. Fix the eight classes as rows and the platform's archetypes as columns.
2. Score each cell with the stance vocabulary — `strong`, `partial`, `weak`, or `n_a` — with no partial credit across classes.
3. Check the layering rule: does a breach at layer i grant authority at layer i+1? If yes, the composition is broken regardless of how good the individual cells look.
4. Report gaps as named limitations, not averaged scores.

## Evidence in this repository

- Manuscript: [@sec:evaluation_framework] (manuscript/03_evaluation_framework.md)
- Data: output/data/defensive_stack.csv
- Conformance: tests/test_stack.py::test_eight_unique_layers_with_pinned_ids
