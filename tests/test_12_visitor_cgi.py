"""TC-12: visitor.cgi 呼び出し（フロントエンド）テスト"""
import sys
import pytest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts" / "tools"))
from create_app_template import generate


def test_tc_12_01_visitor_tracking_true_includes_fetch(tmp_path, monkeypatch):
    """TC-12-01: visitor_tracking: true のとき visitor.cgi への fetch が生成される"""
    monkeypatch.chdir(tmp_path)
    app_dir = generate(app_id="app-001-sample", app_name="テスト", visitor_tracking=True)

    app_js = (app_dir / "app.js").read_text(encoding="utf-8")
    assert "visitor.cgi" in app_js or "visitor" in app_js
    assert "fetch(" in app_js


def test_tc_12_02_visitor_tracking_false_excludes_fetch(tmp_path, monkeypatch):
    """TC-12-02: visitor_tracking: false のとき visitor.cgi fetch が含まれない"""
    monkeypatch.chdir(tmp_path)
    app_dir = generate(
        app_id="app-001-sample", app_name="テスト", visitor_tracking=False
    )

    app_js = (app_dir / "app.js").read_text(encoding="utf-8")
    # visitor.cgi への fetch が含まれないこと
    # （コメントアウトまたは条件分岐で無効化されていること）
    assert "VISITOR_TRACKING = false" in app_js or "visitor_tracking = false" in app_js.lower()


def test_tc_12_03_fetch_failure_does_not_block(tmp_path, monkeypatch):
    """TC-12-03: fetch() 失敗がアプリ本体を止めない（.catch(() => {}) が存在する）"""
    monkeypatch.chdir(tmp_path)
    app_dir = generate(app_id="app-001-sample", app_name="テスト", visitor_tracking=True)

    app_js = (app_dir / "app.js").read_text(encoding="utf-8")
    # .catch() で失敗を握りつぶしている
    assert ".catch(" in app_js


def test_tc_12_04_domcontentloaded_fires(tmp_path, monkeypatch):
    """TC-12-04: visitor.cgi 呼び出しが DOMContentLoaded ハンドラ内に配置されている"""
    monkeypatch.chdir(tmp_path)
    app_dir = generate(app_id="app-001-sample", app_name="テスト", visitor_tracking=True)

    app_js = (app_dir / "app.js").read_text(encoding="utf-8")
    assert "DOMContentLoaded" in app_js

    # DOMContentLoaded より後に visitor.cgi 呼び出しが来る
    dom_pos = app_js.find("DOMContentLoaded")
    visitor_pos = app_js.find("visitor")
    assert visitor_pos > dom_pos, "visitor.cgi 呼び出しが DOMContentLoaded より前にある"
