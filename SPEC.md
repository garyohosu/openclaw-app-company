# OpenClaw App Company 仕様書

- リポジトリ名: `openclaw-app-company`
- デプロイ先: GitHub Pages
- 実装エンジン: Codex CLI
- オーケストレーション: OpenClaw
- バックエンド連携: Sakuraレンタルサーバー CGI/Python API Toolbox
- ドキュメント版数: v0.1
- 作成日: 2026-03-23

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

### 3.1 組織として動かす

AIを万能な一体として使うのではなく、役割を持つ複数エージェントに分割する。人間の開発組織のように、調査、企画、設計、実装、QA、運用を分ける。

### 3.2 実装と判断を分離する

- 判断、整理、優先順位付けは OpenClaw 側が担当する
- コード生成と修正は Codex CLI に委任する

### 3.3 まず静的、次に軽API、最後にDB

バックエンドは最初から持たない。以下の順で設計判断する。

1. 完全静的で成立しないか
2. 既存の軽量 CGI API Toolbox で足りないか
3. それでも足りない場合のみ `db.cgi` を使う

この順番を破ると、だいたい後で保守費が増える。

### 3.4 1リポジトリで複数アプリを増やす

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
- browser-use CLI などのブラウザ確認手段
  - E2E確認
  - 表示確認
  - API疎通テスト画面確認
- Sakuraレンタルサーバー CGI/Python API Toolbox
  - 時刻取得
  - UUID発行
  - JSON検証
  - 単位変換
  - 訪問者記録
  - SQLite汎用DB API

### 4.2 採用理由

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
      test-db.html
  /artifacts
    /research
    /prd
    /design
    /qa
    /sprints
  /docs
    workflow.md
    org-chart.md
    roadmap.md
  /shared
    /components
    /styles
    /utils
  /scripts
    create-app-template.py
    build-index.py
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
- テストページへのリンク

### 5.2 `.nojekyll`

GitHub Pages で不要な変換を避けるため、`.nojekyll` を配置する。

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

- `test-db.html`

### 6.4 設計原則

- できるだけ単体で動作すること
- 相対パスで動作すること
- Pages のサブパスで壊れないこと
- 他アプリへの依存を減らすこと
- API利用は `api.js` に集約すること
- DB操作は必ず `db.cgi` 経由とすること

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

### 8.4 CORS ポリシー

Sakura CGI 側は GitHub Pages からの `fetch()` を許可する必要がある。許可対象オリジンは原則 `https://garyohosu.github.io` に限定する。

### 8.5 SSL 確認

CORS に見えて SSL 証明書エラーが原因のケースがあるため、API URL はブラウザで直接開いて証明書警告が出ないものを採用する。

### 8.6 共通要件

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
- `database` と `table` は仕様で固定管理する
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
  "database": "myapp",
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
  "database": "myapp",
  "operation": "insert",
  "table": "users",
  "data": {
    "name": "Alice",
    "email": "alice@example.com"
  }
}
```

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

### 11.3 Codex CLI 委任テンプレート必須項目

各タスクでは以下を必須とする。

- 目的
- 対象ファイル
- 画面要件
- 動作要件
- Pages サブパス制約
- API利用有無
- DB利用有無
- 完了条件
- テスト観点
- 禁止事項

### 11.4 Codex CLI 実装順序

1. 静的版を先に作る
2. APIが必要なら `test-api.html` を作る
3. DBが必要なら `test-db.html` を作る
4. 疎通確認後に本体へ統合する
5. README と spec を更新する

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

## 14. 開発ワークフロー

### Phase 0: 初期化

成果物:

- `agents/agents.yaml`
- `docs/org-chart.md`
- `SPEC.md`
- `state/company_state.json`

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

- `artifacts/prd/prd.md`

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

### Phase 6: API疎通確認

必要時のみ実施。

成果物:

- `artifacts/qa/api_connectivity_report.md`

内容:

- SSL確認
- CORS確認
- `now.cgi` か `uuid.cgi` で疎通確認

### Phase 7: DB接続確認

DB利用時のみ実施。

成果物:

- `artifacts/qa/db_connectivity_report.md`

内容:

- `select`
- `insert`
- `count`
- エラー系確認

### Phase 8: Codex CLI 実装

成果物:

- `/apps/...` 内コード
- `README.md`
- `spec.md`
- `api.js`
- `test-api.html`
- `test-db.html`

### Phase 9: テスト

成果物:

- `artifacts/qa/qa_report.md`
- `artifacts/qa/browser_test_report.md`
- `artifacts/qa/design_review.md`

### Phase 10: GitHub Pages 公開

成果物:

- `artifacts/sprints/deploy_report.md`

内容:

- 公開URL
- ビルド状態
- 既知の問題
- 一覧ページ反映状況

### Phase 11: 改善スプリント

成果物:

- `docs/roadmap.md`
- `artifacts/sprints/sprint_next.md`

---

## 15. テスト仕様

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

- `test-db.html` でCRUDの最小確認ができる
- `count` が使える
- 不正操作時に適切に失敗する

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

## 16. 品質ゲート

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

---

## 17. デザイン原則

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

## 18. 運用ルール

### 18.1 Git運用

- 各アプリ追加はディレクトリ単位で完結する
- README と spec は同時更新する
- ルート一覧も更新する
- 破壊的変更は ADR に記録する

### 18.2 新規アプリ追加手順

1. アイデア選定
2. `app-xxx-name` フォルダ作成
3. `spec.md` 作成
4. 静的版作成
5. 必要なら `test-api.html` 追加
6. 必要なら `test-db.html` 追加
7. Pages 公開
8. 一覧更新

### 18.3 API追加ルール

新規 CGI を追加する前に、既存 Toolbox で代替可能か必ず審査する。

### 18.4 DB追加ルール

- DB名は固定管理
- テーブル名は固定管理
- スキーマ変更は ADR を作る
- 個人用用途であることを前提にする

---

## 19. セキュリティ方針

- GitHub Pages 側に秘密情報を置かない
- APIキーやトークンは必要最小限にする
- CORS は許可オリジンを限定する
- SQL操作は `db.cgi` の許可範囲に限定する
- 直接ファイルアクセスは禁止する
- 危険な更新系操作には設計審査を通す

---

## 20. 状態管理ファイル

`state/company_state.json` の例:

```json
{
  "current_phase": "implementation",
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

---

## 21. 各アプリの `spec.md` テンプレート項目

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

---

## 22. 想定ユースケース

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

## 23. MVP 範囲

初期MVPで必ずやること:

- 30体のロール定義
- 1つのアプリを企画から公開まで回す
- GitHub Pages 一覧ページを作る
- Codex CLI による実装委任を成立させる
- `test-api.html` を含む構成を標準化する
- 必要なら `db.cgi` の最小接続確認を行う

初期MVPでやらないこと:

- 完全自動24時間無停止運転
- 課金システム
- 大規模認証基盤
- 複雑なCI/CD地獄

---

## 24. この仕様の要約

本仕様は、OpenClaw 上の30体AIエージェントが仮想開発会社として役割分担し、Codex CLI を実装エンジンとして用い、複数の静的Webアプリを1つのGitHubリポジトリ内で増やし、GitHub Pages に公開し、必要な場合のみ Sakuraレンタルサーバーの CGI/Python API Toolbox を利用して機能拡張する量産型アプリ開発システムを定義する。

