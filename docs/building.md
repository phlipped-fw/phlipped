# Building and contributing

How to build the framework, what the build checks, how to add an object, and how CI
gates changes. Written so someone who has never seen the repository can get from a
clean checkout to a validated build.

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
```

`requirements-dev.txt` installs the build and site dependencies and the assessment
tool in editable mode (`-e ./tools/assess`).

## Build

```bash
python -m build.build
```

This validates every object against its schema, resolves every cross-reference, and,
on a clean build, writes `phlipped.json` and the per-type files under `dist/`. It
prints the object counts on success and exits non-zero with per-object messages on
any failure. Nothing is written on a failed build.

Run from the repository root. The build is the gate: if it fails, nothing downstream
should proceed.

## Test

```bash
pytest build/tests tools/assess -q
```

`build/tests` covers the build: loading, schema validation, every cross-reference
rule, the duplicate and malformed-input checks, and the artifact emission.
`tools/assess/tests` covers the assessment tool end to end against a freshly built
artifact.

## Run an assessment

The assessment tool reads the built `phlipped.json`:

```bash
python -m build.build                                  # produce phlipped.json
phlipped-assess run --data phlipped.json --out assessment.json
phlipped-assess report --in assessment.json --out report.html
phlipped-assess list-items --data phlipped.json
```

The score is derived from the object graph: each assessment item probes specific
techniques or mitigations by id.

## Adding an object

Source lives under `data/<type>/`, one file per object. The identified types
(tactic, technique, data source, detection, mitigation, assessment) are one object
per file; mappings are lists grouped by framework under `data/mappings/`.

1. Create the source file with the fields its type requires (see
   [data-model](data-model.md)). Give it a new, unused identifier following the
   type's pattern, and the lifecycle fields (`status: experimental`, `version`,
   `added`, `modified`).
2. Point its cross-references at identifiers that already exist. A technique needs at
   least one tactic. A detection needs at least one technique and one data source.
3. Run `python -m build.build`. Fix any error it reports. Unknown fields are rejected,
   so a typo in a field name fails the build rather than being ignored.
4. Run the tests.

Techniques are Markdown with YAML frontmatter; the body below the frontmatter is the
write-up. Every other type is YAML.

Do not reuse an identifier. To retire an object, mark it `deprecated` with a
`superseded_by`; do not delete it.

## Continuous integration

CI runs on every push and pull request:

1. install dependencies;
2. `python -m build.build` (schema, cross-references, duplicates, rule integrity);
3. `pytest build/tests tools/assess site/tests -q`;
4. `mkdocs build --strict -f site/mkdocs.yml`, the strict site build.

A green build gates deploy.
