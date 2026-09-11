"""Graphical abstract (cover figure) — NOT a manuscript figure.

``output/figures/graphical_abstract.png`` — a wide 16:9 cover layout with no
``{#fig:...}`` label. It stays out of the manuscript figure registry and out
of ``RESULT_NUM_FIGURES``; the cover embed references the PNG path directly.

Layout (left to right, bottom band):
1. Left: the two failure paths — exploitation of the OS boundary by
   offensive agents, and authorized misuse by sanctioned agents.
2. Center: the nine evaluation properties as chips; each chip carries a
   mini stacked bar of the 24-candidate stance distribution computed from
   :func:`agentic_os_security.registry.matrix_rows`.
3. Right: the eight candidate classes with stance glyph counts summed over
   the class's candidates.
4. Bottom band: the composition thesis — containment + reproducible
   operations + boot integrity + capability-limited agents as one design
   target.

Same byte-determinism contract as every figure generator: fixed fonts, no
wall-clock, no pyplot state, metadata stripped on save.
"""

from __future__ import annotations

from collections import Counter
from pathlib import Path

from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle

from ..project_paths import figures_dir
from ..registry import CANDIDATES, PROPERTIES, matrix_rows
from ._common import (
    CATEGORY_COLORS,
    CATEGORY_LABELS,
    OKABE_ITO,
    STANCE_COLORS,
    STANCE_GLYPHS,
    ascii_text,
    new_figure,
    save_figure,
    wrap_ascii,
)

__all__ = ["generate_graphical_abstract"]

_EXPLOIT = OKABE_ITO["vermillion"]
_MISUSE = OKABE_ITO["orange"]
_ACCENT = OKABE_ITO["blue"]
_COMPOSE = OKABE_ITO["bluish_green"]
_INK = "#222222"
_SOFT = "#555555"

_THESIS_PARTS = (
    "Qubes-like containment",
    "Nix-like reproducibility",
    "Boot integrity",
    "Capability-limited agents",
)

_STANCE_ORDER = ("strong", "partial", "weak", "n_a")


def _stance_tallies() -> tuple[dict[str, Counter], dict[str, Counter]]:
    """Per-property and per-category stance tallies from the matrix rows."""
    category_of = {candidate.candidate_id: candidate.category for candidate in CANDIDATES}
    per_property: dict[str, Counter] = {prop.property_id: Counter() for prop in PROPERTIES}
    per_category: dict[str, Counter] = {}
    for candidate_id, property_id, stance in matrix_rows():
        per_property[property_id][stance] += 1
        per_category.setdefault(category_of[candidate_id], Counter())[stance] += 1
    return per_property, per_category


def _chip(
    ax,
    x: float,
    y: float,
    w: float,
    h: float,
    face: str,
    edge: str,
    lw: float = 1.0,
    radius: float = 0.1,
) -> None:
    ax.add_patch(
        FancyBboxPatch(
            (x, y),
            w,
            h,
            boxstyle=f"round,pad=0,rounding_size={radius}",
            facecolor=face,
            edgecolor=edge,
            linewidth=lw,
            zorder=2,
        )
    )


def _arrow(ax, x0: float, y0: float, x1: float, y1: float, color: str, lw: float = 2.2) -> None:
    ax.add_patch(
        FancyArrowPatch(
            (x0, y0),
            (x1, y1),
            arrowstyle="-|>",
            mutation_scale=22,
            linewidth=lw,
            color=color,
            shrinkA=0,
            shrinkB=0,
            zorder=5,
        )
    )


