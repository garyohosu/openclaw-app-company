const APP_ID = "app-001-kakeibo-memo";
const VISITOR_TRACKING = true;
const STORAGE_KEY = `${APP_ID}:entries:v1`;

const el = {
  form: document.getElementById('entry-form'),
  date: document.getElementById('date'),
  category: document.getElementById('category'),
  amount: document.getElementById('amount'),
  memo: document.getElementById('memo'),
  count: document.getElementById('count'),
  total: document.getElementById('total'),
  list: document.getElementById('list'),
  empty: document.getElementById('empty'),
  clearAll: document.getElementById('clear-all')
};

const load = () => {
  try { return JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]'); }
  catch { return []; }
};
const save = (entries) => localStorage.setItem(STORAGE_KEY, JSON.stringify(entries));

let entries = load();

function yen(n){ return `¥${Number(n).toLocaleString('ja-JP')}`; }

function render(){
  el.list.innerHTML = '';
  const total = entries.reduce((a, e) => a + Number(e.amount), 0);
  el.count.textContent = String(entries.length);
  el.total.textContent = yen(total);
  el.empty.style.display = entries.length ? 'none' : 'block';

  entries
    .slice()
    .sort((a,b)=> (a.date < b.date ? 1 : -1))
    .forEach((e) => {
      const li = document.createElement('li');
      li.className = 'item';
      li.innerHTML = `
        <div>
          <div><strong>${e.category}</strong> ${yen(e.amount)}</div>
          <div class="meta">${e.date} ${e.memo ? ` / ${e.memo}` : ''}</div>
        </div>
        <button class="del" data-id="${e.id}">削除</button>
      `;
      el.list.appendChild(li);
    });
}

el.form.addEventListener('submit', (ev) => {
  ev.preventDefault();
  const date = el.date.value;
  const category = el.category.value.trim();
  const amount = Number(el.amount.value);
  const memo = el.memo.value.trim();
  if (!date || !category || !Number.isFinite(amount) || amount <= 0) return;

  entries.push({
    id: crypto.randomUUID(),
    date, category, amount, memo,
    createdAt: new Date().toISOString()
  });
  save(entries);
  el.form.reset();
  el.date.valueAsDate = new Date();
  render();
});

el.list.addEventListener('click', (ev) => {
  const btn = ev.target.closest('.del');
  if (!btn) return;
  entries = entries.filter(e => e.id !== btn.dataset.id);
  save(entries);
  render();
});

el.clearAll.addEventListener('click', () => {
  if (!confirm('全データを削除します。よろしいですか？')) return;
  entries = [];
  save(entries);
  render();
});

document.addEventListener('DOMContentLoaded', () => {
  el.date.valueAsDate = new Date();
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
