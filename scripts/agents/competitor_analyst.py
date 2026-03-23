"""scripts/agents/competitor_analyst.py — Competitor Analyst (リサーチ部)"""
import logging
from pathlib import Path
from agents._base import check_inputs, setup_agent_logging

AGENT_ID = "competitor_analyst"
REQUIRED_INPUTS = ["docs/roadmap.md"]
OUTPUTS = ["artifacts/research/competitor_report.md"]
logger = logging.getLogger(AGENT_ID)


def main() -> None:
    setup_agent_logging(AGENT_ID)
    logger.info(f"=== {AGENT_ID} 開始 ===")
    check_inputs(REQUIRED_INPUTS)

    out_dir = Path("artifacts/research")
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "competitor_report.md").write_text(
        "# competitor_report.md\n\nsource: docs/roadmap.md\n\n## 競合分析\n\n"
        "- 家計簿: Zaim / Moneytree (有料・重い)\n"
        "- 単語帳: Anki (高機能だが学習コストが高い)\n"
        "- 習慣管理: Habitica (ゲーミフィケーション強め)\n"
        "- 差別化ポイント: 軽量・日本語・無料・静的ホスティング\n",
        encoding="utf-8",
    )
    logger.info("competitor_report.md を出力しました")
    raise SystemExit(0)


if __name__ == "__main__":
    import os, sys
    from pathlib import Path
    os.chdir(Path(__file__).parent.parent.parent)
    sys.path.insert(0, str(Path(__file__).parent.parent))
    main()
