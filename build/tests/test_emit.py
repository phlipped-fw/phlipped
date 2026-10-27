import json

import pytest

from build import build as b


def test_phlipped_json_has_every_type_and_version(tmp_path):
    b.main(out_dir=tmp_path)
    data = json.loads((tmp_path / "phlipped.json").read_text(encoding="utf-8"))
    for key in ("tactics", "techniques", "data_sources", "detections", "mitigations",
                "mappings", "assessment"):
        assert data[key], key
    assert data["mappings_matrix"]
    assert data["framework_version"] == b.FRAMEWORK_VERSION == "0.1.0"
    assert data["generated"].endswith("Z")


def test_per_type_files_are_emitted_to_dist(tmp_path):
    b.main(out_dir=tmp_path)
    dist = tmp_path / "dist"
    combined = json.loads((tmp_path / "phlipped.json").read_text(encoding="utf-8"))
    for name, key in (("tactic", "tactics"), ("technique", "techniques"),
                      ("data_source", "data_sources"), ("detection", "detections"),
                      ("mitigation", "mitigations"), ("assessment", "assessment"),
                      ("mappings", "mappings"), ("mappings_matrix", "mappings_matrix")):
        assert json.loads((dist / f"{name}.json").read_text(encoding="utf-8")) == combined[key]


def test_nothing_is_written_on_a_failed_build(tmp_path, monkeypatch):
    monkeypatch.setattr(b, "build", lambda: ({}, ["boom"]))
    with pytest.raises(SystemExit) as exc:
        b.main(out_dir=tmp_path)
    assert exc.value.code == 1
    assert list(tmp_path.iterdir()) == []


def test_exact_duplicate_mapping_relation_fails_the_build(monkeypatch):
    row = {"subject_id": "PHL-T-001", "framework": "attack", "external_id": "T1200"}
    other = {**row, "external_id": "T1111"}
    # same relation twice, even with a differing note, is a duplicate
    errs = b.check_duplicate_mappings([row, other, {**row, "note": "again"}])
    assert len(errs) == 1 and "PHL-T-001" in errs[0] and "T1200" in errs[0]
    assert b.check_duplicate_mappings([row, other]) == []

    real = b.load_mappings()[0]
    monkeypatch.setattr(b, "load_mappings", lambda: (real + [real[0]], []))
    _, errors = b.build()
    assert any("duplicate mapping" in e for e in errors)


def test_only_the_first_five_mitigations_carry_cost_figures():
    graph, errors = b.build()
    assert errors == []
    by_id = {m["id"]: m for m in graph["mitigation"]}
    for n in range(1, 19):
        m = by_id[f"PHL-M-{n:03d}"]
        has = "cost_eur" in m or "effort_hours" in m
        assert has == (n <= 5), m["id"]
