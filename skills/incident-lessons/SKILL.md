---
name: incident-lessons
description: Classify a documented incident into the five boundary-lesson classes and extract which boundary held or failed.
---
# Incident Lessons

The documented agentic incidents — the GTG-1002 campaign investigation, the AISI unsanctioned-behavior runs, the OpenAI-Hugging Face disruption and their 2024-2026 successors — are classified into five boundary-lesson classes; every incident-register row carries exactly one `lesson_class` ([@fig:incidents]; the register of [@sec:threat_model]). The failure this closes: reading incident reports as vendor narratives instead of evidence about which boundary held — in every documented case the damage was bounded by a boundary or a human gate, not by model restraint, and the taxonomy forces that boundary question on every new report. Vendor findings stay labeled as vendor findings; none is an independently measured universal capability rate. One of nine concept skills shipped by this review under the CogSecSkills registry doctrine [@cogsecskills2026].

## Apply

1. Read the incident as a sequence: capability exercised, boundary encountered, outcome.
2. Assign exactly one of the five lesson classes.
3. Name the boundary or human gate that bounded — or failed to bound — the damage.
4. Attribute the finding to its reporting party (vendor report, national institute, standards canon) with the matching caveat.

## Evidence in this repository

- Manuscript: [@sec:threat_model] (manuscript/02_threat_model.md)
- Data: output/data/incident_register.csv
- Conformance: tests/test_evidence.py::test_lesson_taxonomy_pins_five_unique_classes
