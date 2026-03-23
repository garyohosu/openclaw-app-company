"""
tests/conftest.py
共通フィクスチャ
"""
import json
from pathlib import Path

import pytest

ADSENSE_PUB_ID = "ca-pub-6743751614716161"
ADSENSE_SCRIPT = (
    f'<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js'
    f'?client={ADSENSE_PUB_ID}" crossorigin="anonymous"></script>'
)


@pytest.fixture
def company_state_data() -> dict:
    return {
        "current_phase": "research",
        "current_sprint": 1,
        "selected_app": "app-001-sample",
        "deployment_target": "github_pages",
        "runtime_mode": "static",
        "api_endpoints": [],
        "quality_gate": {
            "pages_ready": False,
            "ssl_verified": False,
            "cors_verified": False,
            "browser_test_passed": False,
            "adsense_verified": False,
            "test_pages_adsense_clean": False,
            "release_gate_passed": False,
        },
        "next_action": "",
        "followup_action": "",
    }


@pytest.fixture
def company_state_json(tmp_path, company_state_data):
    p = tmp_path / "company_state.json"
    p.write_text(json.dumps(company_state_data), encoding="utf-8")
    return p


@pytest.fixture
def agents_yaml_path(tmp_path):
    content = (Path(__file__).parent.parent / "agents" / "agents.yaml").read_text(
        encoding="utf-8"
    )
    p = tmp_path / "agents.yaml"
    p.write_text(content, encoding="utf-8")
    return p


@pytest.fixture
def artifacts_dir(tmp_path):
    """artifacts/ ディレクトリを tmp_path 以下に作成する"""
    d = tmp_path / "artifacts"
    d.mkdir()
    return d
