# QandA.md — SPEC.md レビュー質問集

作成日: 2026-03-23
対象: SPEC.md 補足設計回答 / 追加レビュー回答
ステータス: 全57件 回答確定 / SPEC.md v0.9 反映済み

---

## Q1. OpenClaw とは何か

**回答:**
OpenClaw は本プロジェクトの **オーケストレーション実行基盤** として定義する。外部製品名ではなく、以下の役割を持つ仕組みの総称。

- エージェント定義の読み込み
- フェーズ進行管理
- 成果物ファイルの受け渡し
- Codex CLI 実行指示の発行
- 品質ゲート判定
- 状態ファイル更新

**エージェント通信方式:** ファイルシステム経由。`artifacts/` `apps/` `docs/` `state/` 配下を共通の受け渡し面とし、エージェント同士が直接会話する前提にはしない。

**agents.yaml 最小スキーマ:**

```yaml
agents:
  - id: ceo
    name: CEO Agent
    role: executive
    responsibilities:
      - approve_product_direction
      - approve_release
    inputs:
      - artifacts/research/scored_ideas.md
      - artifacts/product/prd.md
    outputs:
      - artifacts/executive/decision.md
    can_run:
      - review
      - approve
    human_approval_required: false
```

---

## Q2. Codex CLI の具体的な利用方法

**回答:**
- 対象は OpenAI の `codex` CLI（バージョン・モデルはSPECで固定しない。その時点で利用可能な安定版を使う）
- 委任文は `artifacts/prompts/task-xxx.md` としてファイル生成し、Codex CLI に渡す
- プロンプトはファイル保存。実行ログも保存

**採否フロー:**
1. 一次判定: Tech Lead Agent
2. 品質判定: TDD Enforcer / Bug Triage Agent / Browser Test Operator
3. 最終採用: COO Agent または Release Manager

Codex CLI は実装者であって決裁者ではない。

---

## Q3. Sakura CGI API Toolbox のベース URL

**回答:**
SPEC ではベース URL を固定文字列で埋め込まない。各アプリの `api.js` または `config.js` に集約管理する。

```javascript
const API_CONFIG = {
  baseUrl: "https://your-sakura-domain.example/api",
  endpoints: {
    now:      "/now.cgi",
    uuid:     "/uuid.cgi",
    validate: "/validate.cgi",
    convert:  "/convert.cgi",
    visitor:  "/visitor.cgi",
    db:       "/db.cgi"
  }
};
```

環境は production / local-test の2系統。GitHub Pages 本番から呼ぶ URL は本番固定。開発時は `test-api.html` で個別確認。

---

## Q4. `db.cgi` の認証・認可

**回答:**
MVP段階では `db.cgi` は公開書き込みを前提にしない。

- 原則として読み取り中心
- 書き込み系（insert / update / delete）は限定用途のみ
- 公開アプリで誰でも叩ける更新系は原則禁止
- 更新系を使う場合は別途認証または制限設計が必要

DB 名・テーブル名のホワイトリストは `db.cgi` 側で管理する。フロント側の制約だけにはしない。

---

## Q5. `create_table` オペレーションの仕様

**回答:**
`create_table` は MVP では運用初期化用とし、日常のアプリ操作からは呼ばない。

```json
{
  "action": "database",
  "database": "app003",
  "operation": "create_table",
  "table": "items",
  "schema": {
    "id":         "TEXT PRIMARY KEY",
    "title":      "TEXT NOT NULL",
    "created_at": "TEXT NOT NULL"
  },
  "if_not_exists": true
}
```

- `if_not_exists: true` を標準とする
- 既存テーブルがある場合はスキップ成功
- 強制再作成は MVP 範囲外

---

## Q6. `state/` ディレクトリがリポジトリ構成から欠落

**回答:**
`state/` はリポジトリ構成に含める。

| ファイル | Git 管理 |
|---------|---------|
| `state/schema.md` | ○ コミット対象 |
| `state/example-company_state.json` | ○ コミット対象 |
| `state/company_state.json`（実行中） | × `.gitignore` |

ひな形はコミット対象、実行状態は `.gitignore` に追加する。

---

## Q7. 各フェーズのトリガーと進行管理

**回答:**
MVP では **人間トリガー + OpenClaw 補助進行** とする。

1. 人間が Phase 開始を指示
2. OpenClaw が成果物確認と次工程候補を出す
3. 人間が go を出して次へ進む

**失敗時の対応（差し戻し方式）:**

- `artifacts/sprints/sprint-xx/failure_report.md` を作成
- `next_action` を state に記録
- 前フェーズ成果物は保持
- 修正後に同一フェーズ再実行

---

## Q8. `deploy.yml` の内容と GitHub Pages のトリガー

**回答:**
- `deploy.yml` は MVP に含める（現時点未作成）
- 担当: Release Manager + Codex Prompt Writer が作成
- トリガー: `main` への push で Pages 更新（初期は GitHub Pages 標準公開でも可）
- `index.html` は `build-index.py` で生成する方針（MVP に含める）

---

## Q9. `scripts/` 内スクリプトは既存か未作成か

**回答:**
現時点では未作成前提。MVP に含める。

| スクリプト | 仕様 | 実装 | レビュー |
|-----------|-----|------|---------|
| `create-app-template.py` | Tech Lead Agent | Codex CLI | COO Agent |
| `build-index.py` | Tech Lead Agent | Codex CLI | Browser Test Operator |

---

## Q10. `validate.cgi` と `convert.cgi` の対応範囲

