"""scripts/agents/solution_architect.py — Solution Architect (設計部)"""
import logging
from pathlib import Path
from agents._base import check_inputs, get_selected_app, setup_agent_logging

AGENT_ID = "solution_architect"
REQUIRED_INPUTS = ["artifacts/product/prd.md"]
OUTPUTS = ["artifacts/design/architecture.md"]
logger = logging.getLogger(AGENT_ID)


def main() -> None:
    setup_agent_logging(AGENT_ID)
    logger.info(f"=== {AGENT_ID} 開始 ===")
    check_inputs(REQUIRED_INPUTS)

    app = get_selected_app()
    out_dir = Path("artifacts/design")
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "architecture.md").write_text(
        f"# architecture.md — {app}\n\n"
        "## アーキテクチャ概要\n\n"
        "- デプロイ先: GitHub Pages (静的ホスティング)\n"
        "- フロントエンド: HTML5 + Vanilla JS\n"
        "- データ永続化: LocalStorage\n"
        "- バックエンド: なし (静的のみ)\n\n"
        "## ディレクトリ構成\n\n"
        "```\n"
        f"apps/{app}/\n"
        "  index.html\n"
        "  style.css\n"
        "  app.js\n"
        "```\n\n"
        "## 設計方針\n\n"
        "- 外部ライブラリ依存を最小化\n"
        "- AdSense 広告枠を index.html に配置\n"
        "- LocalStorage のキーは app 名でプレフィックス付与\n",
        encoding="utf-8",
    )
    logger.info(f"architecture.md を出力しました (app={app})")
    raise SystemExit(0)


if __name__ == "__main__":
    import os, sys
    from pathlib import Path
    os.chdir(Path(__file__).parent.parent.parent)
    sys.path.insert(0, str(Path(__file__).parent.parent))
    main()
