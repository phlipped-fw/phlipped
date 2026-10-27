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


def test_dangling_data_source_ref_is_rejected():
    graph = {"data_source": [{"id": "PHL-DS-01"}],
             "technique": [{"id": "PHL-T-001", "data_sources": ["PHL-DS-99"]}]}
    errs = resolve_refs(graph)
    assert len(errs) == 1 and "PHL-DS-99" in errs[0]


def test_resolving_data_source_ref_is_clean():
    graph = {"data_source": [{"id": "PHL-DS-01"}],
             "technique": [{"id": "PHL-T-001", "data_sources": ["PHL-DS-01"]}]}
    assert resolve_refs(graph) == []


def test_malformed_data_sources_do_not_crash_or_add_noise():
    base = {"data_source": [{"id": "PHL-DS-01"}]}
    for bad in ("PHL-DS-99", None, 7, {"a": 1}, [["PHL-DS-01"]], [None, 3]):
        graph = {**base, "technique": [{"id": "PHL-T-001", "data_sources": bad}]}
        assert resolve_refs(graph) == []


def test_techniques_without_data_sources_are_allowed():
    graph = {"data_source": [], "technique": [{"id": "PHL-T-001"}]}
    assert resolve_refs(graph) == []


def test_real_data_sources_are_seeded_and_referenced():
    graph, errs = build()
    assert errs == []
    ds_ids = {d["id"] for d in graph["data_source"]}
    assert ds_ids  # seeded
    cited = {r for t in graph["technique"] for r in t.get("data_sources", [])}
    assert cited <= ds_ids
    assert ds_ids <= cited  # no seeded channel that nothing references


def test_dangling_detection_technique_ref_is_rejected():
    graph = {"technique": [{"id": "PHL-T-001"}],
             "data_source": [{"id": "PHL-DS-01"}],
             "detection": [{"id": "PHL-D-001", "techniques": ["PHL-T-099"],
                            "data_sources": ["PHL-DS-01"]}]}
    errs = resolve_refs(graph)
    assert len(errs) == 1 and "PHL-D-001" in errs[0] and "PHL-T-099" in errs[0]


def test_dangling_detection_data_source_ref_is_rejected():
    graph = {"technique": [{"id": "PHL-T-001"}],
             "data_source": [{"id": "PHL-DS-01"}],
             "detection": [{"id": "PHL-D-001", "techniques": ["PHL-T-001"],
                            "data_sources": ["PHL-DS-99"]}]}
    errs = resolve_refs(graph)
    assert len(errs) == 1 and "PHL-D-001" in errs[0] and "PHL-DS-99" in errs[0]


def test_resolving_detection_refs_are_clean():
    graph = {"technique": [{"id": "PHL-T-001"}],
             "data_source": [{"id": "PHL-DS-01"}],
             "detection": [{"id": "PHL-D-001", "techniques": ["PHL-T-001"],
                            "data_sources": ["PHL-DS-01"]}]}
    assert resolve_refs(graph) == []


def test_malformed_detection_refs_do_not_crash_or_add_noise():
    base = {"technique": [{"id": "PHL-T-001"}], "data_source": [{"id": "PHL-DS-01"}]}
    for bad in ("PHL-T-099", None, 7, {"a": 1}, [["PHL-T-001"]], [None, 3]):
        graph = {**base, "detection": [{"id": "PHL-D-001", "techniques": bad,
                                        "data_sources": bad}]}
        assert resolve_refs(graph) == []


def test_real_detections_are_loaded_with_inline_logic():
    graph, errs = build()
    assert errs == []
    dets = {d["id"]: d for d in graph["detection"]}
    assert set(dets) == {"PHL-D-002", "PHL-D-003", "PHL-D-011"}
    for d in dets.values():
        assert "rule_file" not in d
        assert "detection:" in d["logic"] and "condition:" in d["logic"]
        assert "catalog/threats" not in d["logic"]
