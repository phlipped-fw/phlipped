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
}

FRONTMATTER = re.compile(r"\A---\n(.*?)\n---[ \t]*\n?(.*)\Z", re.DOTALL)


class _Loader(yaml.SafeLoader):
    """SafeLoader that leaves ISO dates as strings, so they validate as text."""


_Loader.yaml_implicit_resolvers = {
    ch: [(tag, rx) for tag, rx in resolvers if tag != "tag:yaml.org,2002:timestamp"]
    for ch, resolvers in yaml.SafeLoader.yaml_implicit_resolvers.items()
}


def _parse(path: Path, fmt: str) -> dict:
    text = path.read_text(encoding="utf-8")
    if fmt == "frontmatter":
        m = FRONTMATTER.match(text)
        if not m:
            raise ValueError(f"{path.name}: no YAML frontmatter")
        obj = yaml.load(m.group(1), Loader=_Loader)
        obj["body"] = m.group(2)
        return obj
    if fmt == "yaml":
        return yaml.load(text, Loader=_Loader)
    raise ValueError(f"unknown format {fmt!r}")


def load_objects(obj_type: str) -> list[dict]:
    cfg = OBJECT_TYPES[obj_type]
    ext = "*.md" if cfg["format"] == "frontmatter" else "*.yml"
    objects = []
    for path in sorted((ROOT / cfg["dir"]).glob(ext)):
        obj = _parse(path, cfg["format"])
        obj["_source"] = path.name
        objects.append(obj)
    return objects


def validate_schema(objects: list[dict], schema_path: str) -> list[str]:
    schema = json.loads((ROOT / schema_path).read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    errors: list[str] = []
    for obj in objects:
        label = obj.get("_source", obj.get("id", "?"))
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
        target = (obj.get("deprecated") or {}).get("superseded_by")
        if target and target not in ids:
            errors.append(f"{obj.get('id')}: superseded_by {target} does not exist")
    return errors


def build() -> tuple[dict, list[str]]:
    graph: dict[str, list[dict]] = {}
    errors: list[str] = []
    for obj_type, cfg in OBJECT_TYPES.items():
        objects = load_objects(obj_type)
        errors += validate_schema(objects, cfg["schema"])
        errors += check_duplicate_ids(objects)
        errors += check_superseded(objects)
        graph[obj_type] = [{k: v for k, v in o.items() if k != "_source"} for o in objects]
    return graph, errors


def main() -> None:
    graph, errors = build()
    if errors:
        print(f"build failed ({len(errors)} error(s)):", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        raise SystemExit(1)
    counts = ", ".join(f"{len(v)} {k}" for k, v in graph.items())
    print(f"build ok ({counts})")


if __name__ == "__main__":
    main()
