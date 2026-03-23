"""scripts/agents/product_planner.py — Product Planner (企画部)"""
import logging
from pathlib import Path
from agents._base import check_inputs, get_selected_app, setup_agent_logging

AGENT_ID = "product_planner"
REQUIRED_INPUTS = ["artifacts/research/scored_ideas.md"]
OUTPUTS = ["artifacts/product/product_plan.md"]
logger = logging.getLogger(AGENT_ID)


def main() -> None:
    setup_agent_logging(AGENT_ID)
    logger.info(f"=== {AGENT_ID} 開始 ===")
    check_inputs(REQUIRED_INPUTS)

    app = get_selected_app()
    out_dir = Path("artifacts/product")
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "product_plan.md").write_text(
        f"# product_plan.md\n\nselected_app: {app}\n\n"
        "## 開発計画\n\n"
        "- Sprint 1: 基本機能実装 (HTML/JS + LocalStorage)\n"
        "- Sprint 2: UI 改善 + レスポンシブ対応\n"
        "- Sprint 3: GitHub Pages 公開 + AdSense 設置\n",
        encoding="utf-8",
    )
    logger.info(f"product_plan.md を出力しました (app={app})")
    raise SystemExit(0)


if __name__ == "__main__":
    import os, sys
    from pathlib import Path
    os.chdir(Path(__file__).parent.parent.parent)
    sys.path.insert(0, str(Path(__file__).parent.parent))
    main()
