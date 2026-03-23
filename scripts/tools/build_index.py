"""
scripts/tools/build_index.py
ルートの index.html をアプリ一覧から再生成する
"""
from __future__ import annotations

import sys
from pathlib import Path

ADSENSE_PUB_ID = "ca-pub-6743751614716161"
ADSENSE_SCRIPT = (
    f'<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js'
    f'?client={ADSENSE_PUB_ID}" crossorigin="anonymous"></script>'
)

INDEX_TEMPLATE = """\
<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>OpenClaw App Company</title>
  {adsense_script}
  <style>
    body {{ font-family: sans-serif; max-width: 800px; margin: 40px auto; padding: 0 20px; }}
    ul {{ list-style: none; padding: 0; }}
    li {{ margin: 8px 0; }}
    a {{ text-decoration: none; color: #0066cc; }}
  </style>
</head>
<body>
  <h1>OpenClaw App Company</h1>
  <ul>
{app_links}
  </ul>
</body>
</html>
"""


def build_index(apps_dir: Path = Path("apps"), output: Path = Path("index.html")) -> None:
    app_links = []
    if apps_dir.exists():
        for app_dir in sorted(apps_dir.iterdir()):
            if app_dir.is_dir() and (app_dir / "index.html").exists():
                app_links.append(
                    f'    <li><a href="apps/{app_dir.name}/">{app_dir.name}</a></li>'
                )

    content = INDEX_TEMPLATE.format(
        adsense_script=ADSENSE_SCRIPT,
        app_links="\n".join(app_links),
    )
    output.write_text(content, encoding="utf-8")


def main() -> None:
    build_index()
    print("Generated: index.html")


if __name__ == "__main__":
    import os
    os.chdir(Path(__file__).parent.parent.parent)
    sys.path.insert(0, str(Path(__file__).parent.parent))
    main()
