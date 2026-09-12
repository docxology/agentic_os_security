"""Figure generators: the eleven registry manuscript figures plus the
cover graphical abstract (which carries no ``{#fig:...}`` label and is not
part of the manuscript figure registry).

Every generator takes ``project_root`` and returns the written PNG path
(under ``output/figures/``).  All figures are 300 dpi, colorblind-safe, and
byte-deterministic across runs given identical inputs (see ``_common``).
"""

from ._common import (
    CATEGORY_COLORS,
    CATEGORY_LABELS,
    CONFIDENCE_COLORS,
    DETERMINISTIC_RC,
    OKABE_ITO,
    PALETTE,
    STANCE_COLORS,
    STANCE_GLYPHS,
    FigureSpec,
    apply_style,
    save_figure,
)
from .agent_surface import generate_agent_surface
from .authority_ladder import generate_authority_ladder
from .defensive_stack import generate_defensive_stack
from .evidence_timeline import generate_evidence_timeline
from .forecast_horizon import generate_forecast_horizon
from .graphical_abstract import generate_graphical_abstract
from .incident_lessons import generate_incidents
from .orchestration_boundaries import generate_orchestration_boundaries
from .os_stack import generate_os_stack
from .property_matrix import generate_property_matrix
from .trust_domains import generate_trust_domains
from .update_windows import generate_update_windows


__all__ = [
    "apply_style",
    "save_figure",
    "PALETTE",
    "OKABE_ITO",
    "STANCE_COLORS",
    "STANCE_GLYPHS",
    "CONFIDENCE_COLORS",
    "CATEGORY_COLORS",
    "CATEGORY_LABELS",
    "DETERMINISTIC_RC",
    "FigureSpec",
    "generate_incidents",
    "generate_evidence_timeline",
    "generate_defensive_stack",
    "generate_trust_domains",
    "generate_authority_ladder",
    "generate_os_stack",
    "generate_orchestration_boundaries",
    "generate_agent_surface",
    "generate_forecast_horizon",
    "generate_update_windows",
    "generate_graphical_abstract",
]
