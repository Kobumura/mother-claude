// roundtable client -- streams the convo, shows who's here, and controls the AIs.
let NAME = localStorage.rt_name || prompt("Your name?") || "guest";
let CODE = localStorage.rt_code || prompt("Room code?") || "";
localStorage.rt_name = NAME;
localStorage.rt_code = CODE;

const inner  = document.getElementById('inner');
const log    = document.getElementById('log');
const tx     = document.getElementById('text');
const roster = document.getElementById('roster');

function esc(s) {
  return (s || '').replace(/[&<>]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c]));
}

// each viewer sees the time in THEIR own local timezone
function fmtTime(t) {
  try { return new Date(t * 1000).toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' }); }
  catch (e) { return ''; }
}

function add(m) {
  const d = document.createElement('div');
  d.className = 'msg ' + (m.kind === 'system' ? 'system' : esc(m.name));
  const time = m.t ? '<span class=time>' + fmtTime(m.t) + '</span>' : '';
  if (m.kind === 'system') d.innerHTML = '<div>' + esc(m.text) + ' ' + time + '</div>';
  else d.innerHTML = '<div class=name>' + esc(m.name) + time + '</div><div>' + esc(m.text) + '</div>';
  inner.appendChild(d);
  log.scrollTop = log.scrollHeight;
}

function postConfig(body) {
  fetch('/config', {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(Object.assign({ code: CODE, name: NAME }, body))
  });
}

// top bar: AI controls (checkbox in/out + cheap|heavy) on the left, humans present on the right
function renderRoster(d) {
  let html = '<div class=ais>';
  (d.ais || []).forEach(a => {
    html += '<label class="ai-ctl ' + esc(a.name) + (a.on ? '' : ' off') + '">'
      + '<input type=checkbox data-ai="' + esc(a.name) + '"' + (a.enabled ? ' checked' : '') + (a.hasKey ? '' : ' disabled') + '>'
      + '<span class=ainame>' + esc(a.name) + '</span>';
    if (a.hasKey) {
      html += '<select class=tier data-ai="' + esc(a.name) + '"' + (a.enabled ? '' : ' disabled') + '>'
        + ['cheap', 'heavy'].map(t => '<option' + (a.tier === t ? ' selected' : '') + '>' + t + '</option>').join('')
        + '</select>';
    } else { html += '<span class=nokey>no key</span>'; }
    html += '</label>';
  });
  html += '</div><div class=humans>';
  (d.humans || []).forEach(p => {
    html += '<span class="who ' + esc(p.status) + '"><span class=dot></span>' + esc(p.name) + '</span>';
  });
  html += '</div>';
  roster.innerHTML = html;
  roster.querySelectorAll('input[type=checkbox][data-ai]').forEach(cb =>
    cb.onchange = () => postConfig({ ai: cb.dataset.ai, enabled: cb.checked }));
  roster.querySelectorAll('select.tier[data-ai]').forEach(sel =>
    sel.onchange = () => postConfig({ ai: sel.dataset.ai, tier: sel.value }));
}

const es = new EventSource('/stream?name=' + encodeURIComponent(NAME));
es.onmessage = e => {
  const m = JSON.parse(e.data);
  if (m.kind === 'roster') renderRoster(m);
  else add(m);
};

function send() {
  const t = tx.value.trim();
  if (!t) return;
  tx.value = '';
  fetch('/send', {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name: NAME, code: CODE, text: t })
  }).then(r => r.json()).then(j => { if (!j.ok) alert(j.error || 'error'); });
}

document.getElementById('send').onclick = send;
tx.addEventListener('keydown', e => { if (e.key === 'Enter') send(); });
