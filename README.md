# Stack Trace Time Machine (`stt`)

> Find the commit that broke your test, automatically.

`stt` is a developer tool that combines `git bisect` with the failing stack trace to identify the offending commit fast — and (optionally) draft a revert PR. The naive way takes 15 minutes to four hours. `stt` does it while you finish your coffee.

```
$ stt bisect --good v1.4.2 --test tests/test_billing.py::test_invoice_total \
             --trace-file failure.log
Using last recorded passing SHA: v1.4.2
Smart bisect: filtering to commits touching 3 file(s):
  - src/billing/invoice.py
  - src/billing/tax.py
  - tests/test_billing.py
Bisecting a1b2c3d4e5..f6e5d4c3b2 for test 'tests/test_billing.py::test_invoice_total' using pytest
  step 1: 3f4a8b9c1d → PASS
  step 2: 8e2d1c0b5a → FAIL
  step 3: 5b9f2e7c4a → FAIL

First bad commit: 5b9f2e7c4a3d2e1f0a9b8c7d6e5f4a3b2c1d0e9f
  iterations: 3
  skipped 47 of 53 commits via stack-trace filter
```

---

## The problem

When a test fails on `main` (or in CI), the engineer typically:
1. Pulls `main`, confirms the failure locally.
2. Manually checks out commits one by one until they find the bad one.
3. Reads the diff. Decides whether to fix forward or revert.
4. Tags the original author. Opens a revert PR.

For a non-trivial regression in a busy repo, that's **15 minutes to four hours of focused engineering time per incident**. At a 100-engineer company with two regressions a week, that's roughly **520 engineer-hours / year** burned on bisect by hand.

`stt` automates steps 2–4. The engineer goes from "the test is failing" to "here's the commit, here's a draft revert PR" in one command.

---

## How it works

```
                ┌─────────────────────────────────────────────┐
                │                stt bisect                    │
                └────────────────────┬────────────────────────┘
                                     │
        ┌────────────────────────────┼─────────────────────────────┐
        ▼                            ▼                             ▼
  ┌───────────┐             ┌────────────────┐             ┌───────────────┐
  │  Storage  │             │  Stack-trace   │             │ Test runner   │
  │  (SQLite) │             │   parser       │             │  (pytest, …)  │
  └─────┬─────┘             └────────┬───────┘             └───────┬───────┘
        │                            │                             │
        │ last passing SHA           │ files in trace              │ pass/fail
        ▼                            ▼                             ▼
                  ┌────────────────────────────────┐
                  │       core bisect loop         │
                  │ (binary search + smart filter) │
                  └─────────────┬──────────────────┘
                                │
                                ▼
                  ┌────────────────────────────────┐
                  │   flaky-test re-confirmation   │
                  └─────────────┬──────────────────┘
                                │
                                ▼
                  ┌────────────────────────────────┐
                  │     GitHub revert-PR draft     │
                  └────────────────────────────────┘
```

Each box is a single Python module under [`stt/`](stt/). They're decoupled — you can swap the test runner, plug in a new stack-trace extractor, or skip the GitHub bit entirely.

---

## Quick start

```bash
git clone https://github.com/rrathore02/stack-trace-time-machine.git
cd stack-trace-time-machine
pip install -e .

# Bisect: find the commit that broke a test
stt bisect --repo /path/to/your/repo \
           --good HEAD~50 \
           --bad HEAD \
           --test tests/test_thing.py::test_works
```

After the first run, `--good` is optional — `stt` remembers the last commit where the test was green and uses that automatically.

---

## CLI reference

### `stt bisect`

Find the first commit between `--good` and `--bad` where `--test` starts failing.

| Flag | Default | Purpose |
|---|---|---|
| `--repo` | `.` | Path to git repo |
| `--good` | last passing SHA from history | Known-good commit ref |
| `--bad` | `HEAD` | Known-bad commit ref |
| `--test` | (required) | Test id, e.g. `tests/test_x.py::test_y` |
| `--runner` | `pytest` | Test framework (more coming) |
| `--trace-file` | — | Path to a file with the failing stack trace; enables smart filter |
| `--flaky-runs` | `1` | Re-run apparent failures this many times |
| `--flaky-threshold` | `0.6` | Fraction of re-runs that must fail to confirm |
| `--open-pr` | off | Push a revert branch and open a draft PR via `gh` |
| `--pr-base` | `main` | Base branch for the revert PR |
| `--restore/--no-restore` | restore | Restore original HEAD when bisect ends |

