# About PHLIPPED

PHLIPPED is a defensive framework for physical electronic attacks: the class of
intrusions that use cheap, pocket-sized radios and implants, such as a Flipper
Zero cloning a badge, a malicious USB cable typing commands into a locked
workstation, or a dropped Raspberry Pi phoning home from inside the network.
Most security tooling assumes the attacker is remote. PHLIPPED assumes they
walked in.

## Parts and status

The framework is made of five parts: a threat catalog, an assessment method, a
detection layer, a hardening playbook and a reference implementation. The
[architecture](start/architecture.md) page describes each one and how they
connect.

PHLIPPED is in alpha. The catalog, the assessment command, the detection rules
as authored files and one fully worked thread (badge cloning) are in place, and
the site rebuilds from the data on every change. Full detection coverage across
the catalog, validation of the rules against live telemetry and the lab that
does it are on the roadmap, not in this release.

## How the pieces fit

```
threats  ->  phlipped.json  ->  this site (what the attacks are)
                            ->  assessment score (how exposed you are)
indicators  ->  detection rules (how you catch it)
            ->  remediation (how you close it)
```

Start with the [worked thread](worked-thread.md) to see the whole loop on one
attack, then browse the [catalog](techniques/index.md).

## Licence

MIT. Source lives at
[github.com/phlipped-fw/phlipped](https://github.com/phlipped-fw/phlipped).
