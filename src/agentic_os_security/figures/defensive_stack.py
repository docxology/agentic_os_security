"""Figure: defensive stack coverage (24 candidates x 8 mitigation classes).

``{#fig:defensive_stack}`` -> ``output/figures/defensive_stack.png``

A heatmap of :data:`agentic_os_security.registry.DEFENSIVE_STACK` (all 24
candidates x all 8 mitigation classes = 192 stance cells, same
``strong | partial | weak | n_a`` vocabulary as the property matrix),
grouped into the 8 candidate categories with a colored side band, and a
right-side marginal coverage bar per mitigation class. Driven entirely by
:data:`DEFENSIVE_STACK` / :func:`defensive_stack_rows`.
"""

from __future__ import annotations

from pathlib import Path

from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch, Rectangle

from ..project_paths import figures_dir
from ..registry import (
    CANDIDATES,
    CATEGORY_VOCAB,
    MITIGATION_CLASSES,
    defensive_stack_rows,
)
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


__all__ = ["generate_defensive_stack"]

_STANCE_ORDER: tuple[str, ...] = ("strong", "partial", "weak", "n_a")
_STANCE_INDEX: dict[str, int] = {stance: i for i, stance in enumerate(_STANCE_ORDER)}

_BAND_X0, _BAND_X1, _BAND_LABEL_X = -1.75, -1.25, -1.50


def generate_defensive_stack(project_root: Path | str) -> Path:
    """Render the 24-candidate by 8-mitigation-class coverage heatmap."""
    root = Path(project_root)
    out = figures_dir(root) / "defensive_stack.png"

    stances: dict[tuple[str, str], str] = {}
    for candidate_id, class_id, stance in defensive_stack_rows():
        stances[(candidate_id, class_id)] = stance

    rows: list[tuple[str, str, str]] = []  # (candidate_id, display_name, category)
    for category in CATEGORY_VOCAB:
        for candidate in CANDIDATES:
            if candidate.category == category:
                rows.append((candidate.candidate_id, ascii_text(candidate.name), category))
    assert len(rows) == len(CANDIDATES), "category grouping lost candidates"

    class_ids = [mc.class_id for mc in MITIGATION_CLASSES]
    class_names = [ascii_text(mc.name) for mc in MITIGATION_CLASSES]

    grid = [[_STANCE_INDEX[stances[(cid, class_id)]] for class_id in class_ids] for cid, _, _ in rows]

    fig = new_figure((7.6, 9.4))
    fig.subplots_adjust(left=0.225, right=0.872, top=0.945, bottom=0.185)
    ax = fig.add_subplot(111)
    ax_marg = fig.add_axes((0.902, 0.185, 0.040, 0.76))

    cmap = ListedColormap([STANCE_COLORS[stance] for stance in _STANCE_ORDER])
    ax.imshow(grid, cmap=cmap, vmin=0, vmax=len(_STANCE_ORDER) - 1, aspect="auto")
    ax.set_xlim(_BAND_X0 - 0.1, len(class_ids) - 0.5)

    # White gridlines between cells; heavier separators between category bands.
    ax.set_xticks([x - 0.5 for x in range(1, len(class_ids))], minor=True)
    ax.set_yticks([y - 0.5 for y in range(1, len(rows))], minor=True)
    ax.grid(which="minor", color="white", linewidth=0.8)
    for i in range(1, len(rows)):
        if rows[i][2] != rows[i - 1][2]:
            ax.axhline(i - 0.5, color="#444444", linewidth=1.6, zorder=5)
    for x in range(1, len(class_ids)):
        ax.axvline(x - 0.5, color="white", linewidth=1.2, zorder=4)
    ax.tick_params(which="minor", length=0)

    for row_idx, (cid, _, _) in enumerate(rows):
        for col_idx, cid_cls in enumerate(class_ids):
            stance = stances[(cid, cid_cls)]
            ax.text(
                col_idx,
                row_idx,
                STANCE_GLYPHS[stance],
                ha="center",
                va="center",
                fontsize=6.4,
                fontweight="bold",
                color=STANCE_GLYPH_COLORS[stance],
            )

    ax.set_xticks(range(len(class_ids)))
    ax.set_xticklabels(class_names, rotation=45, ha="right", fontsize=7.0)
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels([name for _, name, _ in rows], fontsize=7.0)
    ax.tick_params(which="major", length=0)
    for side in ("top", "right", "left", "bottom"):
        ax.spines[side].set_visible(False)

    # Category band strip.
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

    # Right marginal: per-class coverage distribution (counts across 24).
    tallies = {cid_cls: {stance: 0 for stance in _STANCE_ORDER} for cid_cls in class_ids}
    for _cid, cid_cls, stance in defensive_stack_rows():
        tallies[cid_cls][stance] += 1
    ax_marg.set_xlim(0, len(CANDIDATES))
    ax_marg.set_ylim(len(rows), 0)
    ax_marg.set_xticks([])
    ax_marg.set_yticks([])
    for col_idx, cid_cls in enumerate(class_ids):
        left = 0
        for stance in _STANCE_ORDER:
            count = tallies[cid_cls][stance]
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

    # Legend with per-class stance counts, embedded in the lower-left margin.
    total_counts = {
        stance: sum(tallies[cid_cls][stance] for cid_cls in class_ids) for stance in _STANCE_ORDER
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
        bbox_to_anchor=(0.012, 0.014),
        fontsize=6.6,
        title="coverage (192 cells)",
        title_fontsize=6.6,
        frameon=True,
        facecolor="white",
        edgecolor="#AAAAAA",
        framealpha=0.95,
        borderpad=0.6,
        handlelength=1.2,
        handleheight=0.9,
    )

    ax.set_title("Defensive stack: candidate x mitigation class (24 x 8 = 192 cells)", fontsize=9, pad=10)

    return save_figure(fig, out)