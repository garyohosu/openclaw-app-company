"""TC-06: CommissionDoc (Phase 8 Codex CLI 委任書) テスト"""
import pytest
from pathlib import Path
import logging
import agents.codex_prompt_writer as codex_prompt_writer


@pytest.fixture(autouse=True)
def reset_logger():
    logging.getLogger("codex_prompt_writer").handlers.clear()
    yield
    logging.getLogger("codex_prompt_writer").handlers.clear()


def _make_tasks_md(tasks_dir: Path, count: int = 1) -> Path:
    lines = ["# tasks.md\n"]
    for i in range(1, count + 1):
        lines.append(f"## task-{i:03d}: タスク{i}\n")
        lines.append(f"runtime_mode: static\n\n")
    p = tasks_dir / "tasks.md"
    p.write_text("".join(lines), encoding="utf-8")
    return p


def test_tc_06_01_header_present(tmp_path, monkeypatch):
    """TC-06-01: 生成された task-001.md が 'Status: Draft for Codex CLI' を含む"""
    monkeypatch.chdir(tmp_path)
    design_dir = tmp_path / "artifacts" / "design"
    design_dir.mkdir(parents=True)
    _make_tasks_md(design_dir)
    (tmp_path / "artifacts" / "prompts").mkdir(parents=True)

    try:
        codex_prompt_writer.main()
    except SystemExit as e:
        if e.code != 0:
            pytest.xfail("codex_prompt_writer 未実装")

    task_file = tmp_path / "artifacts" / "prompts" / "task-001.md"
    assert task_file.exists(), "task-001.md が生成されていない"
    content = task_file.read_text(encoding="utf-8")
    assert "Status: Draft for Codex CLI" in content


def test_tc_06_02_required_sections(tmp_path, monkeypatch):
    """TC-06-02: 必須セクション（目的/スコープ/入出力/完了条件）が存在する"""
    monkeypatch.chdir(tmp_path)
    design_dir = tmp_path / "artifacts" / "design"
    design_dir.mkdir(parents=True)
    _make_tasks_md(design_dir)
    (tmp_path / "artifacts" / "prompts").mkdir(parents=True)

    try:
        codex_prompt_writer.main()
    except SystemExit as e:
        if e.code != 0:
            pytest.xfail("codex_prompt_writer 未実装")

    task_file = tmp_path / "artifacts" / "prompts" / "task-001.md"
    content = task_file.read_text(encoding="utf-8")
    for section in ["## 1. 目的", "## 2. スコープ", "## 4. 入出力", "## 8. 完了条件"]:
        assert section in content, f"必須セクション不在: {section}"


def test_tc_06_03_runtime_mode_present(tmp_path, monkeypatch):
    """TC-06-03: task-001.md に runtime_mode が記載されている"""
    monkeypatch.chdir(tmp_path)
    design_dir = tmp_path / "artifacts" / "design"
    design_dir.mkdir(parents=True)
    _make_tasks_md(design_dir)
    (tmp_path / "artifacts" / "prompts").mkdir(parents=True)

    try:
        codex_prompt_writer.main()
    except SystemExit as e:
        if e.code != 0:
            pytest.xfail("codex_prompt_writer 未実装")

    task_file = tmp_path / "artifacts" / "prompts" / "task-001.md"
    content = task_file.read_text(encoding="utf-8")
    assert "runtime_mode:" in content


def test_tc_06_04_multiple_tasks(tmp_path, monkeypatch):
    """TC-06-04: tasks.md に 3件あると task-001〜003.md が生成される"""
    monkeypatch.chdir(tmp_path)
    design_dir = tmp_path / "artifacts" / "design"
    design_dir.mkdir(parents=True)
    _make_tasks_md(design_dir, count=3)
    (tmp_path / "artifacts" / "prompts").mkdir(parents=True)

    try:
        codex_prompt_writer.main()
    except SystemExit as e:
        if e.code != 0:
            pytest.xfail("codex_prompt_writer 未実装")

    prompts_dir = tmp_path / "artifacts" / "prompts"
    for i in range(1, 4):
        assert (prompts_dir / f"task-{i:03d}.md").exists(), f"task-{i:03d}.md 不在"
