# Demo: catch a planted regression

This directory contains seed scripts that build a tiny git repo with a planted regression so you can run `stt bisect` end-to-end without inventing your own bug.

## Layout of the seeded repo

```
demo/
├── compute.py          # the production code
├── tests/
│   └── test_compute.py # one passing test
└── (6 commits)
```

Commits 1–3 are noise (whitespace, docstring tweaks, an unrelated helper). **Commit 4 changes `compute.answer()` from `42` to `41` — the planted regression.** Commits 5–6 are more noise.

The test `tests/test_compute.py::test_answer` passes at commits 1–3 and fails at 4–6.

## Run it

### Bash / WSL / Linux / macOS

```bash
bash examples/demo_repo/seed.sh /tmp/stt-demo
stt bisect --repo /tmp/stt-demo --good HEAD~5 --test tests/test_compute.py::test_answer
```

### PowerShell (Windows)

```powershell
.\examples\demo_repo\seed.ps1 -Path C:\Temp\stt-demo
stt bisect --repo C:\Temp\stt-demo --good HEAD~5 --test tests/test_compute.py::test_answer
```

### Expected output

```
Bisecting <good>..<HEAD> for test 'tests/test_compute.py::test_answer' using pytest
  step 1: <sha> → FAIL
  step 2: <sha> → PASS
  step 3: <sha> → FAIL

First bad commit: <commit 4 SHA>
  iterations: 3
```

`stt` should identify the commit titled `"BUG: change answer to 41"` in fewer than 4 iterations.

## Try smart bisect

```bash
echo 'File "compute.py", line 5' > /tmp/trace.txt
stt bisect --repo /tmp/stt-demo --good HEAD~5 \
           --test tests/test_compute.py::test_answer \
           --trace-file /tmp/trace.txt
```

With the filter, `stt` only tests the one commit that touched `compute.py` — it finds the bug in **a single iteration**.
