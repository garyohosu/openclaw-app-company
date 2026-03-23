"""
scripts/state/company_state.py
CompanyState / QualityGate — 状態ファイル読み書き
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import List


@dataclass
class QualityGate:
    pages_ready: bool = False
    ssl_verified: bool = False
    cors_verified: bool = False
    browser_test_passed: bool = False
    adsense_verified: bool = False
    test_pages_adsense_clean: bool = False
    release_gate_passed: bool = False


@dataclass
class CompanyState:
    current_phase: str = "initialization"
    current_sprint: int = 1
    selected_app: str = ""
    deployment_target: str = "github_pages"
    runtime_mode: str = "static"
    api_endpoints: List[str] = field(default_factory=list)
    quality_gate: QualityGate = field(default_factory=QualityGate)
    next_action: str = ""

    @classmethod
    def load(cls, path: Path) -> "CompanyState":
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"State file not found: {path}")
        data = json.loads(path.read_text(encoding="utf-8"))
        qg_data = data.pop("quality_gate", {})
        state = cls(**data)
        state.quality_gate = QualityGate(**qg_data)
        return state

    @classmethod
    def default(cls) -> "CompanyState":
        return cls()

    def save(self, path: Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(asdict(self), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
