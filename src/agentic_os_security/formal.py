"""Formal definitions: 8 numbered formalisms for the v0.4.0 manuscript round.

Each definition carries a LaTeX-renderable inline-math statement (ASCII
only — LaTeX escapes, never unicode), an informal gloss, the manuscript
surface where its equation embed lives, and citation keys into
``manuscript/references.bib``. The ids are pinned and stable: they are
the ``{#eq:...}`` label registry consumed by the manuscript sections and
``tests/test_manuscript_structure.py``.

Surfaces follow the v0.4.0 placement plan:

- ``registry/evaluation matrix`` — §03, new H2 "A formal stance model".
- ``sec:agentic_authority`` — §09 ladder order and defense composition.
- ``sec:orchestration`` — §12 delta-bounded delegation.
- ``sec:configuration_authorization`` — §13 invariant predicate.
- ``sec:servers`` — §07 stack layering.
- ``registry/update windows`` — the update-window figure/section ground.

No I/O at import time; the module is a pure constant surface.
"""

from __future__ import annotations

from dataclasses import dataclass

__all__ = ["FormalDefinition", "FORMAL_DEFINITIONS", "definitions_by_surface"]


@dataclass(frozen=True)
class FormalDefinition:
    """One numbered formalism: LaTeX statement, gloss, surface, citations."""

    definition_id: str
    name: str
    formal_latex: str
    informal: str
    surface: str
    citation_keys: tuple[str, ...]


#: The 8 formal definitions (ids pinned; statements pure-ASCII LaTeX inline
#: math — the digits 24, 9, and 216 are the registered matrix constants).
FORMAL_DEFINITIONS: tuple[FormalDefinition, ...] = (
    FormalDefinition(
        "stance_mapping",
        "Stance mapping",
        (
            r"\sigma\colon C \times P \to S \cup \{\textit{n/a}\},\quad"
            r"|C| = 24,\ |P| = 9,\ |\operatorname{dom}(\sigma)| = 216"
        ),
        (
            "The evaluation is a total function from every candidate-property "
            "pair to a stance: with 24 candidates and 9 properties, the "
            "matrix is 216 stance cells, and n/a marks the pairs a candidate "
            "does not engage at its architectural level."
        ),
        "registry/evaluation matrix",
        ("cif_formal_2026",),
    ),
    FormalDefinition(
        "stance_order",
        "Stance order",
        r"\textit{strong} \succ \textit{partial} \succ \textit{weak},\quad"
        r"\textit{n/a} \notin \operatorname{dom}(\succ)",
        (
            "Stances form a preference order over postures — strong is "
            "strictly better than partial, partial than weak — while n/a "
            "sits outside the order entirely: it records non-engagement, "
            "not a worse posture than weak."
        ),
        "registry/evaluation matrix",
        ("cif_formal_2026",),
    ),
    FormalDefinition(
        "authority_ladder_order",
        "Authority-ladder order",
        (
            r"\textit{propose} \prec \textit{stage} \prec \textit{authorize}"
            r" \prec \textit{exercise} \prec \textit{audit}"
            r" \prec \textit{revoke},\quad"
            r"\forall a\colon \textit{exercise}(a) \Rightarrow"
            r" \textit{approved}_{\textit{external}}(a)"
        ),
        (
            "The six rungs are a total order, and the ladder carries one "
            "invariant: an agent exercising authority must have had it "
            "approved by an external principal — no rung lets the agent "
            "enlarge its own authorization."
        ),
        "sec:agentic_authority",
        ("cif_formal_2026",),
    ),
    FormalDefinition(
        "delegation_bound",
        "Delta-bounded delegation",
        (
            r"\textit{trust}(a \to c) \le \delta \cdot"
            r" \textit{trust}(a \to b),\quad a \to b \to c"
        ),
        (
            "Across an agent-to-agent delegation chain a to b to c, the "
            "trust the origin extends to the final delegate is bounded by "
            "delta times the trust of the intermediate hop: each hop may "
            "narrow the authority it passes, never widen it, so trust "
            "cannot amplify along the chain."
        ),
        "sec:orchestration",
        ("cif_formal_2026",),
    ),
    FormalDefinition(
        "defense_composition",
        "Defense composition",
        r"D = d_1 \circ d_2 \circ \cdots \circ d_8",
        (
            "Layered controls compose as a single defense object: the eight "
            "mitigation classes act as one composed defense D rather than "
            "an ad-hoc stack of independent toggles, so the composition can "
            "be reasoned about as a whole."
        ),
        "sec:agentic_authority",
        ("cif_formal_2026",),
    ),
    FormalDefinition(
        "invariant_predicate",
        "Invariant predicate",
        (
            r"\forall g \in G_{\textit{agent}}\colon"
            r" \neg \textit{reachable}(g, \textit{violate}(\iota_i)),"
            r"\quad i = 1, \ldots, 9"
        ),
        (
            "Each of the nine configuration invariants is a predicate over "
            "unreachable states: no agent goal may reach a configuration "
            "state that violates it. Authorization is enforced by making "
            "the violating state unreachable, not by trusting the agent to "
            "refrain."
        ),
        "sec:configuration_authorization",
        ("cif_formal_2026", "cif_validation_2026"),
    ),
    FormalDefinition(
        "stack_layering",
        "Stack layering",
        (
            r"L_1 \prec L_2 \prec L_3 \prec L_4 \prec L_5 \equiv L_6 \prec"
            r" L_7 \prec L_8;\quad"
            r"\forall i < 8\colon \textit{compromise}(L_i) \not\Rightarrow"
            r" \textit{authority}(L_{i+1})"
        ),
        (
            "The operating-system stack is an ordered defense sequence from "
            "hardware and firmware up to the agent runtime, with the "
            "container/microVM runtime and the update/provisioning layer as "
            "peers; the layering carries one requirement — a compromise at "
            "one layer must not grant authority at the next."
        ),
        "sec:servers",
        ("qubes_architecture", "nist_sp800_207"),
    ),
    FormalDefinition(
        "update_window_semantics",
        "Update-window semantics",
        (
            r"W(c) \in \mathbb{N} \cup \{\infty\},\quad"
            r"\textit{risk}(c, t) \nearrow \textit{as}\ t \to W(c)"
        ),
        (
            "A candidate's support window W is a fixed number of months or "
            "infinity under a rolling model; as the window is exhausted the "
            "risk of running the candidate grows, which is why the review "
            "treats an exhausted window as a posture change, not a footnote."
        ),
        "registry/update windows",
        ("fedora_release_lifecycle", "ubuntu_release_cycle", "nixos_2605_announcement"),
    ),
)


def definitions_by_surface() -> dict[str, list[FormalDefinition]]:
    """Group the 8 formal definitions by their manuscript surface.

    Returns a dict keyed by surface string, with definitions in
    :data:`FORMAL_DEFINITIONS` order within each group.
    """
    grouped: dict[str, list[FormalDefinition]] = {}
    for definition in FORMAL_DEFINITIONS:
        grouped.setdefault(definition.surface, []).append(definition)
    return grouped