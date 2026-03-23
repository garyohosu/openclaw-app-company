"""scripts/agents/improvement_strategist.py — Improvement Strategist (リリース部 Phase 12)"""
from __future__ import annotations

import logging
from pathlib import Path

from agents._base import check_inputs, setup_agent_logging

AGENT_ID = "improvement_strategist"
REQUIRED_INPUTS = ["artifacts/sprints/deploy_report.md"]
OUTPUTS = [
    "artifacts/sprints/sprint_next.md",
    "artifacts/sprints/user_feedback.md",
    "artifacts/sprints/usage_insights.md",
]
logger = logging.getLogger(AGENT_ID)

SPRINT_NEXT_READY_TEMPLATE = """\
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
"""

SPRINT_NEXT_PROVISIONAL_TEMPLATE = """\
# sprint_next.md

source: deploy_report.md
improvement_mode: qa_remediation
blocked_by: {blocked_by}

## 必要な QA 作業
required_actions:
- browser_test_report.md を実際のテスト結果で更新する (OK または PASS を含む形式)
- design_review.md を実際のレビュー結果で更新する (OK または PASS を含む形式)

## 次ステップ
next_action: start-qa-remediation
"""

USAGE_INSIGHTS_TEMPLATE = """\
# usage_insights.md

summary: placeholder (no data yet)
"""

USER_FEEDBACK_TEMPLATE = """\
# user_feedback.md

summary: placeholder (no feedback yet)
"""


def _parse_field(content: str, field: str) -> str:
    """deploy_report.md から `field: value` 形式の値を返す。なければ空文字。"""
    for line in content.splitlines():
        if line.startswith(f"{field}:"):
            return line.split(":", 1)[1].strip()
    return ""


def _get_readiness(content: str) -> str:
    """release_readiness を返す。フィールドなし (旧フォーマット) は Release OK で判定。"""
    readiness = _parse_field(content, "release_readiness")
    if readiness:
        return readiness
    # 旧フォーマット互換
    return "ready" if "Release OK" in content else "ng"


def main() -> None:
    setup_agent_logging(AGENT_ID)
    logger.info(f"=== {AGENT_ID} 開始 ===")
    check_inputs(REQUIRED_INPUTS)

    content = Path(REQUIRED_INPUTS[0]).read_text(encoding="utf-8")
    readiness = _get_readiness(content)

    out_dir = Path("artifacts") / "sprints"
    out_dir.mkdir(parents=True, exist_ok=True)

    if readiness == "ready":
        logger.info("release_readiness=ready → 通常改善ループへ")
        sprint_next = SPRINT_NEXT_READY_TEMPLATE

    elif readiness == "provisional":
        blocked_by = _parse_field(content, "publish_blocked_reason") or "未特定"
        logger.warning(f"release_readiness=provisional → QA remediation モード (blocked_by: {blocked_by})")
        sprint_next = SPRINT_NEXT_PROVISIONAL_TEMPLATE.format(blocked_by=blocked_by)

    else:
        logger.error(f"deploy_report.md の release_readiness が NG または不正: {readiness!r}")
        raise SystemExit(1)

    (out_dir / "sprint_next.md").write_text(sprint_next, encoding="utf-8")
    (out_dir / "usage_insights.md").write_text(USAGE_INSIGHTS_TEMPLATE, encoding="utf-8")
    (out_dir / "user_feedback.md").write_text(USER_FEEDBACK_TEMPLATE, encoding="utf-8")
    logger.info(f"sprint_next.md, usage_insights.md, user_feedback.md を出力しました (mode={readiness})")
    raise SystemExit(0)


if __name__ == "__main__":
    import os, sys
    from pathlib import Path
    os.chdir(Path(__file__).parent.parent.parent)
    sys.path.insert(0, str(Path(__file__).parent.parent))
    main()
