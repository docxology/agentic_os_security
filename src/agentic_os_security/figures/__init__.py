"""Figure generators for the six manuscript figures.

Every generator takes ``project_root`` and returns the written PNG path
(under ``output/figures/``).  All figures are 300 dpi, colorblind-safe, and
byte-deterministic across runs given identical inputs (see ``_common``).
"""

from ._common import (
    CONFIDENCE_COLORS,
    DETERMINISTIC_RC,
    OKABE_ITO,
    PALETTE,
    STANCE_COLORS,
    FigureSpec,
    apply_style,
    save_figure,
)
from .authority_ladder import generate_authority_ladder
from .evidence_timeline import generate_evidence_timeline
from .forecast_horizon import generate_forecast_horizon
from .orchestration_boundaries import generate_orchestration_boundaries
from .property_matrix import generate_property_matrix
from .trust_domains import generate_trust_domains

__all__ = [
    "apply_style",
    "save_figure",
    "PALETTE",
    "OKABE_ITO",
    "STANCE_COLORS",
    "CONFIDENCE_COLORS",
    "DETERMINISTIC_RC",
    "FigureSpec",
    "generate_evidence_timeline",
    "generate_property_matrix",
    "generate_trust_domains",
    "generate_authority_ladder",
    "generate_orchestration_boundaries",
    "generate_forecast_horizon",
]
