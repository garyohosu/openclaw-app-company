"""scripts/agents/frontend_architect.py — Frontend Architect (設計部)"""
import logging
from pathlib import Path
from agents._base import check_inputs, get_selected_app, setup_agent_logging

AGENT_ID = "frontend_architect"
REQUIRED_INPUTS = [
    "artifacts/product/prd.md",
    "artifacts/design/architecture.md",
]
OUTPUTS = ["artifacts/design/frontend_spec.md"]
logger = logging.getLogger(AGENT_ID)


def main() -> None:
    setup_agent_logging(AGENT_ID)
    logger.info(f"=== {AGENT_ID} 開始 ===")
    check_inputs(REQUIRED_INPUTS)

    app = get_selected_app()
    out_dir = Path("artifacts/design")
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "frontend_spec.md").write_text(
        f"# frontend_spec.md — {app}\n\n"
        "## 画面構成\n\n"
        "- ヘッダー: アプリ名 + ナビゲーション\n"
        "- メインエリア: データ入力フォーム + 一覧表示\n"
        "- フッター: AdSense 広告枠\n\n"
        "## 技術仕様\n\n"
        "- HTML5 セマンティックタグ使用\n"
        "- CSS: Flexbox / Grid レイアウト\n"
        "- JS: ES2020 (モジュール不使用、単一ファイル)\n"
        "- レスポンシブ: media query (768px ブレークポイント)\n",
        encoding="utf-8",
    )
    logger.info("frontend_spec.md を出力しました")
    raise SystemExit(0)


if __name__ == "__main__":
    import os, sys
    from pathlib import Path
    os.chdir(Path(__file__).parent.parent.parent)
    sys.path.insert(0, str(Path(__file__).parent.parent))
    main()
