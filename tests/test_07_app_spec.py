"""TC-07: AppSpec 生成と検証テスト"""
import sys
import pytest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts" / "tools"))
from create_app_template import generate, ADSENSE_PUB_ID, ADSENSE_SCRIPT
from spec_validator import validate_spec


def test_tc_07_01_spec_generated(tmp_path, monkeypatch):
    """TC-07-01: create-app-template.py でアプリを生成すると spec.md が生成される"""
    monkeypatch.chdir(tmp_path)
    app_dir = generate(app_id="app-001-sample", app_name="サンプルアプリ")

    spec = app_dir / "spec.md"
    assert spec.exists(), "spec.md が生成されていない"
    content = spec.read_text(encoding="utf-8")

    required_fields = [
        "app_id", "app_name", "runtime_mode", "visitor_tracking",
        "pages_path", "adsense_required",
    ]
    for field in required_fields:
        assert field in content, f"spec.md に必須フィールド不在: {field}"


def test_tc_07_02_adsense_required_default(tmp_path, monkeypatch):
    """TC-07-02: 生成された spec.md の adsense_required がデフォルト true"""
    monkeypatch.chdir(tmp_path)
    app_dir = generate(app_id="app-001-sample", app_name="サンプルアプリ")
    content = (app_dir / "spec.md").read_text(encoding="utf-8")
    assert "adsense_required: true" in content


def test_tc_07_03_adsense_required_false_needs_reason(tmp_path):
    """TC-07-03: adsense_required: false に adsense_exception_reason なしは検証エラー"""
    spec = tmp_path / "spec.md"
    spec.write_text(
        "app_id: app-001-sample\n"
        "app_name: テスト\n"
        "summary: テスト\n"
        "target_user: テスト\n"
        "runtime_mode: static\n"
        "visitor_tracking: true\n"
        "pages_path: /apps/app-001-sample/\n"
        "adsense_required: false\n"
        "adsense_applied: false\n",
        encoding="utf-8",
    )
    errors = validate_spec(spec)
    assert any("adsense_exception_reason" in e for e in errors)


def test_tc_07_03_adsense_required_false_with_reason_ok(tmp_path):
    """TC-07-03: adsense_required: false + exception_reason があれば検証 OK"""
    spec = tmp_path / "spec.md"
    spec.write_text(
        "app_id: app-001-sample\n"
        "app_name: テスト\n"
        "summary: テスト\n"
        "target_user: テスト\n"
        "runtime_mode: static\n"
        "visitor_tracking: true\n"
        "pages_path: /apps/app-001-sample/\n"
        "adsense_required: false\n"
        "adsense_exception_reason: 内部ツールのため広告対象外\n"
        "adsense_applied: false\n",
        encoding="utf-8",
    )
    errors = validate_spec(spec)
    assert not any("adsense_exception_reason" in e for e in errors)


def test_tc_07_04_visitor_tracking_false_needs_reason(tmp_path):
    """TC-07-04: visitor_tracking: false に visitor_tracking_reason なしは検証エラー"""
    spec = tmp_path / "spec.md"
    spec.write_text(
        "app_id: app-001-sample\n"
        "app_name: テスト\n"
        "summary: テスト\n"
        "target_user: テスト\n"
        "runtime_mode: static\n"
        "visitor_tracking: false\n"
        "pages_path: /apps/app-001-sample/\n"
        "adsense_required: true\n"
        "adsense_applied: false\n",
        encoding="utf-8",
    )
    errors = validate_spec(spec)
    assert any("visitor_tracking_reason" in e for e in errors)
