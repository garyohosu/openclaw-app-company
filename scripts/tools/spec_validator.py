"""
scripts/tools/spec_validator.py
apps/app-xxx/spec.md の必須フィールド検証
"""
from __future__ import annotations

import re
import sys
from pathlib import Path


def _extract_field(content: str, field: str) -> str | None:
    """Markdown 内の `field: value` パターンを抽出する"""
    pattern = rf"^{re.escape(field)}:\s*(.+)$"
    match = re.search(pattern, content, re.MULTILINE)
    return match.group(1).strip() if match else None


def validate_spec(spec_path: Path) -> list[str]:
    """
    spec.md を検証し、エラーメッセージのリストを返す。
    エラーなし = 空リスト。
    """
    errors: list[str] = []
    content = spec_path.read_text(encoding="utf-8")

    required_fields = [
        "app_id", "app_name", "summary", "target_user",
        "runtime_mode", "visitor_tracking", "pages_path",
        "adsense_required", "adsense_applied",
    ]
    for field in required_fields:
        if _extract_field(content, field) is None:
            errors.append(f"必須フィールド不在: {field}")

    # adsense_required: false の場合は adsense_exception_reason 必須
    adsense_required = _extract_field(content, "adsense_required")
    if adsense_required is not None and adsense_required.lower() == "false":
        if _extract_field(content, "adsense_exception_reason") is None:
            errors.append(
                "adsense_required: false の場合は adsense_exception_reason が必須"
            )

    # visitor_tracking: false の場合は visitor_tracking_reason 必須
    visitor_tracking = _extract_field(content, "visitor_tracking")
    if visitor_tracking is not None and visitor_tracking.lower() == "false":
        if _extract_field(content, "visitor_tracking_reason") is None:
            errors.append(
                "visitor_tracking: false の場合は visitor_tracking_reason が必須"
            )

    return errors


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: spec_validator.py <spec.md path>", file=sys.stderr)
        raise SystemExit(1)

    spec_path = Path(sys.argv[1])
    if not spec_path.exists():
        print(f"Not found: {spec_path}", file=sys.stderr)
        raise SystemExit(1)

    errors = validate_spec(spec_path)
    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        raise SystemExit(1)

    print("OK: spec.md validation passed")


if __name__ == "__main__":
    main()
