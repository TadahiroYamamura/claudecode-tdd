#!/usr/bin/env bash
# Ends a TDD session: removes the TDD guard block from the pre-commit hook.
set -euo pipefail

if [ ! -f ".tdd/active" ]; then
  echo "No active TDD session." >&2
  exit 0
fi

GIT_DIR=$(git rev-parse --git-dir 2>/dev/null) || { echo "Error: not inside a git repository." >&2; exit 1; }
HOOK="$GIT_DIR/hooks/pre-commit"

if grep -q "#<claudecode-tdd-block>" "$HOOK" 2>/dev/null; then
  sed -i '/#<claudecode-tdd-block>/,/#<\/claudecode-tdd-block>/d' "$HOOK"
fi

rm .tdd/active
echo "TDD session ended. Normal git commit is now allowed."
