"""TC-15: アプリの Pages 公開品質テスト"""
import sys
import pytest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts" / "tools"))
from create_app_template import generate


def test_tc_15_01_relative_paths_work(tmp_path, monkeypatch):
    """TC-15-01: CSS・JS・画像が相対パスで参照されている（絶対URLなし）"""
    monkeypatch.chdir(tmp_path)
    app_dir = generate(app_id="app-001-sample", app_name="テストアプリ")

    index_html = (app_dir / "index.html").read_text(encoding="utf-8")

    # src/href に絶対URLが使われていないことを確認
    import re
    absolute_refs = re.findall(
        r'(?:src|href)=["\']https?://[^"\']*(?:\.css|\.js|\.png|\.jpg)["\']',
        index_html,
    )
    assert absolute_refs == [], f"絶対URLの参照が含まれる: {absolute_refs}"


def test_tc_15_02_no_404_on_sub_path(tmp_path, monkeypatch):
    """TC-15-02: サブパス対応 — pages_path が spec.md に記載されている"""
    monkeypatch.chdir(tmp_path)
    app_dir = generate(app_id="app-001-sample", app_name="テストアプリ")

    spec = (app_dir / "spec.md").read_text(encoding="utf-8")
    assert "pages_path:" in spec


def test_tc_15_03_mobile_viewport(tmp_path, monkeypatch):
    """TC-15-03: モバイル幅対応 — viewport meta タグが存在する"""
    monkeypatch.chdir(tmp_path)
    app_dir = generate(app_id="app-001-sample", app_name="テストアプリ")

    index_html = (app_dir / "index.html").read_text(encoding="utf-8")
    assert "viewport" in index_html
    assert "width=device-width" in index_html


def test_tc_15_04_nojekyll_exists(tmp_path, monkeypatch):
    """TC-15-04: リポジトリルートに .nojekyll が存在する"""
    # プロジェクトルートの .nojekyll を確認
    repo_root = Path(__file__).parent.parent
    nojekyll = repo_root / ".nojekyll"
    if not nojekyll.exists():
        pytest.fail(
            ".nojekyll が存在しない。"
            "GitHub Pages で Jekyll 処理をスキップするために必要。"
        )


@pytest.mark.e2e
def test_tc_15_01_pages_url_from_deploy_report():
    """TC-15-01 [E2E]: deploy_report.md の public_url で 200 が返る"""
    deploy_report = Path("artifacts/sprints/deploy_report.md")
    if not deploy_report.exists():
        pytest.skip("deploy_report.md が存在しない（未公開）")

    import re
    content = deploy_report.read_text(encoding="utf-8")
    url_match = re.search(r"public_url:\s*(https?://[^\s]+)", content)
    if not url_match:
        pytest.skip("deploy_report.md に public_url が記載されていない")

    import urllib.request
    url = url_match.group(1)
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            assert resp.status == 200
    except Exception as e:
        pytest.fail(f"public_url へのアクセス失敗: {e}")
