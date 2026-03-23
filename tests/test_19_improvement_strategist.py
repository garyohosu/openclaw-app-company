"""TC-19: Improvement Strategist 最小実装テスト"""
from pathlib import Path
import logging

import pytest

import agents.improvement_strategist as improvement_strategist


@pytest.fixture(autouse=True)
def reset_logger():
    logging.getLogger("improvement_strategist").handlers.clear()
    yield
    logging.getLogger("improvement_strategist").handlers.clear()


def _write_deploy_report(path: Path, ok: bool) -> None:
    content = "Release OK\n" if ok else "Release NG\n"
    path.write_text(content, encoding="utf-8")


def test_tc_19_01_ok_generates_outputs(tmp_path, monkeypatch):
    """TC-19-01: Release OK なら3成果物が生成される"""
    monkeypatch.chdir(tmp_path)
    sprints = tmp_path / "artifacts" / "sprints"
    sprints.mkdir(parents=True)
    _write_deploy_report(sprints / "deploy_report.md", ok=True)

    try:
        improvement_strategist.main()
    except SystemExit as e:
        assert e.code == 0

    assert (sprints / "sprint_next.md").exists()
    assert (sprints / "usage_insights.md").exists()
    assert (sprints / "user_feedback.md").exists()


def test_tc_19_02_ng_exits_1(tmp_path, monkeypatch):
    """TC-19-02: Release NG なら SystemExit(1)"""
    monkeypatch.chdir(tmp_path)
    sprints = tmp_path / "artifacts" / "sprints"
    sprints.mkdir(parents=True)
    _write_deploy_report(sprints / "deploy_report.md", ok=False)

    with pytest.raises(SystemExit) as exc_info:
        improvement_strategist.main()
    assert exc_info.value.code == 1


def _write_provisional_report(path: Path, blocked_by: str = "browser_test_report, design_review") -> None:
    path.write_text(
        "# deploy_report.md\n\n"
        "release_result: Release Provisional\n"
        "release_readiness: provisional\n"
        f"publish_blocked_reason: QA stub 未完成: {blocked_by}\n",
        encoding="utf-8",
    )


def test_tc_19_03_provisional_exits_0(tmp_path, monkeypatch):
    """TC-19-03: Release Provisional なら exit(0) で qa_remediation モードになる"""
    monkeypatch.chdir(tmp_path)
    sprints = tmp_path / "artifacts" / "sprints"
    sprints.mkdir(parents=True)
    _write_provisional_report(sprints / "deploy_report.md")

    with pytest.raises(SystemExit) as exc_info:
        improvement_strategist.main()
    assert exc_info.value.code == 0

    content = (sprints / "sprint_next.md").read_text(encoding="utf-8")
    assert "improvement_mode: qa_remediation" in content


def test_tc_19_04_provisional_sprint_next_has_required_actions(tmp_path, monkeypatch):
    """TC-19-04: provisional の sprint_next.md に required_actions が含まれる"""
    monkeypatch.chdir(tmp_path)
    sprints = tmp_path / "artifacts" / "sprints"
    sprints.mkdir(parents=True)
    _write_provisional_report(sprints / "deploy_report.md")

    with pytest.raises(SystemExit):
        improvement_strategist.main()

    content = (sprints / "sprint_next.md").read_text(encoding="utf-8")
    assert "required_actions:" in content
    assert "browser_test_report.md" in content
    assert "design_review.md" in content


def test_tc_19_05_provisional_sprint_next_has_remediation_action(tmp_path, monkeypatch):
    """TC-19-05: provisional の sprint_next.md に start-qa-remediation が含まれる"""
    monkeypatch.chdir(tmp_path)
    sprints = tmp_path / "artifacts" / "sprints"
    sprints.mkdir(parents=True)
    _write_provisional_report(sprints / "deploy_report.md")

    with pytest.raises(SystemExit):
        improvement_strategist.main()

    content = (sprints / "sprint_next.md").read_text(encoding="utf-8")
    assert "start-qa-remediation" in content


def test_tc_19_06_provisional_outputs_all_three_files(tmp_path, monkeypatch):
    """TC-19-06: provisional でも 3成果物すべて生成される"""
    monkeypatch.chdir(tmp_path)
    sprints = tmp_path / "artifacts" / "sprints"
    sprints.mkdir(parents=True)
    _write_provisional_report(sprints / "deploy_report.md")

    with pytest.raises(SystemExit) as exc_info:
        improvement_strategist.main()
    assert exc_info.value.code == 0

    assert (sprints / "sprint_next.md").exists()
    assert (sprints / "usage_insights.md").exists()
    assert (sprints / "user_feedback.md").exists()


def test_tc_19_07_provisional_blocked_by_in_output(tmp_path, monkeypatch):
    """TC-19-07: publish_blocked_reason が sprint_next.md の blocked_by に反映される"""
    monkeypatch.chdir(tmp_path)
    sprints = tmp_path / "artifacts" / "sprints"
    sprints.mkdir(parents=True)
    _write_provisional_report(sprints / "deploy_report.md", blocked_by="browser_test_report")

    with pytest.raises(SystemExit):
        improvement_strategist.main()

    content = (sprints / "sprint_next.md").read_text(encoding="utf-8")
    assert "browser_test_report" in content
