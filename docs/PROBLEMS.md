# TDDスキル 既知の問題

## P1: GREEN フェーズで PHASE 書き込みがコミット後になる ✅ 対応済み

**発見方法**: iteration-2 スナップショットの `cycle-N-green/git_diff.txt` を確認

**現象**: green.md には「`green` を `.tdd/PHASE` に書いてから `git commit`」と指示しているが、
エージェントは実装をコミットした後に PHASE=green を書く。
その結果、GREEN スナップショットの `git_diff.txt` に実装差分が現れない。

**影響**: 「GREEN フェーズで Fake It が使われたか」をスナップショットから検証できない。

**再現**: iteration-2 全3件（fizzbuzz-go / stack-go / calculator-go）で発生。

**対応**: `scripts/tdd-commit.sh <phase> "<message>"` ラッパーを導入。PHASE 書き込みとコミットをアトミックに行い、エージェントが `git commit` を直接叩けないよう pre-commit フックでブロックする。iteration-3 で改善を確認する。

---

## P2: REFACTOR 不要時に空コミットが作られる ✅ 対応済み

**発見方法**: iteration-1/2 の git_log.txt を確認

**現象**: リファクタリングすべき箇所がない場合でも `refactor: サイクルNリファクタリングなし` という
コードを変更しないコミットを作る。1サイクルで複数の refactor: コミットを作ること自体は問題ではないが、
何も変更しないコミットは git 履歴を汚染する。改善箇所がなければ次の RED へ進むべき。

**再現**: iteration-2 calculator-go に3件（サイクル1〜3）、iteration-1 fizzbuzz-go/calculator-go にも発生。

**対応**: `scripts/tdd-commit.sh refactor ""` のように空メッセージを渡すと PHASE のみ更新してコミットをスキップする。`refactor.md` のワークフローに「改善不要の場合は空メッセージで PHASE を進める」を明示した。

---

## P3: GREEN フェーズでテストを追加する

**発見方法**: iteration-2 calculator-go の `cycle-1-green/git_diff.txt` を確認

**現象**: GREEN フェーズ（実装だけすべきフェーズ）でテストファイルへの追加が行われている。
テストの追加は RED フェーズの責務。

**再現**: iteration-2 calculator-go のサイクル1。

---

## P5: Fake It をスキップして Obvious Implementation を多用する

**発見方法**: iteration-2 GREEN スナップショットの実装ファイルを確認

**現象**: テストが1件しかない段階から Obvious Implementation（汎用的な正解実装）を書く。
Kent Beck の TDD では最初は最小限の偽実装（Fake It）で通し、テストを追加しながら
Triangulation で一般化していくことで「本当に必要な実装」を導き出す。

- calculator cycle-1: `Add(2,3)=5` の1テストに対して `return 5` ではなく `return a+b` を実装
- stack cycle-2: `Push→IsEmpty==false` に対してスライス全実装

**P3との複合**: GREEN フェーズで追加テストを先に書いてから Obvious Implementation で
一気に通すパターンが観察された（calculator cycle-1）。Fake It → Triangulation の
プロセスが迂回される。

**影響**: テストが検証していない動作まで実装が先行するリスク。

**再現**: iteration-2 stack-go（サイクル2〜）、calculator-go（全サイクル）。

---

## P7: 実装を後追いするテストを書く（チート）

**発見方法**: iteration-2 calculator-go の RED スナップショットでテスト関数の出現タイミングを追跡

**現象**: `TestAdd_handlesNegativeNumbers` は cycle-1-green で `return a+b` の実装と同時に追加された。
この時点で実装はすでに `Add(-4,7)=3` をパスするため、このテストは一度も RED にならなかった。
実装を通すためのテストであり、テストで実装を駆動するという TDD の根本原則に反する。

| サイクル | テスト状態 |
|---|---|
| cycle-1-red | 存在しない（まだ書かれていない）|
| cycle-1-green | `return a+b` と同時に追加 → 書いた瞬間からパス |
| cycle-2-red 以降 | 存在するが Add は常に PASS |

**P3との関係**: GREEN フェーズでテストを追加する（P3）が発生すると、
実装が先行しているためチートが生まれやすい構造になる。

**再現**: iteration-2 calculator-go（`TestAdd_handlesNegativeNumbers`）。

---

## P11: RED フェーズでテストが実際に失敗していない

**発見方法**: RED スナップショットの `test_output.txt` を確認

