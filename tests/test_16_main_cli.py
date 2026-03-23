"""TC-16: main.py CLI と state/quality_gate 更新テスト"""
from __future__ import annotations

import logging
from pathlib import Path

import pytest

import main as main_mod
from state.company_state import CompanyState


def _clear_main_logger():
    logging.getLogger("main").handlers.clear()


def _patch_agent(monkeypatch, module, *, required_inputs=None, outputs=None, main_impl=None):
    if required_inputs is not None:
        monkeypatch.setattr(module, "REQUIRED_INPUTS", required_inputs, raising=False)
    if outputs is not None:
        monkeypatch.setattr(module, "OUTPUTS", outputs, raising=False)
    if main_impl is not None:
        monkeypatch.setattr(module, "main", main_impl, raising=True)


def _write_state(tmp_path: Path, **kwargs) -> Path:
    state = CompanyState.default()
    for k, v in kwargs.items():
        setattr(state, k, v)
    state_path = tmp_path / "state" / "company_state.json"
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state.save(state_path)
    return state_path


def test_tc_16_01_phase_only_runs_selected(tmp_path, monkeypatch):
    """TC-16-01: --phase で指定フェーズのみ実行される"""
    monkeypatch.chdir(tmp_path)
    _clear_main_logger()

    import agents.codex_prompt_writer as codex_prompt_writer
    import agents.product_planner as product_planner
    import agents.github_pages_release_manager as github_pages_release_manager

    calls = []

    def prompt_main():
        calls.append("prompt")

    def should_not_run():
        raise AssertionError("unexpected phase executed")

    _patch_agent(
        monkeypatch,
        codex_prompt_writer,
        required_inputs=["artifacts/design/tasks.md"],
        outputs=["artifacts/prompts/task-001.md"],
        main_impl=prompt_main,
    )
    _patch_agent(monkeypatch, product_planner, main_impl=should_not_run)
    _patch_agent(monkeypatch, github_pages_release_manager, main_impl=should_not_run)

    (tmp_path / "artifacts" / "design").mkdir(parents=True)
    (tmp_path / "artifacts" / "design" / "tasks.md").write_text("# tasks\n", encoding="utf-8")

    monkeypatch.setattr(main_mod.sys, "argv", ["main.py", "--phase", "prompt"])
    main_mod.main()

    assert calls == ["prompt"]


def test_tc_16_02_phase_missing_inputs_fails(tmp_path, monkeypatch):
    """TC-16-02: --phase で必須入力不足なら失敗する"""
    monkeypatch.chdir(tmp_path)
    _clear_main_logger()

    import agents.codex_prompt_writer as codex_prompt_writer

    _patch_agent(
        monkeypatch,
        codex_prompt_writer,
        required_inputs=["missing.txt"],
        outputs=["artifacts/prompts/task-001.md"],
        main_impl=lambda: None,
    )

    monkeypatch.setattr(main_mod.sys, "argv", ["main.py", "--phase", "prompt"])

    with pytest.raises(SystemExit) as exc_info:
        main_mod.main()
    assert exc_info.value.code == 1

    state = CompanyState.load(tmp_path / "state" / "company_state.json")
    assert state.current_phase == "prompt"
    assert state.next_action == "fix-prompt-missing-inputs"


def test_tc_16_03_dry_run_no_write(tmp_path, monkeypatch):
    """TC-16-03: --dry-run は no-write で state/log/成果物を書かない"""
    monkeypatch.chdir(tmp_path)
    _clear_main_logger()

    import agents.codex_prompt_writer as codex_prompt_writer

    _patch_agent(
        monkeypatch,
        codex_prompt_writer,
        required_inputs=["artifacts/design/tasks.md"],
        outputs=["artifacts/prompts/task-001.md"],
        main_impl=lambda: None,
    )

    (tmp_path / "artifacts" / "design").mkdir(parents=True)
    (tmp_path / "artifacts" / "design" / "tasks.md").write_text("# tasks\n", encoding="utf-8")

    monkeypatch.setattr(main_mod.sys, "argv", ["main.py", "--phase", "prompt", "--dry-run"])
    main_mod.main()

    assert not (tmp_path / "state" / "company_state.json").exists()
    assert not (tmp_path / "logs").exists()
    assert not (tmp_path / "artifacts" / "prompts" / "task-001.md").exists()


