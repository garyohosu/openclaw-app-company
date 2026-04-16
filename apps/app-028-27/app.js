const APP_ID = "app-028-27";
const VISITOR_TRACKING = true;
const STORAGE_KEY = `${APP_ID}:memos:v1`;

const el = {
  form: document.getElementById('memo-form'),
  input: document.getElementById('memo-input'),
  list: document.getElementById('memo-list'),
  empty: document.getElementById('empty'),
  count: document.getElementById('count'),
  clearAll: document.getElementById('clear-all')
};

const load = () => {
  try { return JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]'); }
  catch { return []; }
};
const save = (rows) => localStorage.setItem(STORAGE_KEY, JSON.stringify(rows));

let memos = load();

function render() {
  el.list.innerHTML = '';
  el.count.textContent = String(memos.length);
  el.empty.style.display = memos.length ? 'none' : 'block';

  memos.forEach((m) => {
    const li = document.createElement('li');
    li.className = 'item';
    li.innerHTML = `
      <span>${m.text}</span>
      <button class="del" data-id="${m.id}">削除</button>
    `;
    el.list.appendChild(li);
  });
}

el.form.addEventListener('submit', (ev) => {
  ev.preventDefault();
  const text = el.input.value.trim();
  if (!text) return;
  memos.unshift({ id: crypto.randomUUID(), text, createdAt: new Date().toISOString() });
  save(memos);
  el.form.reset();
  render();
});

el.list.addEventListener('click', (ev) => {
  const btn = ev.target.closest('.del');
  if (!btn) return;
  memos = memos.filter(m => m.id !== btn.dataset.id);
  save(memos);
  render();
});

el.clearAll.addEventListener('click', () => {
  if (!confirm('全メモを削除します。よろしいですか？')) return;
  memos = [];
  save(memos);
  render();
});

document.addEventListener('DOMContentLoaded', () => {
  render();
  if (VISITOR_TRACKING) {
    fetch(API_CONFIG.baseUrl + API_CONFIG.endpoints.visitor, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        action: 'visit',
        app_id: APP_ID,
        page: location.pathname,
        referrer: document.referrer || 'direct'
      })
    }).catch(() => {});
  }
});
