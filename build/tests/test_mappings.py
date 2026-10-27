import json

from build.build import ROOT, build, build_matrix, load_mappings, resolve_refs, validate_mappings

FRAMEWORKS = {"attack", "d3fend", "nist-csf", "iso27001", "nis2", "cis"}


def _row(**kw):
    return {"subject_id": "PHL-T-001", "framework": "attack", "external_id": "T1200", **kw}


def test_mapping_subject_must_resolve():
    graph = {"technique": [{"id": "PHL-T-001"}], "mitigation": [],
             "mappings": [{"subject_id": "PHL-T-999", "framework": "attack", "external_id": "T1200"}]}
    errs = resolve_refs(graph)
    assert len(errs) == 1 and "PHL-T-999" in errs[0]


def test_mapping_subject_may_be_a_mitigation():
    graph = {"technique": [{"id": "PHL-T-001"}], "mitigation": [{"id": "PHL-M-001"}],
             "mappings": [{"subject_id": "PHL-M-001", "framework": "nis2", "external_id": "21(2)(d)"}]}
    assert resolve_refs(graph) == []


def test_malformed_mapping_subject_does_not_crash_or_add_noise():
    # the schema reports these shapes; the ref rule must neither raise nor pile on
    base = {"technique": [{"id": "PHL-T-001"}], "mitigation": []}
    for bad in (None, 7, ["PHL-T-001"], {"a": 1}):
        graph = {**base, "mappings": [{"subject_id": bad, "framework": "attack", "external_id": "T1200"}]}
        assert resolve_refs(graph) == []
    assert resolve_refs({**base, "mappings": [None, "x", 3]}) == []


def test_matrix_has_a_row_per_subject():
    graph, errs = build()
    assert errs == []
    matrix = build_matrix(graph)
    assert "PHL-T-003" in matrix and "attack" in matrix["PHL-T-003"]
    assert matrix["PHL-T-003"]["attack"] == ["T1556", "T1078"]
    assert matrix["PHL-T-003"]["d3fend"] == ["D3-HBPI"]


def test_matrix_groups_by_subject_then_framework():
    graph = {"mappings": [
        {"subject_id": "PHL-T-001", "framework": "attack", "external_id": "T1200"},
        {"subject_id": "PHL-T-001", "framework": "attack", "external_id": "T1078"},
        {"subject_id": "PHL-T-001", "framework": "d3fend", "external_id": "D3-HBPI"},
        {"subject_id": "PHL-M-002", "framework": "nis2", "external_id": "21"},
    ]}
    assert build_matrix(graph) == {
        "PHL-T-001": {"attack": ["T1200", "T1078"], "d3fend": ["D3-HBPI"]},
        "PHL-M-002": {"nis2": ["21"]},
    }


def test_real_data_has_expected_relation_counts():
    graph, _ = build()
    by_fw = {}
    for m in graph["mappings"]:
        by_fw[m["framework"]] = by_fw.get(m["framework"], 0) + 1
    assert by_fw == {"attack": 21, "d3fend": 8}
    keys = [(m["subject_id"], m["framework"], m["external_id"]) for m in graph["mappings"]]
    assert len(keys) == len(set(keys))


def test_relations_carry_no_id_or_lifecycle():
    graph, _ = build()
    for m in graph["mappings"]:
        assert not {"id", "status", "version", "added", "modified"} & set(m)


def test_techniques_no_longer_carry_inline_mitre_refs():
    graph, _ = build()
    for t in graph["technique"]:
        assert "mitre_attack" not in t and "mitre_d3fend" not in t
    props = json.loads((ROOT / "schema/technique.schema.json").read_text())["properties"]
    assert "mitre_attack" not in props and "mitre_d3fend" not in props


def test_mapping_schema_framework_enum_is_exactly_the_six():
    schema = json.loads((ROOT / "schema/mapping.schema.json").read_text())
    assert set(schema["properties"]["framework"]["enum"]) == FRAMEWORKS


def test_mapping_schema_rejects_bad_relations():
    bad = [
        _row(framework="soc2"),
        _row(subject_id="PHL-D-001"),
        _row(subject_id="PHL-T-1"),
        _row(external_id=""),
        _row(external_id=7),
        _row(status="stable"),
        {"subject_id": "PHL-T-001", "framework": "attack"},
    ]
    for row in bad:
        assert validate_mappings([row], "x.yml"), row
    assert validate_mappings([_row(note="why"), _row(subject_id="PHL-M-001", framework="cis", external_id="1.1")], "x.yml") == []


def test_mapping_file_must_be_a_list():
    assert any("list" in e for e in validate_mappings({"subject_id": "PHL-T-001"}, "x.yml"))
    assert any("list" in e for e in validate_mappings(None, "x.yml"))
    assert any("not a mapping" in e or "object" in e for e in validate_mappings(["PHL-T-001"], "x.yml"))


def test_load_mappings_flattens_every_file():
    rows, errs = load_mappings()
    assert errs == []
    assert len(rows) == 29
