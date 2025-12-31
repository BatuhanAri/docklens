from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from .parser import load_compose
from .report import render_json, render_markdown, write_output
from .rules import Severity, run_rules

app = typer.Typer(
    add_completion=False, help="DockLens: docker-compose analyzer and report generator."
)
console = Console()

ComposePath = Annotated[Path, typer.Argument(help="Path to docker-compose.yml")]
OutPath = Annotated[Path | None, typer.Option("--out", "-o", help="Write Markdown report")]
JsonPath = Annotated[Path | None, typer.Option("--json", help="Write JSON report")]


@app.command()
def scan(
    compose: ComposePath,
    out: OutPath = None,
    json_out: JsonPath = None,
) -> None:
    """
    Scan a docker-compose file and print a findings summary.
    """
    model = load_compose(compose)
    findings = run_rules(model)

    # Terminal summary table
    table = Table(title=f"DockLens Findings — {model.path.name}")
    table.add_column("Severity", style="bold")
    table.add_column("Rule")
    table.add_column("Service")
    table.add_column("Title")

    sev_style = {
        Severity.ERROR: "red",
        Severity.WARN: "yellow",
        Severity.INFO: "cyan",
    }

    for f in findings:
        table.add_row(
            f.severity.value.upper(),
            f.rule_id,
            f.service,
            f.title,
            style=sev_style.get(f.severity, ""),
        )

    console.print(table)

    # Short summary
    errors = sum(1 for f in findings if f.severity == Severity.ERROR)
    warns = sum(1 for f in findings if f.severity == Severity.WARN)
    infos = sum(1 for f in findings if f.severity == Severity.INFO)
    console.print(
        f"\nSummary: [red]{errors} error(s)[/red], [yellow]{warns} warning(s)[/yellow], [cyan]{infos} info[/cyan]"
    )

    # Write outputs
    if out:
        md = render_markdown(model, findings)
        p = write_output(out, md)
        console.print(f"\nWrote Markdown report: {p}")

    if json_out:
        js = render_json(model, findings)
        p = write_output(json_out, js)
        console.print(f"Wrote JSON report: {p}")

    # Exit code discipline: fail CI if errors exist
    if errors > 0:
        raise typer.Exit(code=2)


if __name__ == "__main__":
    app()