**現象**: RED フェーズでは「失敗するテストを書く」ことが必須だが、
テストを書いた時点ですでにパスしている場合がある。
例: 既存の実装が偶然カバーしているケースのテストを書く、
または never-fail なアサーション（`if false`）を書いてしまう。

**影響**: テストが仕様を駆動しておらず、RED→GREEN の因果関係が成立しない。
「テストが RED にならない RED フェーズ」は TDD の根本を崩す。

**判定方法**: `cycle-N-red/test_output.txt` に FAIL または build error が含まれるか

**行動分類**: 無視 / 誤解

---

## P4: Triangulation で RED を踏まずに GREEN→GREEN が発生する

**発見方法**: iteration-2 fizzbuzz-go の history.log で PHASE=green が cycle-4 に2回記録されている

**現象**: Fake It の後、Triangulation（より一般的な実装への置き換え）を行う際に、
新たな RED（失敗テスト）を書かずに GREEN を2回書いている。
サイクル数とコミット数が一致しなくなり（REDスナップ4件に対してfeat:コミット5件）、
スナップショットの cycle-N の番号が実際のコミット履歴とずれる。

**再現**: iteration-2 fizzbuzz-go のサイクル4（`feat: 数値文字列変換をstrconv.Itoa` が REDなしで追加）。

---

## P6: 言語固有のイディオムが REFACTOR で採用されない

**発見方法**: iteration-2 の *_test.go を確認

**現象**: Go では複数のテストケースを Table-Driven Test にまとめるのが推奨イディオムだが、
エージェントは REFACTOR フェーズでこの構造を採用しなかった。各テストケースが独立した
関数として残り続けている。

```go
// エージェントが書いたスタイル（個別関数）
func TestFizzBuzz_returns_1_for_1(t *testing.T) { ... }
func TestFizzBuzz_returns_Fizz_for_3(t *testing.T) { ... }

// Go イディオムとして推奨されるスタイル（Table-Driven）
func TestFizzBuzz(t *testing.T) {
    tests := []struct{ n int; want string }{
        {1, "1"}, {3, "Fizz"}, {5, "Buzz"}, {15, "FizzBuzz"},
    }
    for _, tt := range tests {
        t.Run(fmt.Sprintf("%d", tt.n), func(t *testing.T) {
            if got := FizzBuzz(tt.n); got != tt.want {
                t.Errorf("got %q, want %q", got, tt.want)
            }
        })
    }
}
```

**背景**: TDD スキルは Go に限らず一般言語を対象としているため、言語固有のお作法が
スキルに含まれていない。言語別の規約をどこかに記述する仕組みが必要。

**影響**: 生成されるテストコードが言語コミュニティの標準から外れる。
Table-Driven にしておくと Triangulation でテストケースを追加しやすくなる副次効果もある。

---

## P8: timing.json がエージェント自身では保存できない

**発見方法**: iteration-2 実行後に timing.json が存在しないことを確認

**現象**: run_spec.md には「timing.json はエージェント完了通知に含まれる total_tokens と
duration_ms から即座に保存すること」と記載されているが、完了通知はオーケストレーター側に
届く情報であり、サブエージェント自身はアクセスできない。

**影響**: トークン数・ツール呼び出し数・実行時間はスキルの効率を測る重要な指標だが、
現状は手動で拾わない限り記録されない。

**対策**: オーケストレーター（Agent ツールを呼び出す側）が完了通知の `subagent_tokens`・
`tool_uses`・`duration_ms` を読み取り、timing.json として保存する手順を run_spec.md に明記する。

---

## P9: REFACTOR の「1コミット1変更」という基準が言語化できていない

**発見方法**: iteration-2 の refactor: コミットを確認する中でユーザーが指摘

**背景**: refactor.md の「20行未満」は Kent Beck が人間向けに示した目安であり、
厳密なルールではない。関数抽出のような単純な変更は20行を超えても問題ない。
避けるべきは **「1コミットに複数の概念的変更を詰め込む」** こと。

```
NG: 変数リネーム AND メソッド抽出 を同一コミットで行う
OK: 関数抽出（23行であっても、変更の意図が1つであれば問題ない）
```

**現状の問題**: この「1コミット1変更」という基準を
refactor.md で十分に言語化できていない。現在の記述（行数制限）は
代理指標に過ぎず、本質を伝えていない。

