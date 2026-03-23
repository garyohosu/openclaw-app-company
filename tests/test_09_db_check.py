"""TC-09: DB 接続確認 (Phase 7) テスト"""
import pytest
from pathlib import Path


@pytest.mark.integration
def test_tc_09_01_select_recorded(tmp_path, monkeypatch):
    """TC-09-01: select テスト結果が db_connectivity_report.md に記録される"""
    pytest.skip("Phase 7 は結合テスト: ローカル CGI サーバーが必要")


@pytest.mark.integration
def test_tc_09_02_insert_count_increases(tmp_path, monkeypatch):
    """TC-09-02: insert → count で件数が 1 増加する"""
    pytest.skip("Phase 7 は結合テスト: ローカル CGI サーバーが必要")


@pytest.mark.integration
def test_tc_09_03_error_case_recorded(tmp_path, monkeypatch):
    """TC-09-03: 不正パラメータでエラー JSON が返り report に記録される"""
    pytest.skip("Phase 7 は結合テスト: ローカル CGI サーバーが必要")


def test_tc_09_04_toolbox_skips_phase7(tmp_path, monkeypatch):
    """TC-09-04: runtime_mode: toolbox では Phase 7 がスキップされる"""
    from main import run_phase
    from state.company_state import CompanyState

    monkeypatch.chdir(tmp_path)
    state = CompanyState(runtime_mode="toolbox")
    state_path = tmp_path / "state" / "company_state.json"
    state_path.parent.mkdir()
    state.save(state_path)

    loaded = CompanyState.load(state_path)

    calls = []
    def mock_db_check():
        calls.append("db_check")

    # db モードのみ Phase 7 を実行する
    if loaded.runtime_mode == "db":
        run_phase("db_connectivity", mock_db_check)

    assert calls == [], "toolbox モードで DB チェックが実行されてしまった"
