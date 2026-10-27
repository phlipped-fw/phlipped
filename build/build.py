#!/usr/bin/env python3
"""Load per-object source files under data/, validate each against its JSON
Schema, run cross-object integrity checks, and assemble one object graph.
Exits non-zero if anything is invalid so CI fails on bad data."""
import json
import re
import sys
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parent.parent

OBJECT_TYPES: dict[str, dict] = {
    "technique": {
        "dir": "data/techniques",
        "schema": "schema/technique.schema.json",
        "id_pattern": r"^PHL-T-[0-9]{3}$",
        "format": "frontmatter",
    },
    "tactic": {
        "dir": "data/tactics",
        "schema": "schema/tactic.schema.json",
        "id_pattern": r"^PHL-TA-\d{2}$",
        "format": "yaml",
    },
    "data_source": {
        "dir": "data/data_sources",
        "schema": "schema/data_source.schema.json",
        "id_pattern": r"^PHL-DS-\d{2}$",
        "format": "yaml",
    },
    "detection": {
        "dir": "data/detections",
        "schema": "schema/detection.schema.json",
        "id_pattern": r"^PHL-D-\d{3}$",
        "format": "yaml",
    },
    "mitigation": {
        "dir": "data/mitigations",
        "schema": "schema/mitigation.schema.json",
        "id_pattern": r"^PHL-M-\d{3}$",
        "format": "yaml",
    },
    "assessment": {
        "dir": "data/assessment",
        "schema": "schema/assessment.schema.json",
        "id_pattern": r"^PSPS-\d{3}$",
        "format": "yaml",
    },
}

MAPPINGS_DIR = "data/mappings"
MAPPING_SCHEMA = "schema/mapping.schema.json"
ARTIFACT = "phlipped.json"

FRONTMATTER = re.compile(r"\A---\n(.*?)\n---[ \t]*\n?(.*)\Z", re.DOTALL)


class _Loader(yaml.SafeLoader):
    """SafeLoader that leaves ISO dates as strings, so they validate as text."""


_Loader.yaml_implicit_resolvers = {
    ch: [(tag, rx) for tag, rx in resolvers if tag != "tag:yaml.org,2002:timestamp"]
    for ch, resolvers in yaml.SafeLoader.yaml_implicit_resolvers.items()
}


def _parse(path: Path, fmt: str) -> dict:
    """Parse one source file. Malformed input yields a stub carrying
    `_parse_error`, which validate_schema reports, so bad data never
    surfaces as a traceback."""
    text = path.read_text(encoding="utf-8")
    body = None
    if fmt == "frontmatter":
        m = FRONTMATTER.match(text)
        if not m:
            return {"_parse_error": "no YAML frontmatter"}
        text, body = m.group(1), m.group(2)
    elif fmt != "yaml":
        raise ValueError(f"unknown format {fmt!r}")
    try:
        obj = yaml.load(text, Loader=_Loader)
    except yaml.YAMLError as exc:
        return {"_parse_error": f"invalid YAML: {exc}"}
    if not isinstance(obj, dict):
        return {"_parse_error": "frontmatter is empty or not a mapping"}
    if body is not None:
        obj["body"] = body
    return obj


def load_objects(obj_type: str) -> list[dict]:
    cfg = OBJECT_TYPES[obj_type]
    ext = "*.md" if cfg["format"] == "frontmatter" else "*.yml"
    objects = []
    for path in sorted((ROOT / cfg["dir"]).glob(ext)):
        obj = _parse(path, cfg["format"])
        obj["_source"] = path.name
        objects.append(obj)
    return objects


