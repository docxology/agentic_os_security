"""Figure: the authority ladder as a three-actor swimlane chart.

``{#fig:authority_ladder}`` -> ``output/figures/authority_ladder.png``

Swimlane redesign for v0.2.0: three actor columns (human principal /
orchestrator + agent / tool broker + target) x six rungs
(:data:`agentic_os_security.threat_model.AUTHORITY_LADDER` in pinned order),
with the agent-exercise-without-external-authorization region shaded as
forbidden and the independence fallacy annotated (the agent cannot both
write policy and approve it).
"""

from __future__ import annotations

from pathlib import Path

from matplotlib.patches import FancyBboxPatch, Patch

from ..project_paths import figures_dir
from ..threat_model import AUTHORITY_LADDER_RUNGS
from ._common import OKABE_ITO, ascii_text, new_figure, save_figure, wrap_ascii

__all__ = ["generate_authority_ladder"]

_COLS: tuple[str, ...] = ("human_principal", "orchestrator_agent", "tool_broker_target")
_COL_TITLES: dict[str, str] = {
    "human_principal": "HUMAN PRINCIPAL",
    "orchestrator_agent": "ORCHESTRATOR + AGENT",
    "tool_broker_target": "TOOL BROKER + TARGET",
}
_COL_NOTES: dict[str, str] = {
    "human_principal": "identity, approvals, revocation",
    "orchestrator_agent": "drafts, stages, proposes",
    "tool_broker_target": "mediated execution surface",
}

# Actor involvement per rung: (human, agent, broker) in {none, assist, lead, gate}.
# Grounded in the pinned rung definitions (threat_model.AUTHORITY_LADDER docstring):
# propose/stage are agent work; authorize is the human gate; exercise runs under
# broker mediation; audit and revoke are principal powers over external state.
_RUNG_ACTORS: dict[str, tuple[str, str, str]] = {
    "propose": ("review", "active", "none"),
    "stage": ("inspect", "active", "receives"),
    "authorize": ("ACTIVE", "forbidden", "none"),
    "exercise": ("informed", "active", "enforces"),
    "audit": ("owns", "writes-once", "contributes"),
    "revoke": ("owns", "forbidden", "executes"),
}

_FACE_AGENT = "#E8F4FA"  # agent-active cells: light sky blue
_FACE_HUMAN = "#EAF6F0"  # human-owned cells: light bluish green
_FACE_BROKER = "#FDF3E3"  # broker cells: light orange
_FACE_FORBIDDEN = "#F9E3D9"  # forbidden cells: light vermillion
_FACE_NONE = "#FAFAFA"
_EDGE_FORBIDDEN = OKABE_ITO["vermillion"]

_HATCH_FORBIDDEN = "xx"


