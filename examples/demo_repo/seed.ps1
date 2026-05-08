# Seed a tiny git repo with a planted regression for the stt demo.
#
# Usage: .\seed.ps1 -Path C:\Temp\stt-demo

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$Path
)

$ErrorActionPreference = 'Stop'

if (Test-Path $Path) {
    Write-Error "refusing to overwrite existing path: $Path"
    exit 2
}

New-Item -ItemType Directory -Path $Path | Out-Null
Push-Location $Path
try {
    git init -q -b main
    git config user.email "demo@example.com"
    git config user.name "Demo User"
    git config commit.gpgsign false

    New-Item -ItemType Directory -Path tests | Out-Null

    # --- commit 1: initial code, test passes ---
    @'
"""Toy module used by the stt demo."""


def answer():
    return 42
'@ | Set-Content -Encoding utf8 compute.py

    @'
from compute import answer


def test_answer():
    assert answer() == 42
'@ | Set-Content -Encoding utf8 tests/test_compute.py

    @'
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
'@ | Set-Content -Encoding utf8 conftest.py

    git add . | Out-Null
    git commit -q -m "Initial: compute.answer() returns 42"

    # --- commit 2: docstring tweak (noise) ---
    (Get-Content compute.py) -replace 'Toy module used by the stt demo.', 'Toy module used by the stt demo. (revised)' |
        Set-Content -Encoding utf8 compute.py
    git commit -q -am "docs: tighten compute docstring"

    # --- commit 3: add an unrelated helper (noise) ---
    @'
def double(x):
    return x * 2
'@ | Set-Content -Encoding utf8 util.py
    git add util.py | Out-Null
    git commit -q -m "feat: add util.double()"

    # --- commit 4: THE BUG ---
    (Get-Content compute.py) -replace 'return 42', 'return 41' |
        Set-Content -Encoding utf8 compute.py
    git commit -q -am "BUG: change answer to 41"

    # --- commit 5: README (noise) ---
    "# Demo repo" | Set-Content -Encoding utf8 README.md
    git add README.md | Out-Null
    git commit -q -m "docs: add README"

    # --- commit 6: another helper (noise) ---
    Add-Content -Encoding utf8 util.py @'


def triple(x):
    return x * 3
'@
    git commit -q -am "feat: add util.triple()"

    Write-Host "Seeded $Path with 6 commits. The regression is in commit titled 'BUG: change answer to 41'."
    git --no-pager log --oneline
}
finally {
    Pop-Location
}
