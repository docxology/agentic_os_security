"""Graphical abstract (cover figure) v2 — NOT a manuscript figure.

``output/figures/graphical_abstract.png`` — a tall portrait cover layout
(9.6 x 11.8 in @ 300 dpi) with no ``{#fig:...}`` label. It stays out of the
manuscript figure registry and out of ``RESULT_NUM_FIGURES``; the cover
embed scales it by the title-page height fraction.

v2 layout (top to bottom, three side-by-side columns, thesis band):
1. Title strip: thesis headline + the 24 x 9 evaluation scope in words.
2. Left column: the two failure paths — exploitation of the
   operating-system boundary by offensive agents, and authorized misuse by
   sanctioned agents.
3. Middle column: the nine evaluation properties, each with a mini stacked
   bar of the 24-candidate stance distribution computed from
   :func:`agentic_os_security.registry.matrix_rows`.
4. Right column: the eight candidate classes as horizontal stacked bars
   with full-word counts ("7 strong / 34 partial / 22 weak" style) summed
   over the class's candidates — no letter codes anywhere on the figure.
5. Bottom band: the composition thesis — containment + reproducible
   operations + boot integrity + capability-limited agents as one design
   target.

Typography floor: 15.5 pt on the canvas (>= 11 pt effective at the cover's
0.72 height fraction). Same byte-determinism contract as every figure
generator: fixed fonts, no wall-clock, no pyplot state, metadata stripped
on save.
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
    ascii_text,
    new_figure,
    save_figure,
)

__all__ = ["generate_graphical_abstract"]

_EXPLOIT = OKABE_ITO["vermillion"]
_MISUSE = OKABE_ITO["orange"]
_ACCENT = OKABE_ITO["blue"]
_COMPOSE = OKABE_ITO["bluish_green"]
_INK = "#222222"
_SOFT = "#555555"

#: On-canvas typography floor: 15.5 pt keeps every glyph at >= 11 pt
#: effective after the title page scales the cover by height fraction 0.72.
_BODY = 15.5
_BOLD = 17.0
_HEADER = 15.5

_CANVAS_W = 9.6
_CANVAS_H = 11.8

_STANCE_ORDER = ("strong", "partial", "weak", "n_a")
_STANCE_WORDS = {
    "strong": "strong",
    "partial": "partial",
    "weak": "weak",
    "n_a": "not assessed",
}


def _stance_tallies() -> tuple[dict[str, Counter], dict[str, Counter]]:
    """Per-property and per-category stance tallies from the matrix rows."""
    category_of = {candidate.candidate_id: candidate.category for candidate in CANDIDATES}
    per_property: dict[str, Counter] = {prop.property_id: Counter() for prop in PROPERTIES}
    per_category: dict[str, Counter] = {}
    for candidate_id, property_id, stance in matrix_rows():
        per_property[property_id][stance] += 1
        per_category.setdefault(category_of[candidate_id], Counter())[stance] += 1
    return per_property, per_category


def _counts_lines(tallies: Counter) -> list[str]:
    """Full-word stance counts, e.g. ``["7 strong / 34 partial / 22 weak"]``.

    Zero-count stances are omitted; ``n_a`` renders as "not assessed".
    Segments pack greedily into at most two lines that fit the class
    column (36 characters at the 15.5 pt body size).
    """
    parts = [
        f"{tallies[stance]} {_STANCE_WORDS[stance]}"
        for stance in ("strong", "partial", "weak")
        if tallies[stance]
    ]
    if tallies["n_a"]:
        parts.append(f"{tallies['n_a']} not assessed")
    lines: list[str] = []
    current = ""
    for part in parts:
        candidate = f"{current} / {part}" if current else part
        if len(candidate) <= 36 or not current:
            current = candidate
        else:
            lines.append(current)
            current = part
    if current:
        lines.append(current)
    return lines


def _wrap_name(name: str, width: int = 18) -> list[str]:
    """Greedy word wrap for a property name (at most three lines)."""
    words = ascii_text(name).split()
    display: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}" if current else word
        if len(candidate) <= width or not current:
            current = candidate
        else:
            display.append(current)
            current = word
    if current:
        display.append(current)
    return display


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


def _arrow(ax, x0: float, y0: float, x1: float, y1: float, color: str, lw: float = 2.6) -> None:
    ax.add_patch(
        FancyArrowPatch(
            (x0, y0),
            (x1, y1),
            arrowstyle="-|>",
            mutation_scale=26,
            linewidth=lw,
            color=color,
            shrinkA=0,
            shrinkB=0,
            zorder=5,
        )
    )


def _stacked_bar(
    ax,
    x: float,
    y: float,
    w: float,
    h: float,
    tallies: Counter,
) -> None:
    """Horizontal stance bar; segment widths proportional to the counts."""
    total = sum(tallies.values()) or 1
    cursor = x
    for stance in _STANCE_ORDER:
        seg = w * tallies[stance] / total
        if seg <= 0:
            continue
        ax.add_patch(
            Rectangle(
                (cursor, y),
                seg,
                h,
                facecolor=STANCE_COLORS[stance],
                edgecolor="white",
                linewidth=0.5,
                zorder=3,
            )
        )
        cursor += seg


def generate_graphical_abstract(project_root: Path | str) -> Path:
    """Render the tall portrait cover graphical abstract at 300 dpi."""
    root = Path(project_root)
    out = figures_dir(root) / "graphical_abstract.png"

    per_property, per_category = _stance_tallies()
    n_candidates = len(CANDIDATES)
    n_properties = len(PROPERTIES)
    properties = list(PROPERTIES)
    categories = [cat for cat in CATEGORY_LABELS if cat in per_category]

    # Canvas: 9.6 x 11.8 inches, absolute inch coordinates.
    fig = new_figure((_CANVAS_W, _CANVAS_H))
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
    ax = fig.add_axes((0, 0, 1, 1))
    ax.set_xlim(0, _CANVAS_W)
    ax.set_ylim(0, _CANVAS_H)
    ax.axis("off")

    # --- Title strip. ---
    ax.text(
        _CANVAS_W / 2,
        11.40,
        ascii_text("Securing AI agents at the operating-system boundary"),
        fontsize=21.0,
        fontweight="bold",
        ha="center",
        va="center",
        color=_INK,
    )
    ax.text(
        _CANVAS_W / 2,
        11.04,
        ascii_text("the composition that matters"),
        fontsize=21.0,
        fontweight="bold",
        ha="center",
        va="center",
        color=_INK,
    )
    ax.text(
        _CANVAS_W / 2,
        10.70,
        ascii_text(f"{n_candidates} operating systems x {n_properties} properties"),
        fontsize=_BODY,
        ha="center",
        va="center",
        color=_SOFT,
    )
    ax.text(
        _CANVAS_W / 2,
        10.42,
        ascii_text("two failure paths, one composed defense"),
        fontsize=_BODY,
        ha="center",
        va="center",
        color=_SOFT,
    )

    # Column frame: content zone y 9.86 (top) -> 2.02 (bottom).
    zone_top = 9.86
    zone_bottom = 2.02

    # Column headers.
    ax.text(1.23, 10.10, "FAILURE PATHS", fontsize=_HEADER, fontweight="bold", ha="center", va="center", color=_SOFT)
    ax.text(3.88, 10.10, "NINE PROPERTIES", fontsize=_HEADER, fontweight="bold", ha="center", va="center", color=_SOFT)
    ax.text(7.40, 10.10, "EIGHT CANDIDATE CLASSES", fontsize=_HEADER, fontweight="bold", ha="center", va="center", color=_SOFT)

    # --- Left column (x 0.28 - 2.18): the two failure paths. ---
    _chip(ax, 0.28, 7.30, 1.90, 2.30, "#FBE9E4", _EXPLOIT, lw=2.0)
    ax.text(1.23, 9.22, "Exploitation", fontsize=_BOLD, fontweight="bold", ha="center", va="center", color=_INK)
    ax.text(
        1.23,
        8.25,
        "Offensive agents\nattack the\noperating-system\nboundary",
        fontsize=_BODY,
        ha="center",
        va="center",
        color=_INK,
        linespacing=1.25,
    )

    _chip(ax, 0.28, 4.60, 1.90, 2.30, "#FCF2E4", _MISUSE, lw=2.0)
    ax.text(
        1.23,
        6.52,
        "Authorized\nmisuse",
        fontsize=_BOLD,
        fontweight="bold",
        ha="center",
        va="center",
        color=_INK,
        linespacing=1.2,
    )
    ax.text(
        1.23,
        5.55,
        "Sanctioned\nagents exceed\nintent from\ninside the\nboundary",
        fontsize=_BODY,
        ha="center",
        va="center",
        color=_INK,
        linespacing=1.25,
    )

    ax.text(
        1.23,
        3.40,
        "the same nine\nproperties\nscore both\npaths",
        fontsize=_BODY,
        style="italic",
        ha="center",
        va="center",
        color=_SOFT,
        linespacing=1.35,
    )

    # --- Middle column (x 2.58 - 5.18): the nine properties. ---
    col_b_x, col_b_w = 2.58, 2.60
    pitch_b = 0.83
    for idx, prop in enumerate(properties):
        row_top = zone_top - idx * pitch_b
        for line_idx, line in enumerate(_wrap_name(prop.name)):
            ax.text(
                col_b_x,
                row_top - 0.16 - line_idx * 0.24,
                line,
                fontsize=_BODY,
                fontweight="bold",
                ha="left",
                va="center",
                color=_INK,
            )
        _stacked_bar(ax, col_b_x, row_top - 0.72, col_b_w - 0.24, 0.15, per_property[prop.property_id])

    # --- Right column (x 5.48 - 9.32): candidate classes, full-word counts. ---
    col_c_x, col_c_w = 5.48, 3.84
    pitch_c = 0.98
    for idx, category in enumerate(categories):
        row_top = zone_top - idx * pitch_c
        label = ascii_text(CATEGORY_LABELS[category])
        tallies = per_category[category]
        ax.add_patch(
            Rectangle(
                (col_c_x, row_top - 0.28),
                0.26,
                0.26,
                facecolor=CATEGORY_COLORS[category],
                edgecolor="#888888",
                linewidth=0.6,
                zorder=3,
            )
        )
        ax.text(col_c_x + 0.40, row_top - 0.15, label, fontsize=_BODY, fontweight="bold", ha="left", va="center", color=_INK)
        count_lines = _counts_lines(tallies)
        if len(count_lines) == 1:
            ax.text(
                col_c_x + 0.40,
                row_top - 0.42,
                count_lines[0],
                fontsize=_BODY,
                ha="left",
                va="center",
                color=_SOFT,
            )
        else:
            ax.text(
                col_c_x + 0.40,
                row_top - 0.36,
                count_lines[0],
                fontsize=_BODY,
                ha="left",
                va="center",
                color=_SOFT,
            )
            ax.text(
                col_c_x + 0.40,
                row_top - 0.58,
                count_lines[1],
                fontsize=_BODY,
                ha="left",
                va="center",
                color=_SOFT,
            )
        _stacked_bar(ax, col_c_x, row_top - 0.88, col_c_w, 0.14, tallies)

    # --- Flow arrows: failure paths -> properties -> classes -> thesis. ---
    _arrow(ax, 2.20, 8.40, 2.54, 8.10, _EXPLOIT)
    _arrow(ax, 2.20, 5.75, 2.54, 6.05, _MISUSE)
    _arrow(ax, 5.20, 5.90, 5.44, 5.90, _ACCENT)
    _arrow(ax, 7.40, zone_bottom, 7.40, 1.78, _COMPOSE)
    # --- Stance color legend (full-word labels, no letter codes). ---
    legend_items = (
        ("strong", "strong"),
        ("partial", "partial"),
        ("weak", "weak"),
        ("n_a", "not assessed"),
    )
    legend_x = 0.90
    for stance_key, label in legend_items:
        ax.add_patch(
            Rectangle(
                (legend_x, 1.80),
                0.30,
                0.18,
                facecolor=STANCE_COLORS[stance_key],
                edgecolor=_SOFT,
                linewidth=0.6,
            )
        )
        ax.text(
            legend_x + 0.42,
            1.89,
            ascii_text(label),
            fontsize=12.5,
            ha="left",
            va="center",
            color=_INK,
        )
        legend_x += 1.52

    # --- Bottom band: the composition thesis (y 0.30 - 1.72, full width). ---
    _chip(ax, 0.28, 0.30, 9.04, 1.42, "#E9F5F0", _COMPOSE, lw=2.0)
    ax.text(
        _CANVAS_W / 2,
        1.42,
        "THE COMPOSITION THESIS",
        fontsize=_HEADER,
        fontweight="bold",
        ha="center",
        va="center",
        color=_COMPOSE,
    )
    ax.text(
        _CANVAS_W / 2,
        1.02,
        ascii_text("Qubes-like containment + Nix-like reproducibility + verified boot"),
        fontsize=16.0,
        fontweight="bold",
        ha="center",
        va="center",
        color=_INK,
    )
    ax.text(
        _CANVAS_W / 2,
        0.66,
        ascii_text("+ capability-limited agents = one design target"),
        fontsize=16.0,
        fontweight="bold",
        ha="center",
        va="center",
        color=_INK,
    )

    return save_figure(fig, out)