**回答:**
- `validate.cgi`: JSON Schema バージョンは MVP では固定しない。CGI 側 README に対応バージョンを明記する。アプリ側は `test-api.html` で利用前確認を必須とする
- `convert.cgi`: 変換種類の一覧は API 側仕様書に明記必須。現時点での対応候補: 長さ / 重さ / 温度 / 面積 / 体積。実装済み範囲のみを明記する

---

## Q11. `visitor.cgi` のデータ構造

**回答:**

**visit リクエスト例:**
```json
{
  "action": "visit",
  "app_id": "app-001-idea-board",
  "page": "/apps/app-001-idea-board/",
  "referrer": "direct",
  "timestamp": "2026-03-23T10:00:00Z"
}
```

**stats レスポンス例:**
```json
{
  "status": "ok",
  "app_id": "app-001-idea-board",
  "total_visits": 120,
  "countries": [
    {"code": "JP", "count": 80},
    {"code": "US", "count": 20}
  ],
  "hourly": [
    {"hour": "09", "count": 5},
    {"hour": "10", "count": 9}
  ]
}
```

永続ストレージ実装は API 側責務とし、フロントからは隠蔽する。

---

## Q12. エージェント間の成果物受け渡し方法

**回答:**
基本は **Git リポジトリ内ファイル経由** で統一。

- MVP では本格並列実行はやらず、原則逐次実行
- 1成果物1担当
- 別担当が触る場合は `handoff.md` または更新ログを残す

---

## Q13. セキュリティ審査の担当エージェント

**回答:**

| 審査段階 | 担当 |
|---------|-----|
| 一次審査 | API Integration Architect |
| 二次審査 | Sakura API Coordinator |
| 最終承認 | COO Agent |

記録場所:
- `artifacts/security/security_review.md`
- 設計変更は `artifacts/design/adr/` にも記録

---

## Q14. `shared/` ディレクトリの利用方針

**回答:**
MVP では控えめにスタート。初期対象:

- `shared/styles/base.css`
- `shared/utils/fetch-json.js`
- `shared/utils/date-format.js`

**サブパス対策:** 各アプリから `../../shared/...` で相対参照。共有物が重い場合は各アプリへ複製も許容。最初から立派な社内共通基盤を作りすぎない。

---

## Q15. アプリ番号の採番ルール

**回答:**
`app-xxx-name` の `xxx` は **3桁連番**。

- 新規作成時に次番号を採番
- 廃止しても **欠番維持**（再利用しない）
- 理由: URL・ログ参照の安定性、過去記録との混同防止

---

_既存15件 回答確定。SPEC.md v0.2 へ反映済み。_

---

## 2026-03-23 v0.3 レビュー追補回答（回答確定）

## Q16. `artifacts/prompts/` と `artifacts/security/` は正式なリポジトリ構成に含めるか

**回答:**
含める。正式ディレクトリとして固定してよい。

**正式な `artifacts/` 配下:**

- `artifacts/research/`
- `artifacts/product/`
- `artifacts/design/`
- `artifacts/qa/`
- `artifacts/security/`
- `artifacts/prompts/`
- `artifacts/sprints/`
- `artifacts/executive/`

**理由:**

- `prompts/` は Codex CLI 委任文の保存先として実運用上必須
- `security/` はセキュリティ審査記録の保管先として必須
- ディレクトリが仕様で固定されていれば、テンプレート生成や補助スクリプトで前提化しやすい

**補足:** 空ディレクトリ維持が必要なら `.gitkeep` を置いてよい。

---

## Q17. `agents/agents.yaml` と `scripts/main.py` の関係はどう定義するか

**回答:**
役割を分ける。

- `agents/agents.yaml`: エージェント台帳兼メタデータ定義
- `scripts/main.py`: 実行順序と状態遷移の唯一の制御点

`main.py` は `agents.yaml` を読んでよいが、`agents.yaml` だけで実行順を自動決定しない。`agents.yaml` は「誰が何を担当し、何を入力・出力するか」を表し、実行順序の正本は `main.py` が持つ。

**対応規則:**

- `id: market_researcher`
- 実装ファイル: `scripts/agents/market_researcher.py`

この `id = 実装ファイル名` を標準規則にする。`default_phases` のような補助項目は追加してよいが、フェーズ定義の正本は `main.py` とする。

---

## Q18. Codex CLI 委任書の `Status: Draft for Claude Code` は意図した表記か

**回答:**
修正対象。`Claude Code` は歴史的経緯の残骸として扱い、`Draft for Codex CLI` に統一する。

**正式表記:**

```text
Status: Draft for Codex CLI
```

**理由:**

- 本仕様では実装担当を Codex CLI に統一済み
- 委任文テンプレートと実体がずれると後から読む人が混乱する
- 自動生成テンプレートにもそのまま影響する

**互換方針:** 旧テンプレートが残っていても、v0.3 以降は非推奨とする。

---

## Q19. Phase 8 の成果物は `runtime_mode` に応じて条件付きか

**回答:**
条件付き。常時出力ではなく、`runtime_mode` に応じて生成対象を切り替える。

**`runtime_mode: static`**

必須:

- `index.html`
- `style.css`
- `app.js`
- `README.md`
- `spec.md`

不要:

- `api.js`
- `test-api.html`
- `test-db-readonly.html`
- `admin-db-test.html`

**`runtime_mode: toolbox`**

必須:

- `api.js`
- `test-api.html`

通常不要:

- `test-db-readonly.html`
- `admin-db-test.html`

**`runtime_mode: db`**

必須:

- `api.js`
- `test-api.html`
- `test-db-readonly.html`（公開する場合）

