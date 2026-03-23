"""TC-04: エージェント基底規約テスト"""
import importlib
import os
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest

AGENT_IDS = [
    "ceo", "coo", "roi_agent",
    "market_researcher", "trend_analyst", "pain_finder",
    "competitor_analyst", "idea_scorer",
    "product_planner", "ux_scenario_writer", "value_proposition_agent", "prd_writer",
    "solution_architect", "frontend_architect", "api_integration_architect", "adr_writer",
    "tech_lead", "task_breakdown_agent", "codex_prompt_writer", "refactor_director",
    "test_designer", "tdd_enforcer", "bug_triage_agent", "browser_test_operator",
    "design_critic", "copy_critic", "accessibility_reviewer",
    "github_pages_release_manager", "sakura_api_coordinator", "improvement_strategist",
]


@pytest.mark.parametrize("agent_id", AGENT_IDS)
def test_tc_04_01_has_main(agent_id):
    """TC-04-01: 全30エージェントが main() 関数を持つ"""
    mod = importlib.import_module(f"agents.{agent_id}")
    assert hasattr(mod, "main"), f"agents/{agent_id}.py has no main()"
    assert callable(mod.main)


@pytest.mark.parametrize("agent_id", AGENT_IDS)
def test_tc_04_01_has_required_inputs_attr(agent_id):
    """全30エージェントが REQUIRED_INPUTS 属性を持つ"""
    mod = importlib.import_module(f"agents.{agent_id}")
    assert hasattr(mod, "REQUIRED_INPUTS"), f"{agent_id} has no REQUIRED_INPUTS"
    assert isinstance(mod.REQUIRED_INPUTS, list)


@pytest.mark.parametrize("agent_id", AGENT_IDS)
def test_tc_04_03_missing_input_exits_1(agent_id, tmp_path, monkeypatch):
    """TC-04-03: 必須入力ファイルが存在しない場合 SystemExit(1) が送出される"""
    monkeypatch.chdir(tmp_path)
    # ロガーのハンドラをリセット（重複ハンドラ防止）
    import logging
    for name in [agent_id, "agents._base"]:
        logging.getLogger(name).handlers.clear()

    mod = importlib.import_module(f"agents.{agent_id}")
    required = getattr(mod, "REQUIRED_INPUTS", [])
    if not required:
        pytest.skip(f"{agent_id} has no required inputs")

    with pytest.raises(SystemExit) as exc_info:
        mod.main()
    assert exc_info.value.code == 1


@pytest.mark.parametrize("agent_id", AGENT_IDS)
def test_tc_04_04_log_file_created(agent_id, tmp_path, monkeypatch):
    """TC-04-04: main() 実行後にログファイルが生成される"""
    monkeypatch.chdir(tmp_path)
    import logging
    logging.getLogger(agent_id).handlers.clear()

    mod = importlib.import_module(f"agents.{agent_id}")
    try:
        mod.main()
    except SystemExit:
        pass

    jst = ZoneInfo("Asia/Tokyo")
    today = datetime.now(jst).strftime("%Y-%m-%d")
    log_name = agent_id.replace("_", "-")
    log_file = tmp_path / "logs" / f"{log_name}-{today}.log"
    assert log_file.exists(), f"Log file not found: {log_file}"


@pytest.mark.parametrize("agent_id", AGENT_IDS)
def test_tc_04_05_has_outputs_attr(agent_id):
    """全30エージェントが OUTPUTS 属性を持つ"""
    mod = importlib.import_module(f"agents.{agent_id}")
    assert hasattr(mod, "OUTPUTS"), f"{agent_id} has no OUTPUTS"
    assert isinstance(mod.OUTPUTS, list)
