#!/usr/bin/env python3
"""Check that every internal link and asset reference in the built site resolves
to a file that exists. External (http/https/mailto) links and pure #anchors are
skipped. Exits non-zero if any internal link is broken."""
from __future__ import annotations

import re
import sys
from pathlib import Path

PUBLIC = Path(__file__).parent / "public"
REF = re.compile(r'(?:href|src)\s*=\s*"([^"]+)"')


def main() -> None:
    if not PUBLIC.exists():
        raise SystemExit("error: site/public not built; run site/build.py first")

    broken: list[str] = []
    for html in sorted(PUBLIC.rglob("*.html")):
        for raw in REF.findall(html.read_text(encoding="utf-8")):
            link = raw.split("#", 1)[0]
            if not link or link.startswith(("http://", "https://", "mailto:", "//")):
                continue
            target = (html.parent / link).resolve()
            try:
                target.relative_to(PUBLIC.resolve())
            except ValueError:
                broken.append(f"{html.relative_to(PUBLIC)} -> {raw} (escapes site root)")
                continue
            if not target.exists():
                broken.append(f"{html.relative_to(PUBLIC)} -> {raw}")

    if broken:
        print(f"link check failed ({len(broken)} broken):", file=sys.stderr)
        for b in broken:
            print(f"  - {b}", file=sys.stderr)
        raise SystemExit(1)
    print("link check ok (no broken internal links)")


if __name__ == "__main__":
    main()
