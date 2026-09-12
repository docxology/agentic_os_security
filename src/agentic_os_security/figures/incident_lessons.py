"""Figure: 14 documented incidents x 5 boundary-lesson classes.

``{#fig:incidents}`` -> ``output/figures/incident_lessons.png``

A chronological (top = earliest) incident x lesson matrix: one row per
:data:`agentic_os_security.evidence.INCIDENTS` entry in date order, one
column per :data:`agentic_os_security.evidence.LESSON_TAXONOMY` class in
pinned order. Each incident's marker sits in its assigned
``lesson_class`` column; marker color encodes the evidentiary tier of the
incident's citation key (the same five-tier vocabulary as
:data:`agentic_os_security.evidence.TIER_VOCAB`, resolved by lookup into
:data:`agentic_os_security.evidence.SOURCES`). Labels are full-word, the
tier legend is full-word, and rendering is byte-deterministic (see
``_common``): no wall-clock, no pyplot state, DejaVu fonts only.

Row order and marker placement are layout choices, not date claims: dates
plot at month precision where available; year-only incidents ("2026")
plot at mid-year.

v0.5.0 addition: registry figure_001 (section "Threat Model");
``RESULT_NUM_FIGURES`` becomes 11.
"""

from __future__ import annotations

from pathlib import Path

from matplotlib.lines import Line2D

from ..evidence import INCIDENTS, LESSON_TAXONOMY, SOURCES
from ..project_paths import figures_dir
from ._common import OKABE_ITO, ascii_text, new_figure, save_figure

__all__ = ["generate_incidents"]

#: Evidentiary-tier color encoding (shared with the evidence timeline).
_TIER_COLORS: dict[str, str] = {
    "official": OKABE_ITO["blue"],
    "advisory": OKABE_ITO["orange"],
    "incident_report": OKABE_ITO["vermillion"],
    "research": OKABE_ITO["bluish_green"],
    "community": OKABE_ITO["reddish_purple"],
}

#: Full-word legend labels per tier.
_TIER_LABELS: dict[str, str] = {
    "official": "official",
    "advisory": "vendor advisory",
    "incident_report": "incident report",
    "research": "research / assessment",
    "community": "community",
}

_TIER_ORDER: tuple[str, ...] = ("official", "advisory", "incident_report", "research", "community")

#: Neutral fallback for a citation key whose source is not registered.
_FALLBACK_TIER_COLOR = OKABE_ITO["gray"]

#: Month index (0-11) per abbreviated month name used in incident dates.
_MONTH_INDEX: dict[str, int] = {
    "jan": 0, "feb": 1, "mar": 2, "apr": 3, "may": 4, "jun": 5,
    "jul": 6, "aug": 7, "sep": 8, "oct": 9, "nov": 10, "dec": 11,
}


def _tier_color_for(citation_key: str) -> str:
    """Return the tier color for a citation key (gray fallback unknown)."""
    for source in SOURCES:
        if source.key == citation_key:
            color = _TIER_COLORS.get(source.tier)
            if color is not None:
                return color
    return _FALLBACK_TIER_COLOR


def _date_sort_key(date: str) -> tuple[int, int]:
    """Convert an incident date string into a sortable (year, month) key.

    Supported pinned shapes: ``YYYY-MM``, ``YYYY-MM-DD``,
    ``YYYY-MM-DD..DD``, and bare ``YYYY`` (plots at mid-year).
    """
    year = int(date[:4])
    rest = date[5:]
    if not rest:
        return year, 6  # year-only: mid-year plotting position
    month_token = rest[:2]
    if month_token.isdigit():
        return year, int(month_token) - 1
    return year, _MONTH_INDEX.get(month_token.lower(), 0)


