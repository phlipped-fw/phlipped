# About PHLIPPED

PHLIPPED is a defensive framework for physical electronic attacks: the class of
intrusions that use cheap, pocket-sized radios and implants, such as a Flipper
Zero cloning a badge, a malicious USB cable typing commands into a locked
workstation, or a dropped Raspberry Pi phoning home from inside the network.
Most security tooling assumes the attacker is remote. PHLIPPED assumes they
walked in.

## The four parts

- **Catalog.** A structured list of physical electronic threats. Each entry
  records how hard the attack is, what hardware it needs, how it maps to MITRE
  ATT&CK, and what it leaves behind in the logs. This site is the catalog.
- **Assessment.** A command-line tool that walks you through a short checklist
  and produces a Physical Security Posture Score from 0 to 100, plus your worst
  gaps ranked by weight, each linked to the catalog threat it comes from.
- **Detection rules.** Sigma and Wazuh rules written to fire on the indicators
  in the catalog. Every rule carries the id of the threat it defends against.
  The rules are authored; validating them against live telemetry is roadmap.
- **Lab.** A reproducible environment for validating that the rules fire as
  expected against sample telemetry.

## Status

This is an **alpha**. The catalog holds ten threats, the assessment tool and one
fully-worked thread (badge cloning) are complete, and the site deploys
automatically. Full detection coverage for every threat and a live validation
lab are on the roadmap, not in this release.

## How the pieces fit

```
threats  ->  phlipped.json  ->  this site (what the attacks are)
                            ->  assessment score (how exposed you are)
indicators  ->  detection rules (how you catch it)
            ->  remediation (how you close it)
```

Start with the [worked thread](worked-thread.md) to see the whole loop on one
attack, then browse the [catalog](index.md).

## Licence

MIT. Source lives at
[github.com/phlipped-fw/phlipped](https://github.com/phlipped-fw/phlipped).
