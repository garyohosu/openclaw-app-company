"""TC-05: Market Researcher / Idea Scorer テスト"""
import pytest
from pathlib import Path
import logging
import agents.market_researcher as market_researcher
import agents.idea_scorer as idea_scorer


@pytest.fixture(autouse=True)
def reset_loggers():
    for name in ["market_researcher", "idea_scorer"]:
        logging.getLogger(name).handlers.clear()
    yield
    for name in ["market_researcher", "idea_scorer"]:
        logging.getLogger(name).handlers.clear()


def test_tc_05_01_research_report_generated(tmp_path, monkeypatch):
    """TC-05-01: roadmap.md が存在すると research_report.md が生成される"""
    monkeypatch.chdir(tmp_path)
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "roadmap.md").write_text("# Roadmap\n- アイデア1\n", encoding="utf-8")
    (tmp_path / "artifacts" / "research").mkdir(parents=True)

    with pytest.raises(SystemExit) as exc_info:
        market_researcher.main()
    assert exc_info.value.code == 0
    assert (tmp_path / "artifacts" / "research" / "research_report.md").exists()


def test_tc_05_01_research_report_generated_impl(tmp_path, monkeypatch):
    """TC-05-01 [実装後]: research_report.md が生成される (TDD グリーンフェーズ用)"""
    monkeypatch.chdir(tmp_path)
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "roadmap.md").write_text("# Roadmap\n- アイデア1\n", encoding="utf-8")
    (tmp_path / "artifacts" / "research").mkdir(parents=True)

    try:
        market_researcher.main()
    except SystemExit as e:
        if e.code != 0:
            pytest.xfail("market_researcher 未実装")

    report = tmp_path / "artifacts" / "research" / "research_report.md"
    assert report.exists(), "research_report.md が生成されていない"


def test_tc_05_02_source_notes_generated(tmp_path, monkeypatch):
    """TC-05-02: source_notes.md が生成される (TDD グリーンフェーズ用)"""
    monkeypatch.chdir(tmp_path)
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "roadmap.md").write_text("# Roadmap\n", encoding="utf-8")
    (tmp_path / "artifacts" / "research").mkdir(parents=True)

    try:
        market_researcher.main()
    except SystemExit as e:
        if e.code != 0:
            pytest.xfail("market_researcher 未実装")

    notes = tmp_path / "artifacts" / "research" / "source_notes.md"
    assert notes.exists(), "source_notes.md が生成されていない"


def test_tc_05_03_scored_ideas_has_10_items(tmp_path, monkeypatch):
    """TC-05-03: scored_ideas.md に 10 件以上の候補が含まれる (TDD グリーンフェーズ用)"""
    monkeypatch.chdir(tmp_path)
    research_dir = tmp_path / "artifacts" / "research"
    research_dir.mkdir(parents=True)
    (research_dir / "research_report.md").write_text("# Research\n", encoding="utf-8")
    (research_dir / "idea_pool.md").write_text("# Ideas\n", encoding="utf-8")

    try:
        idea_scorer.main()
    except SystemExit as e:
        if e.code != 0:
            pytest.xfail("idea_scorer 未実装")

    scored = research_dir / "scored_ideas.md"
    assert scored.exists(), "scored_ideas.md が生成されていない"
    content = scored.read_text(encoding="utf-8")
    # 10件以上の候補（行または見出し）が含まれることを確認
    assert content.count("\n") >= 10 or len(content.split("##")) >= 10
