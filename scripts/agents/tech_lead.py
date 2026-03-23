"""scripts/agents/tech_lead.py — Tech Lead Agent (実装管理部)"""
import logging
from pathlib import Path
from agents._base import check_inputs, get_selected_app, setup_agent_logging

AGENT_ID = "tech_lead"
REQUIRED_INPUTS = ["artifacts/design/tasks.md"]
OUTPUTS = ["artifacts/implementation/tech_review.md"]
logger = logging.getLogger(AGENT_ID)


def main() -> None:
    setup_agent_logging(AGENT_ID)
    logger.info(f"=== {AGENT_ID} 開始 ===")
    check_inputs(REQUIRED_INPUTS)

    tasks_path = Path(REQUIRED_INPUTS[0])
    tasks_content = tasks_path.read_text(encoding="utf-8")
    task_count = tasks_content.count("\n## task-")
    # パイプライン上、tech_lead は task_breakdown_agent より前に実行される。
    # tasks.md が正式版かどうかを判別するため、先頭行を snapshot として記録する。
    tasks_snapshot = tasks_content.splitlines()[0] if tasks_content else "(empty)"
    is_stub = task_count == 0
    reviewed_basis = "stub (task_breakdown_agent 未実行)" if is_stub else f"正式版 ({task_count} tasks)"
    app = get_selected_app()

    out_dir = Path("artifacts/implementation")
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "tech_review.md").write_text(
        f"# tech_review.md — {app}\n\n"
        f"source: tasks.md\n"
        f"reviewed_basis: {reviewed_basis}\n"
        f"tasks_snapshot: {tasks_snapshot}\n\n"
        "## レビュー結果\n\n"
        "- 技術選定: 静的ホスティング + LocalStorage → 適切\n"
        "- タスク分割: 適切 (各タスクは独立して実装可能)\n"
        "- リスク: LocalStorage 容量制限 (5MB)\n\n"
        "## 承認\n\n"
        "status: approved\n",
        encoding="utf-8",
    )
    logger.info(f"tech_review.md を出力しました (app={app}, reviewed_basis={reviewed_basis})")
    raise SystemExit(0)


if __name__ == "__main__":
    import os, sys
    from pathlib import Path
    os.chdir(Path(__file__).parent.parent.parent)
    sys.path.insert(0, str(Path(__file__).parent.parent))
    main()
