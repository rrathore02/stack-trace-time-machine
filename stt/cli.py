"""Command-line entry point for stt."""

from __future__ import annotations

import sys
from pathlib import Path

import click

from . import __version__, git_utils
from .bisect import bisect
from .runners import PytestRunner


@click.group()
@click.version_option(__version__, prog_name="stt")
def cli() -> None:
    """Stack Trace Time Machine — find the commit that broke your test."""


@cli.command(name="bisect")
@click.option("--repo", default=".", show_default=True, help="Path to git repo.")
@click.option("--good", required=True, help="Known-good commit ref (test passes).")
@click.option("--bad", default="HEAD", show_default=True, help="Known-bad commit ref.")
@click.option("--test", required=True, help="Test id (e.g. tests/test_x.py::test_y).")
@click.option(
    "--runner",
    type=click.Choice(["pytest"], case_sensitive=False),
    default="pytest",
    show_default=True,
)
@click.option(
    "--restore/--no-restore",
    default=True,
    help="Restore the original HEAD when bisect finishes.",
)
def bisect_cmd(repo: str, good: str, bad: str, test: str, runner: str, restore: bool) -> None:
    """Bisect history between GOOD and BAD to find the commit that broke TEST."""
    repo_path = str(Path(repo).resolve())

    if not git_utils.is_clean(repo_path):
        click.secho("Working tree is not clean — commit or stash before bisecting.", fg="red")
        sys.exit(2)

    original = git_utils.current_sha(repo_path)
    good_sha = git_utils.resolve(repo_path, good)
    bad_sha = git_utils.resolve(repo_path, bad)

    runner_impl = PytestRunner()

    def test_fn(sha: str) -> bool:
        return runner_impl.run(repo_path, test).passed

    def on_step(sha: str, passed: bool, n: int) -> None:
        marker = click.style("PASS", fg="green") if passed else click.style("FAIL", fg="red")
        click.echo(f"  step {n}: {sha[:10]} → {marker}")

    click.echo(
        f"Bisecting {good_sha[:10]}..{bad_sha[:10]} for test {test!r} using {runner}"
    )
    try:
        result = bisect(repo_path, good_sha, bad_sha, test_fn, on_step=on_step)
    finally:
        if restore:
            git_utils.checkout(repo_path, original)

    click.echo("")
    if result.bad_commit:
        click.secho(f"First bad commit: {result.bad_commit}", fg="red", bold=True)
        click.echo(f"  iterations: {result.iterations}")
    else:
        click.secho("No regression found — the test passed at every candidate.", fg="yellow")


if __name__ == "__main__":
    cli()
