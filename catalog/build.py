#!/usr/bin/env python3
"""Build catalog.json from threats/*.md frontmatter, validating each entry
against schema/threat.schema.json. Exits non-zero if any entry is invalid or
if an id is duplicated, so CI fails on bad catalog data."""
import json
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("install pyyaml: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

try:
    from jsonschema import Draft202012Validator
except ImportError:
    print("install jsonschema: pip install jsonschema", file=sys.stderr)
    sys.exit(1)

ROOT = Path(__file__).parent
THREATS = ROOT / "threats"
SCHEMA = ROOT / "schema" / "threat.schema.json"
OUT = ROOT / "catalog.json"

FM = re.compile(r"^---\n(.*?)\n---", re.DOTALL)


def load_entries() -> list[dict]:
    entries = []
    for md in sorted(THREATS.glob("PHL-T-*.md")):
        m = FM.match(md.read_text(encoding="utf-8"))
        if not m:
            raise SystemExit(f"error: {md.name} has no YAML frontmatter")
        entry = yaml.safe_load(m.group(1))
        entry["_source"] = md.name
        entries.append(entry)
    return entries


def validate(entries: list[dict]) -> list[str]:
    """Return a list of human-readable error strings; empty means valid."""
    validator = Draft202012Validator(json.loads(SCHEMA.read_text()))
    errors: list[str] = []
    seen: dict[str, str] = {}
    for entry in entries:
        src = entry.get("_source", entry.get("id", "?"))
        for err in validator.iter_errors({k: v for k, v in entry.items() if k != "_source"}):
            path = "/".join(str(p) for p in err.path) or "(root)"
            errors.append(f"{src}: {path}: {err.message}")
        eid = entry.get("id")
        if eid in seen:
            errors.append(f"{src}: duplicate id {eid} (also in {seen[eid]})")
        elif eid:
            seen[eid] = src
    return errors


def main() -> None:
    entries = load_entries()
    errors = validate(entries)
    if errors:
        print(f"catalog validation failed ({len(errors)} error(s)):", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        raise SystemExit(1)
    clean = [{k: v for k, v in e.items() if k != "_source"} for e in entries]
    OUT.write_text(json.dumps({"version": "0.1.0", "threats": clean}, indent=2) + "\n")
    print(f"wrote {OUT} ({len(clean)} entries, all valid)")


if __name__ == "__main__":
    main()
