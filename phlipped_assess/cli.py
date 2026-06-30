from __future__ import annotations

import json
from importlib import resources
from pathlib import Path

import click
import yaml
from rich.console import Console
from rich.table import Table

from .scoring import Item, gaps, psps

console = Console()


def load_checklist() -> list[Item]:
    raw = yaml.safe_load(resources.files("phlipped_assess.data").joinpath("checklist.yml").read_text())
    return [Item(**i) for i in raw["items"]]


@click.group()
def cli() -> None:
    """PHLIPPED assessment CLI."""


@cli.command()
@click.option("--answers", "answers_path", type=click.Path(exists=True, path_type=Path), help="YAML mapping of item_id: bool")
@click.option("--out", "out_path", type=click.Path(path_type=Path), default=Path("assessment.json"))
def run(answers_path: Path | None, out_path: Path) -> None:
    """Run the assessment checklist (interactive unless --answers is given)."""
    items = load_checklist()
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
        t.add_column("ID"); t.add_column("Weight", justify="right"); t.add_column("Recommendation"); t.add_column("€", justify="right"); t.add_column("hrs", justify="right")
        for g in missing[:10]:
            t.add_row(g.id, str(g.weight), g.recommendation, str(g.cost_eur), str(g.effort_hours))
        console.print(t)

    out_path.write_text(json.dumps({"psps": score, "answers": answers, "gaps": [g.id for g in missing]}, indent=2))
    console.print(f"\nWrote {out_path}")


@cli.command()
def list_items() -> None:
    """List checklist items."""
    items = load_checklist()
    for it in items:
        console.print(f"[cyan]{it.id}[/cyan] (w={it.weight}) - {it.question}")


if __name__ == "__main__":
    cli()
