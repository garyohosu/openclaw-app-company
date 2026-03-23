# OpenClaw App Company 仕様書

- リポジトリ名: `openclaw-app-company`
- デプロイ先: GitHub Pages
- 実装エンジン: Codex CLI
- オーケストレーション: OpenClaw
- バックエンド連携: Sakuraレンタルサーバー CGI/Python API Toolbox
- ドキュメント版数: v0.4
- 作成日: 2026-03-23
- 最終更新: 2026-03-23（Q26〜Q33 反映: 命名規則・フェーズ・AdSense・章構成を整理）
- 参考実装: `C:\PROJECT\daily-ai-agent`
- 実行環境: Windows 11 上の WSL2

---

## 1. 目的

本プロジェクトの目的は、30体のAIエージェントを仮想的な開発会社として組織し、市場調査、アイデア選定、PRD作成、設計、実装、テスト、公開、改善までを自律的に回せる仕組みを作ることである。

単なる「コード生成」ではなく、以下を一つの継続運用可能なシステムとして成立させることを狙う。

- 何を作るかを決める
- どう作るかを整理する
- 実装をCodex CLIへ委任する
- GitHub Pagesへ公開する
- 必要時のみSakura CGI API Toolboxを利用する
- 複数アプリを1リポジトリで増やしていく
- 改善サイクルを継続する

---

## 2. 成功条件

### 2.1 最終ゴール

1つのGitHubリポジトリ内に複数のWebアプリを格納し、GitHub Pagesで公開し、必要な場合のみSakura CGI API Toolboxを呼び出す量産型アプリ工場を構築する。

### 2.2 成功条件

以下を満たせば成功とする。

- 各アプリが独立したフォルダで管理されている
- GitHub Pages上で公開可能である
- 実装はCodex CLI前提で統一されている
- OpenClawは役割分担と工程制御に専念している
- APIやDBが必要な場合、既存のSakura CGI API Toolboxを優先利用している
- 仕様、設計、QA、改善履歴が成果物として残る
- 同じ流れで次のアプリを追加できる

### 2.3 非ゴール

以下は初期段階では対象外とする。

- 巨大SaaSの一括開発
- フルスタック常駐サーバー前提のシステム
- SSRや複雑なクラウド基盤の構築
- いきなり完全無人で長期運転すること
- 毎回ゼロから新しいバックエンドを量産すること

---

## 3. 基本思想

### 3.1 OpenClaw の定義

OpenClaw は本プロジェクトにおける **Pythonオーケストレータ** の総称である。外部製品名ではなく、リポジトリ内の `scripts/main.py` として実装される。

**実行環境:** Windows 11 上の WSL2（Ubuntu）で動作する。Python スクリプトはすべて WSL2 環境内で実行する。

**参考実装:** `C:\PROJECT\daily-ai-agent\scripts\main.py`

実行モデル:

```python
# scripts/main.py の骨格（daily-ai-agent パターン）
def run_phase(name: str, fn) -> bool:
    try:
        fn()
        return True
    except SystemExit as e:
        if e.code == 0:
            return True  # 新規なしで正常終了
        return False      # 異常終了
    except Exception:
        return False

def main():
    # Phase 1: 市場調査
    import agents.market_researcher as m
    if not run_phase("market_researcher", m.main): sys.exit(1)
    # Phase 2: アイデア選定 ...
```

各エージェントは `scripts/agents/` 内の **Pythonモジュール** として実装する。

```python
# scripts/agents/market_researcher.py の骨格
def main() -> None:
    # 入力: artifacts/research/ 配下のファイルを読む
    # 出力: artifacts/research/research_report.md を書く
    # 正常終了: return または SystemExit(0)
    # 異常終了: raise SystemExit(1)
```

エージェント間の通信は **ファイルシステム経由** で行う。`artifacts/` `apps/` `docs/` `state/` 配下のファイルを共通の受け渡し面とし、エージェント同士が直接会話する前提にはしない。

**Python実装規約（daily-ai-agent 準拠）:**

- 各モジュールは `main()` 関数を持つ
- 正常終了: `return` または `raise SystemExit(0)`
- 異常終了: `raise SystemExit(1)`
- ログ: Python `logging` モジュール使用、`logs/agent-name-YYYY-MM-DD.log` に出力
- オーケストレータは異常終了時に後続フェーズをスキップする

### 3.2 組織として動かす

AIを万能な一体として使うのではなく、役割を持つ複数エージェントに分割する。人間の開発組織のように、調査、企画、設計、実装、QA、運用を分ける。

### 3.3 実装と判断を分離する

- 判断、整理、優先順位付けは OpenClaw 側が担当する
- コード生成と修正は Codex CLI に委任する

