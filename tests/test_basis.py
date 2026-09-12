"""Candidate-basis registry invariants: one dense stance-profile basis per
registry candidate id, with primary sources that resolve to real
bibliography entries in ``manuscript/references.bib``.

Grounded in the v0.5.0 shared brief: 24 rows, ids pinned to
:data:`agentic_os_security.registry.CANDIDATES`, summaries of at least 80
characters, and 3–6 primary sources per row, all existing bib keys.
"""

from __future__ import annotations

import re

from agentic_os_security import basis, registry

# key -> entry, exactly the regex ``test_evidence.py`` pins for bib parity.
BIB_ENTRY_RE = re.compile(r"@(\w+)\s*\{\s*([^,\s]+)\s*,")


def test_one_basis_row_per_registry_candidate_in_registry_order(project_root):
    ids = [entry.basis_id for entry in basis.CANDIDATE_BASIS]
    registry_ids = [candidate.candidate_id for candidate in registry.CANDIDATES]
    assert len(ids) == 24
    assert len(set(ids)) == len(ids)
    assert set(ids) == set(registry_ids)
    # Same order as the registry so derived artifacts stay deterministic.
    assert ids == registry_ids


def test_summaries_are_dense_stance_profile_bases():
    for entry in basis.CANDIDATE_BASIS:
        assert isinstance(entry.summary, str)
        assert len(entry.summary) >= 80, entry.basis_id
        assert entry.summary.strip(), entry.basis_id


def test_primary_sources_are_three_to_six_existing_bib_keys(project_root):
    bib_text = (project_root / "manuscript" / "references.bib").read_text(
        encoding="utf-8"
    )
    bib_keys = {match.group(2) for match in BIB_ENTRY_RE.finditer(bib_text)}
    for entry in basis.CANDIDATE_BASIS:
        count = len(entry.primary_sources)
        assert 3 <= count <= 6, f"{entry.basis_id}: {count} primary sources"
        missing = set(entry.primary_sources) - bib_keys
        assert not missing, f"{entry.basis_id}: {sorted(missing)}"
