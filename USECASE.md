# USECASE.md — OpenClaw App Company ユースケース図

- 対象: SPEC.md v0.5
- 作成日: 2026-03-23

---

## 1. アクター一覧

| アクター | 種別 | 説明 |
|---------|-----|------|
| 運営者 | 主アクター | フェーズ開始・承認・公開判断を行う人間 |
| エンドユーザー | 主アクター | 公開されたアプリを利用する利用者 |
| Codex CLI | 外部システム | アプリコードを生成する実装エンジン |
| GitHub Pages | 外部システム | 静的アプリを配信するホスティング基盤 |
| Sakura CGI Toolbox | 外部システム | 時刻・UUID・DB等の軽量バックエンド |

---

## 2. 全体ユースケース図

```mermaid
flowchart LR
    %% ── アクター（システム外）──────────────────────
    op["👤 運営者"]
    eu["👤 エンドユーザー"]
    codex["⚙️ Codex CLI"]
    ghp["🌐 GitHub Pages"]
    sakura["🔧 Sakura CGI\nToolbox"]

    %% ── システム境界 ────────────────────────────────
    subgraph SYS["● OpenClaw App Company  システム境界"]

        subgraph GRP1["企画・調査"]
            UC01("市場調査を実施する")
            UC02("アイデアを評価・選定する")
            UC03("ROI評価を行う")
            UC04("PRDを作成する")
        end

        subgraph GRP2["設計・準備"]
            UC05("システム設計を行う")
            UC06("タスクを分解する")
            UC07("API疎通確認を行う")
            UC08("DB接続確認を行う")
            UC09("Codex CLI委任書を作成する")
        end

        subgraph GRP3["実装・品質"]
            UC10("アプリを実装する")
            UC11("AdSenseを組み込む")
            UC12("テスト・品質審査を行う")
        end

        subgraph GRP4["公開・改善"]
            UC13("GitHub Pagesに公開する")
            UC14("改善スプリントを回す")
        end

        subgraph GRP5["制御・管理"]
            UC20("フェーズ進行を制御する")
            UC21("状態ファイルを管理する")
            UC22("品質ゲートを判定する")
        end
    end

    %% ── 運営者の関連 ────────────────────────────────
    op --- UC01
    op --- UC04
    op --- UC13
    op --- UC14
    op -. "フェーズ承認" .-> UC20

    %% ── エンドユーザーの関連 ─────────────────────────
    eu --- UC13
    eu --- ghp

    %% ── 外部システムの関連 ───────────────────────────
    UC10 --- codex
    UC13 --- ghp
    UC07 --- sakura
    UC08 --- sakura
    UC10 -. "API/DB利用時" .-> sakura

    %% ── «include» ───────────────────────────────────
    UC01 -. "«include»" .-> UC02
    UC02 -. "«include»" .-> UC03
    UC04 -. "«include»" .-> UC05
    UC05 -. "«include»" .-> UC06
    UC09 -. "«include»" .-> UC10
    UC11 -. "«include»" .-> UC13
    UC12 -. "«include»" .-> UC22

    %% ── «extend» ────────────────────────────────────
    UC07 -. "«extend»\n必要時のみ" .-> UC06
    UC08 -. "«extend»\nDB利用時のみ" .-> UC07
```

---

## 3. フェーズワークフロー図

Phase 0〜12 の実行順序と、各フェーズに関与するアクターを示す。

```mermaid
flowchart TD
    %% ── フェーズノード ──────────────────────────────
    P0["🔧 Phase 0\n初期化\n成果物: agents.yaml / main.py"]
    P1["🔍 Phase 1\n市場調査"]
    P2["💡 Phase 2\nアイデア選定"]
    P3["📋 Phase 3\nPRD作成"]
    P4["🏗 Phase 4\n設計"]
    P5["🗂 Phase 5\nタスク分解"]
    P6["🔌 Phase 6\nAPI疎通確認\n必要時のみ"]
    P7["🗄 Phase 7\nDB接続確認\nDB利用時のみ"]
    P8["📝 Phase 8\nCodex CLI委任書作成"]
    P9["⚙️ Phase 9\nCodex CLI実装"]
    P10["✅ Phase 10\nテスト・品質審査"]
    P11["🚀 Phase 11\nGitHub Pages公開"]
    P12["🔁 Phase 12\n改善スプリント"]

    %% ── 主フロー ────────────────────────────────────
    P0 --> P1 --> P2 --> P3 --> P4 --> P5
    P5 --> P6
    P5 --> P7
    P6 --> P8
    P7 --> P8
    P5 -->|"Static のみ\nAPI/DB不要"| P8
    P8 --> P9 --> P10 --> P11 --> P12
    P12 -. "次アプリを追加する場合" .-> P1
    P12 -. "同一アプリを改善する場合" .-> P5

    %% ── 担当アクター ─────────────────────────────────
    op["👤 運営者"]
    claw["🐾 OpenClaw\nscripts/main.py"]
    codex["⚙️ Codex CLI"]
    ghp["🌐 GitHub Pages"]
    sakura["🔧 Sakura CGI"]

    op -. "フェーズ開始・承認" .-> P0
    op -. "公開承認（git push）" .-> P11
    claw -. "フェーズ実行・状態更新" .-> P1
    claw -. "フェーズ実行・状態更新" .-> P8
    codex -. "コード生成" .-> P9
    sakura -. "疎通確認対象" .-> P6
    sakura -. "疎通確認対象" .-> P7
    ghp -. "デプロイ先" .-> P11
```

