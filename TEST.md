# TEST.md — OpenClaw App Company テストケース定義

- 対象: SPEC.md v0.9 / CLASS.md / SEQUENCE.md
- 作成日: 2026-03-23
- 方針: TDD（テストファースト）。実装前にこのテストケースを受け入れ条件として確認する

---

## テスト方針

| 項目 | 方針 |
|-----|------|
| テストフレームワーク | pytest（予定。Q58 で確認） |
| ファイルI/O | `tmp_path` フィクスチャで一時ディレクトリを使う |
| 外部CGI | MVP ではモック。実サーバーへのリクエストは手動確認（Q59 で確認） |
| カバレッジ目標 | `scripts/` 配下の主要パスを網羅。Codex CLI 生成コードは対象外 |
| テスト配置 | `tests/` ディレクトリ（未作成。Phase 0 成果物に追加候補） |

---

## TC-01: `run_phase()` ヘルパー

### TC-01-01 正常終了（return）

| 項目 | 内容 |
|-----|------|
| 対象 | `run_phase(name, fn)` |
| 前提 | `fn` が正常に `return` する |
| 操作 | `run_phase("dummy", lambda: None)` |
| 期待結果 | `True` が返る |

### TC-01-02 正常終了（SystemExit(0)）

| 項目 | 内容 |
|-----|------|
| 前提 | `fn` が `raise SystemExit(0)` する |
| 操作 | `run_phase("dummy", lambda: (_ for _ in ()).throw(SystemExit(0)))` |
| 期待結果 | `True` が返る（新規なし扱い） |

### TC-01-03 異常終了（SystemExit(1)）

| 項目 | 内容 |
|-----|------|
| 前提 | `fn` が `raise SystemExit(1)` する |
| 操作 | `run_phase("dummy", fn_that_exits_1)` |
| 期待結果 | `False` が返る |

### TC-01-04 未捕捉例外

| 項目 | 内容 |
|-----|------|
| 前提 | `fn` が `raise RuntimeError("unexpected")` する |
| 操作 | `run_phase("dummy", fn_that_raises)` |
| 期待結果 | `False` が返る（例外を外に伝播させない） |

### TC-01-05 失敗時に後続スキップ

| 項目 | 内容 |
|-----|------|
| 前提 | Phase A が `False` を返す |
| 操作 | `main()` でフェーズ A → B → C を連続実行 |
| 期待結果 | Phase B・C は実行されず `sys.exit(1)` で終了する |

---

## TC-02: `CompanyState` の読み書き

### TC-02-01 正常読み込み

| 項目 | 内容 |
|-----|------|
| 前提 | `state/company_state.json` が有効な JSON で存在する |
| 操作 | `CompanyState.load(path)` |
| 期待結果 | `current_phase`・`quality_gate` 等が正しく読み込まれる |

### TC-02-02 ファイル不在

| 項目 | 内容 |
|-----|------|
| 前提 | `state/company_state.json` が存在しない |
| 操作 | `CompanyState.load(path)` |
| 期待結果 | `FileNotFoundError` または初期値を返す（実装依存。Q58 で確認） |

### TC-02-03 保存と再読み込みの一致

| 項目 | 内容 |
|-----|------|
| 操作 | `state.save(path)` → `CompanyState.load(path)` |
| 期待結果 | 保存前と再読み込み後の全フィールドが一致する |

### TC-02-04 フェーズ失敗時の状態保持

| 項目 | 内容 |
|-----|------|
| 前提 | `current_phase = "implementation"` の状態でフェーズ失敗 |
| 操作 | `main.py` が失敗を検知して `next_action` を記録して保存 |
| 期待結果 | `current_phase` は `"implementation"` のまま。`next_action` に修正内容が記録されている |

### TC-02-05 `QualityGate` フラグの初期値

| 項目 | 内容 |
|-----|------|
| 前提 | 新規作成された `company_state.json` |
| 期待結果 | `quality_gate` の全フラグが `false` |

---

## TC-03: `AgentsYaml` の読み込みと検索

### TC-03-01 正常読み込み

| 項目 | 内容 |
|-----|------|
| 前提 | 有効な `agents/agents.yaml` が存在する |
| 操作 | `AgentsYaml.load(path)` |
| 期待結果 | 30体分の `AgentMeta` が読み込まれる |

