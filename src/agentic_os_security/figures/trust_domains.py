"""Figure: the seven trust domains of a compartmentalized operator setup.

``{#fig:trust_domains}`` -> ``output/figures/trust_domains.png``

Driven by :data:`agentic_os_security.trust_domains.TRUST_DOMAINS`: one rounded
panel per domain with its contents and restrictions, plus a summary panel.
"""

from __future__ import annotations

from pathlib import Path

from matplotlib.patches import FancyBboxPatch

from ..project_paths import figures_dir
from ..trust_domains import TRUST_DOMAINS
from ._common import OKABE_ITO, PALETTE, ascii_text, new_figure, save_figure, wrap_ascii

__all__ = ["generate_trust_domains"]

_COLS = 4
_CONTENT_ITEMS = 3
_RESTRICTION_ITEMS = 2
_WRAP = 30


def _panel_text(contents: tuple[str, ...], restrictions: tuple[str, ...]) -> str:
    lines: list[str] = ["Contents:"]
    for item in contents[:_CONTENT_ITEMS]:
        lines.append(wrap_ascii(f"- {item}", width=34, max_lines=2))
    if len(contents) > _CONTENT_ITEMS:
        lines.append("  ...")
    lines.append("")
    lines.append("Limits:")
    for item in restrictions[:_RESTRICTION_ITEMS]:
        lines.append(wrap_ascii(f"- {item}", width=34, max_lines=2))
    if len(restrictions) > _RESTRICTION_ITEMS:
        lines.append("  ...")
    return "\n".join(lines)


def generate_trust_domains(project_root: Path | str) -> Path:
    """Render the 7-domain authority-separation diagram."""
    root = Path(project_root)
    out = figures_dir(root) / "trust_domains.png"

    domains = list(TRUST_DOMAINS)
    n_panels = len(domains) + 1  # one summary panel
    rows = 2

    fig = new_figure((9.6, 6.0))
    ax = fig.add_subplot(111)
    ax.set_xlim(0, _COLS)
    ax.set_ylim(0, rows)
    ax.invert_yaxis()
    ax.axis("off")

    panel_w = 0.96
    panel_h = 0.92

    def draw_panel(col: float, row: float, title: str, body: str, edge: str, face: str) -> None:
        x = col + (1.0 - panel_w) / 2
        y = row + (1.0 - panel_h) / 2
        ax.add_patch(
            FancyBboxPatch(
                (x, y),
                panel_w,
                panel_h,
                boxstyle="round,pad=0.015,rounding_size=0.04",
                linewidth=1.2,
                edgecolor=edge,
                facecolor=face,
            )
        )
        ax.text(x + 0.05, y + 0.10, ascii_text(title), fontsize=8.2, fontweight="bold", va="top")
        ax.text(x + 0.05, y + 0.24, body, fontsize=6.2, va="top", color="#222222", linespacing=1.35)

    for i, domain in enumerate(domains):
        col = i % _COLS
        row = i // _COLS
        edge = PALETTE[i % len(PALETTE)]
        draw_panel(
            col,
            row,
            domain.name,
            _panel_text(domain.contents, domain.restrictions),
            edge=edge,
            face="#FFFFFF",
        )

    # Summary panel: the separation principle.
    summary = (
        "No agent-execution identity\n"
        "holds administration,\n"
        "personal identity, or\n"
        "credential authority.\n"
        "\n"
        "Every crossing between\n"
        "domains is a mediated\n"
        "boundary (scoped grant,\n"
        "approval, or broker),\n"
        "never a shared account."
    )
    draw_panel(
        len(domains) % _COLS,
        len(domains) // _COLS,
        "Separation principle",
        summary,
        edge=OKABE_ITO["black"],
        face="#F2F2F2",
    )

    ax.set_title("Seven trust domains: separating authority on one machine", fontsize=11.5, pad=12)

    return save_figure(fig, out)
