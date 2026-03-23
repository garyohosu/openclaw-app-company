"""TC-01: run_phase() ヘルパーのテスト"""
import sys
import pytest
from main import run_phase


def test_tc_01_01_return_true():
    """TC-01-01: fn が正常に return すると True が返る"""
    assert run_phase("dummy", lambda: None) is True


def test_tc_01_02_system_exit_0():
    """TC-01-02: fn が SystemExit(0) を raise すると True が返る"""
    def fn():
        raise SystemExit(0)

    assert run_phase("dummy", fn) is True


def test_tc_01_03_system_exit_1():
    """TC-01-03: fn が SystemExit(1) を raise すると False が返る"""
    def fn():
        raise SystemExit(1)

    assert run_phase("dummy", fn) is False


def test_tc_01_04_exception():
    """TC-01-04: fn が未捕捉例外を raise すると False が返る（伝播しない）"""
    def fn():
        raise RuntimeError("unexpected")

    assert run_phase("dummy", fn) is False


def test_tc_01_05_failure_stops_pipeline():
    """TC-01-05: Phase A が失敗したら後続 B・C は実行されない"""
    calls = []

    def phase_a():
        calls.append("a")
        raise SystemExit(1)

    def phase_b():
        calls.append("b")

    def phase_c():
        calls.append("c")

    def pipeline():
        if not run_phase("a", phase_a):
            sys.exit(1)
        run_phase("b", phase_b)
        run_phase("c", phase_c)

    with pytest.raises(SystemExit) as exc_info:
        pipeline()

    assert exc_info.value.code == 1
    assert calls == ["a"]
