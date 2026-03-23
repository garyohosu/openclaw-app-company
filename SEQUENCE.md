# SEQUENCE.md — OpenClaw App Company シーケンス図

- 対象: SPEC.md v0.7
- 作成日: 2026-03-23

---

## 1. メインオーケストレーション（フェーズ起動・進行フロー）

運営者が `scripts/main.py` を起動し、各フェーズを順に進める全体フロー。

```mermaid
sequenceDiagram
    actor 運営者
    participant main as scripts/main.py<br>(OpenClaw)
    participant state as state/company_state.json
    participant agent as scripts/agents/<br>agent_name.py
    participant artifacts as artifacts/

    運営者 ->> main: python scripts/main.py --phase research
    main ->> state: current_phase 読み込み
    state -->> main: current_phase: "research"

    loop 各フェーズ（Phase 1 〜 12）
        main ->> agent: run_phase(name, fn) → fn()
        agent ->> artifacts: 入力ファイル読み込み
        artifacts -->> agent: 既存成果物
        agent ->> artifacts: 成果物ファイル書き出し
        agent -->> main: return (正常) / SystemExit(1) (異常)

        alt 正常終了
            main ->> state: current_phase 更新
            main ->> 運営者: 成果物確認・次フェーズ候補を提示
            運営者 ->> main: 承認（go）
        else 異常終了
            main ->> artifacts: sprints/sprint-xx/failure_report.md 作成
            main ->> state: next_action を記録
            main ->> 運営者: 失敗通知・差し戻し
            main --x main: 後続フェーズをスキップして終了
        end
    end
```

---

## 2. run_phase ヘルパーの詳細フロー

`run_phase()` が各エージェントの `main()` を呼び出し、終了コードを判定する。

```mermaid
sequenceDiagram
    participant main as scripts/main.py
    participant helper as run_phase(name, fn)
    participant agent as agent.main()
    participant log as logs/<br>agent-YYYY-MM-DD.log

    main ->> helper: run_phase("market_researcher", m.main)
    helper ->> agent: fn() 呼び出し
    agent ->> log: ログ出力開始

    alt 正常終了（return / SystemExit(0)）
        agent -->> helper: return または SystemExit(0)
        helper -->> main: True
        main ->> log: ✓ 完了ログ
    else 新規なし（SystemExit(0)）
        agent -->> helper: SystemExit(0)
        helper -->> main: True（新規なし扱い）
        main ->> log: ✓ 完了（新規なし）ログ
    else 異常終了（SystemExit(1)）
        agent -->> helper: SystemExit(1)
        helper -->> main: False
        main ->> log: ✗ 失敗ログ
        main --x main: sys.exit(1) で後続スキップ
    else 未捕捉例外
        agent -->> helper: Exception
        helper -->> main: False
        main ->> log: ✗ 例外ログ
        main --x main: sys.exit(1) で後続スキップ
    end
```

---

## 3. 市場調査〜アイデア選定フロー（Phase 1〜2）

Market Researcher が3系統の入力から調査し、ROI Agent が二段階で評価する。

```mermaid
sequenceDiagram
    actor 運営者
    participant MR as Market Researcher
    participant TA as Trend Analyst
    participant PF as Pain Finder
    participant CA as Competitor Analyst
    participant IS as Idea Scorer
    participant ROI as ROI Agent
    participant CEO as CEO Agent
    participant artifacts as artifacts/research/

    運営者 ->> MR: テーマ・制約・狙いを提供
    MR ->> artifacts: docs/roadmap.md 読み込み
    MR ->> artifacts: 過去スプリントメモ読み込み
    Note over MR: 公開Web情報も参照<br>（出典を source_notes.md に記録）
    MR ->> artifacts: research_report.md + source_notes.md 書き出し

    TA ->> artifacts: research_report.md 読み込み
    TA ->> artifacts: idea_pool.md に技術動向・話題性追記

    PF ->> artifacts: idea_pool.md 読み込み
    PF ->> artifacts: idea_pool.md にユーザーの不満・課題追記

    CA ->> artifacts: idea_pool.md 読み込み
    CA ->> artifacts: idea_pool.md に競合・類似サービス比較追記

    IS ->> artifacts: idea_pool.md 読み込み
    Note over IS: 実装難度・価値・話題性・Pages適性でスコア化
    IS ->> artifacts: scored_ideas.md 書き出し

    Note over ROI: Phase 2: 軽量ROI評価（足切り）
    ROI ->> artifacts: scored_ideas.md 読み込み
    ROI -->> IS: 価値が低い案を除外依頼
    IS ->> artifacts: scored_ideas.md 更新

    CEO ->> artifacts: scored_ideas.md 読み込み
    CEO ->> 運営者: 方向性確認
    運営者 -->> CEO: 承認
    CEO ->> artifacts: selected_idea.md 書き出し
```

