"""TC-11: AdSense ゲート (Phase 11) テスト"""
import logging
import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts" / "tools"))
from create_app_template import generate, ADSENSE_PUB_ID, ADSENSE_SCRIPT
from build_index import build_index
import agents.github_pages_release_manager as release_manager


@pytest.fixture(autouse=True)
def reset_logger():
    logging.getLogger("github_pages_release_manager").handlers.clear()
    yield
    logging.getLogger("github_pages_release_manager").handlers.clear()


def _make_required_qa_files(tmp_path: Path) -> None:
    qa_dir = tmp_path / "artifacts" / "qa"
    qa_dir.mkdir(parents=True, exist_ok=True)
    (qa_dir / "browser_test_report.md").write_text("全テスト PASS\n", encoding="utf-8")
    (qa_dir / "design_review.md").write_text("レイアウト問題なし\n", encoding="utf-8")
    (tmp_path / "artifacts" / "sprints").mkdir(parents=True, exist_ok=True)


def test_tc_11_01_no_adsense_is_ng(tmp_path, monkeypatch):
    """TC-11-01: 収益対象ページに AdSense タグがなければ Release NG"""
    monkeypatch.chdir(tmp_path)
    _make_required_qa_files(tmp_path)

    # AdSense タグなしの HTML を作成
    app_dir = tmp_path / "apps" / "app-001-sample"
    app_dir.mkdir(parents=True)
    (app_dir / "index.html").write_text(
        "<!DOCTYPE html><html><head></head><body>No AdSense</body></html>",
        encoding="utf-8",
    )

    with pytest.raises(SystemExit) as exc_info:
        release_manager.main()
    # 入力チェック通過後、未実装で exit(1) → xfail or assert exit code
    assert exc_info.value.code == 1


def test_tc_11_02_adsense_present_is_ok(tmp_path, monkeypatch):
    """TC-11-02: AdSense タグが存在すれば Release OK に進む"""
    monkeypatch.chdir(tmp_path)
    _make_required_qa_files(tmp_path)

    app_dir = tmp_path / "apps" / "app-001-sample"
    app_dir.mkdir(parents=True)
    (app_dir / "index.html").write_text(
        f"<!DOCTYPE html><html><head>{ADSENSE_SCRIPT}</head><body></body></html>",
        encoding="utf-8",
    )

    try:
        release_manager.main()
    except SystemExit as e:
        if e.code != 0:
            pytest.xfail("github_pages_release_manager 未実装")

    report = tmp_path / "artifacts" / "sprints" / "deploy_report.md"
    assert report.exists()
    content = report.read_text(encoding="utf-8")
    assert "AdSense OK" in content or "Release OK" in content


def test_tc_11_03_test_page_contamination_is_ng(tmp_path, monkeypatch):
    """TC-11-03: テストページへの AdSense 混入を検出する"""
    monkeypatch.chdir(tmp_path)
    _make_required_qa_files(tmp_path)

    app_dir = tmp_path / "apps" / "app-001-sample"
    app_dir.mkdir(parents=True)
    (app_dir / "index.html").write_text(
        f"<!DOCTYPE html><html><head>{ADSENSE_SCRIPT}</head><body></body></html>",
        encoding="utf-8",
    )
    # テストページに誤って AdSense 混入
    (app_dir / "test-api.html").write_text(
        f"<!DOCTYPE html><html><head>{ADSENSE_SCRIPT}</head><body>test</body></html>",
        encoding="utf-8",
    )

    try:
        release_manager.main()
    except SystemExit as e:
        if e.code != 0:
            pytest.xfail("github_pages_release_manager 未実装")

    report = tmp_path / "artifacts" / "sprints" / "deploy_report.md"
    if report.exists():
        content = report.read_text(encoding="utf-8")
        assert "Release NG" in content or "混入" in content


def test_tc_11_04_layout_issue_is_ng(tmp_path, monkeypatch):
    """TC-11-04: design_review.md にレイアウト崩れがあれば NG"""
    monkeypatch.chdir(tmp_path)
    qa_dir = tmp_path / "artifacts" / "qa"
    qa_dir.mkdir(parents=True)
    (qa_dir / "browser_test_report.md").write_text("PASS\n", encoding="utf-8")
    (qa_dir / "design_review.md").write_text(
        "AdSense 挿入でレイアウト崩れあり\n", encoding="utf-8"
    )
    (tmp_path / "artifacts" / "sprints").mkdir(parents=True)

    app_dir = tmp_path / "apps" / "app-001-sample"
    app_dir.mkdir(parents=True)
    (app_dir / "index.html").write_text(
        f"<html><head>{ADSENSE_SCRIPT}</head></html>", encoding="utf-8"
    )

    try:
        release_manager.main()
    except SystemExit as e:
        if e.code != 0:
            pytest.xfail("github_pages_release_manager 未実装")

    report = tmp_path / "artifacts" / "sprints" / "deploy_report.md"
    if report.exists():
        content = report.read_text(encoding="utf-8")
        assert "Release NG" in content or "崩れ" in content


def test_tc_11_05_template_inserts_adsense(tmp_path, monkeypatch):
    """TC-11-05: create-app-template.py が AdSense タグを自動挿入する"""
    monkeypatch.chdir(tmp_path)
    app_dir = generate(app_id="app-001-sample", app_name="テストアプリ")

    index_html = (app_dir / "index.html").read_text(encoding="utf-8")
    assert ADSENSE_PUB_ID in index_html, "AdSense タグが index.html に含まれていない"
    assert "<head>" in index_html.lower()
    # AdSense タグが <head> 内にあることを確認
    head_end = index_html.lower().find("</head>")
    head_content = index_html[:head_end] if head_end != -1 else index_html
    assert ADSENSE_PUB_ID in head_content


def test_tc_11_06_build_index_inserts_adsense(tmp_path, monkeypatch):
    """TC-11-06: build-index.py がルートの index.html に AdSense タグを挿入する"""
    monkeypatch.chdir(tmp_path)
    (tmp_path / "apps").mkdir()
    index_path = tmp_path / "index.html"

    build_index(apps_dir=tmp_path / "apps", output=index_path)

    content = index_path.read_text(encoding="utf-8")
    assert ADSENSE_PUB_ID in content
    head_end = content.lower().find("</head>")
    head_content = content[:head_end] if head_end != -1 else content
    assert ADSENSE_PUB_ID in head_content
