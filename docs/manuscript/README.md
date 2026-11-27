# Defensive design assurance note

Read the [abstract](00_abstract.md), [defensive design](01_design.md), [local verification](02_verification.md), and [scope and provenance](03_scope.md). [Reproduction instructions](../verification/README.md) cover the local check and the pinned PDF and HTML build.

The published v0.7.0 review has separate [source](../../manuscript/) and [generated artifacts](../../output/). Its archived release is identified in the repository's [citation record](../../CITATION.cff).

## Published PDF and historical receipt

The standalone PDF in the v0.7.0 deposit matches the tracked PDF. The PDF
inside the same deposit's ZIP is a different retained build. The historical
artifact manifest identifies the ZIP's PDF.

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| Standalone deposited and tracked PDF | 4,174,222 | `f6705f50bb2101ea46b2b4cbb13ba2127e20a7010708d3a4c9161fc1a95a78ce` |
| PDF inside the deposited ZIP | 4,171,493 | `7fe9f0c600c9815d8689f02ee7d9d450422230e99e4a218d4c63b5df50a7df7e` |

The ZIP preserves the staged manuscript sections from that build. Three
authored source files in the repository differ from the historical source
hashes. The retained receipt applies to its own build. The local build
described above covers the defensive assurance note.