必要時のみ:

- `admin-db-test.html` またはローカル専用確認ページ

**結論:** Phase 8 の成果物一覧は条件付き表記へ修正する。

---

## Q20. `test-db.html` を GitHub Pages 本番へ公開してよいか

**回答:**
原則として、そのまま一般公開しない。本番公開対象に含める場合も read only 限定にする。

**正式方針:**

- 書き込み確認ページはデフォルトで非公開運用
- 公開する場合は読み取り確認専用
- 書き込み系確認は本番公開ページで行わない

**推奨運用:**

- `test-db-readonly.html`
- `admin-db-test.html` またはローカル専用確認ページ

**理由:**

- MVPでは公開書き込みを前提にしない
- 書き込み疎通UIを第三者へ見せるのは設計意図と矛盾する

**結論:** ルート一覧ページに出すのは原則として本体ページ、`test-api.html`、必要時の `test-db-readonly.html` までとする。

---

## Q21. DB の受け入れテスト範囲は `CRUD` か `select/insert/count` か

**回答:**
MVP 合格条件は `select` / `insert` / `count` / エラー系確認を必須にする。`update` / `delete` は API として存在しても、MVP の受け入れ必須にはしない。

**MVP 必須:**

- `select`
- `insert`
- `count`
- エラー系確認

**MVP 任意:**

- `update`
- `delete`

**理由:**

- 公開更新系は原則禁止という方針と整合する
- 最小限の永続化確認としては `insert -> select -> count` で十分
- `update` / `delete` を必須にすると保護設計まで一気に重くなる

**補足:** 管理用または認証付きアプリでは、ADR で明記した上で `update` / `delete` テストを追加してよい。

---

## Q22. `local-test` 環境の CORS / 疎通確認方法は何を正式手順にするか

**回答:**
正式手順は `http://localhost:xxxx` でのローカルHTTPサーバー起動にする。`file://` 直開きは正式手順にしない。

**正式手順:**

- ローカルで簡易HTTPサーバーを起動する
- 例: `python -m http.server 8000`
- `http://localhost:8000/...` で `test-api.html` を確認する

**CORS方針:**

- `https://garyohosu.github.io`
- `http://localhost:8000`

を必要に応じて許可する。

**非推奨:**

- `file://` 直開き

再現性が低く、CORS確認手順として不安定なため。

---

## Q23. `database` パラメータの命名規則は拡張子あり/なしのどちらか

**回答:**
論理名を渡す方式に統一する。フロントからは拡張子なしを渡す。

**正式ルール:**

- フロント送信: `"database": "app003"`
- サーバー内部対応: `app003 -> app003.sqlite`

**理由:**

- 実ファイル名をフロントへ露出しない
- ホワイトリスト管理しやすい
- 将来 SQLite 以外へ変えてもフロント仕様を変えずに済む

**命名規則:**

- DB論理名: `app003`
- アプリID: `app-003-name`
- 対応規則: `app-003-name -> app003`

**結論:** `create_table` 例の `"app003.sqlite"` は v0.3 で `"app003"` に修正する。

---

## Q24. `state/company_state.json` の `current_phase` はどの値を正とするか

**回答:**
英語識別子を正とする。番号は補助情報として持ってよいが、`current_phase` 自体は識別子方式に統一する。

**正式方針:**

- `current_phase: "implementation"` のような英語識別子
- 必要なら補助で `current_phase_number: 8`

**理由:**

- フェーズ番号は将来ずれやすい
- 名前のほうが可読性が高い
- ログやレビュー文書でも扱いやすい

**追加事項:** enum は `state/schema.md` に固定定義する。

---

## Q25. `scripts/main.py --dry-run` が省略する「git push」は本当に自動実行対象か

**回答:**
MVP では `commit` までは自動化候補、`push` は人間承認後にする。`git push` は自動実行の標準対象にしない。

**正式方針:**

- `main.py` が担当してよい範囲:
  - 成果物作成
  - 状態更新
  - 必要なら `git add`
  - 必要なら `git commit`
- 人間承認が必要な範囲:
  - `git push`
  - GitHub Pages 公開反映
  - リリース扱いの更新

**`--dry-run` の意味:**

- ファイル生成
- 実行予定表示
- 状態遷移確認
- Git操作は行わない

**通常実行:** `commit` まで行う設定は可。ただし `push` は明示フラグまたは人間承認必須とする。

---

_全25件 回答確定。SPEC.md v0.3 へ反映済み。_

---

## 2026-03-23 v0.3 追加レビュー（回答確定）

---

## Q26. `scripts/agents/` のファイル命名規則が `agents.yaml` の id と不一致

**該当箇所:** セクション4.2、5、13.31

- Section 4.2 の `agents.yaml` 標準規則: `id: market_researcher` → `scripts/agents/market_researcher.py`（サフィックスなし）
- Section 5 のリポジトリ構成ツリー: `ceo_agent.py`、`coo_agent.py`（`_agent` サフィックスあり）
- Section 13.31 の骨格例: `market_researcher.py`（サフィックスなし）

どちらを正式とするか。`id = 実装ファイル名` の規則に従うならサフィックスなし（`ceo.py`）が正しいが、ツリー表記と矛盾している。

**回答:**
サフィックスなしに統一する。`agents.yaml` の `id` とファイル名を一致させる。

- `id: ceo` → `scripts/agents/ceo.py`
- `id: coo` → `scripts/agents/coo.py`
- `id: market_researcher` → `scripts/agents/market_researcher.py`

