"""Manuscript structure: exactly the 18 registered section files, unique H1
sec labels matching the registry, cross-reference and citation-key parity
against registries and references.bib, and render-prerequisite hygiene
(no mermaid fences, no raw LaTeX cite/ref outside the preamble).
"""

from __future__ import annotations

import re

import pytest

SECTION_FILES = {
    "00_abstract.md": ("Abstract", "sec:abstract"),
    "01_introduction.md": (
        "Introduction: Agents Arrive at the Kernel Boundary",
        "sec:introduction",
    ),
    "02_threat_model.md": ("Threat Model: Two Ways to Lose", "sec:threat_model"),
    "03_evaluation_framework.md": (
        "Evaluation Framework: Properties over Labels",
        "sec:evaluation_framework",
    ),
    "04_compartmentalization_qubes.md": (
        "Compartmentalization: Qubes OS in Depth",
        "sec:qubes",
    ),
    "05_reproducible_operations_nixos.md": (
        "Reproducible Operations: NixOS in Depth",
        "sec:nixos",
    ),
    "06_conventional_desktops.md": (
        "Conventional Desktops and Hardening Candidates",
        "sec:desktops",
    ),
    "07_servers_agent_infrastructure.md": (
        "Servers and Agent-Execution Infrastructure",
        "sec:servers",
    ),
    "08_boundary_comparators.md": (
        "Boundary Comparators and Non-Linux Systems",
        "sec:comparators",
    ),
    "09_agentic_authority_architecture.md": (
        "Agentic Authority Architecture",
        "sec:agentic_authority",
    ),
    "10_cognitive_security.md": (
        "Cognitive Security: The Authorized-Misuse Surface",
        "sec:cognitive_security",
    ),
    "11_opsec_for_agent_operators.md": (
        "Operator OpSec for Agent Work",
        "sec:opsec",
    ),
    "12_orchestration_security.md": (
        "Securing Agent Orchestration",
        "sec:orchestration",
    ),
    "13_configuration_authorization.md": (
        "Configuration Generation Is Not Authorization",
        "sec:configuration_authorization",
    ),
    "14_forecast_2028_2031.md": ("Forecast: 2028–2031", "sec:forecast"),
    "15_scenarios_and_confidence.md": (
        "Scenario Recommendations and Confidence",
        "sec:scenarios",
    ),
    "16_conclusion.md": ("Conclusion: The Composition That Matters", "sec:conclusion"),
    "99_references.md": ("References", "sec:references"),
}

FIGURE_LABELS = {
    "fig:evidence_timeline",
    "fig:property_matrix",
    "fig:trust_domains",
    "fig:authority_ladder",
    "fig:orchestration_boundaries",
    "fig:forecast_horizon",
    "fig:defensive_stack",
    "fig:update_windows",
    "fig:agent_surface",
}

TABLE_LABELS = {
    "tbl:properties",
    "tbl:offensive_evidence",
    "tbl:qubes_limits",
    "tbl:nixos_misconceptions",
    "tbl:desktops",
    "tbl:servers",
    "tbl:comparators",
    "tbl:trust_domains",
    "tbl:controls",
    "tbl:invariants",
    "tbl:scenarios",
    "tbl:confidence",
}

BIB_ENTRY_RE = re.compile(r"@(\w+)\s*\{\s*([^,\s]+)\s*,")
CITATION_RE = re.compile(
    r"(?<![\w@.\-])@([A-Za-z][\w.\-+/]*)(?=[\s\],;)\]}]|$)"
)
SEC_LABEL_RE = re.compile(r"\{#(sec:[\w-]+)\}")
FIG_DEF_RE = re.compile(r"\{#(fig:[\w-]+)")
TBL_DEF_RE = re.compile(r"\{#(tbl:[\w-]+)")
FIG_REF_RE = re.compile(r"\[@(fig:[\w-]+)")
TBL_REF_RE = re.compile(r"\[@(tbl:[\w-]+)")

TOKEN_PLAN = frozenset(
    {
        "CONFIG_VERSION",
        "CONFIG_REVIEW_DATE",
        "CONFIG_FORECAST_HORIZON",
        "CONFIG_NUM_CANDIDATES",
        "CONFIG_NUM_PROPERTIES",
        "CONFIG_NUM_SCENARIOS",
        "CONFIG_NUM_TRUST_DOMAINS",
        "CONFIG_NUM_CONTROLS",
        "CONFIG_NUM_INVARIANTS",
        "CONFIG_NUM_SOURCES",
        "CONFIG_KEYWORDS",
        "RESULT_MATRIX_CELLS",
        "RESULT_MATRIX_COVERAGE_PCT",
        "RESULT_STANCE_STRONG_COUNT",
        "RESULT_STANCE_PARTIAL_COUNT",
        "RESULT_STANCE_WEAK_COUNT",
        "RESULT_STANCE_NA_COUNT",
        "RESULT_NUM_FIGURES",
        "RESULT_FORECAST_TOTAL",
        "RESULT_FORECAST_HIGH",
        "RESULT_FORECAST_MODERATE",
        "RESULT_FORECAST_LOW",
        "ARTIFACT_FIGURES",
        "ARTIFACT_DATA_FILES",
        "ARTIFACT_TOTAL",
        "GENERATION_TIMESTAMP",
        "PYTHON_VERSION",
        "NUMPY_VERSION",
        "PLATFORM",
        "CONFIG_HASH",
    }
)

