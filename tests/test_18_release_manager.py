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


def _write_stub(path: Path) -> None:
    path.write_text("# stub\n\nsummary: placeholder\n", encoding="utf-8")


def test_tc_18_03_stub_generates_provisional(tmp_path, monkeypatch):
    """TC-18-03: stub 入力は Release Provisional を出力して exit(0)"""
    monkeypatch.chdir(tmp_path)
    qa_dir = tmp_path / "artifacts" / "qa"
    qa_dir.mkdir(parents=True)
    _write_stub(qa_dir / "browser_test_report.md")
    _write_stub(qa_dir / "design_review.md")

    with pytest.raises(SystemExit) as exc_info:
        release_manager.main()
    assert exc_info.value.code == 0

    report = tmp_path / "artifacts" / "sprints" / "deploy_report.md"
    assert report.exists()
    content = report.read_text(encoding="utf-8")
    assert "Release Provisional" in content
    assert "release_readiness: provisional" in content
    assert "publish_blocked_reason:" in content
    assert "stub" in content


def test_tc_18_04_partial_stub_is_provisional(tmp_path, monkeypatch):
    """TC-18-04: browser stub + design OK → provisional (公開ブロック)"""
    monkeypatch.chdir(tmp_path)
    qa_dir = tmp_path / "artifacts" / "qa"
    qa_dir.mkdir(parents=True)
    _write_stub(qa_dir / "browser_test_report.md")
    _write_report(qa_dir / "design_review.md", ok=True)

    with pytest.raises(SystemExit) as exc_info:
        release_manager.main()
    assert exc_info.value.code == 0

    content = (tmp_path / "artifacts" / "sprints" / "deploy_report.md").read_text(encoding="utf-8")
    assert "Release Provisional" in content
    assert "browser_test_report" in content  # ブロック理由に含まれる


def test_tc_18_05_ng_overrides_stub(tmp_path, monkeypatch):
    """TC-18-05: NG は stub より優先して exit(1)"""
    monkeypatch.chdir(tmp_path)
    qa_dir = tmp_path / "artifacts" / "qa"
    qa_dir.mkdir(parents=True)
    _write_report(qa_dir / "browser_test_report.md", ok=False)  # NG
    _write_stub(qa_dir / "design_review.md")                     # stub

    with pytest.raises(SystemExit) as exc_info:
        release_manager.main()
    assert exc_info.value.code == 1


def test_tc_18_06_ok_report_has_readiness_ready(tmp_path, monkeypatch):
    """TC-18-06: 両方 OK なら release_readiness: ready が記録される"""
    monkeypatch.chdir(tmp_path)
    qa_dir = tmp_path / "artifacts" / "qa"
    qa_dir.mkdir(parents=True)
    _write_report(qa_dir / "browser_test_report.md", ok=True)
    _write_report(qa_dir / "design_review.md", ok=True)

    with pytest.raises(SystemExit) as exc_info:
        release_manager.main()
    assert exc_info.value.code == 0

    content = (tmp_path / "artifacts" / "sprints" / "deploy_report.md").read_text(encoding="utf-8")
    assert "release_readiness: ready" in content
    assert "publish_blocked_reason: -" in content