### 3.4 まず静的、次に軽API、最後にDB

バックエンドは最初から持たない。以下の順で設計判断する。

1. 完全静的で成立しないか
2. 既存の軽量 CGI API Toolbox で足りないか
3. それでも足りない場合のみ `db.cgi` を使う

この順番を破ると、だいたい後で保守費が増える。

### 3.5 1リポジトリで複数アプリを増やす

1つのリポジトリ内に複数アプリを置き、トップページを「展示場」にする。各アプリは独立して開発・公開・改善できるようにする。

---

## 4. 対象アーキテクチャ

### 4.1 全体構成

- OpenClaw
  - エージェント実行基盤
  - ワークフロー制御
  - 状態管理
  - 判断と分業の司令塔
- Codex CLI
  - HTML/CSS/JavaScript 実装
  - リファクタ
  - テスト観点反映
  - 修正差分生成
- GitHub
  - モノレポ管理
  - 履歴管理
  - GitHub Pages 公開元
- GitHub Pages
  - 静的アプリ公開
  - ルート一覧ページ提供
- ブラウザ確認手段
  - 手動ブラウザ確認（必須）
  - browser-use CLI（自動確認の標準）
  - Playwright / Puppeteer（必要時のみ代替採用可）
- Sakuraレンタルサーバー CGI/Python API Toolbox
  - 時刻取得
  - UUID発行
  - JSON検証
  - 単位変換
  - 訪問者記録
  - SQLite汎用DB API

### 4.2 `agents.yaml` 最小スキーマ

`agents/agents.yaml` は Phase 0 の成果物として作成する。各エージェントは以下の項目を持つ。

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

`agents/agents.yaml` は **エージェント台帳兼メタデータ定義** として扱う。`scripts/main.py` はこれを読んで担当、入力、出力を参照してよいが、**実行順序と状態遷移の正本** は `scripts/main.py` が持つ。

標準規則として、`id: market_researcher` は `scripts/agents/market_researcher.py` に対応させる。必要に応じて `default_phases` のような補助項目を追加してよいが、フェーズ割当の最終定義は `main.py` とする。

### 4.3 採用理由

- GitHub Pages は無料、HTTPS、管理が軽い
- Codex CLI は定額利用の前提に合う
- 1リポジトリで全体を俯瞰しやすい
- Sakura CGI Toolbox は既に検証済みの実体があり、軽いバックエンドとして使える

---

## 5. リポジトリ構成

リポジトリはモノレポとして管理する。

```text
/openclaw-app-company
  /.github
    /workflows
      deploy.yml
  /agents
    agents.yaml
  /apps
    /app-001-sample
      index.html
      style.css
      app.js
      api.js
      spec.md
      README.md
      test-api.html
      test-db-readonly.html
  /artifacts
    /research
    /product
    /design
      /adr
    /qa
    /security
    /prompts
    /sprints
    /executive
  /docs
    workflow.md
    org-chart.md
    roadmap.md
  /shared
    /components
    /styles
    /utils
  /scripts
    main.py                    # オーケストレータ（実行順序の唯一の定義元）
    create-app-template.py
    build-index.py
    /agents
      ceo.py
      coo.py
      market_researcher.py
      ...（30体分）
  /logs
  /state
    schema.md
    example-company_state.json
  /.nojekyll
  /index.html
  /README.md
  /SPEC.md
```

### 5.1 ルートページ

`index.html` はアプリ一覧ページにする。

表示項目:

- アプリ名
- 説明
- 状態
- 最終更新日
- 技術スタック
- Pages 公開URL
- API利用有無
- DB利用有無
- 公開用テストページへのリンク

### 5.2 `.nojekyll`

GitHub Pages で不要な変換を避けるため、`.nojekyll` を配置する。

### 5.3 Google AdSense

AdSense は本プロジェクトの **主要収益源** であり、MVP 必須要件とする。`daily-ai-agent` で入れ忘れた教訓を活かし、生成時点で組み込む設計にする。

**対象ページ（必須）:**
- ルート `index.html`
- 各アプリ `index.html`

**対象外:**
- `test-api.html`
- `test-db-readonly.html`
- ローカル専用確認ページ
- 管理ページ

**共通タグ:**

```html
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-6743751614716161"
     crossorigin="anonymous"></script>
```

**忘れ防止ルール:**
- `scripts/create-app-template.py` がアプリ `index.html` 生成時に挿入する
- `scripts/build-index.py` がルート `index.html` 生成時に挿入する
- 後付けではなく、生成時点で組み込み済みにする

**リリース停止条件（Release NG）:**
- ルート `index.html` に AdSense タグなし
- 新規アプリ本体 `index.html` に AdSense タグなし
- AdSense script 配置でレイアウト崩れが発生している
- テストページに誤って混入している

