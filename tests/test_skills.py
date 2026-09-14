"""Concept-skill library conformance: the skills/ surface (registry +
SKILL.md files) mirrors the directory tree, parses cleanly, points at
real section labels, real evidence artifacts, real conformance tests,
and only citation keys that exist in references.bib.

Zero-mock, deterministic, network-free: validated against the real
repository files only.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

from test_manuscript_structure import SECTION_FILES

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = PROJECT_ROOT / "skills"
REGISTRY_PATH = SKILLS_DIR / "registry.yaml"
BIB_PATH = PROJECT_ROOT / "manuscript" / "references.bib"

SKILL_COUNT = 9
SECTION_LABELS = {label for _, label in SECTION_FILES.values()}


@pytest.fixture(scope="module")
def registry() -> list[dict]:
    raw = yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8"))
    assert isinstance(raw, dict) and "skills" in raw, "registry.yaml: no skills key"
    rows = raw["skills"]
    assert isinstance(rows, list)
    return rows


def skill_text(row: dict) -> str:
    return (SKILLS_DIR / row["id"] / "SKILL.md").read_text(encoding="utf-8")


def frontmatter(row: dict) -> dict:
    text = skill_text(row)
    match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    assert match is not None, f"{row['id']}/SKILL.md: no --- frontmatter block"
    front = yaml.safe_load(match.group(1))
    assert isinstance(front, dict), f"{row['id']}/SKILL.md: frontmatter not a mapping"
    return front


def test_registry_parses_with_nine_unique_slug_ids(registry):
    assert len(registry) == SKILL_COUNT
    ids = [row["id"] for row in registry]
    assert len(set(ids)) == SKILL_COUNT
    for sid in ids:
        assert re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", sid), sid


def test_rows_carry_required_fields(registry):
    for row in registry:
        for field in ("id", "title", "section", "artifact", "test"):
            assert isinstance(row.get(field), str) and row[field].strip(), (
                row.get("id"),
                field,
            )


def test_directory_parity_both_directions(registry):
    ids = {row["id"] for row in registry}
    dirs = {p.name for p in SKILLS_DIR.iterdir() if p.is_dir()}
    assert dirs == ids, "skills/ directories and registry rows disagree"
    for sid in ids:
        assert (SKILLS_DIR / sid / "SKILL.md").is_file(), sid


def test_frontmatter_name_and_description(registry):
    for row in registry:
        front = frontmatter(row)
        assert front.get("name") == row["id"], row["id"]
        description = front.get("description")
        assert isinstance(description, str) and description.strip(), row["id"]


def test_body_has_summary_apply_and_evidence(registry):
    for row in registry:
        text = skill_text(row)
        assert re.search(r"^## Apply$", text, re.MULTILINE), row["id"]
        assert re.search(r"^## Evidence in this repository$", text, re.MULTILINE), (
            row["id"]
        )
        for pointer in ("Manuscript:", "Data:", "Conformance:"):
            assert pointer in text, (row["id"], pointer)


def test_section_labels_within_structure_registry(registry):
    for row in registry:
        assert row["section"] in SECTION_LABELS, (row["id"], row["section"])
        text = skill_text(row)
        for label in re.findall(r"\[@sec:([a-z0-9_]+)\]", text):
            assert f"sec:{label}" in SECTION_LABELS, (row["id"], label)


def test_artifact_paths_exist(registry):
    for row in registry:
        artifact = row["artifact"]
        path_part, _, symbol = artifact.partition("::")
        target = PROJECT_ROOT / path_part
        assert target.is_file(), (row["id"], artifact)
        if symbol:
            assert re.search(rf"\b{re.escape(symbol)}\b", target.read_text()), (
                row["id"],
                artifact,
            )


def test_referenced_conformance_tests_exist(registry):
    for row in registry:
        spec = row["test"]
        path_part, _, test_name = spec.partition("::")
        target = PROJECT_ROOT / path_part
        assert target.is_file(), (row["id"], spec)
        assert test_name, (row["id"], spec)
        module_text = target.read_text(encoding="utf-8")
        assert re.search(rf"^def {re.escape(test_name)}\(", module_text, re.MULTILINE), (
            row["id"],
            spec,
        )


def test_skill_body_citation_keys_in_bib(registry):
    bib_text = BIB_PATH.read_text(encoding="utf-8")
    bib_keys = set(re.findall(r"^@\w+\{([^,\s]+),", bib_text, re.MULTILINE))
    assert bib_keys, "references.bib parsed empty"
    for row in registry:
        text = skill_text(row)
        for key in re.findall(r"\[@([A-Za-z0-9_]+)\]", text):
            assert key in bib_keys, (row["id"], key)
