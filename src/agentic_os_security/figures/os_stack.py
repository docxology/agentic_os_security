"""Figure: the operating-system security stack, layer by layer.

``{#fig:os_stack}`` -> ``output/figures/os_stack.png``

Publication-grade v0.6.0 layout: the left column carries a documented
entry-point marker per struck layer (small vermillion dot + short tag
naming the incidents from :data:`agentic_os_security.evidence.INCIDENTS`),
the right hand side is an archetype-coverage grid — the eight category
archetypes x the eight layers, colored by the shared ``strong | partial |
weak | n_a`` stance vocabulary from :data:`agentic_os_security.stack.STACK_COVERAGE`
— with a full-word legend (no letter codes).

Publication-grade document-scale typography (7-11 pt), colorblind-safe,
and byte-deterministic across runs (fixed fonts, no wall-clock, no pyplot
state, metadata stripped on save).
"""

from __future__ import annotations

from pathlib import Path

from matplotlib.patches import Rectangle

from ..evidence import INCIDENTS
from ..project_paths import figures_dir
from ..stack import ARCHETYPE_LABELS, STACK_COVERAGE, STACK_LAYERS
from ._common import OKABE_ITO, STANCE_COLORS, ascii_text, new_figure, save_figure, wrap_ascii

_ACCENT = OKABE_ITO["blue"]
_GREEN = OKABE_ITO["bluish_green"]
_INK = "#222222"
_SOFT = "#555555"

_CANVAS_W = 10.2
_CANVAS_H = 6.6

_GRID_X0 = 6.70
_CELL_W = 0.38
_CELL_H = 0.52
_ROW_PITCH = 0.60
_GRID_TOP = 5.55
_STANCE_ORDER = ("strong", "partial", "weak", "n_a")
_STANCE_WORDS = {"strong": "strong", "partial": "partial", "weak": "weak", "n_a": "not assessed"}
#: Documented entry points (v0.6.0): layer_id -> (incident ids from
#: :data:`evidence.INCIDENTS`, short full-word tag drawn beside a small
#: vermillion dot on that layer's name row).
_ENTRY_POINT_MARKERS: dict[str, tuple[tuple[str, ...], str]] = {
    "hypervisor": (("qsb-110", "qsb-115", "qsb-116"), "QSB-110/115/116"),
    "sandbox_runtime": (("cve_2026_1386",), "Firecracker CVE-2026-1386"),
    "update_provisioning": (
        ("nix_ghsa_g3g9", "nix_ghsa_vh5x", "cve_2026_44029"),
        "Nix GHSAs",
    ),
    "agent_runtime_tool_bridge": (("aisi_inc_2026_07_28_01",), "AISI unsanctioned actions"),
}


