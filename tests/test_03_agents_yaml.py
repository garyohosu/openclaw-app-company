"""TC-03: AgentsYaml の読み込みと検索テスト"""
import pytest
from config.agents_yaml import AgentsYaml, AgentMeta


def test_tc_03_01_load(agents_yaml_path):
    """TC-03-01: 有効な agents.yaml から 30体分が読み込まれる"""
    ay = AgentsYaml.load(agents_yaml_path)
    assert len(ay.agents) == 30


def test_tc_03_02_find_by_id(agents_yaml_path):
    """TC-03-02: ID で AgentMeta を検索できる"""
    ay = AgentsYaml.load(agents_yaml_path)
    agent = ay.find("market_researcher")
    assert agent is not None
    assert agent.id == "market_researcher"
    assert isinstance(agent, AgentMeta)


def test_tc_03_03_not_found(agents_yaml_path):
    """TC-03-03: 存在しない ID は None を返す"""
    ay = AgentsYaml.load(agents_yaml_path)
    result = ay.find("nonexistent_agent")
    assert result is None


def test_tc_03_04_ceo_inputs(agents_yaml_path):
    """TC-03-04: CEO Agent の inputs が正しく取得できる"""
    ay = AgentsYaml.load(agents_yaml_path)
    ceo = ay.find("ceo")
    assert ceo is not None
    assert "artifacts/research/scored_ideas.md" in ceo.inputs
    assert "artifacts/product/prd.md" in ceo.inputs


def test_tc_03_file_not_found(tmp_path):
    """agents.yaml が存在しない場合 FileNotFoundError が送出される"""
    with pytest.raises(FileNotFoundError):
        AgentsYaml.load(tmp_path / "nonexistent.yaml")
