"""
scripts/main.py
OpenClaw オーケストレータ — 全フェーズを順番に実行する唯一の定義元

使い方:
  python scripts/main.py                  # 全フェーズ実行
  python scripts/main.py --dry-run        # Git操作なし
  python scripts/main.py --phase research # 特定フェーズのみ

各サブスクリプトは SystemExit(0) を「正常終了」、SystemExit(1) を「異常終了」として使う。
異常終了が発生した場合、以降のフェーズは実行しない。
"""

import argparse
import logging
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

LOGS_DIR = Path("logs")
JST = ZoneInfo("Asia/Tokyo")
ARTIFACTS_DIR = Path("artifacts")
STATE_PATH = Path("state/company_state.json")

ADSENSE_PUB_ID = "ca-pub-6743751614716161"


# ---- ログ設定 ---------------------------------------------------------------

def setup_logging() -> logging.Logger:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    today = datetime.now(JST).strftime("%Y-%m-%d")
    log_path = LOGS_DIR / f"main-{today}.log"

    logger = logging.getLogger("main")
    logger.setLevel(logging.DEBUG)

    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

    fh = logging.FileHandler(log_path, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fmt)

    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(fmt)

    if not logger.handlers:
        logger.addHandler(fh)
        logger.addHandler(ch)
    return logger


def _get_logger() -> logging.Logger:
    return logging.getLogger("main")


# ---- フェーズ実行ヘルパー ---------------------------------------------------

def run_phase(name: str, fn) -> bool:
    """
    fn() を呼び出す。
    - 正常終了 (return / SystemExit(0)): True を返す
    - 異常終了 (SystemExit(1) / 例外)  : False を返す
    """
    logger = _get_logger()
    logger.info(f"▶ {name} 開始")
    try:
        fn()
        logger.info(f"✓ {name} 完了")
        return True
    except SystemExit as e:
        code = e.code if isinstance(e.code, int) else 1
        if code == 0:
            logger.info(f"✓ {name} 完了 (新規なし)")
            return True
        logger.error(f"✗ {name} 失敗 (exit {code})")
        return False
    except Exception as e:
        logger.exception(f"✗ {name} 例外: {e}")
        return False


# ---- QualityGate 更新 -------------------------------------------------------

def update_state_after_phase(state, phase: str, artifacts_dir: Path = ARTIFACTS_DIR) -> None:
    """
    フェーズ完了後に成果物レポートを読んで QualityGate フラグを更新する。
    エージェントは state を直接書き換えず、OpenClaw がここで一括更新する。
    """
    if phase == "api_connectivity":
        report = artifacts_dir / "design/api_connectivity_report.md"
        if report.exists():
            content = report.read_text(encoding="utf-8")
            if "NG" not in content and "FAIL" not in content:
                state.quality_gate.ssl_verified = True
                state.quality_gate.cors_verified = True

    elif phase == "testing":
        report = artifacts_dir / "qa/browser_test_report.md"
        if report.exists():
            content = report.read_text(encoding="utf-8")
            if "FAIL" not in content and "NG" not in content:
                state.quality_gate.browser_test_passed = True

    elif phase == "release":
        report = artifacts_dir / "sprints/deploy_report.md"
        if report.exists():
            content = report.read_text(encoding="utf-8")
            if "AdSense OK" in content:
                state.quality_gate.adsense_verified = True
            if "混入なし" in content:
                state.quality_gate.test_pages_adsense_clean = True
            if "Release OK" in content:
                state.quality_gate.release_gate_passed = True
            if "Release NG" in content:
                state.quality_gate.release_gate_passed = False


# ---- メイン -----------------------------------------------------------------

