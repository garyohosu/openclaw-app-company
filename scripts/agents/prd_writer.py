"""scripts/agents/prd_writer.py — PRD Writer (企画部)"""
import logging
from pathlib import Path
from agents._base import check_inputs, get_selected_app, setup_agent_logging

AGENT_ID = "prd_writer"
REQUIRED_INPUTS = ["artifacts/research/scored_ideas.md"]
OUTPUTS = ["artifacts/product/prd.md"]
logger = logging.getLogger(AGENT_ID)


def main() -> None:
    setup_agent_logging(AGENT_ID)
    logger.info(f"=== {AGENT_ID} 開始 ===")
    check_inputs(REQUIRED_INPUTS)

    app = get_selected_app()
    out_dir = Path("artifacts/product")
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "prd.md").write_text(
        f"# prd.md — {app}\n\n"
        "## 概要\n\n"
        f"{app} は軽量・無料の Web ツールです。\n"
        "GitHub Pages で静的ホスティングし、LocalStorage でデータを永続化します。\n\n"
        "## 機能要件\n\n"
        "- データの追加・編集・削除\n"
        "- LocalStorage による永続化\n"
        "- レスポンシブ UI (スマートフォン対応)\n\n"
        "## 非機能要件\n\n"
        "- 外部サーバー不要 (静的ホスティング)\n"
        "- 日本語 UI\n"
        "- AdSense 広告枠を含む\n",
        encoding="utf-8",
    )
    logger.info(f"prd.md を出力しました (app={app})")
    raise SystemExit(0)


if __name__ == "__main__":
    import os, sys
    from pathlib import Path
    os.chdir(Path(__file__).parent.parent.parent)
    sys.path.insert(0, str(Path(__file__).parent.parent))
    main()
