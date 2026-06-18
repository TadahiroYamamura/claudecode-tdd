# gopls MCP 利用ガイド

参考: https://go.dev/gopls/features/mcp

## インストール

```bash
go install golang.org/x/tools/gopls@latest
```

## 起動モード

### デタッチモード（headless / stdio）

```bash
gopls mcp
```

LSP クライアント不要でスタンドアロン動作する。stdin/stdout 経由の MCP サーバーとして機能する。ディスク上に保存済みのファイルのみを認識する。

### アタッチモード（エディタ連携）

```bash
gopls serve -mcp.listen=localhost:8092
```

エディタの LSP セッションに相乗りする形で HTTP/SSE 起動する。未保存バッファも認識できる。エディタが起動している必要がある。

TDD スキルでの利用はデタッチモードで十分。

## Claude Code への登録

```bash
claude mcp add gopls -- gopls mcp
```

登録確認:

```bash
claude mcp list
claude mcp get gopls
```

## モノレポ（マルチモジュール構成）での登録

`gopls mcp` は起動時のカレントディレクトリを workspace として認識する。`claude mcp add` に `--cwd` オプションがないため、シェルラッパーで `cd` してから起動する。

```bash
claude mcp add gopls-<module-name> \
  --scope project \
  -- bash -c 'cd /path/to/module && gopls mcp'
```

- `--scope project` により設定はそのディレクトリの `.claude/settings.json` に書き込まれ、プロジェクト内でのみ有効になる
- モジュールごとに別名で登録することで複数モジュールを並立できる

例（`api-gateway` と `auth-service` を個別登録する場合）:

```bash
# api-gateway ディレクトリで実行
claude mcp add gopls-api-gateway --scope project \
  -- bash -c 'cd ~/work/myapp/api-gateway && gopls mcp'

# auth-service ディレクトリで実行
claude mcp add gopls-auth-service --scope project \
  -- bash -c 'cd ~/work/myapp/auth-service && gopls mcp'
```

## モデル命令（コンテキストファイル）の取得

```bash
gopls mcp -instructions > gopls_instructions.md
```

AI アシスタントにコンテキストとして追加できる。

## TDD スキルでの活用方針

| フェーズ | 活用するツール | 目的 |
|---|---|---|
| RED | `diagnostics` | 存在しないメソッド・型を参照するテストを書いた際にコンパイルエラーを即確認 |
| GREEN | `definition` / `references` | 既存コードの構造を正確に把握してから実装（憶測による誤実装の抑制） |
| REFACTOR | `rename` | 安全なシンボルリネーム |
