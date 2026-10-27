# Introduction

PHLIPPED is a defensive framework for the physical electronic attacks that became cheap and easy to run over the last five years: a pocket radio that clones a badge, a USB cable that types commands, a small computer left plugged into a wall port.

The frameworks most organisations already use (NIST CSF 2.0, ISO 27001, CIS Controls, MITRE ATT&CK) touch physical security only lightly. They tell you to control physical access, but not how a cloned badge shows up in a door log or which USB policy stops a keystroke injector. PHLIPPED fills that gap with concrete detections, an auditable assessment method and hardening guidance written for small and medium organisations that have no internal red team.

## What it produces

- An open threat catalog, held as one validated dataset.
- A Python assessment command, `phlipped-assess`, that scores posture from 0 to 100.
- Detection rules in Sigma and Wazuh formats.
- A hardening playbook that costs each mitigation in euros and hours.
- A whitepaper and conference talk.

The first three exist in this release in alpha form; the [about page](../about.md) gives the exact state. For what the framework does and does not cover, read the [scope](scope.md); for how the pieces connect, the [architecture](architecture.md).
