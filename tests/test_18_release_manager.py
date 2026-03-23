"""TC-18: Release Manager 最小実装テスト"""
from pathlib import Path
import logging

import pytest

import agents.github_pages_release_manager as release_manager


@pytest.fixture(autouse=True)
def reset_logger():
    logging.getLogger("github_pages_release_manager").handlers.clear()
    yield
    logging.getLogger("github_pages_release_manager").handlers.clear()


def _write_report(path: Path, ok: bool) -> None:
    content = "Result: OK\n" if ok else "Result: NG\n"
    path.write_text(content, encoding="utf-8")


def test_tc_18_01_ok_generates_deploy_report(tmp_path, monkeypatch):
    """TC-18-01: 両方 OK なら deploy_report.md が生成される"""
    monkeypatch.chdir(tmp_path)
    qa_dir = tmp_path / "artifacts" / "qa"
    qa_dir.mkdir(parents=True)
    _write_report(qa_dir / "browser_test_report.md", ok=True)
    _write_report(qa_dir / "design_review.md", ok=True)

    try:
        release_manager.main()
    except SystemExit as e:
        assert e.code == 0

    report = tmp_path / "artifacts" / "sprints" / "deploy_report.md"
    assert report.exists()
    content = report.read_text(encoding="utf-8")
    assert "Release OK" in content
    assert "browser_test_report: OK" in content
    assert "design_review: OK" in content


def test_tc_18_02_ng_exits_1(tmp_path, monkeypatch):
    """TC-18-02: どちらか NG なら SystemExit(1)"""
    monkeypatch.chdir(tmp_path)
    qa_dir = tmp_path / "artifacts" / "qa"
    qa_dir.mkdir(parents=True)
    _write_report(qa_dir / "browser_test_report.md", ok=False)
    _write_report(qa_dir / "design_review.md", ok=True)

    with pytest.raises(SystemExit) as exc_info:
        release_manager.main()
    assert exc_info.value.code == 1
