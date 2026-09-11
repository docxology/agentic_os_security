"""Evidence registry invariants: 65 pinned sources, tier vocabulary,
URL contract, capability baseline, and bib parity with references.bib.

The key->URL mapping below is pinned by the project brief; the evidence
module must reproduce it exactly (plus the https scheme). Bib parity is
checked with a regex over `@<type>{<key>,` occurrences — no bibtex parser
dependency.
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
}

BIB_ENTRY_RE = re.compile(r"@(\w+)\s*\{\s*([^,\s]+)\s*,")


def test_65_unique_source_keys_matching_pinned_set():
    keys = [s.key for s in evidence.SOURCES]
    assert len(evidence.SOURCES) == 65
    assert len(set(keys)) == 65
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
    assert sum(counts.values()) == 65
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
    # Brief: 71 entries total = 65 source-derived + 6 scholarly.
    scholarly = {
        "saltzer1975",
        "lampson1974",
        "klein2009",
        "hardy1988",
        "nist_sp800_207",
        "levy1984",
    }
    assert scholarly <= bib_keys
    assert len(bib_keys) >= 71
