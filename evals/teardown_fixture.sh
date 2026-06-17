#!/usr/bin/env bash
# Stops the PHASE watcher and collects snapshot outputs for eval grading.
# Usage: teardown_fixture.sh <target-dir> <output-dir>
set -euo pipefail

TARGET_DIR="${1:?Usage: teardown_fixture.sh <target-dir> <output-dir>}"
OUTPUT_DIR="${2:?Usage: teardown_fixture.sh <target-dir> <output-dir>}"

# ウォッチャーを停止
PID_FILE="$TARGET_DIR/.tdd/watcher.pid"
if [ -f "$PID_FILE" ]; then
  PID=$(cat "$PID_FILE")
  if kill -0 "$PID" 2>/dev/null; then
    kill "$PID"
    echo "Watcher stopped (PID: $PID)"
  fi
  rm -f "$PID_FILE"
fi

# スナップショットを出力ディレクトリへコピー
SNAP_SRC="$TARGET_DIR/.tdd/snapshots"
SNAP_DST="$OUTPUT_DIR/snapshots"
if [ -d "$SNAP_SRC" ]; then
  mkdir -p "$OUTPUT_DIR"
  cp -r "$SNAP_SRC" "$SNAP_DST"
  echo "Snapshots saved: $SNAP_DST"
  echo "--- snapshot summary ---"
  ls "$SNAP_DST"
else
  echo "No snapshots found"
fi
