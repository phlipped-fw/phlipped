---
id: PHL-T-005
name: Drop device on corporate LAN (Responder / mitm6 / ntlmrelayx)
category: drop-device
prerequisites:
  physical_access: touch
  time_seconds: 30
  hardware: [Raspberry Pi, ESP32, LAN Turtle, Packet Squirrel]
  skill_level: 3
mitre_attack: [T1200, T1557.001, T1187]
mitre_d3fend: [D3-NTA, D3-ITF]
observables:
  - DHCP lease for unknown MAC OUI on a user VLAN (Pi Foundation B8:27:EB / DC:A6:32, Espressif 24:0A:C4)
  - Sudden LLMNR / NBT-NS / mDNS responder traffic from a single host
  - NTLM authentication attempts to a non-DC SMB endpoint
  - DHCPv6 advertisements from a non-infrastructure host (mitm6 indicator)
known_tools: [Responder, mitm6, ntlmrelayx, Impacket, LAN Turtle, Bash Bunny]
severity: 9.2
---

# Drop device on corporate LAN

A pocket-sized Linux device plugged into any reachable RJ45 port turns a five-second hallway visit into the foothold for full domain compromise. Default Windows name resolution (LLMNR, NBT-NS, mDNS) and DHCPv6 fallback hand NTLM hashes to anyone listening, and `ntlmrelayx` chains those into LDAP/SMB/MSSQL writes.

## Attack chain

1. Attacker plugs the device into a wall jack, printer port, or unattended desk switch.
2. Responder poisons name resolution; victim workstations send NTLM authentication to the attacker.
3. `mitm6` floods DHCPv6 to become the IPv6 DNS; attacker relays auth into the directory.
4. `ntlmrelayx` writes to an LDAP attribute or coerces a privileged service, escalating to domain admin.

## Why it matters

The "minutes of physical access to domain admin" pipeline is the highest-impact PHLIPPED scenario for SMEs. Almost every default Windows network is vulnerable unless LLMNR is GPO-disabled and SMB signing is enforced everywhere.

## Defensive layers

- Detection: `PHL-D-005` (Responder traffic anomaly), `PHL-D-011` (suspicious MAC OUI on non-IT VLAN), `PHL-D-006` (DHCPv6 from unknown host).
- Prevent: GPO-disable LLMNR and NBT-NS; require SMB signing; deploy 802.1X with MAB fallback alerts; physical port security on switches.
- Respond: NAC quarantine VLAN on first unauthorized MAC, physical inspection of the port, credential reset for any user observed authenticating to the rogue host.