---

## 6. アプリ単位の仕様

各アプリは `/apps/app-xxx-name/` に配置する。

### 6.1 必須ファイル

- `index.html`
- `style.css`
- `app.js`
- `spec.md`
- `README.md`

### 6.2 API利用時の追加ファイル

- `api.js`
- `test-api.html`

### 6.3 DB利用時の追加ファイル

- `test-db-readonly.html`（公開する場合のみ）
- ローカル専用確認ページ（書き込み確認用、Pages 公開対象にしない）

### 6.4 設計原則

- できるだけ単体で動作すること
- 相対パスで動作すること
- Pages のサブパスで壊れないこと
- 他アプリへの依存を減らすこと
- API利用は `api.js` に集約すること
- DB操作は必ず `db.cgi` 経由とすること
- 公開用DB確認ページは read only にすること
- 書き込み確認UIは本番公開ページに出さないこと
- 公開対象HTMLには共通の Google AdSense タグを `<head>` に入れること

---

## 7. アプリの分類

### 7.1 Static

GitHub Pages だけで完結する。

例:

- 変換ツール
- 個人用メモ
- タスク整理
- UIジェネレータ
- 学習補助

保存:

- localStorage
- URLパラメータ
- 埋め込みJSON

### 7.2 Toolbox

Sakura CGI API Toolbox の軽量エンドポイントを使う。

例:

- UUID発行
- 現在時刻利用
- 入力データ検証
- 単位変換
- 訪問計測

### 7.3 DB

`db.cgi` を用いて SQLite に永続化する。

例:

- 投稿保存
- 履歴保存
- 複数端末共有
- 軽い会員データ
- スコアやランキング

---

## 8. Sakura CGI API Toolbox 利用仕様

### 8.1 前提

Sakuraレンタルサーバー上には「1ファイル = 1エンドポイント」の CGI/Python API Toolbox が存在する。アプリ側はこれを既存バックエンド部品として利用する。

### 8.2 Toolbox 対象

- `now.cgi`
- `uuid.cgi`
- `validate.cgi`
- `convert.cgi`
- `visitor.cgi`
- `db.cgi`

### 8.3 利用優先順位

1. Static で済ませる
2. `now.cgi` `uuid.cgi` `validate.cgi` `convert.cgi` `visitor.cgi` で足りないか確認する
3. それでも必要なら `db.cgi` を使う
4. 新規 CGI 追加は最後の手段とする

### 8.4 API ベース URL の管理

SPEC 内にベース URL を固定文字列で埋め込まない。各アプリの `api.js` または `config.js` で集約管理する。

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

環境は `production` / `local-test` の2系統とする。GitHub Pages 本番から呼ぶ URL は本番固定。開発時はローカルHTTPサーバー（例: `python -m http.server 8000`）を起動し、`http://localhost:8000/...` 上の `test-api.html` で個別確認する。`file://` 直開きは正式手順にしない。

### 8.5 CORS ポリシー

Sakura CGI 側は GitHub Pages からの `fetch()` を許可する必要がある。許可対象オリジンは原則 `https://garyohosu.github.io` に限定し、ローカル検証が必要な場合のみ `http://localhost:8000` を追加許可する。`file://` は許可対象にしない。

### 8.6 SSL 確認

CORS に見えて SSL 証明書エラーが原因のケースがあるため、API URL はブラウザで直接開いて証明書警告が出ないものを採用する。

### 8.7 共通要件

- レスポンスは原則 JSON
- `Content-Type: application/json` を利用
- 失敗時はエラー内容を返す
- CGIファイルに実行権限を付与する
- 改行コードは LF とする

---

## 9. 各 CGI の使い分け

### 9.1 `now.cgi`

用途:

- サーバー時刻取得
- タイムゾーン付き日時の基準化
- 更新時刻表示

### 9.2 `uuid.cgi`

用途:

- 一意ID発行
- 投稿ID
- セッション識別子

### 9.3 `validate.cgi`

用途:

- JSONスキーマによる入力検証
- 投稿前チェック
- バリデーションロジックの分離

### 9.4 `convert.cgi`

用途:

- 温度、長さ、圧力などの変換
- 各種計算系ミニアプリ

### 9.5 `visitor.cgi`

用途:

- 訪問記録
- 国別ランキング
- 時間帯別統計
- オンライン数や最近の訪問状況把握

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

永続ストレージの実装は API 側責務とし、フロントからは隠蔽する。

### 9.6 `db.cgi`

用途:

- SQLite を使った汎用永続化
- `select`
- `insert`
- `update`
- `delete`
- `count`
- `create_table`

