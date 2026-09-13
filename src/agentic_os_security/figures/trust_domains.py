"""Figure: the seven trust domains as a layered authority architecture.

``{#fig:trust_domains}`` -> ``output/figures/trust_domains.png``

Redesigned for v0.2.0 as a clean layered flow: hostile *intake* feeds a
disposable *execution* domain, whose crossings are mediated by the
*authority mediation* layer (credential service, release/deployment) before
they reach *assets* (personal identity). Administration and recovery sit
outside the daily path. Numbered mediation arrows point to the pinned
control ids from :data:`agentic_os_security.trust_domains.CONTROLS`; box
contents and restrictions come from :data:`TRUST_DOMAINS`. A v0.6.0
annotation appends the failure path each arrow counters —
``(exploitation)`` / ``(authorized misuse)`` / ``(both)`` — derived from
:data:`agentic_os_security.threat_model.CAPABILITY_LINKAGE` by majority
vote across the capabilities each arrow's mediation points cover.
"""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch

from ..project_paths import figures_dir
from ..threat_model import CAPABILITY_LINKAGE
from ..trust_domains import TRUST_DOMAINS
from ._common import OKABE_ITO, ascii_text, new_figure, save_figure, wrap_ascii

__all__ = ["generate_trust_domains"]

# Control ids pinned by the brief; mediation arrows carry these.
_CTRL_EGRESS = "egress_boundary"
_CTRL_CREDS = "scoped_credentials"
_CTRL_APPROVAL = "external_approvals"
_CTRL_OP_MEDIATION = "operation_mediation"
_CTRL_RECOVERY = "rehearsed_recovery"

_FACE_INTAKE = "#FDF3E3"  # light orange
_FACE_EXEC = "#E8F4FA"  # light sky blue
_FACE_ASSETS = "#F4E9F4"  # light reddish purple
_FACE_OUTSIDE = "#F2F2F2"  # gray band for administration + recovery

_BY_ID = {domain.domain_id: domain for domain in TRUST_DOMAINS}


_BY_ID = {domain.domain_id: domain for domain in TRUST_DOMAINS}

#: Failure-path display words (full words, no codes).
_FAILURE_PATH_WORDS: dict[str, str] = {
    "exploitation": "exploitation",
    "authorized_misuse": "authorized misuse",
}

#: Numbered-arrow control id -> the orchestration mediation-point ids that
#: arrow realizes. The failure-path suffix on each arrow is the majority
#: vote across :data:`threat_model.CAPABILITY_LINKAGE` capabilities whose
#: mediation_points include any of these ids.
_ARROW_MEDIATION_IDS: dict[str, tuple[str, ...]] = {
    _CTRL_EGRESS: ("egress_proxy",),
    _CTRL_CREDS: ("oauth_resource_server", "agent_identity_exchange"),
    _CTRL_APPROVAL: ("external_approval",),
    _CTRL_OP_MEDIATION: ("tool_annotations", "classifier_escalation"),
}


def _failure_path_suffix(mediation_ids: tuple[str, ...]) -> str:
    """Return the ``(failure path)`` suffix for one numbered arrow.

    Majority vote across the CAPABILITY_LINKAGE capabilities covered by
    *mediation_ids*: a failure path wins when more than half of the covered
    capabilities list it; both paths winning renders ``(both)``. With no
    covering capability the vote falls back to the full linkage.
    """
    covered = [
        link
        for link in CAPABILITY_LINKAGE
        if set(mediation_ids) & set(link.mediation_points)
    ] or list(CAPABILITY_LINKAGE)
    tally = Counter(fp for link in covered for fp in link.failure_paths)
    winners = sorted(fp for fp, n in tally.items() if n > len(covered) / 2)
    if not winners:
        winners = [min(tally, key=lambda fp: (-tally[fp], fp))]
    if len(winners) == 1:
        return f"({_FAILURE_PATH_WORDS[winners[0]]})"
    return "(both)"


def _box(
    ax,
    x: float,
    y: float,
    w: float,
    h: float,
    title: str,
    contents: tuple[str, ...],
    limit: str,
    edge: str,
    face: str,
    dashed: bool = False,
    n_contents: int = 2,
    wrap: int = 30,
) -> None:
    """Draw a trust-domain box; y is the TOP edge (axis is inverted)."""
    ax.add_patch(
        FancyBboxPatch(
            (x, y),
            w,
            h,
            boxstyle="round,pad=0.045,rounding_size=0.10",
            edgecolor=edge,
            facecolor=face,
            linewidth=1.3,
            linestyle="--" if dashed else "-",
            zorder=2,
        )
    )
    tx = x + 0.13
    ax.text(tx, y + 0.15, ascii_text(title), fontsize=6.8, fontweight="bold", va="top", ha="left", color=edge, zorder=3)
    body = "\n".join(wrap_ascii(f"- {item}", width=wrap, max_lines=2) for item in contents[:n_contents])
    ax.text(tx, y + 0.48, body, fontsize=5.5, va="top", ha="left", color="#333333", linespacing=1.3, zorder=3)
    ax.text(
        tx,
        y + h - 0.28,
        "limit: " + wrap_ascii(ascii_text(limit), width=40, max_lines=2),
        fontsize=5.2,
        style="italic",
        va="top",
        ha="left",
        color="#555555",
        linespacing=1.25,
        zorder=3,
    )


