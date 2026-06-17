#!/usr/bin/env bash
# Creates a fresh Go + git fixture for TDD skill eval runs.
# Usage: setup_fixture.sh <target-dir> [module-name]
set -euo pipefail

TARGET_DIR="${1:?Usage: setup_fixture.sh <target-dir> [module-name]}"
MODULE_NAME="${2:-example.com/tdd-eval}"

# inotify-tools が必要
if ! command -v inotifywait &> /dev/null; then
  echo "Installing inotify-tools..."
  sudo apt-get install -y -qq inotify-tools
fi

mkdir -p "$TARGET_DIR"
cd "$TARGET_DIR"

git init -q
git config user.email "eval@tdd-skill.test"
git config user.name "TDD Eval"

go mod init "$MODULE_NAME" > /dev/null

mkdir -p .tdd/snapshots
echo "none" > .tdd/PHASE
printf '.tdd/*\n!.tdd/PHASE\n' > .gitignore

# Stage .tdd/PHASE on every commit so phase transitions appear in git history.
mkdir -p .git/hooks
cat > .git/hooks/pre-commit << 'HOOK'
#!/usr/bin/env bash
if [ -f .tdd/PHASE ]; then
  git add .tdd/PHASE
fi
HOOK
chmod +x .git/hooks/pre-commit

# PHASEファイルを監視してサイクルごとにスナップショットを保存するウォッチャー。
# TDDではREDフェーズでコミットしないため、pre-commitフックではREDを捕捉できない。
# close_write イベントで go test を実行し、その時点のテスト結果と .go ファイルを保存する。
cat > .tdd/watcher.sh << 'WATCHER'
#!/usr/bin/env bash
set -euo pipefail
WORKDIR="$(cd "$(dirname "$0")/.." && pwd)"
SNAPSHOT_DIR="$WORKDIR/.tdd/snapshots"
CYCLE=0

while true; do
  inotifywait -qq -e close_write "$WORKDIR/.tdd/PHASE" 2>/dev/null || break
  PHASE=$(cat "$WORKDIR/.tdd/PHASE" 2>/dev/null)
  [ -z "$PHASE" ] && continue

  if [ "$PHASE" = "red" ]; then
    CYCLE=$((CYCLE + 1))
  fi

  SNAP="$SNAPSHOT_DIR/cycle-${CYCLE}-${PHASE}"
  mkdir -p "$SNAP"

  cd "$WORKDIR"

  # テスト結果を保存（失敗しても継続）
  go test ./... > "$SNAP/test_output.txt" 2>&1 || true

  # 直前のコミットからの差分を保存（未追跡ファイルも含める）
  # intent-to-add で未追跡の .go ファイルを一時的にインデックスに登録してから diff を取り、
  # その後 restore --staged で元の未追跡状態に戻す。
  git add -N $(git ls-files --others --exclude-standard -- '*.go' ':!.tdd/' 2>/dev/null) 2>/dev/null || true
  git diff HEAD > "$SNAP/git_diff.txt" 2>/dev/null || true
  git restore --staged . 2>/dev/null || true

  # ワーキングツリーの状態を保存
  git status --short > "$SNAP/git_status.txt" 2>/dev/null || true

  # .go ファイルをすべてコピー
  find "$WORKDIR" -name "*.go" -not -path "*/.git/*" | while read -r f; do
    rel="${f#$WORKDIR/}"
    mkdir -p "$SNAP/$(dirname "$rel")"
    cp "$f" "$SNAP/$rel"
  done

  echo "$(date -Iseconds) PHASE=$PHASE CYCLE=$CYCLE" >> "$SNAPSHOT_DIR/history.log"
done
WATCHER
chmod +x .tdd/watcher.sh

# ウォッチャーをバックグラウンドで起動（最大1時間で自動終了）
timeout 3600 .tdd/watcher.sh &
echo $! > .tdd/watcher.pid

git add go.mod
git commit -q -m "chore: initialize eval fixture"

echo "Fixture ready: $TARGET_DIR (watcher PID: $(cat .tdd/watcher.pid))"
