"""Figure: candidate x property stance matrix (24 x 9 = 216 cells).

``{#fig:property_matrix}`` -> ``output/figures/property_matrix.png``

Publication-grade layout (v0.2.0): the 24 candidate rows are grouped into
the 8 pinned candidate categories (colored side band with rotated category
labels and thin category separator lines), a right-side marginal
stance-distribution bar per property, and a legend with stance counts
embedded inside the plot. A v0.6.0 lower-left inset panel adds the
per-category stance distribution (8 stacked mini-bars in registry order,
full-word counts beside each bar). Driven entirely by
:func:`agentic_os_security.registry.matrix_rows`; the qualitative color
encoding (Okabe-Ito) mirrors the stance vocabulary
``strong | partial | weak | n_a``.
"""

from __future__ import annotations

from pathlib import Path

from matplotlib.figure import Figure
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch, Rectangle

from ..project_paths import figures_dir
from ..registry import CANDIDATES, CATEGORY_VOCAB, PROPERTIES, matrix_rows
from ._common import (
    CATEGORY_COLORS,
    CATEGORY_LABELS,
    STANCE_COLORS,
    STANCE_GLYPHS,
    STANCE_GLYPH_COLORS,
    ascii_text,
    new_figure,
    save_figure,
)

_BAND_LABEL_OVERRIDES: dict[str, str] = {
    "compartmentalized": "Comp.",
    "reproducible": "Repro.",
    "high_assurance": "High\nassur.",
    "offensive_toolkit": "Off.\ntoolkit",
}


__all__ = ["generate_property_matrix"]

_STANCE_ORDER: tuple[str, ...] = ("strong", "partial", "weak", "n_a")
_STANCE_INDEX: dict[str, int] = {stance: i for i, stance in enumerate(_STANCE_ORDER)}
_STANCE_WORDS: dict[str, str] = {
    "strong": "strong",
    "partial": "partial",
    "weak": "weak",
    "n_a": "not assessed",
}

#: Lower-left inset panel (figure fractions): per-category stance
#: distribution — 8 stacked mini-bars in registry order with full-word
#: counts beside each bar, placed in the whitespace above the stance
#: legend and left of the rotated property labels.

_PANEL_RECT = (0.012, 0.098, 0.262, 0.116)
_PANEL_NAME_W = 0.31  # axes-fraction column reserved for category names
_PANEL_BAR_W = 0.13  # axes-fraction width of each mini-bar
_BAND_X0, _BAND_X1, _BAND_LABEL_X = -1.85, -1.35, -1.60

def _category_counts_lines(counts: dict[str, int]) -> str:
    """Full-word stance counts, e.g. ``"2 strong/7 partial"``.

    Zero-count stances are omitted; ``n_a`` renders as ``not assessed``
    on its own line (only the high-assurance category carries n_a cells).
    """
    lines = [
        "/".join(
            f"{counts[stance]} {_STANCE_WORDS[stance]}"
            for stance in _STANCE_ORDER[:3]
            if counts[stance]
        )
    ]
    if counts["n_a"]:
        lines.append(f"{counts['n_a']} {_STANCE_WORDS['n_a']}")
    return "\n".join(line for line in lines if line)