### TC-03-02 ID による検索

| 項目 | 内容 |
|-----|------|
| 操作 | `agents_yaml.find("market_researcher")` |
| 期待結果 | `id="market_researcher"` の `AgentMeta` が返る |

### TC-03-03 存在しない ID の検索

| 項目 | 内容 |
|-----|------|
| 操作 | `agents_yaml.find("nonexistent_agent")` |
| 期待結果 | `None` または `KeyError` が返る |

### TC-03-04 inputs/outputs の取得

| 項目 | 内容 |
|-----|------|
| 操作 | `agents_yaml.find("ceo").inputs` |
| 期待結果 | `["artifacts/research/scored_ideas.md", "artifacts/product/prd.md"]` が返る |

---

## TC-04: エージェント基底規約

### TC-04-01 `main()` が存在する

| 項目 | 内容 |
|-----|------|
| 対象 | 全30エージェントモジュール |
| 操作 | `hasattr(module, "main")` |
| 期待結果 | 全モジュールで `True` |

### TC-04-02 正常終了が `return` / `SystemExit(0)`

| 項目 | 内容 |
|-----|------|
| 前提 | 正常入力ファイルが存在する |
| 操作 | `run_phase("xxx", agent.main)` |
| 期待結果 | `True` が返る（`SystemExit(1)` を送出しない） |

### TC-04-03 入力ファイル不在で `SystemExit(1)`

| 項目 | 内容 |
|-----|------|
| 前提 | 必須入力ファイルが存在しない |
| 操作 | `agent.main()` |
| 期待結果 | `SystemExit(1)` が送出される |

### TC-04-04 ログファイルが生成される

| 項目 | 内容 |
|-----|------|
| 操作 | `agent.main()` 実行後 |
| 期待結果 | `logs/agent-name-YYYY-MM-DD.log` が生成されている |

### TC-04-05 作業ディレクトリがリポジトリルート

| 項目 | 内容 |
|-----|------|
| 操作 | エージェントを `scripts/agents/` から直接実行 |
| 期待結果 | `os.getcwd()` がリポジトリルートと一致する |

---

## TC-05: `Market Researcher`（Phase 1）

### TC-05-01 出力ファイルが生成される

| 項目 | 内容 |
|-----|------|
| 前提 | `docs/roadmap.md` が存在する（空でもよい） |
| 操作 | `market_researcher.main()` |
| 期待結果 | `artifacts/research/research_report.md` が生成される |

### TC-05-02 `source_notes.md` が生成される

| 項目 | 内容 |
|-----|------|
| 操作 | `market_researcher.main()` 実行後 |
| 期待結果 | `artifacts/research/source_notes.md` が生成される |

### TC-05-03 `idea_pool.md` が 10 件以上の候補を含む

| 項目 | 内容 |
|-----|------|
| 前提 | `research_report.md` が存在する |
| 操作 | `idea_scorer.main()` 実行後に `scored_ideas.md` を読む |
| 期待結果 | 候補10件以上が記録されている |

---

## TC-06: `CommissionDoc`（Phase 8）

### TC-06-01 委任書が正しいヘッダを持つ

| 項目 | 内容 |
|-----|------|
| 前提 | `artifacts/design/tasks.md` が存在する |
| 操作 | `codex_prompt_writer.main()` |
| 期待結果 | `artifacts/prompts/task-001.md` が生成され、冒頭に `Status: Draft for Codex CLI` を含む |

### TC-06-02 必須セクションが存在する

| 項目 | 内容 |
|-----|------|
| 操作 | 生成された `task-001.md` を読む |
| 期待結果 | `## 1. 目的` `## 2. スコープ` `## 4. 入出力` `## 8. 完了条件` が存在する |

### TC-06-03 `runtime_mode` が記載されている

| 項目 | 内容 |
|-----|------|
| 操作 | `task-001.md` を読む |
| 期待結果 | `runtime_mode: static / toolbox / db` のいずれかが記載されている |

### TC-06-04 タスク数分のファイルが生成される

| 項目 | 内容 |
|-----|------|
| 前提 | `tasks.md` に3件のタスクが定義されている |
| 操作 | `codex_prompt_writer.main()` |
| 期待結果 | `task-001.md`・`task-002.md`・`task-003.md` が生成される |

