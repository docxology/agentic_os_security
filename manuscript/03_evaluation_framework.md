# Evaluation Framework: Properties over Labels {#sec:evaluation_framework}

## Why not a distribution label

"Secure Linux" is not a property of a distribution; it is an outcome of a deployment matching a threat model. Distribution labels hide exactly the heterogeneity that matters: one candidate may pair a strong containment architecture with a weak update-operations story, another may have excellent supply-chain discipline and no runtime confinement at all. A single label collapses those differences into a ranking question that no available evidence answers — and ranking invites the numeric composite scores ("Qubes 9.4" style) that this review refuses, for reasons given below. The alternative, inherited from the source assessment, is to evaluate every candidate against a fixed set of properties, each phrased as a question a deployment can be interrogated with.

## The nine properties

[@tbl:properties] states the {{CONFIG_NUM_PROPERTIES}} properties used throughout the review, with the question each property asks and its security significance in this threat model.

| Property | Question to ask | Security significance |
| --- | --- | --- |
| Containment | What remains protected after the browser or agent is fully controlled? | A prevention failure should not automatically become whole-machine compromise. |
| Authority | What can the process already read, transmit, sign, or change? | Excessive legitimate permissions can bypass the need for an exploit; this is the authorized-misuse axis from [@sec:threat_model]. |
| Trusted computing base | Which privileged components must all remain correct? | A small, carefully constrained boundary is preferable to many privileged integrations; it is also what patch operations must cover [@saltzer1975]. |
| Application confinement | Are permissions restrictive by default and actually compatible with the applications? | A theoretical policy is not protection if users routinely disable it. |
| Integrity | What verifies the boot chain and deployed software, and who holds the keys? | Authenticity, runtime integrity, and resistance to rollback are distinct properties, not one checkbox. |
| Persistence and recovery | Which state survives replacement or reboot? | Rebuilding the system is insufficient if malicious user state or stolen credentials survive. |
| Update operations | How quickly do fixes reach every active environment? | A strong architecture with neglected templates or pinned dependencies can lose its advantage — the QSB-118 lesson in [@sec:qubes]. |
| Supply-chain trust | Who may introduce or approve new executable code? | Reproducibility and signatures answer different questions from whether code is benign [@nixos_reproducibility]. |
| Human usability | Will the owner preserve the intended boundaries during real work? | Sustainable security is more valuable than a configuration abandoned under pressure. |
: The {{CONFIG_NUM_PROPERTIES}} evaluation properties: the question each property asks and its security significance in this threat model. {#tbl:properties}

The properties are evaluation criteria, not a scoring model. They overlap deliberately where the underlying security properties genuinely interact (authority with containment, trusted computing base with update operations), and the overlap is visible in the analysis rather than averaged away.

## The anti-scoring stance

There is no adequate evidence in this review for assigning meaningful universal scores, and raw vulnerability counts would not resolve the comparison either: they conflate disclosure volume with exposure, and they are confounded by project size, patch latency, and measurement effort. Worse, composite scores create false precision across incommensurable properties — trading a point of "usability" against a point of "containment" implies an exchange rate that no operator's actual threat model supplies. This is the same discipline that separates reproducible deployment from verified reproducible builds [@nixos_reproducibility] and authenticity from provenance: properties that answer different questions must stay separate.

Instead, every candidate–property cell receives one qualitative stance: **strong**, **partial**, **weak**, or **n_a**. A `strong` stance means the documented design directly and coherently addresses the property in this threat model. `partial` means the property is addressed with material conditions, integration gaps, or operator obligations attached. `weak` means the documented design provides little of what the property asks. `n_a` marks candidates for which the property is out of scope or unverified by available evidence — used rather than guessed, because absence of a confirmed feature in this review is not proof the feature is unavailable.

## How the matrix is constructed and refreshed

The matrix lives as data, not prose. In `src/agentic_os_security/registry.py`, each candidate carries a `property_stance` dictionary keyed by all {{CONFIG_NUM_PROPERTIES}} property identifiers, alongside a design summary, a named limitation, and an assessment. The pipeline emits the full {{CONFIG_NUM_CANDIDATES}}-candidate × {{CONFIG_NUM_PROPERTIES}}-property table to `output/data/evaluation_matrix.csv` — one row per pair — and self-checks enforce stance-vocabulary validity and matrix completeness before any figure is regenerated. Stances are assigned from documented designs, official security documentation, project advisories, and primary incident reports; vendor feature lists support `partial` or `strong` stances only where the project itself documents the mechanism, never as measured resistance results.

Refresh is a deliberate operation: a stance changes when the underlying documentation, an advisory, or a release note changes — for example, a fixed advisory can move an update-operations stance, while a new integration gap documented by the project can move an application-confinement stance. Because the matrix is deterministic data with the review date {{CONFIG_REVIEW_DATE}} stamped into the build, a future refresh produces a diffable artifact: added rows, changed stances, and the reasons, rather than rewritten narrative. [@fig:property_matrix] renders the current matrix.

![The candidate–property stance matrix across {{CONFIG_NUM_CANDIDATES}} candidates and {{CONFIG_NUM_PROPERTIES}} properties, rendered from output/data/evaluation_matrix.csv with colorblind-safe encoding of the strong/partial/weak/n_a vocabulary.](../output/figures/property_matrix.png){#fig:property_matrix width=100%}

## What the matrix buys

Three things. First, **comparability without false precision**: two candidates can be contrasted property by property, and the contrast shows *where* they differ (Qubes holds containment strongly and application confinement partially; NixOS holds update operations and supply-chain trust strongly and application confinement weakly) rather than by how much in aggregate. Second, **auditability**: each stance is a claim about documentation that a reader can check against the cited source, and the structural invariants are test-enforced — every candidate covers every property, every stance is in the vocabulary, and the matrix has {{CONFIG_NUM_CANDIDATES}} × {{CONFIG_NUM_PROPERTIES}} cells exactly. Third, **scenario grounding**: the per-scenario recommendations in [@sec:scenarios] select candidates by which properties the scenario's threat model weights most, which is precisely what a label-based ranking cannot do.

## Limitations of matrix thinking

A matrix is a discipline for judgment, not a substitute for it, and four limits should be kept in view.

- **Stances are not measurements.** Every cell is an analytical judgment from documented designs [@saltzer1975]; none is a penetration-test result. The vocabulary encodes confidence in a documented capability, not a measured resistance rate against a live adversary.
- **Properties interact.** A strong containment stance can be nullified by a weak update-operations stance if the containment mechanism itself ships unpatched; a strong integrity stance does not constrain what an authorized agent does with verified software. Cell-level reading without row-level synthesis will mislead, which is why the scenario chapters, not the matrix, carry the recommendations.
- **Unverified defaults are a standing gap.** Where this review could not verify a current default or security property, the cell says so; a future audit may legitimately move stances in either direction, and the diffability of the matrix is designed for exactly that.
- **The matrix is frozen in time at {{CONFIG_REVIEW_DATE}}.** Projects ship; advisories land; trajectories noted per candidate (for instance, the GUI-domain split in [@sec:qubes] and boot-integrity work in [@sec:nixos]) may convert into stronger stances at the next refresh. Low-confidence forecasting of those movements is handled in [@sec:forecast] rather than smuggled into current stances.

With the framework fixed, the next two sections apply it in depth to the two anchor platforms whose properties the rest of the architecture inherits: Qubes OS for containment [@qubes_architecture] and NixOS for reproducible operations [@nixos_wiki].