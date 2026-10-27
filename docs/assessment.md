# Assessment

The assessment turns the catalog into a number and a to-do list. It is an auditable checklist whose yes or no answers produce the Physical Security Posture Score (PSPS), from 0 to 100, plus the worst gaps ranked by weight.

## How the score works

Each checklist item is a posture question with a weight from 0 to 10, for example whether the badge system uses mutually authenticated cards or whether 802.1X is enforced on publicly reachable network ports. The score is the weighted sum of the answers, normalised to 0 to 100.

The weights are set by hand, and each item links to the techniques or mitigations it probes, so every unmet item in the gap report traces back to a catalogued threat. Deriving the weights from technique severity is a possible later change, held back until a systematic literature review validates the inputs. See [decisions](decisions.md) D8 for the reasoning.

The checklist is short and grows with the catalog. The [data model](data-model.md) describes the item fields.

## Running it

The reference implementation is `phlipped-assess`, in `tools/assess` of the [repository](https://github.com/phlipped-fw/phlipped). It reads the items from the built `phlipped.json`.

```bash
python -m build.build
phlipped-assess run --data phlipped.json --out assessment.json
phlipped-assess report --in assessment.json --out report.html
```

The [building](building.md) guide covers setup, and the [hardening](hardening.md) playbook says what to do about each gap.
