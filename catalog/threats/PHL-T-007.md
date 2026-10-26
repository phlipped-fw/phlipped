---
id: PHL-T-007
name: Evil twin rogue AP with captive portal credential harvest
category: rogue-ap
prerequisites:
  physical_access: rf-range
  time_seconds: 300
  hardware: [ESP32 Marauder, WiFi Pineapple, laptop with monitor-mode dongle]
  skill_level: 2
mitre_attack: [T1557, T1539, T1566.002]
mitre_d3fend: [D3-NTA]
observables:
  - Duplicate corporate SSID with BSSID outside the known AP MAC pool
  - Sudden DEAUTH frame burst against the legitimate AP (forcing client roam)
  - Client devices probe-requesting then associating to the BSSID outside expected channels
  - Captive-portal-style HTTP 302 to an attacker-controlled host
known_tools: [WiFi Pineapple, ESP32 Marauder, hostapd-wpe, Airgeddon]
severity: 7.5
---

# Evil twin rogue AP

The attacker broadcasts an SSID identical to the corporate WiFi at higher signal strength (or after deauthenticating clients from the legitimate AP) and serves a captive portal that mimics the company SSO. Victims enter credentials, which the attacker forwards to the real IdP or simply harvests.

## Attack chain

1. Attacker arrives within RF range of the target premises.
2. Optionally deauths clients off the legitimate AP using `aireplay-ng` or Marauder.
3. Brings up a hostapd AP with the same SSID and a captive portal cloning the corp login.
4. Victims connect; credentials are captured. Optional: attacker proxies real auth so victim sees normal behavior.

## Why it matters

Even SSO + MFA does not fully neutralize this if the captive portal also harvests the TOTP / push approval in real time (attacker-in-the-middle pattern, also known as Evilginx-style for web SSO).

## Defensive layers

- Detection: `PHL-D-007` (duplicate SSID with foreign BSSID), `PHL-D-009` (deauth burst), `PHL-D-010` (client SSID probe to corp name from outside expected client pool).
- Prevent: enterprise WPA2/3 with EAP-TLS (mutual cert auth, no password to phish); phishing-resistant MFA (WebAuthn/FIDO2); disable WPA2-PSK SSIDs for staff.
- Respond: alert on duplicate BSSID via Kismet or APs in wireless IDS mode; rotate any credentials observed authenticating on the rogue AP; geographically locate via signal triangulation.
