---
id: PHL-T-004
name: Sub-GHz fixed-code replay (garage doors, gates, simple remotes)
category: sub-ghz
prerequisites:
  physical_access: rf-range
  time_seconds: 10
  hardware: [Flipper Zero, HackRF, CC1101 dongle]
  skill_level: 1
mitre_attack: [T1200]
mitre_d3fend: []
observables:
  - Repeated identical RF frames captured by an SDR sensor near the perimeter
  - Gate/garage activation logs without a corresponding tenant authentication event
  - Tenant complaints of "ghost openings" outside their usage pattern
known_tools: [Flipper Zero, HackRF One, YARD Stick One, rtl_433]
severity: 6.5
---

# Sub-GHz fixed-code replay

Garage door openers, building perimeter gates, and many low-cost remotes built before the 2000s still use fixed-code OOK/ASK modulation on 315/433/868 MHz with no rolling code or authentication. A capture-and-replay attack with a Flipper Zero takes under 10 seconds and works at meaningful distance.

## Attack chain

1. Attacker idles within RF range while a legitimate user opens the gate.
2. Flipper captures the burst on 433.92 / 868 MHz.
3. Replay later, at will, from outside the immediate property line.

## Why it matters

Property breaches via sub-GHz replay are under-investigated because the physical entry leaves no electronic trail at the gate controller, only the open/close event. Insurance and CCTV review become the only forensic surface.

## Defensive layers

- Detection: `PHL-D-004` - out-of-pattern activation events correlated with no tenant credential.
- Prevent: replace fixed-code receivers with rolling-code (KeeLoq with secure session keys, AES-128 systems like Faac SLH or Came Hormann ProxiMity).
- Respond: incident playbook treats sub-GHz replay as physical intrusion; rotate codes if hardware supports it.
