"""Build-time page generation for the PHLIPPED site.

Reads phlipped.json from the repo root and writes per-object pages, the tactic
matrix and the mappings table into the virtual docs tree via mkdocs-gen-files.
The builders are pure functions returning markdown so they can be tested without
MkDocs.
"""
import json
import pathlib

FRAMEWORK_LABELS = {"attack": "ATT&CK", "d3fend": "D3FEND"}


def _present(value):
    """True when an optional field carries something worth rendering."""
    return value not in (None, "", [], {})


def _cell(text):
    return str(text).replace("|", "\\|").replace("\n", " ")


def _bullets(items):
    return "\n".join(f"- {item}" for item in items)


def _tech_link(tid, prefix=""):
    return f"[{tid}]({prefix}techniques/{tid}.md)"


def _strip_leading_h1(body):
    lines = body.strip("\n").splitlines()
    if lines and lines[0].startswith("# "):
        return "\n".join(lines[1:]).strip("\n")
    return "\n".join(lines)


def technique_page(t, matrix):
    prereq = t.get("prerequisites", {})
    rows = [("Category", t.get("category")),
            ("Severity", f"{t['severity']:.1f} / 10" if t.get("severity") is not None else None),
            ("Physical access", prereq.get("physical_access")),
            ("Time", f"{prereq['time_seconds']} s" if prereq.get("time_seconds") is not None else None),
            ("Skill level", prereq.get("skill_level")),
            ("Hardware", ", ".join(prereq["hardware"]) if _present(prereq.get("hardware")) else None)]
    out = []
    if _present(t.get("category")):
        out += ["---", "tags:", f"  - {t['category']}", "---", ""]
    out += [f"# {t['id']}: {t['name']}", "", "| Field | Value |", "|---|---|"]
    out += [f"| {k} | {_cell(v)} |" for k, v in rows if _present(v)]
    refs = matrix.get(t["id"], {})
    for fw in sorted(refs):
        if _present(refs[fw]):
            out += ["", f"**{FRAMEWORK_LABELS.get(fw, fw)}:** {', '.join(refs[fw])}"]
    for key, title in (("data_sources", "Data sources"), ("observables", "Observables"),
                       ("known_tools", "Known tools")):
        if _present(t.get(key)):
            out += ["", f"## {title}", "", _bullets(t[key])]
    body = _strip_leading_h1(t.get("body") or "")
    if body:
        out += ["", body]
    return "\n".join(out) + "\n"


def detection_page(d):
    out = [f"# {d['id']}: {d['name']}", "", "| Field | Value |", "|---|---|"]
    if _present(d.get("platform")):
        out.append(f"| Platform | {_cell(d['platform'])} |")
    if _present(d.get("techniques")):
        out.append("| Techniques | " + ", ".join(_tech_link(x, "../") for x in d["techniques"]) + " |")
    if _present(d.get("data_sources")):
        out.append("| Data sources | " + ", ".join(d["data_sources"]) + " |")
    if _present(d.get("logic")):
        out += ["", "## Rule", "", "```yaml", d["logic"].rstrip("\n"), "```"]
    if _present(d.get("false_positives")):
        out += ["", "## False positives", "", _bullets(d["false_positives"])]
    return "\n".join(out) + "\n"


def mitigation_page(m):
    out = [f"# {m['id']}: {m['name']}", "", "| Field | Value |", "|---|---|"]
    if _present(m.get("phase")):
        out.append(f"| Phase | {_cell(m['phase'])} |")
    if _present(m.get("techniques")):
        out.append("| Techniques | " + ", ".join(_tech_link(x, "../") for x in m["techniques"]) + " |")
    if m.get("cost_eur") is not None:
        out.append(f"| Cost | {m['cost_eur']} EUR |")
    if m.get("effort_hours") is not None:
        out.append(f"| Effort | {m['effort_hours']} hours |")
    if _present(m.get("description")):
        out += ["", m["description"]]
    return "\n".join(out) + "\n"


