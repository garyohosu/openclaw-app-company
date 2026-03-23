"""
scripts/tools/create_app_template.py
新規アプリのスケルトンを生成する

使い方:
  python scripts/tools/create_app_template.py --app-id app-001-sample --name "サンプルアプリ"
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ADSENSE_PUB_ID = "ca-pub-6743751614716161"
ADSENSE_SCRIPT = (
    f'<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js'
    f'?client={ADSENSE_PUB_ID}" crossorigin="anonymous"></script>'
)

HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{app_name}</title>
  {adsense_script}
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <h1>{app_name}</h1>
  <script src="api.js"></script>
  <script src="app.js"></script>
</body>
</html>
"""

API_JS_TEMPLATE = """\
const API_CONFIG = {{
  baseUrl: "https://your-sakura-domain.example/api",
  endpoints: {{
    now:      "/now.cgi",
    uuid:     "/uuid.cgi",
    validate: "/validate.cgi",
    convert:  "/convert.cgi",
    visitor:  "/visitor.cgi",
    db:       "/db.cgi"
  }}
}};
"""

APP_JS_TEMPLATE = """\
const APP_ID = "{app_id}";
const VISITOR_TRACKING = {visitor_tracking};

document.addEventListener('DOMContentLoaded', () => {{
  if (VISITOR_TRACKING) {{
    fetch(API_CONFIG.baseUrl + API_CONFIG.endpoints.visitor, {{
      method: 'POST',
      headers: {{ 'Content-Type': 'application/json' }},
      body: JSON.stringify({{
        action: 'visit',
        app_id: APP_ID,
        page: location.pathname,
        referrer: document.referrer || 'direct'
      }})
    }}).catch(() => {{}});
  }}
}});
"""

SPEC_TEMPLATE = """\
# {app_name} spec.md

app_id: {app_id}
app_name: {app_name}
summary: （アプリの概要を記載）
target_user: （対象ユーザーを記載）
main_use_cases:
  - （ユースケース1）
runtime_mode: static
api_endpoints: []
storage_strategy: localStorage
visitor_tracking: true
cors_origins: ["https://garyohosu.github.io", "http://localhost:8000"]
ssl_checked: false
pages_path: /apps/{app_id}/
known_constraints: なし
acceptance_criteria:
  - 表示できる
adsense_required: true
adsense_applied: false
adsense_checked_at_release: false
"""


def generate(app_id: str, app_name: str, visitor_tracking: bool = True) -> Path:
    app_dir = Path("apps") / app_id
    app_dir.mkdir(parents=True, exist_ok=True)

    adsense_script = ADSENSE_SCRIPT
    vt = "true" if visitor_tracking else "false"

    (app_dir / "index.html").write_text(
        HTML_TEMPLATE.format(
            app_name=app_name,
            adsense_script=adsense_script,
        ),
        encoding="utf-8",
    )
    (app_dir / "style.css").write_text(
        "/* styles */\n", encoding="utf-8"
    )
    (app_dir / "api.js").write_text(
        API_JS_TEMPLATE, encoding="utf-8"
    )
    (app_dir / "app.js").write_text(
        APP_JS_TEMPLATE.format(app_id=app_id, visitor_tracking=vt),
        encoding="utf-8",
    )
    (app_dir / "spec.md").write_text(
        SPEC_TEMPLATE.format(app_id=app_id, app_name=app_name),
        encoding="utf-8",
    )
    return app_dir


def main() -> None:
    parser = argparse.ArgumentParser(description="アプリテンプレート生成")
    parser.add_argument("--app-id", required=True, help="例: app-001-sample")
    parser.add_argument("--name", required=True, help="アプリ名")
    parser.add_argument("--no-visitor-tracking", action="store_true")
    args = parser.parse_args()

    app_dir = generate(
        app_id=args.app_id,
        app_name=args.name,
        visitor_tracking=not args.no_visitor_tracking,
    )
    print(f"Generated: {app_dir}")


if __name__ == "__main__":
    import os
    os.chdir(Path(__file__).parent.parent.parent)
    sys.path.insert(0, str(Path(__file__).parent.parent))
    main()
