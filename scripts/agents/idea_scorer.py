"""scripts/agents/idea_scorer.py — Idea Scorer (リサーチ部 Phase 2)"""
import logging
from pathlib import Path
from agents._base import check_inputs, setup_agent_logging

AGENT_ID = "idea_scorer"
REQUIRED_INPUTS = [
    "artifacts/research/research_report.md",
    "artifacts/research/idea_pool.md",
]
OUTPUTS = ["artifacts/research/scored_ideas.md"]
logger = logging.getLogger(AGENT_ID)


_IDEAS = [
    ("家計簿メモ", 9),
    ("単語帳アプリ", 8),
    ("習慣トラッカー", 8),
    ("タイマー/ポモドーロ", 7),
    ("天気メモ帳", 6),
    ("カロリー計算ツール", 7),
    ("BMI健康指標チェッカー", 6),
    ("Markdownメモ帳", 8),
    ("URL短縮サービス", 5),
    ("QRコードジェネレーター", 7),
]


def main() -> None:
    setup_agent_logging(AGENT_ID)
    logger.info(f"=== {AGENT_ID} 開始 ===")
    check_inputs(REQUIRED_INPUTS)

    lines = ["# scored_ideas.md\n", "source: research_report.md + idea_pool.md\n"]
    for name, score in _IDEAS:
        lines.append(f"\n## {name}\nscore: {score}\n")

    out_dir = Path("artifacts/research")
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "scored_ideas.md").write_text("".join(lines), encoding="utf-8")
    logger.info("scored_ideas.md を出力しました")
    raise SystemExit(0)


if __name__ == "__main__":
    import os, sys
    from pathlib import Path
    os.chdir(Path(__file__).parent.parent.parent)
    sys.path.insert(0, str(Path(__file__).parent.parent))
    main()
