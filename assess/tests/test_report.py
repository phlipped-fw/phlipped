from phlipped_assess.report import render_report
from phlipped_assess.scoring import Item


def _item(id, weight, refs):
    return Item(
        id=id,
        question=f"q {id}",
        weight=weight,
        threat_refs=refs,
        recommendation=f"fix {id}",
        cost_eur=100,
        effort_hours=8,
    )


def test_report_shows_the_score():
    html = render_report(42.5, [])
    assert "42.5" in html


def test_report_lists_each_gap_recommendation_and_threat_link():
    gaps = [_item("PSPS-001", 9, ["PHL-T-003"])]
    html = render_report(10.0, gaps)
    assert "PSPS-001" in html
    assert "fix PSPS-001" in html
    # each gap links to its catalog threat page
    assert "PHL-T-003" in html
    assert "/threats/PHL-T-003" in html


def test_report_renders_gaps_in_given_priority_order():
    gaps = [_item("PSPS-A", 9, []), _item("PSPS-B", 3, [])]
    html = render_report(0.0, gaps)
    assert html.index("PSPS-A") < html.index("PSPS-B")
