"""Figure: stated update and support windows for all 24 candidates.

``{#fig:update_windows}`` -> ``output/figures/update_windows.png``

Horizontal support-window bars driven by
:data:`agentic_os_security.registry.UPDATE_WINDOWS`: bar length is the
project's stated fixed support window in months, bars are colored by the
8 pinned candidate categories, and candidates whose project states no
fixed window get a hatched full-span placeholder bar. Policy detail lives
in the registry; the figure carries a pointer note.
"""

from __future__ import annotations

from pathlib import Path

from matplotlib.patches import Patch

from ..project_paths import figures_dir
from ..registry import CANDIDATES, CATEGORY_VOCAB, UPDATE_WINDOWS
from ._common import CATEGORY_COLORS, CATEGORY_LABELS, ascii_text, new_figure, save_figure

__all__ = ["generate_update_windows"]


def generate_update_windows(project_root: Path | str) -> Path:
    """Render the horizontal support-window bars for all 24 candidates."""
    root = Path(project_root)
    out = figures_dir(root) / "update_windows.png"

    # Registry order is already grouped by the pinned category vocabulary.
    rows: list[tuple[str, str, str, int | None]] = []  # (cid, name, category, months)
    for candidate in CANDIDATES:
        window = UPDATE_WINDOWS[candidate.candidate_id]
        rows.append((candidate.candidate_id, ascii_text(candidate.name), candidate.category, window.months))

    fixed = [months for _, _, _, months in rows if months is not None]
    x_max = max(fixed) if fixed else 1
    x_max = ((x_max // 12) + 1) * 12  # round up to a whole year

    n = len(rows)
    fig = new_figure((8.4, 8.2))
    fig.subplots_adjust(left=0.205, right=0.965, top=0.925, bottom=0.245)
    ax = fig.add_subplot(111)

    bar_h = 0.62
    for row_idx, (cid, name, category, months) in enumerate(rows):
        color = CATEGORY_COLORS[category]
        if months is not None:
            ax.barh(
                row_idx,
                months,
                height=bar_h,
                color=color,
                edgecolor="#555555",
                linewidth=0.5,
                zorder=3,
            )
            ax.text(
                months + x_max * 0.008,
                row_idx,
                f"{months} mo",
                fontsize=6.2,
                va="center",
                ha="left",
                color="#333333",
                zorder=4,
            )
        else:
            ax.barh(
                row_idx,
                x_max,
                height=bar_h,
                facecolor="#F0F0F0",
                edgecolor="#888888",
                linewidth=0.5,
                hatch="///",
                zorder=2,
            )
            ax.text(
                x_max * 0.99,
                row_idx,
                "no fixed window stated",
                fontsize=5.8,
                va="center",
                ha="right",
                color="#666666",
                style="italic",
                zorder=4,
            )

    # Category band separators between groups.
    band_positions = {}
    for i, row in enumerate(rows):
        band_positions.setdefault(row[2], []).append(i)
    for i in range(1, n):
        if rows[i][2] != rows[i - 1][2]:
            ax.plot([0, x_max * 1.10], [i - 0.5, i - 0.5], color="#666666", linewidth=1.2, zorder=1)

    ax.set_yticks(range(n))
    ax.set_yticklabels([name for _, name, _, _ in rows], fontsize=7.0)
    ax.set_xlim(0, x_max * 1.10)
    ax.set_ylim(n - 0.4, -0.6)
    ax.set_xlim(0, x_max * 1.10)
    ax.set_xticks(range(0, x_max + 1, 24))
    ax.set_xticklabels([str(m) for m in range(0, x_max + 1, 24)], fontsize=7.0)
    ax.grid(axis="x", which="major", color="#DDDDDD", linewidth=0.5, zorder=0)
    ax.tick_params(length=0)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.set_xlabel("Stated fixed support window (months)", fontsize=7.5)

    handles = [
        Patch(facecolor=CATEGORY_COLORS[category], edgecolor="#555555", linewidth=0.5,
              label=ascii_text(CATEGORY_LABELS[category]))
        for category in CATEGORY_VOCAB
        if category in band_positions
    ]
    handles.append(
        Patch(facecolor="#F0F0F0", edgecolor="#888888", linewidth=0.5, hatch="///",
              label="no fixed window stated")
    )
    fig.legend(
        handles=handles,
        loc="lower left",
        bbox_to_anchor=(0.012, 0.004),
        ncol=2,
        fontsize=6.2,
        title="candidate category",
        title_fontsize=6.4,
        frameon=True,
        facecolor="white",
        edgecolor="#AAAAAA",
        framealpha=0.95,
        borderpad=0.5,
        handlelength=1.4,
        handleheight=1.0,
        columnspacing=1.0,
    )

    ax.set_title(
        "Stated update and support windows (all 24 candidates)",
        fontsize=9,
        pad=10,
    )
    fig.text(
        0.012,
        0.200,
        "Hatched bars: the project documents a rolling or lifecycle-based update policy without a fixed support "
        "window; policy detail in registry.UPDATE_WINDOWS.",
        ha="left",
        va="top",
        fontsize=5.4,
        color="#666666",
    )

    return save_figure(fig, out)