Section 5 ツリーの `ceo_agent.py` / `coo_agent.py` は誤りとして修正する。

---

## Q27. `artifacts/design/adr/` がリポジトリ構成図に未記載

**該当箇所:** セクション5、Phase 4（セクション14）

- Section 5 のツリーには `/artifacts/design` のみで `adr/` サブディレクトリが記載されていない
- Phase 4 の成果物には `artifacts/design/adr/*.md` が登場する
- `artifacts/design/adr/` はツリーに追加すべきか

**回答:**
追加する。`/artifacts/design/adr/` を正式なリポジトリ構成に含める。

---

## Q28. Codex CLI 委任書を作るフェーズが未定義

**該当箇所:** セクション11.3、13.19（Codex Prompt Writer）、Phase 5・8

- Phase 5（タスク分解）で `artifacts/design/tasks.md` が作られる
- Phase 8（実装）で Codex CLI が動く
- しかし `artifacts/prompts/task-xxx.md`（委任書）をいつ・どのフェーズで・誰が作るかがワークフローに明記されていない
- Codex Prompt Writer（13.19）が担当するはずだが、対応するフェーズが存在しない
- Phase 5 と Phase 8 の間に「Phase 5.5: 委任書作成」あるいは「Phase 5 の後工程」として定義すべきか

**回答:**
Phase 5 と旧 Phase 6 の間に **Phase 6: Codex CLI 委任書作成** を独立追加する。旧 Phase 6〜11 を 1 つずつ後ろへ繰り下げる。

- 主担当: Codex Prompt Writer
- レビュー: Tech Lead Agent
- 成果物: `artifacts/prompts/task-001.md`, `task-002.md`, ...

---

## Q29. `browser-use CLI など` が曖昧

**該当箇所:** セクション4.1

`browser-use CLI などのブラウザ確認手段` と記載されているが、「など」で実際に使うツールが特定できない。

- `browser-use CLI` は正式採用ツールか、候補例か
- MVP で使うブラウザ確認ツールを1〜2個に絞って明記すべきでは
- 代替として Playwright、Puppeteer、手動確認なども選択肢に挙がるが、どれを基準にするか

**回答:**
MVP の標準は **手動ブラウザ確認 + browser-use CLI** に固定する。

- 手動ブラウザ確認: 必須
- browser-use CLI: 自動確認の標準
- Playwright / Puppeteer: 必要時のみ代替採用可

Section 4.1 の「など」を上記3行の明文に書き換える。

---

## Q30. AdSense の MVP での扱いが設計原則と矛盾している

**該当箇所:** セクション5.3、6.4、23

- Section 6.4 の設計原則: 「公開対象HTMLには共通の Google AdSense タグを `<head>` に入れること」（必須扱い）
- Section 23 の MVP 必須項目: AdSense が含まれていない
- 矛盾している。どちらが正しいか。設計原則から削除するか、MVP 必須に追加するか

加えて、AdSense タグ（`ca-pub-6743751614716161`）が SPEC.md 本文に埋め込まれている。これはリポジトリに公開してよいか確認が必要。

**回答:**
AdSense は **MVP 必須** とする。収益源のため daily-ai-agent で入れ忘れた教訓を活かし、仕様で強制する。

- 公開対象ページ（ルート `index.html`・各アプリ `index.html`）に標準組み込み
- `create-app-template.py` / `build-index.py` 生成時点で挿入済みにする（後付けしない）
- テストページ・管理ページ・ローカル確認ページは対象外
- 各アプリ `spec.md` に `adsense_required` / `adsense_applied` / `adsense_checked_at_release` フィールドを追加
- 公開品質ゲート G6 に AdSense 確認を追加
- リリース停止条件: 本体ページに AdSense なし → Release NG

AdSense publisher ID はリポジトリに公開してよい（公開情報）。

---

## Q31. Phase 0 の成果物に `scripts/main.py` が含まれていない

**該当箇所:** セクション14（Phase 0）、23（MVP）

- Phase 0 の成果物: `agents/agents.yaml`、`docs/org-chart.md`、`SPEC.md`、`state/schema.md`、`state/example-company_state.json`
- `scripts/main.py` は OpenClaw の中心実装であり、MVP 必須だが Phase 0 成果物に含まれていない
- Phase 0 に含めるか、別フェーズで作るか

**回答:**
Phase 0 の成果物に `scripts/main.py` を追加する。必要に応じて `scripts/agents/__init__.py` も含める。

---

## Q32. `prd` と `product` の命名ゆれ

**該当箇所:** セクション20（状態管理）、リポジトリ構成

- `state/company_state.json` の `current_phase` enum: Phase 3 = `"prd"`
- リポジトリ構成ディレクトリ: `artifacts/product/`
- Phase 3 の成果物パス: `artifacts/product/prd.md`

`prd` と `product` が混在している。`state` の enum を `"product"` に統一すべきか、それとも enum は短縮形 `"prd"` のまま維持するか。

**回答:**
`"product"` に統一する。ディレクトリ名・フェーズ識別子を揃える。ファイル名 `prd.md` はそのまま維持。

- ディレクトリ: `artifacts/product/`
- 成果物: `artifacts/product/prd.md`
- `current_phase` enum: `"product"`（旧 `"prd"` は廃止）

---

## Q33. `13.31 エージェント実装規約` のセクション番号が不自然

**該当箇所:** セクション13.31

- セクション13.1〜13.30 はエージェント個別の責務定義
- セクション13.31 だけが実装規約（技術的な内容）で性質が異なる
- 他の読者が「31体目のエージェントか」と誤読しやすい
- 独立したセクション番号（例: `## 11.6`、または新章 `## 13.5 エージェント実装規約`）に分離すべきか

