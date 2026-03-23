# QandA.md — SPEC.md レビュー質問集

作成日: 2026-03-23
対象: SPEC.md v0.1 → v0.2 補足設計回答 / SPEC.md v0.3 レビュー追補
ステータス: 全25件 回答確定 / SPEC.md v0.3 反映済み

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

## 2026-03-23 v0.3 追加レビュー（未回答）

---

## Q26. `scripts/agents/` のファイル命名規則が `agents.yaml` の id と不一致

**該当箇所:** セクション4.2、5、13.31

- Section 4.2 の `agents.yaml` 標準規則: `id: market_researcher` → `scripts/agents/market_researcher.py`（サフィックスなし）
- Section 5 のリポジトリ構成ツリー: `ceo_agent.py`、`coo_agent.py`（`_agent` サフィックスあり）
- Section 13.31 の骨格例: `market_researcher.py`（サフィックスなし）

どちらを正式とするか。`id = 実装ファイル名` の規則に従うならサフィックスなし（`ceo.py`）が正しいが、ツリー表記と矛盾している。

---

## Q27. `artifacts/design/adr/` がリポジトリ構成図に未記載

**該当箇所:** セクション5、Phase 4（セクション14）

- Section 5 のツリーには `/artifacts/design` のみで `adr/` サブディレクトリが記載されていない
- Phase 4 の成果物には `artifacts/design/adr/*.md` が登場する
- `artifacts/design/adr/` はツリーに追加すべきか

---

## Q28. Codex CLI 委任書を作るフェーズが未定義

**該当箇所:** セクション11.3、13.19（Codex Prompt Writer）、Phase 5・8

- Phase 5（タスク分解）で `artifacts/design/tasks.md` が作られる
- Phase 8（実装）で Codex CLI が動く
- しかし `artifacts/prompts/task-xxx.md`（委任書）をいつ・どのフェーズで・誰が作るかがワークフローに明記されていない
- Codex Prompt Writer（13.19）が担当するはずだが、対応するフェーズが存在しない
- Phase 5 と Phase 8 の間に「Phase 5.5: 委任書作成」あるいは「Phase 5 の後工程」として定義すべきか

---

## Q29. `browser-use CLI など` が曖昧

**該当箇所:** セクション4.1

`browser-use CLI などのブラウザ確認手段` と記載されているが、「など」で実際に使うツールが特定できない。

- `browser-use CLI` は正式採用ツールか、候補例か
- MVP で使うブラウザ確認ツールを1〜2個に絞って明記すべきでは
- 代替として Playwright、Puppeteer、手動確認なども選択肢に挙がるが、どれを基準にするか

---

## Q30. AdSense の MVP での扱いが設計原則と矛盾している

**該当箇所:** セクション5.3、6.4、23

- Section 6.4 の設計原則: 「公開対象HTMLには共通の Google AdSense タグを `<head>` に入れること」（必須扱い）
- Section 23 の MVP 必須項目: AdSense が含まれていない
- 矛盾している。どちらが正しいか。設計原則から削除するか、MVP 必須に追加するか

加えて、AdSense タグ（`ca-pub-6743751614716161`）が SPEC.md 本文に埋め込まれている。これはリポジトリに公開してよいか確認が必要。

---

## Q31. Phase 0 の成果物に `scripts/main.py` が含まれていない

**該当箇所:** セクション14（Phase 0）、23（MVP）

- Phase 0 の成果物: `agents/agents.yaml`、`docs/org-chart.md`、`SPEC.md`、`state/schema.md`、`state/example-company_state.json`
- `scripts/main.py` は OpenClaw の中心実装であり、MVP 必須だが Phase 0 成果物に含まれていない
- Phase 0 に含めるか、別フェーズで作るか

---

## Q32. `prd` と `product` の命名ゆれ

**該当箇所:** セクション20（状態管理）、リポジトリ構成

- `state/company_state.json` の `current_phase` enum: Phase 3 = `"prd"`
- リポジトリ構成ディレクトリ: `artifacts/product/`
- Phase 3 の成果物パス: `artifacts/product/prd.md`

`prd` と `product` が混在している。`state` の enum を `"product"` に統一すべきか、それとも enum は短縮形 `"prd"` のまま維持するか。

---

## Q33. `13.31 エージェント実装規約` のセクション番号が不自然

**該当箇所:** セクション13.31

- セクション13.1〜13.30 はエージェント個別の責務定義
- セクション13.31 だけが実装規約（技術的な内容）で性質が異なる
- 他の読者が「31体目のエージェントか」と誤読しやすい
- 独立したセクション番号（例: `## 11.6`、または新章 `## 13.5 エージェント実装規約`）に分離すべきか

_全8件 未回答。_
