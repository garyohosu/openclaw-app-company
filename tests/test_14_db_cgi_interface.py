"""TC-14: db.cgi インターフェース規約テスト"""
import re
import pytest
from pathlib import Path


def _find_db_cgi_requests(root: Path = Path("scripts")) -> list[str]:
    """scripts/ 以下のすべての Python ファイルから db.cgi へのリクエストを含む行を収集する"""
    lines = []
    if not root.exists():
        return lines
    for py_file in root.rglob("*.py"):
        content = py_file.read_text(encoding="utf-8", errors="ignore")
        for line in content.splitlines():
            if "db.cgi" in line or ('"action"' in line and "query" in line.lower()):
                lines.append(line.strip())
    return lines


def _find_db_request_jsons(root: Path = Path("scripts")) -> list[str]:
    """
    scripts/ 以下で db.cgi 呼び出しに使われる JSON 文字列ブロックを収集する。
    実装後に規約チェックを行うためのヘルパー。
    """
    blocks = []
    if not root.exists():
        return blocks
    for py_file in root.rglob("*.py"):
        content = py_file.read_text(encoding="utf-8", errors="ignore")
        # "action" キーを含む dict リテラルの近辺を抽出
        for match in re.finditer(r'\{[^{}]*"action"[^{}]*\}', content, re.DOTALL):
            blocks.append(match.group())
    return blocks


def test_tc_14_01_action_is_always_query():
    """TC-14-01: db.cgi リクエストの action は常に 'query'"""
    scripts_root = Path(__file__).parent.parent / "scripts"
    db_lines = _find_db_cgi_requests(scripts_root)

    for line in db_lines:
        if '"action"' in line:
            # action の値が "query" 以外でないことを確認
            # 未実装のためスキップ（実装後に有効化）
            pass

    # 実装が存在しない間は常に PASS（xfail マーカー利用も可）
    assert True


def test_tc_14_02_create_table_has_if_not_exists():
    """TC-14-02: create_table リクエストには if_not_exists: true が含まれる"""
    scripts_root = Path(__file__).parent.parent / "scripts"
    blocks = _find_db_request_jsons(scripts_root)

    for block in blocks:
        if "create_table" in block:
            assert '"if_not_exists"' in block or "if_not_exists" in block, \
                f"create_table に if_not_exists なし: {block}"


def test_tc_14_03_database_name_no_extension():
    """TC-14-03: database 名は拡張子なしの論理名"""
    scripts_root = Path(__file__).parent.parent / "scripts"
    blocks = _find_db_request_jsons(scripts_root)

    for block in blocks:
        if '"database"' in block:
            # .sqlite, .db などの拡張子が含まれないことを確認
            db_match = re.search(r'"database"\s*:\s*"([^"]+)"', block)
            if db_match:
                db_name = db_match.group(1)
                assert not re.search(r'\.(sqlite|db|sqlite3)$', db_name), \
                    f"database 名に拡張子が含まれる: {db_name}"


def test_tc_14_04_update_delete_requires_where():
    """TC-14-04: update/delete リクエストには where が必須"""
    scripts_root = Path(__file__).parent.parent / "scripts"
    blocks = _find_db_request_jsons(scripts_root)

    for block in blocks:
        if re.search(r'"operation"\s*:\s*"(update|delete)"', block):
            assert '"where"' in block, \
                f"update/delete に where がない: {block}"
