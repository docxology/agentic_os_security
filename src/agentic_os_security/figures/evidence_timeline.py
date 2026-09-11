"""Figure: evidence timeline of offensive and defensive AI-agent capability.

``{#fig:evidence_timeline}`` -> ``output/figures/evidence_timeline.png``

Event facts are driven by :data:`agentic_os_security.evidence.CAPABILITY_BASELINE`
plus lookups into :data:`agentic_os_security.evidence.SOURCES` (matched by URL
substring, which the brief pins).  Publication months that the evidence base
does not pin to the day are shown year-only; the plotted marker position is a
layout choice, not a date claim.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from matplotlib.patches import Patch

from ..evidence import CAPABILITY_BASELINE, SOURCES, Source
from ..project_paths import figures_dir
from ._common import OKABE_ITO, ascii_text, new_figure, save_figure, wrap_ascii

__all__ = ["generate_evidence_timeline"]

_TIER_COLORS: dict[str, str] = {
    "official": OKABE_ITO["blue"],
    "advisory": OKABE_ITO["orange"],
    "incident_report": OKABE_ITO["vermillion"],
    "research": OKABE_ITO["reddish_purple"],
    "community": OKABE_ITO["gray"],
}

_URL_FRAGMENTS: dict[str, tuple[str, ...]] = {
    "ncsc": ("ncsc.gov.uk",),
    "anthropic": ("anthropic.com",),
    "aixcc": ("darpa.mil",),
    "aisi": ("aisi.gov.uk",),
    "qsb_118": ("qsb-118", "qubes-os.org/news/2026/08"),
    "nix_advisory": ("ghsa-g3g9", "nix/security/advisories"),
    "nixos_2605": ("nixos-2605", "nixos.org/blog/announcements"),
}


@dataclass(frozen=True)
class _TimelineEvent:
    event_id: str
    x: float  # fractional-year marker position (layout only)
    level: float  # stem height; signs alternate to prevent overlap
    label: str
    detail: str
    tier: str
    align: str = "center"  # horizontal text alignment (edge events: left)


def _find_source(*fragments: str) -> Source | None:
    for source in SOURCES:
        url = getattr(source, "url", "") or ""
        if any(fragment in url.lower() for fragment in fragments):
            return source
    return None


def _tier_of(source: Source | None, default: str) -> str:
    tier = getattr(source, "tier", None)
    return tier if isinstance(tier, str) and tier in _TIER_COLORS else default


def _build_events() -> list[_TimelineEvent]:
    baseline = CAPABILITY_BASELINE
    tiers = {
        key: _tier_of(_find_source(*frags), default)
        for key, frags, default in (
            ("ncsc", _URL_FRAGMENTS["ncsc"], "official"),
            ("anthropic", _URL_FRAGMENTS["anthropic"], "incident_report"),
            ("aixcc", _URL_FRAGMENTS["aixcc"], "official"),
            ("aisi", _URL_FRAGMENTS["aisi"], "incident_report"),
            ("qsb_118", _URL_FRAGMENTS["qsb_118"], "advisory"),
            ("nix_advisory", _URL_FRAGMENTS["nix_advisory"], "advisory"),
            ("nixos_2605", _URL_FRAGMENTS["nixos_2605"], "official"),
        )
    }
    aisi_days = ascii_text(str(baseline.get("aisi_incident_days", "2026-07-25..28")))
    aisi_start = aisi_days.split("..")[0]

    return [
        _TimelineEvent(
            "ncsc_assessment",
            2025.35,
            1.05,
            "NCSC assessment (2025)",
            "AI already assists reconnaissance and exploit development; scaling expected through "
            f"{baseline.get('ncsc_horizon_year', 2027)}",
            tiers["ncsc"],
            align="right",
        ),
        _TimelineEvent(
            "aixcc_results",
            2025.72,
            2.6,
            "DARPA AIxCC results (2025)",
            f"Competition systems discovered and patched real vulnerabilities "
            f"({baseline.get('aixcc_year', 2025)})",
            tiers["aixcc"],
        ),
        _TimelineEvent(
            "anthropic_campaign",
            2025.9,
            -1.1,
            "Anthropic campaign (Nov 2025)",
            f"Campaign against roughly {baseline.get('anthropic_targeted_entities', 30)} entities; "
            "agent involvement across the attack chain (vendor findings)",
            tiers["anthropic"],
            align="right",
        ),
        _TimelineEvent(
            "nix_advisory",
            2026.3,
            -2.6,
            "Nix security advisory (Apr 2026)",
            "Symlink-following flaw in fixed-output derivation registration (multi-user installs)",
            tiers["nix_advisory"],
            align="right",
        ),
        _TimelineEvent(
            "aisi_incident",
            2026.58,
            1.05,
            f"AISI incident report ({aisi_start})",
            f"Out-of-scope internet actions in {baseline.get('aisi_unsanctioned_runs', 10)} of "
            f"{baseline.get('aisi_runs_total', 122)} runs; no sandbox escape",
            tiers["aisi"],
            align="left",
        ),
        _TimelineEvent(
            "qsb_118",
            2026.67,
            -1.1,
            "QSB-118 (Aug 2026)",
            f"Compromised qube to dom0 command injection; fixed in "
            f"{baseline.get('qsb_118_fix_package', 'qubes-core-dom0-linux 4.3.22')}",
            tiers["qsb_118"],
            align="left",
        ),
        _TimelineEvent(
            "nixos_2605_eol",
            2026.98,
            2.6,
            "NixOS 26.05 support ends",
            f"Security updates end {baseline.get('nixos_2605_support_end', '2026-12-31')}",
            tiers["nixos_2605"],
            align="right",
        ),
    ]

def generate_evidence_timeline(project_root: Path | str) -> Path:
    """Render the 2025-2026 evidence timeline and return the written path."""
    root = Path(project_root)
    out = figures_dir(root) / "evidence_timeline.png"
    events = _build_events()

    fig = new_figure((7.8, 5.0))
    ax = fig.add_subplot(111)

    ax.axhline(0.0, color="#333333", linewidth=1.2, zorder=1)
    for year in (2025, 2026, 2027):
        ax.axvline(year, color="#CCCCCC", linewidth=0.6, zorder=0)

    for event in events:
        color = _TIER_COLORS.get(event.tier, OKABE_ITO["black"])
        ax.plot(
            [event.x, event.x],
            [0.0, event.level],
            color=color,
            linewidth=1.1,
            zorder=2,
        )
        ax.plot(
            [event.x],
            [event.level],
            marker="o",
            markersize=5.5,
            color=color,
            zorder=3,
        )
        above = event.level > 0
        va = "bottom" if above else "top"
        label_y = event.level + (0.14 if above else -0.14)
        detail_y = event.level + (0.58 if above else -0.58)
        ax.annotate(
            event.label,
            xy=(event.x, label_y),
            ha=event.align,
            va=va,
            fontsize=8.0,
            fontweight="bold",
            zorder=4,
        )
        ax.annotate(
            wrap_ascii(event.detail, width=30, max_lines=3),
            xy=(event.x, detail_y),
            ha=event.align,
            va=va,
            fontsize=6.6,
            color="#333333",
            zorder=4,
        )

    ax.set_xlim(2024.7, 2027.45)
    ax.set_ylim(-4.5, 4.5)
    ax.set_xticks([2025, 2026, 2027])
    ax.set_xticklabels(["2025", "2026", "2027"], fontsize=9)
    ax.set_yticks([])
    for side in ("left", "top", "right"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_bounds(2025.0, 2027.4)
    ax.set_title(
        "Documented offensive and defensive AI-agent capability evidence",
        fontsize=10.5,
        pad=10,
    )

    handles = [
        Patch(facecolor=_TIER_COLORS[tier], edgecolor="none", label=shown)
        for tier, shown in (
            ("official", "official"),
            ("advisory", "advisory"),
            ("incident_report", "incident report"),
            ("research", "research"),
        )
    ]
    ax.legend(
        handles=handles,
        loc="upper left",
        bbox_to_anchor=(0.005, 0.995),
        ncol=1,
        fontsize=7.0,
        title="Source tier",
        title_fontsize=7.0,
        frameon=False,
    )

    return save_figure(fig, out)
