"""TC-10: QualityGate 更新テスト"""
import json
import pytest
import logging
from pathlib import Path
from state.company_state import CompanyState, QualityGate
from main import update_state_after_phase


@pytest.fixture(autouse=True)
def reset_loggers():
    for name in ["sakura_api_coordinator", "browser_test_operator", "github_pages_release_manager"]:
        logging.getLogger(name).handlers.clear()
    yield


def test_tc_10_01_phase6_sets_ssl_cors(tmp_path):
    """TC-10-01: Phase 6 完了後に ssl_verified・cors_verified が True"""
    state = CompanyState()
    artifacts = tmp_path / "artifacts"
    design_dir = artifacts / "design"
    design_dir.mkdir(parents=True)
    (design_dir / "api_connectivity_report.md").write_text(
        "## API 疎通確認レポート\n\nvisitor.cgi: OK\nuuid.cgi: OK\n全件確認完了\n",
        encoding="utf-8",
    )

    update_state_after_phase(state, "api_connectivity", artifacts)

    assert state.quality_gate.ssl_verified is True
    assert state.quality_gate.cors_verified is True


def test_tc_10_01_phase6_ng_keeps_false(tmp_path):
    """TC-10-01: Phase 6 でNG があれば ssl_verified は False のまま"""
    state = CompanyState()
    artifacts = tmp_path / "artifacts"
    design_dir = artifacts / "design"
    design_dir.mkdir(parents=True)
    (design_dir / "api_connectivity_report.md").write_text(
        "## API 疎通確認レポート\n\nuuid.cgi: NG (5xx)\n",
        encoding="utf-8",
    )

    update_state_after_phase(state, "api_connectivity", artifacts)

    assert state.quality_gate.ssl_verified is False
    assert state.quality_gate.cors_verified is False


def test_tc_10_02_phase10_sets_browser_test(tmp_path):
    """TC-10-02: Phase 10 完了後に browser_test_passed が True"""
    state = CompanyState()
    artifacts = tmp_path / "artifacts"
    qa_dir = artifacts / "qa"
    qa_dir.mkdir(parents=True)
    (qa_dir / "browser_test_report.md").write_text(
        "## ブラウザテストレポート\n\n全テスト PASS\n",
        encoding="utf-8",
    )

    update_state_after_phase(state, "testing", artifacts)

    assert state.quality_gate.browser_test_passed is True


def test_tc_10_03_agents_do_not_write_state(tmp_path, monkeypatch):
    """TC-10-03: エージェントは company_state.json を直接書き換えない"""
    import importlib
    monkeypatch.chdir(tmp_path)

    state_dir = tmp_path / "state"
    state_dir.mkdir()
    state_path = state_dir / "company_state.json"
    state = CompanyState(current_phase="research")
    state.save(state_path)

    original_mtime = state_path.stat().st_mtime

    # 任意エージェント（market_researcher）の main() を実行
    import agents.market_researcher as mr
    logging.getLogger("market_researcher").handlers.clear()
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "roadmap.md").write_text("# Roadmap\n", encoding="utf-8")

    try:
        mr.main()
    except SystemExit:
        pass

    # state ファイルが変更されていないことを確認
    assert state_path.stat().st_mtime == original_mtime, \
        "エージェントが company_state.json を直接書き換えた"


def test_tc_10_04_phase11_ok_updates_state(tmp_path):
    """TC-10-04: Phase 11 OK 判定を OpenClaw が state に反映する"""
    state = CompanyState()
    artifacts = tmp_path / "artifacts"
    sprints_dir = artifacts / "sprints"
    sprints_dir.mkdir(parents=True)
    (sprints_dir / "deploy_report.md").write_text(
        "## デプロイレポート\n\nAdSense OK\n混入なし\nRelease OK\n",
        encoding="utf-8",
    )

    update_state_after_phase(state, "release", artifacts)

    assert state.quality_gate.adsense_verified is True
    assert state.quality_gate.test_pages_adsense_clean is True
    assert state.quality_gate.release_gate_passed is True


def test_tc_10_05_phase11_ng_keeps_false(tmp_path):
    """TC-10-05: Phase 11 NG 判定を OpenClaw が state に反映する"""
    state = CompanyState()
    state.quality_gate.release_gate_passed = False

    artifacts = tmp_path / "artifacts"
    sprints_dir = artifacts / "sprints"
    sprints_dir.mkdir(parents=True)
    (sprints_dir / "deploy_report.md").write_text(
        "## デプロイレポート\n\nAdSense タグ不在\nRelease NG\n",
        encoding="utf-8",
    )

    update_state_after_phase(state, "release", artifacts)

    assert state.quality_gate.release_gate_passed is False
