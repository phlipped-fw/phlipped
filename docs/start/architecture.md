# Architecture

PHLIPPED has five parts that depend on each other.

The threat catalog is a hierarchical taxonomy of physical electronic attacks. Each entry has a unique identifier, prerequisites (physical access, time, hardware, skill level from 1 to 5), a MITRE ATT&CK mapping, observable indicators, known tools and a baseline severity. Browse it in the [catalog](../techniques/index.md).

The assessment methodology is an auditable checklist that produces the Physical Security Posture Score (PSPS), from 0 to 100. It is described on the [assessment](../assessment.md) page.

The detection layer holds Wazuh and Sigma rules, one set per threat: a typing-rate rule for HID injection, a duplicate-SSID rule for rogue access points, a rule for a drop-device MAC prefix appearing on a non-IT VLAN. They are listed under [detections](../detections/index.md).

The hardening playbook gives prevent, detect and respond measures per threat, each with an approximate cost in euros and an effort in hours. See [hardening](../hardening.md).

The reference implementation is the `phlipped-assess` command together with a docker-compose lab and a validation report that compares a baseline environment with a hardened one. The assessment command exists today; the lab and the report are roadmap items.

All five read from the same source. Per-object files under `data/` are compiled by a build step into a single `phlipped.json`, and the site, the assessment command and the tests consume that file. The [data model](../data-model.md) describes the objects and the [decisions](../decisions.md) record why they look the way they do.