---

## 4. PRD 作成フロー（Phase 3）

企画部が PRD を作成し、ROI Agent が詳細評価する。

```mermaid
sequenceDiagram
    participant PP as Product Planner
    participant UX as UX Scenario Writer
    participant VP as Value Proposition Agent
    participant PW as PRD Writer
    participant ROI as ROI Agent
    participant COO as COO Agent
    participant artifacts as artifacts/product/

    PP ->> artifacts: selected_idea.md 読み込み
    PP ->> artifacts: prd.md（ドラフト）書き出し

    UX ->> artifacts: prd.md 読み込み
    UX ->> artifacts: prd.md にユースケース追記

    VP ->> artifacts: prd.md 読み込み
    VP ->> artifacts: prd.md に価値提案を一文で追記

    Note over ROI: Phase 3: PRD詳細ROI評価
    ROI ->> artifacts: prd.md 読み込み
    alt MVP サイズに収まっている
        ROI -->> PW: 承認
    else 企画が広がりすぎ / 収益導線が破綻
        ROI -->> PW: 差し戻し・スコープ縮小依頼
        PW ->> artifacts: prd.md 修正
    end

    PW ->> artifacts: prd.md 確定版書き出し
    COO -->> PW: PRD 確定承認
```

---

## 5. 設計〜タスク分解フロー（Phase 4〜5）

```mermaid
sequenceDiagram
    participant SA as Solution Architect
    participant FA as Frontend Architect
    participant AA as API Integration Architect
    participant AW as ADR Writer
    participant TL as Tech Lead Agent
    participant TB as Task Breakdown Agent
    participant artifacts as artifacts/design/

    SA ->> artifacts: prd.md 読み込み
    SA ->> artifacts: system_design.md 書き出し

    FA ->> artifacts: system_design.md 読み込み
    FA ->> artifacts: system_design.md に画面構成・状態管理追記

    AA ->> artifacts: system_design.md 読み込み
    Note over AA: Static / Toolbox / DB の選定
    AA ->> artifacts: system_design.md に runtime_mode 確定追記

    AW ->> artifacts: adr/adr-xxx.md 書き出し

    TL ->> artifacts: system_design.md 読み込み
    TL ->> artifacts: 実装順序・委任単位の設計追記

    TB ->> artifacts: system_design.md 読み込み
    TB ->> artifacts: tasks.md 書き出し
    Note over TB: task_id / 目的 / 対象ファイル /<br>入出力 / 完了条件 を各タスクに記載
```

---

## 6. API 疎通確認フロー（Phase 6）

必要時のみ実施。Sakura API Coordinator が主担当。

```mermaid
sequenceDiagram
    participant SC as Sakura API Coordinator
    participant local as ローカル HTTP サーバー<br>http://localhost:8000
    participant sakura as Sakura CGI Toolbox<br>now.cgi / uuid.cgi
    participant artifacts as artifacts/qa/

    Note over SC: runtime_mode が toolbox / db の場合のみ実施
    SC ->> local: test-api.html をブラウザで開く
    local ->> sakura: fetch() → now.cgi SSL 確認
    sakura -->> local: 200 OK + JSON（時刻）
    local ->> sakura: fetch() → uuid.cgi CORS 確認
    sakura -->> local: 200 OK + JSON（UUID）

    alt SSL / CORS いずれかでエラー
        local -->> SC: エラー詳細
        SC ->> artifacts: api_connectivity_report.md（NG 記録）
        SC -->> SC: 差し戻し
    else 正常
        SC ->> artifacts: api_connectivity_report.md（OK 記録）
    end
```

---

## 7. DB 接続確認フロー（Phase 7）

DB 利用時のみ実施。

