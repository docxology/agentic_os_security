"""Evidence registry invariants: 150 pinned sources, tier vocabulary,
URL contract, capability baseline, and bib parity with references.bib.

The key->URL mapping below is pinned by the project brief plus the
v0.2.0 research dossier (85 extension keys + the OpenAI-Hugging Face
incident report); the evidence module must reproduce it exactly (plus
the https scheme). Bib parity is checked with a regex over
`@<type>{<key>,` occurrences — no bibtex parser dependency.
"""

from __future__ import annotations

import re

from agentic_os_security import evidence

# key -> URL path, exactly as pinned in the brief.
PINNED_URLS = {
    "redhat_errata_policy": "https://access.redhat.com/support/policy/updates/errata",
    "alpine_design": "https://alpinelinux.org/about/",
    "alpine_support_scope": "https://alpinelinux.org/releases/",
    "nixos_hardened_profile_deprecation": "https://discourse.nixos.org/t/proposal-to-deprecate-the-hardened-profile/63081",
    "nixos_rollback_data_discussion": "https://discourse.nixos.org/t/rolling-back-data-as-well-not-only-nix-config/63169",
    "nix_cache_signatures": "https://discourse.nixos.org/t/what-guarantees-do-signatures-by-binary-caches-give/34802",
    "qubes_43_release_notes": "https://doc.qubes-os.org/en/latest/developer/releases/4_3/release-notes.html",
    "qubes_qrexec": "https://doc.qubes-os.org/en/latest/developer/services/qrexec.html",
    "qubes_architecture": "https://doc.qubes-os.org/en/latest/developer/system/architecture.html",
    "qubes_gui_protocol": "https://doc.qubes-os.org/en/latest/developer/system/gui.html",
    "qubes_security_design_goals": "https://doc.qubes-os.org/en/latest/developer/system/security-design-goals.html",
    "qubes_faq": "https://doc.qubes-os.org/en/latest/introduction/faq.html",
    "qubes_gui_domain": "https://doc.qubes-os.org/en/latest/user/advanced-topics/gui-domain.html",
    "qubes_disposables": "https://doc.qubes-os.org/en/latest/user/how-to-guides/how-to-use-disposables.html",
    "qubes_anti_evil_maid": "https://doc.qubes-os.org/en/latest/user/security-in-qubes/anti-evil-maid.html",
    "qubes_templates": "https://doc.qubes-os.org/en/latest/user/templates/templates.html",
    "fedora_coreos_updates": "https://docs.fedoraproject.org/en-US/fedora-coreos/auto-updates/",
    "fedora_silverblue_technical": "https://docs.fedoraproject.org/en-US/fedora-silverblue/technical-information/",
    "fedora_selinux_getting_started": "https://docs.fedoraproject.org/en-US/quick-docs/selinux-getting-started/",
    "fedora_release_lifecycle": "https://docs.fedoraproject.org/en-US/releases/lifecycle/",
    "flatpak_permissions": "https://docs.flatpak.org/en/latest/sandbox-permissions.html",
    "ubuntu_core_confinement": "https://documentation.ubuntu.com/core/explanation/security-and-sandboxing/",
    "snap_confinement": "https://documentation.ubuntu.com/security/security-features/privilege-restriction/snap-confinement/",
    "opensuse_aeon": "https://en.opensuse.org/Portal:Aeon",
    "opensuse_transactional_update": "https://en.opensuse.org/Transactional-update",
    "fedora_selinux_config": "https://fedoraproject.org/wiki/SELinux/Config",
    "genode_sculpt": "https://genode.org/download/sculpt",
    "nix_ghsa_g3g9": "https://github.com/NixOS/nix/security/advisories/GHSA-g3g9-5vj6-r3gj",
    "qubes_issue_4371": "https://github.com/QubesOS/qubes-issues/issues/4371",
    "qubes_issue_7992": "https://github.com/QubesOS/qubes-issues/issues/7992",
    "bottlerocket_security_features": "https://github.com/bottlerocket-os/bottlerocket/blob/develop/SECURITY_FEATURES.md",
    "lanzaboote_repo": "https://github.com/nix-community/lanzaboote",
    "talos_repo": "https://github.com/siderolabs/talos",
    "grapheneos_features": "https://grapheneos.org/features",
    "nix_store_secrets": "https://nix.dev/manual/nix/2.33/store/secrets.html",
    "nix_sandbox_config": "https://nix.dev/manual/nix/2.35/command-ref/conf-file.html",
    "nixos_2605_announcement": "https://nixos.org/blog/announcements/2026/nixos-2605/",
    "parrot_intended_use": "https://parrotsec.org/docs/introduction/what-is-parrot/",
    "nixos_reproducibility": "https://reproducible.nixos.org/",
    "secureblue_features": "https://secureblue.dev/features",
    "sel4_verification_assumptions": "https://sel4.systems/Verification/assumptions.html",
    "tails_overview": "https://tails.net/about/index.en.html",
    "tails_persistent_storage": "https://tails.net/doc/persistent_storage/",
    "nixos_security_tracker": "https://tracker.security.nixos.org/",
    "ubuntu_release_cycle": "https://ubuntu.com/about/release-cycle",
    "nixos_lanzaboote_wiki": "https://wiki.nixos.org/wiki/Lanzaboote",
    "nixos_wiki": "https://wiki.nixos.org/wiki/NixOS",
    "nixos_rebuild_wiki": "https://wiki.nixos.org/wiki/Nixos-rebuild",
    "nixos_security_wiki": "https://wiki.nixos.org/wiki/Security",
    "anthropic_campaign_report": "https://www-cdn.anthropic.com/d7dd50dd1185f59be051b307150d877f2b82bd2c.pdf",
    "aisi_incident_report": "https://www.aisi.gov.uk/blog/incident-report-unsanctioned-agent-behaviour-during-cyber-testing",
    "darpa_aixcc_results": "https://www.darpa.mil/news/2025/aixcc-results",
    "debian_lts": "https://www.debian.org/lts/",
    "debian_security": "https://www.debian.org/security/",
    "kali_intended_use": "https://www.kali.org/docs/introduction/should-i-use-kali-linux/",
    "kicksecure_sysmaint_split": "https://www.kicksecure.com/wiki/Dev/user-sysmaint-split",
    "kicksecure_hardening": "https://www.kicksecure.com/wiki/Operating_System_Hardening",
    "ncsc_ai_cyber_threat": "https://www.ncsc.gov.uk/report/impact-ai-cyber-threat-now-2027",
    "openbsd_innovations": "https://www.openbsd.org/innovations.html",
    "openbsd_security": "https://www.openbsd.org/security.html",
    "qsb_118": "https://www.qubes-os.org/news/2026/08/29/qsb-118/",
    "qubes_qsb_index": "https://www.qubes-os.org/security/qsb/",
    "talos_secureboot": "https://www.talos.dev/v1.11/talos-guides/install/bare-metal-platforms/secureboot/",
    "whonix_technical_design": "https://www.whonix.org/wiki/Dev/Technical_Introduction",
    "whonix_workstation_security": "https://www.whonix.org/wiki/Whonix-Workstation_Security",
    "ncsc_ai_threat_2024": "https://www.ncsc.gov.uk/report/impact-of-ai-on-cyber-threat",
    "cisa_agentic_guidance": "https://www.cisa.gov/resources-tools/resources/careful-adoption-agentic-ai-services",
    "anthropic_misuse_aug_2025": "https://www.anthropic.com/news/detecting-countering-misuse-aug-2025",
    "anthropic_ti_sept_2026": "https://www.anthropic.com/threat-intelligence-report-september-2026",
    "mitre_c0062": "https://attack.mitre.org/campaigns/C0062/",
    "arstechnica_gtg_skepticism": "https://arstechnica.com/security/2025/11/researchers-question-anthropic-claim-that-ai-assisted-attack-was-90-autonomous/",
    "openai_disruption_oct_2025": "https://openai.com/global-affairs/disrupting-malicious-uses-of-ai-october-2025/",
    "openai_disruption_2026": "https://openai.com/global-affairs/disrupting-malicious-uses-of-ai/",
    "gtig_prompting_autonomy": "https://cloud.google.com/blog/topics/threat-intelligence/from-prompting-to-autonomy-the-evolution-of-adversarial-ai",
    "aisi_incident_pdf": "https://cdn.prod.website-files.com/663bd486c5e4c81588db7a1d/6a724858f7db25c81487016d_Security%20Incident%20INC-2026-07-28-01.pdf",
    "darpa_aixcc_finals": "https://aicyberchallenge.com/finals-winners-announcement/",
    "aixcc_atlantis_paper": "https://doi.org/10.48550/arxiv.2509.14589",
    "agent_cyber_benchmark": "https://arxiv.org/html/2603.11214v2",
    "openai_hf_incident": "https://cdn.openai.com/pdf/67869394-cb91-4c12-888c-5cbd85c7814c/OpenAI-Hugging%20Face%20Incident-Technical-Report.pdf",
    "qubes_430_release": "https://www.qubes-os.org/news/2025/12/21/qubes-os-4-3-0-has-been-released/",
    "qsb_110": "https://www.qubes-os.org/news/2026/03/17/qsb-110/",
    "qsb_115": "https://www.qubes-os.org/news/2026/06/09/qsb-115/",
    "qsb_116": "https://www.qubes-os.org/news/2026/07/28/qsb-116/",
    "qubes_43_requirements": "https://doc.qubes-os.org/en/r4.3/user/hardware/system-requirements.html",
    "qubes_salt_administration": "https://doc.qubes-os.org/en/latest/user/advanced-topics/salt.html",
    "qubes_devices_api": "https://doc.qubes-os.org/projects/core-admin/en/latest/qubes-devices.html",
    "trenchboot_aem_uefi": "https://beta.blog.3mdeb.com/2025/2025-06-10-aem-uefi/",
    "nix_ghsa_vh5x": "https://github.com/NixOS/nix/security/advisories/GHSA-vh5x-56v6-4368",
    "nix_ghsa_gr92": "https://github.com/NixOS/nix/security/advisories/GHSA-gr92-w2r5-qw5p",
    "nix_ghsa_6h4g": "https://github.com/NixOS/nix/security/advisories/GHSA-6h4g-g5j9-fm5f",
    "nix_2_35_notes": "https://nix.dev/manual/nix/2.35/release-notes/rl-2.35",
    "lanzaboote_packaging_pr": "https://github.com/NixOS/nixpkgs/pull/496059",
    "nixpkgs_source_provenance": "https://github.com/NixOS/nixpkgs/pull/425478",
    "trustix_rebuilt": "https://github.com/nix-community/trustix",
    "sbomnix": "https://github.com/tiiuae/sbomnix",
    "nixos_reproducibility_iso": "https://reproducible.nixos.org/nixos-iso-gnome-r13y/",
    "reproducible_study_2025": "https://arxiv.org/pdf/2501.15919",
    "nixos_hardening_wiki": "https://wiki.nixos.org/wiki/NixOS_Hardening",
    "nix_hardened_removed": "https://github.com/NixOS/nixpkgs/pull/501199",
    "secureblue_v491": "https://github.com/secureblue/secureblue/releases/tag/v4.9.1",
    "secureblue_v430": "https://github.com/secureblue/secureblue/releases/tag/v4.3.0",
    "fedora_wayland_only": "https://fedoraproject.org/wiki/Changes/WaylandOnlyGNOME",
    "debian_trixie": "https://www.debian.org/releases/trixie/index.en.html",
    "ubuntu_2604_security": "https://ubuntu.com/blog/ubuntu-26-04-lts-security-updates",
    "kicksecure_verified_boot": "https://www.kicksecure.com/wiki/Verified_Boot",
    "talos_1_12_notes": "https://github.com/siderolabs/talos/releases/tag/v1.12.0",
    "talos_secureboot_docs": "https://docs.siderolabs.com/talos/v1.12/platform-specific-installations/bare-metal-platforms/secureboot",
    "ubuntu_core_26_fde": "https://documentation.ubuntu.com/core/explanation/full-disk-encryption/index.html",
    "firecracker_jailer_advisory": "https://aws.amazon.com/security/security-bulletins/2026-003-AWS/",
    "firecracker_jailer_docs": "https://github.com/firecracker-microvm/firecracker/blob/main/docs/jailer.md",
    "gvisor_security_policy": "https://gvisor.dev/security/",
    "gvisor_seccheck": "https://github.com/google/gvisor/blob/master/pkg/sentry/seccheck/README.md",
    "linux_landlock_docs": "https://docs.kernel.org/userspace-api/landlock.html",
    "seccomp_pin_args": "https://lwn.net/Articles/1070987/",
    "io_uring_hardening": "https://www.systemshardening.com/articles/linux/io-uring-hardening/",
    "ubuntu_restricted_userns": "https://ubuntu.com/blog/ubuntu-23-10-restricted-unprivileged-user-namespaces",
    "userns_debate_lwn": "https://lwn.net/Articles/1079640/",
    "openbsd_78": "https://www.openbsd.org/78.html",
    "openbsd_79": "https://www.openbsd.org/79.html",
    "openbsd_errata78": "https://www.openbsd.org/errata78.html",
    "sel4_2026_news": "https://www.sel4.systems/news/2026.html",
    "microkit_2_3": "https://docs.sel4.systems/releases/microkit/2.3.0",
    "sculpt_26_04": "https://genode.org/news/sculpt-os-release-26.04",
    "grapheneos_releases": "https://grapheneos.org/releases",
    "tails_7_12": "https://tails.net/news/version_7.12/",
    "whonix_18_support": "https://forums.whonix.org/t/whonix-17-end-of-security-support-and-deprecation-notice-all-users-should-move-to-whonix-18-as-soon-as-possible/22644",
    "cloud_hypervisor_v52": "https://www.cloudhypervisor.org/blog/cloud-hypervisor-v52.0-released/",
    "owasp_agentic_tm": "https://genai.owasp.org/resource/agentic-ai-threats-and-mitigations/",
    "owasp_agentic_top10": "https://genai.owasp.org/2025/12/09/owasp-top-10-for-agentic-applications-the-benchmark-for-agentic-security-in-the-age-of-autonomous-ai/",
    "csa_maestro": "https://cloudsecurityalliance.org/blog/2025/02/06/agentic-ai-threat-modeling-framework-maestro",
    "csa_securing_swarm": "https://cloudsecurityalliance.org/blog/2026/06/24/securing-the-swarm-governance-attack-surfaces-and-zero-trust-architectures-in-multi-agent-ai-environments",
    "csa_agent_insider": "https://labs.cloudsecurityalliance.org/wp-content/uploads/2026/03/AI-agent-insider-threat-autonomous-compromise-v1-csa-styled.pdf",
    "mcp_spec_changelog": "https://modelcontextprotocol.io/specification/2025-06-18/changelog",
    "mcp_tools_annotations": "https://modelcontextprotocol.io/specification/2025-06-18/server/tools",
    "mcp_registry_preview": "https://blog.modelcontextprotocol.io/posts/2025-09-08-mcp-registry-preview/",
    "mcp_spec_2025_11": "https://blog.modelcontextprotocol.io/posts/2025-11-25-first-mcp-anniversary/",
    "a2a_protocol": "https://a2a-protocol.org/latest/",
    "anthropic_sandboxing": "https://www.anthropic.com/engineering/claude-code-sandboxing",
    "anthropic_contain_claude": "https://www.anthropic.com/engineering/how-we-contain-claude",
    "codex_sandboxing": "https://openai-codex.mintlify.app/architecture/sandboxing",
    "gemini_cli_sandbox": "https://google-gemini.github.io/gemini-cli/docs/cli/sandbox.html",
    "nist_ai_agent_standards": "https://www.nist.gov/artificial-intelligence/ai-agent-standards-initiative",
    "nist_ai_600_1": "https://nvlpubs.nist.gov/nistpubs/ai/nist.ai.600-1.pdf",
    "eu_ai_act_transparency": "https://digital-strategy.ec.europa.eu/en/policies/guidelines-ai-transparency-obligations",
    "ietf_agent_identity": "https://datatracker.ietf.org/doc/draft-klrc-aiagent-auth/",
    "aisi_inspect_framework": "https://inspect.aisi.org.uk/",
    "aisi_control_red_team": "https://www.aisi.gov.uk/blog/how-our-new-control-red-team-is-stress-testing-frontier-monitors",
    "apollo_automode": "https://apolloresearch.ai/monitoring/pilot-automode-campaign",
    "shade_arena": "https://www.anthropic.com/research/shade-arena-sabotage-monitoring",
    "claude_code_auto_mode": "https://www.anthropic.com/engineering/claude-code-auto-mode",
}

