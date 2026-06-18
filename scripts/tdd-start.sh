#!/usr/bin/env bash
# Starts a TDD session: appends the TDD guard block to the pre-commit hook.
set -euo pipefail

if [ ! -d ".tdd" ]; then
  echo "Error: .tdd directory not found. Run from the project root." >&2
  exit 1
fi

GIT_DIR=$(git rev-parse --git-dir 2>/dev/null) || { echo "Error: not inside a git repository." >&2; exit 1; }
HOOK="$GIT_DIR/hooks/pre-commit"

if grep -q "#<claudecode-tdd-block>" "$HOOK" 2>/dev/null; then
  echo "TDD guard already installed in $HOOK."
else
  if [ ! -f "$HOOK" ]; then
    printf '#!/usr/bin/env bash\n' > "$HOOK"
    chmod +x "$HOOK"
  fi
  cat >> "$HOOK" << 'BLOCK'
#<claudecode-tdd-block>
if [ -f .tdd/active ] && [ -z "$TDD_COMMIT" ]; then
  echo "Error: TDD session is active. Direct git commit is not allowed." >&2
  echo "  To commit: scripts/tdd-commit.sh <green|refactor> \"<message>\"" >&2
  echo "  To exit:   /tdd:end" >&2
  exit 1
fi
#</claudecode-tdd-block>
BLOCK
fi

touch .tdd/active
echo "TDD session started. Direct git commit is now blocked."
echo "Use scripts/tdd-commit.sh to commit, or run /tdd:end to exit the session."
