"""Check the static defensive registry and render a reproducible count inventory."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "agentic_os_security" / "trust_domains.py"


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    # WHY: Use the same isolated module as the native test, without importing the
    # review's unrelated registries through the package initializer.
    sys.path.insert(0, str(SOURCE.parent.parent))
    from agentic_os_security import trust_domains

    domains = trust_domains.TRUST_DOMAINS
    controls = trust_domains.CONTROLS
    invariants = trust_domains.CONFIGURATION_INVARIANTS
    classifications = {
        "Trust domains": [item.domain_id for item in domains],
        "Design controls": [item.control_id for item in controls],
        "Configuration invariants": list(invariants),
    }
    for category, entries in classifications.items():
        if not entries or len(entries) != len(set(entries)) or not all(entries):
            raise ValueError(f"Missing or duplicate entries in {category}.")
    if not all(item.contents and item.restrictions for item in domains):
        raise ValueError("A trust domain is missing contents or restrictions.")
    if not all(item.rule.strip() and item.rationale.strip() for item in controls):
        raise ValueError("A design control is missing its rule or rationale.")

    counts = {category: len(entries) for category, entries in classifications.items()}
    data = ROOT / "output" / "data"
    figures = ROOT / "output" / "figures"
    data.mkdir(parents=True, exist_ok=True)
    figures.mkdir(parents=True, exist_ok=True)
    write_json(
        data / "defensive_registry_check.json",
        {
            "source": SOURCE.relative_to(ROOT).as_posix(),
            "inventory": counts,
            "structural_check": "pass",
        },
    )
    figure = Figure(figsize=(6.0, 2.6), layout="constrained")
    FigureCanvasAgg(figure)
    axes = figure.subplots()
    bars = axes.barh(list(counts), list(counts.values()), color="#256884")
    axes.invert_yaxis()
    axes.set(xlabel="Number of distinct entries", xlim=(0, max(counts.values()) + 2))
    axes.bar_label(bars, padding=4)
    filename = "defensive_registry_inventory.png"
    figure.savefig(figures / filename, dpi=160)
    write_json(
        figures / "figure_registry.json",
        {
            "fig:defensive-registry": {
                "filename": filename,
                "caption": "Counts of distinct entries in the defensive design registry.",
                "alt_text": "Horizontal bars compare counts across the three registry categories.",
            }
        },
    )


if __name__ == "__main__":
    main()
