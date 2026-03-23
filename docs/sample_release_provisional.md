# サンプル出力: Release Provisional

QA 成果物が stub/placeholder のまま未更新のときの出力例。
パイプラインは exit(0) で継続するが、公開はブロックされる。

---

## 入力: `artifacts/qa/browser_test_report.md`

```markdown
# browser_test_report.md (stub)

summary: placeholder browser test report
```

## 入力: `artifacts/qa/design_review.md`

```markdown
# design_review.md (stub)

summary: placeholder design review
```

---

## 出力: `artifacts/sprints/deploy_report.md`

```markdown
# deploy_report.md

release_result: Release Provisional
release_readiness: provisional
browser_test_report: stub
design_review: stub
publish_blocked_reason: QA stub 未完成: browser_test_report, design_review
public_url: N/A
index_updated: false
notes: minimal release report
```

## 出力: `artifacts/sprints/sprint_next.md`

```markdown
# sprint_next.md

source: deploy_report.md
improvement_mode: qa_remediation
blocked_by: QA stub 未完成: browser_test_report, design_review

## 必要な QA 作業
required_actions:
- browser_test_report.md を実際のテスト結果で更新する (OK または PASS を含む形式)
- design_review.md を実際のレビュー結果で更新する (OK または PASS を含む形式)

## 次ステップ
next_action: start-qa-remediation
```

## 状態: `state/company_state.json` (improvement フェーズ完了後)

```json
{
  "current_phase": "improvement",
  "next_action": "pipeline-complete",
  "followup_action": "start-qa-remediation",
  "quality_gate": {
    "release_gate_passed": false
  }
}
```

---

## ログ出力

```
[INFO]    === github_pages_release_manager 開始 ===
[WARNING] publish blocked — QA stub 未完成: browser_test_report, design_review
[INFO]    ✓ github_pages_release_manager 完了

[INFO]    === improvement_strategist 開始 ===
[WARNING] release_readiness=provisional → QA remediation モード (blocked_by: QA stub 未完成: ...)
[INFO]    sprint_next.md, usage_insights.md, user_feedback.md を出力しました (mode=provisional)
```

---

## Provisional → Release OK への移行手順

1. `artifacts/qa/browser_test_report.md` を実際の確認結果で更新 (`OK` または `PASS` を含める)
2. `artifacts/qa/design_review.md` を実際のレビュー結果で更新 (`OK` または `PASS` を含める)
3. `python scripts/main.py --phase release` を再実行
4. `deploy_report.md` が `Release OK / release_readiness: ready` になることを確認
5. `python scripts/main.py --phase improvement` を再実行
6. `sprint_next.md` が `improvement_mode: normal` になることを確認