TIER_VOCAB = {"official", "advisory", "incident_report", "research", "community"}

EXPECTED_BASELINE = {
    "ncsc_horizon_year": 2027,
    "anthropic_targeted_entities": 30,
    "aisi_runs_total": 122,
    "aisi_unsanctioned_runs": 10,
    "aisi_incident_days": "2026-07-25..28",
    "aixcc_year": 2025,
    "qsb_118_fix_package": "qubes-core-dom0-linux 4.3.22",
    "nixos_2605_support_end": "2026-12-31",
    "ncsc_original_date": "2024-01-24",
    "gtg1002_autonomy_low_pct": 80,
    "gtg1002_autonomy_high_pct": 90,
    "gtg1002_decision_points_low": 4,
    "gtg1002_decision_points_high": 6,
    "aisi_actions": 19,
    "aisi_models": 7,
    "aixcc_identified_pct": 86,
    "aixcc_patched_pct": 68,
    "aixcc_real_vulns": 18,
    "qsb_118_cve": "CVE-2026-82636",
    "qsb_118_cvss": 7.9,
    "openai_hf_actions": 17600,
    "reproducible_iso_pct": 95.18,
    "reproducible_closure_pct": 99.48,
    "ncsc_2027_assessment_date": "2025-05-07",
    "aisi_report_published": "2026-08-04",
}

