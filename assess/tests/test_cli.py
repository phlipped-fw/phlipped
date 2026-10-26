import json

from click.testing import CliRunner

from phlipped_assess.cli import cli


def test_report_command_writes_html(tmp_path):
    answers = tmp_path / "a.yml"
    answers.write_text("PSPS-001: false\nPSPS-002: true\n")
    assessment = tmp_path / "assessment.json"

    runner = CliRunner()
    r = runner.invoke(cli, ["run", "--answers", str(answers), "--out", str(assessment)])
    assert r.exit_code == 0, r.output
    assert assessment.exists()

    out = tmp_path / "report.html"
    r2 = runner.invoke(cli, ["report", "--in", str(assessment), "--out", str(out)])
    assert r2.exit_code == 0, r2.output

    html = out.read_text()
    assert "/ 100" in html
    # PSPS-001 was answered 'no' so it is a gap and must appear
    assert "PSPS-001" in html
