"""scripts/agents/api_integration_architect.py — API Integration Architect (設計部)"""
import logging
from pathlib import Path
from agents._base import check_inputs, get_selected_app, setup_agent_logging

AGENT_ID = "api_integration_architect"
REQUIRED_INPUTS = ["artifacts/product/prd.md"]
OUTPUTS = ["artifacts/design/api_spec.md"]
logger = logging.getLogger(AGENT_ID)


def main() -> None:
    setup_agent_logging(AGENT_ID)
    logger.info(f"=== {AGENT_ID} 開始 ===")
    check_inputs(REQUIRED_INPUTS)

    app = get_selected_app()
    out_dir = Path("artifacts/design")
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "api_spec.md").write_text(
        f"# api_spec.md — {app}\n\n"
        "## API 方針\n\n"
        "- 静的ホスティング優先のため外部 API 呼び出しなし\n"
        "- データは LocalStorage で完結\n"
        "- Sakura CGI API Toolbox は今スプリントでは不使用\n\n"
        "## 将来の拡張候補\n\n"
        "- データのサーバーバックアップ (CGI 連携)\n"
        "- 外部データ取得 (Weather API 等)\n",
        encoding="utf-8",
    )
    logger.info("api_spec.md を出力しました")
    raise SystemExit(0)


if __name__ == "__main__":
    import os, sys
    from pathlib import Path
    os.chdir(Path(__file__).parent.parent.parent)
    sys.path.insert(0, str(Path(__file__).parent.parent))
    main()
