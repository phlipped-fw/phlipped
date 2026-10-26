---
id: PHL-T-001
name: HID Prox 125 kHz cloning
category: rfid-nfc
prerequisites:
  physical_access: proximity
  time_seconds: 5
  hardware: [Flipper Zero, Proxmark3]
  skill_level: 1
mitre_attack: [T1556, T1078]
mitre_d3fend: [D3-HBPI]
observables:
  - Badge reader logs with duplicate UID within short timeframe
  - Failed reads on retired card numbers
known_tools: [Flipper Zero, Proxmark3, ChameleonMini]
severity: 7.5
---

# HID Prox 125 kHz cloning

Legacy HID Prox 125 kHz badges transmit a static, unauthenticated ID. A Flipper Zero in LF mode reads and replays the credential in seconds.

## Attack chain

1. Attacker approaches badge within ~10 cm (pocket-level distance with antenna boost).
2. Flipper Zero reads the UID and stores it.
3. Replay against any compatible reader grants access.

## Why it matters

Still deployed widely in office buildings, gyms, parking garages. Migration to iCLASS SE / Seos or DESFire EV3 with mutual authentication is the only durable fix.

## Defensive layers

See `phlipped-rules/PHL-D-001` (detection) and the hardening playbook for migration guidance.
