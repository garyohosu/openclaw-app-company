"""scripts/agents/market_researcher.py — Market Researcher (リサーチ部 Phase 1)"""
import logging
from pathlib import Path
from agents._base import check_inputs, setup_agent_logging

AGENT_ID = "market_researcher"
REQUIRED_INPUTS = ["docs/roadmap.md"]
OUTPUTS = [
    "artifacts/research/research_report.md",
    "artifacts/research/source_notes.md",
]
logger = logging.getLogger(AGENT_ID)


def main() -> None:
    setup_agent_logging(AGENT_ID)
    logger.info(f"=== {AGENT_ID} 開始 ===")
    check_inputs(REQUIRED_INPUTS)
    raise SystemExit(1)  # TODO: 未実装


if __name__ == "__main__":
    import os, sys
    os.chdir(Path(__file__).parent.parent.parent)
    sys.path.insert(0, str(Path(__file__).parent.parent))
    main()