---

## TC-07: `AppSpec` の生成と検証

### TC-07-01 テンプレートから生成される

| 項目 | 内容 |
|-----|------|
| 操作 | `create-app-template.py` でアプリを生成 |
| 期待結果 | `apps/app-xxx-name/spec.md` が生成され、Section 22 の必須項目を含む |

### TC-07-02 `adsense_required: true` がデフォルト

| 項目 | 内容 |
|-----|------|
| 操作 | 生成された `spec.md` を読む |
| 期待結果 | `adsense_required: true` が含まれる |

### TC-07-03 `adsense_required: false` には `adsense_exception_reason` が必須

| 項目 | 内容 |
|-----|------|
| 前提 | `spec.md` に `adsense_required: false` が設定されている |
| 操作 | `spec.md` を検証スクリプトで読む |
| 期待結果 | `adsense_exception_reason` が存在しない場合は検証エラーになる |

### TC-07-04 `visitor_tracking: false` には `visitor_tracking_reason` が必須

| 項目 | 内容 |
|-----|------|
| 前提 | `spec.md` に `visitor_tracking: false` が設定されている |
| 期待結果 | `visitor_tracking_reason` が存在しない場合は検証エラーになる |

---

## TC-08: API 疎通確認（Phase 6）

### TC-08-01 採用済み CGI の全件確認を要求する

| 項目 | 内容 |
|-----|------|
| 前提 | `api_endpoints: ["visitor.cgi", "uuid.cgi"]` が設定されている |
| 操作 | `sakura_api_coordinator.main()` |
| 期待結果 | `api_connectivity_report.md` に `visitor.cgi` と `uuid.cgi` の両方の確認結果が記録される |

### TC-08-02 一件でもエラーなら NG 記録

| 項目 | 内容 |
|-----|------|
| 前提 | `visitor.cgi` は正常、`uuid.cgi` が 5xx を返す |
| 期待結果 | `api_connectivity_report.md` に NG が記録され、`SystemExit(1)` が送出される |

### TC-08-03 `runtime_mode: static` では実施不要

| 項目 | 内容 |
|-----|------|
| 前提 | `company_state.json` の `runtime_mode = "static"` |
| 操作 | `main.py` が Phase 6 をスキップするか確認 |
| 期待結果 | Phase 6 が実行されず Phase 8 に進む |

### TC-08-04 `runtime_mode: db` では `db.cgi` 基本応答も確認

| 項目 | 内容 |
|-----|------|
| 前提 | `runtime_mode = "db"` |
| 操作 | Phase 6 実行 |
| 期待結果 | `api_connectivity_report.md` に `db.cgi` の基本応答確認結果が含まれる |

---

## TC-09: DB 接続確認（Phase 7）

### TC-09-01 `select` テストが記録される

| 項目 | 内容 |
|-----|------|
| 前提 | `runtime_mode = "db"`、テスト用 DB が存在する |
| 操作 | Phase 7 実行（ローカルサーバー上） |
| 期待結果 | `db_connectivity_report.md` に `select` テストの結果が記録される |

### TC-09-02 `insert` → `count` で件数増加を確認

| 項目 | 内容 |
|-----|------|
| 操作 | `insert` → `count` の順でテスト |
| 期待結果 | `count` の結果が `insert` 前より 1 増加している |

### TC-09-03 エラー系テストが記録される

| 項目 | 内容 |
|-----|------|
| 操作 | 不正なパラメータで `db.cgi` を呼ぶ |
| 期待結果 | エラー JSON が返り、`db_connectivity_report.md` にエラー系結果が記録される |

### TC-09-04 `runtime_mode: toolbox` では Phase 7 をスキップ

| 項目 | 内容 |
|-----|------|
| 前提 | `runtime_mode = "toolbox"` |
| 期待結果 | Phase 7 が実行されず Phase 8 に進む |

---

## TC-10: `QualityGate` の更新

### TC-10-01 Phase 6 完了後に `ssl_verified`・`cors_verified` が `true`

| 項目 | 内容 |
|-----|------|
| 前提 | API 疎通確認が全件 OK |
| 操作 | Phase 6 正常完了後に `company_state.json` を読む |
| 期待結果 | `quality_gate.ssl_verified = true`、`quality_gate.cors_verified = true` |

