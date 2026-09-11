"""Figure: isolation boundaries between orchestrator, tool broker, and workers.

``{#fig:orchestration_boundaries}`` -> ``output/figures/orchestration_boundaries.png``

A nested-boundary diagram: the orchestrator plans and audits, the tool broker
mediates every crossing (scoped credentials, egress, operation mediation), and
workers execute only inside their own compartments.  Control labels are taken
from :data:`agentic_os_security.trust_domains.CONTROLS` ids.
"""

from __future__ import annotations

from pathlib import Path

from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

from ..project_paths import figures_dir
from ..trust_domains import CONTROLS
from ._common import OKABE_ITO, ascii_text, new_figure, save_figure

__all__ = ["generate_orchestration_boundaries"]

_CONTROL_LABELS: dict[str, str] = {
    "scoped_credentials": "task-scoped credentials",
    "egress_boundary": "boundary-controlled egress",
    "external_approvals": "external approvals",
    "operation_mediation": "operation mediation",
    "independent_audit": "independent audit trail",
    "tool_bridge_constrain": "tool-bridge constraining",
}


def generate_orchestration_boundaries(project_root: Path | str) -> Path:
    """Render the orchestrator / tool-broker / worker isolation diagram."""
    root = Path(project_root)
    out = figures_dir(root) / "orchestration_boundaries.png"

    control_ids = [str(control.control_id) for control in CONTROLS]
    broker_labels = [
        _CONTROL_LABELS.get(control_id, ascii_text(control_id.replace("_", " ")))
        for control_id in control_ids
        if control_id in _CONTROL_LABELS
    ]

    fig = new_figure((8.8, 6.6))
    ax = fig.add_subplot(111)
    ax.set_xlim(0.0, 10.0)
    ax.set_ylim(0.0, 7.0)
    ax.invert_yaxis()
    ax.axis("off")

    def panel(x: float, y: float, w: float, h: float, edge: str, face: str, lw: float = 1.4) -> None:
        ax.add_patch(
            FancyBboxPatch(
                (x, y),
                w,
                h,
                boxstyle="round,pad=0.02,rounding_size=0.18",
                linewidth=lw,
                edgecolor=edge,
                facecolor=face,
            )
        )

    def arrow(x0: float, y0: float, x1: float, y1: float, color: str) -> None:
        ax.add_patch(
            FancyArrowPatch(
                (x0, y0),
                (x1, y1),
                arrowstyle="-|>",
                mutation_scale=13,
                linewidth=1.3,
                color=color,
            )
        )


    # Orchestrator boundary enclosing everything.
    panel(0.4, 0.7, 9.2, 5.9, edge=OKABE_ITO["blue"], face="#F5F8FC", lw=1.6)
    ax.text(0.62, 0.9, "Orchestrator (policy, approvals, audit)", fontsize=8.8, fontweight="bold", va="top", color=OKABE_ITO["blue"])


    # Tool broker boundary enclosing the workers.
    panel(0.9, 2.6, 8.2, 3.6, edge=OKABE_ITO["orange"], face="#FFFFFF", lw=1.8)
    ax.text(1.05, 2.75, "Tool broker (mediation layer)", fontsize=8.4, fontweight="bold", va="top", color=OKABE_ITO["orange"])
    ax.text(
        9.42,
        1.0,
        "Broker mediation controls:\n"
        + "\n".join(f"- {label}" for label in broker_labels),
        fontsize=6.2,
        ha="right",
        va="top",
        color="#333333",
        linespacing=1.45,
    )
    ax.text(1.05, 3.0, "every tool call is scoped, mediated, and logged", fontsize=6.2, ha="left", va="top", color="#333333")


    # Worker compartments (inside the broker boundary).
    worker_boxes = ((1.6, 3.5), (4.3, 3.5), (7.0, 3.5))
    for i, (wx, wy) in enumerate(worker_boxes):
        panel(wx, wy, 1.4, 1.9, edge=OKABE_ITO["sky_blue"], face="#E4F2FA", lw=1.2)
        ax.text(wx + 0.7, wy + 0.45, f"Worker {i + 1}", fontsize=7.6, fontweight="bold", ha="center", va="top")
        ax.text(
            wx + 0.7,
            wy + 0.85,
            "agent execution\ncompartment\n(no shared state)",
            fontsize=5.8,
            ha="center",
            va="top",
            color="#333333",
        )
    # Mediation arrows: orchestrator -> broker, broker -> workers, workers -> broker.
    arrow(2.2, 2.05, 2.2, 2.55, OKABE_ITO["blue"])  # task + scoped grant down
    ax.text(2.35, 2.3, "task + scoped grant", fontsize=6.2, ha="left", va="center", color="#333333")
    arrow(3.2, 5.95, 3.2, 5.5, OKABE_ITO["sky_blue"])  # mediated call down to worker 1
    arrow(6.8, 5.4, 6.8, 5.95, OKABE_ITO["sky_blue"])  # results up from worker 3
    ax.text(3.35, 5.72, "mediated tool call", fontsize=6.2, ha="left", va="center", color="#333333")
    ax.text(6.65, 5.72, "results", fontsize=6.2, ha="right", va="center", color="#333333")

    # Egress crossing at the orchestrator edge.
    arrow(9.0, 3.05, 9.75, 3.05, OKABE_ITO["vermillion"])
    ax.text(9.75, 3.38, "egress only via broker", fontsize=5.9, ha="right", va="top", color=OKABE_ITO["vermillion"])

    ax.set_title("Orchestration isolation boundaries: workers never bypass the broker", fontsize=10.5, pad=12)

    return save_figure(fig, out)
