"""Figure orchestration: each of the nine registry generators plus the
cover graphical abstract writes its PNG (exists, >10KB), and two
consecutive full generation runs are byte-identical given the same inputs
(determinism contract).
"""

from __future__ import annotations

import hashlib

import pytest

from agentic_os_security import project_paths
from agentic_os_security.figures import (
    generate_agent_surface,
    generate_authority_ladder,
    generate_defensive_stack,
    generate_evidence_timeline,
    generate_forecast_horizon,
    generate_graphical_abstract,
    generate_orchestration_boundaries,
    generate_property_matrix,
    generate_trust_domains,
    generate_update_windows,
)

FIGURE_REGISTRY = {
    "evidence_timeline": "evidence_timeline.png",
    "property_matrix": "property_matrix.png",
    "defensive_stack": "defensive_stack.png",
    "trust_domains": "trust_domains.png",
    "authority_ladder": "authority_ladder.png",
    "orchestration_boundaries": "orchestration_boundaries.png",
    "agent_surface": "agent_surface.png",
    "forecast_horizon": "forecast_horizon.png",
    "update_windows": "update_windows.png",
}

GENERATOR_FILENAMES = {
    **FIGURE_REGISTRY,
    # The cover figure, outside the manuscript registry.
    "graphical_abstract": "graphical_abstract.png",
}


GENERATORS = {
    "evidence_timeline": generate_evidence_timeline,
    "property_matrix": generate_property_matrix,
    "defensive_stack": generate_defensive_stack,
    "trust_domains": generate_trust_domains,
    "authority_ladder": generate_authority_ladder,
    "orchestration_boundaries": generate_orchestration_boundaries,
    "agent_surface": generate_agent_surface,
    "forecast_horizon": generate_forecast_horizon,
    "update_windows": generate_update_windows,
    # The cover graphical abstract: a tenth generator that is deliberately
    # NOT a manuscript figure registry entry.
    "graphical_abstract": generate_graphical_abstract,
}


@pytest.mark.parametrize("name", sorted(GENERATOR_FILENAMES))
def test_generator_produces_registered_png(tmp_project, name):
    written = GENERATORS[name](tmp_project)
    assert written is not None
    expected = project_paths.figures_dir(tmp_project) / GENERATOR_FILENAMES[name]
    assert expected.exists(), f"{name} did not produce {expected.name}"
    assert expected.stat().st_size > 10_000, f"{expected.name} suspiciously small"


def test_all_ten_figures_present_after_full_generation(tmp_project):
    for name, generator in GENERATORS.items():
        generator(tmp_project)
    figures_dir = project_paths.figures_dir(tmp_project)
    produced = {p.name for p in figures_dir.glob("*.png")}
    expected = set(FIGURE_REGISTRY.values()) | {"graphical_abstract.png"}
    assert produced == expected


def _hash_tree(root):
    digest = hashlib.sha256()
    for path in sorted(root.rglob("*")):
        digest.update(str(path.relative_to(root)).encode("utf-8"))
        if path.is_file():
            digest.update(path.read_bytes())
    return digest.hexdigest()


def test_two_consecutive_full_runs_are_byte_identical(tmp_project):
    first_root = tmp_project / "run_one"
    second_root = tmp_project / "run_two"
    for root in (first_root, second_root):
        (root / "manuscript").mkdir(parents=True)
        (root / "output").mkdir()
    import shutil

    for root in (first_root, second_root):
        shutil.copyfile(
            tmp_project / "manuscript" / "config.yaml",
            root / "manuscript" / "config.yaml",
        )

    for root in (first_root, second_root):
        for generator in GENERATORS.values():
            generator(root)

    first_hash = _hash_tree(project_paths.figures_dir(first_root))
    second_hash = _hash_tree(project_paths.figures_dir(second_root))
    assert first_hash == second_hash, "figures are not byte-deterministic"