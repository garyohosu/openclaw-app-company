"""scripts/agents/value_proposition_agent.py — Value Proposition Agent (企画部)"""
import logging
from pathlib import Path
from agents._base import check_inputs, get_selected_app, setup_agent_logging

AGENT_ID = "value_proposition_agent"
REQUIRED_INPUTS = ["artifacts/research/scored_ideas.md"]
OUTPUTS = ["artifacts/product/value_proposition.md"]
logger = logging.getLogger(AGENT_ID)


def main() -> None:
    setup_agent_logging(AGENT_ID)
    logger.info(f"=== {AGENT_ID} 開始 ===")
    check_inputs(REQUIRED_INPUTS)

    app = get_selected_app()

    out_dir = Path("artifacts/product")
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "value_proposition.md").write_text(
        f"# value_proposition.md — {app}\n\n"
        "## 提供価値\n\n"
        f"- **軽量**: {app} は広告・登録不要で即利用可能\n"
        "- **オフライン対応**: LocalStorage により通信なしで動作\n"
        "- **日本語 UI**: 日本語ユーザーに最適化\n"
        "- **無料**: GitHub Pages 静的ホスティングで維持費ゼロ\n\n"
        "## ターゲットユーザー\n\n"
        "- 手軽に使えるツールを探している個人ユーザー\n"
        "- スマートフォンでも快適に使いたいユーザー\n",
        encoding="utf-8",
    )
    logger.info("value_proposition.md を出力しました")
    raise SystemExit(0)


if __name__ == "__main__":
    import os, sys
    from pathlib import Path
    os.chdir(Path(__file__).parent.parent.parent)
    sys.path.insert(0, str(Path(__file__).parent.parent))
    main()
