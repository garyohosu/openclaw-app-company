"""scripts/agents/adr_writer.py — ADR Writer (設計部)"""
import logging
from pathlib import Path
from agents._base import check_inputs, get_selected_app, setup_agent_logging

AGENT_ID = "adr_writer"
REQUIRED_INPUTS = ["artifacts/design/architecture.md"]
OUTPUTS = ["artifacts/design/adr/adr-001.md"]
logger = logging.getLogger(AGENT_ID)


def main() -> None:
    setup_agent_logging(AGENT_ID)
    logger.info(f"=== {AGENT_ID} 開始 ===")
    check_inputs(REQUIRED_INPUTS)

    app = get_selected_app()
    adr_dir = Path("artifacts/design/adr")
    adr_dir.mkdir(parents=True, exist_ok=True)
    (adr_dir / "adr-001.md").write_text(
        f"# ADR-001: {app} — 静的ホスティング採用\n\n"
        "## ステータス: Accepted\n\n"
        "## コンテキスト\n\n"
        f"{app} は個人向け軽量ツールであり、サーバー維持コストを最小化したい。\n\n"
        "## 決定\n\n"
        "GitHub Pages による静的ホスティングを採用する。\n"
        "データ永続化は LocalStorage を使用する。\n\n"
        "## 結果\n\n"
        "- インフラコストゼロ\n"
        "- オフライン動作可能\n"
        "- スケーラビリティは LocalStorage の容量に依存\n",
        encoding="utf-8",
    )
    logger.info("adr/adr-001.md を出力しました")
    raise SystemExit(0)


if __name__ == "__main__":
    import os, sys
    from pathlib import Path
    os.chdir(Path(__file__).parent.parent.parent)
    sys.path.insert(0, str(Path(__file__).parent.parent))
    main()
