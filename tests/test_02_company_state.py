"""TC-02: CompanyState の読み書きテスト"""
import json
import pytest
from state.company_state import CompanyState, QualityGate


def test_tc_02_01_load(company_state_json):
    """TC-02-01: 正常な JSON から CompanyState を読み込める"""
    state = CompanyState.load(company_state_json)
    assert state.current_phase == "research"
    assert state.current_sprint == 1
    assert isinstance(state.quality_gate, QualityGate)


def test_tc_02_02_file_not_found(tmp_path):
    """TC-02-02: ファイル不在で FileNotFoundError が送出される"""
    with pytest.raises(FileNotFoundError):
        CompanyState.load(tmp_path / "nonexistent.json")


def test_tc_02_03_save_reload(company_state_json, tmp_path):
    """TC-02-03: 保存 → 再読み込みで全フィールドが一致する"""
    state = CompanyState.load(company_state_json)
    state.current_phase = "implementation"
    state.next_action = "fix-bug"
    state.quality_gate.ssl_verified = True

    out = tmp_path / "out.json"
    state.save(out)
    reloaded = CompanyState.load(out)

    assert reloaded.current_phase == "implementation"
    assert reloaded.next_action == "fix-bug"
    assert reloaded.quality_gate.ssl_verified is True
    assert reloaded.current_sprint == state.current_sprint


def test_tc_02_04_phase_failure_state(tmp_path):
    """TC-02-04: フェーズ失敗時に current_phase はそのまま、next_action に記録される"""
    state = CompanyState(current_phase="implementation")
    state.next_action = "Fix import error in codex output"

    p = tmp_path / "state.json"
    state.save(p)
    reloaded = CompanyState.load(p)

    assert reloaded.current_phase == "implementation"
    assert "Fix" in reloaded.next_action


def test_tc_02_05_quality_gate_defaults():
    """TC-02-05: 新規 QualityGate の全フラグが False"""
    gate = QualityGate()
    assert gate.pages_ready is False
    assert gate.ssl_verified is False
    assert gate.cors_verified is False
    assert gate.browser_test_passed is False
    assert gate.adsense_verified is False
    assert gate.test_pages_adsense_clean is False
    assert gate.release_gate_passed is False
