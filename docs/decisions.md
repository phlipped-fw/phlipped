# Design decisions

A record of the decisions that shaped the PHLIPPED data layer, with the reasoning
and the cost if a decision turns out wrong. These are the choices that are not
obvious from reading the code, kept here so they survive and so the systematic
review has the rationale in front of it.

Each entry is dated and states what was decided, why, and what it costs to reverse.

## D1. Data first: the framework is a validated dataset

PHLIPPED is a set of per-object source files under `data/`, compiled by a Python
build into a single validated `phlipped.json`. The website and the assessment tool
are consumers of that artifact. They never read the source files directly and never
hand-edit the JSON.

Why: a framework that other people cite and audit needs stable identifiers and a
single source of truth. Putting the content in validated data, not in prose or in a
site generator, means the taxonomy can be checked, versioned, and rebuilt without
touching any consumer.

Cost if wrong: low. The consumers are thin; repointing them at a different artifact
shape is a contained change.

## D2. Container now, content later

The object model, the identifier scheme, and the build pipeline are fixed. The
taxonomy they hold is provisional. The final tactic list, the validated technique
set, and the checked external mappings are outputs of the systematic literature
review, not of this build.

Why: the review gates the graded academic work. Locking the structure lets the
review fill in content without a restructure, and keeps the alpha honest about what
is validated and what is a starting point.

Cost if wrong: low. The schema was built to accept whatever the review concludes.

## D3. Detections carry their rule logic inline

A detection is an object in `data/detections/PHL-D-NNN.yml` with a `logic` field
holding the rule body as a block of text. There is no pointer to a separate rule
file, and the old standalone `rules/sigma/` tree was folded into the detection
objects and removed.

Why: the spec lists `logic` as a field of the detection object, and the repository
architecture has no separate rules directory. One object, one source of truth.

Cost if wrong: low and additive. If deployable Sigma or Wazuh files are wanted
later, the build can generate them from the `logic` field. The Wazuh rules under
`rules/wazuh/` and the detection lab under `lab/` were left in place untouched,
because the lab mounts them and reconciling the lab belongs to the site and
infrastructure plan, not here.

Date: 2026-10-27.

## D4. No fabricated numbers on mitigations

`cost_eur` and `effort_hours` are optional on a mitigation. Only the five
mitigations that came from the real assessment checklist carry those figures, copied
over verbatim. The thirteen mitigations derived from technique prose carry neither
field. The systematic review fills them with sourced values.

Why: a framework headed for academic review must not ship invented cost and effort
estimates. An absent field is honest; a made-up figure with a comment is not.

Cost if wrong: trivial to reverse. The fields are optional, so adding real values
later is a data edit with no schema change.

Date: 2026-10-27.

## D5. Mappings are first-class relations, not fields on a technique

The MITRE ATT&CK and D3FEND references that used to sit inline in each technique
(`mitre_attack`, `mitre_d3fend`) were extracted into relation files under
`data/mappings/` and removed from the techniques and from the technique schema. A
relation is `{subject_id, framework, external_id}`. The build resolves every subject
to a real technique or mitigation and emits a subject-by-framework matrix.

Why: the compliance translation layer is one of the framework's two novelty claims.
Modelling it as data, with a single source of truth and a generated matrix, makes it
an artifact an auditor can consume rather than prose a reader has to trust. The
`framework` field already allows `nist-csf`, `iso27001`, `nis2`, and `cis`, which the
review will populate.

Cost if wrong: low. The relations are separate files; changing their shape does not
touch the techniques.

Date: 2026-10-27.

## D6. The built JSON is a gitignored artifact

`phlipped.json` and the per-type files in `dist/` are build outputs, not committed
source. The build and CI regenerate them, and nothing hand-edits them.

Why: committing a derived artifact invites drift between it and the source. The build
is cheap and deterministic, so the artifact is produced on demand.

Cost if wrong: low. If a consumer needs a committed artifact, one line of
`.gitignore` reverses it.

## D7. Schemas reject unknown fields

Every object schema sets `additionalProperties: false`. A typo in a field name, or a
stray field, fails the build with a clear message rather than being silently ignored.

Why: silent acceptance of unknown fields is how data rots. For a dataset that is the
whole point of the project, strictness is worth the small cost of having to declare
every field.

Cost if wrong: low. Relaxing it is per-schema and reversible.

## D8. The assessment tool lives under tools/ and reads the built artifact

The `phlipped-assess` CLI moved from a top-level `assess/` to `tools/assess/`, to
match the repository architecture. It reads assessment items from the built
`phlipped.json` (via a `--data` option) instead of a bundled checklist. The
assessment score is derived from the object graph, because each assessment item
probes specific techniques or mitigations by id.

Why: the tool is a consumer of the data like any other, so it belongs beside the data
it consumes and reads the same validated artifact. Cost and effort figures that used
to live on checklist items now live on mitigations, which is their correct home, so
the tool no longer shows per-item cost.

Cost if wrong: low. The move preserved history, and the `--data` option keeps the
artifact path configurable.

Date: 2026-10-27.

## D9. A provisional tactic axis, built to be revised

The matrix needs a second axis. Until the review validates one from the literature,
the framework scaffolds a five-phase kill chain of a close-access intrusion:
Approach, Capture, Inject, Implant, Pivot or Exfil (`PHL-TA-01` to `PHL-TA-05`),
each marked `status: draft`. The identifiers and the object model do not change when
the review renames, splits, merges, or reorders them, and the tactic schema carries a
`deprecated` block so a retired tactic keeps its id rather than being deleted.

Why: a matrix needs columns to exist before techniques can be placed in it. Marking
the axis `draft` says plainly that the review refines it rather than inventing it
from nothing.

Cost if wrong: contained. The axis is five files and a set of `tactics:` fields on
the techniques; the review can revise both without a code change.

Date: 2026-10-27.

## Migration record

The data layer was built by consolidating and restructuring the four earlier
`phlipped-*` repositories and the Starlight docs, with history preserved. The moves:

- `phlipped-catalog/threats/PHL-T-NNN.md` became `data/techniques/PHL-T-NNN.md`
  (bodies unchanged, lifecycle fields added, inline MITRE refs extracted to mappings).
- The three Sigma rules under `phlipped-rules/sigma/` became detection objects under
  `data/detections/` with their logic inline; the standalone Sigma tree was removed.
- `phlipped-assess` became `tools/assess/`, reading the built artifact.
- The assessment checklist became `data/assessment/PSPS-NNN.yml`, one file per item,
  with `threat_refs` renamed to `probes`.
- The inline `mitre_attack` and `mitre_d3fend` on the ten techniques became 29
  mapping relations (21 ATT&CK, 8 D3FEND) under `data/mappings/`.

This traceability is deliberate, so the framework's history from the earlier
exploratory repositories to the restructured data layer is auditable.
