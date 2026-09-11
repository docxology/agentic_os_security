"""Figure: isolation boundaries between orchestrator, tool broker, and workers.

``{#fig:orchestration_boundaries}`` -> ``output/figures/orchestration_boundaries.png``

Realistic deployment redesign for v0.2.0: the orchestrator delegates through
a tool broker (MCP-shaped) to isolated workers, with the ten numbered
mediation points from :data:`agentic_os_security.orchestration.MEDIATION_POINTS`
keyed at the trust boundaries they police, dashed trust-boundary lines, and
the egress proxy as a choke point on the outer edge. The pattern note comes
from :data:`ORCHESTRATION_PATTERNS`.
"""

from __future__ import annotations

from pathlib import Path

from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch

from ..orchestration import MEDIATION_POINTS
from ..project_paths import figures_dir
from ._common import OKABE_ITO, ascii_text, new_figure, save_figure, wrap_ascii

__all__ = ["generate_orchestration_boundaries"]

# point_id -> (placement, x, y) in axis coords; "broker_top" places the badge
# on the broker's upper edge at x, "worker" on a worker box, "egress" at the
# egress crossing, "approval" on the external-approval entry point, "audit"
# on the audit trail band, "identity" on the agent-identity crossing.
_PLACEMENTS: dict[str, tuple[str, float, float]] = {
    "sandbox_primitives": ("worker", 0, 0.5),
    "egress_proxy": ("egress", 0, 0),
    "tool_annotations": ("broker_top", 0, 0),
    "oauth_resource_server": ("broker_top", 0, 0),
    "url_mode_elicitation": ("broker_left", 0, 0),
    "a2a_tls_auth": ("broker_right", 0, 0),
    "agent_identity_exchange": ("broker_left", 0, 0),
    "classifier_escalation": ("orchestrator", 0, 0),
    "sandbox_observability": ("audit", 0, 0),
    "external_approval": ("approval", 0, 0),
}


