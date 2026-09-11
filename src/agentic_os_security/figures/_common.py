"""Shared deterministic style and save helpers for the figure package (v2).

Contract for every generator in :mod:`agentic_os_security.figures`:

- Pure matplotlib (Agg), no network, no wall-clock, no pyplot state.
- Typography tuned for a 9pt-document print: all text drawn at 6-10 pt in
  figure inches, so at ``width=100%`` textwidth embedding the on-page size
  matches 6.5-10 pt effective.
- Byte-determinism: fixed fonts (DejaVu family only), fixed
  ``svg.hashsalt``, PNG metadata stripped (``Software: None``), no
  timestamps anywhere in figure code. Two runs on the same inputs produce
  byte-identical files.
- Colorblind-safe encoding: Okabe-Ito palette everywhere; stance and
  confidence vocabularies get fixed color assignments.

Version 2 additions over v0.1: category color map for the 8 candidate
categories (shared by the property matrix, defensive stack, and update
windows), print-scale rcParams (font sizes 6-10 pt), and the helper
:func:`category_rows` used by the banded matrix figures.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import matplotlib

matplotlib.use("Agg", force=True)

from matplotlib import rcParams  # noqa: E402
from matplotlib.backends.backend_agg import FigureCanvasAgg  # noqa: E402
from matplotlib.figure import Figure  # noqa: E402

__all__ = [
    "OKABE_ITO",
    "PALETTE",
    "STANCE_COLORS",
    "STANCE_GLYPHS",
    "CONFIDENCE_COLORS",
    "CATEGORY_COLORS",
    "CATEGORY_LABELS",
    "DETERMINISTIC_RC",
    "FigureSpec",
    "Figure",
    "FigureCanvasAgg",
    "apply_style",
    "new_figure",
    "save_figure",
    "ascii_text",
    "wrap_ascii",
]

#: Okabe-Ito colorblind-safe qualitative palette.
OKABE_ITO: dict[str, str] = {
    "black": "#000000",
    "orange": "#E69F00",
    "sky_blue": "#56B4E9",
    "bluish_green": "#009E73",
    "yellow": "#F0E442",
    "blue": "#0072B2",
    "vermillion": "#D55E00",
    "reddish_purple": "#CC79A7",
    "gray": "#999999",
}

PALETTE: tuple[str, ...] = (
    OKABE_ITO["blue"],
    OKABE_ITO["orange"],
    OKABE_ITO["bluish_green"],
    OKABE_ITO["vermillion"],
    OKABE_ITO["sky_blue"],
    OKABE_ITO["reddish_purple"],
    OKABE_ITO["yellow"],
    OKABE_ITO["black"],
    OKABE_ITO["gray"],
)

#: Qualitative stance encoding for the candidate x property matrix and the
#: defensive stack (same ``strong | partial | weak | n_a`` vocabulary).
STANCE_COLORS: dict[str, str] = {
    "strong": OKABE_ITO["bluish_green"],
    "partial": OKABE_ITO["sky_blue"],
    "weak": OKABE_ITO["orange"],
    "n_a": "#D9D9D9",
}

#: Single-letter cell glyphs kept legible at 9pt-document scale.
STANCE_GLYPHS: dict[str, str] = {"strong": "S", "partial": "P", "weak": "W", "n_a": "-"}

#: Glyph color per stance (chosen for contrast against STANCE_COLORS fills).
STANCE_GLYPH_COLORS: dict[str, str] = {
    "strong": "white",
    "partial": "black",
    "weak": "black",
    "n_a": "#666666",
}

#: Confidence-tier encoding for the forecast figure (colorblind-safe subset).
CONFIDENCE_COLORS: dict[str, str] = {
    "high": OKABE_ITO["bluish_green"],
    "moderate": OKABE_ITO["blue"],
    "low": OKABE_ITO["vermillion"],
}

#: Category color map for the 8-category candidate vocabulary (pinned ids in
#: ``agentic_os_security.registry.CATEGORY_VOCAB``). Distinct hues under the
#: Okabe-Ito constraint; yellow is paired with dark text wherever used as a
#: band fill.
CATEGORY_COLORS: dict[str, str] = {
    "compartmentalized": OKABE_ITO["blue"],
    "reproducible": OKABE_ITO["bluish_green"],
    "desktop": OKABE_ITO["sky_blue"],
    "server": OKABE_ITO["orange"],
    "anonymity": OKABE_ITO["reddish_purple"],
    "high_assurance": OKABE_ITO["vermillion"],
    "mobile": OKABE_ITO["yellow"],
    "offensive_toolkit": OKABE_ITO["gray"],
}

#: ASCII display labels for the category ids (title case).
CATEGORY_LABELS: dict[str, str] = {
    "compartmentalized": "Compartmentalized",
    "reproducible": "Reproducible",
    "desktop": "Desktop",
    "server": "Server",
    "anonymity": "Anonymity",
    "high_assurance": "High assurance",
    "mobile": "Mobile",
    "offensive_toolkit": "Offensive toolkit",
}

DETERMINISTIC_RC: dict[str, object] = {
    # Byte-determinism anchors.
    "svg.hashsalt": "agentic-os-security-0.2.0",
    # Fixed fonts: never resolve to a system font that varies by host.
    "font.family": "sans-serif",
    "font.sans-serif": ["DejaVu Sans"],
    "font.serif": ["DejaVu Serif"],
    "font.monospace": ["DejaVu Sans Mono"],
    "mathtext.fontset": "dejavusans",
    # No typographic minus sign (missing-glyph safety).
    "axes.unicode_minus": False,
    # Print typography: 9pt-document scale; generators draw at 6-10 pt.
    "font.size": 8.0,
    "figure.titlesize": 10.0,
    "figure.titleweight": "bold",
    "axes.titlesize": 9.0,
    "axes.titleweight": "bold",
    "axes.labelsize": 8.0,
    "axes.labelweight": "normal",
    "xtick.labelsize": 7.0,
    "ytick.labelsize": 7.0,
    "legend.fontsize": 6.8,
    # Output discipline: PNG only, fixed dpi, no bbox-time surprises.
    "savefig.format": "png",
    "savefig.dpi": 300,
    "savefig.bbox": None,
    "savefig.pad_inches": 0.08,
    "figure.dpi": 100.0,
    # Flat, print-friendly defaults.
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "axes.edgecolor": "#444444",
    "axes.labelcolor": "black",
    "axes.grid": False,
    "axes.linewidth": 0.6,
    "grid.color": "#CCCCCC",
    "grid.linewidth": 0.5,
    "xtick.color": "#444444",
    "ytick.color": "#444444",
    "xtick.major.width": 0.6,
    "ytick.major.width": 0.6,
    "text.color": "black",
    "legend.frameon": False,
    "lines.linewidth": 1.0,
    "patch.linewidth": 0.8,
}

_ASCII_TRANSLATION = {
    0x2013: "-",  # en dash
    0x2014: "-",  # em dash
    0x2018: "'",
    0x2019: "'",
    0x201C: '"',
    0x201D: '"',
    0x2026: "...",
    0x00D7: "x",
    0x2192: "->",
    0x00A0: " ",
}


def ascii_text(text: str) -> str:
    """Return *text* restricted to ASCII, mapping common punctuation."""
    replaced = text.translate(_ASCII_TRANSLATION)
    return replaced.encode("ascii", "replace").decode("ascii")


def wrap_ascii(text: str, width: int = 32, max_lines: int = 3) -> str:
    """ASCII-wrap *text* to *width* characters, truncating past *max_lines*."""
    words = ascii_text(text).split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if len(candidate) <= width or not current:
            current = candidate
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        lines[-1] = lines[-1][: max(0, width - 3)].rstrip() + "..."
    return "\n".join(lines)


@dataclass(frozen=True)
class FigureSpec:
    """One entry of the pinned figure registry."""

    label: str
    filename: str
    section: str


def apply_style() -> None:
    """Apply the deterministic rcParams profile for all generators."""
    rcParams.update(DETERMINISTIC_RC)


def new_figure(figsize: tuple[float, float]) -> Figure:
    """Create a styled Agg-backed figure without touching pyplot state."""
    apply_style()
    fig = Figure(figsize=figsize, dpi=100.0, facecolor="white")
    FigureCanvasAgg(fig)
    return fig


def save_figure(fig: Figure, path: str | Path, dpi: int = 300) -> Path:
    """Save *fig* to *path* as a byte-deterministic 300-dpi PNG."""
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(
        out,
        format="png",
        dpi=dpi,
        facecolor="white",
        metadata={"Software": None},
    )
    return out