### TC-10-02 Phase 10 完了後に `browser_test_passed` が `true`

| 項目 | 内容 |
|-----|------|
| 前提 | `browser_test_report.md` にすべて PASS が記録されている |
| 操作 | Phase 10 正常完了後に `company_state.json` を読む |
| 期待結果 | `quality_gate.browser_test_passed = true` |

### TC-10-03 エージェントは `company_state.json` を直接書き換えない

| 項目 | 内容 |
|-----|------|
| 操作 | 任意エージェントの `main()` 実行中に `company_state.json` を監視する |
| 期待結果 | エージェント実行中に `company_state.json` が更新されない |

---

## TC-11: AdSense ゲート（Phase 11）

### TC-11-01 収益対象ページに AdSense タグがなければ Release NG

| 項目 | 内容 |
|-----|------|
| 前提 | `apps/app-001-sample/index.html` に AdSense タグが含まれない |
| 操作 | `github_pages_release_manager.main()` |
| 期待結果 | `SystemExit(1)` が送出される / `deploy_report.md` に NG が記録される |

### TC-11-02 AdSense タグが存在すれば Release OK に進む

| 項目 | 内容 |
|-----|------|
| 前提 | ルート `index.html` と各アプリ `index.html` の両方に `ca-pub-6743751614716161` を含む |
| 期待結果 | `quality_gate.adsense_verified = true` に更新される |

### TC-11-03 テストページへの AdSense 混入を検出する

| 項目 | 内容 |
|-----|------|
| 前提 | `test-api.html` に誤って AdSense タグが混入している |
| 期待結果 | `quality_gate.test_pages_adsense_clean = false` / Release NG |

### TC-11-04 AdSense タグ埋め込みでレイアウト崩れがあれば NG

| 項目 | 内容 |
|-----|------|
| 前提 | `design_review.md` にレイアウト崩れが記録されている |
| 期待結果 | `release_gate_passed = false` |

### TC-11-05 `create-app-template.py` が AdSense タグを自動挿入する

| 項目 | 内容 |
|-----|------|
| 操作 | `create-app-template.py` で新規アプリを生成 |
| 期待結果 | 生成された `index.html` の `<head>` に AdSense スクリプトタグが含まれる |

### TC-11-06 `build-index.py` がルートページに AdSense タグを挿入する

| 項目 | 内容 |
|-----|------|
| 操作 | `build-index.py` 実行後に `index.html` を確認 |
| 期待結果 | ルート `index.html` の `<head>` に AdSense スクリプトタグが含まれる |

---

## TC-12: `visitor.cgi` 呼び出し（フロントエンド）

### TC-12-01 `visitor_tracking: true` のとき呼び出しコードが生成される

| 項目 | 内容 |
|-----|------|
| 前提 | `spec.md` に `visitor_tracking: true` |
| 操作 | `create-app-template.py` でアプリを生成 |
| 期待結果 | `app.js` または `api.js` に `visitor.cgi` への `fetch()` コードが含まれる |

### TC-12-02 `visitor_tracking: false` のとき呼び出しコードが生成されない

| 項目 | 内容 |
|-----|------|
| 前提 | `spec.md` に `visitor_tracking: false`、`visitor_tracking_reason` が記載されている |
| 期待結果 | 生成されたコードに `visitor.cgi` の `fetch()` が含まれない（またはコメントアウト） |

### TC-12-03 `fetch()` の失敗がアプリ本体を止めない

| 項目 | 内容 |
|-----|------|
| 操作 | `visitor.cgi` がタイムアウトする状況でページを開く |
| 期待結果 | アプリ本体の機能（変換・メモ等）は正常に動作する |

### TC-12-04 `DOMContentLoaded` で発火する

| 項目 | 内容 |
|-----|------|
| 操作 | 生成された `app.js` のコードを読む |
| 期待結果 | `visitor.cgi` 呼び出しが `DOMContentLoaded` イベントハンドラ内に配置されている |

---

## TC-13: Phase 12 ループバック判断

### TC-13-01 同一アプリ改善は Phase 5 へ

| 項目 | 内容 |
|-----|------|
| 前提 | `sprint_next.md` の `loop_back_target = PHASE_5_TASK_BREAKDOWN` |
| 操作 | `improvement_strategist.main()` → COO → CEO 承認 |
| 期待結果 | `main.py` が `--phase task_breakdown` 相当で再起動するよう促す |