**回答:**
`## 14. エージェント実装規約（Python）` として独立章に分離する。旧 Section 14〜24 を 1 つずつ繰り下げ（→ 15〜25）。

_全8件 回答確定。SPEC.md v0.4 へ反映済み。_

---

## 2026-03-23 v0.5 追加レビュー（回答確定）

## Q34. `db.cgi` の `action` は `query` と `database` のどちらが正式仕様か

**回答:**
`action: "query"` に統一する。`"database"` は表記ゆれとして廃止する。

**正式ルール:**

- `action`: `query`
- `operation`: 実際の処理種別
- `select`
- `insert`
- `update`
- `delete`
- `count`
- `create_table`

**修正例:**

```json
{
  "action": "query",
  "database": "app003",
  "operation": "create_table",
  "table": "items",
  "schema": {
    "id": "TEXT PRIMARY KEY",
    "title": "TEXT NOT NULL",
    "created_at": "TEXT NOT NULL"
  },
  "if_not_exists": true
}
```

**理由:**

- フロントとCGIの契約が単純になる
- `create_table` だけ別 `action` にする理由が薄い
- 実際の分岐は `operation` で十分表現できる

---

## Q35. 委任書作成を API / DB 疎通確認より先に置くのが正式フローか

**回答:**
正式フローは **疎通確認を先、委任書確定を後** に直す。

- Phase 5: タスク分解
- Phase 6: API疎通確認
- Phase 7: DB接続確認
- Phase 8: Codex CLI 委任書作成
- Phase 9: Codex CLI 実装

**理由:**

- API / DB の疎通結果でズレが見つかると、先に作った委任書がすぐ古くなる
- 確認済み前提で委任書を確定するほうが仕様として自然

**補足運用:**

- タスク分解直後にドラフト委任書を作るのは可
- ただし `artifacts/prompts/task-xxx.md` を正式成果物として確定するのは疎通確認後

---

## Q36. AdSense の適用対象は「本体公開HTML」のみか、「公開対象HTML」全体か

**回答:**
**本体公開HTMLのみ** に固定する。`test-api.html` や `test-db-readonly.html` は常に対象外でよい。

**正式対象:**

- ルート `index.html`
- 各アプリ本体 `index.html`
- 必要なら収益導線ページ

**対象外:**

- `test-api.html`
- `test-db-readonly.html`
- 管理ページ
- ローカル確認ページ

**修正文言:**

`公開対象HTMLには共通の Google AdSense タグを <head> に入れること`

ではなく、

`本体公開HTMLおよび収益対象ページには、共通の Google AdSense タグを <head> に入れること`

とする。

**理由:**

- テストページは公開されていても収益対象ではない
- 検証UIに広告を入れると品質確認の邪魔になりやすい
- Q30 の「収益源として必須」と両立する

---

## Q37. `current_phase_number` は補助項目として維持するか、それとも廃止するか

**回答:**
廃止でよい。正本は `current_phase` の英語識別子だけにする。

**正式方針:**

- 残す項目: `current_phase`
- 廃止する項目: `current_phase_number`

**理由:**

- フェーズ追加や並び替えでずれやすい
- 実例でもすでにずれている
- 番号が必要なら表示側で `current_phase` から導出すればよい

**代替案:**

表示順が必要なら `state/schema.md` に順序マップを持たせる。

---

## Q38. Browser Test Operator はローカル専用DB確認ページまで担当範囲に含むか

**回答:**
含む。ただし、担当範囲を **公開確認** と **ローカル管理確認** に分けて明記する。

**正式な担当範囲:**

- A. 公開確認
- 本体ページ
- `test-api.html`
- `test-db-readonly.html`（ある場合）
- B. ローカル管理確認
- ローカルHTTPサーバー上の書き込み確認ページ

**正式手順:**

- ローカルHTTPサーバーを起動
- `http://localhost:8000/...` で確認
- 必要なCORS許可を用意
- 書き込み系の `insert` テストはここで行う

**役割分離:**

- MVP では別ロールに分けない
- Browser Test Operator が公開確認とローカル管理確認の両方を担当する

**理由:**

- テスト観点が連続している
- 人数を増やすほどではない
- 同じ担当者が続けて見たほうが差分に気づきやすい

---

_全38件 回答確定。SPEC.md v0.5 へ反映済み。_

---

## 2026-03-23 USECASE.md 作成時の不明点（Q39〜Q43 回答確定）

---

## Q39. Market Researcher（Phase 1）が参照するデータソースは何か

**回答:**
MVPでは **内部成果物 + 運営者入力 + 公開Web情報** の3系統を正式入力とする。

**正式入力:**
- `docs/roadmap.md`
- 過去スプリントの改善メモ（`artifacts/sprints/` 配下）
- 既存アプリ一覧と利用状況
- 運営者が与えるテーマ・制約・狙い
- 公開Web上の競合・類似サービス・検索結果・話題情報

**出力先:**
- `artifacts/research/research_report.md`
- `artifacts/research/source_notes.md`（外部情報の出典メモ）

**ルール:**
- 外部情報を使った場合は出典URLまたは参照元メモを残す
- 初期段階はデータが少ないため外部調査の比重が高くてよい
- 改善サイクル継続後は既存アプリの結果も入力に含める

---

## Q40. エンドユーザーのフィードバックはどの経路で Phase 12（改善スプリント）に届くか

**回答:**
MVPでは **間接経路を正規ルート** とする。専用フィードバックフォームを必須にせず、以下の順で扱う。

