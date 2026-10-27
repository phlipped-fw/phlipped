# Architecture

PHLIPPED has five parts that depend on each other.

1. **Threat catalog.** A hierarchical taxonomy of physical electronic attacks. Each entry has a unique identifier, prerequisites (physical access, time, hardware, skill level from 1 to 5), a MITRE ATT&CK mapping, observable indicators, known tools and a baseline severity. Browse it in the [catalog](../techniques/index.md).
2. **Assessment methodology.** An auditable checklist that produces the Physical Security Posture Score (PSPS), from 0 to 100. See [assessment](../assessment.md).
3. **Detection layer.** Wazuh and Sigma rules, one set per threat, for example a typing-rate rule for HID injection, a duplicate-SSID rule for rogue access points, and a rule for a drop-device MAC prefix appearing on a non-IT VLAN. See [detections](../detections/index.md).
4. **Hardening playbook.** Prevent, detect and respond measures per threat, each with an approximate cost in euros and an effort in hours. See [hardening](../hardening.md).
5. **Reference implementation and validation.** The `phlipped-assess` command, a docker-compose lab, and a validation report that compares a baseline environment with a hardened one. The lab and report are roadmap items.

All five read from the same source. Per-object files under `data/` are compiled by a build step into a single `phlipped.json`, and the site, the assessment command and the tests consume that file. The [data model](../data-model.md) describes the objects and the [decisions](../decisions.md) record why they look the way they do.
