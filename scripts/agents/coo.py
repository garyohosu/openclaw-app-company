"""scripts/agents/coo.py — COO Agent (経営層)"""
import logging
from pathlib import Path
from agents._base import check_inputs, setup_agent_logging

AGENT_ID = "coo"
REQUIRED_INPUTS = ["state/company_state.json", "artifacts/executive/decision.md"]
OUTPUTS = ["artifacts/executive/workflow_approval.md"]
logger = logging.getLogger(AGENT_ID)


def main() -> None:
    setup_agent_logging(AGENT_ID)
    logger.info(f"=== {AGENT_ID} 開始 ===")
    check_inputs(REQUIRED_INPUTS)

    decision = Path("artifacts/executive/decision.md").read_text(encoding="utf-8")
    approved = "decision: approved" in decision

    out_dir = Path("artifacts/executive")
    out_dir.mkdir(parents=True, exist_ok=True)
    status = "approved" if approved else "rejected"
    (out_dir / "workflow_approval.md").write_text(
        f"# workflow_approval.md\n\nsource: decision.md\nworkflow: {status}\n",
        encoding="utf-8",
    )
    logger.info(f"workflow_approval.md を出力しました (status: {status})")
    if not approved:
        raise SystemExit(1)
    raise SystemExit(0)


if __name__ == "__main__":
    import os, sys
    from pathlib import Path
    os.chdir(Path(__file__).parent.parent.parent)
    sys.path.insert(0, str(Path(__file__).parent.parent))
    main()