```mermaid
sequenceDiagram
    participant BTO as Browser Test Operator
    participant local as ローカル HTTP サーバー<br>http://localhost:8000
    participant dbcgi as db.cgi<br>(Sakura CGI)
    participant artifacts as artifacts/qa/

    Note over BTO: runtime_mode が db の場合のみ実施
    BTO ->> local: ローカル専用DB確認ページを開く

    BTO ->> local: select テスト
    local ->> dbcgi: POST {action:"query", operation:"select", ...}
    dbcgi -->> local: JSON レスポンス

    BTO ->> local: insert テスト
    local ->> dbcgi: POST {action:"query", operation:"insert", ...}
    dbcgi -->> local: JSON レスポンス

    BTO ->> local: count テスト
    local ->> dbcgi: POST {action:"query", operation:"count", ...}
    dbcgi -->> local: JSON レスポンス

    BTO ->> local: エラー系テスト（不正パラメータ等）
    local ->> dbcgi: POST（不正リクエスト）
    dbcgi -->> local: エラー JSON

    alt 全テスト通過
        BTO ->> artifacts: db_connectivity_report.md（OK 記録）
    else テスト失敗
        BTO ->> artifacts: db_connectivity_report.md（NG 記録）
        BTO -->> BTO: 差し戻し
    end
```

---

## 8. Codex CLI 委任フロー（Phase 8〜9）

疎通確認後に委任書を確定し、Codex CLI にコード生成を委任する。

```mermaid
sequenceDiagram
    participant TL as Tech Lead Agent
    participant CP as Codex Prompt Writer
    participant main as scripts/main.py<br>(OpenClaw)
    participant codex as Codex CLI
    participant apps as apps/app-xxx-name/
    participant artifacts as artifacts/prompts/

    Note over CP: Phase 6/7 の疎通確認結果を参照
    CP ->> artifacts: tasks.md 読み込み
    CP ->> artifacts: task-001.md 書き出し<br>(Status: Draft for Codex CLI)
    CP ->> artifacts: task-002.md 書き出し
    Note over CP,TL: タスク数分繰り返し

    TL ->> artifacts: task-xxx.md レビュー
    TL -->> CP: 差し戻し or 承認

    Note over main: Phase 9: Codex CLI 実装
    main ->> artifacts: task-001.md 読み込み
    main ->> codex: ファイル内容を渡す<br>(stdin or --file)
    codex ->> apps: index.html / style.css / app.js 生成
    codex ->> apps: api.js / test-api.html 生成（必要時）
    codex ->> apps: README.md / spec.md 更新
    codex -->> main: 実装完了

    main ->> artifacts: 実行ログ保存（logs/配下）
```

---

## 9. テスト・品質審査フロー（Phase 10）

```mermaid
sequenceDiagram
    participant TD as Test Designer
    participant TDD as TDD Enforcer
    participant BTA as Bug Triage Agent
    participant BTO as Browser Test Operator
    participant DC as Design Critic
    participant CC as Copy Critic
    participant AR as Accessibility Reviewer
    participant artifacts as artifacts/qa/

    TD ->> artifacts: qa_report.md（テスト観点定義）書き出し

    TDD ->> artifacts: 受け入れ条件確認
    alt 受け入れ条件なしで実装されている
        TDD -->> TDD: 実装差し戻し（Phase 9 へ）
    end

    BTO ->> BTO: Pages 本体ページをブラウザで確認
    BTO ->> BTO: test-api.html で API 疎通再確認
    BTO ->> BTO: test-db-readonly.html で DB 読み取り確認
    BTO ->> artifacts: browser_test_report.md 書き出し

    BTA ->> artifacts: browser_test_report.md 読み込み
    BTA ->> artifacts: qa_report.md に不具合優先度追記

    DC ->> DC: 余白・情報密度・視線誘導を審査
    CC ->> CC: UI 文言・説明文を審査
    AR ->> AR: 可読性・ラベル・操作性を審査
    DC ->> artifacts: design_review.md 書き出し
```

---

## 10. GitHub Pages 公開フロー（Phase 11）

AdSense 確認を含むリリースゲートを通過した後、人間承認で push する。

