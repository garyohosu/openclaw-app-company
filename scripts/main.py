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

def setup_logging(dry_run: bool = False) -> logging.Logger:
    logger = logging.getLogger("main")
    logger.setLevel(logging.DEBUG)
    if logger.handlers:
        return logger

    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

    if not dry_run:
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
        today = datetime.now(JST).strftime("%Y-%m-%d")
        log_path = LOGS_DIR / f"main-{today}.log"
        fh = logging.FileHandler(log_path, encoding="utf-8")
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(fmt)
        logger.addHandler(fh)

    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(fmt)
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


def reset_quality_gate_for_phase(state, phase: str) -> None:
    if phase == "api_connectivity":
        state.quality_gate.ssl_verified = False
        state.quality_gate.cors_verified = False
    elif phase == "testing":
        state.quality_gate.browser_test_passed = False
    elif phase == "release":
        state.quality_gate.adsense_verified = False
        state.quality_gate.test_pages_adsense_clean = False
        state.quality_gate.release_gate_passed = False


def _list_step_inputs(step_module) -> list[str]:
    return list(getattr(step_module, "REQUIRED_INPUTS", []))


def _list_step_outputs(step_module) -> list[str]:
    return list(getattr(step_module, "OUTPUTS", []))


def _check_required_inputs(required: list[str]) -> list[str]:
    missing = []
    for path_str in required:
        if not Path(path_str).exists():
            missing.append(path_str)
    return missing


# ---- メイン -----------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="OpenClaw オーケストレータ")
    parser.add_argument("--dry-run", action="store_true", help="no-write mode")
    parser.add_argument("--phase", default="all", help="実行フェーズ指定")
    args = parser.parse_args()

    setup_logging(dry_run=args.dry_run)
    logger = _get_logger()

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

    phases = [
        {
            "id": "research",
            "steps": [
                ("market_researcher", market_researcher),
                ("trend_analyst", trend_analyst),
                ("pain_finder", pain_finder),
                ("competitor_analyst", competitor_analyst),
                ("roi_agent", roi_agent),
                ("idea_scorer", idea_scorer),
                ("ceo", ceo),
                ("coo", coo),
            ],
        },
        {
            "id": "product",
            "steps": [
                ("product_planner", product_planner),
                ("ux_scenario_writer", ux_scenario_writer),
                ("value_proposition_agent", value_proposition_agent),
                ("prd_writer", prd_writer),
            ],
        },
        {
            "id": "design",
            "steps": [
                ("solution_architect", solution_architect),
                ("frontend_architect", frontend_architect),
                ("api_integration_architect", api_integration_architect),
                ("adr_writer", adr_writer),
                ("tech_lead", tech_lead),
                ("task_breakdown_agent", task_breakdown_agent),
            ],
        },
        {
            "id": "api_connectivity",
            "steps": [
                ("sakura_api_coordinator", sakura_api_coordinator),
            ],
            "condition": lambda st: st.runtime_mode in ("toolbox", "db"),
        },
        {
            "id": "prompt",
            "steps": [
                ("codex_prompt_writer", codex_prompt_writer),
            ],
        },
        {
            "id": "release",
            "steps": [
                ("github_pages_release_manager", github_pages_release_manager),
            ],
        },
        {
            "id": "improvement",
            "steps": [
                ("improvement_strategist", improvement_strategist),
            ],
        },
    ]

    phase_ids = [p["id"] for p in phases]
    if args.phase != "all" and args.phase not in phase_ids:
        logger.error(f"Unknown phase: {args.phase}")
        logger.error(f"Available: {', '.join(phase_ids)}")
        sys.exit(1)

    def _run_selected_phase(phase, next_phase_id: str | None) -> None:
        phase_id = phase["id"]
        condition = phase.get("condition")
        if condition is not None and not condition(state):
            logger.info(f"↷ {phase_id} スキップ (runtime_mode={state.runtime_mode})")
            if not args.dry_run:
                state.current_phase = phase_id
                state.next_action = f"skipped-{phase_id}"
                state.save(state_path)
            return

        steps = phase["steps"]
        all_required: list[str] = []
        all_outputs: list[str] = []
        for _, mod in steps:
            all_required.extend(_list_step_inputs(mod))
            all_outputs.extend(_list_step_outputs(mod))

        missing = _check_required_inputs(all_required)
        if missing:
            logger.error(f"{phase_id} 必須入力不足: {missing}")
            if not args.dry_run:
                state.current_phase = phase_id
                state.next_action = f"fix-{phase_id}-missing-inputs"
                state.save(state_path)
            sys.exit(1)

        if args.dry_run:
            logger.info(f"[dry-run] Phase: {phase_id}")
            logger.info(f"[dry-run] Steps: {[name for name, _ in steps]}")
            logger.info(f"[dry-run] Required inputs: {sorted(set(all_required))}")
            logger.info(f"[dry-run] Expected outputs: {sorted(set(all_outputs))}")
            if phase_id in ("api_connectivity", "testing", "release"):
                logger.info(f"[dry-run] Would reset quality_gate for {phase_id}")
                logger.info(f"[dry-run] Would update quality_gate after {phase_id} if reports are OK")
            return

        state.current_phase = phase_id
        state.next_action = f"running-{phase_id}"
        reset_quality_gate_for_phase(state, phase_id)
        state.save(state_path)

        for name, mod in steps:
            if not run_phase(name, mod.main):
                state.next_action = f"fix-{name}-failure"
                state.save(state_path)
                logger.error(f"{name} 失敗。以降のフェーズをスキップします")
                sys.exit(1)

        update_state_after_phase(state, phase_id)
        if next_phase_id is None:
            state.next_action = "pipeline-complete"
        else:
            state.next_action = f"start-{next_phase_id}"
        state.save(state_path)

    selected = phases if args.phase == "all" else [
        p for p in phases if p["id"] == args.phase
    ]

    for idx, phase in enumerate(selected):
        next_phase_id = None
        if args.phase == "all" and idx + 1 < len(selected):
            next_phase_id = selected[idx + 1]["id"]
        elif args.phase != "all":
            current_index = phase_ids.index(args.phase)
            if current_index + 1 < len(phase_ids):
                next_phase_id = phase_ids[current_index + 1]
        _run_selected_phase(phase, next_phase_id)

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