def generate_os_stack(project_root: Path | str) -> Path:
    """Render the eight-layer operating-system stack with coverage columns."""
    root = Path(project_root)
    out = figures_dir(root) / "os_stack.png"

    layers = list(STACK_LAYERS)
    archetypes = list(ARCHETYPE_LABELS)

    # Documented entry points must trace to registered incidents.
    incident_ids = {incident.incident_id for incident in INCIDENTS}
    for _layer_id, (marker_ids, _tag) in _ENTRY_POINT_MARKERS.items():
        assert all(mid in incident_ids for mid in marker_ids), (
            f"entry-point marker cites unknown incidents: {_layer_id}"
        )

    fig = new_figure((_CANVAS_W, _CANVAS_H))
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
    ax = fig.add_axes((0, 0, 1, 1))
    ax.set_xlim(0, _CANVAS_W)
    ax.set_ylim(0, _CANVAS_H)
    ax.axis("off")

    # --- Title strip. ---
    ax.text(
        0.35,
        6.32,
        "The operating-system security stack",
        fontsize=11.5,
        fontweight="bold",
        ha="left",
        va="center",
        color=_INK,
    )
    ax.text(
        0.35,
        6.06,
        ascii_text("eight layers, from hardware and firmware to the agent runtime and its tool bridge"),
        fontsize=8.0,
        ha="left",
        va="center",
        color=_SOFT,
    )

    # --- Archetype column headers (rotated above the grid). ---
    for col, archetype in enumerate(archetypes):
        cx = _GRID_X0 + col * _CELL_W + _CELL_W / 2
        ax.text(
            cx,
            _GRID_TOP + 0.06,
            ascii_text(ARCHETYPE_LABELS[archetype]),
            rotation=45,
            ha="right",
            va="baseline",
            rotation_mode="anchor",
            fontsize=7.2,
            fontweight="bold",
            color=_INK,
        )

    # --- Layer rows (ordinal 1 = hardware and firmware, top). ---
    for row, layer in enumerate(layers):
        row_top = _GRID_TOP - row * _ROW_PITCH
        y_mid = row_top - _CELL_H / 2

        # Ordinal badge.
        ax.add_patch(
            Rectangle(
                (0.35, row_top - 0.44),
                0.30,
                0.30,
                facecolor=_ACCENT,
                edgecolor="none",
                zorder=3,
            )
        )
        ax.text(
            0.50,
            row_top - 0.29,
            str(layer.ordinal),
            fontsize=8.0,
            fontweight="bold",
            ha="center",
            va="center",
            color="white",
            zorder=4,
        )

        # Layer name + mechanism annotations + candidate example.
        ax.text(
            0.80,
            row_top - 0.16,
            ascii_text(layer.name),
            fontsize=9.0,
            fontweight="bold",
            ha="left",
            va="center",
            color=_INK,
        )
        ax.text(
            0.80,
            row_top - 0.34,
            wrap_ascii(ascii_text(", ".join(layer.mechanisms)), width=96, max_lines=2),
            fontsize=7.2,
            ha="left",
            va="center",
            color=_SOFT,
            linespacing=1.15,
        )
        ax.text(
            0.80,
            row_top - 0.52,
            wrap_ascii(ascii_text(f"e.g. {layer.candidate_example}"), width=90, max_lines=1),
            fontsize=7.2,
            style="italic",
            ha="left",
            va="center",
            color=_ACCENT,
        )

        # Documented entry-point marker: vermillion dot + short tag on the
        # layer-name row, right-aligned against the coverage grid.
        marker = _ENTRY_POINT_MARKERS.get(layer.layer_id)
        if marker:
            _marker_ids, tag = marker
            ax.plot(
                [6.56],
                [row_top - 0.16],
                marker="o",
                markersize=3.4,
                color=OKABE_ITO["vermillion"],
                zorder=4,
            )
            ax.text(
                6.46,
                row_top - 0.16,
                ascii_text(tag),
                fontsize=6.2,
                ha="right",
                va="center",
                color=OKABE_ITO["vermillion"],
                zorder=4,
            )

        # Archetype coverage cells for this layer.
        for col, archetype in enumerate(archetypes):
            stance = STACK_COVERAGE[archetype][layer.layer_id]
            ax.add_patch(
                Rectangle(
                    (_GRID_X0 + col * _CELL_W, row_top - _CELL_H),
                    _CELL_W - 0.03,
                    _CELL_H - 0.03,
                    facecolor=STANCE_COLORS[stance],
                    edgecolor="white",
                    linewidth=0.5,
                    zorder=2,
                )
            )

    # --- Full-word stance legend under the grid (no letter codes). ---
    legend_y = 0.52
    x_cursor = _GRID_X0
    for stance in _STANCE_ORDER:
        ax.add_patch(
            Rectangle(
                (x_cursor, legend_y),
                0.16,
                0.16,
                facecolor=STANCE_COLORS[stance],
                edgecolor="#888888",
                linewidth=0.5,
                zorder=3,
            )
        )
        ax.text(
            x_cursor + 0.21,
            legend_y + 0.08,
            _STANCE_WORDS[stance],
            fontsize=7.2,
            ha="left",
            va="center",
            color=_INK,
        )
        x_cursor += 0.21 + 0.072 * (len(_STANCE_WORDS[stance]) + 2)

    # --- Footnote: the layering invariant (eq:stack_layering in prose). ---
    ax.text(
        0.35,
        legend_y + 0.08,
        ascii_text("A compromise at one layer must not grant authority at the next layer."),
        fontsize=7.8,
        style="italic",
        ha="left",
        va="center",
        color=_GREEN,
    )

    return save_figure(fig, out)
