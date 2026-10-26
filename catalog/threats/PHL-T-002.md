---
id: PHL-T-002
name: HID injection via BadUSB
category: hid-injection
prerequisites:
  physical_access: touch
  time_seconds: 3
  hardware: [RubberDucky, O.MG Cable, Flipper Zero BadUSB]
  skill_level: 2
mitre_attack: [T1200, T1059.001]
mitre_d3fend: [D3-PSA]
observables:
  - cmd.exe / powershell.exe spawned with no parent UI focus
  - Burst typing speed >80 keystrokes/sec sustained
  - USB device enumeration of HID class on locked workstations
known_tools: [RubberDucky, Bash Bunny, O.MG Cable, Flipper Zero]
severity: 8.0
---

# HID injection via BadUSB

A device emulating a USB HID keyboard injects keystrokes at machine speed. Bypasses USB mass-storage controls because the OS sees a keyboard.

## Defensive layers

- Detection: typing-rate anomaly via Sysmon Event ID 1 + endpoint telemetry. See `phlipped-rules/PHL-D-002`.
- Prevent: USB lockdown via GPO restricting HID class on locked sessions; physical port blockers on kiosks.
- Respond: isolate endpoint, review last 60s of process tree, revoke any credentials potentially touched.
