"""scripts/agents/codex_prompt_writer.py — Codex Prompt Writer (実装管理部 Phase 8)"""
import logging
from agents._base import check_inputs, setup_agent_logging

AGENT_ID = "codex_prompt_writer"
REQUIRED_INPUTS = ["artifacts/design/tasks.md"]
OUTPUTS = ["artifacts/prompts/task-001.md"]
logger = logging.getLogger(AGENT_ID)


def main() -> None:
    setup_agent_logging(AGENT_ID)
    logger.info(f"=== {AGENT_ID} 開始 ===")
    check_inputs(REQUIRED_INPUTS)
    raise SystemExit(1)  # TODO: 未実装


if __name__ == "__main__":
    import os, sys
    from pathlib import Path
    os.chdir(Path(__file__).parent.parent.parent)
    sys.path.insert(0, str(Path(__file__).parent.parent))
    main()
