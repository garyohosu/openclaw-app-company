"""scripts/agents/improvement_strategist.py — Improvement Strategist (リリース部 Phase 12)"""
from __future__ import annotations

import logging
from pathlib import Path

from agents._base import check_inputs, setup_agent_logging

AGENT_ID = "improvement_strategist"
REQUIRED_INPUTS = ["artifacts/sprints/deploy_report.md"]
OUTPUTS = [
    "artifacts/sprints/sprint_next.md",
    "artifacts/sprints/user_feedback.md",
    "artifacts/sprints/usage_insights.md",
]
logger = logging.getLogger(AGENT_ID)

SPRINT_NEXT_TEMPLATE = """\
# sprint_next.md

source: deploy_report.md
summary: minimal improvement plan
"""

USAGE_INSIGHTS_TEMPLATE = """\
# usage_insights.md

summary: placeholder (no data yet)
"""

USER_FEEDBACK_TEMPLATE = """\
# user_feedback.md

summary: placeholder (no feedback yet)
"""


def main() -> None:
    setup_agent_logging(AGENT_ID)
    logger.info(f"=== {AGENT_ID} 開始 ===")
    check_inputs(REQUIRED_INPUTS)
    report_path = Path(REQUIRED_INPUTS[0])
    content = report_path.read_text(encoding="utf-8")
    if "Release OK" not in content:
        logger.error("deploy_report.md is not Release OK")
        raise SystemExit(1)

    out_dir = Path("artifacts") / "sprints"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "sprint_next.md").write_text(
        SPRINT_NEXT_TEMPLATE, encoding="utf-8"
    )
    (out_dir / "usage_insights.md").write_text(
        USAGE_INSIGHTS_TEMPLATE, encoding="utf-8"
    )
    (out_dir / "user_feedback.md").write_text(
        USER_FEEDBACK_TEMPLATE, encoding="utf-8"
    )
    raise SystemExit(0)


if __name__ == "__main__":
    import os, sys
    from pathlib import Path
    os.chdir(Path(__file__).parent.parent.parent)
    sys.path.insert(0, str(Path(__file__).parent.parent))
    main()
