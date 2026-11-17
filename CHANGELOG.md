# Changelog

Versions follow the framework version in `build/build.py`. Breaking schema changes bump
major, new content bumps minor, corrections bump patch.

## 0.1.0-alpha (2026-11-17)

First tagged alpha.

- Data layer: 10 techniques, 5 provisional tactics, 8 data sources, 3 detections,
  18 mitigations, 6 assessment items and 29 MITRE mappings, compiled by `build/` into a
  validated `phlipped.json`.
- `phlipped-assess`: PSPS posture score and HTML gap report off the built artifact.
- Site: Material for MkDocs generated from `phlipped.json`, live at phlipped.n0t.space.
- Detections: Wazuh rules for PHL-D-002 (keystroke injection), PHL-D-003 (cloned MIFARE
  badge: failed-read burst then grant, and the same UID at two sites) and PHL-D-011
  (drop-device OUI on a non-IT VLAN).
- `lab/validate.py`: replays synthetic attack and benign events through a real Wazuh
  manager and checks every rule, gated in CI.

### Fixed

- The Wazuh rules never loaded in the lab: they were mounted into `local_rules.d`, which
  Wazuh does not read, and a mount under `/var/ossec/etc` stopped the image installing its
  config. Rules now go through `/wazuh-config-mount`.
- PHL-D-002 could never fire: its rule file sorted before the stock Sysmon rules, so its
  `if_sid` parent did not exist yet. Renamed to `phlipped_rules.xml`.
- PHL-D-002 alerted on any shell started from explorer and claimed a locked-session check
  it did not make. It now also requires a payload-style command line.
- PHL-D-003 had no Wazuh rule. Added correlation rules for both patterns.
- PHL-D-011 relied on a DHCP decoder that stock Wazuh does not ship. It now reads
  JSON-normalised DHCP/NAC events, with IT VLANs allow-listed.
