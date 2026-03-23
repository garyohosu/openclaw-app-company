"""scripts/agents/idea_scorer.py — Idea Scorer (リサーチ部 Phase 2)"""
import logging
from agents._base import check_inputs, setup_agent_logging

AGENT_ID = "idea_scorer"
REQUIRED_INPUTS = [
    "artifacts/research/research_report.md",
    "artifacts/research/idea_pool.md",
]
OUTPUTS = ["artifacts/research/scored_ideas.md"]
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
