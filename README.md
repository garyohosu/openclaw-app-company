# OpenClaw App Company

GitHub Pages 上で動く軽量 Web アプリを自律的に量産する仮想開発会社パイプライン。
市場調査からリリース・改善まで、エージェントが各フェーズを順番に担当する。

---

## クイックスタート

```bash
# 依存関係インストール
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt

# テスト実行
python -m pytest -q

# パイプライン全体を実行
python scripts/main.py

# 特定フェーズのみ実行
python scripts/main.py --phase release

# 入力・出力を確認するだけ (ファイル書き込みなし)
python scripts/main.py --dry-run
```

---

## フェーズ一覧

| フェーズ | 主なエージェント | 主な成果物 |
|---|---|---|
| `research` | market_researcher, trend_analyst, pain_finder, competitor_analyst, roi_agent, idea_scorer, ceo, coo | `artifacts/research/`, `artifacts/executive/decision.md` |
| `product` | product_planner, ux_scenario_writer, value_proposition_agent, prd_writer | `artifacts/product/` |
| `design` | solution_architect, frontend_architect, api_integration_architect, adr_writer, tech_lead, task_breakdown_agent | `artifacts/design/`, `artifacts/implementation/tasks.md` |
| `prompt` | codex_prompt_writer | `artifacts/prompts/` |
| `release` | github_pages_release_manager | `artifacts/sprints/deploy_report.md` |
| `improvement` | improvement_strategist | `artifacts/sprints/sprint_next.md` |

`api_connectivity` フェーズは `runtime_mode: toolbox` または `db` のときのみ実行される。

---

## 状態遷移図

```
[research] → [product] → [design] → [prompt]
                                           |
                                      [release]
                                      /        \
                              Release OK     Release Provisional
                                  |                  |
                          [improvement]        [improvement]
                          mode: normal         mode: qa_remediation
                              |                      |
                    next_phase: PHASE_5       next_action: start-qa-remediation
                    (task_breakdown)               (人手で QA 修正)
                    next_phase: PHASE_1                |
                    (research)              QA 成果物を正式版に更新
                              \                       |
                               +---------+------------+
                                         |
                                    [release 再実行]
```

### Release Provisional が発生する条件

`artifacts/qa/browser_test_report.md` または `artifacts/qa/design_review.md` が
stub/placeholder のまま未更新の場合。これらを実際の確認結果で更新してから
`--phase release` を再実行することで Release OK に移行できる。

---

## 状態ファイル (`state/company_state.json`)

```json
{
  "current_phase": "improvement",
  "next_action": "pipeline-complete",
  "followup_action": "start-task-breakdown"
}
```

| フィールド | 意味 |
|---|---|
| `current_phase` | 最後に完了したフェーズ |
| `next_action` | 今回のパイプライン実行結果 (例: `pipeline-complete`, `fix-release-missing-inputs`) |
| `followup_action` | 次ランまたは人手で行うべき実務アクション (例: `start-task-breakdown`, `start-qa-remediation`) |

`next_action` と `followup_action` は意図的に役割を分けている。
`next_action` は「このパイプライン run が何で終わったか」、
`followup_action` は「次に人または次 run が何をすべきか」を示す。

---

## QA 成果物の更新方法

### `artifacts/qa/browser_test_report.md`

最低記載項目:

```markdown
result: OK
confirmed_at: YYYY-MM-DD
confirmed_by: (確認者)
environment: (ブラウザ、OS)

## 確認項目
| 機能 | 結果 | 備考 |
|---|---|---|
| トップページ表示 | PASS | |
...

release_gate: OK
```

`OK` または `PASS` が含まれていれば `release_readiness: ready` に移行する。
`FAIL` または `NG` が含まれると即 exit(1)。
それ以外 (stub/placeholder のみ) は Release Provisional になる。

### `artifacts/qa/design_review.md`

最低記載項目:

```markdown
result: OK
confirmed_at: YYYY-MM-DD
confirmed_by: (レビュアー)

## レビュー観点と結果
| 観点 | 結果 | 備考 |
|---|---|---|
| レイアウト崩れ | PASS | |
...

design_gate: OK
```

---

## サンプル出力

詳細は `docs/` を参照:

- [Release OK サンプル](docs/sample_release_ok.md)
- [Release Provisional サンプル](docs/sample_release_provisional.md)
- [通常改善ループ 実行例](docs/sample_normal_loop.md)

---

## ディレクトリ構成

```
scripts/
  main.py               # オーケストレータ
  agents/               # 各フェーズのエージェント実装
  state/                # CompanyState 定義・読み書き
artifacts/
  research/             # 市場調査成果物
  executive/            # CEO 意思決定 (decision.md)
  product/              # 企画・PRD
  design/               # アーキテクチャ・設計
  implementation/       # tasks.md (タスク一覧)
  prompts/              # Codex へのプロンプト
  qa/                   # QA 確認結果 (要手動更新)
  sprints/              # deploy_report.md, sprint_next.md
state/
  company_state.json    # パイプライン状態
docs/                   # 設計ドキュメント・サンプル出力
tests/                  # pytest テストスイート
```
