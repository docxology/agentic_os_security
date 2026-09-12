"""Candidate basis: one stance-profile basis per registry candidate.

``CANDIDATE_BASIS`` carries 24 rows — one per candidate id pinned in
:data:`agentic_os_security.registry.CANDIDATES`, in the same order. Each
row records why the candidate's 9-property stance profile (the 216-cell
matrix) is what it is: a dense 1–2-sentence basis grounded in the source
assessment's per-candidate sections and the documented-design facts the
v0.2.0 research wave verified (QSB cadence, Nix GHSAs, secureblue
versions, Talos/Bottlerocket boot stories, support windows, and the
incident record). ``primary_sources`` names the 3–6 bibliography keys
the basis stands on; every key must exist in
``manuscript/references.bib`` (enforced by ``tests/test_basis.py``).

No I/O at import time; the module is a pure constant surface.
"""

from __future__ import annotations

from dataclasses import dataclass

__all__ = ["CandidateBasis", "CANDIDATE_BASIS"]


@dataclass(frozen=True)
class CandidateBasis:
    """One candidate's stance-profile basis and its supporting sources.

    ``basis_id`` is the pinned registry candidate id; ``summary`` is the
    dense stance-profile basis; ``primary_sources`` is a 3–6-key tuple of
    bibliography keys.
    """

    basis_id: str
    summary: str
    primary_sources: tuple[str, ...]