---

## 4. アプリ利用フロー（エンドユーザー視点）

公開後のアプリをエンドユーザーがどう利用するかを示す。

```mermaid
flowchart LR
    eu["👤 エンドユーザー"]

    subgraph APP["公開アプリ（apps/app-xxx-name/）"]
        direction TB
        s_static["Static アプリ\nlocalStorage / URLパラメータ"]
        s_toolbox["Toolbox アプリ\nnow.cgi / uuid.cgi 等"]
        s_db["DB アプリ\ndb.cgi（read中心）"]
    end

    ghp["🌐 GitHub Pages"]
    sakura["🔧 Sakura CGI Toolbox"]
    visitor["📊 visitor.cgi\n訪問記録"]

    eu -->|"https://garyohosu.github.io/..."| ghp
    ghp --> s_static
    ghp --> s_toolbox
    ghp --> s_db

    s_toolbox -->|"fetch()"| sakura
    s_db -->|"fetch()"| sakura
    s_static -. "自動記録" .-> visitor
    s_toolbox -. "自動記録" .-> visitor
    s_db -. "自動記録" .-> visitor
```

---

## 5. エージェント組織と担当フェーズの対応

30体のエージェントがどのフェーズで主に動くかを示す。

```mermaid
flowchart LR
    subgraph EXEC["経営層"]
        CEO["CEO Agent"]
        COO["COO Agent"]
        ROI["ROI Agent"]
    end

    subgraph RESEARCH["リサーチ部"]
        MR["Market Researcher"]
        TA["Trend Analyst"]
        PF["Pain Finder"]
        CA["Competitor Analyst"]
        IS["Idea Scorer"]
    end

    subgraph PLAN["企画部"]
        PP["Product Planner"]
        UX["UX Scenario Writer"]
        VP["Value Proposition Agent"]
        PW["PRD Writer"]
    end

    subgraph DESIGN["設計部"]
        SA["Solution Architect"]
        FA["Frontend Architect"]
        AA["API Integration Architect"]
        AW["ADR Writer"]
    end

    subgraph IMPL["実装管理部"]
        TL["Tech Lead Agent"]
        TB["Task Breakdown Agent"]
        CP["Codex Prompt Writer"]
        RD["Refactor Director"]
    end

    subgraph QA["QA部"]
        TD["Test Designer"]
        TDD["TDD Enforcer"]
        BT["Bug Triage Agent"]
        BTO["Browser Test Operator"]
    end

    subgraph DESIGN2["デザイン部"]
        DC["Design Critic"]
        CC["Copy Critic"]
        AR["Accessibility Reviewer"]
    end

    subgraph RELEASE["リリース・改善部"]
        RM["Release Manager"]
        SC["Sakura API Coordinator"]
        IS2["Improvement Strategist"]
    end

    P1["Phase 1-2\n市場調査・選定"]
    P3["Phase 3\nPRD作成"]
    P4["Phase 4-5\n設計・タスク分解"]
    P6["Phase 6-7\n疎通確認"]
    P8["Phase 8\n委任書作成"]
    P9["Phase 9\n実装"]
    P10["Phase 10\nテスト"]
    P11["Phase 11\n公開"]
    P12["Phase 12\n改善"]

    RESEARCH --> P1
    EXEC -. "方向性承認" .-> P1
    PLAN --> P3
    ROI -. "ROI評価" .-> P3
    DESIGN --> P4
    SC --> P6
    IMPL --> P8
    IMPL -. "Codex CLI委任" .-> P9
    QA --> P10
    DESIGN2 -. "デザイン審査" .-> P10
    RELEASE --> P11
    RELEASE --> P12
    COO -. "工程制御" .-> P11
    CEO -. "リリース承認" .-> P11
```

---

## 6. AdSense 組み込み判定フロー

```mermaid
flowchart TD
    start(["Phase 11: 公開 開始"])
    check1{"本体 index.html に\nAdSense タグあり？"}
    check2{"ルート index.html に\nAdSense タグあり？"}
    check3{"AdSense による\nレイアウト崩れなし？"}
    check4{"テストページに\nAdSense 混入なし？"}
    ok(["✅ Release OK\nGitHub Pages 公開へ"])
    ng(["❌ Release NG\n修正して再確認"])

    start --> check1
    check1 -->|"あり"| check2
    check1 -->|"なし"| ng
    check2 -->|"あり"| check3
    check2 -->|"なし"| ng
    check3 -->|"問題なし"| check4
    check3 -->|"崩れあり"| ng
    check4 -->|"混入なし"| ok
    check4 -->|"混入あり"| ng
```

---

_以上。不明点は QandA.md に追記。_
