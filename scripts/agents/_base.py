"""
scripts/agents/_base.py
エージェント共通ユーティリティ
"""
import logging
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

LOGS_DIR = Path("logs")
JST = ZoneInfo("Asia/Tokyo")


def setup_agent_logging(agent_id: str) -> logging.Logger:
    """エージェント用ロガーをセットアップする。重複設定を防ぐ。"""
    logger = logging.getLogger(agent_id)
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)
    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    today = datetime.now(JST).strftime("%Y-%m-%d")
    log_name = agent_id.replace("_", "-")
    log_file = LOGS_DIR / f"{log_name}-{today}.log"

    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fmt)

    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(fmt)

    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger


def check_inputs(required: list) -> None:
    """必須入力ファイルの存在確認。不在なら SystemExit(1) を送出する。"""
    for path_str in required:
        if not Path(path_str).exists():
            logging.getLogger("agents._base").error(
                f"Required input not found: {path_str}"
            )
            raise SystemExit(1)