def _add_category_stance_panel(
    fig: Figure,
    rows: list[tuple[str, str, str]],
    stances: dict[tuple[str, str], str],
    property_ids: list[str],
) -> None:
    """Draw the lower-left per-category stance-distribution inset panel.

    One stacked mini-bar per candidate category in registry order
    (segment colors = ``STANCE_COLORS``), with the category name and its
    full-word stance counts beside the bar.
    """
    tallies: dict[str, dict[str, int]] = {
        category: {stance: 0 for stance in _STANCE_ORDER} for category in CATEGORY_VOCAB
    }
    for cid, _name, category in rows:
        for pid in property_ids:
            tallies[category][stances[(cid, pid)]] += 1

    ax_panel = fig.add_axes(_PANEL_RECT)
    ax_panel.patch.set_visible(False)  # never mask the rotated property labels
    ax_panel.set_xlim(0, 1)
    ax_panel.set_ylim(0, len(CATEGORY_VOCAB))
    ax_panel.invert_yaxis()
    ax_panel.set_xticks([])
    ax_panel.set_yticks([])
    ax_panel.tick_params(length=0)
    for side in ax_panel.spines.values():
        side.set_visible(False)

    for row, category in enumerate(CATEGORY_VOCAB):
        counts = tallies[category]
        y_mid = row + 0.5
        ax_panel.text(
            0.0,
            y_mid,
            ascii_text(CATEGORY_LABELS[category]),
            fontsize=4.8,
            fontweight="bold",
            ha="left",
            va="center",
            color="#1A1A1A",
        )
        total = sum(counts.values()) or 1
        left = _PANEL_NAME_W
        for stance in _STANCE_ORDER:
            count = counts[stance]
            if not count:
                continue
            width = _PANEL_BAR_W * count / total
            ax_panel.add_patch(
                Rectangle(
                    (left, row + 0.24),
                    width,
                    0.52,
                    facecolor=STANCE_COLORS[stance],
                    edgecolor="white",
                    linewidth=0.3,
                )
            )
            left += width
        ax_panel.text(
            _PANEL_NAME_W + _PANEL_BAR_W + 0.015,
            y_mid,
            _category_counts_lines(counts),
            fontsize=4.3,
            ha="left",
            va="center",
            color="#333333",
        )


