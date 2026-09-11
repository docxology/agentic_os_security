"""Figure: agent capability classes x orchestration mediation controls.

``{#fig:agent_surface}`` -> ``output/figures/agent_surface.png``

A mapping matrix between the pinned agent capability classes
(:data:`agentic_os_security.threat_model.AGENT_CAPABILITY_CLASSES`) and the
ten orchestration mediation points
(:data:`agentic_os_security.orchestration.MEDIATION_POINTS`). A filled,
numbered cell marks a mediation point that governs the capability class;
columns carry the numbered mediation-point ids, decoded in the embedded
legend, and a right marginal shows each class's coverage count.
"""

from __future__ import annotations

from pathlib import Path

from matplotlib.patches import FancyBboxPatch

from ..orchestration import MEDIATION_POINTS
from ..project_paths import figures_dir
from ..threat_model import AGENT_CAPABILITY_CLASSES
from ._common import OKABE_ITO, ascii_text, new_figure, save_figure, wrap_ascii

__all__ = ["generate_agent_surface"]

#: Pinned mapping: capability class id -> mediation points that govern it.
#: Grounded in each MediationPoint's boundary/mechanism: sandbox primitives
#: confine process and intake surfaces; the egress proxy governs external
#: communications; OAuth audience binding and URL-mode elicitation govern
#: credential touch; classifiers gate consequential (state-changing,
#: self-modifying) actions; observability feeds independent audit.
_CLASS_MEDIATION: dict[str, tuple[str, ...]] = {
    "content_intake": ("sandbox_primitives", "sandbox_observability", "classifier_escalation"),
    "tool_bridge_use": ("sandbox_primitives", "tool_annotations", "oauth_resource_server", "classifier_escalation"),
    "credential_touch": (
        "oauth_resource_server",
        "url_mode_elicitation",
        "agent_identity_exchange",
        "external_approval",
    ),
    "external_comms": ("egress_proxy", "a2a_tls_auth", "sandbox_observability"),
    "state_mutation": ("sandbox_primitives", "classifier_escalation", "external_approval", "sandbox_observability"),
    "self_modification": (
        "sandbox_primitives",
        "classifier_escalation",
        "external_approval",
        "sandbox_observability",
    ),
}

_FILL = OKABE_ITO["blue"]
_EMPTY = "#EDEDED"


def _parse_class(entry: str) -> tuple[str, str, str]:
    """Split ``id: description`` entries into (id, display name, gloss)."""
    class_id, _, description = entry.partition(":")
    class_id = class_id.strip()
    name = class_id.replace("_", " ").title()
    return class_id, name, ascii_text(description.strip())


