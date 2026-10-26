---
id: PHL-T-009
name: WPA handshake capture and offline cracking (pwnagotchi, opportunistic)
category: rogue-ap
prerequisites:
  physical_access: rf-range
  time_seconds: 1200
  hardware: [Raspberry Pi Zero + USB WiFi, pwnagotchi, ESP32 Marauder, laptop]
  skill_level: 2
mitre_attack: [T1110, T1200]
mitre_d3fend: []
observables:
  - DEAUTH frame bursts to force client reauthentication
  - Pmkid capture queries to the AP (no client interaction required for WPA2-PSK with newer attack)
  - Unknown WiFi MAC OUI observed continuously near the perimeter (pwnagotchi badge frame leaks)
known_tools: [pwnagotchi, hcxdumptool, aircrack-ng suite, hashcat, ESP32 Marauder]
severity: 6.0
---

# WPA handshake capture and offline cracking

A pocket Linux device passively or actively captures the 4-way handshake (or directly the PMKID via the AP's RSN IE) and ships it off for offline cracking with `hashcat`. Pwnagotchi makes this a fire-and-forget badge that an attacker leaves running in their pocket during a coffee-shop or office visit.

## Attack chain

1. Attacker enters RF range with the capture device running.
2. Optional active deauth forces clients to reauthenticate, exposing the 4-way handshake.
3. Newer PMKID attack pulls a crackable hash from the AP itself with no client needed.
4. Offline cracking against a wordlist or rules-based attack reveals the PSK if it is weak.

## Why it matters

Mainly a threat for WPA2-PSK / WPA3-Personal corporate guest networks and any staff network not on EAP-TLS. Once the PSK is cracked, the attacker rejoins the network at will from a distance, indistinguishable from a legitimate device on the wire.

## Defensive layers

- Detection: `PHL-D-009` (deauth burst), `PHL-D-013` (pwnagotchi-style probe pattern with characteristic SSID list).
- Prevent: WPA2/3-Enterprise with EAP-TLS only; segregated guest VLAN with rate-limit; long random PSK with rotation if Personal is unavoidable.
- Respond: rotate guest PSK on detection; investigate connected devices for unusual traffic; revoke certs proactively when EAP-TLS is in use.
