"""scripts/agents/github_pages_release_manager.py — GitHub Pages Release Manager (リリース部 Phase 11)"""
from __future__ import annotations

import logging
from pathlib import Path

from agents._base import check_inputs, setup_agent_logging

AGENT_ID = "github_pages_release_manager"
REQUIRED_INPUTS = [
    "artifacts/qa/browser_test_report.md",
    "artifacts/qa/design_review.md",
]
OUTPUTS = ["artifacts/sprints/deploy_report.md"]
logger = logging.getLogger(AGENT_ID)

REPORT_TEMPLATE = """\
# deploy_report.md

release_result: {release_result}
browser_test_report: {browser_status}
design_review: {design_status}
public_url: {public_url}
index_updated: {index_updated}
notes: {notes}
"""


def _read_status(path: Path) -> bool:
    content = path.read_text(encoding="utf-8")
    return "OK" in content and "NG" not in content and "FAIL" not in content


def main() -> None:
    setup_agent_logging(AGENT_ID)
    logger.info(f"=== {AGENT_ID} 開始 ===")
    check_inputs(REQUIRED_INPUTS)
    browser_path = Path(REQUIRED_INPUTS[0])
    design_path = Path(REQUIRED_INPUTS[1])

    browser_ok = _read_status(browser_path)
    design_ok = _read_status(design_path)

    if not browser_ok:
        logger.error("browser_test_report is NG")
        raise SystemExit(1)
    if not design_ok:
        logger.error("design_review is NG")
        raise SystemExit(1)

    out_dir = Path("artifacts") / "sprints"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "deploy_report.md"
    out_path.write_text(
        REPORT_TEMPLATE.format(
            release_result="Release OK",
            browser_status="OK",
            design_status="OK",
            public_url="N/A",
            index_updated="false",
            notes="minimal release report",
        ),
        encoding="utf-8",
    )
    raise SystemExit(0)


if __name__ == "__main__":
    import os, sys
    from pathlib import Path
    os.chdir(Path(__file__).parent.parent.parent)
    sys.path.insert(0, str(Path(__file__).parent.parent))
    main()
