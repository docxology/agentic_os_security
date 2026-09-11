"""Canonical registry: 9 properties, 24 candidates, 8 scenarios.

This module is the single source of truth for the evaluation matrix —
the candidate x property stance grid (24 x 9 = 216 cells) consumed by
analysis, figures, manuscript variables, and the tests. Content is
pinned by the shared brief: property ids, candidate ids, scenario ids,
the stance vocabulary ``strong | partial | weak | n_a``, and the
8-category candidate vocabulary ``compartmentalized | reproducible |
desktop | server | anonymity | high_assurance | mobile |
offensive_toolkit``.

Every ``design_summary``, ``limitation``, ``assessment``, and
``trajectory_note`` is an analytical judgment grounded in documented
designs, project advisories, and the source assessment ("Secure Linux
in the age of offensive AI agents"), not a penetration-test result.
``n_a`` marks a property the reviewed sources withhold for a candidate
(e.g. deployment-dependent properties of research microkernels);
absence of a confirmed feature in this review is not proof of absence.

No I/O and no wall-clock: the module is a pure constant surface.
"""

from __future__ import annotations

from dataclasses import dataclass

__all__ = [
    "Property",
    "Candidate",
    "Scenario",
    "STANCE_VOCAB",
    "CATEGORY_VOCAB",
    "PROPERTIES",
    "CANDIDATES",
    "SCENARIOS",
    "matrix_rows",
    "category_counts",
    "stance_counts",
    "candidates_by_category",
]


@dataclass(frozen=True)
class Property:
    """One evaluation property: the question to ask and its significance."""

    property_id: str
    name: str
    question: str
    significance: str


@dataclass(frozen=True)
class Candidate:
    """One candidate system with its documented-design judgment and 9 stances."""

    candidate_id: str
    name: str
    category: str
    design_summary: str
    limitation: str
    assessment: str
    trajectory_note: str
    property_stance: dict[str, str]


@dataclass(frozen=True)
class Scenario:
    """One scenario recommendation with the condition that could change it."""

    scenario_id: str
    situation: str
    recommendation: str
    change_condition: str


#: Stance vocabulary for the candidate x property matrix (pinned).
STANCE_VOCAB: tuple[str, ...] = ("strong", "partial", "weak", "n_a")

#: 8-category candidate vocabulary (pinned).
CATEGORY_VOCAB: tuple[str, ...] = (
    "compartmentalized",
    "reproducible",
    "desktop",
    "server",
    "anonymity",
    "high_assurance",
    "mobile",
    "offensive_toolkit",
)

#: The 9 evaluation properties (ids pinned; wording mirrors the source's
#: "What matters more than a distribution label" table).
PROPERTIES: tuple[Property, ...] = (
    Property(
        "containment",
        "Containment",
        "What remains protected after the browser or agent is fully controlled?",
        "A prevention failure should not automatically become whole-machine compromise.",
    ),
    Property(
        "authority",
        "Authority",
        "What can the process already read, transmit, sign, or change?",
        "Excessive legitimate permissions can bypass the need for an exploit.",
    ),
    Property(
        "trusted_computing_base",
        "Trusted computing base",
        "Which privileged components must all remain correct?",
        "A small, carefully constrained boundary is preferable to many privileged integrations.",
    ),
    Property(
        "application_confinement",
        "Application confinement",
        "Are permissions restrictive by default and actually compatible with the applications?",
        "A theoretical policy is not protection if users routinely disable it.",
    ),
    Property(
        "integrity",
        "Integrity",
        "What verifies the boot chain and deployed software, and who holds the keys?",
        "Authenticity, runtime integrity, and resistance to rollback are distinct properties.",
    ),
    Property(
        "persistence_recovery",
        "Persistence and recovery",
        "Which state survives replacement or reboot?",
        "Rebuilding the system is insufficient if malicious user state or stolen credentials survive.",
    ),
    Property(
        "update_operations",
        "Update operations",
        "How quickly do fixes reach every active environment?",
        "A strong architecture with neglected templates or pinned dependencies can lose its advantage.",
    ),
    Property(
        "supply_chain_trust",
        "Supply-chain trust",
        "Who may introduce or approve new executable code?",
        "Reproducibility and signatures answer different questions from whether code is benign.",
    ),
    Property(
        "human_usability",
        "Human usability",
        "Will the owner preserve the intended boundaries during real work?",
        "Sustainable security is more valuable than a configuration abandoned under pressure.",
    ),
)

