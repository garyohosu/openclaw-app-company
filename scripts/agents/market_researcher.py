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

    roadmap = Path("docs/roadmap.md").read_text(encoding="utf-8")
    out_dir = Path("artifacts/research")
    out_dir.mkdir(parents=True, exist_ok=True)

    (out_dir / "research_report.md").write_text(
        f"# research_report.md\n\nsource: docs/roadmap.md\n\n## ロードマップ概要\n\n{roadmap}\n",
        encoding="utf-8",
    )
    (out_dir / "source_notes.md").write_text(
        "# source_notes.md\n\nsource: docs/roadmap.md\nnotes: ロードマップをそのまま一次資料として使用\n",
        encoding="utf-8",
    )
    logger.info("research_report.md, source_notes.md を出力しました")
    raise SystemExit(0)


if __name__ == "__main__":
    import os, sys
    os.chdir(Path(__file__).parent.parent.parent)
    sys.path.insert(0, str(Path(__file__).parent.parent))
    main()
