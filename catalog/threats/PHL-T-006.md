---
id: PHL-T-006
name: O.MG Cable (malicious USB cable with HID + WiFi C2)
category: hid-injection
prerequisites:
  physical_access: touch
  time_seconds: 60
  hardware: [O.MG Cable, O.MG Programmer]
  skill_level: 3
mitre_attack: [T1200, T1059.001, T1102]
mitre_d3fend: [D3-PSA]
observables:
  - Unfamiliar WiFi SSID broadcast briefly near a victim workstation (cable's hotspot mode)
  - HID device enumeration of an "Apple Inc." or "Lightning" descriptor on a non-Apple host
  - Outbound DNS to known O.MG C2 paths (if cable is configured for callback)
  - Process spawn with characteristics of `PHL-T-002` typing-burst
known_tools: [O.MG Cable (USB-A, USB-C, Lightning variants)]
severity: 8.5
---

# O.MG Cable

The O.MG Cable looks identical to a vendor USB cable but contains an ESP32 plus an HID controller. It can deliver Rubber Ducky scripts, expose a WiFi access point for live keyboard injection, and self-destruct firmware on completion. Detection is hard because the cable also passes data and charge transparently.

## Attack chain

1. Attacker swaps an unattended cable (charging station, conference room, executive desk) for an O.MG.
2. Victim plugs in their phone/laptop, OS enumerates the HID controller alongside the legitimate USB-PD/USB-DATA endpoints.
3. Attacker connects to the cable's beacon or scheduled trigger fires payload directly into the victim's session.
4. Cable optionally self-erases firmware after payload completes.

## Why it matters

The O.MG breaks two defensive assumptions at once: "USB devices I personally bought are trusted" and "USB lockdown blocks bad cables." Visual inspection is unreliable; only x-ray or pre-purchased trusted-source cables defeat it.

## Defensive layers

- Detection: `PHL-D-002` (typing-burst), `PHL-D-006` (unusual HID descriptors enumerated on locked sessions), `PHL-D-008` (ephemeral SSID broadcasts near sensitive workstations).
- Prevent: USB Data Blockers ("USB condoms") on charging stations; sealed, inventory-tracked cables for executives; physically distinct cable colors per location.
- Respond: trigger workstation isolation on Sysmon Event ID 12/13/14 burst plus typing anomaly; physical seizure of the cable for forensics.
