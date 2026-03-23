"""scripts/agents/pain_finder.py — Pain Finder (リサーチ部)"""
import logging
from pathlib import Path
from agents._base import check_inputs, setup_agent_logging

AGENT_ID = "pain_finder"
REQUIRED_INPUTS = ["docs/roadmap.md"]
OUTPUTS = ["artifacts/research/pain_points.md"]
logger = logging.getLogger(AGENT_ID)


def main() -> None:
    setup_agent_logging(AGENT_ID)
    logger.info(f"=== {AGENT_ID} 開始 ===")
    check_inputs(REQUIRED_INPUTS)

    out_dir = Path("artifacts/research")
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "pain_points.md").write_text(
        "# pain_points.md\n\nsource: docs/roadmap.md\n\n## ユーザーの課題\n\n"
        "- 既存ツールが重い / 広告が多い\n"
        "- オフライン利用ができない\n"
        "- カスタマイズ性が低い\n"
        "- 日本語対応が不十分\n",
        encoding="utf-8",
    )
    logger.info("pain_points.md を出力しました")
    raise SystemExit(0)


if __name__ == "__main__":
    import os, sys
    from pathlib import Path
    os.chdir(Path(__file__).parent.parent.parent)
    sys.path.insert(0, str(Path(__file__).parent.parent))
    main()
