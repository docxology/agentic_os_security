---
name: trust-domain-design
description: Partition a workspace into the seven trust domains with explicit per-domain contents and restrictions.
---
# Trust-Domain Design

A workspace is partitioned into seven trust domains — administration, personal identity, credential/signing service, agent execution, browsing and intake, release/deployment, and recovery — each with explicit contents and restrictions ([@tbl:trust_domains] in [@sec:agentic_authority]). The failure this closes: an undivided workspace lets hostile content in one context (a document, a browser session, a repository) reach the credentials and authority of another, so a single compromised component or a steered agent becomes host-level compromise. Agent execution is just one domain: disposable, narrowly scoped, holding no host home, no broad credential directory, and no privileged container socket. One of nine concept skills shipped by this review under the CogSecSkills registry doctrine [@cogsecskills2026].

## Apply

1. List the seven domains and assign every artifact, credential, and network path to exactly one.
2. Write each domain's restrictions as what may not cross into it (no routine browsing in administration; no colocating personal identity with untrusted dependencies or a general-purpose agent).
3. Check that no agent task spans domains that were meant to be isolated, and that intake content is reviewed before it crosses into trusted work.
4. Keep recovery (known-good configuration, independent backups, recovery credentials) beyond the destructive authority of the daily workstation and its agent.

## Evidence in this repository

- Manuscript: [@sec:agentic_authority] (manuscript/09_agentic_authority_architecture.md)
- Data: src/agentic_os_security/trust_domains.py::TRUST_DOMAINS
- Conformance: tests/test_trust_domains.py::test_seven_unique_trust_domains_with_pinned_ids
