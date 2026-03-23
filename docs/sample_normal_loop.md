# 実行例: 通常改善ループ (Release OK → improvement normal)

2026-03-23 に実施した Provisional → Release OK → 通常改善ループへの移行記録。

---

## 前提状態

| 項目 | 値 |
|---|---|
| `release_readiness` | `provisional` (QA stub のまま) |
| `followup_action` | `start-qa-remediation` |

---

## Step 1: QA 成果物を正式版に更新

```bash
# browser_test_report.md を手動確認後に更新
# (OK / PASS を含む内容に書き換える)
vi artifacts/qa/browser_test_report.md

# design_review.md を手動レビュー後に更新
vi artifacts/qa/design_review.md
```

---

## Step 2: release フェーズ再実行

```bash
python scripts/main.py --phase release
```

### ログ出力

```
[INFO] === github_pages_release_manager 開始 ===
[INFO] Release OK — QA 両方合格
[INFO] ✓ github_pages_release_manager 完了
```

### 成果物: `artifacts/sprints/deploy_report.md`

```markdown
release_result: Release OK
release_readiness: ready
browser_test_report: OK
design_review: OK
publish_blocked_reason: -
```

### 状態更新

```json
{
  "current_phase": "release",
  "next_action": "start-improvement",
  "quality_gate": { "release_gate_passed": true }
}
```

---

## Step 3: improvement フェーズ実行 (通常モード)

```bash
python scripts/main.py --phase improvement
```

### ログ出力

```
[INFO] === improvement_strategist 開始 ===
[INFO] release_readiness=ready → 通常改善ループへ
[INFO] sprint_next.md, usage_insights.md, user_feedback.md を出力しました (mode=ready)
```

### 成果物: `artifacts/sprints/sprint_next.md`

```markdown
# sprint_next.md

source: deploy_report.md
improvement_mode: normal
summary: improvement plan with loopback options

## 同一アプリ改善ループ
next_phase: PHASE_5
action: task_breakdown

## 新規アプリ探索ループ
next_phase: PHASE_1
action: research

next_action: start-task-breakdown
```

### 最終状態

```json
{
  "current_phase": "improvement",
  "next_action": "pipeline-complete",
  "followup_action": "start-task-breakdown",
  "quality_gate": { "release_gate_passed": true }
}
```

---

## 次の判断ポイント

`followup_action: start-task-breakdown` が示す通り、次の選択肢は2つ:

1. **同一アプリ改善**: `--phase design` から再実行し task_breakdown → prompt → release ループ
2. **新規アプリ探索**: `--phase research` から再実行し次の app idea を選定

どちらを選ぶかは `sprint_next.md` の改善案を見て人間が判断する。
