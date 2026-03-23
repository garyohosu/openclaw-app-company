"""scripts/agents/ceo.py — CEO Agent (経営層)"""
import logging
from pathlib import Path
from agents._base import check_inputs, setup_agent_logging

AGENT_ID = "ceo"
REQUIRED_INPUTS = ["artifacts/research/scored_ideas.md", "artifacts/product/prd.md"]
OUTPUTS = ["artifacts/executive/decision.md"]
logger = logging.getLogger(AGENT_ID)


def main() -> None:
    setup_agent_logging(AGENT_ID)
    logger.info(f"=== {AGENT_ID} 開始 ===")
    check_inputs(REQUIRED_INPUTS)

    scored = Path("artifacts/research/scored_ideas.md").read_text(encoding="utf-8")
    # 最高スコアのアイデアを選出（score: N が最大のもの）
    best = ""
    best_score = -1
    for line in scored.splitlines():
        if line.startswith("## "):
            current = line[3:].strip()
        if line.startswith("score:"):
            try:
                s = int(line.split(":")[1].strip())
                if s > best_score:
                    best_score = s
                    best = current
            except ValueError:
                pass

    out_dir = Path("artifacts/executive")
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "decision.md").write_text(
        f"# decision.md\n\nsource: scored_ideas.md\n"
        f"decision: approved\nselected_app: {best}\nreason: 最高スコア ({best_score}点)\n",
        encoding="utf-8",
    )
    logger.info(f"decision.md を出力しました (selected: {best})")
    raise SystemExit(0)


if __name__ == "__main__":
    import os, sys
    from pathlib import Path
    os.chdir(Path(__file__).parent.parent.parent)
    sys.path.insert(0, str(Path(__file__).parent.parent))
    main()
