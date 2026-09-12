"""OS-security-stack structured layer: 8 layers, 8 archetype coverage rows.

The v0.4.0 round adds a structured model of the operating-system
security stack that the manuscript's server-infrastructure section and
the new ``{#fig:os_stack}`` figure both draw on:

- :data:`STACK_LAYERS` — the 8 layers, ordinal 1 (hardware and firmware,
  the bottom-most trust anchor, drawn at the top of the figure) through
  ordinal 8 (the agent runtime and its tool bridge), each with real
  documented mechanisms.
- :data:`STACK_COVERAGE` — how strongly each of the 8 candidate-category
  archetypes (ids mirror :data:`agentic_os_security.registry.CATEGORY_VOCAB`)
  covers each layer, judged from documented designs only.
- :data:`ARCHETYPE_LABELS` — full-word labels (no codes) for the figure
  heat columns and the coverage CSV.
- :func:`stack_rows` — the 8 x 8 = 64 flattened (archetype, layer,
  stance) coverage rows.

Coverage stances use the same vocabulary as the property matrix
(``strong | partial | weak | n_a``): ``strong`` means the archetype's
documented designs make the layer a first-class mechanism, ``partial``
means real but secondary or uneven coverage, ``weak`` means the
mechanism is largely absent, and ``n_a`` means the archetype does not
engage the layer at its architectural level. No I/O at import time.
"""

from __future__ import annotations

from dataclasses import dataclass

__all__ = [
    "StackLayer",
    "STACK_LAYERS",
    "ARCHETYPE_LABELS",
    "STACK_COVERAGE",
    "stack_rows",
]


@dataclass(frozen=True)
class StackLayer:
    """One layer of the OS security stack: id, ordinal, mechanisms, example."""

    layer_id: str
    ordinal: int
    name: str
    mechanisms: tuple[str, ...]
    candidate_example: str


#: The 8 stack layers (ids pinned; ordinal 1 = hardware/firmware top of the
#: figure ... ordinal 8 = agent runtime/tool bridge; mechanisms grounded in
#: documented technology — TPM/measured boot/IOMMU; Xen/Firecracker/Cloud
#: Hypervisor; SELinux/AppArmor/Landlock/seccomp; bubblewrap/seatbelt/
#: gVisor/jailer; Kata/libkrun/systemd sandboxing; A/B atomic and
#: transactional updates, reproducible builds, signed updates;
#: Flatpak/snap/entitlements/browser sandboxing; MCP OAuth binding, tool
#: annotations, classifier escalation, egress proxy).
STACK_LAYERS: tuple[StackLayer, ...] = (
    StackLayer(
        "hardware_firmware",
        1,
        "Hardware and firmware",
        (
            "TPM measured boot",
            "verified boot chains",
            "IOMMU DMA isolation",
            "SMM/UEFI hardening",
        ),
        "Talos Linux (measured and verified boot)",
    ),
    StackLayer(
        "hypervisor",
        2,
        "Hypervisor",
        (
            "Xen type-1 hypervisor",
            "microVM VMMs: Firecracker and Cloud Hypervisor",
        ),
        "Qubes OS (Xen-based compartmentalization)",
    ),
    StackLayer(
        "kernel_lsm",
        3,
        "Kernel and LSM",
        (
            "SELinux",
            "AppArmor",
            "Landlock",
            "seccomp filters",
        ),
        "Fedora (SELinux enforcing)",
    ),
    StackLayer(
        "sandbox_runtime",
        4,
        "Sandbox runtime",
        (
            "bubblewrap",
            "macOS Seatbelt",
            "gVisor",
            "Firecracker jailer",
        ),
        "Codex CLI (Seatbelt/Landlock sandboxing)",
    ),
    StackLayer(
        "container_microvm_runtime",
        5,
        "Container and microVM runtime",
        (
            "Kata Containers",
            "libkrun",
            "systemd per-service sandboxing",
        ),
        "Fedora CoreOS (systemd-sandboxed services)",
    ),
    StackLayer(
        "update_provisioning",
        6,
        "Update and provisioning",
        (
            "A/B atomic image updates",
            "transactional-update",
            "reproducible builds",
            "signed update channels",
        ),
        "NixOS (reproducible, signed, atomic updates)",
    ),
    StackLayer(
        "application_framework",
        7,
        "Application framework",
        (
            "Flatpak sandboxing",
            "snap confinement",
            "macOS-style entitlements",
            "browser process sandboxing",
        ),
        "Flatpak (desktop application confinement)",
    ),
    StackLayer(
        "agent_runtime_tool_bridge",
        8,
        "Agent runtime and tool bridge",
        (
            "MCP OAuth tool-server binding",
            "tool annotations",
            "classifier-gated escalation",
            "egress proxy",
        ),
        "MCP tool bridge (annotated, bound servers)",
    ),
)