**正式経路:**
1. `visitor.cgi` による利用状況データ（訪問数・ページ遷移・時間帯）
2. GitHub Issue または README 誘導
3. 運営者が手動で収集したメモ
4. 必要になったらアプリ内フィードバックフォームを追加

**Improvement Strategist への受け渡し成果物:**
- `artifacts/sprints/user_feedback.md`（定性フィードバック整理）
- `artifacts/sprints/usage_insights.md`（数値系利用状況まとめ）

**理由:** `visitor.cgi` + 運営者回収 を正式ルートにするほうが軽く現実的。

---

## Q41. Phase 12 から Phase 1 / Phase 5 へのループバック判断基準は何か

**回答:**

| 条件 | 戻り先 |
|-----|-------|
| 既存アプリの改善案が明確、PRD不要、タスク分解から再開できる | Phase 5（タスク分解） |
| 新しいテーマ探索・別カテゴリのアプリ・新規企画が必要 | Phase 1（市場調査） |

**判断者:**
1. 一次整理: Improvement Strategist
2. 妥当性確認: COO Agent
3. 最終承認: CEO Agent

**判断材料:** visitor.cgi の利用状況 / QA改善点 / AdSense・導線の改善余地 / 新規アイデア候補 / ROI観点での優先度

---

## Q42. ROI Agent は Phase 2（アイデア選定）で動くか Phase 3（PRD作成）で動くか

**回答:**
**両方で動く。ただし役割を分ける。**

- **Phase 2:** 軽量ROI評価（アイデア候補の足切り）
- **Phase 3:** PRD確定前の詳細ROI評価（企画規模・収益導線の妥当性確認）

USECASE.md の図では Phase 3 への点線のみ描いたが、Phase 2 にも参加する。二段階評価が正式仕様。

---

## Q43. Codex CLI への委任書渡し方は「ファイルパス指定」か「標準入力」か

**回答:**
**正本をファイルに固定する。渡し方は実装依存でよい。**

- 正本: `artifacts/prompts/task-xxx.md`（必ずファイル保存）
- 実行時: ファイル内容を読み込んで Codex CLI に渡す（ファイルパス指定または stdin どちらでも可）
- stdin のみで完結してファイルを残さない運用は不可

**理由:** 委任書ファイルが正式成果物であり、CLI 引数形式が変わっても正本は変更不要にする設計。

---

_全43件 回答確定。SPEC.md v0.6 へ反映済み。_

---

## 2026-03-23 SPEC.md / USECASE.md 追加レビュー回答（Q44〜Q50 回答確定）

## Q44. G6 公開品質の判定結果は `state/company_state.json` と `deploy_report.md` のどちらへどう記録するか

**回答:**
両方に記録する。役割を分ける。

**正式方針:**

- `state/company_state.json`: 機械可読な最新状態の正本
- `artifacts/sprints/deploy_report.md`: 人間向けの公開記録・判定理由の正本

`state/company_state.json` の `quality_gate` に以下を追加する。

- `adsense_verified`
- `test_pages_adsense_clean`
- `release_gate_passed`

`artifacts/sprints/deploy_report.md` には以下を明記する。

- 公開URL
- ビルド状態
- AdSense確認結果
- テストページ混入有無
- 既知の問題
- 最終公開可否

**理由:**
`state` だけだと「なぜ OK / NG だったか」が薄く、`deploy_report` だけだと自動判定しにくい。機械判定は `state`、人間の監査証跡は `deploy_report` に分けるのが自然。

---

## Q45. 各アプリ `spec.md` の `adsense_required` は常に `true` なのか、例外を許すのか

**回答:**
例外を許す。デフォルトは `true` とする。

**正式方針:**

- デフォルト: `adsense_required: true`
- 例外許可:
- 社内検証用
- 純粋ツールページで収益対象外と明示したもの
- 法務・審査・UX上の理由で広告非表示が妥当なもの

例外時は `spec.md` に理由必須とする。

- `adsense_required: false`
- `adsense_exception_reason: ...`

**理由:**
原則必須・例外明示の形が最も整合する。テンプレートに `true / false` がある以上、完全固定値より例外を説明責任付きで許すほうが自然。

---

## Q46. API疎通確認は `now.cgi` / `uuid.cgi` の汎用疎通だけでよいか、それとも採用した各 CGI を個別確認するか

**回答:**
汎用疎通 + 採用エンドポイント個別確認の両方を必須とする。

**正式手順:**

- 汎用疎通確認:
- `now.cgi` または `uuid.cgi`
- 採用エンドポイント個別確認:
- そのアプリが使う CGI をすべて `test-api.html` で確認
- 例: `validate.cgi`, `convert.cgi`, `visitor.cgi`, `db.cgi`

**判定ルール:**

- 汎用疎通 OK だけでは Phase 6 合格にしない
- 採用した各 CGI が正常応答して初めて Phase 6 合格

**理由:**
サーバー疎通だけで実際の採用 CGI が壊れていたら、事前確認の意味が薄い。利用前確認を `test-api.html` で必須にする方針と揃える。

---

## Q47. Phase 1 の「既存アプリ一覧と利用状況」の正式入力ファイルは何か

**回答:**
専用集約ファイルを正本にする。

**正式入力ファイル:**

- `artifacts/research/app_inventory.md`
- `artifacts/sprints/usage_insights.md`
- `artifacts/sprints/user_feedback.md`

**役割分担:**

