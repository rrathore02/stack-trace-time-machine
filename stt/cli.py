"""Command-line entry point for stt."""

from __future__ import annotations

import sys
from pathlib import Path

import click

from . import __version__, git_utils
from .bisect import bisect, make_stack_trace_filter
from .flaky import wrap_predicate
from .github_integration import GitHubError, build_revert_pr, open_revert_pr
from .runners import PytestRunner
from .stack_trace import extract_python_files
from .storage import Storage


@click.group()
@click.version_option(__version__, prog_name="stt")
def cli() -> None:
    """Stack Trace Time Machine — find the commit that broke your test."""


@cli.command(name="bisect")
@click.option("--repo", default=".", show_default=True, help="Path to git repo.")
@click.option(
    "--good",
    default=None,
    help="Known-good commit ref. If omitted, uses the last passing SHA from history.",
)
@click.option("--bad", default="HEAD", show_default=True, help="Known-bad commit ref.")
@click.option("--test", required=True, help="Test id (e.g. tests/test_x.py::test_y).")
@click.option(
    "--runner",
    type=click.Choice(["pytest"], case_sensitive=False),
    default="pytest",
    show_default=True,
)
@click.option(
    "--trace-file",
    type=click.Path(exists=True, dir_okay=False),
    help="Path to a file containing the failing stack trace. Enables smart filtering.",
)
@click.option(
    "--flaky-runs",
    default=1,
    show_default=True,
    type=click.IntRange(min=1, max=10),
    help="Re-run apparent failures this many times to weed out flakes.",
)
@click.option(
    "--flaky-threshold",
    default=0.6,
    show_default=True,
    type=click.FloatRange(min=0.1, max=1.0),
    help="Fraction of re-runs that must fail to confirm a real failure.",
)
@click.option(
    "--open-pr",
    is_flag=True,
    default=False,
    help="After identifying the bad commit, open a draft revert PR via gh.",
)
@click.option(
    "--pr-base",
    default="main",
    show_default=True,
    help="Base branch for the revert PR.",
)
@click.option(
    "--restore/--no-restore",
    default=True,
    help="Restore the original HEAD when bisect finishes.",
)
def bisect_cmd(
    repo: str,
    good: str | None,
    bad: str,
    test: str,
    runner: str,
    trace_file: str | None,
    flaky_runs: int,
    flaky_threshold: float,
    open_pr: bool,
    pr_base: str,
    restore: bool,
) -> None:
    """Bisect history between GOOD and BAD to find the commit that broke TEST."""
    repo_path = str(Path(repo).resolve())

    if not git_utils.is_clean(repo_path):
        click.secho("Working tree is not clean — commit or stash before bisecting.", fg="red")
        sys.exit(2)

    storage = Storage()

    if good is None:
        good = storage.last_passing_sha(repo_path, test)
        if good is None:
            click.secho(
                "No --good provided and no passing run recorded for this test yet. "
                "Pass --good explicitly or run the test on a known-good commit first.",
                fg="red",
            )
            sys.exit(2)
        click.echo(f"Using last recorded passing SHA: {good[:10]}")

    original = git_utils.current_sha(repo_path)
    good_sha = git_utils.resolve(repo_path, good)
    bad_sha = git_utils.resolve(repo_path, bad)

    candidate_filter = None
    if trace_file:
        trace_text = Path(trace_file).read_text(encoding="utf-8", errors="replace")
        files = extract_python_files(trace_text)
        if files:
            click.echo(f"Smart bisect: filtering to commits touching {len(files)} file(s):")
            for f in files[:5]:
                click.echo(f"  - {f}")
            if len(files) > 5:
                click.echo(f"  … and {len(files) - 5} more")
            candidate_filter = make_stack_trace_filter(repo_path, files)
        else:
            click.secho("No source files found in trace; falling back to full bisect.", fg="yellow")

    runner_impl = PytestRunner()

    def raw_test_fn(sha: str) -> bool:
        result = runner_impl.run(repo_path, test)
        storage.record(repo_path, test, sha, result.passed)
        return result.passed

    test_fn = wrap_predicate(raw_test_fn, runs=flaky_runs, fail_threshold=flaky_threshold)

    def on_step(sha: str, passed: bool, n: int) -> None:
        marker = click.style("PASS", fg="green") if passed else click.style("FAIL", fg="red")
        click.echo(f"  step {n}: {sha[:10]} → {marker}")

    click.echo(
        f"Bisecting {good_sha[:10]}..{bad_sha[:10]} for test {test!r} using {runner}"
    )
    try:
        result = bisect(
            repo_path,
            good_sha,
            bad_sha,
            test_fn,
            candidate_filter=candidate_filter,
            on_step=on_step,
        )
    finally:
        if restore:
            git_utils.checkout(repo_path, original)

    click.echo("")
    if result.bad_commit:
        click.secho(f"First bad commit: {result.bad_commit}", fg="red", bold=True)
        click.echo(f"  iterations: {result.iterations}")
        if result.skipped:
            click.echo(
                f"  skipped {result.skipped} of {result.total_candidates} commits via stack-trace filter"
            )

        pr = build_revert_pr(
            bad_sha=result.bad_commit,
            base_branch=pr_base,
            bisect_log=result.log,
            failing_test=test,
        )
        if open_pr:
            try:
                pr = open_revert_pr(repo_path, pr, bad_sha=result.bad_commit)
                click.secho(f"\nDraft revert PR opened: {pr.url}", fg="green", bold=True)
            except GitHubError as exc:
                click.secho(f"\nCould not open PR automatically: {exc}", fg="red")
                click.echo("Falling back to dry-run output:\n")
                click.echo(f"  branch: {pr.branch}\n  title:  {pr.title}\n")
                click.echo(pr.body)
        else:
            click.echo("\nDry run — pass --open-pr to push a revert branch and open a draft PR.")
            click.echo(f"  branch: {pr.branch}")
            click.echo(f"  title:  {pr.title}")
    else:
        click.secho("No regression found — the test passed at every candidate.", fg="yellow")


@cli.command(name="history")
@click.option("--repo", default=".", show_default=True)
@click.option("--test", required=True)
@click.option("--limit", default=20, show_default=True)
def history_cmd(repo: str, test: str, limit: int) -> None:
    """Show recent recorded runs for a test."""
    repo_path = str(Path(repo).resolve())
    storage = Storage()
    rows = storage.history(repo_path, test, limit=limit)
    if not rows:
        click.echo("(no recorded runs)")
        return
    for sha, passed, ts in rows:
        marker = click.style("PASS", fg="green") if passed else click.style("FAIL", fg="red")
        click.echo(f"  {ts}  {sha[:10]}  {marker}")


if __name__ == "__main__":
    cli()