def generate_orchestration_boundaries(project_root: Path | str) -> Path:
    """Render the orchestrator / broker / worker boundary diagram."""
    root = Path(project_root)
    out = figures_dir(root) / "orchestration_boundaries.png"

    fig = new_figure((9.8, 7.0))
    ax = fig.add_subplot(111)
    ax.set_xlim(0, 11.4)
    ax.set_ylim(0, 8.15)
    ax.invert_yaxis()
    ax.axis("off")

    def box(x, y, w, h, title, subtitle, edge, face, lw=1.3, dashed=False):
        ax.add_patch(
            FancyBboxPatch(
                (x, y), w, h,
                boxstyle="round,pad=0.045,rounding_size=0.10",
                edgecolor=edge, facecolor=face,
                linewidth=lw, linestyle="--" if dashed else "-", zorder=2,
            )
        )
        ax.text(x + 0.12, y + 0.16, ascii_text(title), fontsize=6.6, fontweight="bold", va="top", color=edge, zorder=3)
        if subtitle:
            ax.text(x + 0.12, y + 0.42, wrap_ascii(ascii_text(subtitle), width=38, max_lines=2),
                    fontsize=5.0, va="top", color="#444444", linespacing=1.25, zorder=3)

    def arrow(x0, y0, x1, y1, color, dashed=False, lw=1.1):
        ax.add_patch(
            FancyArrowPatch(
                (x0, y0), (x1, y1),
                arrowstyle="-|>", mutation_scale=9,
                color=color, linewidth=lw,
                linestyle="--" if dashed else "-",
                shrinkA=1, shrinkB=1, zorder=4,
            )
        )

    def badge(x, y, number, color):
        ax.add_patch(Circle((x, y), 0.17, facecolor=color, edgecolor="white", linewidth=0.7, zorder=6))
        ax.text(x, y, str(number), fontsize=5.2, fontweight="bold", ha="center", va="center", color="white", zorder=7)

    points = {point.point_id: point for point in MEDIATION_POINTS}
    numbers = {point.point_id: i + 1 for i, point in enumerate(MEDIATION_POINTS)}
    C_AGENT, C_BROKER, C_EGRESS, C_AUDIT = (
        OKABE_ITO["sky_blue"], OKABE_ITO["orange"], OKABE_ITO["vermillion"], OKABE_ITO["bluish_green"],
    )

    # --- Orchestrator zone (top). ---
    box(0.45, 0.40, 8.1, 1.55, "Orchestrator", "plans, assigns tasks, reviews results; holds no production credentials",
        OKABE_ITO["blue"], "#F3F7FC")

    # --- Tool broker zone (middle). ---
    box(0.45, 2.55, 8.1, 1.75, "Tool broker (MCP-shaped mediation layer)",
        "every tool call is scoped, mediated, and logged; grants are task-scoped and revocable",
        C_BROKER, "#FEF9F1", lw=1.7)

    # --- Workers (inside broker's execution perimeter). ---
    worker_y = 4.75
    for i, (wx, label) in enumerate(((0.70, "worker A"), (3.65, "worker B"), (6.60, "worker C"))):
        box(wx, worker_y, 2.6, 1.7, label, "disposable sandboxed environment", C_AGENT, "#EDF6FC", lw=1.1)

    # Trust boundaries (dashed) around workers and around the broker zone.
    for wx in (0.55, 3.50, 6.45):
        ax.add_patch(
            FancyBboxPatch(
                (wx - 0.06, worker_y - 0.06), 2.72, 1.82,
                boxstyle="round,pad=0.01,rounding_size=0.08",
                edgecolor="#999999", facecolor="none", linestyle="--", linewidth=0.9, zorder=1,
            )
        )

    # --- Egress proxy choke point (outer right edge). ---
    box(9.0, 2.55, 2.05, 1.75, "Egress proxy", "allowlist-only outbound; reachable = mediated", C_EGRESS, "#FDF0E9")
    arrow(8.55, 3.40, 8.95, 3.40, C_EGRESS)
    ax.text(8.72, 3.18, "only exit", fontsize=4.8, ha="center", va="top", color=C_EGRESS)

    # --- External approval (outside, top right). ---
    box(9.35, 0.40, 1.95, 1.55, "Human principal", "approvals originate outside the hierarchy", OKABE_ITO["blue"], "#FFFFFF", dashed=True)
    arrow(9.30, 1.15, 8.60, 1.15, OKABE_ITO["blue"], dashed=True)

    # --- Audit trail (bottom, outside every write authority). ---
    box(0.45, 6.95, 10.95, 0.75, "Append-only audit trail",
        "broker decisions, credential events, approvals - beyond every agent's write authority",
        C_AUDIT, "#F1F9F5")

    # --- Flows. ---
    arrow(2.4, 1.95, 2.4, 2.5, OKABE_ITO["blue"])  # task + scoped grant
    ax.text(2.55, 2.24, "task + scoped grant", fontsize=5.2, ha="left", va="center", color="#333333")
    arrow(3.4, 4.30, 2.4, 4.72, C_AGENT)  # mediated call down
    arrow(7.9, 4.72, 7.4, 4.30, C_AGENT)  # results up
    ax.text(3.55, 4.52, "mediated tool call", fontsize=5.2, ha="left", va="center", color="#333333")
    ax.text(7.30, 4.52, "results", fontsize=5.2, ha="right", va="center", color="#333333")

    # --- Numbered mediation badges. ---
    badge_xy: dict[str, tuple[float, float, str]] = {
        # id, (x, y, badge color)
        "sandbox_primitives": (4.30, 5.55, C_AGENT),
        "egress_proxy": (8.75, 3.62, C_EGRESS),
        "tool_annotations": (2.72, 5.62, C_BROKER),
        "oauth_resource_server": (4.55, 2.68, C_BROKER),
        "url_mode_elicitation": (0.75, 3.55, C_BROKER),
        "a2a_tls_auth": (7.95, 3.85, C_BROKER),
        "agent_identity_exchange": (0.75, 4.20, C_BROKER),
        "classifier_escalation": (6.20, 1.15, OKABE_ITO["blue"]),
        "sandbox_observability": (7.20, 6.95, C_AUDIT),
        "external_approval": (9.05, 1.15, OKABE_ITO["blue"]),
    }
    # draw badges with leader alignment into the legend
    for point_id, (bx, by, color) in badge_xy.items():
        n = numbers[point_id]
        ax.add_patch(Circle((bx, by), 0.19, facecolor=color, edgecolor="white", linewidth=0.8, zorder=7))
        ax.text(bx, by, str(n), fontsize=5.6, fontweight="bold", ha="center", va="center", color="white", zorder=8)

    # Legend of numbered points below the diagram.
    entries = [
        f"{numbers[point.point_id]}  {ascii_text(point.point_id)} - {ascii_text(point.name)}"
        for point in MEDIATION_POINTS
    ]
    half = (len(entries) + 1) // 2
    leg = fig.add_axes((0.02, 0.005, 0.95, 0.125))
    leg.axis("off")
    leg.set_xlim(0, 2)
    leg.set_ylim(0, half + 1.2)
    leg.invert_yaxis()
    leg.text(0.0, 0.1, "Mediation points (numbered as plotted; boundary detail in orchestration.MEDIATION_POINTS)",
             fontsize=5.2, fontweight="bold", color="#444444", va="top")
    for i, entry in enumerate(entries):
        col = i // half
        row = i % half
        leg.text(col + 0.02, row + 0.95, entry, fontsize=5.2, ha="left", va="center", color="#333333")

    fig.suptitle("Orchestration boundaries: workers never bypass the broker", fontsize=9.5, y=0.975)

    return save_figure(fig, out)