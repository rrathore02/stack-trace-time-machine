# Stack Trace Time Machine

Find the commit that broke your test, automatically.

When a test starts failing, `stt` runs `git bisect` between a known-good and known-bad commit, identifies the offending commit, and (optionally) drafts a revert PR. It uses the failing stack trace to skip commits that don't touch relevant files, making bisect dramatically faster on real repos.

## Status

Early work-in-progress. See `ROADMAP` below.

## Roadmap

- [ ] CLI skeleton
- [ ] Core bisect loop
- [ ] Pytest runner
- [ ] Stack-trace-aware commit filtering
- [ ] Flaky test detection
- [ ] SQLite history of test runs
- [ ] GitHub revert-PR drafts
- [ ] Jest runner
- [ ] Docs + demo repo