def matrix_table(tactics, techniques):
    cols = sorted(tactics, key=lambda x: x["order"])
    per_col = [[t for t in techniques if c["id"] in t.get("tactics", [])] for c in cols]
    height = max((len(c) for c in per_col), default=0)
    out = ["| " + " | ".join(_cell(c["name"]) for c in cols) + " |",
           "|" + "---|" * len(cols)]
    for i in range(height):
        cells = [f"{_tech_link(c[i]['id'])} {_cell(c[i]['name'])}" if i < len(c) else ""
                 for c in per_col]
        out.append("| " + " | ".join(cells) + " |")
    return "\n".join(out) + "\n"


def mappings_table(matrix):
    frameworks = sorted({fw for refs in matrix.values() for fw in refs})
    labels = [FRAMEWORK_LABELS.get(fw, fw) for fw in frameworks]
    out = ["| Technique | " + " | ".join(labels) + " |", "|---|" + "---|" * len(frameworks)]
    for tid in sorted(matrix):
        cells = [", ".join(matrix[tid].get(fw, [])) for fw in frameworks]
        out.append(f"| {_tech_link(tid)} | " + " | ".join(cells) + " |")
    return "\n".join(out) + "\n"


def _index(title, intro, items):
    out = [f"# {title}", "", intro, "", "| ID | Name |", "|---|---|"]
    out += [f"| [{i['id']}]({i['id']}.md) | {_cell(i['name'])} |" for i in items]
    return "\n".join(out) + "\n"


def catalog_index(techniques):
    return _index("Technique catalog", "Every catalogued technique, by identifier.",
                  sorted(techniques, key=lambda x: x["id"]))


def detection_index(detections):
    return _index("Detections", "Detection rules and the techniques they cover.",
                  sorted(detections, key=lambda x: x["id"]))


def mitigation_index(mitigations):
    return _index("Mitigations", "Countermeasures and the techniques they address.",
                  sorted(mitigations, key=lambda x: x["id"]))


def main():
    import mkdocs_gen_files

    root = pathlib.Path(__file__).resolve().parents[2]
    data = json.loads((root / "phlipped.json").read_text(encoding="utf-8"))
    matrix = data["mappings_matrix"]

    def write(path, text, source):
        with mkdocs_gen_files.open(path, "w") as f:
            f.write(text)
        mkdocs_gen_files.set_edit_path(path, source)

    sections = (
        ("techniques", data["techniques"], lambda x: technique_page(x, matrix), "md", catalog_index),
        ("detections", data["detections"], detection_page, "yml", detection_index),
        ("mitigations", data["mitigations"], mitigation_page, "yml", mitigation_index),
    )
    for section, items, builder, ext, indexer in sections:
        nav = mkdocs_gen_files.Nav()
        nav["Overview"] = "index.md"
        for item in sorted(items, key=lambda x: x["id"]):
            write(f"{section}/{item['id']}.md", builder(item), f"data/{section}/{item['id']}.{ext}")
            nav[f"{item['id']}: {item['name']}"] = f"{item['id']}.md"
        write(f"{section}/index.md", indexer(items), f"data/{section}")
        with mkdocs_gen_files.open(f"{section}/SUMMARY.md", "w") as f:
            f.writelines(nav.build_literate_nav())

    write("matrix.md", "# Tactic matrix\n\nTechniques placed under every tactic they serve.\n\n"
          + matrix_table(data["tactics"], data["techniques"]), "data/tactics")
    write("mappings.md", "# Mappings\n\nTechniques mapped to external frameworks.\n\n"
          + mappings_table(matrix), "data/mappings")


# mkdocs-gen-files executes this file with runpy.run_path, which names it "<run_path>".
# Importing it from tests (as gen_pages) must not trigger a build.
if __name__ == "<run_path>":
    main()
