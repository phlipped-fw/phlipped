---
id: PHL-T-010
name: Vehicle key fob relay attack (signal amplification)
category: sub-ghz
prerequisites:
  physical_access: rf-range
  time_seconds: 30
  hardware: [Relay attack pair (active + passive antennas), HackRF, custom SDR setup]
  skill_level: 3
mitre_attack: [T1200]
mitre_d3fend: []
observables:
  - Vehicle unlock event timestamps inconsistent with the registered fob's known location
  - Telematics platforms reporting key-in-vehicle status while owner has fob elsewhere
known_tools: [Commercial relay devices ("car opener boxes"), HackRF + custom firmware]
severity: 7.0
---

# Vehicle key fob relay attack

Modern Passive Keyless Entry (PKE) systems unlock when the fob is in proximity to the vehicle. A relay attack uses two devices, one near the fob (often inside a home) and one near the car, to extend the apparent proximity over arbitrary distance. Within seconds the vehicle is unlocked and started.

## Attack chain

1. Attacker A stands next to the parked vehicle with the "car-side" relay device.
2. Attacker B walks past the owner's home or pocket with the "fob-side" device.
3. The two devices relay the LF/UHF challenge-response between the car and fob in real time.
4. Vehicle treats the fob as present, unlocks and ignites.

## Why it matters

While outside the office context of the rest of PHLIPPED, this threat is included because executive vehicles in corporate carparks are a documented attack vector and increasingly a chain into laptop theft or social engineering pivots.

## Defensive layers

- Detection: telematics anomaly detection (vehicle off-pattern movement); CCTV with motion-trigger on parked exec vehicles.
- Prevent: store key fob in a Faraday pouch; enable PIN-to-drive on vehicles that support it; disable PKE mode and use the physical key.
- Respond: vehicle GPS recovery; physical security review of executive parking; PR / legal escalation if data was in the stolen vehicle.