#: The 24 candidates (ids and categories pinned; judgments grounded in the
#: source assessment's per-candidate sections and documented sources).
CANDIDATES: tuple[Candidate, ...] = (
    Candidate(
        "qubes_os",
        "Qubes OS",
        "compartmentalized",
        "Application qubes under the bare-metal Xen hypervisor, networking kept out of the "
        "privileged administrative domain, template-backed qubes seeing a read-only root while "
        "app qubes retain persistent private state, disposable qubes discarding hostile intake, "
        "and qrexec policy mediating every cross-domain channel including GUI and clipboard.",
        "Explicitly no isolation between applications inside one qube; dom0 or hypervisor "
        "compromise is documented as fatal to the security model; user-authorized clipboard and "
        "qrexec transfers are workflow attacks rather than boundary escapes; x86 covert channels "
        "between VMs remain; Anti Evil Maid carries specific TPM/Intel TXT requirements and "
        "merely signing the bootloader or Xen is insufficient (qubes-issues 4371).",
        "Leading architectural choice for a compartmentalized, high-risk personal workstation "
        "when hardware is suitable and the user maintains meaningful trust boundaries; the "
        "recommendation weakens under compartment collapse, poor hardware, or firmware- and "
        "physical-adversary dominance; for the highest-value secrets separate hardware remains "
        "a reasonable additional boundary rather than a failure of the Qubes concept.",
        "4.3 release notes document GUI/admin-domain splitting, new device-assignment "
        "mechanisms, and initial Wayland work — relevant directions, not proof every "
        "installation already runs a fully separated hardened GUI stack; QSB-118 (an arbitrary "
        "dom0 command injectable via qvm-copy-to-vm from an already compromised qube, fixed in "
        "qubes-core-dom0-linux 4.3.22) shows dom0 transfer tooling must be patched promptly; "
        "community templates receive no Qubes-project updates.",
        {
            "containment": "strong",
            "authority": "partial",
            "trusted_computing_base": "partial",
            "application_confinement": "partial",
            "integrity": "partial",
            "persistence_recovery": "strong",
            "update_operations": "partial",
            "supply_chain_trust": "partial",
            "human_usability": "partial",
        },
    ),
    Candidate(
        "nixos",
        "NixOS",
        "reproducible",
        "Declarative system configuration with generation-based activation and rollback, a "
        "content-addressed store, Nix-sandboxed build namespaces, and a Nixpkgs security "
        "tracker coordinating vulnerability matching and mitigation.",
        "The documented sandbox concerns builds, not runtime security; generation rollback does "
        "not restore service data or remove malware from persistent state, and older retained "
        "generations are potentially vulnerable software; the store is readable by all users, "
        "so declarative secrets leak; SELinux and AppArmor integration incomplete as of April "
        "2026; Lanzaboote Secure Boot in development with key management outside project scope; "
        "the hardened profile lacks a coherent baseline and can undermine browser sandboxing "
        "without compensating setup; the April 2026 GHSA-g3g9 symlink flaw shows a privileged "
        "build service is part of the attack surface.",
        "Strong foundation for controlled configuration and rebuildable environments for a "
        "capable operator — especially constructing, auditing, and replacing tightly scoped, "
        "separately isolated environments; not a substitute for a containment architecture, not "
        "the default recommendation over Qubes for containing a hostile desktop workload, and "
        "not enough by itself to make a powerful autonomous coding agent safe.",
        "The most compelling role is compositional: declarative construction inside a "
        "separately enforced least-privilege execution architecture; reproducible deployment is "
        "not independently verified reproducible builds, and NixOS 26.05 support ends "
        "2026-12-31; Qubes-plus-NixOS-template stacks carry integration and maintenance risk "
        "documented in qubes-issues 7992.",
        {
            "containment": "weak",
            "authority": "weak",
            "trusted_computing_base": "partial",
            "application_confinement": "weak",
            "integrity": "partial",
            "persistence_recovery": "partial",
            "update_operations": "strong",
            "supply_chain_trust": "partial",
            "human_usability": "partial",
        },
    ),
    Candidate(
        "secureblue",
        "secureblue",
        "desktop",
        "Fedora Atomic base with broad hardened_malloc deployment, a confined Trivalent "
        "browser, removal of SUID-root programs, restrictive application settings, disabled "
        "Xwayland, user-namespace restrictions with documented exceptions, and signed-container "
        "policy.",
        "Documented compatibility-affecting restrictions require the supported workflow to fit "
        "and some tools need user-namespace exceptions; the feature list is project-documented "
        "design, not measured exploit resistance, patch latency, or independent audit coverage; "
        "persistent writable user state remains.",
        "One of the most compelling conventional security-focused desktop candidates in this "
        "review — it addresses more of the runtime attack surface than immutability alone and "
        "can be preferable to assembling a large custom NixOS hardening stack when its "
        "supported workflow fits; the recommendation is conditional on application "
        "compatibility, update reliability, and the operator not undoing hardening for "
        "convenience; an autonomous agent still belongs in a separate trust domain.",
        "Its distinguishing proposition is runtime hardening rather than image-based delivery; "
        "sustained maintenance and upstream Fedora integration determine whether it stays ahead "
        "of assembling custom hardening; the sensible benchmark is documented per-application "
        "authority narrowing, with no crowning of comparative superiority.",
        {
            "containment": "partial",
            "authority": "partial",
            "trusted_computing_base": "partial",
            "application_confinement": "strong",
            "integrity": "partial",
            "persistence_recovery": "partial",
            "update_operations": "partial",
            "supply_chain_trust": "partial",
            "human_usability": "partial",
        },
    ),
    Candidate(
        "fedora_atomic",
        "Fedora Atomic (Silverblue/Kinoite)",
        "desktop",
        "Atomic desktop variants with read-only system paths, writable /etc and /var, and "
        "SELinux enforcing documented as the Fedora default baseline.",
        "Persistent writable user state remains; the approximately 13-month release support "
        "window demands regular upgrades; Flatpak permission grants, including unrestricted "
        "bus access, must be inspected per application; Silverblue-specific details should not "
        "be assumed to prove every Kinoite property.",
        "A defensible conventional atomic choice when a recognizable standard environment is "
        "more sustainable for the owner than a hardened or compartmentalized workflow; "
        "runtime authority depends on per-application policy as deployed, not on immutability "
        "of system paths.",
        "The atomic/image-based direction keeps gaining mainstream reach; whether "
        "application-permission narrowing and agent-authority mediation follow is the open "
        "composition question for this category.",
        {
            "containment": "weak",
            "authority": "partial",
            "trusted_computing_base": "partial",
            "application_confinement": "weak",
            "integrity": "partial",
            "persistence_recovery": "partial",
            "update_operations": "partial",
            "supply_chain_trust": "partial",
            "human_usability": "strong",
        },
    ),
    Candidate(
        "fedora_workstation",
        "Fedora Workstation",
        "desktop",
        "Standard Fedora desktop whose documented baseline includes SELinux enforcing without "
        "choosing an atomic variant, under the Fedora release lifecycle.",
        "The existence of a kernel access-control mechanism does not by itself establish a "
        "tight sandbox for each application as deployed; mutable system state; no documented "
        "atomic rollback in the reviewed sources.",
        "A defensible compatibility-first choice when the operator preserves the security "
        "baseline and uses separate isolation for dangerous work; do not presume an atomic "
        "variant automatically wins every runtime-security comparison.",
        "Baseline distributions matter mainly as substrates for separately enforced agent "
        "confinement; the quality of per-application sandboxing as deployed is the open "
        "question this category leaves unanswered.",
        {
            "containment": "weak",
            "authority": "partial",
            "trusted_computing_base": "partial",
            "application_confinement": "weak",
            "integrity": "weak",
            "persistence_recovery": "weak",
            "update_operations": "partial",
            "supply_chain_trust": "partial",
            "human_usability": "strong",
        },
    ),
    Candidate(
        "debian_stable",
        "Debian stable",
        "desktop",
        "Coordinated security-advisory process with recommended unattended security upgrades; "
        "LTS extends stable support under a separate group from the Debian security team.",
        "A maintenance policy is not evidence of isolation between arbitrary desktop "
        "applications; the different support phases and organizations should not be conflated; "
        "no comprehensive default MAC baseline is described in the reviewed sources.",
        "A sound conservative platform when configured for the actual workload; prefer a "
        "well-maintained, narrowly configured installation over a more elaborate stack the "
        "owner cannot sustain.",
        "Enterprise-grade advisory coordination with voluntary maintenance obligations; agent "
        "workloads need externally imposed confinement regardless of the platform's process "
        "discipline.",
        {
            "containment": "weak",
            "authority": "weak",
            "trusted_computing_base": "partial",
            "application_confinement": "weak",
            "integrity": "weak",
            "persistence_recovery": "weak",
            "update_operations": "partial",
            "supply_chain_trust": "partial",
            "human_usability": "strong",
        },
    ),
    Candidate(
        "ubuntu_lts",
        "Ubuntu LTS",
        "desktop",
        "Five years of documented standard security maintenance with longer coverage under "
        "specified offerings; snap packaging distinguishes strict, classic, and development "
        "confinement modes.",
        "Classic snaps have no confinement, so installed-as-a-snap is not evidence of "
        "application isolation; coverage must be matched to the package, release, and support "
        "entitlement.",
        "A pragmatic supported baseline when entitlement and package coverage match the "
        "workload; runtime isolation depends on the per-snap mode actually used and on "
        "separately imposed policy.",
        "Snap strict-confinement machinery is the platform's confinement bet; mixed-mode "
        "realities keep per-application authority inspection necessary for agent workloads.",
        {
            "containment": "weak",
            "authority": "weak",
            "trusted_computing_base": "partial",
            "application_confinement": "weak",
            "integrity": "weak",
            "persistence_recovery": "weak",
            "update_operations": "strong",
            "supply_chain_trust": "partial",
            "human_usability": "strong",
        },
    ),
    Candidate(
        "kicksecure",
        "Kicksecure",
        "desktop",
        "Debian-based hardening distribution documenting a user/sysmaintenance split that "
        "separates everyday boot roles from maintenance authority.",
        "The hardening documentation explicitly contains research and non-default proposals "
        "that can cause breakage; a long wiki page must not be mistaken for shipped defaults; "
        "verified boot is labeled planned rather than shipped.",
        "A serious security-focused candidate, particularly where reducing everyday "
        "administrative authority is valuable; judge the installed release and enabled "
        "settings rather than the wiki's promises.",
        "Shares development with the Whonix ecosystem; value depends on distilling its "
        "maintenance-split and hardening ideas into maintainable shipped defaults.",
        {
            "containment": "partial",
            "authority": "partial",
            "trusted_computing_base": "partial",
            "application_confinement": "weak",
            "integrity": "weak",
            "persistence_recovery": "weak",
            "update_operations": "partial",
            "supply_chain_trust": "partial",
            "human_usability": "partial",
        },
    ),
    Candidate(
        "opensuse_aeon",
        "openSUSE Aeon",
        "desktop",
        "Immutable Tumbleweed-based desktop where transactional-update prepares changes in a "
        "new snapshot without modifying the running system.",
        "Snapshot-based system replacement is not evidence that a compromised application "
        "cannot read or modify its authorized user data; the documented mechanism principally "
        "concerns system updates rather than runtime confinement.",
        "A credible image/snapshot-oriented desktop direction; this review does not establish "
        "a basis for placing it ahead of Qubes for containment or secureblue for documented "
        "desktop hardening.",
        "Worth watching as mainstream image-based deployment; role-specific and boot-integrity "
        "details remain to be validated per image rather than inferred from the snapshot "
        "mechanism.",
        {
            "containment": "weak",
            "authority": "partial",
            "trusted_computing_base": "partial",
            "application_confinement": "weak",
            "integrity": "partial",
            "persistence_recovery": "weak",
            "update_operations": "partial",
            "supply_chain_trust": "partial",
            "human_usability": "strong",
        },
    ),
    Candidate(
        "opensuse_microos",
        "openSUSE MicroOS",
        "server",
        "Transactional openSUSE server roles where transactional-update prepares a new system "
        "snapshot and provides rollback operations.",
        "Role-specific defaults and a distinct boot-integrity baseline were not verified in "
        "this review — those fields are withheld as n.a. rather than inferred from Aeon.",
        "Consider for transactional server operation subject to validating the exact image and "
        "workload; the evidence here is insufficient for a stronger security ranking.",
        "Transactional server operation parallels the Aeon desktop direction; adoption depends "
        "on validated role defaults and a fleet update policy the operator actually owns.",
        {
            "containment": "weak",
            "authority": "partial",
            "trusted_computing_base": "partial",
            "application_confinement": "weak",
            "integrity": "partial",
            "persistence_recovery": "partial",
            "update_operations": "partial",
            "supply_chain_trust": "partial",
            "human_usability": "partial",
        },
    ),
    Candidate(
        "alpine_linux",
        "Alpine Linux",
        "server",
        "Small musl/BusyBox-based distribution whose project documents PIE and stack-smashing "
        "protection for userland binaries.",
        "Roughly two-year main-repository support versus community-repository support only "
        "until the next stable release; small size is not itself an application-isolation "
        "policy.",
        "Good for deliberately minimal workloads when dependency compatibility and support "
        "scope are controlled; not a general claim to the strongest desktop or hostile-code "
        "boundary.",
        "The minimal trusted base makes it a natural microVM and base-image substrate when "
        "paired with an externally supplied isolation boundary.",
        {
            "containment": "weak",
            "authority": "weak",
            "trusted_computing_base": "strong",
            "application_confinement": "weak",
            "integrity": "partial",
            "persistence_recovery": "weak",
            "update_operations": "weak",
            "supply_chain_trust": "partial",
            "human_usability": "partial",
        },
    ),
    Candidate(
        "talos_linux",
        "Talos Linux",
        "server",
        "Kubernetes-specific OS with no shell or interactive console, API-only management "
        "secured by mutual TLS, atomic updates, and a Secure Boot path using a signed unified "
        "kernel image containing the OS.",
        "API credentials and the orchestrator remain high-value authority; Secure Boot depends "
        "on the supported boot mode, enrolled keys, and the actual deployment; not a general "
        "workstation substitute.",
        "A leading specialized candidate for a controlled Kubernetes node fleet; its authority "
        "story is elimination of interfaces rather than per-workload isolation, which the "
        "container runtime supplies separately.",
        "The strongest currently shipping reduced-interface Kubernetes-node pattern; "
        "orchestrator and extension trust remains the residual boundary that host hardening "
        "cannot close.",
        {
            "containment": "strong",
            "authority": "partial",
            "trusted_computing_base": "partial",
            "application_confinement": "partial",
            "integrity": "strong",
            "persistence_recovery": "strong",
            "update_operations": "strong",
            "supply_chain_trust": "partial",
            "human_usability": "partial",
        },
    ),
    Candidate(
        "bottlerocket",
        "Bottlerocket",
        "server",
        "Container-host OS with a read-only dm-verity root, enforcing SELinux, stateless /etc, "
        "kernel lockdown, no host shell or interpreters, and Secure Boot support documented in "
        "its feature history.",
        "Its own goals distinguish host persistence resistance, vulnerability mitigation, and "
        "protection between containers — these should not be collapsed into VM-equivalent "
        "workload separation; deployment-ecosystem fit gates adoption.",
        "A leading container-host candidate where the deployment ecosystem fits; host "
        "hardening and the isolation chosen for hostile workloads are separable decisions, and "
        "an ordinary container host is not that stronger boundary.",
        "Container-host hardening keeps converging on image verification and stateless "
        "operation; executing untrusted agent-generated code still needs a disposable VM or "
        "microVM boundary beyond the container host.",
        {
            "containment": "partial",
            "authority": "partial",
            "trusted_computing_base": "partial",
            "application_confinement": "partial",
            "integrity": "strong",
            "persistence_recovery": "strong",
            "update_operations": "strong",
            "supply_chain_trust": "partial",
            "human_usability": "partial",
        },
    ),
    Candidate(
        "fedora_coreos",
        "Fedora CoreOS",
        "server",
        "Atomic container-host OS with automated update coordination through Zincati and "
        "retained previous deployments for rollback.",
        "Updates require reboot coordination and their benefits depend on a fleet policy that "
        "actually allows completion; the reviewed sources document no per-workload isolation "
        "beyond the container runtime.",
        "Strong for automated container infrastructure when the operator can sustain its "
        "update model.",
        "Zincati automation exemplifies hands-off update operations for fleets; rollback and "
        "reboot policy must still be owned deliberately, and hostile agent workloads need an "
        "externally supplied boundary.",
        {
            "containment": "weak",
            "authority": "partial",
            "trusted_computing_base": "partial",
            "application_confinement": "weak",
            "integrity": "partial",
            "persistence_recovery": "partial",
            "update_operations": "partial",
            "supply_chain_trust": "partial",
            "human_usability": "partial",
        },
    ),
    Candidate(
        "rhel",
        "RHEL",
        "server",
        "Formal security-errata classification and maintenance policy providing an explicit "
        "basis for planning supported operation.",
        "Coverage depends on the applicable product, phase, severity, and entitlement rather "
        "than the brand alone; the reviewed sources document the maintenance process, not "
        "runtime isolation quality.",
        "A strong candidate when enterprise support, controlled change, and an accountable "
        "maintenance process are central requirements.",
        "Entitlement-bound support models trade process accountability for coverage; agent "
        "authority needs separately imposed confinement regardless of the errata process.",
        {
            "containment": "weak",
            "authority": "partial",
            "trusted_computing_base": "partial",
            "application_confinement": "weak",
            "integrity": "weak",
            "persistence_recovery": "weak",
            "update_operations": "strong",
            "supply_chain_trust": "strong",
            "human_usability": "partial",
        },
    ),
    Candidate(
        "ubuntu_core",
        "Ubuntu Core",
        "server",
        "All-snap appliance/IoT edition whose security model documents AppArmor, seccomp, "
        "device controls, and mount namespaces for snaps.",
        "Not Ubuntu Desktop LTS with an immutability switch — the intended workload and "
        "packaging model differ; application supply concentrates in the snap store.",
        "Relevant for controlled appliances, not the default answer for a general developer "
        "workstation.",
        "The strict-confinement appliance model is the clearest mainstream example of narrow "
        "by-default authority; whether it extends to developer desktops and agent workloads "
        "remains unresolved.",
        {
            "containment": "partial",
            "authority": "partial",
            "trusted_computing_base": "partial",
            "application_confinement": "strong",
            "integrity": "partial",
            "persistence_recovery": "partial",
            "update_operations": "strong",
            "supply_chain_trust": "strong",
            "human_usability": "partial",
        },
    ),
    Candidate(
        "whonix",
        "Whonix",
        "anonymity",
        "Gateway/workstation split targeting anonymity, built on Debian with "
        "Kicksecure-derived hardening.",
        "Workstation documentation warns that compromise exposes the workstation's "
        "credentials and browser data; it does not make an authorized agent harmless.",
        "Valuable for an anonymity requirement, potentially within a broader compartmentalized "
        "design; anonymity and credential protection are distinct properties and Whonix "
        "addresses the former.",
        "Its boundary is anonymity engineering — Tor routing and gateway separation; local "
        "credential protection requires additional compartmentalization beyond the gateway "
        "split.",
        {
            "containment": "partial",
            "authority": "weak",
            "trusted_computing_base": "partial",
            "application_confinement": "weak",
            "integrity": "weak",
            "persistence_recovery": "weak",
            "update_operations": "partial",
            "supply_chain_trust": "partial",
            "human_usability": "partial",
        },
    ),
    Candidate(
        "tails",
        "Tails",
        "anonymity",
        "Amnesic live environment with Tor networking, optional encrypted Persistent Storage, "
        "and documented warnings about malicious hardware.",
        "Trace reduction and session reset do not recover information exposed during the "
        "active session; enabling Persistent Storage re-opens exactly the state the amnesic "
        "mode otherwise avoids.",
        "Recommended where reduced local traces are the priority — Whonix or Tails according "
        "to whether persistent separated work or amnesic sessions are required; it is not a "
        "containment architecture for daily agent work.",
        "Amnesia remains the strongest mainstream full-state-reset story; persistence features "
        "trade back the state reset buys, so the choice is deliberate per use case.",
        {
            "containment": "weak",
            "authority": "partial",
            "trusted_computing_base": "partial",
            "application_confinement": "weak",
            "integrity": "weak",
            "persistence_recovery": "strong",
            "update_operations": "partial",
            "supply_chain_trust": "partial",
            "human_usability": "partial",
        },
    ),
    Candidate(
        "openbsd",
        "OpenBSD",
        "high_assurance",
        "Secure-by-default service choices, privilege separation, and exploit mitigations "
        "including W^X and system-wide hardening documented by the project.",
        "This evidence does not establish superiority for a modern browser-heavy, "
        "GPU-dependent, AI-development workstation; the reviewed sources describe system-level "
        "mitigation, not a per-application permission model comparable to mobile platforms.",
        "A serious non-Linux comparator for narrowly scoped services; compatibility rather "
        "than mitigation quality is the limiting factor for the assessed workstation scenario.",
        "Sustained whole-system mitigation discipline remains the reference for by-default "
        "baselines; relevance to agent-hosting is as a dedicated, narrowly scoped service "
        "substrate.",
        {
            "containment": "partial",
            "authority": "partial",
            "trusted_computing_base": "partial",
            "application_confinement": "partial",
            "integrity": "partial",
            "persistence_recovery": "weak",
            "update_operations": "partial",
            "supply_chain_trust": "partial",
            "human_usability": "partial",
        },
    ),
    Candidate(
        "sel4",
        "seL4",
        "high_assurance",
        "Formally verified microkernel whose proofs are scoped by explicit assumptions, "
        "including boot, hardware, and DMA-related qualifications.",
        "Verification establishes assurance of a small core, not security of a complete "
        "browser, driver stack, firmware chain, or user workflow; proof claims must not be "
        "automatically transferred to complete configurations built on it.",
        "A compelling route to stronger assurance of a small core; a deployed system on it "
        "must still be evaluated at its whole reachable boundary, and a verified microkernel "
        "does not automatically yield the best practical desktop.",
        "High-assurance research to track — evaluate the complete deployed system and its "
        "proof boundary; production compatibility, drivers, tooling, and operational assurance "
        "outweigh theoretical elegance for practical desktops.",
        {
            "containment": "strong",
            "authority": "n_a",
            "trusted_computing_base": "strong",
            "application_confinement": "n_a",
            "integrity": "partial",
            "persistence_recovery": "n_a",
            "update_operations": "n_a",
            "supply_chain_trust": "n_a",
            "human_usability": "n_a",
        },
    ),
    Candidate(
        "genode_sculpt",
        "Genode / Sculpt",
        "high_assurance",
        "General-purpose OS built from Genode's microkernel architecture with capability-based "
        "security, sandboxed drivers, and VMs; a 26.04 release in day-to-day use by its "
        "developers.",
        "seL4 proof claims must not be automatically transferred to every Genode/Sculpt "
        "configuration or the applications it hosts; ecosystem and driver coverage remain "
        "niche for browser-heavy workstation use.",
        "A meaningful architectural trajectory to watch; capability-mediated authority is the "
        "relevant lesson independent of desktop readiness.",
        "The clearest shipping example that capability-based authority mediation can support a "
        "usable desktop; watch driver and tooling coverage growth rather than expecting "
        "near-term workstation parity.",
        {
            "containment": "strong",
            "authority": "strong",
            "trusted_computing_base": "partial",
            "application_confinement": "partial",
            "integrity": "partial",
            "persistence_recovery": "partial",
            "update_operations": "weak",
            "supply_chain_trust": "weak",
            "human_usability": "partial",
        },
    ),
    Candidate(
        "grapheneos",
        "GrapheneOS",
        "mobile",
        "Hardened mobile platform atop Android's security model keeping even Google Play "
        "inside the standard app sandbox.",
        "A mobile comparator, not a desktop Linux replacement; hardware/vendor constraints and "
        "application ecosystems differ from workstation use.",
        "The relevant lesson is making useful applications operate with constrained authority "
        "by default — the property desktop Linux most lacks; do not misclassify it as a "
        "desktop candidate.",
        "Mobile per-app sandboxing and permission narrowing is the deployment to benchmark "
        "desktop default authority against.",
        {
            "containment": "partial",
            "authority": "partial",
            "trusted_computing_base": "partial",
            "application_confinement": "strong",
            "integrity": "partial",
            "persistence_recovery": "partial",
            "update_operations": "partial",
            "supply_chain_trust": "partial",
            "human_usability": "strong",
        },
    ),
    Candidate(
        "kali_linux",
        "Kali Linux",
        "offensive_toolkit",
        "Distribution documenting penetration testing and security auditing as its explicit "
        "purpose.",
        "Offensive-tool availability is not evidence of superior protection for the machine "
        "running those tools; the rolling Debian base inherits the desktop weaknesses of the "
        "underlying platform.",
        "Appropriate as a dedicated, isolated tool environment; use for the assessed "
        "workstation threat model would expand reachable authority without adding containment.",
        "Its role is producing attacks, not resisting them; keep offensive tooling isolated "
        "from credentials, production access, and daily hostile-intake work.",
        {
            "containment": "weak",
            "authority": "weak",
            "trusted_computing_base": "partial",
            "application_confinement": "weak",
            "integrity": "weak",
            "persistence_recovery": "weak",
            "update_operations": "partial",
            "supply_chain_trust": "partial",
            "human_usability": "partial",
        },
    ),
    Candidate(
        "parrot_security",
        "Parrot Security",
        "offensive_toolkit",
        "Security and forensics distribution documenting hardening measures while its core "
        "remains tuned for security and forensics work.",
        "Documented hardening does not establish a containment architecture; forensics tuning "
        "drives defaults different from daily hostile-intake work.",
        "As with Kali, offensive-tool availability is not machine-protection evidence; "
        "suitable as a separate tooling environment only.",
        "Tooling-focused distributions illustrate that purpose-built tuning is not hardening "
        "for the assessed threat model.",
        {
            "containment": "weak",
            "authority": "weak",
            "trusted_computing_base": "partial",
            "application_confinement": "weak",
            "integrity": "weak",
            "persistence_recovery": "weak",
            "update_operations": "partial",
            "supply_chain_trust": "partial",
            "human_usability": "partial",
        },
    ),
)

