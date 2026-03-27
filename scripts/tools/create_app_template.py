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
  <main class="wrap">
    <header>
      <h1>{app_name}</h1>
      <p>クイックメモを保存して、あとから見返せるシンプルアプリ。</p>
    </header>

    <section class="card">
      <form id="memo-form" class="row">
        <input id="memo-input" type="text" placeholder="メモを入力" required>
        <button type="submit">追加</button>
      </form>
    </section>

    <section class="card summary">
      <div>件数: <strong id="count">0</strong></div>
      <button id="clear-all" class="danger">全削除</button>
    </section>

    <section class="card">
      <ul id="memo-list" class="list"></ul>
      <p id="empty" class="empty">メモはまだありません。</p>
    </section>
  </main>

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
const STORAGE_KEY = `${{APP_ID}}:memos:v1`;

const el = {{
  form: document.getElementById('memo-form'),
  input: document.getElementById('memo-input'),
  list: document.getElementById('memo-list'),
  empty: document.getElementById('empty'),
  count: document.getElementById('count'),
  clearAll: document.getElementById('clear-all')
}};

const load = () => {{
  try {{ return JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]'); }}
  catch {{ return []; }}
}};
const save = (rows) => localStorage.setItem(STORAGE_KEY, JSON.stringify(rows));

let memos = load();

function render() {{
  el.list.innerHTML = '';
  el.count.textContent = String(memos.length);
  el.empty.style.display = memos.length ? 'none' : 'block';

  memos.forEach((m) => {{
    const li = document.createElement('li');
    li.className = 'item';
    li.innerHTML = `
      <span>${{m.text}}</span>
      <button class="del" data-id="${{m.id}}">削除</button>
    `;
    el.list.appendChild(li);
  }});
}}

el.form.addEventListener('submit', (ev) => {{
  ev.preventDefault();
  const text = el.input.value.trim();
  if (!text) return;
  memos.unshift({{ id: crypto.randomUUID(), text, createdAt: new Date().toISOString() }});
  save(memos);
  el.form.reset();
  render();
}});

el.list.addEventListener('click', (ev) => {{
  const btn = ev.target.closest('.del');
  if (!btn) return;
  memos = memos.filter(m => m.id !== btn.dataset.id);
  save(memos);
  render();
}});

el.clearAll.addEventListener('click', () => {{
  if (!confirm('全メモを削除します。よろしいですか？')) return;
  memos = [];
  save(memos);
  render();
}});

document.addEventListener('DOMContentLoaded', () => {{
  render();
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
        ":root{--bg:#0f1117;--card:#1a1d27;--line:#2a2d3a;--text:#e2e4eb;--muted:#8b90a8;--accent:#4f8ef7;--danger:#e05252}\n"
        "*{box-sizing:border-box} body{margin:0;background:var(--bg);color:var(--text);font-family:-apple-system,BlinkMacSystemFont,\"Segoe UI\",sans-serif}\n"
        ".wrap{max-width:760px;margin:0 auto;padding:28px 16px 40px} header h1{margin:0 0 6px} header p{margin:0 0 14px;color:var(--muted)}\n"
        ".card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px;margin-bottom:12px}\n"
        ".row{display:flex;gap:8px;flex-wrap:wrap} input{flex:1;min-width:220px;background:#0f1420;border:1px solid var(--line);border-radius:8px;color:var(--text);padding:10px}\n"
        "button{background:var(--accent);border:none;border-radius:8px;color:#fff;padding:10px 12px;cursor:pointer;font-weight:700}\n"
        ".summary{display:flex;justify-content:space-between;align-items:center}.danger{background:var(--danger)}\n"
        ".list{list-style:none;margin:0;padding:0;display:grid;gap:8px}.item{display:flex;justify-content:space-between;align-items:center;gap:8px;border:1px solid var(--line);border-radius:10px;padding:10px;background:#131928}\n"
        ".empty{color:var(--muted);margin:2px 0}.del{background:#30384f;padding:6px 10px;font-size:.8rem}\n",
        encoding="utf-8"
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