BIB_ENTRY_RE = re.compile(r"@(\w+)\s*\{\s*([^,\s]+)\s*,")


def test_150_unique_source_keys_matching_pinned_set():
    keys = [s.key for s in evidence.SOURCES]
    assert len(evidence.SOURCES) == 150
    assert len(set(keys)) == 150
    assert set(keys) == set(PINNED_URLS)


def test_urls_match_brief_mapping_and_are_https():
    for source in evidence.SOURCES:
        assert source.url == PINNED_URLS[source.key], source.key
        assert source.url.startswith("https://"), source.key


def test_tiers_in_vocabulary_and_every_tier_populated():
    for source in evidence.SOURCES:
        assert source.tier in TIER_VOCAB, (source.key, source.tier)
    from collections import Counter

    assert set(evidence.sources_by_tier()) == TIER_VOCAB
    counts = evidence.sources_by_tier()
    assert sum(counts.values()) == 150
    assert counts == dict(Counter(s.tier for s in evidence.SOURCES))


def test_sources_have_title_publisher_year_and_claims():
    for source in evidence.SOURCES:
        assert source.title.strip(), source.key
        assert source.publisher.strip(), source.key
        assert isinstance(source.year, int) and 1970 <= source.year <= 2027, source.key
        assert source.claims, source.key
        assert all(claim.strip() for claim in source.claims), source.key


def test_capability_baseline_matches_pinned_values():
    assert evidence.CAPABILITY_BASELINE == EXPECTED_BASELINE


def test_bib_parity_every_source_key_is_a_bib_entry(project_root):
    bib_text = (project_root / "manuscript" / "references.bib").read_text(encoding="utf-8")
    bib_keys = {match.group(2) for match in BIB_ENTRY_RE.finditer(bib_text)}
    source_keys = {s.key for s in evidence.SOURCES}
    missing = source_keys - bib_keys
    assert not missing, f"SOURCES keys missing from references.bib: {sorted(missing)}"
    # v0.2.0 contract: 156 entries total = 150 source-derived + 6 scholarly.
    scholarly = {
        "saltzer1975",
        "lampson1974",
        "klein2009",
        "hardy1988",
        "nist_sp800_207",
        "levy1984",
    }
    assert scholarly <= bib_keys
    assert len(bib_keys) >= 156
