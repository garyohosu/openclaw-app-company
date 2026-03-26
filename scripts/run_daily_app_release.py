"""
Daily runner for openclaw-app-company.

Flow:
1) Run pipeline (scripts/main.py)
2) Create one new app from latest decision
3) Rebuild top index
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APPS_DIR = ROOT / "apps"
DECISION = ROOT / "artifacts" / "executive" / "decision.md"
SCORED = ROOT / "artifacts" / "research" / "scored_ideas.md"


def _run(cmd: list[str]) -> None:
    r = subprocess.run(cmd, cwd=ROOT)
    if r.returncode != 0:
        raise SystemExit(r.returncode)


def _slugify(text: str) -> str:
    s = text.strip().lower()
    s = s.replace(" ", "-")
    s = re.sub(r"[^a-z0-9\-]", "", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s or "app"


def _next_app_id() -> str:
    APPS_DIR.mkdir(parents=True, exist_ok=True)
    max_n = 0
    for p in APPS_DIR.iterdir():
        if not p.is_dir():
            continue
        m = re.match(r"app-(\d+)-", p.name)
        if m:
            max_n = max(max_n, int(m.group(1)))
    return f"app-{max_n+1:03d}"


def _selected_name() -> str:
    if DECISION.exists():
        for line in DECISION.read_text(encoding="utf-8").splitlines():
            if line.startswith("selected_app:"):
                name = line.split(":", 1)[1].strip()
                if name:
                    return name
    return "新規アプリ"


def _scored_ideas() -> list[str]:
    ideas: list[str] = []
    if SCORED.exists():
        for line in SCORED.read_text(encoding="utf-8").splitlines():
            if line.startswith("## "):
                name = line[3:].strip()
                if name:
                    ideas.append(name)
    return ideas


def _existing_app_names() -> set[str]:
    names: set[str] = set()
    if not APPS_DIR.exists():
        return names
    for spec in APPS_DIR.glob("*/spec.md"):
        for line in spec.read_text(encoding="utf-8").splitlines():
            if line.startswith("app_name:"):
                names.add(line.split(":", 1)[1].strip())
                break
    return names


def _pick_name() -> str:
    used = _existing_app_names()
    candidates = [_selected_name(), *_scored_ideas(), "習慣チェック", "買い物メモ", "学習タイマー"]
    for c in candidates:
        if c and c not in used:
            return c
    return f"新規アプリ-{len(used)+1}"


def main() -> None:
    # 1) run pipeline
    _run([sys.executable, "scripts/main.py"])

    # 2) create one new app
    name = _pick_name()
    app_id = _next_app_id() + "-" + _slugify(name)[:24]
    _run([sys.executable, "scripts/tools/create_app_template.py", "--app-id", app_id, "--name", name])

    # 3) rebuild index
    _run([sys.executable, "scripts/tools/build_index.py"])

    print(f"CREATED_APP={app_id}")


if __name__ == "__main__":
    main()
