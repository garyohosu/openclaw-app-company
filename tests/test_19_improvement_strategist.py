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
