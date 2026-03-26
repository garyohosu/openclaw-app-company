const APP_ID = "app-002-focus-timer";
const STORAGE_KEY = `${APP_ID}:done`;
const FOCUS = 25 * 60;
const BREAK = 5 * 60;

const el = {
  mode: document.getElementById('mode'),
  time: document.getElementById('time'),
  done: document.getElementById('done'),
  start: document.getElementById('start'),
  pause: document.getElementById('pause'),
  reset: document.getElementById('reset'),
  clear: document.getElementById('clear'),
};

let mode = 'FOCUS';
let remain = FOCUS;
let timer = null;
let doneCount = Number(localStorage.getItem(STORAGE_KEY) || 0);

function fmt(sec){
  const m = String(Math.floor(sec/60)).padStart(2,'0');
  const s = String(sec%60).padStart(2,'0');
  return `${m}:${s}`;
}

function render(){
  el.mode.textContent = mode;
  el.time.textContent = fmt(remain);
  el.done.textContent = String(doneCount);
}

function tick(){
  remain -= 1;
  if(remain <= 0){
    if(mode === 'FOCUS'){
      doneCount += 1;
      localStorage.setItem(STORAGE_KEY, String(doneCount));
      mode = 'BREAK';
      remain = BREAK;
    } else {
      mode = 'FOCUS';
      remain = FOCUS;
    }
  }
  render();
}

el.start.addEventListener('click', ()=>{
  if(timer) return;
  timer = setInterval(tick, 1000);
});
el.pause.addEventListener('click', ()=>{
  if(!timer) return;
  clearInterval(timer);
  timer = null;
});
el.reset.addEventListener('click', ()=>{
  if(timer){ clearInterval(timer); timer = null; }
  mode = 'FOCUS';
  remain = FOCUS;
  render();
});
el.clear.addEventListener('click', ()=>{
  doneCount = 0;
  localStorage.setItem(STORAGE_KEY, '0');
  render();
});

render();
