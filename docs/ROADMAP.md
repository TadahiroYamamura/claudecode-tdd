# TDD スキル改善ロードマップ

## 現状（iteration-2 時点）

iteration-2 での Tier 1 指標ベースライン:

| 指標 | iteration-2 |
|---|---|
| `red_authenticity_rate` | 100% |
| `phase_write_order_rate` | 5.6% ← 最重要課題 |
| `red_preceded_green_rate` | 85% |
| `green_phase_purity` | 88.9% |
| `refactor_noop_rate` | 20% |
| `test_first_rate` | 91.7% |

---

## フェーズ 1: インフラ整備（P1 修正）

**目標**: `phase_write_order_rate` を改善可能な状態にする

### タスク

**P1 の根本修正: 方針未決定**

現在エージェントは実装をコミットした後に PHASE を書くため、GREEN/REFACTOR スナップショットに実装差分が残らない。以下の選択肢がある:

- **A案**: commit-msg フックがコミットメッセージのプレフィックスから PHASE を推定して自動書き込み
  - `feat:` → green、`refactor:` → refactor、`test:` → red
  - エージェントの手順変更が不要
- **B案**: commit-msg フックがコミット時の PHASE を検証し、不一致を拒否
  - エージェントが PHASE を正しく書く能力を直接試す

方針を決定し、iteration-3 で `phase_write_order_rate` の改善を確認する。

---

## フェーズ 2: スキル文書の改善

**目標**: P2・P3・P4 を instruction-level で修正する

### タスク

**P2: 空 REFACTOR コミット抑制**

`refactor.md` に「改善点がなければ次の RED へ進む。空コミットを作らない」を明示する。

**P3: GREEN フェーズでのテスト追加禁止**

`green.md` に「GREEN フェーズではテストを追加しない。テストの追加は RED フェーズの責務」を明示する。

**P4: Triangulation での RED 必須**

`green.md` に「Fake It の後、より一般的な実装へ移行する場合も必ず新しい RED テストを書いてから行う」を明示する。

---

## フェーズ 3: 言語別イディオム対応（P6）

**目標**: 言語固有のベストプラクティスをスキルに組み込む

### タスク

**テストスタイルルールの整備**

`~/.claude/rules/` にパス指定ルールを作成する:

```
# Go テストファイル向けルール
paths: "**/*_test.go"
- テストは Table-Driven Test スタイルで記述する
- テストヘルパーは t.Helper() を呼ぶ
```

他言語も同様に `*.spec.ts`、`*_test.py` 等で追加できる構造にする。

**gopls MCP の導入（Go 専用）**

gopls（Go 公式言語サーバー）を MCP サーバーとして接続し、エージェントが静的解析・型情報・参照検索をツール呼び出しで行えるようにする。詳細は [GOPLS_USAGE.md](./GOPLS_USAGE.md) を参照。

対応後にスキル文書（`green.md` / `refactor.md`）に gopls ツールの使用タイミングを明記する。

---

## フェーズ 4: 高度な評価

**目標**: P5・P9・P10 を評価できる体制を整える

### タスク

**P5: Fake It 採用率（LLM 採点）**

P1 修正により GREEN スナップショットに実装差分が残るようになったら、LLM が「最小実装か否か」を採点できる。`grade.py` に `--tier2` オプションとして追加する。

**P9: 1コミット1変更の定義**

「1変更」の基準を言語化して `refactor.md` に追記する。基準が確立したら `grade.py` に機械的なチェックを追加する。

**P10: コンテキスト汚染テスト**

10〜20 サイクルを要する eval タスクを設計する（例: Markdown パーサー）。`grade.py` に「サイクル位置 vs 遵守率」の集計機能を追加する。

---

## 長期: 継続的改善サイクル

各イテレーションの流れ:

```
eval 実行
  ↓
grade.py <iteration-dir>  →  benchmark.json
  ↓
前イテレーションと比較
  ↓
低スコアの指標に対応する問題を特定
  ↓
スキル文書またはインフラを修正
  ↓
次のイテレーションへ
```

ベースラインは iteration-2 の benchmark.json。各指標で「前回比でどう変わったか」を見ることで、スキル改善が再現可能・検証可能になる。