### `stt history`

Show recent recorded runs for a test.

```
stt history --test tests/test_billing.py::test_invoice_total --limit 10
```

---

## The interesting part: smart bisect

A bisect over 200 commits naïvely takes ~8 test runs. If the failing test takes 30s, that's 4 minutes — fine. But on a real codebase the test setup is often the slow part: container spin-up, fixture load, etc. Each iteration can be 2–5 minutes.

**Stack-trace-aware filtering** changes the math. Given the failing trace, we extract the source files involved (skipping `site-packages` and pytest internals) and only test commits that touched at least one of those files. On real codebases this typically prunes 80–95% of candidates.

Tradeoff: it's a **heuristic**. A regression caused by a config change or a transitively-imported file that doesn't appear in the trace will be missed and falsely attributed to a later commit. When in doubt, run without `--trace-file`.

The implementation lives in [`stt/bisect.py`](stt/bisect.py) (`make_stack_trace_filter`) and [`stt/stack_trace.py`](stt/stack_trace.py).

---

## Flaky-test handling

If we trust a single failure, a 5%-flaky test will make `stt` blame whichever commit happened to fail on the first roll. To avoid this, `--flaky-runs N` re-runs apparent failures up to N times. We only burn extra runs on **failures**, since flakiness is virtually always intermittent failures rather than intermittent passes.

The implementation short-circuits as soon as the verdict is unambiguous: with `--flaky-runs 5 --flaky-threshold 0.6`, two passes already make confirmation impossible, so we stop after run 2. See [`stt/flaky.py`](stt/flaky.py).

---

## Running the demo

A reproducible demo lives under [`examples/demo_repo/`](examples/demo_repo/). One script seeds a tiny repo with a planted regression; then you run `stt` against it.

```bash
# bash
bash examples/demo_repo/seed.sh /tmp/stt-demo
stt bisect --repo /tmp/stt-demo --good HEAD~5 --test tests/test_compute.py::test_answer
```

```powershell
# PowerShell
.\examples\demo_repo\seed.ps1 -Path C:\Temp\stt-demo
stt bisect --repo C:\Temp\stt-demo --good HEAD~5 --test tests/test_compute.py::test_answer
```

Expected output: `stt` finds the planted bad commit in 2–3 iterations.

---

## Limitations / non-goals

These are deliberate, not bugs.

- **Linear history only.** Bisecting through merge commits gets philosophically interesting (which side of the merge is "bad"?) and `stt` doesn't try. Use `git log --first-parent` to flatten if needed.
- **One failing test at a time.** If your suite has multiple regressions in one push, run `stt` per test.
- **Pytest only (today).** The runner ABC is in place; Jest, Go, and Rust runners are easy adds — see [`stt/runners/base.py`](stt/runners/base.py).
- **Stack-trace filter is a heuristic.** See above. Skip it when in doubt.
- **No parallel bisect.** `git worktree` would let us test commits in parallel — would roughly halve wall time. On the roadmap.

---

## What I'd build next

- **`git worktree`-based parallel bisect.** Run two candidates concurrently — biggest remaining lever on wall time.
- **Jest and Go runners.** Trivial extensions of the runner ABC.
- **CI integration.** A GitHub Action that triggers on red main, runs `stt`, and comments on the offending PR with a link to the revert.
- **Verify-before-revert.** Before opening the revert PR, run the full suite on the proposed revert branch — don't blindly revert.
- **Web dashboard.** Show in-progress bisects and history of caught regressions across a fleet of repos.

---

## Development

```bash
pip install -e ".[dev]"
pytest -q
```

17 tests; bisect tests build a real throwaway git repo so the binary search exercises real `git rev-list` / `git checkout`, not a mock.

---

## License

MIT. See [LICENSE](LICENSE).