---

## 10. `db.cgi` 利用仕様

### 10.0 MVP段階の制約

MVP 段階では `db.cgi` は公開書き込みを前提にしない。

- 原則として読み取り中心
- 書き込み系（insert / update / delete）は限定用途のみ
- 公開アプリで誰でも叩ける更新系は原則禁止
- 更新系を使う場合は別途認証または制限設計が必要
- DB 名・テーブル名のホワイトリストは `db.cgi` 側で管理する（フロント側制約のみでは不十分）

### 10.1 利用条件

`db.cgi` は以下の場合にのみ採用する。

- localStorage では足りない
- データを複数端末で共有したい
- 履歴保存が必要
- 集計やランキングが必要
- 複数ユーザーの軽いデータ管理が必要

### 10.2 基本ルール

- フロントから直接SQLiteファイルには触れない
- DB操作は `db.cgi` に JSON を送る
- `action` は `query`
- `database` は拡張子なしの論理名で固定管理する
- サーバー内部で論理名を実ファイル名（例: `app003` → `app003.sqlite`）へ解決する
- `table` は仕様で固定管理する
- 許可された `operation` のみ使う

### 10.3 セキュリティルール

- プリペアドステートメント前提
- UPDATE/DELETE は WHERE 必須
- DB名をユーザー入力で決めない
- テーブル名も自由入力にしない
- APIキーやトークンが必要な機能は別途追加設計する

### 10.4 推奨JSON例

#### SELECT

```json
{
  "action": "query",
  "database": "app003",
  "operation": "select",
  "table": "users",
  "where": {"active": true},
  "limit": 10
}
```

#### INSERT

```json
{
  "action": "query",
  "database": "app003",
  "operation": "insert",
  "table": "users",
  "data": {
    "name": "Alice",
    "email": "alice@example.com"
  }
}
```

#### CREATE TABLE

`create_table` は **運用初期化用** とし、日常のアプリ操作から呼ばない。

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
- アプリID `app-003-name` に対応する DB 論理名は `app003` とする

---

## 11. 実装エンジン仕様

### 11.1 Codex CLI の位置付け

Codex CLI は本プロジェクトにおける主実装エンジンである。

担当範囲:

- HTML/CSS/JavaScript 実装
- 既存コード修正
- リファクタ
- README/spec更新
- テストページ作成
- API統合コード作成

### 11.2 OpenClaw の位置付け

OpenClaw はコードを直接大量生成する主体ではなく、以下に集中する。

- 役割分担
- 工程管理
- 情報整理
- タスク分解
- Codex CLI への委任文作成
- 品質判定
- 改善ループ管理

### 11.3 Codex CLI 委任書フォーマット

**参考実装:** `C:\PROJECT\daily-ai-agent\fetch_gmail_spec.md`

委任書は `artifacts/prompts/task-xxx.md` として保存し、Codex CLI に渡す。
冒頭に必ず `Status: Draft for Codex CLI` を記載する。

```markdown
# task-xxx: [対象ファイル名] 仕様書
Project: openclaw-app-company
Phase: [フェーズ番号]
Status: Draft for Codex CLI

---

## 1. 目的
[何を作るか1〜2文で]

## 2. スコープ

### 2.1 このタスクが行うこと
- ...

### 2.2 このタスクが行わないこと（責務外）
- ...

## 3. 前提条件
- ...

## 4. 入出力
- 入力ファイル: artifacts/xxx/yyy.md
- 出力ファイル: apps/app-xxx-name/index.html

## 5. 画面要件 / 動作要件
- ...

## 6. Pages サブパス制約
- 相対パスで動作すること
- ...

## 7. API 利用有無 / DB 利用有無
- runtime_mode: static / toolbox / db

## 8. 完了条件
- ...

## 9. テスト観点
- ...

## 10. 禁止事項
- ...
```

### 11.4 Codex CLI 採否フロー

Codex CLI は実装者であって決裁者ではない。生成されたコードは以下のフローで採否を判定する。

1. **一次判定:** Tech Lead Agent（実装意図との合致確認）
2. **品質判定:** TDD Enforcer / Bug Triage Agent / Browser Test Operator
3. **最終採用:** COO Agent または GitHub Pages Release Manager

委任文は `artifacts/prompts/task-xxx.md` としてファイル生成し、Codex CLI に渡す。実行ログも保存する。

### 11.5 Codex CLI 実装順序

1. 静的版を先に作る
2. APIが必要なら `test-api.html` を作る
3. DBが必要なら公開用 `test-db-readonly.html` を作り、必要に応じてローカル専用DB確認ページを用意する
4. 疎通確認後に本体へ統合する
5. README と spec を更新する
6. 採否フロー（11.4）を通す

