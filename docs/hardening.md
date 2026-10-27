# Hardening

The hardening playbook organises the response to each threat as prevent, detect and respond. Where a measure has a known approximate cost in euros and effort in hours, it records them, so a small organisation can rank the work against a real budget. Not every measure has those figures yet.

The three phases live in two places in the data. Prevent and respond measures are mitigations, each recording its phase, the techniques it addresses and a short description, plus a cost and an effort where known; browse them in the [mitigations](mitigations/index.md) section. Detection is the job of the rules in the [detections](detections/index.md) section, which is why a mitigation's phase is either prevent or respond.

Prevention closes the hole, for example by moving from 125 kHz proximity or MIFARE Classic badges to cards with mutual authentication. Detection shortens the time an attack goes unnoticed. Response says what to do when a rule fires, such as revoking the flagged badge and checking who last used it. The [worked thread](worked-thread.md) shows all three on one attack, and the [assessment](assessment.md) points each unmet checklist item at the measures that close it.

The cost and effort figures, where present, are planning estimates for comparing options.
