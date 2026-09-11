"""Figure: evidence timeline of offensive AI-agent capability and platform incidents.

``{#fig:evidence_timeline}`` -> ``output/figures/evidence_timeline.png``

Two-lane layout (redesigned for v0.2.0):

- **Upper lane** - offensive capability and governance evidence: national
  assessments (NCSC 2024 and 2025), documented offensive-AI campaigns and
  incident reports, standards publications, and official adoption guidance.
- **Lower lane** - platform incidents and releases: the advisories, version
  releases, and hardening milestones on the operating-system side.

Event facts are anchored on :data:`agentic_os_security.evidence.CAPABILITY_BASELINE`
plus lookups into :data:`agentic_os_security.evidence.SOURCES` (matched by URL
substring, which the brief pins); the marker tier color follows the matched
source's tier and falls back to a documented default when a source key has
not yet been registered. Events are plotted at month precision; the plotted
marker position is a layout choice, not a date claim. Annotation callouts
are staggered across fixed levels with leader lines so no two texts overlap.
"""

from __future__ import annotations

from pathlib import Path

from matplotlib.lines import Line2D
from matplotlib.patches import Patch

from ..evidence import SOURCES, Source
from ..project_paths import figures_dir
from ._common import OKABE_ITO, ascii_text, new_figure, save_figure, wrap_ascii

__all__ = ["generate_evidence_timeline"]

_TIER_COLORS: dict[str, str] = {
    "official": OKABE_ITO["blue"],
    "advisory": OKABE_ITO["orange"],
    "incident_report": OKABE_ITO["vermillion"],
    "research": OKABE_ITO["bluish_green"],
    "community": OKABE_ITO["reddish_purple"],
}
_TIER_ORDER: tuple[str, ...] = ("official", "advisory", "incident_report", "research", "community")
_TIER_LABELS: dict[str, str] = {
    "official": "official",
    "advisory": "vendor advisory",
    "incident_report": "incident report",
    "research": "research / assessment",
    "community": "community",
}

_LANE_A_COLOR = OKABE_ITO["vermillion"]
_LANE_B_COLOR = OKABE_ITO["blue"]
_LEVEL_GAP = 0.95  # vertical distance between annotation levels (axis units)
_LEVEL_OFFSET = 1.05  # first annotation level above/below the lane line
_TEXT_WIDTH = 22  # wrap width (chars) for callout descriptions


def _find_source(*fragments: str) -> Source | None:
    for source in SOURCES:
        url = getattr(source, "url", "").lower()
        if url and all(fragment.lower() in url for fragment in fragments):
            return source
    return None


def _tier_of(source: Source | None, default: str) -> str:
    tier = getattr(source, "tier", None)
    return tier if isinstance(tier, str) and tier in _TIER_COLORS else default


def _assign_levels(dates: list[float], n_levels: int, min_gap: float) -> list[int]:
    """Greedily assign stagger levels so same-level callouts never collide.

    Events are processed in date order; a level is reused only when the
    horizontal distance to the last event on that level clears *min_gap*
    (in years). Assignment is deterministic given the input order.
    """
    last_on_level = [-10.0] * n_levels
    levels: list[int] = []
    for date in dates:
        chosen = None
        for offset in range(n_levels):
            level = (len(levels) + offset) % n_levels
            if abs(date - last_on_level[level]) >= min_gap:
                chosen = level
                break
        if chosen is None:  # dense cluster: take the level with the widest gap
            chosen = max(range(n_levels), key=lambda lv: abs(date - last_on_level[lv]))
        last_on_level[chosen] = date
        levels.append(chosen)
    return levels