def validate_mappings(rows, label: str) -> list[str]:
    """Validate one mapping file (a list of relations) against the mapping
    schema. Malformed shapes become errors, never tracebacks."""
    if not isinstance(rows, list):
        return [f"{label}: mapping file must be a list of relations"]
    schema = json.loads((ROOT / MAPPING_SCHEMA).read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    errors: list[str] = []
    for i, row in enumerate(rows):
        if not isinstance(row, dict):
            errors.append(f"{label}[{i}]: relation is not a mapping")
            continue
        for err in validator.iter_errors(row):
            path = "/".join(str(p) for p in err.path) or "(root)"
            errors.append(f"{label}[{i}]: {path}: {err.message}")
    return errors


def load_mappings() -> tuple[list, list[str]]:
    """Read every data/mappings/*.yml (each a list of relations), validate it,
    and flatten into one list. Relations are edges, so they load separately
    from OBJECT_TYPES."""
    rows: list = []
    errors: list[str] = []
    for path in sorted((ROOT / MAPPINGS_DIR).glob("*.yml")):
        try:
            data = yaml.load(path.read_text(encoding="utf-8"), Loader=_Loader)
        except yaml.YAMLError as exc:
            errors.append(f"{path.name}: invalid YAML: {exc}")
            continue
        errors += validate_mappings(data, path.name)
        if isinstance(data, list):
            rows += data
    return rows, errors


def validate_schema(objects: list[dict], schema_path: str) -> list[str]:
    schema = json.loads((ROOT / schema_path).read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    errors: list[str] = []
    for obj in objects:
        label = obj.get("_source", obj.get("id", "?"))
        if "_parse_error" in obj:
            errors.append(f"{label}: {obj['_parse_error']}")
            continue
        data = {k: v for k, v in obj.items() if k not in ("_source", "body")}
        for err in validator.iter_errors(data):
            path = "/".join(str(p) for p in err.path) or "(root)"
            errors.append(f"{label}: {path}: {err.message}")
    return errors


def check_duplicate_ids(objects: list[dict]) -> list[str]:
    errors: list[str] = []
    seen: set[str] = set()
    for obj in objects:
        oid = obj.get("id")
        if oid in seen:
            errors.append(f"duplicate id {oid}")
        elif oid:
            seen.add(oid)
    return errors


def check_superseded(objects: list[dict]) -> list[str]:
    ids = {o.get("id") for o in objects}
    errors: list[str] = []
    for obj in objects:
        deprecated = obj.get("deprecated")
        if deprecated is None:
            continue
        if not isinstance(deprecated, dict):
            errors.append(f"{obj.get('id')}: deprecated must be a mapping")
            continue
        target = deprecated.get("superseded_by")
        if target and target not in ids:
            errors.append(f"{obj.get('id')}: superseded_by {target} does not exist")
    return errors


def _ids(graph: dict, obj_type: str) -> set[str]:
    """Loaded ids of one type; non-string ids (malformed data) are ignored."""
    return {o["id"] for o in graph.get(obj_type, []) if isinstance(o.get("id"), str)}


def _dangling_refs(obj: dict, field: str, valid_ids: set[str], target: str) -> list[str]:
    """One error per entry of obj[field] that is not in valid_ids. Malformed
    shapes (field not a list, entry not a string) are skipped: the schema
    already reports them, so a ref rule must neither raise nor add noise."""
    refs = obj.get(field)
    if not isinstance(refs, list):
        return []
    return [
        f"{obj.get('id')}: {field}: {ref} does not resolve to a loaded {target}"
        for ref in refs
        if isinstance(ref, str) and ref not in valid_ids
    ]


def _resolve_technique_tactics(graph: dict) -> list[str]:
    """Every technique's tactics[] must resolve to a loaded tactic id."""
    tactic_ids = _ids(graph, "tactic")
    errors: list[str] = []
    for obj in graph.get("technique", []):
        errors += _dangling_refs(obj, "tactics", tactic_ids, "tactic")
    return errors


def _resolve_technique_data_sources(graph: dict) -> list[str]:
    """Every technique's data_sources[] (optional) must resolve to a loaded data source id."""
    ds_ids = _ids(graph, "data_source")
    errors: list[str] = []
    for obj in graph.get("technique", []):
        errors += _dangling_refs(obj, "data_sources", ds_ids, "data source")
    return errors


def _resolve_detection_techniques(graph: dict) -> list[str]:
    """Every detection's techniques[] must resolve to a loaded technique id."""
    technique_ids = _ids(graph, "technique")
    errors: list[str] = []
    for obj in graph.get("detection", []):
        errors += _dangling_refs(obj, "techniques", technique_ids, "technique")
    return errors


def _resolve_detection_data_sources(graph: dict) -> list[str]:
    """Every detection's data_sources[] must resolve to a loaded data source id."""
    ds_ids = _ids(graph, "data_source")
    errors: list[str] = []
    for obj in graph.get("detection", []):
        errors += _dangling_refs(obj, "data_sources", ds_ids, "data source")
    return errors


def _resolve_mitigation_techniques(graph: dict) -> list[str]:
    """Every mitigation's techniques[] must resolve to a loaded technique id."""
    technique_ids = _ids(graph, "technique")
    errors: list[str] = []
    for obj in graph.get("mitigation", []):
        errors += _dangling_refs(obj, "techniques", technique_ids, "technique")
    return errors


def _resolve_mapping_subjects(graph: dict) -> list[str]:
    """Every mapping's subject_id (a scalar) must resolve to a loaded technique
    or mitigation id. Non-dict rows and non-string subjects are skipped: the
    schema already reports them."""
    subject_ids = _ids(graph, "technique") | _ids(graph, "mitigation")
    errors: list[str] = []
    for row in graph.get("mappings", []):
        if not isinstance(row, dict):
            continue
        subject = row.get("subject_id")
        if isinstance(subject, str) and subject not in subject_ids:
            errors.append(
                f"mapping {row.get('framework')} {row.get('external_id')}: "
                f"subject_id {subject} does not resolve to a loaded technique or mitigation"
            )
    return errors


def _resolve_assessment_probes(graph: dict) -> list[str]:
    """Every assessment item's probes[] must resolve to a loaded technique or mitigation id."""
    probe_ids = _ids(graph, "technique") | _ids(graph, "mitigation")
    errors: list[str] = []
    for obj in graph.get("assessment", []):
        errors += _dangling_refs(obj, "probes", probe_ids, "technique or mitigation")
    return errors


# One rule per cross-reference axis. Later tasks extend this list with a rule
# each (assessment -> probe) rather than modifying resolve_refs.
_REF_RULES = [
    _resolve_technique_tactics,
    _resolve_technique_data_sources,
    _resolve_detection_techniques,
    _resolve_detection_data_sources,
    _resolve_mitigation_techniques,
    _resolve_mapping_subjects,
    _resolve_assessment_probes,
]


def resolve_refs(graph: dict) -> list[str]:
    errors: list[str] = []
    for rule in _REF_RULES:
        errors += rule(graph)
    return errors


def build_matrix(graph: dict) -> dict:
    """Compliance matrix: subject_id -> {framework: [external_id, ...]}, in
    file order. Malformed rows are skipped (the schema reports them)."""
    matrix: dict[str, dict[str, list[str]]] = {}
    for row in graph.get("mappings", []):
        if not isinstance(row, dict):
            continue
        subject, fw, ext = row.get("subject_id"), row.get("framework"), row.get("external_id")
        if not all(isinstance(v, str) for v in (subject, fw, ext)):
            continue
        matrix.setdefault(subject, {}).setdefault(fw, []).append(ext)
    return matrix


def build() -> tuple[dict, list[str]]:
    graph: dict[str, list[dict]] = {}
    errors: list[str] = []
    for obj_type, cfg in OBJECT_TYPES.items():
        objects = load_objects(obj_type)
        errors += validate_schema(objects, cfg["schema"])
        errors += check_duplicate_ids(objects)
        errors += check_superseded(objects)
        graph[obj_type] = [{k: v for k, v in o.items() if k != "_source"} for o in objects]
    graph["mappings"], mapping_errors = load_mappings()
    errors += mapping_errors
    errors += resolve_refs(graph)
    return graph, errors


def main() -> None:
    graph, errors = build()
    if errors:
        print(f"build failed ({len(errors)} error(s)):", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        raise SystemExit(1)
    artifact = dict(graph, mappings_matrix=build_matrix(graph))
    (ROOT / ARTIFACT).write_text(
        json.dumps(artifact, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    counts = ", ".join(f"{len(v)} {k}" for k, v in graph.items())
    print(f"build ok ({counts})")


if __name__ == "__main__":
    main()
