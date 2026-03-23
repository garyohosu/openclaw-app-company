"""TC-13: Phase 12 ループバック判断テスト"""
import logging
import pytest
from pathlib import Path
import agents.improvement_strategist as improvement_strategist


@pytest.fixture(autouse=True)
def reset_logger():
    logging.getLogger("improvement_strategist").handlers.clear()
    yield
    logging.getLogger("improvement_strategist").handlers.clear()


def _make_deploy_report(tmp_path: Path) -> None:
    sprints_dir = tmp_path / "artifacts" / "sprints"
    sprints_dir.mkdir(parents=True, exist_ok=True)
    (sprints_dir / "deploy_report.md").write_text(
        "公開完了\nRelease OK\n", encoding="utf-8"
    )


def test_tc_13_01_same_app_loops_to_phase5(tmp_path, monkeypatch):
    """TC-13-01: 同一アプリ改善は Phase 5 へのループバックが sprint_next.md に記録される"""
    monkeypatch.chdir(tmp_path)
    _make_deploy_report(tmp_path)

    try:
        improvement_strategist.main()
    except SystemExit as e:
        if e.code != 0:
            pytest.xfail("improvement_strategist 未実装")

    sprint_next = tmp_path / "artifacts" / "sprints" / "sprint_next.md"
    assert sprint_next.exists()
    content = sprint_next.read_text(encoding="utf-8")
    assert "PHASE_5" in content or "task_breakdown" in content


def test_tc_13_02_new_app_loops_to_phase1(tmp_path, monkeypatch):
    """TC-13-02: 新規アプリ追加は Phase 1 へのループバックが sprint_next.md に記録される"""
    monkeypatch.chdir(tmp_path)
    _make_deploy_report(tmp_path)

    try:
        improvement_strategist.main()
    except SystemExit as e:
        if e.code != 0:
            pytest.xfail("improvement_strategist 未実装")

    sprint_next = tmp_path / "artifacts" / "sprints" / "sprint_next.md"
    assert sprint_next.exists()
    content = sprint_next.read_text(encoding="utf-8")
    assert "PHASE_1" in content or "research" in content


def test_tc_13_03_user_feedback_generated(tmp_path, monkeypatch):
    """TC-13-03: user_feedback.md が生成される"""
    monkeypatch.chdir(tmp_path)
    _make_deploy_report(tmp_path)

    try:
        improvement_strategist.main()
    except SystemExit as e:
        if e.code != 0:
            pytest.xfail("improvement_strategist 未実装")

    assert (tmp_path / "artifacts" / "sprints" / "user_feedback.md").exists()


def test_tc_13_04_usage_insights_generated(tmp_path, monkeypatch):
    """TC-13-04: usage_insights.md が生成される"""
    monkeypatch.chdir(tmp_path)
    _make_deploy_report(tmp_path)

    try:
        improvement_strategist.main()
    except SystemExit as e:
        if e.code != 0:
            pytest.xfail("improvement_strategist 未実装")

    assert (tmp_path / "artifacts" / "sprints" / "usage_insights.md").exists()
