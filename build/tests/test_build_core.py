from build.build import (
    check_duplicate_ids,
    check_superseded,
    load_objects,
    validate_schema,
)


def test_loads_ten_techniques():
    objs = load_objects("technique")
    assert len(objs) == 10
    assert {o["id"] for o in objs} >= {"PHL-T-001", "PHL-T-010"}


def test_duplicate_id_is_rejected():
    errs = check_duplicate_ids([{"id": "PHL-T-001"}, {"id": "PHL-T-001"}])
    assert any("PHL-T-001" in e for e in errs)


def test_valid_techniques_pass_schema():
    errs = validate_schema(load_objects("technique"), "schema/technique.schema.json")
    assert errs == []


def test_missing_superseded_target_is_rejected():
    errs = check_superseded([{"id": "PHL-T-009", "deprecated": {"superseded_by": "PHL-T-099"}}])
    assert any("PHL-T-099" in e for e in errs)


def test_schema_invalid_technique_is_rejected():
    tech = next(o for o in load_objects("technique") if o["id"] == "PHL-T-001")
    bad = {k: v for k, v in tech.items() if k != "version"}
    errs = validate_schema([bad], "schema/technique.schema.json")
    assert any("version" in e for e in errs)


def test_draft_status_is_accepted():
    tech = dict(load_objects("technique")[0], status="draft")
    assert validate_schema([tech], "schema/technique.schema.json") == []


def test_non_mapping_deprecated_is_an_error_not_a_crash():
    errs = check_superseded([{"id": "PHL-T-009", "deprecated": "PHL-T-010"}])
    assert any("PHL-T-009" in e and "deprecated" in e for e in errs)


def test_empty_frontmatter_is_an_error_not_a_crash(tmp_path):
    from build.build import _parse

    f = tmp_path / "PHL-T-999.md"
    f.write_text("---\n\n---\n\nbody\n", encoding="utf-8")
    errs = validate_schema([dict(_parse(f, "frontmatter"), _source=f.name)], "schema/technique.schema.json")
    assert any("PHL-T-999.md" in e and "frontmatter" in e for e in errs)


def test_main_writes_artifact_only_on_clean_build(tmp_path, monkeypatch):
    import json
    import build.build as b

    graph = {"technique": [{"id": "PHL-T-001"}], "mappings": [
        {"subject_id": "PHL-T-001", "framework": "f", "external_id": "x"}]}
    monkeypatch.setattr(b, "ROOT", tmp_path)

    monkeypatch.setattr(b, "build", lambda: (graph, ["boom"]))
    try:
        b.main()
        raise AssertionError("expected SystemExit")
    except SystemExit as exc:
        assert exc.code == 1
    assert not (tmp_path / "phlipped.json").exists()

    monkeypatch.setattr(b, "build", lambda: (graph, []))
    b.main()
    out = json.loads((tmp_path / "phlipped.json").read_text())
    assert out["technique"] == [{"id": "PHL-T-001"}]
    assert out["mappings_matrix"] == {"PHL-T-001": {"f": ["x"]}}
