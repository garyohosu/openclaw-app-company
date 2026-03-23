"""
scripts/config/agents_yaml.py
AgentsYaml / AgentMeta — agents/agents.yaml 読み込みと検索
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

import yaml


@dataclass
class AgentMeta:
    id: str
    name: str
    role: str = ""
    responsibilities: List[str] = field(default_factory=list)
    inputs: List[str] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)
    can_run: List[str] = field(default_factory=list)
    human_approval_required: bool = False


@dataclass
class AgentsYaml:
    agents: List[AgentMeta] = field(default_factory=list)

    @classmethod
    def load(cls, path: Path) -> "AgentsYaml":
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"agents.yaml not found: {path}")
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        agents = [AgentMeta(**entry) for entry in data.get("agents", [])]
        return cls(agents=agents)

    def find(self, agent_id: str) -> Optional[AgentMeta]:
        for a in self.agents:
            if a.id == agent_id:
                return a
        return None