#: Full-word archetype labels (no codes) for the os_stack figure heat
#: columns and the coverage CSV. Ids mirror ``registry.CATEGORY_VOCAB``.
ARCHETYPE_LABELS: dict[str, str] = {
    "compartmentalized": "Compartmentalized",
    "reproducible": "Reproducible",
    "desktop": "Desktop",
    "server": "Server",
    "anonymity": "Anonymity",
    "high_assurance": "High assurance",
    "mobile": "Mobile",
    "offensive_toolkit": "Offensive toolkit",
}

#: Archetype x layer coverage — 8 x 8 = 64 stance cells judged from
#: documented designs. ``strong`` = first-class mechanism in the
#: archetype's flagship designs (e.g. compartmentalized at the hypervisor
#: and sandbox runtime; reproducible at update/provisioning; mobile at
#: verified boot and app sandboxing; server at MAC frameworks, container
#: runtimes, and atomic updates); ``partial`` = real but secondary or
#: uneven; ``weak`` = largely absent; ``n_a`` = not engaged at the
#: archetype's architectural level (offensive toolkits and anonymity and
#: high-assurance systems ship no agent tool bridge to cover).
STACK_COVERAGE: dict[str, dict[str, str]] = {
    "compartmentalized": {
        "hardware_firmware": "partial",
        "hypervisor": "strong",
        "kernel_lsm": "partial",
        "sandbox_runtime": "strong",
        "container_microvm_runtime": "partial",
        "update_provisioning": "partial",
        "application_framework": "strong",
        "agent_runtime_tool_bridge": "weak",
    },
    "reproducible": {
        "hardware_firmware": "partial",
        "hypervisor": "weak",
        "kernel_lsm": "partial",
        "sandbox_runtime": "partial",
        "container_microvm_runtime": "partial",
        "update_provisioning": "strong",
        "application_framework": "weak",
        "agent_runtime_tool_bridge": "weak",
    },
    "desktop": {
        "hardware_firmware": "partial",
        "hypervisor": "weak",
        "kernel_lsm": "strong",
        "sandbox_runtime": "partial",
        "container_microvm_runtime": "partial",
        "update_provisioning": "partial",
        "application_framework": "strong",
        "agent_runtime_tool_bridge": "weak",
    },
    "server": {
        "hardware_firmware": "partial",
        "hypervisor": "partial",
        "kernel_lsm": "strong",
        "sandbox_runtime": "partial",
        "container_microvm_runtime": "strong",
        "update_provisioning": "strong",
        "application_framework": "weak",
        "agent_runtime_tool_bridge": "partial",
    },
    "anonymity": {
        "hardware_firmware": "partial",
        "hypervisor": "partial",
        "kernel_lsm": "partial",
        "sandbox_runtime": "partial",
        "container_microvm_runtime": "weak",
        "update_provisioning": "weak",
        "application_framework": "partial",
        "agent_runtime_tool_bridge": "n_a",
    },
    "high_assurance": {
        "hardware_firmware": "partial",
        "hypervisor": "strong",
        "kernel_lsm": "strong",
        "sandbox_runtime": "strong",
        "container_microvm_runtime": "n_a",
        "update_provisioning": "partial",
        "application_framework": "strong",
        "agent_runtime_tool_bridge": "n_a",
    },
    "mobile": {
        "hardware_firmware": "strong",
        "hypervisor": "n_a",
        "kernel_lsm": "strong",
        "sandbox_runtime": "strong",
        "container_microvm_runtime": "weak",
        "update_provisioning": "partial",
        "application_framework": "strong",
        "agent_runtime_tool_bridge": "weak",
    },
    "offensive_toolkit": {
        "hardware_firmware": "weak",
        "hypervisor": "weak",
        "kernel_lsm": "weak",
        "sandbox_runtime": "weak",
        "container_microvm_runtime": "weak",
        "update_provisioning": "partial",
        "application_framework": "weak",
        "agent_runtime_tool_bridge": "weak",
    },
}


def stack_rows() -> list[tuple[str, str, str]]:
    """Flatten the archetype x layer grid to 8 x 8 = 64 (archetype, layer,
    stance) rows.

    Archetypes iterate in :data:`ARCHETYPE_LABELS` (registry category)
    order; layers iterate in ordinal order within each archetype, so the
    row order is stable for CSV serialization.
    """
    layer_order = [layer.layer_id for layer in STACK_LAYERS]
    return [
        (archetype, layer_id, STACK_COVERAGE[archetype][layer_id])
        for archetype in ARCHETYPE_LABELS
        for layer_id in layer_order
    ]