def generate_agent_surface(project_root: Path | str) -> Path:
    """Render the capability-class x mediation-point coverage matrix."""
    root = Path(project_root)
    out = figures_dir(root) / "agent_surface.png"

    point_ids = [point.point_id for point in MEDIATION_POINTS]
    point_numbers = {point.point_id: i + 1 for i, point in enumerate(MEDIATION_POINTS)}
    point_names = {point.point_id: point.name for point in MEDIATION_POINTS}
    point_boundaries = {point.point_id: point.boundary for point in MEDIATION_POINTS}

    classes: list[tuple[str, str, str]] = []
    for entry in AGENT_CAPABILITY_CLASSES:
        class_id, name, gloss = _parse_class(entry)
        classes.append((class_id, name, gloss))
    unknown = {
        point_id
        for class_id, _, _ in classes
        for point_id in _CLASS_MEDIATION.get(class_id, ())
        if point_id not in point_numbers
    }
    assert not unknown, f"mediation mapping references unknown points: {sorted(unknown)}"

    n_rows = len(classes) * 2
    n_cols = len(point_ids)
    row_step = lambda i: i * 2.0  # class row centers (cells sit at even y)

    fig = new_figure((8.6, 6.1))
    fig.subplots_adjust(left=0.265, right=0.968, top=0.855, bottom=0.325)
    ax = fig.add_subplot(111)
    ax.set_xlim(-0.62, n_cols - 0.38)
    ax.set_ylim(n_rows - 0.5, -0.72)
    ax.invert_yaxis()
    ax.axis("off")

    cell_w = 0.34
    for row_idx, (class_id, _name, _gloss) in enumerate(classes):
        row_y = row_idx * 2.0
        mediated = set(_CLASS_MEDIATION.get(class_id, ()))
        for col_idx, point_id in enumerate(point_ids):
            covered = point_id in mediated
            ax.add_patch(
                FancyBboxPatch(
                    (col_idx - cell_w / 2, row_y - cell_w / 2),
                    cell_w,
                    cell_w,
                    boxstyle="round,pad=0.008,rounding_size=0.06",
                    facecolor=_FILL if covered else _EMPTY,
                    edgecolor="#666666" if covered else "#CCCCCC",
                    linewidth=0.6,
                )
            )
            if covered:
                ax.text(
                    col_idx,
                    row_y,
                    str(point_numbers[point_id]),
                    fontsize=5.6,
                    fontweight="bold",
                    ha="center",
                    va="center",
                    color="white",
                )

    # Column headers: numbered mediation points (number above rotated id).
    for col_idx, point_id in enumerate(point_ids):
        ax.text(col_idx, -0.60, str(point_numbers[point_id]), fontsize=5.6, fontweight="bold", ha="center", va="center", color=_FILL)
        ax.text(
            col_idx,
            -0.52,
            ascii_text(point_id),
            rotation=45,
            fontsize=5.4,
            ha="right",
            va="bottom",
            color="#333333",
        )

    # Row labels: class name (bold) with its gloss wrapped below.
    for row_idx, (_class_id, name, gloss) in enumerate(classes):
        row_y = row_idx * 2.0
        ax.text(
            -0.68,
            row_y + 0.10,
            name,
            fontsize=6.4,
            fontweight="bold",
            ha="right",
            va="bottom",
            color="#222222",
        )
        ax.text(
            -0.62,
            row_y + 0.04,
            wrap_ascii(gloss, width=54, max_lines=2),
            fontsize=4.6,
            ha="right",
            va="top",
            color="#777777",
            linespacing=1.25,
        )

    # Grid lines between rows/columns.
    for x in range(n_cols + 1):
        ax.axvline(x - 0.5, color="#E0E0E0", linewidth=0.5, zorder=0)
    for row_idx in range(len(classes)):
        ax.axhline(row_idx * 2 - 0.5, color="#E0E0E0", linewidth=0.5, zorder=0)
    ax.axhline((len(classes) - 1) * 2 + 0.5, color="#E0E0E0", linewidth=0.5, zorder=0)

    # Right marginal: per-class coverage counts.
    ax_cov = fig.add_axes((0.968, 0.325, 0.020, 0.53))
    ax_cov.set_xlim(0, 4.6)
    ax_cov.set_ylim((len(classes) - 1) * 2 + 0.9, -0.75)
    ax_cov.invert_yaxis()
    ax_cov.set_xticks([])
    ax_cov.set_yticks([])
    for row_idx, (class_id, _name, _gloss) in enumerate(classes):
        row_y = row_idx * 2.0
        count = len(_CLASS_MEDIATION.get(class_id, ()))
        ax_cov.barh(row_y, count, height=0.5, color=_FILL, edgecolor="white", linewidth=0.4)
        ax_cov.text(count + 0.12, row_y, str(count), fontsize=5.0, va="center", color="#333333")
    for side in ("top", "right", "left", "bottom"):
        ax_cov.spines[side].set_visible(False)
    ax_cov.set_title("n", fontsize=5.6, pad=3)

    # Embedded legend: numbered mediation points (id + name), two columns.
    legend_entries = [
        f"{point_numbers[point_id]}  {ascii_text(point_id)} - {ascii_text(point_names[point_id])}"
        for point_id in point_ids
    ]
    half = (len(legend_entries) + 1) // 2
    col_ax = fig.add_axes((0.012, 0.012, 0.95, 0.24))
    col_ax.axis("off")
    col_ax.set_xlim(0, 2)
    col_ax.set_ylim(0, half + 1)
    col_ax.invert_yaxis()
    for i, entry in enumerate(legend_entries):
        col = i // half
        row = i % half
        col_ax.text(col + 0.02, row + 0.5, entry, fontsize=5.4, ha="left", va="center", color="#333333")
    col_ax.text(
        0.0,
        0.08,
        "Mediation points (numbered as plotted; boundary detail in orchestration.MEDIATION_POINTS)",
        fontsize=5.2,
        fontweight="bold",
        color="#444444",
        ha="left",
        va="top",
    )

    ax.set_title(
        "Which mediation controls govern which agent capability classes",
        fontsize=9,
        pad=8,
    )
    return save_figure(fig, out)