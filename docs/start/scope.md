# Scope

PHLIPPED covers attacks where the attacker is physically present, or has physically placed a device, and the attack runs through an electronic channel.

## In scope

- Proximity electronic attacks of the kind a Flipper Zero performs: sub-GHz, NFC and RFID, infrared, iButton.
- HID injection through BadUSB devices, Rubber Ducky style tools and the O.MG cable.
- Drop devices on corporate networks: Raspberry Pi and ESP32 boards, hardware implants.
- Badge cloning and the physical access control systems that accept the clones.
- Rogue Wi-Fi access points and captive portals set up on the premises.
- Immediate electronic side channels such as USB exfiltration.

## Out of scope

- Mechanical lockpicking, safe manipulation and physical door bypass. Others have covered this well, for example the TOOOL community and Deviant Ollam.
- Social engineering with no electronic vector, a field with its own literature.
- Optical surveillance and counter-surveillance.
- State-level threats such as TEMPEST and deep RF emanation analysis.

!!! note "Why the line sits here"
    A narrower scope keeps every catalog entry testable and every claim defensible with a small team and a fixed amount of time. Anything on the out-of-scope list could become a later extension, but none of it is attempted in this release.