def generate_property_matrix(project_root: Path | str) -> Path:
    """Render the 24-candidate by 9-property stance heatmap with category bands."""
    root = Path(project_root)
    out = figures_dir(root) / "property_matrix.png"

    stances: dict[tuple[str, str], str] = {}
    for candidate_id, property_id, stance in matrix_rows():
        stances[(candidate_id, property_id)] = stance

    # Rows grouped by the pinned category order, candidates in registry order
    # within each band. Each entry: (candidate_id, display_name, category).
    rows: list[tuple[str, str, str]] = []
    for category in CATEGORY_VOCAB:
        for candidate in CANDIDATES:
            if candidate.category == category:
                rows.append((candidate.candidate_id, ascii_text(candidate.name), category))
    assert len(rows) == len(CANDIDATES), "category grouping lost candidates"

    property_ids = [prop.property_id for prop in PROPERTIES]
    property_names = [ascii_text(prop.name) for prop in PROPERTIES]

    grid = [[_STANCE_INDEX[stances[(cid, pid)]] for pid in property_ids] for cid, _, _ in rows]

    fig = new_figure((8.2, 9.4))
    fig.subplots_adjust(left=0.222, right=0.872, top=0.945, bottom=0.225)
    ax = fig.add_subplot(111)
    ax_marg = fig.add_axes((0.902, 0.225, 0.040, 0.72))  # right marginal axis

    cmap = ListedColormap([STANCE_COLORS[stance] for stance in _STANCE_ORDER])
    ax.imshow(grid, cmap=cmap, vmin=0, vmax=len(_STANCE_ORDER) - 1, aspect="auto")
    # Widen the x range so the category band strip fits left of column 0.
    ax.set_xlim(_BAND_X0 - 0.1, len(property_ids) - 0.5)

    # White gridlines between cells; heavier separators between category bands.
    ax.set_xticks([x - 0.5 for x in range(1, len(property_ids))], minor=True)
    ax.set_yticks([y - 0.5 for y in range(1, len(rows))], minor=True)
    ax.grid(which="minor", color="white", linewidth=0.8)
    for i in range(1, len(rows)):
        if rows[i][2] != rows[i - 1][2]:
            ax.axhline(i - 0.5, color="#444444", linewidth=1.6, zorder=5)
    for x in range(1, len(property_ids)):
        ax.axvline(x - 0.5, color="white", linewidth=1.2, zorder=4)
    ax.tick_params(which="minor", length=0)

    # Cell glyphs (kept legible at 9pt-document scale).
    for row_idx, (cid, _, _) in enumerate(rows):
        for col_idx, pid in enumerate(property_ids):
            stance = stances[(cid, pid)]
            ax.text(
                col_idx,
                row_idx,
                STANCE_GLYPHS[stance],
                ha="center",
                va="center",
                fontsize=6.2,
                fontweight="bold",
                color=STANCE_GLYPH_COLORS[stance],
            )

    ax.set_xticks(range(len(property_ids)))
    ax.set_xticklabels(property_names, rotation=45, ha="right", fontsize=7.2)
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels([name for _, name, _ in rows], fontsize=7.0)
    ax.tick_params(which="major", length=0)
    for side in ("top", "right", "left", "bottom"):
        ax.spines[side].set_visible(False)

    # Category band strip: one colored span per category with a rotated label.
    for category in CATEGORY_VOCAB:
        member_positions = [i for i, row in enumerate(rows) if row[2] == category]
        if not member_positions:
            continue
        start, end = member_positions[0], member_positions[-1]
        ax.add_patch(
            Rectangle(
                (_BAND_X0, start - 0.5),
                _BAND_X1 - _BAND_X0,
                end - start + 1,
                facecolor=CATEGORY_COLORS[category],
                edgecolor="white",
                linewidth=0.8,
                clip_on=False,
            )
        )
        ax.text(
            _BAND_LABEL_X,
            (start + end) / 2,
            _BAND_LABEL_OVERRIDES.get(category, ascii_text(CATEGORY_LABELS[category])),
            rotation=90,
            ha="center",
            va="center",
            fontsize=5.4,
            fontweight="bold",
            color="#1A1A1A",
            linespacing=0.9,
            zorder=6,
            clip_on=False,
        )

    # Right marginal: stance distribution per property (counts across 24).
    tallies = {pid: {stance: 0 for stance in _STANCE_ORDER} for pid in property_ids}
    for _cid, pid, stance in matrix_rows():
        tallies[pid][stance] += 1
    ax_marg.set_xlim(0, len(CANDIDATES))
    ax_marg.set_ylim(len(rows), 0)
    ax_marg.set_xticks([])
    ax_marg.set_yticks([])
    for col_idx, pid in enumerate(property_ids):
        left = 0
        for stance in _STANCE_ORDER:
            count = tallies[pid][stance]
            if count:
                ax_marg.barh(
                    col_idx,
                    count,
                    left=left,
                    height=0.78,
                    color=STANCE_COLORS[stance],
                    edgecolor="white",
                    linewidth=0.4,
                )
                left += count
    ax_marg.set_title("n=24", fontsize=6.0, pad=4)
    for side in ("top", "right", "left"):
        ax_marg.spines[side].set_visible(False)
    ax_marg.spines["bottom"].set_color("#888888")

    # Lower-left inset: per-category stance distribution (v0.6.0), placed
    # in the whitespace above the legend, left of the rotated labels.
    _add_category_stance_panel(fig, rows, stances, property_ids)
    # Legend with stance counts, embedded in the lower-left margin (empty
    # area below the category band strip).
    total_counts = {
        stance: sum(tallies[pid][stance] for pid in property_ids) for stance in _STANCE_ORDER
    }
    handles = [
        Patch(
            facecolor=STANCE_COLORS[stance],
            edgecolor="#777777",
            linewidth=0.4,
            label=f"{stance} ({total_counts[stance]})",
        )
        for stance in _STANCE_ORDER
    ]
    fig.legend(
        handles=handles,
        loc="lower left",
        bbox_to_anchor=(0.012, 0.018),
        fontsize=6.6,
        title="stance (216 cells)",
        title_fontsize=6.6,
        frameon=True,
        facecolor="white",
        edgecolor="#AAAAAA",
        framealpha=0.95,
        borderpad=0.6,
        handlelength=1.2,
        handleheight=0.9,
    )

    ax.set_title("Candidate x property stance matrix (24 x 9 = 216 cells)", fontsize=9, pad=10)

    return save_figure(fig, out)