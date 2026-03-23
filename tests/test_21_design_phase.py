"""TC-21: Design フェーズ エージェントテスト"""
import logging
import pytest
from pathlib import Path

import agents.solution_architect as solution_architect
import agents.frontend_architect as frontend_architect
import agents.api_integration_architect as api_integration_architect
import agents.adr_writer as adr_writer
import agents.tech_lead as tech_lead
import agents.task_breakdown_agent as task_breakdown_agent

_AGENT_NAMES = [
    "solution_architect", "frontend_architect", "api_integration_architect",
    "adr_writer", "tech_lead", "task_breakdown_agent",
]

PRD_STUB = "# prd.md — テストアプリ\n\n## 概要\nテスト用。\n"
ARCH_STUB = "# architecture.md — テストアプリ\n\n## アーキテクチャ\n静的ホスティング。\n"
TASKS_STUB = (
    "# tasks.md — テストアプリ\n\n"
    "## task-001: 基本実装\nruntime_mode: static\n"
)


@pytest.fixture(autouse=True)
def reset_loggers():
    for name in _AGENT_NAMES:
        logging.getLogger(name).handlers.clear()
    yield
    for name in _AGENT_NAMES:
        logging.getLogger(name).handlers.clear()


def _setup_product(tmp_path: Path) -> None:
    (tmp_path / "artifacts" / "product").mkdir(parents=True)
    (tmp_path / "artifacts" / "product" / "prd.md").write_text(PRD_STUB, encoding="utf-8")


def _setup_design(tmp_path: Path) -> None:
    design_dir = tmp_path / "artifacts" / "design"
    design_dir.mkdir(parents=True)
    (design_dir / "architecture.md").write_text(ARCH_STUB, encoding="utf-8")


def _setup_tasks(tmp_path: Path) -> None:
    design_dir = tmp_path / "artifacts" / "design"
    design_dir.mkdir(parents=True, exist_ok=True)
    (design_dir / "tasks.md").write_text(TASKS_STUB, encoding="utf-8")


# ---- solution_architect -------------------------------------------------------

def test_tc_21_01_architecture_generated(tmp_path, monkeypatch):
    """TC-21-01: prd.md があると architecture.md が生成される"""
    monkeypatch.chdir(tmp_path)
    _setup_product(tmp_path)

    with pytest.raises(SystemExit) as exc_info:
        solution_architect.main()
    assert exc_info.value.code == 0
    assert (tmp_path / "artifacts" / "design" / "architecture.md").exists()


def test_tc_21_01b_architecture_missing_input(tmp_path, monkeypatch):
    """TC-21-01b: 入力不足時は失敗する"""
    monkeypatch.chdir(tmp_path)
    with pytest.raises(SystemExit) as exc_info:
        solution_architect.main()
    assert exc_info.value.code == 1


# ---- frontend_architect -------------------------------------------------------

def test_tc_21_02_frontend_spec_generated(tmp_path, monkeypatch):
    """TC-21-02: frontend_spec.md が生成される"""
    monkeypatch.chdir(tmp_path)
    _setup_product(tmp_path)
    _setup_design(tmp_path)

    with pytest.raises(SystemExit) as exc_info:
        frontend_architect.main()
    assert exc_info.value.code == 0
    assert (tmp_path / "artifacts" / "design" / "frontend_spec.md").exists()


# ---- api_integration_architect ------------------------------------------------

def test_tc_21_03_api_spec_generated(tmp_path, monkeypatch):
    """TC-21-03: api_spec.md が生成される"""
    monkeypatch.chdir(tmp_path)
    _setup_product(tmp_path)

    with pytest.raises(SystemExit) as exc_info:
        api_integration_architect.main()
    assert exc_info.value.code == 0
    assert (tmp_path / "artifacts" / "design" / "api_spec.md").exists()


# ---- adr_writer ---------------------------------------------------------------

def test_tc_21_04_adr_generated(tmp_path, monkeypatch):
    """TC-21-04: adr/adr-001.md が生成される"""
    monkeypatch.chdir(tmp_path)
    _setup_design(tmp_path)

    with pytest.raises(SystemExit) as exc_info:
        adr_writer.main()
    assert exc_info.value.code == 0
    assert (tmp_path / "artifacts" / "design" / "adr" / "adr-001.md").exists()


# ---- task_breakdown_agent -----------------------------------------------------

def test_tc_21_05_tasks_generated(tmp_path, monkeypatch):
    """TC-21-05: tasks.md が codex_prompt_writer 形式で生成される"""
    monkeypatch.chdir(tmp_path)
    _setup_design(tmp_path)

    with pytest.raises(SystemExit) as exc_info:
        task_breakdown_agent.main()
    assert exc_info.value.code == 0
    tasks = tmp_path / "artifacts" / "design" / "tasks.md"
    assert tasks.exists()
    content = tasks.read_text(encoding="utf-8")
    assert "## task-001:" in content
    assert "runtime_mode: static" in content


# ---- tech_lead ----------------------------------------------------------------

def test_tc_21_06_tech_review_generated(tmp_path, monkeypatch):
    """TC-21-06: tech_review.md が生成され、reviewed_basis が記録される"""
    monkeypatch.chdir(tmp_path)
    _setup_tasks(tmp_path)

    with pytest.raises(SystemExit) as exc_info:
        tech_lead.main()
    assert exc_info.value.code == 0
    review = tmp_path / "artifacts" / "implementation" / "tech_review.md"
    assert review.exists()
    content = review.read_text(encoding="utf-8")
    assert "reviewed_basis:" in content
    assert "tasks_snapshot:" in content


def test_tc_21_06b_tech_review_stub_basis(tmp_path, monkeypatch):
    """TC-21-06b: stub tasks.md (task-NNN なし) では reviewed_basis が stub と明示される"""
    monkeypatch.chdir(tmp_path)
    design_dir = tmp_path / "artifacts" / "design"
    design_dir.mkdir(parents=True)
    (design_dir / "tasks.md").write_text("# tasks.md (stub)\nsummary: placeholder\n", encoding="utf-8")

    with pytest.raises(SystemExit) as exc_info:
        tech_lead.main()
    assert exc_info.value.code == 0
    content = (tmp_path / "artifacts" / "implementation" / "tech_review.md").read_text(encoding="utf-8")
    assert "stub" in content
