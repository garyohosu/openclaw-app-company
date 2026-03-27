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
    :root {{ --bg:#0f1117; --card:#1a1d27; --line:#2a2d3a; --text:#e2e4eb; --muted:#7a7f9a; --accent:#4f8ef7; }}
    * {{ box-sizing: border-box; }}
    body {{ margin:0; background:var(--bg); color:var(--text); font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }}
    .wrap {{ max-width: 880px; margin: 0 auto; padding: 40px 20px 64px; }}
    h1 {{ margin:0; font-size:1.8rem; }}
    .sub {{ color:var(--muted); margin:8px 0 24px; }}
    .panel {{ background:var(--card); border:1px solid var(--line); border-radius:12px; padding:16px; }}
    ul {{ list-style:none; margin:0; padding:0; display:grid; gap:12px; }}
    a {{ color:var(--accent); text-decoration:none; font-weight:600; }}
    .item {{ border:1px solid var(--line); border-radius:10px; padding:12px 14px; background:#141823; }}
    .hint {{ margin-top:20px; color:var(--muted); font-size:.9rem; }}
  </style>
</head>
<body>
  <div class="wrap">
    <h1>OpenClaw App Company</h1>
    <p class="sub">生成済みアプリ一覧</p>
    <section class="panel">
      <ul>
{app_links}
      </ul>
    </section>
    <p class="hint">※ アプリを追加したら <code>python scripts/tools/build_index.py</code> で再生成。</p>
    <p class="hint"><a href="privacy-policy/">Privacy Policy</a> / <a href="contact/">Contact</a></p>
  </div>
</body>
</html>
"""


def build_index(apps_dir: Path = Path("apps"), output: Path = Path("index.html")) -> None:
    app_links = []
    if apps_dir.exists():
        for app_dir in sorted(apps_dir.iterdir()):
            if app_dir.is_dir() and (app_dir / "index.html").exists():
                app_links.append(
                    f'        <li class="item"><a href="apps/{app_dir.name}/">{app_dir.name}</a></li>'
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
