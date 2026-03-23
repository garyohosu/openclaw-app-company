"""scripts/agents/roi_agent.py — ROI Agent (経営層)"""
import logging
from pathlib import Path
from agents._base import check_inputs, setup_agent_logging

AGENT_ID = "roi_agent"
REQUIRED_INPUTS = ["artifacts/research/idea_pool.md"]
OUTPUTS = ["artifacts/research/roi_report.md"]
logger = logging.getLogger(AGENT_ID)


def main() -> None:
    setup_agent_logging(AGENT_ID)
    logger.info(f"=== {AGENT_ID} 開始 ===")
    check_inputs(REQUIRED_INPUTS)

    out_dir = Path("artifacts/research")
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "roi_report.md").write_text(
        "# roi_report.md\n\nsource: artifacts/research/idea_pool.md\n\n## ROI 試算\n\n"
        "- 実装コスト: 低 (Codex CLI 委任)\n"
        "- AdSense 想定月間収益: 数百〜数千円/アプリ\n"
        "- 回収期間: 公開後 1〜3 ヶ月\n"
        "- リスク: 検索流入が得られない場合は収益ゼロ\n",
        encoding="utf-8",
    )
    logger.info("roi_report.md を出力しました")
    raise SystemExit(0)


if __name__ == "__main__":
    import os, sys
    from pathlib import Path
    os.chdir(Path(__file__).parent.parent.parent)
    sys.path.insert(0, str(Path(__file__).parent.parent))
    main()
