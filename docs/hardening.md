# Hardening

The hardening playbook covers each threat in three layers: prevent, detect and respond. Every measure carries an approximate cost in euros and an effort in hours, so a small organisation can rank the work against a real budget instead of guessing.

The layers live in two places in the data. Prevent and respond measures are mitigations, each recording its phase, the techniques it addresses, a cost, an effort and a short description; browse them in the [mitigations](mitigations/index.md) section. Detection is the job of the rules in the [detections](detections/index.md) section, which is why a mitigation's phase is either prevent or respond.

Prevention closes the hole, for example by moving from 125 kHz proximity or MIFARE Classic badges to cards with mutual authentication. Detection shortens the time an attack goes unnoticed. Response says what to do when a rule fires, such as revoking the flagged badge and checking who last used it. The [worked thread](worked-thread.md) shows all three on one attack, and the [assessment](assessment.md) points each unmet checklist item at the measures that close it.

The cost and effort figures are planning estimates, not quotes. Use them to compare options against each other.
