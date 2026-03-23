"""scripts/agents/task_breakdown_agent.py — Task Breakdown Agent (実装管理部)"""
import logging
from pathlib import Path
from agents._base import check_inputs, get_selected_app, setup_agent_logging

AGENT_ID = "task_breakdown_agent"
REQUIRED_INPUTS = ["artifacts/design/architecture.md"]
OUTPUTS = ["artifacts/design/tasks.md"]
logger = logging.getLogger(AGENT_ID)

# codex_prompt_writer が期待するフォーマット:
#   ## task-NNN: タイトル
#   runtime_mode: static|toolbox|db
_TASKS = [
    ("task-001", "HTML/JS 基本構造の実装", "static"),
    ("task-002", "LocalStorage データ管理の実装", "static"),
    ("task-003", "レスポンシブ UI の実装", "static"),
    ("task-004", "AdSense 広告枠の配置", "static"),
    ("task-005", "GitHub Pages デプロイ設定", "static"),
]


def main() -> None:
    setup_agent_logging(AGENT_ID)
    logger.info(f"=== {AGENT_ID} 開始 ===")
    check_inputs(REQUIRED_INPUTS)

    app = get_selected_app()
    lines = [f"# tasks.md — {app}\n\nsource: architecture.md\n"]
    for task_id, title, runtime_mode in _TASKS:
        lines.append(f"\n## {task_id}: {title}\nruntime_mode: {runtime_mode}\n")

    out_dir = Path("artifacts/design")
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "tasks.md").write_text("".join(lines), encoding="utf-8")
    logger.info(f"tasks.md を出力しました ({len(_TASKS)} tasks, app={app})")
    raise SystemExit(0)


if __name__ == "__main__":
    import os, sys
    from pathlib import Path
    os.chdir(Path(__file__).parent.parent.parent)
    sys.path.insert(0, str(Path(__file__).parent.parent))
    main()
