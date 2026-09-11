"""Deterministic build-clock for the ``agentic_os_security`` data layer.

Generated artifacts must contain no wall-clock time. Every timestamp an
artifact carries is derived from the ``SOURCE_DATE_EPOCH`` environment
variable when the build is invoked, falling back to the pinned review
date (2026-09-10) at noon UTC. All three helpers therefore return the
same value on every invocation of a given build, and identical values
across builds that share ``SOURCE_DATE_EPOCH``.

Contract (brief ``## src/ API contract``):

- :func:`build_timestamp` -> ISO 8601 UTC build timestamp string.
- :func:`build_date` -> ``YYYY-MM-DD`` build date string.
- :func:`build_epoch` -> integer Unix epoch seconds.
"""

from __future__ import annotations

import os
from datetime import datetime, timezone

__all__ = ["REVIEW_DATE", "FALLBACK_EPOCH", "SOURCE_DATE_EPOCH_VAR", "build_timestamp", "build_date", "build_epoch"]

#: Pinned review date from ``manuscript/config.yaml`` (``CONFIG_REVIEW_DATE``).
REVIEW_DATE: str = "2026-09-10"

#: Deterministic fallback instant: REVIEW_DATE at noon UTC.
_FALLBACK_DT: datetime = datetime(2026, 9, 10, 12, 0, 0, tzinfo=timezone.utc)

#: Integer Unix epoch seconds of the deterministic fallback instant.
FALLBACK_EPOCH: int = int(_FALLBACK_DT.timestamp())

#: Environment variable consulted for reproducible builds.
SOURCE_DATE_EPOCH_VAR: str = "SOURCE_DATE_EPOCH"


def _build_dt() -> datetime:
    """Return the deterministic build datetime.

    Honors ``SOURCE_DATE_EPOCH`` (integer Unix seconds) when set; the
    fallback is the pinned review date at noon UTC. Raises
    :class:`ValueError` when ``SOURCE_DATE_EPOCH`` is present but not
    an integer, so a malformed reproducible-build invocation fails
    loudly instead of silently introducing nondeterminism.
    """
    raw = os.environ.get(SOURCE_DATE_EPOCH_VAR)
    if raw is None or raw.strip() == "":
        return _FALLBACK_DT
    try:
        epoch = int(raw.strip())
    except ValueError as exc:
        raise ValueError(
            f"{SOURCE_DATE_EPOCH_VAR} must be an integer Unix timestamp; got {raw!r}"
        ) from exc
    return datetime.fromtimestamp(epoch, tz=timezone.utc)


def build_timestamp() -> str:
    """Return the deterministic ISO 8601 UTC build timestamp.

    Examples: ``"2026-09-10T12:00:00+00:00"`` (fallback) or the
    ``SOURCE_DATE_EPOCH``-derived equivalent.
    """
    return _build_dt().isoformat()


def build_date() -> str:
    """Return the deterministic ``YYYY-MM-DD`` build date (UTC)."""
    return _build_dt().date().isoformat()


def build_epoch() -> int:
    """Return the deterministic build instant as integer Unix seconds."""
    return int(_build_dt().timestamp())
