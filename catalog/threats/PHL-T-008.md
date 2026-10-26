---
id: PHL-T-008
name: USB mass-storage exfiltration from kiosks and unattended endpoints
category: usb-exfil
prerequisites:
  physical_access: touch
  time_seconds: 60
  hardware: [USB flash drive, USB Rubber Ducky in storage mode, smartphone in MTP mode]
  skill_level: 1
mitre_attack: [T1052.001, T1200]
mitre_d3fend: [D3-IO]
observables:
  - Sysmon Event ID 6 (driver load) for `usbstor.sys` on locked workstations
  - Windows Event 4663 mass file reads from removable media drive letters
  - File copies sourced from sensitive shares to a removable volume
known_tools: [any USB flash drive, Bash Bunny in exfil mode, KeyCroc, USaBUSe]
severity: 7.0
---

# USB mass-storage exfiltration

The simplest physical attack: stick a USB drive into a kiosk, signage PC, conference-room laptop, or any session left logged in. Copy whatever is reachable from the user's privilege level. With Bash Bunny / Rubber Ducky variants, the device can both inject keystrokes to pop a shell and present itself as storage to receive the output.

## Attack chain

1. Attacker locates an endpoint with an active user session (kiosk, signage, abandoned workstation).
2. Inserts USB device; for advanced variants, simultaneous HID burst opens a script.
3. Files / browser cookies / SAM hive / SSH keys copied to the device.
4. Device removed; data offboarded.

## Why it matters

Cheap, fast, and bypasses everything except endpoint USB policy and proper session locking. Single most common physical exfil vector reported in industry incident retros.

## Defensive layers

- Detection: `PHL-D-012` (mass file read followed by removable-media write).
- Prevent: GPO disable USB mass storage on shared/kiosk endpoints; BitLocker so offline disk reads are also blocked; aggressive session timeout (60s) on signage/kiosks.
- Respond: USB device serial number captured by Sysmon allows physical traceback; combine with CCTV timestamp for attribution.
