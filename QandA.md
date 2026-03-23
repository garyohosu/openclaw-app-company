# QandA.md — SPEC.md レビュー質問集（回答済み）

作成日: 2026-03-23
対象: SPEC.md v0.1 → v0.2 補足設計回答
ステータス: 全15件 回答確定 / SPEC.md v0.2 反映済み

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
  "database": "app003.sqlite",
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

_全15件 回答確定。SPEC.md v0.2 へ反映済み。_
