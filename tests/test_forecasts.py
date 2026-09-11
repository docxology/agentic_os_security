"""Forecast structural invariants: >=10 entries, confidence vocabulary,
horizon window 2028-2031, counts_by_confidence consistency, and the
pinned claim-to-tier mapping (compartmentalization value high; composition
outcomes moderate; named-distribution winner low).
"""

from __future__ import annotations

import re

from agentic_os_security import forecasts

CONFIDENCE_VOCAB = {"high", "moderate", "low"}


def test_at_least_ten_unique_forecasts():
    ids = [f.forecast_id for f in forecasts.FORECASTS]
    assert len(forecasts.FORECASTS) >= 10
    assert len(set(ids)) == len(ids)


def test_confidence_vocabulary_and_horizon_window():
    for forecast in forecasts.FORECASTS:
        assert forecast.confidence in CONFIDENCE_VOCAB, forecast.forecast_id
        assert forecast.claim.strip(), forecast.forecast_id
        low, high = forecast.horizon
        assert isinstance(low, int) and isinstance(high, int)
        assert low <= high, (forecast.forecast_id, forecast.horizon)
        assert forecast.horizon in {
            forecasts.HORIZON,
            forecasts.NEAR_TERM_HORIZON,
        }, (forecast.forecast_id, forecast.horizon)


def test_counts_by_confidence_consistent_with_forecasts():
    counts = forecasts.counts_by_confidence()
    assert set(counts) == CONFIDENCE_VOCAB
    assert sum(counts.values()) == len(forecasts.FORECASTS)
    from collections import Counter

    assert counts == dict(Counter(f.confidence for f in forecasts.FORECASTS))


def test_high_confidence_forecasts_cover_pinned_topics():
    # Brief: high = compartmentalization value, capability mediation,
    # fast replacement, small-interfaces investment, defaults over menus.
    high_claims = " ".join(
        f.claim.lower() for f in forecasts.FORECASTS if f.confidence == "high"
    )
    for topic in ("compartmental", "mediation", "replace", "interface", "default"):
        assert topic in high_claims, topic


def test_moderate_confidence_covers_composition_outcomes():
    moderate_claims = " ".join(
        f.claim.lower() for f in forecasts.FORECASTS if f.confidence == "moderate"
    )
    assert "composition" in moderate_claims or "integration" in moderate_claims


def test_named_distribution_winner_is_low_confidence_or_cautioned():
    # Any forecast predicting a single named-distribution winner must be low
    # confidence; the source's overconfidence cautions appear as
    # low-confidence negative forecasts. The winner entry is identified by
    # its pinned id, not by claim text.
    by_id = {f.forecast_id: f for f in forecasts.FORECASTS}
    winner = by_id["no_named_distribution_winner"]
    assert winner.confidence == "low", winner.forecast_id
    assert winner.horizon == forecasts.HORIZON


def test_forecast_ids_are_slug_like():
    slug = re.compile(r"^[a-z][a-z0-9_]*$")
    for forecast in forecasts.FORECASTS:
        assert slug.match(forecast.forecast_id), forecast.forecast_id
