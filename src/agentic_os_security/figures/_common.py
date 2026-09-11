"""Shared deterministic style and save helpers for the figure package.

Every figure in this package MUST be byte-identical across runs given identical
inputs:

- the Agg backend is forced before any canvas is created;
- fonts are pinned to DejaVu Sans (shipped with matplotlib, no system lookup);
- ``svg.hashsalt`` is fixed so any SVG-derived element (clip paths, gradients)
  hashes identically on every run;
- no wall-clock value, environment string, or matplotlib version string is
  written into the output file metadata;
- all rendered text is ASCII (see :func:`ascii_text`).

Figures are built directly on :class:`matplotlib.figure.Figure` rather than
through ``pyplot`` so no global figure state can leak between generators.
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
    "CONFIDENCE_COLORS",
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

# Okabe-Ito colorblind-safe qualitative palette.
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

# Qualitative stance encoding for the candidate x property matrix.
STANCE_COLORS: dict[str, str] = {
    "strong": OKABE_ITO["bluish_green"],
    "partial": OKABE_ITO["sky_blue"],
    "weak": OKABE_ITO["orange"],
    "n_a": "#D9D9D9",
}

# Confidence-tier encoding for forecast figures (colorblind-safe subset).
CONFIDENCE_COLORS: dict[str, str] = {
    "high": OKABE_ITO["bluish_green"],
    "moderate": OKABE_ITO["blue"],
    "low": OKABE_ITO["vermillion"],
}

DETERMINISTIC_RC: dict[str, object] = {
    # Byte-determinism anchors.
    "svg.hashsalt": "agentic-os-security-0.1.0",
    # Fixed fonts: never resolve to a system font that varies by host.
    "font.family": "sans-serif",
    "font.sans-serif": ["DejaVu Sans"],
    "font.serif": ["DejaVu Serif"],
    "font.monospace": ["DejaVu Sans Mono"],
    "mathtext.fontset": "dejavusans",
    # No typographic minus sign (missing-glyph safety).
    "axes.unicode_minus": False,
    # Output discipline: PNG only, fixed dpi.
    "savefig.format": "png",
    "savefig.dpi": 300,
    "savefig.bbox": None,
    "savefig.pad_inches": 0.1,
    "figure.dpi": 100.0,
    # Flat, print-friendly defaults.
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "axes.edgecolor": "#444444",
    "axes.labelcolor": "black",
    "axes.grid": False,
    "grid.color": "#CCCCCC",
    "grid.linewidth": 0.5,
    "xtick.color": "#444444",
    "ytick.color": "#444444",
    "text.color": "black",
    "legend.frameon": False,
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
