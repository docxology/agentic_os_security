"""Figure: the authority ladder from proposal to revocation.

``{#fig:authority_ladder}`` -> ``output/figures/authority_ladder.png``

Rung membership is read from :data:`agentic_os_security.threat_model.AUTHORITY_LADDER`
in its pinned order; shading distinguishes agent-drafted rungs, the human
authorization gate, agent-exercised rungs, and independent/human control rungs.
"""

from __future__ import annotations

from pathlib import Path

from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Patch

from ..project_paths import figures_dir
from ..threat_model import AUTHORITY_LADDER_RUNGS
from ._common import OKABE_ITO, ascii_text, new_figure, save_figure

__all__ = ["generate_authority_ladder"]

# Pinned rung glosses (one line each, ASCII).
_RUNG_GLOSSES: dict[str, str] = {
    "propose": "Agent or tool drafts a change or action request",
    "stage": "Change is prepared without touching the trusted base",
    "authorize": "A human identity approves the staged change",
    "exercise": "Approved action executes under the granted scope",
    "audit": "Independent trail records what ran and who approved",
    "revoke": "Grants and staged changes are withdrawn and rolled back",
}

# Shading classes per rung name.
_AGENT_FACE = "#CDE9F6"  # light Okabe-Ito sky blue
_GATE_FACE = "#FFFFFF"
_AUDIT_FACE = "#CDEBDD"  # light Okabe-Ito bluish green
_REVOKE_FACE = "#F8DCCB"  # light Okabe-Ito vermillion

_RUNG_FACE: dict[str, str] = {
    "propose": _AGENT_FACE,
    "stage": _AGENT_FACE,
    "authorize": _GATE_FACE,
    "exercise": _AGENT_FACE,
    "audit": _AUDIT_FACE,
    "revoke": _REVOKE_FACE,
}
_RUNG_EDGE: dict[str, str] = {
    "propose": OKABE_ITO["sky_blue"],
    "stage": OKABE_ITO["sky_blue"],
    "authorize": OKABE_ITO["black"],
    "exercise": OKABE_ITO["sky_blue"],
    "audit": OKABE_ITO["bluish_green"],
    "revoke": OKABE_ITO["vermillion"],
}
_RUNG_LINEWIDTH: dict[str, float] = {rung: (2.2 if rung == "authorize" else 1.2) for rung in _RUNG_FACE}

_LEGEND = (
    (_AGENT_FACE, OKABE_ITO["sky_blue"], 1.2, "Agent-drafted / agent-exercised (mediated)"),
    (_GATE_FACE, OKABE_ITO["black"], 2.2, "Human authorization gate"),
    (_AUDIT_FACE, OKABE_ITO["bluish_green"], 1.2, "Independent verification"),
    (_REVOKE_FACE, OKABE_ITO["vermillion"], 1.2, "Human recovery control"),
)


def generate_authority_ladder(project_root: Path | str) -> Path:
    """Render the propose-to-revoke authority ladder."""
    root = Path(project_root)
    out = figures_dir(root) / "authority_ladder.png"

    rungs = list(AUTHORITY_LADDER_RUNGS)
    n = len(rungs)

    fig = new_figure((7.6, 7.2))
    fig.subplots_adjust(left=0.02, right=0.64, top=0.93, bottom=0.03)
    ax = fig.add_subplot(111)
    ax.set_ylim(0.0, float(n))
    ax.invert_yaxis()
    ax.axis("off")

    box_left = 0.06
    box_width = 0.62
    box_height = 0.62

    for i, rung in enumerate(rungs):
        top = float(i) + (1.0 - box_height) / 2
        face = _RUNG_FACE.get(rung.rung_id, "#EEEEEE")
        edge = _RUNG_EDGE.get(rung.rung_id, OKABE_ITO["gray"])
        linewidth = _RUNG_LINEWIDTH.get(rung.rung_id, 1.2)
        ax.add_patch(
            FancyBboxPatch(
                (box_left, top),
                box_width,
                box_height,
                boxstyle="round,pad=0.012,rounding_size=0.045",
                linewidth=linewidth,
                edgecolor=edge,
                facecolor=face,
            )
        )
        ax.text(
            box_left + 0.035,
            top + 0.16,
            f"{i + 1}. {ascii_text(rung.name)}",
            fontsize=9.5,
            fontweight="bold",
            va="top",
        )
        ax.text(
            box_left + 0.035,
            top + 0.36,
            _RUNG_GLOSSES.get(rung.rung_id, ""),
            fontsize=6.8,
            va="top",
            color="#333333",
        )
        if i + 1 < n:
            ax.add_patch(
                FancyArrowPatch(
                    (box_left + box_width / 2, i + 1.0 - 0.06),
                    (box_left + box_width / 2, i + 1.0 + 0.02),
                    arrowstyle="-|>",
                    mutation_scale=12,
                    linewidth=1.0,
                    color="#555555",
                )
            )

    handles = [
        Patch(facecolor=face, edgecolor=edge, linewidth=linewidth, label=label)
        for face, edge, linewidth, label in _LEGEND
    ]
    fig.legend(
        handles=handles,
        loc="upper left",
        bbox_to_anchor=(0.67, 0.93),
        fontsize=6.8,
        title="Shading",
        title_fontsize=7.2,
        alignment="left",
    )


    fig.suptitle(
        "Authority ladder: every agent capability passes through the human gate",
        fontsize=10.5,
        y=0.985,
    )
    return save_figure(fig, out)