---

## 12. 30体エージェントの組織仕様

### 経営層

1. CEO Agent
2. COO Agent
3. ROI Agent

### リサーチ部

4. Market Researcher
5. Trend Analyst
6. Pain Finder
7. Competitor Analyst
8. Idea Scorer

### 企画部

9. Product Planner
10. UX Scenario Writer
11. Value Proposition Agent
12. PRD Writer

### 設計部

13. Solution Architect
14. Frontend Architect
15. API Integration Architect
16. ADR Writer

### 実装管理部

17. Tech Lead Agent
18. Task Breakdown Agent
19. Codex Prompt Writer
20. Refactor Director

### QA部

21. Test Designer
22. TDD Enforcer
23. Bug Triage Agent
24. Browser Test Operator

### デザイン部

25. Design Critic
26. Copy Critic
27. Accessibility Reviewer

### リリース・改善部

28. GitHub Pages Release Manager
29. Sakura API Coordinator
30. Improvement Strategist

---

## 13. 各エージェントの責務

### 13.1 CEO Agent

- 作る価値があるか判断する
- 最終優先順位を決める
- スプリント継続可否を判断する

### 13.2 COO Agent

- 工程を前に進める
- 部門間依頼を回す
- 詰まりを可視化する

### 13.3 ROI Agent

- 作る意味を点検する
- 労力と価値の釣り合いを確認する

### 13.4 Market Researcher

- 市場やニーズを調査する

### 13.5 Trend Analyst

- 今の技術動向や話題性を整理する

### 13.6 Pain Finder

- ユーザーの不満や面倒を掘り出す

### 13.7 Competitor Analyst

- 競合や類似サービスを比較する

### 13.8 Idea Scorer

- 実装難度、価値、話題性、Pages適性で点数化する

### 13.9 Product Planner

- アイデアを具体的なプロダクトに変換する

### 13.10 UX Scenario Writer

- 典型的な利用シナリオを作る

### 13.11 Value Proposition Agent

- 一文で価値提案を定義する

### 13.12 PRD Writer

- PRD を書く

### 13.13 Solution Architect

- システム全体構成を決める

### 13.14 Frontend Architect

- UI構成、画面遷移、状態管理を決める

### 13.15 API Integration Architect

- Static / Toolbox / DB のどれにするか決める
- 使う CGI を選定する

### 13.16 ADR Writer

- 技術上の判断を文書化する

### 13.17 Tech Lead Agent

- 実装順序を設計する
- 委任単位を決める

### 13.18 Task Breakdown Agent

- PRD を実装タスクへ落とす

### 13.19 Codex Prompt Writer

- Codex CLI 向けの具体的な委任文を作る

### 13.20 Refactor Director

- コード品質改善の指示を出す

### 13.21 Test Designer

- テスト観点を定義する

### 13.22 TDD Enforcer

- 実装前に受け入れ条件を定める
- テストなし実装を差し戻す

### 13.23 Bug Triage Agent

- 不具合の優先順位を付ける

### 13.24 Browser Test Operator

- Pages本体、APIテストページ、DBテストページを確認する

### 13.25 Design Critic

- 余白、情報密度、視線誘導を審査する

### 13.26 Copy Critic

- UI文言や説明文を改善する

### 13.27 Accessibility Reviewer

- 可読性、ラベル、操作性を点検する

### 13.28 GitHub Pages Release Manager

- 公開URL確認
- `.nojekyll` 維持
- リンク切れ確認
- 一覧ページ更新

### 13.29 Sakura API Coordinator

- 既存 Toolbox で足りるか確認する
- `now.cgi` `uuid.cgi` で疎通確認する
- `visitor.cgi` と `db.cgi` の必要性を審査する
- CORS と SSL を確認する

### 13.30 Improvement Strategist

- 改善案を次スプリントへ反映する

---

## 14. エージェント実装規約（Python）

**参考実装:** `C:\PROJECT\daily-ai-agent\scripts\` 配下の各モジュール

各エージェントは `scripts/agents/agent_name.py` として実装する。以下の規約に従う。

### モジュール骨格

```python
"""
scripts/agents/market_researcher.py
Phase 1: 市場調査

入力: artifacts/research/ （既存ファイルがあれば参照）
出力: artifacts/research/research_report.md
"""

import logging
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ARTIFACTS_DIR = Path("artifacts/research")
LOGS_DIR = Path("logs")
JST = ZoneInfo("Asia/Tokyo")


