#!/usr/bin/env python3
"""Build catalog.json from threats/*.md frontmatter."""
import json
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("install pyyaml: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

ROOT = Path(__file__).parent
THREATS = ROOT / "threats"
OUT = ROOT / "catalog.json"

FM = re.compile(r"^---\n(.*?)\n---", re.DOTALL)


def main() -> None:
    entries = []
    for md in sorted(THREATS.glob("PHL-T-*.md")):
        m = FM.match(md.read_text(encoding="utf-8"))
        if not m:
            print(f"skip {md.name}: no frontmatter", file=sys.stderr)
            continue
        entries.append(yaml.safe_load(m.group(1)))
    OUT.write_text(json.dumps({"version": "0.1.0", "threats": entries}, indent=2) + "\n")
    print(f"wrote {OUT} ({len(entries)} entries)")


if __name__ == "__main__":
    main()
