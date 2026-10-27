import gen_pages as g

T = {"id": "PHL-T-003", "name": "MIFARE cloning", "category": "rfid-nfc", "severity": 8.0,
     "prerequisites": {"physical_access": "proximity", "time_seconds": 30,
                       "hardware": ["Flipper Zero"], "skill_level": 2},
     "tactics": ["PHL-TA-01", "PHL-TA-02"], "body": "## Attack chain\nbody text"}
MATRIX = {"PHL-T-003": {"attack": ["T1556"], "d3fend": ["D3-X"]}}
TACTICS = [{"id": "PHL-TA-01", "name": "Approach", "order": 1},
           {"id": "PHL-TA-02", "name": "Capture", "order": 2}]


def test_technique_page_uses_matrix_not_inline_refs():
    md = g.technique_page(T, MATRIX)
    assert "PHL-T-003" in md and "8.0 / 10" in md and "T1556" in md and "D3-X" in md
    assert "mitre_attack" not in md
    assert "## Attack chain" in md and "body text" in md


def test_technique_page_frontmatter_and_table():
    md = g.technique_page(T, MATRIX)
    assert md.startswith("---\ntags:\n  - rfid-nfc\n---\n")
    assert "| Category | rfid-nfc |" in md


def test_technique_page_omits_absent_optional_fields():
    md = g.technique_page({**T, "data_sources": [], "observables": [], "known_tools": []}, {})
    assert "None" not in md
    for heading in ("Data sources", "Observables", "Known tools", "ATT&CK", "D3FEND"):
        assert heading not in md


def test_technique_page_renders_optional_fields_when_present():
    md = g.technique_page({**T, "data_sources": ["PHL-DS-01"], "observables": ["dup UID"],
                           "known_tools": ["Proxmark3"]}, MATRIX)
    assert "PHL-DS-01" in md and "dup UID" in md and "Proxmark3" in md


def test_technique_page_drops_duplicate_leading_h1():
    md = g.technique_page({**T, "body": "\n# MIFARE cloning\n\ntext"}, {})
    assert md.count("\n# ") == 1
    assert "text" in md


def test_matrix_places_multi_tactic_technique_in_each_column():
    md = g.matrix_table(TACTICS, [T])
    # the link target appears once per placement, so two means two columns
    assert md.count("(techniques/PHL-T-003.md)") == 2
    assert md.index("Approach") < md.index("Capture")


def test_matrix_orders_columns_by_order_field():
    md = g.matrix_table(list(reversed(TACTICS)), [T])
    assert md.index("Approach") < md.index("Capture")


def test_detection_page_renders_logic_in_yaml_fence():
    d = {"id": "PHL-D-002", "name": "x", "techniques": ["PHL-T-002"], "data_sources": ["PHL-DS-07"],
         "platform": "sigma", "logic": "level: high\n", "false_positives": ["admin bursts"]}
    md = g.detection_page(d)
    assert "```yaml\nlevel: high\n```" in md
    assert "PHL-T-002" in md and "PHL-DS-07" in md and "admin bursts" in md


def test_detection_page_without_false_positives():
    d = {"id": "PHL-D-002", "name": "x", "techniques": ["PHL-T-002"], "data_sources": [],
         "platform": "sigma", "logic": "level: high"}
    md = g.detection_page(d)
    assert "None" not in md and "False positives" not in md


def test_mitigation_page_without_cost_renders_clean():
    m = {"id": "PHL-M-006", "name": "x", "phase": "prevent", "techniques": ["PHL-T-003"],
         "description": "d"}
    md = g.mitigation_page(m)
    assert "None" not in md and "cost" not in md.lower() and "effort" not in md.lower()


def test_mitigation_page_with_cost_and_effort():
    m = {"id": "PHL-M-001", "name": "x", "phase": "prevent", "techniques": ["PHL-T-003"],
         "description": "d", "cost_eur": 5000, "effort_hours": 80}
    md = g.mitigation_page(m)
    assert "5000" in md and "80" in md


def test_mappings_table_rows_and_frameworks():
    md = g.mappings_table({"PHL-T-003": {"attack": ["T1556", "T1078"], "d3fend": ["D3-X"]},
                           "PHL-T-001": {"attack": ["T1200"]}})
    lines = md.splitlines()
    assert lines[0].startswith("| Technique")
    assert md.index("PHL-T-001") < md.index("PHL-T-003")
    assert "T1556, T1078" in md and "None" not in md


def test_catalog_index_lists_every_technique():
    md = g.catalog_index([T, {**T, "id": "PHL-T-001", "name": "HID"}])
    assert "PHL-T-001" in md and "PHL-T-003" in md and "PHL-T-003.md" in md