def test_tc_16_04_quality_gate_release_updates_on_report(tmp_path, monkeypatch):
    """TC-16-04: release 開始時にリセットし、レポート合格で true になる"""
    monkeypatch.chdir(tmp_path)
    _clear_main_logger()

    import agents.github_pages_release_manager as github_pages_release_manager

    _patch_agent(
        monkeypatch,
        github_pages_release_manager,
        required_inputs=[],
        outputs=["artifacts/sprints/deploy_report.md"],
        main_impl=lambda: None,
    )

    state = CompanyState.default()
    state.quality_gate.adsense_verified = True
    state.quality_gate.test_pages_adsense_clean = True
    state.quality_gate.release_gate_passed = True
    _write_state(tmp_path, quality_gate=state.quality_gate)

    report = tmp_path / "artifacts" / "sprints" / "deploy_report.md"
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text("AdSense OK\n混入なし\nRelease OK\n", encoding="utf-8")

    monkeypatch.setattr(main_mod.sys, "argv", ["main.py", "--phase", "release"])
    main_mod.main()

    updated = CompanyState.load(tmp_path / "state" / "company_state.json")
    assert updated.quality_gate.adsense_verified is True
    assert updated.quality_gate.test_pages_adsense_clean is True
    assert updated.quality_gate.release_gate_passed is True


def test_tc_16_05_quality_gate_report_missing_keeps_false(tmp_path, monkeypatch):
    """TC-16-05: レポート不在時は false のまま保持される"""
    monkeypatch.chdir(tmp_path)
    _clear_main_logger()

    import agents.github_pages_release_manager as github_pages_release_manager

    _patch_agent(
        monkeypatch,
        github_pages_release_manager,
        required_inputs=[],
        outputs=["artifacts/sprints/deploy_report.md"],
        main_impl=lambda: None,
    )

    state = CompanyState.default()
    state.quality_gate.adsense_verified = True
    state.quality_gate.test_pages_adsense_clean = True
    state.quality_gate.release_gate_passed = True
    _write_state(tmp_path, quality_gate=state.quality_gate)

    monkeypatch.setattr(main_mod.sys, "argv", ["main.py", "--phase", "release"])
    main_mod.main()

    updated = CompanyState.load(tmp_path / "state" / "company_state.json")
    assert updated.quality_gate.adsense_verified is False
    assert updated.quality_gate.test_pages_adsense_clean is False
    assert updated.quality_gate.release_gate_passed is False


def test_tc_16_06_quality_gate_failure_keeps_false(tmp_path, monkeypatch):
    """TC-16-06: フェーズ失敗時は false のまま保持される"""
    monkeypatch.chdir(tmp_path)
    _clear_main_logger()

    import agents.github_pages_release_manager as github_pages_release_manager

    _patch_agent(
        monkeypatch,
        github_pages_release_manager,
        required_inputs=[],
        outputs=["artifacts/sprints/deploy_report.md"],
        main_impl=lambda: None,
    )

    state = CompanyState.default()
    state.quality_gate.adsense_verified = True
    state.quality_gate.test_pages_adsense_clean = True
    state.quality_gate.release_gate_passed = True
    _write_state(tmp_path, quality_gate=state.quality_gate)

    monkeypatch.setattr(main_mod, "run_phase", lambda name, fn: False)
    monkeypatch.setattr(main_mod.sys, "argv", ["main.py", "--phase", "release"])

    with pytest.raises(SystemExit) as exc_info:
        main_mod.main()
    assert exc_info.value.code == 1

    updated = CompanyState.load(tmp_path / "state" / "company_state.json")
    assert updated.quality_gate.adsense_verified is False
    assert updated.quality_gate.test_pages_adsense_clean is False
    assert updated.quality_gate.release_gate_passed is False
    assert updated.current_phase == "release"
    assert updated.next_action == "fix-github_pages_release_manager-failure"


def test_tc_16_07_current_phase_and_next_action(tmp_path, monkeypatch):
    """TC-16-07: current_phase と next_action が更新される"""
    monkeypatch.chdir(tmp_path)
    _clear_main_logger()

    import agents.codex_prompt_writer as codex_prompt_writer

    _patch_agent(
        monkeypatch,
        codex_prompt_writer,
        required_inputs=["artifacts/design/tasks.md"],
        outputs=["artifacts/prompts/task-001.md"],
        main_impl=lambda: None,
    )

    (tmp_path / "artifacts" / "design").mkdir(parents=True)
    (tmp_path / "artifacts" / "design" / "tasks.md").write_text("# tasks\n", encoding="utf-8")

    monkeypatch.setattr(main_mod.sys, "argv", ["main.py", "--phase", "prompt"])
    main_mod.main()

    updated = CompanyState.load(tmp_path / "state" / "company_state.json")
    assert updated.current_phase == "prompt"
    assert updated.next_action == "start-release"
