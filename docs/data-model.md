# Data model

The PHLIPPED framework is one validated object graph. This page documents it as
built: the object types, their fields, the identifier and lifecycle rules, the
cross-references the build enforces, and the shape of the compiled artifact.

Source files live under `data/`, one file per object, grouped by type. The build
in `build/build.py` validates every object against a JSON Schema in `schema/`,
resolves every cross-reference, and emits `phlipped.json`. Nothing consumes the
source files directly, and nothing hand-edits the JSON.

## Object types

Seven object types make up the graph. Six are identified nodes; mappings are
relations (edges) with no identifier of their own.

### Tactic (`PHL-TA-NN`)

A column of the matrix: one phase of a close-access intrusion.

| Field | Required | Notes |
|---|---|---|
| id | yes | `PHL-TA-NN`, two digits |
| name | yes | |
| short_description | yes | |
| order | yes | integer, position on the axis |
| status, version, added, modified | yes | lifecycle |
| deprecated | no | `{superseded_by, reason}` |

The five current tactics are provisional and marked `status: draft`. See
[decisions](decisions.md) D9.

### Technique (`PHL-T-NNN`)

A catalogued attack. The source file is Markdown with YAML frontmatter; the prose
body is the technique write-up.

| Field | Required | Notes |
|---|---|---|
| id | yes | `PHL-T-NNN`, three digits |
| name | yes | |
| category | yes | one of rfid-nfc, sub-ghz, hid-injection, drop-device, rogue-ap, ir, ibutton, usb-exfil |
| prerequisites | yes | `{physical_access, time_seconds, hardware, skill_level}` |
| severity | yes | number 0 to 10; provisional, see below |
| tactics | yes | one or more tactic ids |
| data_sources | no | data source ids whose telemetry reveals the technique |
| observables | no | what a defender would see |
| known_tools | no | |
| status, version, added, modified | yes | lifecycle |
| deprecated | no | |

External framework references are not fields here; they are mapping relations.

`severity` is a 0 to 10 magnitude, higher meaning greater impact and lower
attacker effort combined. The current values are the author's provisional
judgment, not a standardised or sourced metric; the systematic review grounds or
replaces them. See [decisions](decisions.md) D10. `data_sources` is a
presence-only relation: it names the channels that reveal a technique, not the
channels that stay blind to it. The telemetry-mismatch argument lives in that
absence, which the data layer does not yet model; see the open modelling note in
[decisions](decisions.md).

### Data source (`PHL-DS-NN`)

A telemetry channel a defender watches.

| Field | Required | Notes |
|---|---|---|
| id | yes | `PHL-DS-NN`, two digits |
| name | yes | |
| kind | yes | one of PACS, RF, network, host, sensor |
| description | yes | |
| status, version, added, modified | yes | lifecycle |
| deprecated | no | |

The eight current data sources are a seed grounded in the telemetry the techniques'
observables already name, not an exhaustive catalogue.

### Detection (`PHL-D-NNN`)

A detection rule. The rule body is held inline (see [decisions](decisions.md) D3).

| Field | Required | Notes |
|---|---|---|
| id | yes | `PHL-D-NNN`, three digits |
| name | yes | |
| techniques | yes | one or more technique ids the rule covers |
| data_sources | yes | one or more data source ids the rule consumes |
| platform | yes | sigma or wazuh |
| logic | yes | the rule body, inline |
| false_positives | no | |
| status, version, added, modified | yes | lifecycle |
| deprecated | no | |

### Mitigation (`PHL-M-NNN`)

A prevent or respond countermeasure.

| Field | Required | Notes |
|---|---|---|
| id | yes | `PHL-M-NNN`, three digits |
| name | yes | |
| phase | yes | prevent or respond |
| techniques | yes | one or more technique ids it addresses |
| description | yes | |
| cost_eur | no | present only where a real source value exists |
| effort_hours | no | same |
| status, version, added, modified | yes | lifecycle |
| deprecated | no | |

### Mapping (relation)

A cross-reference to an external framework. A relation, not an identified object.

| Field | Required | Notes |
|---|---|---|
| subject_id | yes | a technique or mitigation id |
| framework | yes | one of attack, d3fend, nist-csf, iso27001, nis2, cis |
| external_id | yes | the external framework's identifier |
| note | no | |

Mappings are stored as lists under `data/mappings/`, one file per framework. The
build emits them as a flat list and also as a subject-by-framework matrix.

### Assessment item (`PSPS-NNN`)

A posture question. The Physical Security Posture Score is a weighted sum of
these items' yes/no answers, normalised to 0 to 100. Each item's `probes` link
it to the techniques or mitigations it concerns, which gives the gap report its
traceability from a posture gap to a catalogued threat. The score is not derived
from graph properties; see [decisions](decisions.md) D8.

| Field | Required | Notes |
|---|---|---|
| id | yes | `PSPS-NNN`, three digits |
| question | yes | |
| weight | yes | integer 0 to 10 |
| probes | yes | technique or mitigation ids the item scores against |
| recommendation | yes | |
| status, version, added, modified | yes | lifecycle |
| deprecated | no | |

## Identifiers and lifecycle

- Identifiers are permanent. A retired object is marked `deprecated`, never deleted
  and never reused, so external citations and prior releases stay valid.
- Suffixes are zero-padded: three digits for techniques, detections, mitigations,
  and assessment items; two for tactics and data sources.
- Every identified object carries `status` (draft, experimental, stable, deprecated),
  `version`, `added` (the framework version it first appeared in), `modified`, and an
  optional `deprecated` block with `superseded_by` and `reason`. Alpha content is
  `experimental`; the provisional tactics are `draft`.

## Cross-references the build enforces

The build fails, with a per-object message and a non-zero exit, on any of these:

- a technique naming a tactic that does not exist;
- a technique naming a data source that does not exist;
- a detection naming a technique or data source that does not exist;
- a mitigation naming a technique that does not exist;
- a mapping whose subject is not an existing technique or mitigation;
- an assessment item probing a technique or mitigation that does not exist;
- a `superseded_by` that does not resolve to an object of the same type;
- a duplicate identifier within a type;
- a duplicate mapping relation;
- any object that fails its schema, including an unknown field.

Malformed source (a non-string id, a non-list reference field) produces a clean
error, not a stack trace.

## Build pipeline

1. Load every source file per type (`data/<type>/`), plus the mapping relation lists.
2. Validate each object against its JSON Schema.
3. Resolve every cross-reference against the loaded graph.
4. On a clean build only, emit `phlipped.json` and the per-type files under `dist/`.

`phlipped.json` is shaped:

```
{
  "framework_version": "0.1.0",
  "generated": "<ISO-8601 UTC>",
  "tactics": [...], "techniques": [...], "data_sources": [...],
  "detections": [...], "mitigations": [...], "assessment": [...],
  "mappings": [...], "mappings_matrix": { "<subject>": { "<framework>": [ids] } }
}
```

The site and the assessment tool read this artifact. See [building](building.md) for
how to run the build and add an object.
