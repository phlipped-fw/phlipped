from __future__ import annotations

import json
from pathlib import Path

import click
import yaml
from rich.console import Console
from rich.table import Table

from .report import render_report
from .scoring import Item, gaps, psps

console = Console()


DEFAULT_DATA = Path("phlipped.json")

data_option = click.option(
    "--data",
    "data_path",
    type=click.Path(path_type=Path),
    default=DEFAULT_DATA,
    show_default=True,
    help="built phlipped.json artifact to read assessment items from",
)


def load_items(data_path: Path) -> list[Item]:
    """Read assessment items from the built phlipped.json artifact."""
    if not data_path.is_file():
        raise click.ClickException(f"{data_path} not found; build it first with 'python -m build.build' or pass --data")
    try:
        raw = json.loads(data_path.read_text(encoding="utf-8"))["assessment"]
    except (json.JSONDecodeError, KeyError, TypeError) as exc:
        raise click.ClickException(f"{data_path} is not a built phlipped.json with an 'assessment' list ({exc!r})")
    return [
        Item(id=i["id"], question=i["question"], weight=i["weight"], probes=i["probes"], recommendation=i["recommendation"])
        for i in raw
    ]


@click.group()
def cli() -> None:
    """PHLIPPED assessment CLI."""


@cli.command()
@click.option("--answers", "answers_path", type=click.Path(exists=True, path_type=Path), help="YAML mapping of item_id: bool")
@click.option("--out", "out_path", type=click.Path(path_type=Path), default=Path("assessment.json"))
@data_option
def run(answers_path: Path | None, out_path: Path, data_path: Path) -> None:
    """Run the assessment checklist (interactive unless --answers is given)."""
    items = load_items(data_path)
    answers: dict[str, bool] = {}

    if answers_path:
        answers = yaml.safe_load(answers_path.read_text()) or {}
    else:
        console.print("[bold cyan]PHLIPPED assessment - answer y/n for each item[/bold cyan]\n")
        for it in items:
            answers[it.id] = click.confirm(f"[{it.id}] {it.question}", default=False)

    score = psps(items, answers)
    missing = gaps(items, answers)

    console.print(f"\n[bold]PSPS:[/bold] [green]{score}[/green] / 100")

    if missing:
        t = Table(title="Top gaps (by weight)")
        t.add_column("ID"); t.add_column("Weight", justify="right"); t.add_column("Recommendation")
        for g in missing[:10]:
            t.add_row(g.id, str(g.weight), g.recommendation)
        console.print(t)

    out_path.write_text(json.dumps({"psps": score, "answers": answers, "gaps": [g.id for g in missing]}, indent=2))
    console.print(f"\nWrote {out_path}")


@cli.command()
@click.option("--in", "in_path", type=click.Path(exists=True, path_type=Path), default=Path("assessment.json"), help="assessment.json produced by 'run'")
@click.option("--out", "out_path", type=click.Path(path_type=Path), default=Path("report.html"))
@click.option("--base-url", default="/techniques", help="base URL for catalog technique links")
@data_option
def report(in_path: Path, out_path: Path, base_url: str, data_path: Path) -> None:
    """Render an HTML posture report from an assessment.json."""
    data = json.loads(in_path.read_text())
    items = load_items(data_path)
    answers = data.get("answers", {})
    score = data.get("psps", psps(items, answers))
    missing = gaps(items, answers)
    out_path.write_text(render_report(score, missing, base_url=base_url))
    console.print(f"Wrote {out_path} (PSPS {score}, {len(missing)} gaps)")


@cli.command()
@data_option
def list_items(data_path: Path) -> None:
    """List checklist items."""
    items = load_items(data_path)
    for it in items:
        console.print(f"[cyan]{it.id}[/cyan] (w={it.weight}) - {it.question}")


if __name__ == "__main__":
    cli()
