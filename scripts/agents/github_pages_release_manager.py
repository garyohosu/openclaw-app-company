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
release_readiness: {release_readiness}
browser_test_report: {browser_status}
design_review: {design_status}
publish_blocked_reason: {publish_blocked_reason}
public_url: {public_url}
index_updated: {index_updated}
notes: {notes}
"""


_STUB_MARKERS = frozenset({"stub", "placeholder"})


def _classify_status(path: Path) -> str:
    """ファイル内容からステータスを判定する。
    Returns: "OK" | "NG" | "stub"
      - "NG"  : FAIL または NG を含む (明示的な失敗)
      - "OK"  : OK または PASS を含み NG/FAIL がない (合格)
      - "stub": OK/PASS も NG/FAIL もないが stub/placeholder マーカーを含む (未実施)
      - それ以外: NG 扱い (未確認コンテンツは安全側へ)
    """
    content = path.read_text(encoding="utf-8")
    if "FAIL" in content or "NG" in content:
        return "NG"
    if "OK" in content or "PASS" in content:
        return "OK"
    lower = content.lower()
    if any(marker in lower for marker in _STUB_MARKERS):
        return "stub"
    return "NG"  # 未確認コンテンツは安全側


def main() -> None:
    setup_agent_logging(AGENT_ID)
    logger.info(f"=== {AGENT_ID} 開始 ===")
    check_inputs(REQUIRED_INPUTS)
    browser_path = Path(REQUIRED_INPUTS[0])
    design_path = Path(REQUIRED_INPUTS[1])

    browser_status = _classify_status(browser_path)
    design_status = _classify_status(design_path)

    # 明示的な NG は即失敗
    if browser_status == "NG":
        logger.error("browser_test_report is NG")
        raise SystemExit(1)
    if design_status == "NG":
        logger.error("design_review is NG")
        raise SystemExit(1)

    # stub 検出 → provisional (公開ブロック、ただし pipeline は継続)
    stubs = [name for name, st in [
        ("browser_test_report", browser_status),
        ("design_review", design_status),
    ] if st == "stub"]

    if stubs:
        release_result = "Release Provisional"
        release_readiness = "provisional"
        blocked_reason = f"QA stub 未完成: {', '.join(stubs)}"
        logger.warning(f"publish blocked — {blocked_reason}")
    else:
        release_result = "Release OK"
        release_readiness = "ready"
        blocked_reason = "-"
        logger.info("Release OK — QA 両方合格")

    out_dir = Path("artifacts") / "sprints"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "deploy_report.md").write_text(
        REPORT_TEMPLATE.format(
            release_result=release_result,
            release_readiness=release_readiness,
            browser_status=browser_status,
            design_status=design_status,
            publish_blocked_reason=blocked_reason,
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