def _numbered_arrow(
    ax,
    x0: float,
    y0: float,
    x1: float,
    y1: float,
    color: str,
    number: int,
    label: str,
    label_dx: float = 0.0,
    label_dy: float = 0.26,
    dashed: bool = False,
) -> None:
    ax.add_patch(
        FancyArrowPatch(
            (x0, y0),
            (x1, y1),
            arrowstyle="-|>",
            mutation_scale=9,
            linewidth=1.1,
            color=color,
            linestyle="--" if dashed else "-",
            shrinkA=1.0,
            shrinkB=1.0,
            zorder=4,
        )
    )
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    ax.add_patch(Circle((cx, cy), 0.16, facecolor=color, edgecolor="white", linewidth=0.7, zorder=5))
    ax.text(cx, cy, str(number), fontsize=5.2, fontweight="bold", ha="center", va="center", color="white", zorder=6)
    ax.text(
        cx + label_dx,
        cy + label_dy,
        ascii_text(label),
        fontsize=5.3,
        ha="center",
        va="top",
        color="#333333",
        zorder=6,
    )


def generate_trust_domains(project_root: Path | str) -> Path:
    """Render the layered trust-domain architecture diagram."""
    root = Path(project_root)
    out = figures_dir(root) / "trust_domains.png"

    fig = new_figure((9.8, 6.6))
    ax = fig.add_subplot(111)
    ax.set_xlim(0, 11.1)
    ax.set_ylim(0, 7.6)
    ax.invert_yaxis()
    ax.axis("off")

    # --- Daily-path enclosure: intake + execution. ---
    ax.add_patch(
        FancyBboxPatch(
            (0.30, 2.30),
            5.55,
            4.95,
            boxstyle="round,pad=0.03,rounding_size=0.12",
            edgecolor="#888888",
            facecolor="none",
            linestyle="--",
            linewidth=1.1,
            zorder=1,
        )
    )
    ax.text(0.46, 2.44, "DAILY PATH: hostile input, disposable execution", fontsize=5.4, color="#666666", ha="left", va="top")

    # --- Outside-the-daily-path band: administration + recovery. ---
    ax.add_patch(
        FancyBboxPatch(
            (0.30, 0.30),
            10.45,
            1.58,
            boxstyle="round,pad=0.03,rounding_size=0.12",
            edgecolor="#AAAAAA",
            facecolor=_FACE_OUTSIDE,
            linestyle="--",
            linewidth=1.0,
            zorder=1,
        )
    )
    ax.text(0.44, 0.44, "OUTSIDE THE DAILY PATH", fontsize=5.4, fontweight="bold", color="#777777", ha="left", va="top")

    admin = _BY_ID["administration"]
    _box(
        ax,
        0.55, 0.76, 4.0, 1.02,
        admin.name,
        admin.contents[:2],
        "no agent-generated commands without independent review",
        OKABE_ITO["blue"],
        "#FFFFFF",
        dashed=True,
    )
    recovery = _BY_ID["recovery"]
    _box(
        ax,
        6.85, 0.76, 3.70, 1.02,
        recovery.name,
        recovery.contents[:2],
        "acts on credentials and state the daily path no longer holds",
        OKABE_ITO["bluish_green"],
        "#FFFFFF",
        dashed=True,
    )
    ax.text(
        5.42, 1.26,
        f"[5] {ascii_text(_CTRL_RECOVERY)}:\nrehearsed, external to agents",
        fontsize=5.0,
        ha="center",
        va="center",
        color="#333333",
        linespacing=1.25,
    )
    ax.add_patch(
        FancyArrowPatch(
            (6.60, 1.26), (6.85, 1.26),
            arrowstyle="-|>", mutation_scale=8, linewidth=1.0,
            color=OKABE_ITO["bluish_green"], linestyle="--", zorder=4,
        )
    )

    # --- Layer 1: intake. ---
    intake = _BY_ID["browsing_intake"]
    _box(
        ax,
        0.55, 3.45, 2.25, 3.45,
        intake.name,
        intake.contents,
        intake.restrictions[0],
        OKABE_ITO["orange"],
        _FACE_INTAKE,
    )
    ax.text(0.55, 6.98, "layer 1 - intake", fontsize=5.4, color=OKABE_ITO["orange"], fontweight="bold", va="top")

    # --- Layer 2: execution. ---
    execution = _BY_ID["agent_execution"]
    _box(
        ax,
        3.30, 2.80, 2.30, 4.15,
        execution.name,
        execution.contents[:3],
        "disposable VM; no host home; no broad credentials",
        OKABE_ITO["sky_blue"],
        _FACE_EXEC,
    )
    ax.text(3.30, 2.52, "layer 2 - execution", fontsize=5.4, color=OKABE_ITO["sky_blue"], fontweight="bold", va="top")

    # --- Layer 3: authority mediation. ---
    creds = _BY_ID["credential_service"]
    _box(
        ax,
        6.85, 4.70, 2.35, 2.10,
        creds.name,
        creds.contents,
        creds.restrictions[0],
        OKABE_ITO["bluish_green"],
        "#EAF6F0",
    )
    release = _BY_ID["release_deployment"]
    _box(
        ax,
        6.85, 2.40, 2.35, 2.00,
        release.name,
        release.contents,
        "agent proposes; approval policy lies outside its control",
        OKABE_ITO["blue"],
        "#EAF2FA",
    )
    ax.text(6.85, 2.22, "layer 3 - authority mediation", fontsize=5.4, color=OKABE_ITO["bluish_green"], fontweight="bold", va="top")

    # --- Layer 4: assets. ---
    identity = _BY_ID["personal_identity"]
    _box(
        ax,
        9.40, 4.70, 1.62, 2.10,
        identity.name,
        identity.contents,
        identity.restrictions[1],
        OKABE_ITO["reddish_purple"],
        "#F7ECF5",
        n_contents=2,
        wrap=22,
    )
    ax.text(9.40, 6.98, "layer 4 - assets", fontsize=5.4, color=OKABE_ITO["reddish_purple"], fontweight="bold", va="top")

    # --- Flow and mediation arrows. ---
    # Intake -> execution (content crossing under review).
    ax.add_patch(
        FancyArrowPatch(
            (2.80, 5.10), (3.30, 5.10),
            arrowstyle="-|>", mutation_scale=9, linewidth=1.2,
            color="#666666", zorder=4,
        )
    )
    ax.text(3.05, 4.92, "reviewed\ncrossings", fontsize=4.8, ha="center", va="bottom", color="#555555", linespacing=1.2)

    # (1) Egress: execution back out across the daily-path boundary.
    _numbered_arrow(
        ax, 3.30, 3.05, 0.55, 3.05,
        OKABE_ITO["vermillion"], 1,
        f"{_CTRL_EGRESS}: controlled egress\n{_failure_path_suffix(_ARROW_MEDIATION_IDS[_CTRL_EGRESS])}",
        label_dx=0.0, label_dy=0.15,
    )

    # (2) Credential operations: execution -> credential service.
    _numbered_arrow(
        ax, 5.60, 5.60, 6.85, 5.60,
        OKABE_ITO["bluish_green"], 2,
        f"{_CTRL_CREDS}\n{_failure_path_suffix(_ARROW_MEDIATION_IDS[_CTRL_CREDS])}",
        label_dx=0.0,
    )
    # (3) External approvals: execution -> release/deployment.
    _numbered_arrow(
        ax, 5.60, 3.60, 6.85, 3.40,
        OKABE_ITO["blue"], 3,
        f"{_CTRL_APPROVAL}\n{_failure_path_suffix(_ARROW_MEDIATION_IDS[_CTRL_APPROVAL])}",
        label_dx=0.0, label_dy=0.30,
    )

    # Mediation results into assets.
    ax.add_patch(
        FancyArrowPatch(
            (9.20, 5.60), (9.42, 5.60),
            arrowstyle="-|>", mutation_scale=8, linewidth=1.0,
            color=OKABE_ITO["bluish_green"], zorder=4,
        )
    )
    ax.add_patch(
        FancyArrowPatch(
            (9.20, 3.40), (9.75, 4.62),
            arrowstyle="-|>", mutation_scale=8, linewidth=1.0,
            color=OKABE_ITO["blue"], linestyle="--", zorder=4,
        )
    )

    # (4) Operation mediation: administration (outside daily path) gates commands.
    _numbered_arrow(
        ax, 3.10, 1.96, 3.10, 2.74,
        OKABE_ITO["blue"], 4,
        ascii_text(f"{_CTRL_OP_MEDIATION}\n{_failure_path_suffix(_ARROW_MEDIATION_IDS[_CTRL_OP_MEDIATION])}"),
        label_dx=0.0, label_dy=-0.40,
        dashed=True,
    )

    ax.set_title("Seven trust domains as a layered authority architecture", fontsize=9.5, pad=10)

    return save_figure(fig, out)