#: The 24 stance-profile bases (ids pinned to
#: :data:`agentic_os_security.registry.CANDIDATES`, same order; summaries
#: grounded in the source assessment and the verified research facts;
#: ``primary_sources`` ⊆ existing bibliography keys).
CANDIDATE_BASIS: tuple[CandidateBasis, ...] = (
    CandidateBasis(
        "qubes_os",
        "The compartmentalization anchor of the review: strong containment "
        "comes from application qubes under the bare-metal Xen hypervisor "
        "with networking exiled to an untrusted qube and qrexec mediating "
        "every cross-domain channel, while TCB and update stances stay "
        "partial because dom0 or hypervisor compromise is documented as "
        "fatal and the 2026 dom0 tooling advisories (QSB-110/115/116 plus "
        "the QSB-118 qvm-copy-to-vm command injection) must be patched "
        "promptly. Compartment collapse and user-authorized clipboard or "
        "qrexec transfers remain workflow attacks the mediation points "
        "must bound.",
        ("qubes_architecture", "qubes_qrexec", "qubes_security_design_goals",
         "qsb_118", "qubes_43_release_notes"),
    ),
    CandidateBasis(
        "nixos",
        "Strong update operations come from generation-based activation and "
        "rollback over a content-addressed, sandboxed store, set against "
        "weak containment and authority because the documented sandbox "
        "concerns builds rather than runtime security, rollback does not "
        "remove malware from persistent user state, and the store is "
        "readable by all users so declarative secrets leak. The April 2026 "
        "privileged build-service symlink flaw (GHSA-g3g9) and the removal "
        "of the hardened profile keep supply-chain trust partial, not "
        "strong.",
        ("nixos_wiki", "nix_sandbox_config", "nixos_rollback_data_discussion",
         "nix_ghsa_g3g9", "nixos_2605_announcement"),
    ),
    CandidateBasis(
        "secureblue",
        "The most compelling conventional desktop candidate on documented "
        "design: strong application confinement rests on SELinux-restricted "
        "user namespaces as a default-deny posture, hardened_malloc, a "
        "confined Trivalent browser, and a SUID-less baseline, judged "
        "partial elsewhere because the feature list is project "
        "documentation rather than measured exploit resistance and "
        "persistent writable user state remains. The recommendation is "
        "conditional on the supported workflow fitting and the operator not "
        "undoing hardening for convenience.",
        ("secureblue_features", "secureblue_v491", "fedora_silverblue_technical",
         "fedora_selinux_config"),
    ),
    CandidateBasis(
        "fedora_atomic",
        "A defensible atomic baseline whose strong human-usability stance "
        "comes from a recognizable standard environment, while containment "
        "stays weak because read-only system paths do not confine an "
        "already-running application and Flatpak grants, including "
        "unrestricted bus access, must be inspected per application. The "
        "approximately 13-month release support window makes regular rebase "
        "upgrades part of the posture.",
        ("fedora_silverblue_technical", "fedora_release_lifecycle",
         "flatpak_permissions", "fedora_selinux_getting_started"),
    ),
    CandidateBasis(
        "fedora_workstation",
        "The compatibility-first control group of the desktop category: "
        "SELinux enforcing is documented without atomic rollback, so "
        "integrity, persistence, and recovery stances are weak and "
        "per-application sandboxing as deployed is the open question the "
        "category leaves unanswered. Its value is as a substrate for "
        "separately enforced agent confinement, not as a containment "
        "architecture.",
        ("fedora_selinux_config", "fedora_release_lifecycle",
         "fedora_wayland_only"),
    ),
    CandidateBasis(
        "debian_stable",
        "A conservative, sustainably maintained platform — strong human "
        "usability from coordinated advisories and recommended unattended "
        "security upgrades — with weak containment, authority, integrity, "
        "and persistence because a maintenance policy is not evidence of "
        "isolation between arbitrary desktop applications and no "
        "comprehensive default MAC baseline is documented. LTS support "
        "runs under a separate group and phase, which the stance profile "
        "refuses to conflate with the security team's.",
        ("debian_security", "debian_lts", "debian_trixie"),
    ),
    CandidateBasis(
        "ubuntu_lts",
        "Strong update-operations and human-usability stances come from "
        "five years of documented standard security maintenance, but "
        "authority and containment stay weak because classic snaps carry "
        "no confinement, so installed-as-a-snap is not evidence of "
        "isolation and the per-snap mode plus separately imposed policy "
        "decide runtime authority. Coverage must be matched to package, "
        "release, and support entitlement.",
        ("ubuntu_release_cycle", "snap_confinement", "ubuntu_2604_security"),
    ),
    CandidateBasis(
        "kicksecure",
        "A serious hardening distribution whose partial stances rest on the "
        "documented user/sysmaintenance authority split, held back from "
        "strong marks because the hardening wiki mixes research and "
        "non-default proposals with shipped defaults and verified boot is "
        "labeled planned rather than shipped. Judge the installed release "
        "and enabled settings, not the documentation's promises.",
        ("kicksecure_hardening", "kicksecure_sysmaint_split",
         "kicksecure_verified_boot"),
    ),
    CandidateBasis(
        "opensuse_aeon",
        "Snapshot-based system replacement earns strong human usability on "
        "a rolling Tumbleweed base, while containment stays weak because "
        "transactional-update prepares a new snapshot without modifying the "
        "running system and a compromised application can still read or "
        "modify its authorized user data. The review claims no basis for "
        "ranking it ahead of Qubes for containment or secureblue for "
        "documented desktop hardening.",
        ("opensuse_aeon", "opensuse_transactional_update",
         "qubes_architecture", "secureblue_features"),
    ),
    CandidateBasis(
        "opensuse_microos",
        "A deliberately understated profile: transactional server roles "
        "mirror the Aeon snapshot direction, but role-specific defaults and "
        "a distinct boot-integrity baseline were not verified in this "
        "review and are withheld as n.a. rather than inferred from the "
        "desktop variant, leaving only update-oriented partial stances. "
        "Adoption depends on validating the exact image and owning a fleet "
        "update policy.",
        ("opensuse_transactional_update", "opensuse_aeon",
         "fedora_coreos_updates"),
    ),
    CandidateBasis(
        "alpine_linux",
        "Strong trusted-computing-base marks come from a deliberately small "
        "musl/BusyBox userland with documented PIE and stack-smashing "
        "protection, while containment, authority, and application "
        "confinement stay weak because small size is not an "
        "application-isolation policy. Roughly two-year main-repository "
        "support makes it a natural microVM and base-image substrate when "
        "an externally supplied isolation boundary completes the picture.",
        ("alpine_design", "alpine_support_scope", "firecracker_jailer_docs"),
    ),
    CandidateBasis(
        "talos_linux",
        "Strong containment, integrity, persistence, and update stances "
        "follow from eliminating interfaces — no shell or interactive "
        "console, API-only management secured by mutual TLS, atomic "
        "updates, and a signed unified kernel image containing the OS — "
        "rather than from per-workload isolation, which the container "
        "runtime supplies separately. API credentials and the orchestrator "
        "remain the residual authority boundary, and it is not a general "
        "workstation substitute.",
        ("talos_repo", "talos_secureboot_docs", "talos_1_12_notes"),
    ),
    CandidateBasis(
        "bottlerocket",
        "Strong integrity and persistence marks come from a read-only "
        "dm-verity root, enforcing SELinux, kernel lockdown, stateless "
        "/etc, and no host shell or interpreters, with containment held at "
        "partial because the project's own goals distinguish host "
        "persistence and vulnerability mitigation from protection between "
        "containers, which is not VM-equivalent workload separation. "
        "Executing hostile agent-generated code still needs a disposable VM "
        "or microVM boundary beyond the container host.",
        ("bottlerocket_security_features", "talos_repo",
         "gvisor_security_policy"),
    ),
    CandidateBasis(
        "fedora_coreos",
        "The Zincati-coordinated atomic update model with retained previous "
        "deployments for rollback defines the candidate's value — automated "
        "container infrastructure for operators who can sustain its update "
        "model and own the reboot policy — while containment and "
        "confinement stay weak because the reviewed sources document no "
        "per-workload isolation beyond the container runtime. The incident "
        "record adds the boundary lesson: hostile agent workloads need an "
        "externally supplied egress boundary.",
        ("fedora_coreos_updates", "openai_hf_incident",
         "anthropic_sandboxing"),
    ),
    CandidateBasis(
        "rhel",
        "Strong update-operations and supply-chain stances come from formal "
        "security-errata classification and an accountable maintenance "
        "process bounded by product, phase, severity, and entitlement, "
        "while containment and confinement stay weak because the errata "
        "process documents maintenance, not runtime isolation quality. "
        "Agent authority needs separately imposed confinement regardless of "
        "errata discipline.",
        ("redhat_errata_policy", "debian_security", "csa_agent_insider"),
    ),
    CandidateBasis(
        "ubuntu_core",
        "Strong update, supply-chain, and application-confinement marks "
        "come from the all-snap appliance model — AppArmor, seccomp, device "
        "controls, and mount namespaces for snaps, with 15 years of "
        "maintenance and TPM-sealed full disk encryption on Core 26 — but "
        "the strict-confinement appliance model is not Ubuntu Desktop LTS "
        "with an immutability switch, and application supply concentrates "
        "in the snap store. Whether it extends to developer desktops and "
        "agent workloads remains unresolved.",
        ("ubuntu_core_confinement", "snap_confinement", "ubuntu_core_26_fde"),
    ),
    CandidateBasis(
        "whonix",
        "Anonymity engineering — the Tor gateway/workstation split on "
        "Kicksecure-derived Debian — is the boundary it draws, so authority "
        "and confinement stances stay weak and the workstation "
        "documentation's own warning governs the profile: compromise "
        "exposes the workstation's credentials and browser data and does "
        "not make an authorized agent harmless. Its value is as a component "
        "inside a broader compartmentalized design.",
        ("whonix_technical_design", "whonix_workstation_security",
         "whonix_18_support"),
    ),
    CandidateBasis(
        "tails",
        "Strong persistence-and-recovery marks come from amnesia — the "
        "strongest mainstream full-state-reset story — while containment "
        "stays weak because trace reduction and session reset do not "
        "recover information exposed during the active session. Enabling "
        "the optional encrypted Persistent Storage re-opens exactly the "
        "state the amnesic mode otherwise avoids, so the choice is "
        "deliberate per use case.",
        ("tails_overview", "tails_persistent_storage", "tails_7_12"),
    ),
    CandidateBasis(
        "openbsd",
        "Partial stances across the mitigation dimensions reflect sustained "
        "whole-system discipline — secure-by-default service choices, "
        "privilege separation, W^X, and errata/syspatch delivery on a "
        "twelve-month release window — held at partial rather than strong "
        "because the reviewed sources describe system-level mitigation, not "
        "a per-application permission model. Compatibility rather than "
        "mitigation quality limits its role to a dedicated, narrowly scoped "
        "service substrate.",
        ("openbsd_security", "openbsd_innovations", "openbsd_errata78",
         "openbsd_79"),
    ),
    CandidateBasis(
        "sel4",
        "Strong containment and trusted-computing-base marks rest on formal "
        "verification of a small core, scoped by explicit boot, hardware, "
        "and DMA-related assumptions; the authority, confinement, "
        "persistence, update, and supply-chain stances are withheld as n.a. "
        "because verification establishes assurance of the kernel, not of a "
        "complete browser, driver stack, firmware chain, or user workflow. "
        "A deployed system on seL4 must still be evaluated at its whole "
        "reachable boundary.",
        ("sel4_verification_assumptions", "sel4_2026_news", "microkit_2_3"),
    ),
    CandidateBasis(
        "genode_sculpt",
        "The clearest shipping example that capability-based authority "
        "mediation can support a usable desktop — strong containment and "
        "authority marks from Genode's microkernel architecture with "
        "sandboxed drivers and VMs, in day-to-day developer use at 26.04 — "
        "tempered by weak update and supply-chain stances from the "
        "per-release platform and niche ecosystem. seL4 proof claims do not "
        "automatically transfer to every Sculpt configuration or the "
        "applications it hosts.",
        ("genode_sculpt", "sculpt_26_04", "sel4_verification_assumptions"),
    ),
    CandidateBasis(
        "grapheneos",
        "Strong application-confinement and human-usability marks come from "
        "hardened mobile per-app sandboxing that keeps even Google Play "
        "inside the standard app sandbox — the property desktop Linux most "
        "lacks and the deployment to benchmark desktop default authority "
        "against. It is a mobile comparator, not a desktop Linux "
        "replacement: hardware, vendor, and ecosystem constraints keep the "
        "remaining stances partial.",
        ("grapheneos_features", "grapheneos_releases", "secureblue_features"),
    ),
    CandidateBasis(
        "kali_linux",
        "Weak stances across the protective properties because "
        "offensive-tool availability is not evidence of superior protection "
        "for the machine running those tools, and the rolling Debian base "
        "inherits the desktop weaknesses of the underlying platform. Its "
        "role is producing attacks, not resisting them; keep offensive "
        "tooling isolated from credentials, production access, and daily "
        "hostile-intake work.",
        ("kali_intended_use", "parrot_intended_use", "debian_security"),
    ),
    CandidateBasis(
        "parrot_security",
        "Like Kali, a tooling-focused profile with weak protective stances: "
        "documented hardening measures and forensics tuning are not a "
        "containment architecture, and defaults driven by security and "
        "forensics work differ from what daily hostile-intake work needs. "
        "Suitable only as a separate tooling environment under the assessed "
        "threat model.",
        ("parrot_intended_use", "kali_intended_use", "debian_security"),
    ),
)
