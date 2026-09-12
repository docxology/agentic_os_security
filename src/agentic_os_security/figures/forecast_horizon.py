"""Figure: forecast horizon chart, 2026-2031.

``{#fig:forecast_horizon}`` -> ``output/figures/forecast_horizon.png``

Each :class:`agentic_os_security.forecasts.Forecast` becomes a horizontal bar
spanning its horizon window, colored by confidence tier
(``high | moderate | low``) with a legend; dashed guides mark the pinned
2028-2031 forecast window, and two dashed official-posture reference markers
place the May 2025 NCSC 2027-horizon assessment and the April 2026 Five-Eyes
adoption guidance on the same axis.
"""

from __future__ import annotations

from pathlib import Path

from matplotlib.patches import Patch


from ..forecasts import FORECASTS
from ..project_paths import figures_dir
from ._common import CONFIDENCE_COLORS, OKABE_ITO, ascii_text, new_figure, save_figure

__all__ = ["generate_forecast_horizon"]

_CONFIDENCE_ORDER: tuple[str, ...] = ("high", "moderate", "low")
_CONFIDENCE_LABEL: dict[str, str] = {"high": "high", "moderate": "moderate", "low": "low"}
_X_MIN, _X_MAX = 2026.0, 2031.0

#: Official-posture reference markers (month precision, pinned posture dates):
#: May 2025 NCSC 2027-horizon assessment and April 2026 Five-Eyes adoption
#: guidance (CISA "Careful Adoption of Agentic AI Services").
_POSTURE_MARKERS: tuple[tuple[float, str], ...] = (
    (2025.0 + 4.0 / 12.0, "NCSC 2027-horizon\nassessment (May 2025)"),
    (2026.0 + 4.0 / 12.0, "Five-Eyes adoption\nguidance (May 2026)"),
)


def generate_forecast_horizon(project_root: Path | str) -> Path:
    """Render the confidence-tier forecast horizon chart."""
    root = Path(project_root)
    out = figures_dir(root) / "forecast_horizon.png"

    forecasts = sorted(
        FORECASTS,
        key=lambda f: (f.horizon[0], f.horizon[1], str(f.forecast_id)),
    )
    row_height = 0.42
    n = len(forecasts)
    fig_height = 2.4 + row_height * n
    fig = new_figure((8.0, fig_height))
    fig.subplots_adjust(left=0.03, right=0.985, top=0.86, bottom=0.09)
    ax = fig.add_subplot(111)

    for i, forecast in enumerate(forecasts):
        start, end = float(forecast.horizon[0]), float(forecast.horizon[1])
        color = CONFIDENCE_COLORS.get(str(forecast.confidence), "#999999")
        y = n - 1 - i  # first forecast on top
        ax.barh(
            y,
            max(end - start, 0.25),
            left=start,
            height=0.55,
            color=color,
            edgecolor="none",
            zorder=2,
        )
        label = ascii_text(str(forecast.forecast_id))
        if start <= 2027.0:
            # Early-start bars: put the label inside the bar.
            ax.text(
                start + 0.1,
                y,
                label,
                ha="left",
                va="center",
                fontsize=7.2,
                color="white",
                zorder=3,
            )
        else:
            ax.text(
                start - 0.08,
                y,
                label,
                ha="right",
                va="center",
                fontsize=7.2,
                zorder=3,
            )

    # Horizon guides.
    for year, label in ((2028.0, "horizon\nstart"), (2031.0, "horizon\nend")):
        ax.axvline(year, color="#888888", linewidth=0.9, linestyle="--", zorder=1)
        ax.text(year, n + 1.45, label, fontsize=6.4, ha="center", va="bottom", color="#555555", linespacing=1.2)

    # Official-posture reference markers: May 2025 NCSC 2027-horizon
    # assessment and April 2026 Five-Eyes adoption guidance. Labels sit on
    # two staggered levels to the right of their lines so neither collides
    # with the other annotation nor clips at the axis edge.
    for level, (x, label) in zip((1.0, 0.0), _POSTURE_MARKERS):
        ax.axvline(x, color=OKABE_ITO["vermillion"], linewidth=1.1, linestyle="--", zorder=2.5)
        ax.text(
            x + 0.09,
            n + 0.05 + 1.05 * level,
            ascii_text(label),
            fontsize=6.4,
            ha="left",
            va="bottom",
            color=OKABE_ITO["vermillion"],
            linespacing=1.2,
            zorder=4,
        )

    ax.set_xlim(2024.55, 2031.3)
    ax.set_ylim(-0.7, n + 2.9)
    ax.set_xticks(range(int(_X_MIN), int(_X_MAX) + 1))
    ax.set_xticklabels([str(year) for year in range(int(_X_MIN), int(_X_MAX) + 1)], fontsize=9)
    ax.set_yticks([])
    ax.grid(axis="x", which="major", zorder=0)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.set_xlabel("Year", fontsize=9)

    fig.suptitle("Forecast horizon by confidence tier", fontsize=11, y=0.985)
    handles = [
        Patch(facecolor=CONFIDENCE_COLORS[confidence], edgecolor="none", label=_CONFIDENCE_LABEL[confidence])
        for confidence in _CONFIDENCE_ORDER
    ]
    ax.legend(
        handles=handles,
        loc="lower left",
        bbox_to_anchor=(0.0, 1.01),
        ncol=3,
        fontsize=8.5,
        title="Confidence",
        title_fontsize=8.5,
        frameon=False,
    )

    return save_figure(fig, out)
