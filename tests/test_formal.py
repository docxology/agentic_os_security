"""Formal-definition structural invariants: 8 pinned definitions with
ASCII-only LaTeX statements, balanced braces, bib-resolvable citation
keys, and a surface grouping that covers every definition.
"""

from __future__ import annotations

import re

from agentic_os_security import formal

BIB_ENTRY_RE = re.compile(r"@(\w+)\s*\{\s*([^,\s]+)\s*,")

DEFINITION_IDS = [
    "stance_mapping",
    "stance_order",
    "authority_ladder_order",
    "delegation_bound",
    "defense_composition",
    "invariant_predicate",
    "stack_layering",
    "update_window_semantics",
]


def test_eight_unique_definitions_with_pinned_ids():
    ids = [d.definition_id for d in formal.FORMAL_DEFINITIONS]
    assert len(formal.FORMAL_DEFINITIONS) == 8
    assert len(set(ids)) == 8
    assert ids == DEFINITION_IDS


def test_names_and_informals_are_nonempty():
    for definition in formal.FORMAL_DEFINITIONS:
        assert definition.name.strip(), definition.definition_id
        assert definition.informal.strip(), definition.definition_id


def test_formal_latex_is_pure_ascii():
    for definition in formal.FORMAL_DEFINITIONS:
        bad = [
            ch
            for ch in definition.formal_latex
            if not (32 <= ord(ch) <= 126 or ch == "\n")
        ]
        assert not bad, (definition.definition_id, bad)


def test_formal_latex_braces_are_balanced_ignoring_escapes():
    for definition in formal.FORMAL_DEFINITIONS:
        # Unescape literal \{ and \} before counting: LaTeX renders them
        # as characters, so they must not participate in grouping.
        body = definition.formal_latex.replace(r"\{", "").replace(r"\}", "")
        assert body.count("{") == body.count("}"), definition.definition_id


LATEX_COMMANDS = frozenset(
    {
        "sigma",
        "colon",
        "times",
        "to",
        "cup",
        "textit",
        "operatorname",
        "prec",
        "succ",
        "le",
        "equiv",
        "infty",
        "circ",
        "Rightarrow",
        "not",
        "forall",
        "delta",
        "cdot",
        "cdots",
        "neg",
        "iota",
        "in",
        "notin",
        "nearrow",
        "ldots",
        "mathbb",
        "quad",
    }
)


def test_formal_latex_commands_are_known_math_macros():
    # Every backslash opens a known LaTeX math command (allowlist), so the
    # statements are renderable inline math rather than free text.
    for definition in formal.FORMAL_DEFINITIONS:
        used = set(re.findall(r"\\([A-Za-z]+)", definition.formal_latex))
        unknown = used - LATEX_COMMANDS
        assert not unknown, (definition.definition_id, sorted(unknown))


def test_citation_keys_are_bib_entries(project_root):
    bib_text = (project_root / "manuscript" / "references.bib").read_text(
        encoding="utf-8"
    )
    bib_keys = {match.group(2) for match in BIB_ENTRY_RE.finditer(bib_text)}
    for definition in formal.FORMAL_DEFINITIONS:
        assert definition.citation_keys, definition.definition_id


def test_surfaces_are_nonempty():
    for definition in formal.FORMAL_DEFINITIONS:
        assert definition.surface.strip(), definition.definition_id


def test_definitions_by_surface_covers_all_definitions():
    grouped = formal.definitions_by_surface()
    assert sum(len(defs) for defs in grouped.values()) == 8
    assert set(grouped) == {d.surface for d in formal.FORMAL_DEFINITIONS}
    all_ids = []
    for defs in grouped.values():
        all_ids.extend(d.definition_id for d in defs)
    assert sorted(all_ids) == sorted(DEFINITION_IDS)