@pytest.fixture(scope="module")
def manuscript_dir(project_root):
    return project_root / "manuscript"


@pytest.fixture(scope="module")
def section_paths(manuscript_dir):
    return {name: manuscript_dir / name for name in SECTION_FILES}


@pytest.fixture(scope="module")
def bib_keys(project_root):
    text = (project_root / "manuscript" / "references.bib").read_text(encoding="utf-8")
    return {match.group(2) for match in BIB_ENTRY_RE.finditer(text)}


@pytest.fixture(scope="module")
def section_text(section_paths):
    return {
        name: path.read_text(encoding="utf-8") for name, path in section_paths.items()
    }


def test_manuscript_has_exactly_the_18_section_files(manuscript_dir):
    numbered = re.compile(r"^\d{2}_.*\.md$")
    section_files = {
        p.name for p in manuscript_dir.glob("*.md") if numbered.match(p.name)
    }
    assert section_files == set(SECTION_FILES)


def test_every_section_has_h1_with_registered_label(section_text):
    for name, (title, label) in SECTION_FILES.items():
        text = section_text[name]
        h1s = [line for line in text.splitlines() if line.startswith("# ")]
        assert h1s, f"{name} has no H1"
        first = h1s[0]
        assert title in first, (name, first)
        assert f"{{#{label}}}" in first, (name, first)


def test_sec_labels_unique_across_manuscript(section_text):
    labels = []
    for name, text in section_text.items():
        labels.extend(SEC_LABEL_RE.findall(text))
    assert len(labels) == len(set(labels)), "duplicate sec labels"


def test_registered_sec_labels_all_present(section_text):
    found = set()
    for text in section_text.values():
        found.update(SEC_LABEL_RE.findall(text))
    assert found == {label for _, label in SECTION_FILES.values()}


def test_figure_targets_defined_in_figure_registry(section_text):
    targets = set()
    for text in section_text.values():
        targets.update(FIG_DEF_RE.findall(text))
        targets.update(FIG_REF_RE.findall(text))
    undefined = targets - FIGURE_LABELS
    assert not undefined, f"figure targets not in registry: {sorted(undefined)}"


def test_table_targets_defined_in_table_registry(section_text):
    targets = set()
    for text in section_text.values():
        targets.update(TBL_DEF_RE.findall(text))
        targets.update(TBL_REF_RE.findall(text))
    undefined = targets - TABLE_LABELS
    assert not undefined, f"table targets not in registry: {sorted(undefined)}"


def test_citation_keys_are_bib_keys(section_text, bib_keys):
    # CITATION_RE captures pandoc citation keys only: namespaced
    # pandoc-crossref targets (``@sec:...``, ``@fig:...``, ``@tbl:...``)
    # are rejected by the boundary lookahead, and locator tails
    # (``[@key, pp. 42]``) and multi-citations (``[@k1; @k2]``) resolve
    # to bare keys. Every remaining key must be in references.bib.
    missing = {}
    for name, text in section_text.items():
        keys = set(CITATION_RE.findall(text))
        unknown = keys - bib_keys
        if unknown:
            missing[name] = sorted(unknown)
    assert not missing, f"citation keys absent from references.bib: {missing}"


def test_no_mermaid_fences(section_text):
    for name, text in section_text.items():
        assert "```mermaid" not in text, f"{name} contains a mermaid fence"


def test_no_raw_cite_or_ref_outside_preamble(manuscript_dir):
    offenders = []
    for path in manuscript_dir.glob("*.md"):
        if path.name == "SYNTAX.md":
            continue
        if path.name == "preamble.md":
            continue
        text = path.read_text(encoding="utf-8")
        if re.search(r"\\cite\{", text):
            offenders.append((path.name, "\\cite{"))
        if re.search(r"\\ref\{", text):
            offenders.append((path.name, "\\ref{"))
    assert not offenders, f"raw LaTeX cite/ref in prose: {offenders}"


def test_all_tokens_are_from_token_plan(section_text):
    token_re = re.compile(r"\{\{([A-Z_][A-Z0-9_]*)\}\}")
    used = set()
    for text in section_text.values():
        used.update(token_re.findall(text))
    unknown = used - TOKEN_PLAN
    assert not unknown, f"tokens outside the plan: {sorted(unknown)}"
