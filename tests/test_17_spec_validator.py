"""TC-17: spec_validator の抽出ロジックテスト"""
from pathlib import Path
import sys

from pathlib import Path as _Path
sys.path.insert(0, str(_Path(__file__).parent.parent / "scripts" / "tools"))
from spec_validator import validate_spec


def _write_spec(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def _base_spec_body() -> str:
    return (
        "app_id: app-001-sample\n"
        "app_name: サンプル\n"
        "summary: テスト\n"
        "target_user: テスト\n"
        "runtime_mode: static\n"
        "visitor_tracking: true\n"
        "pages_path: /apps/app-001-sample/\n"
        "adsense_required: true\n"
        "adsense_applied: false\n"
    )


def test_tc_17_01_leading_whitespace_ok(tmp_path):
    """TC-17-01: 行頭空白ありの項目を読める"""
    spec = tmp_path / "spec.md"
    content = (
        "  app_id: app-001-sample\n"
        "  app_name: サンプル\n"
        "  summary: テスト\n"
        "  target_user: テスト\n"
        "  runtime_mode: static\n"
        "  visitor_tracking: true\n"
        "  pages_path: /apps/app-001-sample/\n"
        "  adsense_required: true\n"
        "  adsense_applied: false\n"
    )
    _write_spec(spec, content)
    errors = validate_spec(spec)
    assert errors == []


def test_tc_17_02_code_block_ignored(tmp_path):
    """TC-17-02: コードブロック内の擬似項目は無視する"""
    spec = tmp_path / "spec.md"
    content = (
        "```\n"
        "app_id: fake\n"
        "app_name: fake\n"
        "summary: fake\n"
        "target_user: fake\n"
        "runtime_mode: static\n"
        "visitor_tracking: true\n"
        "pages_path: /apps/fake/\n"
        "adsense_required: true\n"
        "adsense_applied: false\n"
        "```\n"
    )
    _write_spec(spec, content)
    errors = validate_spec(spec)
    assert any("app_id" in e for e in errors)


def test_tc_17_03_normal_markdown_ok(tmp_path):
    """TC-17-03: 通常の markdown 項目を正しく抽出できる"""
    spec = tmp_path / "spec.md"
    _write_spec(spec, _base_spec_body())
    errors = validate_spec(spec)
    assert errors == []
