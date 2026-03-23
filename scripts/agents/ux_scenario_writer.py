"""scripts/agents/ux_scenario_writer.py — UX Scenario Writer (企画部)"""
import logging
from pathlib import Path
from agents._base import check_inputs, get_selected_app, setup_agent_logging

AGENT_ID = "ux_scenario_writer"
REQUIRED_INPUTS = ["artifacts/product/prd.md"]
OUTPUTS = ["artifacts/product/ux_scenarios.md"]
logger = logging.getLogger(AGENT_ID)


def main() -> None:
    setup_agent_logging(AGENT_ID)
    logger.info(f"=== {AGENT_ID} 開始 ===")
    check_inputs(REQUIRED_INPUTS)

    app = get_selected_app()

    out_dir = Path("artifacts/product")
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "ux_scenarios.md").write_text(
        f"# ux_scenarios.md — {app}\n\n"
        "## シナリオ 1: 初回利用\n"
        "- ユーザーがサイトを開く\n"
        "- 使い方説明を読む\n"
        "- 最初のデータを入力する\n\n"
        "## シナリオ 2: 日常利用\n"
        "- ブックマークからアクセス\n"
        "- データを追加・確認する\n"
        "- 必要なら編集・削除する\n\n"
        "## シナリオ 3: データ確認\n"
        "- 蓄積データをまとめて閲覧\n"
        "- 統計・サマリーを確認する\n",
        encoding="utf-8",
    )
    logger.info("ux_scenarios.md を出力しました")
    raise SystemExit(0)


if __name__ == "__main__":
    import os, sys
    from pathlib import Path
    os.chdir(Path(__file__).parent.parent.parent)
    sys.path.insert(0, str(Path(__file__).parent.parent))
    main()
