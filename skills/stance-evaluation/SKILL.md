---
name: stance-evaluation
description: Evaluate a platform candidate against the nine OS-security properties using the qualitative stance vocabulary, never numeric composite scores.
---
# Stance Evaluation

Every candidate is assessed against the nine properties — containment, authority, trusted computing base, application confinement, integrity, persistence and recovery, update operations, supply-chain trust, and human usability — and each candidate-property cell holds exactly one qualitative stance: `strong`, `partial`, `weak`, or `n_a`. The formal statement is the total stance mapping sigma: C x P -> S union {n_a} with the preference order strong > partial > weak, n_a outside the order ([@eq:stance_mapping]; [@eq:stance_order] in [@sec:evaluation_framework]). The failure this closes: distribution labels ("hardened desktop", "verified kernel") hide which specific properties a platform actually holds, and numeric composite scores manufacture precision the evidence does not support — per-property stances keep every judgment traceable to a documented design or advisory. One of nine concept skills shipped by this review under the CogSecSkills registry doctrine [@cogsecskills2026].

## Apply

1. Fix the nine properties as the standing question list for the candidate (platform, deployment, or toolchain) under review.
2. For each property, record exactly one stance — `strong`, `partial`, `weak`, or `n_a` — citing the documented design or advisory that supports it.
3. Refuse composite scores: compare candidates property by property, never by an averaged number.
4. Report every `weak` or `n_a` cell with the named limitation that explains it.

## Evidence in this repository

- Manuscript: [@sec:evaluation_framework] (manuscript/03_evaluation_framework.md)
- Data: output/data/evaluation_matrix.csv
- Conformance: tests/test_registry.py::test_every_candidate_stance_covers_all_properties_with_valid_vocab
