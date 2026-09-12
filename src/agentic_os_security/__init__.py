"""Agentic OS Security — src data layer.

Canonical data surface for "Agentic Security and Operating Systems":
the evaluation registry, evidence base, threat-model constants,
trust-domain architecture, forecast set, experiment configuration, and
deterministic build clock. Sibling modules (figures, analysis,
manuscript variables) and the scripts (00_preflight.py,
10_evaluation_analysis.py, z_generate_manuscript_variables.py) consume
the names re-exported here.

Pure Python; no ``infrastructure`` imports; no I/O at import time.
"""

from .build_clock import (
    FALLBACK_EPOCH,
    REVIEW_DATE,
    SOURCE_DATE_EPOCH_VAR,
    build_date,
    build_epoch,
    build_timestamp,
)
from .evidence import (
    CAPABILITY_BASELINE,
    LESSON_TAXONOMY,
    SOURCES,
    TIER_VOCAB,
    LessonClass,
    Source,
    sources_by_tier,
)
from .basis import CANDIDATE_BASIS, CandidateBasis
from .experiment_config import (
    ExperimentConfigError,
    REQUIRED_KEY_SHAPES,
    load_experiment_config,
)
from .forecasts import (
    CONFIDENCE_VOCAB,
    FORECASTS,
    HORIZON,
    NEAR_TERM_HORIZON,
    Forecast,
    counts_by_confidence,
)
from .project_paths import (
    PACKAGE_DIR_NAME,
    data_dir,
    figures_dir,
    find_project_root,
    output_dir,
)
from .registry import (
    CANDIDATES,
    CATEGORY_VOCAB,
    PROPERTIES,
    SCENARIOS,
    STANCE_VOCAB,
    Candidate,
    Property,
    Scenario,
    candidates_by_category,
    category_counts,
    matrix_rows,
    stance_counts,
)
from .threat_model import (
    ADVERSARY_ASSUMPTIONS,
    AGENT_CAPABILITY_CLASSES,
    AUTHORITY_LADDER,
    AUTHORITY_LADDER_RUNGS,
    FAILURE_PATHS,
    AuthorityRung,
    FailurePath,
)
from .trust_domains import (
    CONFIGURATION_INVARIANTS,
    CONTROLS,
    TRUST_DOMAINS,
    Control,
    TrustDomain,
)

__all__ = [
    # registry
    "Property",
    "Candidate",
    "Scenario",
    "PROPERTIES",
    "CANDIDATES",
    "SCENARIOS",
    "STANCE_VOCAB",
    "CATEGORY_VOCAB",
    "matrix_rows",
    "category_counts",
    "stance_counts",
    "candidates_by_category",
    # evidence
    "Source",
    "SOURCES",
    "TIER_VOCAB",
    "LessonClass",
    "LESSON_TAXONOMY",
    "CandidateBasis",
    "CANDIDATE_BASIS",
    "CAPABILITY_BASELINE",
    "sources_by_tier",
    # threat model
    "FailurePath",
    "AuthorityRung",
    "FAILURE_PATHS",
    "ADVERSARY_ASSUMPTIONS",
    "AUTHORITY_LADDER",
    "AUTHORITY_LADDER_RUNGS",
    "AGENT_CAPABILITY_CLASSES",
    # trust domains
    "TrustDomain",
    "TRUST_DOMAINS",
    "Control",
    "CONTROLS",
    "CONFIGURATION_INVARIANTS",
    # forecasts
    "Forecast",
    "FORECASTS",
    "CONFIDENCE_VOCAB",
    "HORIZON",
    "NEAR_TERM_HORIZON",
    "counts_by_confidence",
    # experiment config
    "ExperimentConfigError",
    "REQUIRED_KEY_SHAPES",
    "load_experiment_config",
    # build clock
    "REVIEW_DATE",
    "FALLBACK_EPOCH",
    "SOURCE_DATE_EPOCH_VAR",
    "build_timestamp",
    "build_date",
    "build_epoch",
    # project paths
    "PACKAGE_DIR_NAME",
    "find_project_root",
    "output_dir",
    "figures_dir",
    "data_dir",
]

__version__ = "0.1.0"