```mermaid
sequenceDiagram
    actor 運営者
    participant RM as GitHub Pages<br>Release Manager
    participant main as scripts/main.py
    participant git as Git（ローカル）
    participant ghp as GitHub Pages
    participant artifacts as artifacts/sprints/

    main ->> RM: Phase 11 開始

    Note over RM: AdSense 判定フロー（USECASE.md 図6 準拠）
    RM ->> RM: ① 収益対象ページ全体に AdSense タグあるか確認<br>（ルート index.html・各アプリ index.html 等）

    alt ① AdSense タグなし
        RM -->> main: Release NG（タグ未埋め込み）
        main -->> 運営者: AdSense 修正要求
        運営者 ->> main: 修正後に再実行
    else ① OK
        RM ->> RM: ② AdSense によるレイアウト崩れなし確認

        alt ② レイアウト崩れあり
            RM -->> main: Release NG（レイアウト崩れ）
            main -->> 運営者: AdSense 修正要求
            運営者 ->> main: 修正後に再実行
        else ② OK
            RM ->> RM: ③ テストページ・管理ページへの AdSense 混入なし確認

            alt ③ 混入あり
                RM -->> main: Release NG（テストページ混入）
                main -->> 運営者: AdSense 修正要求
                運営者 ->> main: 修正後に再実行
            else ③ OK → Release OK
                RM ->> RM: 一覧ページ・公開URL・known issues 確認
                RM ->> artifacts: deploy_report.md 書き出し
                RM -->> 運営者: リリース承認依頼
                運営者 ->> git: git push origin main（手動承認操作）
                git ->> ghp: GitHub Pages ビルド & デプロイ
                ghp -->> 運営者: 公開完了
            end
        end
    end
```

---

## 11. エンドユーザーのアプリ利用フロー

公開後のアプリをエンドユーザーが利用し、visitor.cgi に自動記録される。

```mermaid
sequenceDiagram
    actor エンドユーザー
    participant ghp as GitHub Pages
    participant app as 公開アプリ JS<br>(app.js / api.js)
    participant visitor as visitor.cgi<br>(Sakura CGI)
    participant toolbox as now.cgi / uuid.cgi 等<br>(Sakura CGI)
    participant dbcgi as db.cgi<br>(Sakura CGI)

    エンドユーザー ->> ghp: https://garyohosu.github.io/...
    ghp -->> エンドユーザー: HTML / CSS / JS 配信

    opt visitor_tracking: true の場合（USECASE.md 図4 準拠）
        app ->> visitor: fetch() POST {action:"visit", app_id:..., page:..., referrer:...}
        visitor -->> app: {status:"ok"}
    end

    alt Static アプリ
        エンドユーザー ->> app: 操作（変換・メモ等）
        app ->> app: localStorage / URLパラメータ で完結
    else Toolbox アプリ
        エンドユーザー ->> app: 操作
        app ->> toolbox: fetch() （now.cgi / uuid.cgi 等）
        toolbox -->> app: JSON レスポンス
        app -->> エンドユーザー: 結果表示
    else DB アプリ
        エンドユーザー ->> app: 操作（閲覧中心）
        app ->> dbcgi: fetch() POST {action:"query", operation:"select", ...}
        dbcgi -->> app: JSON データ
        app -->> エンドユーザー: 結果表示
    end
```

---

## 12. 改善スプリントのループ判断フロー（Phase 12）

フィードバックを収集し、次の行き先（Phase 1 か Phase 5 か）を判断する。

```mermaid
sequenceDiagram
    participant IS as Improvement Strategist
    participant COO as COO Agent
    participant CEO as CEO Agent
    actor 運営者
    participant artifacts as artifacts/sprints/
    participant main as scripts/main.py

    IS ->> artifacts: visitor.cgi 利用状況データ読み込み
    IS ->> artifacts: GitHub Issue・運営者メモ読み込み
    IS ->> artifacts: QA で残った改善点読み込み
    IS ->> artifacts: user_feedback.md 書き出し
    IS ->> artifacts: usage_insights.md 書き出し

    IS -->> COO: ループバック先の一次提案<br>（Phase 1 または Phase 5）

    COO ->> artifacts: sprint_next.md（改善案まとめ）書き出し
    COO -->> CEO: 妥当性確認依頼

    alt 同一アプリ改善（PRD 不要・タスク分解から再開）
        CEO -->> 運営者: Phase 5 ループバック承認
        運営者 ->> main: python scripts/main.py --phase task_breakdown
    else 新規アプリ追加（新テーマ探索・別カテゴリ）
        CEO -->> 運営者: Phase 1 ループバック承認
        運営者 ->> main: python scripts/main.py --phase research
    end

    main ->> artifacts: docs/roadmap.md 更新
```

---

_以上。不明点は QandA.md に追記。_
