"""TC-20: Product フェーズ エージェントテスト"""
import logging
import pytest
from pathlib import Path

import agents.product_planner as product_planner
import agents.ux_scenario_writer as ux_scenario_writer
import agents.value_proposition_agent as value_proposition_agent
import agents.prd_writer as prd_writer

_AGENT_NAMES = [
    "product_planner", "ux_scenario_writer",
    "value_proposition_agent", "prd_writer",
]

SCORED_IDEAS = """\
# scored_ideas.md
source: research_report.md + idea_pool.md

## テストアプリ
score: 9

## サブアプリ
score: 7
"""

PRD_STUB = """\
# prd.md — テストアプリ

## 概要
テスト用 PRD。
"""


@pytest.fixture(autouse=True)
def reset_loggers():
    for name in _AGENT_NAMES:
        logging.getLogger(name).handlers.clear()
    yield
    for name in _AGENT_NAMES:
        logging.getLogger(name).handlers.clear()


# ---- product_planner --------------------------------------------------------

def test_tc_20_01_product_plan_generated(tmp_path, monkeypatch):
    """TC-20-01: scored_ideas.md が存在すると product_plan.md が生成される"""
    monkeypatch.chdir(tmp_path)
    research_dir = tmp_path / "artifacts" / "research"
    research_dir.mkdir(parents=True)
    (research_dir / "scored_ideas.md").write_text(SCORED_IDEAS, encoding="utf-8")

    with pytest.raises(SystemExit) as exc_info:
        product_planner.main()
    assert exc_info.value.code == 0
    plan = tmp_path / "artifacts" / "product" / "product_plan.md"
    assert plan.exists(), "product_plan.md が生成されていない"
    assert "テストアプリ" in plan.read_text(encoding="utf-8")


def test_tc_20_01_product_plan_missing_input(tmp_path, monkeypatch):
    """TC-20-01b: 入力不足時は失敗する"""
    monkeypatch.chdir(tmp_path)
    with pytest.raises(SystemExit) as exc_info:
        product_planner.main()
    assert exc_info.value.code == 1


# ---- prd_writer -------------------------------------------------------------

def test_tc_20_02_prd_generated(tmp_path, monkeypatch):
    """TC-20-02: prd.md が生成される"""
    monkeypatch.chdir(tmp_path)
    research_dir = tmp_path / "artifacts" / "research"
    research_dir.mkdir(parents=True)
    (research_dir / "scored_ideas.md").write_text(SCORED_IDEAS, encoding="utf-8")

    with pytest.raises(SystemExit) as exc_info:
        prd_writer.main()
    assert exc_info.value.code == 0
    prd = tmp_path / "artifacts" / "product" / "prd.md"
    assert prd.exists(), "prd.md が生成されていない"
    content = prd.read_text(encoding="utf-8")
    assert "テストアプリ" in content


def test_tc_20_02_prd_uses_decision(tmp_path, monkeypatch):
    """TC-20-02b: decision.md が存在すれば selected_app を反映する"""
    monkeypatch.chdir(tmp_path)
    research_dir = tmp_path / "artifacts" / "research"
    research_dir.mkdir(parents=True)
    (research_dir / "scored_ideas.md").write_text(SCORED_IDEAS, encoding="utf-8")
    exec_dir = tmp_path / "artifacts" / "executive"
    exec_dir.mkdir(parents=True)
    (exec_dir / "decision.md").write_text(
        "# decision.md\n\ndecision: approved\nselected_app: 決定アプリ\n",
        encoding="utf-8",
    )

    with pytest.raises(SystemExit) as exc_info:
        prd_writer.main()
    assert exc_info.value.code == 0
    content = (tmp_path / "artifacts" / "product" / "prd.md").read_text(encoding="utf-8")
    assert "決定アプリ" in content


# ---- ux_scenario_writer -----------------------------------------------------

def test_tc_20_03_ux_scenarios_generated(tmp_path, monkeypatch):
    """TC-20-03: ux_scenarios.md が生成される"""
    monkeypatch.chdir(tmp_path)
    product_dir = tmp_path / "artifacts" / "product"
    product_dir.mkdir(parents=True)
    (product_dir / "prd.md").write_text(PRD_STUB, encoding="utf-8")

    with pytest.raises(SystemExit) as exc_info:
        ux_scenario_writer.main()
    assert exc_info.value.code == 0
    assert (product_dir / "ux_scenarios.md").exists()


# ---- value_proposition_agent ------------------------------------------------

def test_tc_20_04_value_proposition_generated(tmp_path, monkeypatch):
    """TC-20-04: value_proposition.md が生成される"""
    monkeypatch.chdir(tmp_path)
    research_dir = tmp_path / "artifacts" / "research"
    research_dir.mkdir(parents=True)
    (research_dir / "scored_ideas.md").write_text(SCORED_IDEAS, encoding="utf-8")

    with pytest.raises(SystemExit) as exc_info:
        value_proposition_agent.main()
    assert exc_info.value.code == 0
    vp = tmp_path / "artifacts" / "product" / "value_proposition.md"
    assert vp.exists()
    assert "テストアプリ" in vp.read_text(encoding="utf-8")