def setup_logging() -> logging.Logger:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    today = datetime.now(JST).strftime("%Y-%m-%d")
    log_path = LOGS_DIR / f"market-researcher-{today}.log"
    logger = logging.getLogger("market_researcher")
    logger.setLevel(logging.DEBUG)
    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    fh = logging.FileHandler(log_path, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fmt)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(fmt)
    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger


logger = setup_logging()


def main() -> None:
    logger.info("=== market_researcher 開始 ===")
    # ... 処理 ...
    # 正常終了: return（または raise SystemExit(0)）
    # 新規なし: raise SystemExit(0)
    # 異常終了: raise SystemExit(1)
    logger.info("=== market_researcher 完了 ===")


if __name__ == "__main__":
    import os, sys
    os.chdir(Path(__file__).parent.parent.parent)  # リポジトリルートに固定
    main()
```

### 規約まとめ

| 項目 | 内容 |
|-----|------|
| 正常終了 | `return` または `raise SystemExit(0)` |
| 新規なし | `raise SystemExit(0)` |
| 異常終了 | `raise SystemExit(1)` |
| ログ出力先 | `logs/agent-name-YYYY-MM-DD.log` |
| 作業ディレクトリ | リポジトリルート固定（`os.chdir`） |
| 入力 | `artifacts/` 配下のファイルを読む |
| 出力 | `artifacts/` 配下のファイルを書く |
| Codex CLI 成果物 | `apps/` 配下へ書く |

---

## 15. 開発ワークフロー

### オーケストレータ（`scripts/main.py`）の構造

**参考実装:** `C:\PROJECT\daily-ai-agent\scripts\main.py`

```python
"""
scripts/main.py
オーケストレータ: 全フェーズを順番に実行する唯一の定義元

使い方:
  python scripts/main.py                  # 全フェーズ実行
  python scripts/main.py --dry-run        # ファイル生成・状態遷移確認のみ（Git操作なし）
  python scripts/main.py --phase research # 特定フェーズのみ実行
"""
```

各フェーズは `run_phase(name, fn)` ヘルパーで実行し、
異常終了（`SystemExit(1)`）が発生した場合は後続フェーズをスキップして終了する。

`scripts/main.py` はローカル成果物作成と状態更新を担当してよい。必要に応じてローカルの `git add` / `git commit` までは自動化候補とするが、`git push`、GitHub Pages 反映、リリース扱いの更新は人間承認付き操作とする。

### フェーズ進行方式

MVP では **人間トリガー + OpenClaw 補助進行** を採用する。

1. 人間が Phase 開始を指示する
2. OpenClaw（`scripts/main.py`）が成果物確認と次工程候補を提示する
3. 人間が承認（go）を出して次フェーズへ進む

**フェーズ失敗時の対応（差し戻し方式）:**

- `artifacts/sprints/sprint-xx/failure_report.md` を作成する
- `state/company_state.json` の `next_action` を記録する
- 前フェーズの成果物は保持する
- 修正後に同一フェーズを再実行する

---

### Phase 0: 初期化

成果物:

- `agents/agents.yaml`
- `docs/org-chart.md`
- `SPEC.md`
- `state/schema.md`
- `state/example-company_state.json`
- `state/company_state.json`（実行時生成、`.gitignore` 対象）
- `scripts/main.py`
- `scripts/agents/__init__.py`

### Phase 1: 市場調査

成果物:

- `artifacts/research/research_report.md`
- `artifacts/research/idea_pool.md`
- `artifacts/research/scored_ideas.md`

最低条件:

- 候補10件以上
- 誰向けかが明確
- Pages向きか判定済み

### Phase 2: アイデア選定

成果物:

- `artifacts/research/selected_idea.md`

判定軸:

- 小さく作れる
- デモ映えする
- Pagesで公開しやすい
- Static/Toolbox/DB の見通しがよい

### Phase 3: PRD 作成

成果物:

- `artifacts/product/prd.md`

必須項目:

- 背景
- 課題
- 想定ユーザー
- ユースケース
- MVP範囲
- 非機能要件
- 成功指標
- 非対象範囲
- runtime_mode

### Phase 4: 設計

成果物:

- `artifacts/design/system_design.md`
- `artifacts/design/adr/*.md`

設計対象:

- フォルダ名
- URLパス
- 画面構成
- 状態管理
- APIエンドポイント一覧
- DB利用の有無

### Phase 5: タスク分解

成果物:

- `artifacts/design/tasks.md`

各タスク必須項目:

- task_id
- 目的
- 対象ファイル
- 入出力
- 完了条件
- UI条件
- テスト条件
- Pages制約
- API制約

### Phase 6: Codex CLI 委任書作成

成果物:

- `artifacts/prompts/task-001.md`
- `artifacts/prompts/task-002.md`
- ...（タスク数分）

担当:

- 主担当: Codex Prompt Writer
- レビュー: Tech Lead Agent

各委任書は Section 11.3 のテンプレートに従い `Status: Draft for Codex CLI` を冒頭に記載する。

### Phase 7: API疎通確認

必要時のみ実施。

成果物:

- `artifacts/qa/api_connectivity_report.md`

内容:

- SSL確認
- CORS確認
- `now.cgi` か `uuid.cgi` で疎通確認

### Phase 8: DB接続確認

DB利用時のみ実施。

成果物:

- `artifacts/qa/db_connectivity_report.md`

内容:

- `select`
- `insert`
- `count`
- エラー系確認

### Phase 9: Codex CLI 実装

成果物:

- 共通: `/apps/...` 内コード、`README.md`、`spec.md`
- `runtime_mode: toolbox` または `db`: `api.js`、`test-api.html`
- `runtime_mode: db`: 公開用 `test-db-readonly.html`
- `runtime_mode: db` かつ書き込み確認が必要な場合: ローカル専用DB確認ページ

### Phase 10: テスト

成果物:

- `artifacts/qa/qa_report.md`
- `artifacts/qa/browser_test_report.md`
- `artifacts/qa/design_review.md`

### Phase 11: GitHub Pages 公開

成果物:

- `artifacts/sprints/deploy_report.md`

内容:

- 公開URL
- ビルド状態
- 既知の問題
- 一覧ページ反映状況

### Phase 12: 改善スプリント

成果物:

- `docs/roadmap.md`
- `artifacts/sprints/sprint_next.md`

---

## 16. テスト仕様

### 15.1 Static 共通テスト

- Pages 上で表示できる
- 相対パスが壊れない
- サブパスでも動作する
- localStorage が機能する
- モバイル幅で崩れない

### 15.2 API テスト

- `test-api.html` で応答を確認できる
- CORSで失敗しない
- SSL警告がない
- エラー表示がわかる

### 15.3 DB テスト

- 公開用 `test-db-readonly.html` で `select` / `count` を確認できる
- ローカル専用確認ページで `insert` を確認できる
- 不正操作時に適切に失敗する
- `update` / `delete` は MVP では任意とし、必要時は ADR と認証方針を追加する

### 15.4 Visitor テスト

- `visitor.cgi` に `visit` が送れる
- `stats` で統計が取れる
- 自動更新時に壊れない

### 15.5 UX テスト

- 迷わない導線
- エラー文が理解しやすい
- 空状態が説明されている
- 操作ボタンが明確

---

## 17. 品質ゲート

### G1: アイデア品質

- 問題が具体的
- Pagesに向く
- 作る意味がある

### G2: 設計品質

- Static/Toolbox/DB の選択が妥当
- 過剰設計がない
- 実装粒度が適切

### G3: 疎通品質

- SSL確認済み
- CORS確認済み
- テストページで再現できる

### G4: 実装品質

- 読める構成
- 不要な依存が少ない
- Pagesで動く

### G5: UX品質

- デモ感だけで終わっていない
- 情報の主従がある
- 文言が自然

### G6: 公開品質

- 一覧ページから辿れる
- 公開URLが有効
- known issues が整理されている
- 本体ページに AdSense タグが埋め込まれている
- AdSense 埋め込みによるレイアウト崩れがない
- テストページに AdSense が混入していない

---

## 18. デザイン原則

### 17.1 目標

- Apple/Notion級を目標にする
- 余白で整理する
- 画面情報を詰め込みすぎない
- 配色を増やしすぎない
- ボタンを増やしすぎない

### 17.2 禁止事項

- 無意味な派手アニメーション
- 境界線だらけ
- 色だらけ
- 長文だらけ
- AIが適当に並べた感のあるUI

### 17.3 審査項目

- 余白
- 階層
- タイポグラフィ
- CTAの明快さ
- エラー文
- 空状態
- 可読性

---

## 19. 運用ルール

### 18.1 Git運用

- 各アプリ追加はディレクトリ単位で完結する
- README と spec は同時更新する
- ルート一覧も更新する
- 破壊的変更は ADR に記録する
- `git push` と公開反映は人間承認付き操作とする

### 18.2 アプリ番号採番ルール

`app-xxx-name` の `xxx` は **3桁連番** とする。

- 新規作成時に次番号を採番する（例: app-001, app-002, app-003）
- 廃止しても **欠番を維持** し、番号は再利用しない
- 理由: URL・ログ参照の安定性、および過去記録との混同防止

### 18.3 新規アプリ追加手順

1. アイデア選定
2. `app-xxx-name` フォルダ作成（3桁連番で採番）
3. `spec.md` 作成
4. 静的版作成
5. 必要なら `test-api.html` 追加
6. DB利用時は必要に応じて `test-db-readonly.html` とローカル専用DB確認ページを追加
7. 採否フロー（11.4）を通す
8. Pages 公開
9. 一覧更新

### 18.4 API追加ルール

新規 CGI を追加する前に、既存 Toolbox で代替可能か必ず審査する。

### 18.5 DB追加ルール

- DB論理名は固定管理
- テーブル名は固定管理
- スキーマ変更は ADR を作る
- 個人用用途であることを前提にする

---

## 20. セキュリティ方針

- GitHub Pages 側に秘密情報を置かない
- APIキーやトークンは必要最小限にする
- CORS は許可オリジンを限定する
- SQL操作は `db.cgi` の許可範囲に限定する
- 直接ファイルアクセスは禁止する
- 危険な更新系操作には設計審査を通す
- 書き込み確認用ページは本番公開しない
- 公開用DB確認ページは read only に限定する

### 20.1 セキュリティ審査フロー

認証なし書き込み・外部APIキー使用・危険な更新系操作は必ず以下を通す。

| 審査段階 | 担当 |
|---------|-----|
| 一次審査 | API Integration Architect |
| 二次審査 | Sakura API Coordinator |
| 最終承認 | COO Agent |

記録場所:
- `artifacts/security/security_review.md`
- 設計変更を伴う場合は `artifacts/design/adr/` にも記録する

---

## 21. 状態管理ファイル

`state/company_state.json` の例:

```json
{
  "current_phase": "implementation",
  "current_phase_number": 8,
  "current_sprint": 1,
  "selected_app": "app-001-sample",
  "deployment_target": "github-pages",
  "runtime_mode": "toolbox",
  "api_endpoints": ["uuid.cgi", "visitor.cgi"],
  "quality_gate": {
    "pages_ready": true,
    "ssl_verified": true,
    "cors_verified": true,
    "browser_test_passed": false
  },
  "next_action": "fix-relative-path-bug"
}
```

`current_phase` は英語識別子で持つ。正規の enum は `initialization` `research` `idea_selection` `product` `design` `task_breakdown` `prompt_creation` `api_connectivity` `db_connectivity` `implementation` `testing` `release` `improvement` とする。詳細なレビューステップを区別したい場合は `sub_phase` または `next_action` で補助管理する。

---

## 22. 各アプリの `spec.md` テンプレート項目

各アプリの `spec.md` には少なくとも以下を含める。

- app_id
- app_name
- summary
- target_user
- main_use_cases
- runtime_mode (`static` / `toolbox` / `db`)
- api_endpoints
- storage_strategy
- visitor_tracking
- cors_origin
- ssl_checked
- pages_path
- known_constraints
- acceptance_criteria
- adsense_required (`true` / `false`)
- adsense_applied (`true` / `false`)
- adsense_checked_at_release (`true` / `false`)

---

## 23. 想定ユースケース

この工場ラインで作りやすいアプリ例:

- メモ整理ツール
- UUIDや時刻を使う投稿支援ツール
- 単位変換ツール
- 記事補助ツール
- 訪問者可視化ダッシュボード
- 軽いデータ保存型ツール
- ミニCRM
- フォーム受付

---

## 24. MVP 範囲

初期MVPで必ずやること:

- 30体のロール定義（`agents/agents.yaml` 作成）
- `scripts/main.py` を作成する（OpenClaw オーケストレータ）
- 1つのアプリを企画から公開まで回す
- GitHub Pages 一覧ページを作る（`build-index.py` で生成）
- Codex CLI による実装委任を成立させる
- `test-api.html` を含む構成を標準化する
- 必要なら `db.cgi` の最小接続確認を行う
- `.github/workflows/deploy.yml` を作成する
- `scripts/create-app-template.py` を作成する（AdSense タグ組み込み済みテンプレート生成）
- `scripts/build-index.py` を作成する（AdSense タグ組み込み済みルートページ生成）
- `state/schema.md` と `state/example-company_state.json` を作成する
- ルート `index.html` と各アプリ `index.html` に AdSense タグを組み込む

初期MVPでやらないこと:

- 完全自動24時間無停止運転
- 課金システム
- 大規模認証基盤
- 複雑なCI/CD地獄

---

## 25. この仕様の要約

本仕様は、OpenClaw 上の30体AIエージェントが仮想開発会社として役割分担し、Codex CLI を実装エンジンとして用い、複数の静的Webアプリを1つのGitHubリポジトリ内で増やし、GitHub Pages に公開し、必要な場合のみ Sakuraレンタルサーバーの CGI/Python API Toolbox を利用して機能拡張する量産型アプリ開発システムを定義する。
