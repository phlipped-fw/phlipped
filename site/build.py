#!/usr/bin/env python3
"""Build the PHLIPPED static site into site/public/.

Sources:
  catalog/threats/*.md   threat frontmatter + body  -> index + per-threat pages
  docs/worked-thread.md, docs/about.md               -> narrative pages
  site/static/*                                       -> public/assets/
"""
from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path

import markdown
import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape

SITE = Path(__file__).parent
REPO = SITE.parent
THREATS = REPO / "catalog" / "threats"
DOCS = REPO / "docs"
PUBLIC = SITE / "public"

FM = re.compile(r"^---\n(.*?)\n---\n?(.*)$", re.DOTALL)

env = Environment(
    loader=FileSystemLoader(str(SITE / "templates")),
    autoescape=select_autoescape(["html"]),
)


def md_to_html(text: str) -> str:
    return markdown.markdown(text, extensions=["fenced_code", "tables", "sane_lists"])


def load_threats() -> list[dict]:
    threats = []
    for path in sorted(THREATS.glob("PHL-T-*.md")):
        m = FM.match(path.read_text(encoding="utf-8"))
        if not m:
            raise SystemExit(f"error: {path.name} has no frontmatter")
        meta = yaml.safe_load(m.group(1))
        meta["_body_html"] = md_to_html(m.group(2).strip())
        threats.append(meta)
    return threats


def write(rel: str, html: str) -> None:
    out = PUBLIC / rel
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")


def build() -> None:
    if PUBLIC.exists():
        shutil.rmtree(PUBLIC)
    PUBLIC.mkdir(parents=True)

    threats = load_threats()
    categories = sorted({t["category"] for t in threats})

    write("index.html", env.get_template("index.html").render(
        root="", threats=threats, categories=categories))

    threat_tpl = env.get_template("threat.html")
    for t in threats:
        write(f"threats/{t['id']}.html", threat_tpl.render(
            root="../", t=t, body_html=t["_body_html"]))

    page_tpl = env.get_template("page.html")
    pages = {"worked-thread.html": ("Framework in action", "worked-thread.md"),
             "about.html": ("About", "about.md")}
    for out_name, (title, src) in pages.items():
        body = md_to_html((DOCS / src).read_text(encoding="utf-8"))
        write(out_name, page_tpl.render(root="", page_title=title, body_html=body))

    assets = PUBLIC / "assets"
    assets.mkdir(exist_ok=True)
    for static in (SITE / "static").iterdir():
        if static.is_file():
            shutil.copy2(static, assets / static.name)

    pages_count = 2 + len(threats) + 1
    print(f"built {pages_count} pages into {PUBLIC} ({len(threats)} threats)")


if __name__ == "__main__":
    build()
