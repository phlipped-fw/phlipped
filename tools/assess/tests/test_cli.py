import json

from click.testing import CliRunner

from phlipped_assess.cli import cli, load_items


def test_load_items_reads_assessment_from_built_artifact(data_path):
    items = load_items(data_path)
    assert [i.id for i in items] == [f"PSPS-00{n}" for n in range(1, 7)]
    assert all(i.probes for i in items)
    assert items[0].probes == ["PHL-T-001"]


def test_list_items_uses_data_option(data_path):
    r = CliRunner().invoke(cli, ["list-items", "--data", str(data_path)])
    assert r.exit_code == 0, r.output
    assert "PSPS-001" in r.output and "PSPS-006" in r.output


def test_report_command_writes_html(tmp_path, data_path):
    answers = tmp_path / "a.yml"
    answers.write_text("PSPS-001: false\nPSPS-002: true\n")
    assessment = tmp_path / "assessment.json"

    runner = CliRunner()
    r = runner.invoke(cli, ["run", "--data", str(data_path), "--answers", str(answers), "--out", str(assessment)])
    assert r.exit_code == 0, r.output
    assert assessment.exists()

    out = tmp_path / "report.html"
    r2 = runner.invoke(cli, ["report", "--data", str(data_path), "--in", str(assessment), "--out", str(out)])
    assert r2.exit_code == 0, r2.output

    html = out.read_text()
    assert "/ 100" in html
    # PSPS-001 was answered 'no' so it is a gap and must appear, linked to its technique
    assert "PSPS-001" in html
    assert "/threats/PHL-T-001.html" in html


def test_score_is_weighted_from_built_items(tmp_path, data_path):
    answers = tmp_path / "a.yml"
    answers.write_text("PSPS-001: true\n")
    out = tmp_path / "assessment.json"
    r = CliRunner().invoke(cli, ["run", "--data", str(data_path), "--answers", str(answers), "--out", str(out)])
    assert r.exit_code == 0, r.output
    items = load_items(data_path)
    expected = round(100 * 9 / sum(i.weight for i in items), 1)
    assert json.loads(out.read_text())["psps"] == expected


def test_missing_data_file_is_a_clear_error(tmp_path):
    r = CliRunner().invoke(cli, ["list-items", "--data", str(tmp_path / "nope.json")])
    assert r.exit_code != 0
    assert "build" in r.output
