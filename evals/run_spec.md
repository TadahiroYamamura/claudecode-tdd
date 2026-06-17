# Eval Run Specification

各 eval をサブエージェントとして実行するときの手順と出力仕様。

## ディレクトリ構成

```
skills/tdd-workspace/
└── iteration-N/
    └── <eval-name>/          # e.g. fizzbuzz-go
        ├── eval_metadata.json
        ├── outputs/
        │   ├── *.go              # 最終状態のGoソースファイル
        │   ├── test_output.txt   # go test -v ./... の出力
        │   ├── git_log.txt       # git log --oneline
        │   ├── phase.txt         # .tdd/PHASE の最終値
        │   ├── snapshots/        # PHASEフェーズごとのスナップショット
        │   └── repo/             # fixture ディレクトリの完全コピー（.git/ 含む）
        ├── grading.json
        └── timing.json
```

## サブエージェントへの指示テンプレート

```
以下のタスクをTDDで実装してください。

【スキルパス】
/home/develop/work/claudecode-tdd/skills/tdd/SKILL.md を読み込み、
commands/tdd/red.md、green.md、refactor.md の指示に従って作業すること。

【フィクスチャのセットアップ】
1. 次のスクリプトを実行して作業ディレクトリを作成する:
   /home/develop/work/claudecode-tdd/evals/setup_fixture.sh \
     /tmp/tdd-eval-<eval-name>-<unique-id> example.com/<eval-name>
2. 以降の作業はそのディレクトリ内で行うこと

【タスク】
<evals.json の prompt をそのまま記載>

【出力の保存】
作業完了後、以下をすべて <outputs-dir> へ保存すること:

1. Go ソースファイル
   cp /tmp/tdd-eval-.../**.go <outputs-dir>/

2. テスト結果
   cd /tmp/tdd-eval-... && go test -v ./... > <outputs-dir>/test_output.txt 2>&1

3. git ログ
   git -C /tmp/tdd-eval-... log --oneline > <outputs-dir>/git_log.txt

4. フェーズファイル
   cat /tmp/tdd-eval-.../.tdd/PHASE > <outputs-dir>/phase.txt

5. リポジトリ完全コピー（git 履歴込み）
   cp -r /tmp/tdd-eval-... <outputs-dir>/repo

6. ウォッチャー停止とスナップショット収集（**必ず実行**）
   /home/develop/work/claudecode-tdd/evals/teardown_fixture.sh \
     /tmp/tdd-eval-... <outputs-dir>
```

## eval_metadata.json テンプレート

```json
{
  "eval_id": 1,
  "eval_name": "fizzbuzz-go",
  "prompt": "<evals.json の prompt>",
  "assertions": []
}
```

assertions は実行前に evals.json の expectations からコピーする。

## 注意事項

- timing.json はエージェント完了通知に含まれる total_tokens と duration_ms から即座に保存すること
- fixture の /tmp/ ディレクトリはコピー完了後に削除してよい
