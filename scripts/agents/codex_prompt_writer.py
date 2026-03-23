"""scripts/agents/codex_prompt_writer.py — Codex Prompt Writer (実装管理部 Phase 8)"""
from __future__ import annotations

import logging
import re
from pathlib import Path

from agents._base import check_inputs, setup_agent_logging

AGENT_ID = "codex_prompt_writer"
REQUIRED_INPUTS = ["artifacts/design/tasks.md"]
OUTPUTS = ["artifacts/prompts/task-001.md"]
logger = logging.getLogger(AGENT_ID)

TEMPLATE = """\
# {task_id}: {title}
Status: Draft for Codex CLI

## 1. 目的
（目的を記載）

## 2. スコープ
（対象範囲を記載）

## 3. 背景
（背景を記載）

## 4. 入出力
runtime_mode: {runtime_mode}
inputs:
  - （入力）
outputs:
  - （出力）

## 5. 制約
（制約を記載）

## 6. 手順
（手順を記載）

## 7. テスト
（テスト観点を記載）

## 8. 完了条件
（完了条件を記載）
"""


def _parse_tasks(content: str) -> list[dict]:
    pattern = re.compile(r"^##\s*(task-\d+):\s*(.+)$", re.MULTILINE)
    matches = list(pattern.finditer(content))
    tasks: list[dict] = []
    for i, match in enumerate(matches):
        block_start = match.end()
        block_end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
        block = content[block_start:block_end]
        rt_match = re.search(r"^\s*runtime_mode:\s*(\S+)\s*$", block, re.MULTILINE)
        runtime_mode = rt_match.group(1).strip() if rt_match else None
        tasks.append(
            {
                "task_id": match.group(1).strip(),
                "title": match.group(2).strip(),
                "runtime_mode": runtime_mode,
            }
        )
    return tasks


def main() -> None:
    setup_agent_logging(AGENT_ID)
    logger.info(f"=== {AGENT_ID} 開始 ===")
    check_inputs(REQUIRED_INPUTS)
    tasks_path = Path(REQUIRED_INPUTS[0])
    content = tasks_path.read_text(encoding="utf-8")
    tasks = _parse_tasks(content)
    if not tasks:
        logger.error("No tasks found in tasks.md")
        raise SystemExit(1)

    for t in tasks:
        if not t["runtime_mode"]:
            logger.error(f"runtime_mode missing for {t['task_id']}")
            raise SystemExit(1)

    out_dir = Path("artifacts") / "prompts"
    out_dir.mkdir(parents=True, exist_ok=True)
    for t in tasks:
        out_path = out_dir / f"{t['task_id']}.md"
        out_path.write_text(
            TEMPLATE.format(
                task_id=t["task_id"],
                title=t["title"],
                runtime_mode=t["runtime_mode"],
            ),
            encoding="utf-8",
        )
    raise SystemExit(0)


if __name__ == "__main__":
    import os, sys
    from pathlib import Path
    os.chdir(Path(__file__).parent.parent.parent)
    sys.path.insert(0, str(Path(__file__).parent.parent))
    main()
