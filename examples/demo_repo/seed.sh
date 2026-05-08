#!/usr/bin/env bash
# Seed a tiny git repo with a planted regression for the stt demo.
#
# Usage: bash seed.sh /tmp/stt-demo
set -euo pipefail

DEST="${1:-/tmp/stt-demo}"

if [[ -e "$DEST" ]]; then
    echo "refusing to overwrite existing path: $DEST" >&2
    exit 2
fi

mkdir -p "$DEST"
cd "$DEST"

git init -q -b main
git config user.email "demo@example.com"
git config user.name "Demo User"
git config commit.gpgsign false

mkdir tests

# --- commit 1: initial code, test passes ---
cat > compute.py <<'PY'
"""Toy module used by the stt demo."""


def answer():
    return 42
PY

cat > tests/test_compute.py <<'PY'
from compute import answer


def test_answer():
    assert answer() == 42
PY

cat > conftest.py <<'PY'
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
PY

git add . && git commit -q -m "Initial: compute.answer() returns 42"

# --- commit 2: docstring tweak (noise) ---
sed -i.bak 's/Toy module used by the stt demo./Toy module used by the stt demo. (revised)/' compute.py
rm compute.py.bak
git commit -q -am "docs: tighten compute docstring"

# --- commit 3: add an unrelated helper (noise) ---
cat > util.py <<'PY'
def double(x):
    return x * 2
PY
git add util.py && git commit -q -m "feat: add util.double()"

# --- commit 4: THE BUG ---
sed -i.bak 's/return 42/return 41/' compute.py
rm compute.py.bak
git commit -q -am "BUG: change answer to 41"

# --- commit 5: README (noise) ---
echo "# Demo repo" > README.md
git add README.md && git commit -q -m "docs: add README"

# --- commit 6: another helper (noise) ---
cat >> util.py <<'PY'


def triple(x):
    return x * 3
PY
git commit -q -am "feat: add util.triple()"

echo "Seeded $DEST with 6 commits. The regression is in commit titled 'BUG: change answer to 41'."
git -C "$DEST" --no-pager log --oneline
