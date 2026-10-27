from build.build import build, resolve_refs


def test_every_technique_tactic_resolves():
    graph, errs = build()
    assert errs == []  # the real data is self-consistent


def test_dangling_tactic_ref_is_rejected():
    graph = {"tactic": [{"id": "PHL-TA-01"}],
             "technique": [{"id": "PHL-T-001", "tactics": ["PHL-TA-99"]}]}
    assert any("PHL-TA-99" in e for e in resolve_refs(graph))
