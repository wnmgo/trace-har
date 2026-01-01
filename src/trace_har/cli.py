from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console

from trace_har.converter import convert_trace_to_har

app = typer.Typer(add_completion=False, help="Rebuild HAR files from Playwright traces.")
console = Console()


@app.command("build")
def build_har(
    trace: Path = typer.Argument(..., exists=True, help="Trace directory or .zip file."),
    output: Path = typer.Option(Path("trace.har"), "--output", "-o", help="Output HAR path."),
    pretty: bool = typer.Option(False, "--pretty", help="Pretty-print JSON output."),
    overwrite: bool = typer.Option(False, "--overwrite", help="Overwrite existing HAR output."),
) -> None:
    """Convert a Playwright trace into a standalone HAR file."""
    if output.exists() and not overwrite:
        raise typer.BadParameter(f"Output already exists: {output}")

    har = convert_trace_to_har(trace)
    indent = 2 if pretty else None
    output.write_text(json.dumps(har, indent=indent, ensure_ascii=True), encoding="utf-8")

    entry_count = len(har.get("log", {}).get("entries", []))
    page_count = len(har.get("log", {}).get("pages", []))
    console.print(f"Wrote {entry_count} entries across {page_count} pages to {output}")


if __name__ == "__main__":
    app()
