from build.build import build, resolve_refs


def test_every_technique_tactic_resolves():
    graph, errs = build()
    assert errs == []  # the real data is self-consistent


def test_dangling_tactic_ref_is_rejected():
    graph = {"tactic": [{"id": "PHL-TA-01"}],
             "technique": [{"id": "PHL-T-001", "tactics": ["PHL-TA-99"]}]}
    assert any("PHL-TA-99" in e for e in resolve_refs(graph))


def test_malformed_tactics_do_not_crash_or_add_noise():
    # the schema reports these shapes; the ref rule must neither raise nor pile on
    base = {"tactic": [{"id": "PHL-TA-01"}]}
    for bad in ("PHL-TA-99", None, 7, {"a": 1}, [["PHL-TA-01"]], [{"a": 1}], [None, 3]):
        graph = {**base, "technique": [{"id": "PHL-T-001", "tactics": bad}]}
        assert resolve_refs(graph) == []
    mixed = {**base, "technique": [{"id": "PHL-T-001", "tactics": [["x"], "PHL-TA-99"]}]}
    errs = resolve_refs(mixed)
    assert len(errs) == 1 and "PHL-TA-99" in errs[0]