- `app_inventory.md`: 既存アプリ一覧の正本
- `usage_insights.md`: 数値系の利用状況
- `user_feedback.md`: 定性フィードバック
- 各アプリ `spec.md`: 個別仕様参照用であり、一覧の正本ではない
- ルート `index.html`: 表示用であり分析用の正本ではない

**理由:**
一覧・定量・定性の3点セットに分けると、Market Researcher が読む正本がぶれない。

---

## 2026-03-23 USECASE.md レビュー追加回答（Q48〜Q50 回答確定）

## Q48. DBアプリは Phase 6（API疎通確認）と Phase 7（DB接続確認）の両方を通るのが正式か

**回答:**
両方必須。Phase 7 は Phase 6 を内包しない。

**正式方針:**

- `runtime_mode: db` は
- Phase 6: `db.cgi` への到達性・SSL・CORS・基本応答確認
- Phase 7: `select` / `insert` / `count` / `error` のDB機能確認

したがって DB アプリは `P5 -> P6 -> P7 -> P8` を正式ルートとする。

**理由:**
Phase 6 は通信基盤確認、Phase 7 は DB 操作確認として役割が別。分けたほうが事故りにくい。

---

## Q49. `visitor.cgi` による訪問記録は全アプリ共通の標準実装か、それとも任意機能か

**回答:**
標準推奨だが、必須ではなく任意機能とする。

**正式方針:**

- テンプレート既定値: `visitor_tracking: true`
- 無効化は可
- 無効化する場合は `spec.md` に理由を記載
- Static アプリでも `visitor.cgi` を使ってよい
- Static アプリが `visitor.cgi` を使っても分類は `static` のままでよい

**理由:**
USECASE の全アプリ矢印と SPEC の可変項目を両立するには、「原則オン、例外オフ」が自然。改善スプリントへの主要入力として推奨度は高い。

---

## Q50. AdSense 判定フローは「収益対象ページ」まで確認範囲に含めるか

**回答:**
含める。USECASE の判定フローを一般化する。

**正式方針:**

- Release OK 判定対象:
- ルート `index.html`
- 各アプリ本体 `index.html`
- 収益対象ページすべて（例: `landing.html` など）
- 対象外:
- `test-api.html`
- `test-db-readonly.html`
- 管理ページ
- ローカル確認ページ

**USECASE 修正文言案:**

- 収益対象ページに AdSense タグあり？
- AdSense によるレイアウト崩れなし？
- テストページ・管理ページに AdSense 混入なし？

**理由:**
AdSense 対象を `index.html` 限定にすると現行仕様とずれるため、収益対象ページ全体に一般化したほうが自然。

---

_全50件 回答確定。SPEC.md v0.7・USECASE.md へ反映済み。_

_全54件 回答確定。SPEC.md v0.8 へ反映済み。_

---

## 2026-03-23 SEQUENCE.md 作成時の不明点（Q51〜Q54 回答確定）

---

## Q51. `run_phase()` からエージェントを呼ぶ方式は「関数呼び出し」か「subprocess」か

**回答:**
正式方式は **同一 Python プロセス内での関数呼び出し** とする。

**正式方針:**
- 標準: `import scripts.agents.xxx as m` → `run_phase("xxx", m.main)`
- 正常終了: `return` または `SystemExit(0)`
- 異常終了: `SystemExit(1)` または未捕捉例外
- subprocess 実行は MVP 標準にしない
- 将来、分離実行やサンドボックス化が必要になった場合の拡張案としては許容する

**理由:**
SPEC の `scripts/main.py` 骨格が `fn()` 直接呼び出しで書かれており、各エージェントも Python モジュールとして `main()` を持つ前提になっているため。MVP ではこの形が最も単純で、ログ・例外処理・状態遷移も揃えやすい。

---

## Q52. フェーズ失敗時に `company_state.json` の `current_phase` はどう扱うか

**回答:**
失敗時は **`current_phase` を失敗したフェーズの識別子のまま保持**し、`next_action` で修正内容を表現する。

**正式方針:**
- 失敗時に `current_phase` を前フェーズへ巻き戻さない
- `current_phase` は失敗したフェーズの識別子を保持する
- `next_action` に修正内容を記録する
- 必要なら将来 `sub_phase` や `last_error` を追加してもよいが、MVP 必須ではない

**例:**
```json
{
  "current_phase": "implementation",
  "next_action": "fix-relative-path-bug"
}
```

**理由:**
SPEC では `current_phase` は英語識別子の正本で、詳細な状態は `next_action` や `sub_phase` で補助管理するとしている。また失敗時は「前フェーズ成果物は保持」「修正後に同一フェーズ再実行」と定義されているため、巻き戻しより「そのフェーズで止まっている」と表現するほうが自然。

---

## Q53. Phase 11 の git push は運営者が手動で実行するか、それとも `scripts/main.py` が承認後に自動実行するか

**回答:**
MVP の正式方式は **運営者が手動でターミナルから実行する** とする。

**正式方針:**
- `git push origin main` は運営者の手動承認操作
- `scripts/main.py` は公開判定・成果物作成・承認依頼までは行ってよい
- `git push` 自体は自動実行しない
- 将来、自動化する場合でも別フェーズで再設計する

**理由:**
SPEC では `git push` は「人間承認付き操作」であり、`scripts/main.py` の自動化対象は commit までが候補、push は標準対象外とされている。SEQUENCE.md の Phase 11 でも、最終的に運営者が `git push origin main` を手動実行する流れで描かれている。

---

## Q54. `visitor.cgi` への自動記録は「ページロード時に app.js が fetch する」か「別のタイミングか」