def generate_graphical_abstract(project_root: Path | str) -> Path:
    """Render the 16:9 cover graphical abstract at 300 dpi."""
    root = Path(project_root)
    out = figures_dir(root) / "graphical_abstract.png"

    per_property, per_category = _stance_tallies()
    n_candidates = len(CANDIDATES)
    properties = list(PROPERTIES)

    # Canvas: 12.8 x 7.2 inches, absolute inch coordinates.
    fig = new_figure((12.8, 7.2))
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
    ax = fig.add_axes((0, 0, 1, 1))
    ax.set_xlim(0, 12.8)
    ax.set_ylim(0, 7.2)
    ax.axis("off")

    # --- Title band. ---
    ax.text(
        6.4,
        6.88,
        ascii_text("Securing AI agents at the operating-system boundary: the composition that matters"),
        fontsize=18.5,
        fontweight="bold",
        ha="center",
        va="center",
        color=_INK,
    )
    ax.text(
        6.4,
        6.58,
        ascii_text(f"{n_candidates} operating systems x 9 properties - two failure paths, one composed defense"),
        fontsize=11.5,
        ha="center",
        va="center",
        color=_SOFT,
    )

    # --- Left panel: the two failure paths (x 0.28 - 2.80). ---
    ax.text(1.54, 6.30, "TWO FAILURE PATHS", fontsize=11, fontweight="bold", ha="center", va="center", color=_SOFT)

    _chip(ax, 0.28, 4.42, 2.52, 1.30, "#FBE9E4", _EXPLOIT, lw=1.8)
    ax.text(1.54, 5.42, "Exploitation", fontsize=14.5, fontweight="bold", ha="center", va="center", color=_INK)
    ax.text(
        1.54,
        4.88,
        wrap_ascii("Offensive AI agents attack the OS boundary itself", width=30, max_lines=3),
        fontsize=10,
        ha="center",
        va="center",
        color=_INK,
        linespacing=1.35,
    )

    _chip(ax, 0.28, 2.78, 2.52, 1.30, "#FCF2E4", _MISUSE, lw=1.8)
    ax.text(1.54, 3.78, "Authorized misuse", fontsize=14.5, fontweight="bold", ha="center", va="center", color=_INK)
    ax.text(
        1.54,
        3.24,
        wrap_ascii("Sanctioned agents exceed intent from inside the boundary", width=30, max_lines=3),
        fontsize=10,
        ha="center",
        va="center",
        color=_INK,
        linespacing=1.35,
    )

    ax.text(
        1.54,
        2.20,
        "the same 9 properties\nscore both paths",
        fontsize=9.5,
        style="italic",
        ha="center",
        va="center",
        color=_SOFT,
        linespacing=1.4,
    )
    ax.text(
        1.54,
        1.78,
        "S = strong - P = partial - W = weak",
        fontsize=9,
        style="italic",
        ha="center",
        va="center",
        color=_SOFT,
    )

    # --- Center panel: the nine property chips, 3 x 3 (x 3.20 - 8.10). ---
    ax.text(5.65, 6.30, "NINE PROPERTIES", fontsize=11, fontweight="bold", ha="center", va="center", color=_SOFT)
    chip_w, chip_h = 1.48, 1.06
    gap_x, gap_y = 0.23, 0.24
    grid_x0 = 5.65 - (3 * chip_w + 2 * gap_x) / 2  # 3.20
    grid_y0 = 2.42  # bottom row base
    for idx, prop in enumerate(properties):
        col, row = idx % 3, idx // 3
        cx = grid_x0 + col * (chip_w + gap_x)
        cy = grid_y0 + (2 - row) * (chip_h + gap_y)
        _chip(ax, cx, cy, chip_w, chip_h, "#F5F8FB", _ACCENT, lw=1.3)
        ax.text(
            cx + chip_w / 2,
            cy + chip_h - 0.33,
            wrap_ascii(ascii_text(prop.name), width=17, max_lines=2),
            fontsize=10,
            fontweight="bold",
            ha="center",
            va="center",
            color=_INK,
            linespacing=1.15,
        )
        # Mini stacked stance bar across the 24 candidates.
        tallies = per_property[prop.property_id]
        total = sum(tallies.values()) or 1
        bar_x, bar_y, bar_h = cx + 0.12, cy + 0.17, 0.17
        bar_w = chip_w - 0.24
        x_cursor = bar_x
        for stance in _STANCE_ORDER:
            seg = bar_w * tallies[stance] / total
            ax.add_patch(
                Rectangle(
                    (x_cursor, bar_y),
                    seg,
                    bar_h,
                    facecolor=STANCE_COLORS[stance],
                    edgecolor="white",
                    linewidth=0.4,
                    zorder=3,
                )
            )
            x_cursor += seg

    # --- Right panel: candidate classes with stance glyphs (x 8.65 - 12.55). ---
    ax.text(10.60, 6.30, "CANDIDATE CLASSES", fontsize=11, fontweight="bold", ha="center", va="center", color=_SOFT)
    categories = [cat for cat in CATEGORY_LABELS if cat in per_category]
    row_h = 0.56
    y_cursor = 5.55
    for category in categories:
        label = ascii_text(CATEGORY_LABELS[category])
        tallies = per_category[category]
        glyphs = "  ".join(
            f"{STANCE_GLYPHS[stance]}{tallies[stance]}"
            for stance in ("strong", "partial", "weak")
        )
        ax.add_patch(
            Rectangle(
                (8.68, y_cursor - 0.13),
                0.26,
                0.26,
                facecolor=CATEGORY_COLORS[category],
                edgecolor="#888888",
                linewidth=0.5,
                zorder=3,
            )
        )
        ax.text(9.06, y_cursor, label, fontsize=11, ha="left", va="center", color=_INK)
        ax.text(
            11.16,
            y_cursor,
            glyphs,
            fontsize=10.5,
            fontweight="bold",
            ha="left",
            va="center",
            color=_SOFT,
        )
        y_cursor -= row_h
    # --- Flow arrows: failure paths -> properties -> classes -> thesis. ---
    _arrow(ax, 2.86, 4.55, 3.10, 4.10, _EXPLOIT)
    _arrow(ax, 2.86, 3.35, 3.10, 3.80, _MISUSE)
    _arrow(ax, 8.18, 4.00, 8.60, 4.00, _ACCENT)
    _arrow(ax, 5.65, 2.38, 5.65, 1.42, _COMPOSE)

    # --- Bottom band: the composition thesis (y 0.28 - 1.34). ---
    _chip(ax, 0.28, 0.28, 12.24, 1.06, "#E9F5F0", _COMPOSE, lw=1.8)
    ax.text(
        1.22,
        0.81,
        "THE\nCOMPOSITION",
        fontsize=10.5,
        fontweight="bold",
        ha="center",
        va="center",
        color=_COMPOSE,
        linespacing=1.3,
    )
    part_w, part_h = 1.94, 0.62
    x_cursor = 2.05
    for i, part in enumerate(_THESIS_PARTS):
        _chip(ax, x_cursor, 0.50, part_w, part_h, "white", _COMPOSE, lw=1.1)
        ax.text(
            x_cursor + part_w / 2,
            0.81,
            wrap_ascii(ascii_text(part), width=15, max_lines=2),
            fontsize=10.5,
            fontweight="bold",
            ha="center",
            va="center",
            color=_INK,
            linespacing=1.15,
        )
        if i < len(_THESIS_PARTS) - 1:
            ax.text(
                x_cursor + part_w + 0.14,
                0.81,
                "+",
                fontsize=16,
                fontweight="bold",
                ha="center",
                va="center",
                color=_COMPOSE,
            )
        x_cursor += part_w + 0.28
    ax.text(
        x_cursor + 0.12,
        0.81,
        "=",
        fontsize=16,
        fontweight="bold",
        ha="center",
        va="center",
        color=_COMPOSE,
    )
    ax.text(
        x_cursor + 1.10,
        0.81,
        "one design\ntarget",
        fontsize=11.5,
        fontweight="bold",
        ha="center",
        va="center",
        color=_INK,
        linespacing=1.25,
    )

    return save_figure(fig, out)
