# サンプル出力: Release OK

QA 成果物が両方とも正式版 (OK/PASS を含む) のときの出力例。

---

## 入力: `artifacts/qa/browser_test_report.md`

```markdown
# browser_test_report.md

result: OK
confirmed_at: 2026-03-23
confirmed_by: (手動確認)
environment: Chrome / WSL2 ローカル

## 確認項目
| 画面 / 機能         | 結果 | 備考             |
|---|---|---|
| トップページ表示    | PASS | 正常表示         |
| レスポンシブ (375px)| PASS | 崩れなし         |
| LocalStorage 読み書き | PASS | データ永続化確認 |

release_gate: OK
```

## 入力: `artifacts/qa/design_review.md`

```markdown
# design_review.md

result: OK
confirmed_at: 2026-03-23
confirmed_by: (手動確認)

## レビュー観点と結果
| 観点               | 結果 | 備考         |
|---|---|---|
| レイアウト崩れ     | PASS | 主要 BP 確認 |
| カラーパレット統一 | PASS |              |

design_gate: OK
```

---

## 出力: `artifacts/sprints/deploy_report.md`

```markdown
# deploy_report.md

release_result: Release OK
release_readiness: ready
browser_test_report: OK
design_review: OK
publish_blocked_reason: -
public_url: N/A
index_updated: false
notes: minimal release report
```

## 状態: `state/company_state.json` (release フェーズ完了後)

```json
{
  "current_phase": "release",
  "next_action": "start-improvement",
  "followup_action": "",
  "quality_gate": {
    "release_gate_passed": true
  }
}
```

---

## ログ出力

```
[INFO] === github_pages_release_manager 開始 ===
[INFO] Release OK — QA 両方合格
[INFO] ✓ github_pages_release_manager 完了
```
