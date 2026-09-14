---
name: delegation-bound
description: Check an agent-to-agent delegation chain against the delta-bound so trust never amplifies through a broker.
---
# Delegation Bound

For a delegation chain a to b to c, trust does not amplify: trust(a->c) <= delta * trust(a->b) — the delta-bound ([@eq:delegation_bound]; [@def:delegation_bound] in [@sec:orchestration]). The failure this closes: the orchestrator/broker is a privileged intermediary and every delegation chain is a confused-deputy structure [@hardy1988] — a trusted intermediary can be steered into passing on, or compounding, more trust than it holds, so the target of a chain ends up more trusted than the principal that launched it. One of nine concept skills shipped by this review under the CogSecSkills registry doctrine [@cogsecskills2026].

## Apply

1. Write the chain out: who delegates to whom, through which broker.
2. Compare the trust the target receives against delta times the trust the delegator holds in the broker.
3. Reject any hop where the broker passes on, or compounds, authority it does not itself hold.
4. Enforce the check at a mediation point outside the agents, not as an agent-side convention.

## Evidence in this repository

- Manuscript: [@sec:orchestration] (manuscript/12_orchestration_security.md)
- Data: src/agentic_os_security/formal.py::delegation_bound
- Conformance: tests/test_formal.py::test_definition_blocks_mirror_formal_definitions
