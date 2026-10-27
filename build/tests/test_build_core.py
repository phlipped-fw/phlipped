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
