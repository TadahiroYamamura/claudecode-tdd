#!/usr/bin/env bash
# Atomically writes .tdd/PHASE then commits, enforcing write-before-commit ordering.
# Usage: scripts/tdd-commit.sh <green|refactor> <message>
#
# Pass multi-line messages via heredoc:
#   scripts/tdd-commit.sh green "$(cat <<'EOF'
#   feat: summary
#
#   ## 意図
#   why this change was made
#   EOF
#   )"
set -euo pipefail

if [ $# -ne 2 ]; then
  echo "Usage: scripts/tdd-commit.sh <green|refactor> <message>" >&2
  exit 1
fi

PHASE="$1"
MESSAGE="$2"

case "$PHASE" in
  green|refactor) ;;
  *) echo "Error: PHASE must be green or refactor (got: '$PHASE')" >&2; exit 1 ;;
esac

if [ ! -d ".tdd" ]; then
  echo "Error: .tdd directory not found. Run from the project root." >&2
  exit 1
fi

echo "$PHASE" > .tdd/PHASE
TDD_COMMIT=1 git commit -m "$MESSAGE"
