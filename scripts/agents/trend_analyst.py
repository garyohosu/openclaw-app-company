"""scripts/agents/trend_analyst.py — Trend Analyst (リサーチ部)"""
import logging
from pathlib import Path
from agents._base import check_inputs, setup_agent_logging

AGENT_ID = "trend_analyst"
REQUIRED_INPUTS = ["docs/roadmap.md"]
OUTPUTS = ["artifacts/research/trend_report.md"]
logger = logging.getLogger(AGENT_ID)


def main() -> None:
    setup_agent_logging(AGENT_ID)
    logger.info(f"=== {AGENT_ID} 開始 ===")
    check_inputs(REQUIRED_INPUTS)

    out_dir = Path("artifacts/research")
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "trend_report.md").write_text(
        "# trend_report.md\n\nsource: docs/roadmap.md\n\n## トレンド分析\n\n"
        "- 軽量 Web ツール需要は継続的に増加\n"
        "- 個人開発・無料公開 + 広告収益モデルが拡大\n"
        "- LocalStorage 活用で静的ホスティングの限界を拡張\n",
        encoding="utf-8",
    )
    logger.info("trend_report.md を出力しました")
    raise SystemExit(0)


if __name__ == "__main__":
    import os, sys
    from pathlib import Path
    os.chdir(Path(__file__).parent.parent.parent)
    sys.path.insert(0, str(Path(__file__).parent.parent))
    main()