### TC-13-02 新規アプリ追加は Phase 1 へ

| 項目 | 内容 |
|-----|------|
| 前提 | `sprint_next.md` の `loop_back_target = PHASE_1_RESEARCH` |
| 期待結果 | `main.py` が `--phase research` 相当で再起動するよう促す |

### TC-13-03 `user_feedback.md` が生成される

| 項目 | 内容 |
|-----|------|
| 操作 | `improvement_strategist.main()` |
| 期待結果 | `artifacts/sprints/user_feedback.md` が生成される |

### TC-13-04 `usage_insights.md` が生成される

| 項目 | 内容 |
|-----|------|
| 操作 | `improvement_strategist.main()` |
| 期待結果 | `artifacts/sprints/usage_insights.md` が生成される |

---

## TC-14: `db.cgi` インターフェース

### TC-14-01 `action` は常に `"query"`

| 項目 | 内容 |
|-----|------|
| 操作 | `db.cgi` へのリクエスト JSON を生成するすべてのコードを検査 |
| 期待結果 | `"action": "query"` 以外の値が存在しない |

### TC-14-02 `operation: create_table` は `if_not_exists: true` が標準

| 項目 | 内容 |
|-----|------|
| 操作 | `create_table` リクエスト JSON を確認 |
| 期待結果 | `"if_not_exists": true` が含まれる |

### TC-14-03 `database` 名は拡張子なしの論理名

| 項目 | 内容 |
|-----|------|
| 操作 | すべての `db.cgi` 呼び出し箇所を検査 |
| 期待結果 | `"database": "app003"` のように `.sqlite` 等の拡張子が含まれない |

### TC-14-04 UPDATE / DELETE には WHERE が必須

| 項目 | 内容 |
|-----|------|
| 操作 | `update` / `delete` リクエスト JSON を検査 |
| 期待結果 | `"where"` キーが存在しないリクエストは拒否される |

---

## TC-15: アプリの Pages 公開品質

### TC-15-01 相対パスで動作する

| 項目 | 内容 |
|-----|------|
| 操作 | `file://` 直開きではなく `http://localhost:8000/apps/app-xxx/` で開く |
| 期待結果 | CSS・JS・画像のすべてが正常に読み込まれる |

### TC-15-02 サブパスで壊れない

| 項目 | 内容 |
|-----|------|
| 操作 | `https://garyohosu.github.io/openclaw-app-company/apps/app-xxx/` で開く |
| 期待結果 | 404 にならず正常に表示される |

### TC-15-03 モバイル幅で崩れない

| 項目 | 内容 |
|-----|------|
| 操作 | ブラウザ幅を 375px に変更してページを開く |
| 期待結果 | レイアウトが崩れない |

### TC-15-04 `.nojekyll` が存在する

| 項目 | 内容 |
|-----|------|
| 操作 | リポジトリルートを確認 |
| 期待結果 | `.nojekyll` ファイルが存在する |

---

## テストID 一覧

| ID | 対象 | カテゴリ |
|----|-----|---------|
| TC-01-01〜05 | `run_phase()` | 単体 |
| TC-02-01〜05 | `CompanyState` | 単体 |
| TC-03-01〜04 | `AgentsYaml` | 単体 |
| TC-04-01〜05 | エージェント基底規約 | 単体 |
| TC-05-01〜03 | Market Researcher | 単体 |
| TC-06-01〜04 | `CommissionDoc` | 単体 |
| TC-07-01〜04 | `AppSpec` | 単体 |
| TC-08-01〜04 | API 疎通確認（Phase 6） | 結合 |
| TC-09-01〜04 | DB 接続確認（Phase 7） | 結合 |
| TC-10-01〜03 | `QualityGate` 更新 | 結合 |
| TC-11-01〜06 | AdSense ゲート（Phase 11） | 結合 |
| TC-12-01〜04 | `visitor.cgi` フロント | 結合 |
| TC-13-01〜04 | Phase 12 ループバック | 結合 |
| TC-14-01〜04 | `db.cgi` インターフェース | 単体 |
| TC-15-01〜04 | Pages 公開品質 | E2E |

---

_以上。不明点は QandA.md に追記。_
