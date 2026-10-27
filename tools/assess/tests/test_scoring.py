from phlipped_assess.scoring import Item, gaps, psps


def _item(id, weight):
    return Item(id=id, question="q", weight=weight, probes=["PHL-T-001"], recommendation="r")


def test_psps_is_zero_when_all_answers_are_no():
    items = [_item("A", 5), _item("B", 5)]
    assert psps(items, {"A": False, "B": False}) == 0.0


def test_psps_is_100_when_all_answers_are_yes():
    items = [_item("A", 5), _item("B", 3)]
    assert psps(items, {"A": True, "B": True}) == 100.0


def test_psps_is_weighted_not_counted():
    items = [_item("A", 9), _item("B", 1)]
    # only the heavy item passes -> 90, not 50
    assert psps(items, {"A": True, "B": False}) == 90.0


def test_psps_handles_empty_checklist():
    assert psps([], {}) == 0.0


def test_gaps_are_sorted_by_weight_desc():
    items = [_item("light", 2), _item("heavy", 9), _item("mid", 5)]
    order = [g.id for g in gaps(items, {})]
    assert order == ["heavy", "mid", "light"]


def test_gaps_exclude_passed_items():
    items = [_item("A", 5), _item("B", 5)]
    assert [g.id for g in gaps(items, {"A": True})] == ["B"]
