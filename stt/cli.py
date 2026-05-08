"""Command-line entry point for stt."""

from __future__ import annotations

import click

from . import __version__


@click.group()
@click.version_option(__version__, prog_name="stt")
def cli() -> None:
    """Stack Trace Time Machine — find the commit that broke your test."""


@cli.command(name="bisect")
@click.option("--repo", default=".", show_default=True, help="Path to git repo.")
@click.option("--good", required=True, help="Known-good commit SHA (test passes).")
@click.option("--bad", default="HEAD", show_default=True, help="Known-bad commit SHA.")
@click.option("--test", required=True, help="Test identifier (e.g. tests/test_x.py::test_y).")
def bisect_cmd(repo: str, good: str, bad: str, test: str) -> None:
    """Bisect history between GOOD and BAD to find the commit that broke TEST."""
    click.echo(f"[stub] would bisect {good[:8]}..{bad[:8]} in {repo} for test '{test}'")


if __name__ == "__main__":
    cli()
