---
id: PHL-T-003
name: MIFARE Classic key recovery and cloning
category: rfid-nfc
prerequisites:
  physical_access: proximity
  time_seconds: 30
  hardware: [Flipper Zero, Proxmark3, ChameleonMini]
  skill_level: 2
mitre_attack: [T1556, T1078]
mitre_d3fend: [D3-HBPI]
observables:
  - Repeated reads of the same UID with rapid retries (Mfkey32 / nested key recovery in progress)
  - Card-not-found events followed minutes later by successful auth with same UID
  - Inventory drift in PACS when emulated cards reuse UIDs of decommissioned ones
known_tools: [Flipper Zero (Mfkey32), Proxmark3, ChameleonMini, mfoc, mfcuk]
severity: 8.0
---

# MIFARE Classic key recovery and cloning

MIFARE Classic 1K/4K cards use the proprietary Crypto1 cipher with well-documented cryptographic flaws (Garcia et al. 2008, Courtois 2009). Sector keys can be recovered offline via nested or dark-side attacks, or in real time using Mfkey32 by sniffing a single reader authentication. Once any sector key is known, the entire card cloneable.

## Attack chain

1. Attacker presents a Flipper Zero in MFKey32 detection mode near the reader during a legitimate badge tap.
2. The Flipper captures the nT/nR/aR challenge-response and recovers the sector key in seconds.
3. Full dump performed against the original card; emulation onto a Magic UID card or Flipper.
4. Cloned card grants access indistinguishably from the original.

## Why it matters

MIFARE Classic remains widely deployed in transit systems, gym chains, hotel locks, and budget office PACS despite being formally broken for 17 years. Migration path is DESFire EV2/EV3 or Seos.

## Defensive layers

- Detection: `PHL-D-003` - UID anomaly detection on the PACS (same UID seen in geographically incompatible readers within a window).
- Prevent: migrate to DESFire EV3 with AES mutual authentication and diversified keys.
- Respond: revocation procedure for any UID flagged as anomalous; physical inspection of last user.