#: The 8 scenario recommendations (ids pinned; wording mirrors the source's
#: scenario-recommendation table).
SCENARIOS: tuple[Scenario, ...] = (
    Scenario(
        "high_risk_workstation",
        "Technically capable operator using one workstation for browsing, development, "
        "sensitive accounts, documents, and AI-assisted work with distinct sensitive identities.",
        "Qubes, with deliberately separated domains, disposable intake, minimal "
        "administration, and prompt updates.",
        "Incompatible hardware, essential unsupported software, or inability to maintain the "
        "compartmentalized workflow.",
    ),
    Scenario(
        "conventional_hardened_desktop",
        "Conventional Linux desktop where the owner prioritizes hardening within a standard, "
        "recognizable environment.",
        "Evaluate secureblue first against actual application requirements; use Fedora "
        "Workstation or an atomic Fedora desktop when a more standard environment is more "
        "sustainable.",
        "Hardening restrictions require broad exceptions, or project maintenance does not meet "
        "the owner's assurance requirements.",
    ),
    Scenario(
        "auditable_operator",
        "Skilled operator prioritizing auditable configuration and replaceable environments.",
        "NixOS, paired with explicit runtime confinement, boot-integrity decisions, careful "
        "secret handling, and a disciplined update process.",
        "The custom security integration becomes too complex to review and maintain.",
    ),
    Scenario(
        "autonomous_agent_hosting",
        "Autonomous coding or research agents processing hostile material.",
        "Disposable task VMs or comparable isolated workers, with controlled network access "
        "and externally mediated credentials; Nix can help construct the workers.",
        "Tasks demand high-impact access that cannot be safely scoped; those actions should "
        "remain separately authorized.",
    ),
    Scenario(
        "kubernetes_fleet",
        "Controlled Kubernetes node fleet.",
        "Talos; also assess Bottlerocket where its container-host ecosystem fits.",
        "Orchestrator, hardware, extensions, or operational requirements conflict with the "
        "reduced host interface.",
    ),
    Scenario(
        "enterprise_server",
        "General enterprise server operation.",
        "RHEL or Ubuntu LTS with explicit support scope and tested policies; Debian or NixOS "
        "where the operator can own the relevant maintenance obligations.",
        "Package coverage, response requirements, or configuration expertise favor a different "
        "support model.",
    ),
    Scenario(
        "anonymity_traces",
        "Anonymity or reduced local traces.",
        "Whonix or Tails according to whether persistent separated work or amnesic sessions "
        "are required.",
        "The actual priority is protecting local credentials from an already compromised "
        "application rather than anonymity.",
    ),
    Scenario(
        "high_assurance_research",
        "High-assurance architectural research.",
        "Track seL4 and Genode/Sculpt, while evaluating the complete deployed system and its "
        "proof boundary.",
        "Production compatibility, drivers, tooling, and operational assurance outweigh "
        "theoretical elegance.",
    ),
)


def matrix_rows() -> list[tuple[str, str, str]]:
    """Flatten the candidate x property grid to 24 x 9 = 216 stance cells.

    Returns ``(candidate_id, property_id, stance)`` tuples in
    ``CANDIDATES`` x ``PROPERTIES`` order — the evaluation matrix.
    """
    return [
        (candidate.candidate_id, property_.property_id, candidate.property_stance[property_.property_id])
        for candidate in CANDIDATES
        for property_ in PROPERTIES
    ]


def category_counts() -> dict[str, int]:
    """Return the number of candidates per category, all 8 categories present."""
    counts = {category: 0 for category in CATEGORY_VOCAB}
    for candidate in CANDIDATES:
        counts[candidate.category] += 1
    return counts


def stance_counts() -> dict[str, int]:
    """Return the number of 216 matrix cells per stance value, all 4 present."""
    counts = {stance: 0 for stance in STANCE_VOCAB}
    for _, _, stance in matrix_rows():
        counts[stance] += 1
    return counts


def candidates_by_category(category: str) -> list[Candidate]:
    """Return candidates whose ``category`` equals ``category`` (empty if none)."""
    return [candidate for candidate in CANDIDATES if candidate.category == category]
