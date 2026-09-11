"""Figure: candidate x property stance matrix (24 x 9 = 216 cells).

``{#fig:property_matrix}`` -> ``output/figures/property_matrix.png``

Driven entirely by :func:`agentic_os_security.registry.matrix_rows`; the
qualitative color encoding (Okabe-Ito) mirrors the stance vocabulary
``strong | partial | weak | n_a`` with a legend.
"""

from __future__ import annotations

from pathlib import Path

from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch

from ..project_paths import figures_dir
from ..registry import CANDIDATES, PROPERTIES, matrix_rows
from ._common import STANCE_COLORS, ascii_text, new_figure, save_figure

__all__ = ["generate_property_matrix"]

_STANCE_ORDER: tuple[str, ...] = ("strong", "partial", "weak", "n_a")
_STANCE_GLYPH: dict[str, str] = {"strong": "S", "partial": "P", "weak": "W", "n_a": "-"}
_STANCE_GLYPH_COLOR: dict[str, str] = {"strong": "white", "partial": "black", "weak": "black", "n_a": "#666666"}


def generate_property_matrix(project_root: Path | str) -> Path:
    """Render the 24-candidate by 9-property stance heatmap."""
    root = Path(project_root)
    out = figures_dir(root) / "property_matrix.png"

    stances: dict[tuple[str, str], str] = {}
    for candidate_id, property_id, stance in matrix_rows():
        stances[(candidate_id, property_id)] = stance

    candidate_ids = [candidate.candidate_id for candidate in CANDIDATES]
    property_ids = [prop.property_id for prop in PROPERTIES]
    property_names = [ascii_text(prop.name) for prop in PROPERTIES]
    candidate_names = [ascii_text(candidate.name) for candidate in CANDIDATES]

    index = {stance: i for i, stance in enumerate(_STANCE_ORDER)}
    grid = [
        [index[stances[(candidate_id, property_id)]] for property_id in property_ids]
        for candidate_id in candidate_ids
    ]

    fig = new_figure((7.6, 9.6))
    fig.subplots_adjust(left=0.315, right=0.985, top=0.945, bottom=0.245)
    ax = fig.add_subplot(111)

    cmap = ListedColormap([STANCE_COLORS[stance] for stance in _STANCE_ORDER])
    ax.imshow(grid, cmap=cmap, vmin=0, vmax=len(_STANCE_ORDER) - 1, aspect="auto")

    # White gridlines between cells.
    ax.set_xticks([x - 0.5 for x in range(1, len(property_ids))], minor=True)
    ax.set_yticks([y - 0.5 for y in range(1, len(candidate_ids))], minor=True)
    ax.grid(which="minor", color="white", linewidth=1.2)
    ax.tick_params(which="minor", length=0)

    # Cell glyphs.
    for row, candidate_id in enumerate(candidate_ids):
        for col, property_id in enumerate(property_ids):
            stance = stances[(candidate_id, property_id)]
            ax.text(
                col,
                row,
                _STANCE_GLYPH[stance],
                ha="center",
                va="center",
                fontsize=7.0,
                color=_STANCE_GLYPH_COLOR[stance],
            )

    ax.set_xticks(range(len(property_ids)))
    ax.set_xticklabels(property_names, rotation=45, ha="right", fontsize=8.5)
    ax.set_yticks(range(len(candidate_ids)))
    ax.set_yticklabels(candidate_names, fontsize=8.5)
    ax.tick_params(which="major", length=0)
    for side in ("top", "right", "left", "bottom"):
        ax.spines[side].set_visible(False)

    ax.set_title("Candidate x property stance matrix (24 x 9 = 216 cells)", fontsize=11, pad=10)

    handles = [
        Patch(facecolor=STANCE_COLORS[stance], edgecolor="none", label=stance.replace("_", "-"))
        for stance in _STANCE_ORDER
    ]
    ax.legend(
        handles=handles,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.155),
        fontsize=9,
        ncol=4,
        title="Stance",
        title_fontsize=9,
        frameon=False,
    )

    return save_figure(fig, out)