def main() -> None:
    setup_logging()
    logger = _get_logger()

    parser = argparse.ArgumentParser(description="OpenClaw オーケストレータ")
    parser.add_argument("--dry-run", action="store_true", help="Git操作なし")
    parser.add_argument("--phase", default="all", help="実行フェーズ指定")
    args = parser.parse_args()

    logger.info("=" * 60)
    logger.info("=== OpenClaw パイプライン 開始 ===")
    logger.info(f"    dry_run={args.dry_run}  phase={args.phase}")
    logger.info("=" * 60)

    import agents.market_researcher as market_researcher
    import agents.trend_analyst as trend_analyst
    import agents.pain_finder as pain_finder
    import agents.competitor_analyst as competitor_analyst
    import agents.idea_scorer as idea_scorer
    import agents.roi_agent as roi_agent
    import agents.ceo as ceo
    import agents.coo as coo
    import agents.product_planner as product_planner
    import agents.ux_scenario_writer as ux_scenario_writer
    import agents.value_proposition_agent as value_proposition_agent
    import agents.prd_writer as prd_writer
    import agents.solution_architect as solution_architect
    import agents.frontend_architect as frontend_architect
    import agents.api_integration_architect as api_integration_architect
    import agents.adr_writer as adr_writer
    import agents.tech_lead as tech_lead
    import agents.task_breakdown_agent as task_breakdown_agent
    import agents.codex_prompt_writer as codex_prompt_writer
    import agents.github_pages_release_manager as github_pages_release_manager
    import agents.sakura_api_coordinator as sakura_api_coordinator
    import agents.improvement_strategist as improvement_strategist

    from state.company_state import CompanyState

    state_path = STATE_PATH
    if state_path.exists():
        state = CompanyState.load(state_path)
    else:
        state = CompanyState.default()

    # Phase 1-2: 市場調査・アイデア選定
    for name, fn in [
        ("market_researcher", market_researcher.main),
        ("trend_analyst", trend_analyst.main),
        ("pain_finder", pain_finder.main),
        ("competitor_analyst", competitor_analyst.main),
        ("roi_agent", roi_agent.main),
        ("idea_scorer", idea_scorer.main),
        ("ceo", ceo.main),
        ("coo", coo.main),
    ]:
        if not run_phase(name, fn):
            state.next_action = f"fix-{name}-failure"
            state.save(state_path)
            logger.error(f"{name} 失敗。以降のフェーズをスキップします")
            sys.exit(1)

    # Phase 3: PRD作成
    for name, fn in [
        ("product_planner", product_planner.main),
        ("ux_scenario_writer", ux_scenario_writer.main),
        ("value_proposition_agent", value_proposition_agent.main),
        ("prd_writer", prd_writer.main),
    ]:
        if not run_phase(name, fn):
            state.next_action = f"fix-{name}-failure"
            state.save(state_path)
            sys.exit(1)

    # Phase 4-5: 設計・タスク分解
    for name, fn in [
        ("solution_architect", solution_architect.main),
        ("frontend_architect", frontend_architect.main),
        ("api_integration_architect", api_integration_architect.main),
        ("adr_writer", adr_writer.main),
        ("tech_lead", tech_lead.main),
        ("task_breakdown_agent", task_breakdown_agent.main),
    ]:
        if not run_phase(name, fn):
            state.next_action = f"fix-{name}-failure"
            state.save(state_path)
            sys.exit(1)

    # Phase 6: API疎通確認 (toolbox/db のみ)
    if state.runtime_mode in ("toolbox", "db"):
        if not run_phase("sakura_api_coordinator", sakura_api_coordinator.main):
            state.next_action = "fix-api-connectivity"
            state.save(state_path)
            sys.exit(1)
        update_state_after_phase(state, "api_connectivity")
        state.save(state_path)

    # Phase 8: Codex CLI 委任書作成
    if not run_phase("codex_prompt_writer", codex_prompt_writer.main):
        state.next_action = "fix-prompt-creation"
        state.save(state_path)
        sys.exit(1)

    # Phase 11: GitHub Pages 公開
    if not run_phase("github_pages_release_manager", github_pages_release_manager.main):
        state.next_action = "fix-release"
        state.save(state_path)
        sys.exit(1)
    update_state_after_phase(state, "release")
    state.save(state_path)

    # Phase 12: 改善スプリント
    if not run_phase("improvement_strategist", improvement_strategist.main):
        state.next_action = "fix-improvement"
        state.save(state_path)
        sys.exit(1)

    logger.info("=" * 60)
    logger.info("=== パイプライン 完了 ===")
    logger.info("=" * 60)


if __name__ == "__main__":
    import os
    scripts_dir = Path(__file__).parent
    repo_root = scripts_dir.parent
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))
    os.chdir(repo_root)
    main()
