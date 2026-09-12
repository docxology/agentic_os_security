"""OS-security-stack structural invariants: 8 pinned layers with ordinals
1-8, at least two real mechanisms each, and an 8 x 8 = 64 archetype
coverage grid whose stances stay in the registry stance vocabulary and
whose archetype ids mirror the registry category vocabulary.
"""

from __future__ import annotations

import re

from agentic_os_security import registry, stack

LAYER_IDS = [
    "hardware_firmware",
    "hypervisor",
    "kernel_lsm",
    "sandbox_runtime",
    "container_microvm_runtime",
    "update_provisioning",
    "application_framework",
    "agent_runtime_tool_bridge",
]


def test_eight_unique_layers_with_pinned_ids():
    ids = [layer.layer_id for layer in stack.STACK_LAYERS]
    assert len(stack.STACK_LAYERS) == 8
    assert len(set(ids)) == 8
    assert ids == LAYER_IDS


def test_layers_are_ordered_by_consecutive_ordinals():
    ordinals = [layer.ordinal for layer in stack.STACK_LAYERS]
    assert ordinals == list(range(1, 9))


def test_every_layer_has_at_least_two_mechanisms_and_an_example():
    for layer in stack.STACK_LAYERS:
        assert layer.name.strip(), layer.layer_id
        assert len(layer.mechanisms) >= 2, layer.layer_id
        assert all(m.strip() for m in layer.mechanisms), layer.layer_id
        assert layer.candidate_example.strip(), layer.layer_id


def test_mechanism_names_are_full_words_not_codes():
    # No per-class cryptic codes: mechanism names are spelled out (letters,
    # digits inside product names, slashes, hyphens, spaces, parentheses).
    allowed = re.compile(r"^[A-Za-z0-9 /:(),.\-]+$")
    for layer in stack.STACK_LAYERS:
        for mechanism in layer.mechanisms:
            assert allowed.match(mechanism), (layer.layer_id, mechanism)


def test_archetype_ids_mirror_registry_category_vocab():
    assert set(stack.STACK_COVERAGE) == set(registry.CATEGORY_VOCAB)
    assert set(stack.ARCHETYPE_LABELS) == set(registry.CATEGORY_VOCAB)
    assert len(stack.STACK_COVERAGE) == 8


def test_coverage_grid_is_complete_64_rows_in_stance_vocab():
    stance_vocab = set(registry.STANCE_VOCAB)
    for archetype, cells in stack.STACK_COVERAGE.items():
        assert set(cells) == set(LAYER_IDS), archetype
        assert len(cells) == 8, archetype
        for layer_id, stance in cells.items():
            assert stance in stance_vocab, (archetype, layer_id, stance)
    assert sum(len(cells) for cells in stack.STACK_COVERAGE.values()) == 64


def test_stack_rows_flatten_to_64_ordered_rows():
    rows = stack.stack_rows()
    assert len(rows) == 64
    assert len(set(rows)) == 64
    # Archetypes in registry category order; layers in ordinal order.
    expected = [
        (archetype, layer.layer_id, stack.STACK_COVERAGE[archetype][layer.layer_id])
        for archetype in registry.CATEGORY_VOCAB
        for layer in stack.STACK_LAYERS
    ]
    assert rows == expected


def test_archetype_labels_are_full_words_without_codes():
    for archetype_id, label in stack.ARCHETYPE_LABELS.items():
        assert label.strip(), archetype_id
        assert "_" not in label, (archetype_id, label)
        assert label[0].isupper(), (archetype_id, label)