**影響**: エージェントが複数の改善を1コミットにまとめてしまっても
現在の基準では検出できない。

**備考**: refactor: コミットの行数検証にはスナップショットではなく
`repo/` の git 履歴を直接参照する必要がある（P1 の影響）。

---

## P10: コンテキスト汚染によるスキル遵守率の低下が未検証

**背景**: 運用観察から、タスク開始直後はエージェントが TDD の作法を遵守するが、
コンテキストにスキル以外の情報（実装の試行錯誤・エラーログ・会話など）が積まれていくにつれ、
REFACTOR スキップ等の指示逸脱が増えていくことが確認されている。

**現状の評価の限界**: fizzbuzz・stack・calculator はいずれも 3〜5 サイクルで完了する
短いタスク。コンテキストが汚染される前に終わるため、後半での挙動劣化を測定できない。

**計測したいこと**: 「意図せぬ行動変更の混入割合」をサイクル位置ごとに計測する。
  - 初期サイクル（1〜3）と後期サイクル（7〜）で遵守率に差があるか
  - 何サイクル目からスキルへの準拠が崩れ始めるか

**必要な eval 設計**:
  - 10〜20 サイクルを要する複雑なタスク（例: Markdown パーサー、電卓の拡張版）
  - サイクルごとの遵守チェック項目（RED/GREEN/REFACTOR の有無・空コミット・行数）
  - 「サイクル位置 vs 遵守率」のグラフが作れるアサーション構造

---

---

## 問題の分類

行動分類の凡例:
- **無視**: 指示が明確に存在するが従っていない
- **過剰な解釈**: 指示の許可範囲を広く取りすぎて意図しない行動をする
- **誤解**: 指示の意図を間違って解釈して従っている
- **指示の欠落**: そもそも対応する指示が存在しない（エージェントの問題ではなくスキルの問題）

### Tier 1: コア指標（毎イテレーション計測・長期追跡）

| 問題 | 指標名 | 定義 | 行動分類 |
|---|---|---|---|
| P11 | `red_authenticity_rate` | FAILを記録したREDスナップ数 ÷ 総REDスナップ数 | 無視 / 誤解 |
| P1 | `phase_write_order_rate` | git_diffに.go変更を含む(GREEN+REFACTOR)スナップ数 ÷ 総(GREEN+REFACTOR)スナップ数 | 無視 |
| P4 | `red_preceded_green_rate` | 直前に同サイクルのREDがあるGREEN数 ÷ 総GREEN数（history.log） | 誤解 |
| P3 | `green_phase_purity` | テスト追加のなかったGREENスナップ数 ÷ 総GREENスナップ数 | 誤解 / 無視 |
| P2 | `refactor_noop_rate` | 空のrefactor:コミット数 ÷ 全refactor:コミット数 | 過剰な解釈 / 誤解 |
| P7 | `test_first_rate` | REDでFAILしたことのあるテスト関数数 ÷ 総テスト関数数 | 無視 |

### Tier 2: 補助指標（余裕があれば計測）

| 問題 | 指標名 | 定義 | 備考 |
|---|---|---|---|
| P6 | `language_idiom_rate` | 言語イディオムを採用しているか（Go: Table-Driven） | pass/fail |
| P5 | `fake_it_rate` | GREENの実装が最小限か（LLM採点） | **P1解決が前提条件** |

### Tier 3: 効率指標

| 問題 | 指標名 | 定義 |
|---|---|---|
| P8 | `tokens_per_cycle` | 総トークン数 ÷ 総サイクル数 |
| P8 | `tool_calls_per_cycle` | 総ツール呼び出し数 ÷ 総サイクル数 |

### 指標化を保留

| 問題 | 理由 |
|---|---|
| P9: 1コミット1変更 | 「1変更」の定義が未確立。定義が固まり次第追加する |
| P10: サイクル後半の遵守率 | 長いタスク（10サイクル以上）が必要。eval設計が整い次第追加する |

---

## 未解決の設計課題

- P1 の根本対策: `scripts/tdd-commit.sh` ラッパー方式で対応済み。
- P6 の対策: `~/.claude/rules/` にパス指定ルールとして記述する。Go なら `paths: "**/*_test.go"` で
  Table-Driven Test 等のイディオムを定義。他言語も `*.spec.ts`、`*_test.py` 等で同様に追加可能。
  ユーザーレベルに置けば全プロジェクトで有効。