def generate_evidence_timeline(project_root: Path | str) -> Path:
    """Render the 2024-2026 two-lane evidence timeline."""
    root = Path(project_root)
    out = figures_dir(root) / "evidence_timeline.png"

    # (year_float, lane, tier_fragments, fallback_tier, date_label, description)
    lane_a: list[tuple[float, str, tuple[str, ...], str, str, str]] = [
        (2024.0, "ncsc-2024", ("impact-of-ai-on-cyber-threat",), "research",
         "Jan 2024", "NCSC original AI threat assessment"),
        (2025.333, "ncsc-2027", ("impact-ai-cyber-threat-now",), "research",
         "May 2025", "NCSC 'From Now to 2027' capability horizon"),
        (2025.583, "vibe-hacking", ("anthropic",), "incident_report",
         "Aug 2025", "GTG-2002 'vibe hacking', 17+ targets"),
        (2025.667, "mcp-registry", ("modelcontextprotocol", "registry"), "official",
         "Sep 2025", "MCP registry preview opens"),
        (2025.833, "gtg-1002", ("anthropic",), "incident_report",
         "Nov 2025", "GTG-1002 campaign; OWASP Agentic T&M"),
        (2025.917, "owasp-top10", ("owasp",), "research",
         "Dec 2025", "OWASP agentic Top-10"),
        (2026.083, "openai-2026", ("openai",), "incident_report",
         "Feb 2026", "OpenAI consolidated report"),
        (2026.25, "cisa-guidance", ("cisa", "careful-adoption"), "official",
         "Apr 2026", "CISA Five Eyes agentic guidance"),
        (2026.583, "aisi-report", ("aisi",), "incident_report",
         "Aug 2026", "AISI INC-2026-07-28-01 report"),
    ]
    lane_b: list[tuple[float, str, tuple[str, ...], str, str, str]] = [
        (2025.917, "qubes-430", ("4_3/release-notes",), "official",
         "Dec 2025", "Qubes OS 4.3.0 released"),
        (2026.083, "nix-234", ("nix.dev/manual",), "official",
         "Feb 2026", "Nix 2.34"),
        (2026.167, "hardened-removed", ("secureblue", "discourse.nixos.org"), "official",
         "Mar 2026", "secureblue v4.3.0"),
        (2026.25, "nix-advisory", ("ghsa-g3g9",), "advisory",
         "Apr 2026", "Nix GHSA-g3g9 advisory"),
        (2026.333, "may-platforms", ("openbsd", "genode", "secureblue"), "official",
         "May 2026", "OpenBSD 7.9"),
        (2026.417, "jun-platform", ("qsb-116", "qsb/"), "advisory",
         "Jun 2026", "Nix 2.35; QSB-116"),
        (2026.5, "jul-platform", ("sel4",), "official",
         "Jul 2026", "seL4 16.0.0; QSB-118"),
        (2026.583, "openai-hf", ("openai",), "incident_report",
         "Aug 2026", "OpenAI-Hugging Face incident report"),
    ]

    fig = new_figure((8.8, 5.9))
    fig.subplots_adjust(left=0.02, right=0.995, top=0.905, bottom=0.115, hspace=0.30)
    ax_a = fig.add_subplot(211)
    ax_b = fig.add_subplot(212, sharex=ax_a)

    _X_MIN, _X_MAX = 2023.74, 2026.80

    def draw_lane(
        ax,
        events,
        line_y: float,
        direction: int,  # +1: callouts above the line; -1: below
        lane_label: str,
        lane_color: str,
        n_levels: int,
    ) -> None:
        dates = [event[0] for event in events]
        levels = _assign_levels(dates, n_levels, min_gap=0.42)
        for (date, _eid, fragments, fallback, date_label, description), level in zip(events, levels):
            source = _find_source(*fragments)
            tier = _tier_of(source, fallback)
            color = _TIER_COLORS[tier]
            level_y = line_y + direction * (_LEVEL_OFFSET + level * _LEVEL_GAP)
            # Leader line from the lane line to just short of the callout.
            ax.plot(
                [date, date],
                [line_y, level_y - direction * 0.06],
                color="#9A9A9A",
                linewidth=0.55,
                zorder=2,
            )
            ax.scatter(
                [date],
                [line_y],
                s=30,
                color=color,
                edgecolor="white",
                linewidth=0.5,
                zorder=4,
            )
            text = date_label + "\n" + wrap_ascii(ascii_text(description), width=_TEXT_WIDTH, max_lines=3)
            ax.text(
                date,
                level_y,
                text,
                fontsize=6.0,
                ha="center",
                va="top" if direction < 0 else "bottom",
                linespacing=1.25,
                color="#222222",
                zorder=3,
            )
        ax.axhline(line_y, color="#4A4A4A", linewidth=1.0, zorder=1)
        for year in (2024, 2025, 2026):
            ax.axvline(year, color="#E4E4E4", linewidth=0.6, zorder=0)
        if direction > 0:
            ax.set_ylim(line_y, line_y + _LEVEL_OFFSET + n_levels * _LEVEL_GAP)
            ax.text(
                _X_MIN + 0.03,
                line_y + _LEVEL_OFFSET + n_levels * _LEVEL_GAP - 0.18,
                lane_label,
                fontsize=6.6,
                fontweight="bold",
                color=lane_color,
                ha="left",
                va="top",
            )
            ax.tick_params(labelbottom=False)
        else:
            ax.set_ylim(line_y - (_LEVEL_OFFSET + n_levels * _LEVEL_GAP), line_y + 0.55)
            ax.text(
                _X_MIN + 0.03,
                -( _LEVEL_OFFSET + n_levels * _LEVEL_GAP) + 0.14,
                lane_label,
                fontsize=6.6,
                fontweight="bold",
                color=lane_color,
                ha="left",
                va="bottom",
            )
        ax.set_yticks([])
        for side in ("top", "right", "left"):
            ax.spines[side].set_visible(False)
        ax.spines["bottom"].set_color("#888888")

    draw_lane(
        ax_a,
        lane_a,
        line_y=0.0,
        direction=+1,
        lane_label="OFFENSIVE CAPABILITY AND GOVERNANCE EVIDENCE",
        lane_color=_LANE_A_COLOR,
        n_levels=4,
    )
    draw_lane(
        ax_b,
        lane_b,
        line_y=0.0,
        direction=-1,
        lane_label="PLATFORM INCIDENTS AND RELEASES",
        lane_color=_LANE_B_COLOR,
        n_levels=6,
    )

    ax_b.set_xlim(_X_MIN, _X_MAX)
    ax_b.set_xticks(range(2024, 2027))
    ax_b.set_xticklabels(["2024", "2025", "2026"], fontsize=7.5)
    ax_b.set_xlabel("Publication / release month (month precision; positions are a layout choice)", fontsize=6.8)

    fig.suptitle("Offensive-AI evidence and platform incidents, 2024-2026", fontsize=9.5, y=0.975)

    handles = [
        Patch(facecolor=_TIER_COLORS[tier], edgecolor="none", label=_TIER_LABELS[tier])
        for tier in _TIER_ORDER
    ]
    fig.legend(
        handles=handles,
        loc="lower center",
        ncol=5,
        fontsize=6.4,
        bbox_to_anchor=(0.5, 0.005),
        handlelength=1.1,
        handleheight=0.8,
        columnspacing=1.2,
    )

    return save_figure(fig, out)