def generate_incidents(project_root: Path | str) -> Path:
    """Render the incidents x lesson-classes matrix (registry figure_001)."""
    root = Path(project_root)
    out = figures_dir(root) / "incident_lessons.png"

    taxonomy_ids = list(LESSON_TAXONOMY.keys())
    column_labels = [ascii_text(LESSON_TAXONOMY[lesson_id].name) for lesson_id in taxonomy_ids]

    incidents = sorted(
        INCIDENTS,
        key=lambda incident: (_date_sort_key(incident.date), incident.incident_id),
    )
    unknown_classes = sorted({str(incident.lesson_class) for incident in incidents} - set(taxonomy_ids))
    assert not unknown_classes, f"incidents reference unknown lesson classes: {unknown_classes}"

    n_rows = len(incidents)
    n_cols = len(taxonomy_ids)
    row_step = 1.0

    fig = new_figure((8.4, 6.9))
    fig.subplots_adjust(left=0.315, right=0.985, top=0.795, bottom=0.045)
    ax = fig.add_subplot(111)
    ax.set_xlim(-0.55, n_cols - 0.45)
    ax.set_ylim(n_rows - 0.5, -0.5)  # inverted: row 0 (earliest) at top
    ax.axis("off")

    # Grid lines: one per row and column, light.
    for col_idx in range(n_cols + 1):
        ax.axvline(col_idx - 0.5, color="#E0E0E0", linewidth=0.5, zorder=0)
    for row_idx in range(n_rows + 1):
        ax.axhline(row_idx * row_step - 0.5, color="#E0E0E0", linewidth=0.5, zorder=0)

    # Row labels: incident id (bold) with its date below.
    for row_idx, incident in enumerate(incidents):
        row_y = row_idx * row_step
        ax.text(
            -0.62,
            row_y - 0.10,
            ascii_text(str(incident.incident_id)),
            fontsize=6.4,
            fontweight="bold",
            ha="right",
            va="bottom",
            color="#222222",
        )
        ax.text(
            -0.62,
            row_y + 0.12,
            ascii_text(str(incident.date)),
            fontsize=5.6,
            ha="right",
            va="top",
            color="#777777",
        )

    # Column headers: full-word lesson-class names, below the grid.
    for col_idx, label in enumerate(column_labels):
        ax.text(
            col_idx,
            n_rows - 0.35,
            label,
            fontsize=6.8,
            fontweight="bold",
            ha="center",
            va="top",
            color="#333333",
        )

    # Markers: one per incident, in its lesson-class column, tier-colored.
    for row_idx, incident in enumerate(incidents):
        row_y = row_idx * row_step
        col_idx = taxonomy_ids.index(str(incident.lesson_class))
        color = _tier_color_for(str(incident.citation_key))
        ax.plot(
            [col_idx],
            [row_y],
            marker="o",
            markersize=7.5,
            markerfacecolor=color,
            markeredgecolor="#333333",
            markeredgewidth=0.7,
            linestyle="none",
            zorder=3,
        )

    # Full-word tier legend, above the grid.
    handles = [
        Line2D(
            [0],
            [0],
            marker="o",
            linestyle="none",
            markerfacecolor=_TIER_COLORS[tier],
            markeredgecolor="#333333",
            markeredgewidth=0.7,
            markersize=6.5,
            label=_TIER_LABELS[tier],
        )
        for tier in _TIER_ORDER
    ]
    if any(_tier_color_for(str(incident.citation_key)) == _FALLBACK_TIER_COLOR for incident in incidents):
        handles.append(
            Line2D(
                [0],
                [0],
                marker="o",
                linestyle="none",
                markerfacecolor=_FALLBACK_TIER_COLOR,
                markeredgecolor="#333333",
                markeredgewidth=0.7,
                markersize=6.5,
                label="tier unregistered",
            )
        )
    ax.legend(
        handles=handles,
        loc="lower left",
        bbox_to_anchor=(0.0, 1.06),
        ncol=6,
        fontsize=6.4,
        title="Evidentiary tier",
        title_fontsize=6.4,
        frameon=False,
        columnspacing=1.6,
        handletextpad=0.4,
    )

    ax.set_title(
        "Fourteen documented incidents against five boundary-lesson classes",
        fontsize=9.5,
        pad=52,
    )
    return save_figure(fig, out)
