"""Forecasts for the approximate 2028-2031 horizon.

The source assessment's trajectory section pins the confidence
vocabulary (``high | moderate | low``) and the horizon (2028-2031;
near-term entries span 2026-2031). Forecasts are reasoned
expectations, not claims that a project has committed to or will
deliver a particular release, and not measurements of current
capability:

- **high** — architectural bets the source marks highest-confidence
  (compartmentalization value, capability mediation, fast replacement
  over repair, small-interface investment, defaults over hardening
  menus).
- **moderate** — composition and integration outcomes that depend on
  execution (Qubes disaggregation, NixOS confinement/integrity
  integration, conventional-desktop authority narrowing).
- **low** — predictions the source explicitly marks as overconfident,
  including negative forecasts cautioning against them (any
  named-distribution winner 2028-2031, verified-microkernel-implies-
  best-desktop, memory-safe-rewrite-eliminates-logic-bugs,
  reproducible-packages-eliminate-supply-chain-compromise,
  conventional-Linux-obsolescence).

No I/O at import time; the module is a pure constant surface.
"""

from __future__ import annotations

from dataclasses import dataclass

__all__ = ["Forecast", "CONFIDENCE_VOCAB", "HORIZON", "NEAR_TERM_HORIZON", "FORECASTS", "counts_by_confidence"]


@dataclass(frozen=True)
class Forecast:
    """One reasoned expectation: claim, confidence tier, horizon years."""

    forecast_id: str
    claim: str
    confidence: str
    horizon: tuple[int, int]


#: Forecast confidence vocabulary (pinned).
CONFIDENCE_VOCAB: tuple[str, ...] = ("high", "moderate", "low")

#: Standard forecast horizon (pinned).
HORIZON: tuple[int, int] = (2028, 2031)

#: Near-term horizon for high-confidence architectural bets already under way.
NEAR_TERM_HORIZON: tuple[int, int] = (2026, 2031)

#: The forecast set (confidence tiers pinned by the source's trajectory and
#: overconfidence sections).
FORECASTS: tuple[Forecast, ...] = (
    Forecast(
        "compartmentalization_value_rises",
        "Compartmentalization becomes more valuable: if exposed applications fail more "
        "frequently, a design that protects other domains after that failure becomes more "
        "attractive — supporting the Qubes approach and similarly strict task isolation, not "
        "assuming any hypervisor is unbreakable.",
        "high",
        NEAR_TERM_HORIZON,
    ),
    Forecast(
        "capability_mediation_central",
        "Capability mediation becomes as important as exploit mitigation: more capable agents "
        "make it more important to distinguish what they can propose from what they can "
        "authorize; OS isolation and application/API authorization must work together.",
        "high",
        HORIZON,
    ),
    Forecast(
        "replacement_beats_repair",
        "Fast, trustworthy replacement beats elaborate repair: known-good reconstruction and "
        "credential revocation are the attractive responses to uncertain compromise — "
        "favoring declarative and image-based operations when mutable data and secrets are "
        "handled separately.",
        "high",
        HORIZON,
    ),
    Forecast(
        "small_interface_investment",
        "Small interfaces deserve disproportionate investment: the components that move bytes, "
        "credentials, approvals, and device access across domains are natural targets whose "
        "size, privilege, implementation language, and policy semantics can matter more than "
        "the number of isolated workloads.",
        "high",
        HORIZON,
    ),
    Forecast(
        "defaults_over_hardening_menus",
        "Security defaults matter more than optional hardening menus: a coherent baseline "
        "that survives browser updates, developer workflows, and ordinary maintenance is more "
        "valuable than many switches operators cannot safely combine.",
        "high",
        HORIZON,
    ),
    Forecast(
        "qubes_disaggregation_trajectory",
        "For Qubes, further disaggregation and simplification reduce the privileged attack "
        "surface without increasing operational fragility — conditional on integration and "
        "maintenance quality rather than architectural promise.",
        "moderate",
        HORIZON,
    ),
    Forecast(
        "nixos_confinement_integration",
        "For NixOS, reproducible configuration becomes integrated with a coherent confinement "
        "and integrity baseline rather than remaining largely an operator-assembled "
        "composition.",
        "moderate",
        HORIZON,
    ),
    Forecast(
        "desktop_authority_narrowing",
        "For hardened conventional desktops, application permissions and agent authority "
        "become substantially narrower while remaining usable.",
        "moderate",
        HORIZON,
    ),
    Forecast(
        "composition_property_convergence",
        "The attractive destination ships: a compartmentalized system whose small privileged "
        "services are memory-safe where feasible, whose core security properties have strong "
        "verification, whose boot and update paths authenticate the intended software, and "
        "whose environments can be independently rebuilt — each property closing a different "
        "class of failure and none substituting for the others.",
        "moderate",
        HORIZON,
    ),
    Forecast(
        "no_named_distribution_winner",
        "No unconditional prediction of which named distribution will be most secure in "
        "2028-2031: project execution, hardware changes, ecosystem support, and unknown "
        "vulnerabilities could alter the ordering.",
        "low",
        HORIZON,
    ),
    Forecast(
        "no_verified_microkernel_desktop_winner",
        "A verified microkernel does not automatically yield the best practical desktop; "
        "predicting that outcome is premature.",
        "low",
        HORIZON,
    ),
    Forecast(
        "no_memory_safe_logic_bug_elimination",
        "A memory-safe rewrite does not eliminate logic vulnerabilities; predicting that "
        "outcome is premature.",
        "low",
        HORIZON,
    ),
    Forecast(
        "no_reproducible_supply_chain_elimination",
        "Reproducible packages do not eliminate supply-chain compromise; predicting that "
        "outcome is premature.",
        "low",
        HORIZON,
    ),
    Forecast(
        "no_conventional_linux_obsolescence",
        "Conventional Linux is not declared obsolete merely because offensive agents improve; "
        "the security outcome depends on the whole reachable system, the attacker's "
        "objective, and how competently the deployment is maintained.",
        "low",
        HORIZON,
    ),
)


def counts_by_confidence() -> dict:
    """Return forecast counts per confidence tier, all 3 tiers present."""
    counts = {confidence: 0 for confidence in CONFIDENCE_VOCAB}
    for forecast in FORECASTS:
        counts[forecast.confidence] += 1
    return counts