**回答:**
正式方式は **`visitor_tracking: true` の場合、ページロード直後に `app.js` が非同期 fetch する** とする。
標準タイミングは `DOMContentLoaded` とし、`window.onload` は必須にしない。

**正式方針:**
- 発火条件: `visitor_tracking: true`
- 標準タイミング: `DOMContentLoaded`
- 実装場所: `app.js` または `api.js`
- 呼び出しは非同期・失敗しても本体機能を止めない
- `scripts/create-app-template.py` は `visitor_tracking: true` 前提の呼び出し雛形を含めてよい
- `visitor_tracking: false` の場合は生成しないか、無効化コメント付きにする

**理由:**
SEQUENCE.md の利用フローでは、公開アプリ JS がページ表示直後に `visitor.cgi` へ自動記録する流れで描かれている。SPEC でも `visitor_tracking` は既定値 `true` でテンプレート項目として持つ前提になっているので、「ページロード時の軽い非同期記録」を標準化するのが一番すっきりする。`window.onload` まで待つ必要は薄く、初回操作待ちにすると記録漏れが増える。

---

_全54件 回答確定。SPEC.md v0.8 へ反映済み。_

_全57件 回答確定。SPEC.md v0.9 へ反映済み。_

---

## 2026-03-23 CLASS.md 作成時の不明点（Q55〜Q57 回答確定）

---

## Q55. `agents.yaml` の `inputs` / `outputs` は Python 実装側でどう使われるか

**回答:**
正本は `agents.yaml` とし、`scripts/main.py` が参照して成果物確認に使う。各エージェント Python ファイルは原則として `agents.yaml` を直接読まない。

**正式方針:**
- `agents.yaml` の `inputs` / `outputs` はメタデータ正本
- `scripts/main.py`（OpenClaw）がそれを参照して以下に使う
  - フェーズ開始前の入力ファイル存在確認
  - フェーズ終了後の出力ファイル存在確認
  - ログや `failure_report.md` への記録
- 各エージェント実装は自分の責務に必要な既定パスをコード内に持ってよいが、契約上の正本は `agents.yaml`
- エージェントが毎回 `agents.yaml` を自分で読んでパス解決する方式は MVP 標準にしない
- 依存方向は `OpenClaw → AgentsYaml` を正とし、`Agent → AgentsYaml` は必須依存にしない

**理由:**
CLASS.md でも `OpenClaw --> AgentsYaml : 参照（メタデータ台帳）` となっていて、エージェント側から AgentsYaml を読む依存は描かれていない。Q17 で `agents.yaml` は「エージェント台帳兼メタデータ定義」、`scripts/main.py` は「実行順序と状態遷移の唯一の制御点」と整理済みなので、入出力契約の確認も `main.py` 側に寄せるのが自然。

---

## Q56. `QualityGate` の各フラグは誰がどのタイミングで `true` に更新するか

**回答:**
**判定責任は担当エージェント、`state/company_state.json` への書き込み責任は OpenClaw** とする。

**正式方針:**
- 各エージェントは自分の成果物・判定レポートを出力する
- OpenClaw がフェーズ完了時にその成果物を読み、`quality_gate` を更新する
- エージェントが `state` を直接書き換えるのを標準にしない

| フラグ | 判定責任エージェント | 更新タイミング |
|-------|-----------------|--------------|
| `pages_ready` | Tech Lead Agent / Codex 実装結果レビュー | 実装フェーズ完了時 |
| `ssl_verified` | Sakura API Coordinator | API疎通確認フェーズ完了時 |
| `cors_verified` | Sakura API Coordinator | API疎通確認フェーズ完了時 |
| `browser_test_passed` | Browser Test Operator | テストフェーズ完了時 |
| `adsense_verified` | GitHub Pages Release Manager | リリース判定フェーズ完了時 |
| `test_pages_adsense_clean` | GitHub Pages Release Manager | リリース判定フェーズ完了時 |
| `release_gate_passed` | Release Manager + COO / 運営者承認 | リリース判定フェーズの最後 |

**理由:**
CLASS.md では `OpenClaw --> CompanyState : 読み書き` となっており、state 管理主体は OpenClaw 側に置かれている。複数エージェントが直接更新すると責務が散って事故りやすいため、判定は各担当、反映は OpenClaw に一本化する。

---

## Q57. `AppSpec`（各アプリの `spec.md`）は Python データクラスとして定義されるか、それとも Markdown ファイルとして読み書きされるだけか

**回答:**
MVP では **Markdown ファイルを正本** とし、必要時に Python 側で軽量にパースして扱う。専用 dataclass を必須にはしない。

**正式方針:**
- 正本: `apps/app-xxx-name/spec.md`（Markdown）
- 生成はテンプレートベース（`create-app-template.py`）
- 更新は必要項目のテキスト更新または軽量パース
- `AppSpec` は実装上の必須クラスではなく、CLASS.md における **設計上の概念クラス**
- 将来必要になれば `TypedDict` / `dataclass` / YAML Front Matter + パーサへ拡張してよいが MVP 必須にしない

**補足方針:**
- まず Section 22 のテンプレート項目を持つ Markdown を正本にする
- 自動処理が増えて壊れやすくなった時点で構造化形式への移行を検討する
- いきなり Front Matter 必須にしない

**理由:**
SPEC では `spec.md` をテンプレート項目付きの Markdown として定義している。CLASS.md の `AppSpec` は「その Markdown が持つべき項目構造」を表した概念モデルとして読むのが自然。MVP でいきなり型クラスを増やすと実体のない入れ物だけ先にできてしまう。