def generate_authority_ladder(project_root: Path | str) -> Path:
    """Render the authority ladder as a swimlane chart."""
    root = Path(project_root)
    out = figures_dir(root) / "authority_ladder.png"

    rungs = list(AUTHORITY_LADDER_RUNGS)
    n_rungs = len(rungs)

    fig = new_figure((9.4, 7.0))
    fig.subplots_adjust(left=0.02, right=0.985, top=0.855, bottom=0.165)
    ax = fig.add_subplot(111)
    ax.set_xlim(0, 4.0)
    ax.set_ylim(0, n_rungs)
    ax.invert_yaxis()
    ax.axis("off")

    rung_label_x = 0.02
    col_x = {col: 0.72 + i * 1.10 for i, col in enumerate(_COLS)}
    col_w = 1.02
    cell_h = 0.74
    cell_y_off = 0.13

    # Column headers.
    for col in _COLS:
        ax.text(
            col_x[col] + col_w / 2,
            -0.28,
            ascii_text(_COL_TITLES[col]),
            fontsize=6.2,
            fontweight="bold",
            ha="center",
            va="bottom",
            color="#222222",
        )
        ax.text(
            col_x[col] + col_w / 2,
            -0.16,
            ascii_text(_COL_NOTES[col]),
            fontsize=5.0,
            ha="center",
            va="bottom",
            color="#777777",
        )

    # Rung rows.
    for rung_idx, rung in enumerate(rungs):
        row_top = rung_idx
        actors = _RUNG_ACTORS[rung.rung_id]

        # Rung label column.
        ax.text(
            rung_label_x + 0.66,
            row_top + 0.42,
            rung.rung_id.upper(),
            fontsize=6.4,
            fontweight="bold",
            ha="right",
            va="center",
            color="#222222",
        )
        ax.text(
            rung_label_x + 0.66,
            row_top + 0.58,
            wrap_ascii(ascii_text(rung.definition), width=52, max_lines=2),
            fontsize=4.6,
            ha="right",
            va="top",
            color="#666666",
            linespacing=1.2,
        )

        for col_idx, col in enumerate(_COLS):
            state = actors[col_idx]
            x = col_x[col]
            if state == "forbidden":
                face, edge, hatch, text = _FACE_FORBIDDEN, _EDGE_FORBIDDEN, _HATCH_FORBIDDEN, "forbidden"
            elif state == "ACTIVE":
                face, edge, hatch, text = _FACE_HUMAN, OKABE_ITO["bluish_green"], None, "GATE"
            elif state in ("active", "receives", "enforces", "writes-once", "contributes"):
                face = _FACE_AGENT if col == "orchestrator_agent" else _FACE_BROKER
                edge, hatch, text = "#888888", None, state
            else:
                face, edge, hatch, text = _FACE_NONE, "#CCCCCC", None, state
            ax.add_patch(
                FancyBboxPatch(
                    (x, row_top + cell_y_off),
                    col_w,
                    cell_h,
                    boxstyle="round,pad=0.02,rounding_size=0.05",
                    facecolor=face,
                    edgecolor=edge,
                    linewidth=1.4 if state == "forbidden" else 0.7,
                    hatch=hatch,
                )
            )
            if text:
                ax.text(
                    x + col_w / 2,
                    row_top + cell_y_off + cell_h / 2,
                    text,
                    fontsize=5.2,
                    ha="center",
                    va="center",
                    color=_EDGE_FORBIDDEN if state == "forbidden" else "#444444",
                    style="italic" if state == "forbidden" else "normal",
                )

    # Independence-fallacy annotation under the ladder.

    handles = [
        Patch(facecolor=_FACE_HUMAN, edgecolor=OKABE_ITO["bluish_green"], linewidth=0.7, label="human principal gate / ownership"),
        Patch(facecolor=_FACE_AGENT, edgecolor="#888888", linewidth=0.7, label="agent-active rung"),
        Patch(facecolor=_FACE_BROKER, edgecolor="#888888", linewidth=0.7, label="broker-mediated"),
        Patch(facecolor=_FACE_FORBIDDEN, edgecolor=_EDGE_FORBIDDEN, linewidth=0.7, hatch=_HATCH_FORBIDDEN, label="forbidden to the agent"),
    ]
    fig.legend(
        handles=handles,
        loc="upper center",
        bbox_to_anchor=(0.5, 0.128),
        ncol=2,
        fontsize=5.6,
        frameon=True,
        facecolor="white",
        edgecolor="#AAAAAA",
        borderpad=0.4,
        handlelength=1.3,
        handleheight=0.9,
        columnspacing=1.1,
    )

    fig.text(0.5, 0.02, 'Shaded + hatched cells mark authority the agent must never hold:\nthe independence fallacy - an agent that both writes policy and approves it defeats the ladder.', ha='center', va='center', fontsize=5.2, color=_EDGE_FORBIDDEN, linespacing=1.35)
    fig.suptitle("Authority ladder: who acts at each rung (propose to revoke)", fontsize=9.5)
    return save_figure(fig, out)