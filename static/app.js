// ---- API HELPERS ----
async function api(method, path, body = null) {
  const opts = { method, headers: {} };
  if (body !== null) {
    opts.headers['Content-Type'] = 'application/json';
    opts.body = JSON.stringify(body);
  }
  let res;
  try {
    res = await fetch('/api' + path, opts);
  } catch (e) {
    console.error('Network error', path, e);
    alert('Network error — could not reach the server.');
    return null;
  }
  if (!res.ok) {
    let msg = `Request failed (${res.status})`;
    try {
      const err = await res.json();
      if (err && err.error) msg = err.error;
    } catch (_) { /* response wasn't JSON */ }
    console.error('API error', path, res.status, msg);
    alert(msg);
    return null;
  }
  try { return await res.json(); }
  catch (_) { return null; }
}

// ---- HTML / URL ESCAPING ----
function escapeHTML(s) {
  if (s === null || s === undefined) return '';
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

// Returns the URL only if it uses an http(s) scheme; otherwise '#'.
// Stops javascript:/data: URLs from rendering as clickable hrefs.
function safeUrl(u) {
  if (!u) return '';
  const s = String(u).trim();
  if (/^https?:\/\//i.test(s)) return s;
  return '';
}

// ---- LOCAL DATE ----
// Browser-local YYYY-MM-DD (NOT UTC). Using Date.toISOString() produced
// off-by-one dates around midnight in NZDT (UTC+13).
function todayLocal() {
  const d = new Date();
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${y}-${m}-${day}`;
}

// ---- IN-APP CONFIRM ----
// Returns a Promise<boolean>. Replaces native confirm() so the dark theme is
// preserved and prompts don't pause the JS event loop.
function appConfirm(message, { title = 'Are you sure?', okLabel = 'Confirm', danger = true } = {}) {
  return new Promise((resolve) => {
    const overlay = document.getElementById('modal-confirm');
    document.getElementById('confirm-title').textContent = title;
    document.getElementById('confirm-message').textContent = message;
    const ok = document.getElementById('confirm-ok');
    const cancel = document.getElementById('confirm-cancel');
    ok.textContent = okLabel;
    ok.classList.toggle('btn-danger', danger);
    ok.classList.toggle('btn-primary', !danger);
    function done(result) {
      overlay.classList.remove('open');
      ok.removeEventListener('click', okHandler);
      cancel.removeEventListener('click', cancelHandler);
      resolve(result);
    }
    function okHandler() { done(true); }
    function cancelHandler() { done(false); }
    ok.addEventListener('click', okHandler);
    cancel.addEventListener('click', cancelHandler);
    overlay.classList.add('open');
  });
}

// ---- STATE ----
let sessions = [], moves = [], tricks = [], dashData = {}, settings = {};

async function loadAll() {
  const [s, m, t, d, st] = await Promise.all([
    api('GET', '/sessions'),
    api('GET', '/moves'),
    api('GET', '/tricks'),
    api('GET', '/dashboard'),
    api('GET', '/settings'),
  ]);
  sessions = s || [];
  moves    = m || [];
  tricks   = t || [];
  dashData = d || {};
  settings = st || {};

  // Populate settings input
  const inp = document.getElementById('setting-brushup-days');
  if (inp) inp.value = settings.brush_up_days || 14;

  updateAll();
}

// ---- NAVIGATION ----
function nav(page) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
  document.getElementById('page-' + page).classList.add('active');
  document.querySelectorAll('.nav-item').forEach(n => {
    if (n.getAttribute('onclick') === `nav('${page}')`) n.classList.add('active');
  });
  if (page === 'settings') refreshTrash();
}

// ---- MODAL ----
function openModal(id) {
  if (id === 'modal-session') {
    goToSessionStep1();
  }
  if (id === 'modal-move')  clearMoveForm();
  if (id === 'modal-trick') clearTrickForm();
  document.getElementById(id).classList.add('open');
}

// ---- TWO-STEP SESSION MODAL ----
let sessionCategory = null;

const FOCUS_OPTIONS = {
  moves:  ['Sleight of Hand','Controls & Breaks','False Shuffles / Cuts','Forces','Palming','Cardistry'],
  tricks: ['Specific Tricks','Full Routine Run-through','Performance Practice'],
};

function goToSessionStep1() {
  sessionCategory = null;
  document.getElementById('session-step-1').classList.add('active');
  document.getElementById('session-step-2').classList.remove('active');
  document.getElementById('cat-moves').classList.remove('selected');
  document.getElementById('cat-tricks').classList.remove('selected');
  msReset();
}

function selectSessionCategory(cat) {
  sessionCategory = cat;
  document.getElementById('cat-moves').classList.toggle('selected', cat === 'moves');
  document.getElementById('cat-tricks').classList.toggle('selected', cat === 'tricks');
  // Auto-advance — picking a category IS the choice; no need for a Next click.
  goToSessionStep2();
}

function goToSessionStep2() {
  if (!sessionCategory) return;

  // Populate focus dropdown for this category
  const focusSelect = document.getElementById('s-focus');
  focusSelect.innerHTML = '<option value="">— Select focus —</option>' +
    FOCUS_OPTIONS[sessionCategory].map(o => `<option>${o}</option>`).join('');

  // Show/hide checklists based on category
  const movesSection  = document.getElementById('section-moves');
  const tricksSection = document.getElementById('section-tricks');
  movesSection.style.display  = sessionCategory === 'tricks' ? 'none' : '';
  tricksSection.style.display = sessionCategory === 'moves'  ? 'none' : '';

  // Label + reset
  document.getElementById('step2-category-label').textContent =
    sessionCategory === 'moves' ? 'Sleights' : 'Tricks';
  document.getElementById('s-date').value = todayLocal();
  setRating('s-rating', 0);
  onFocusChange('');
  populateSessionChecklists();

  document.getElementById('session-step-1').classList.remove('active');
  document.getElementById('session-step-2').classList.add('active');
}

function populateSessionChecklists() {
  const movesList = document.getElementById('s-moves-list');
  if (!moves.length) {
    movesList.innerHTML = '<div style="color:var(--text3);font-size:12px;padding:10px 12px">No sleights in your library yet — add some in Sleights first.</div>';
  } else {
    movesList.innerHTML = moves.map(m => `
      <div class="check-item" data-id="${m.id}" data-type="move" onclick="toggleCheckItem(this)">
        <span class="check-icon">☐</span>
        <span class="check-name" style="flex:1;font-size:12px">${escapeHTML(m.name)}</span>
        <span class="item-category">${escapeHTML(m.category)}</span>
      </div>`).join('');
  }

  const tricksList = document.getElementById('s-tricks-list');
  if (!tricks.length) {
    tricksList.innerHTML = '<div style="color:var(--text3);font-size:12px;padding:10px 12px">No tricks in your library yet — add some in Tricks first.</div>';
  } else {
    tricksList.innerHTML = tricks.map(t => `
      <div class="check-item" data-id="${t.id}" data-type="trick" onclick="toggleCheckItem(this)">
        <span class="check-icon">☐</span>
        <span class="check-name" style="flex:1;font-size:12px">${escapeHTML(t.name)}</span>
        <span class="level-badge ${statusBadgeClass[t.status] || 'level-learning'}">${escapeHTML(t.status)}</span>
      </div>`).join('');
  }
}

function toggleCheckItem(el) {
  el.classList.toggle('selected');
  el.querySelector('.check-icon').textContent = el.classList.contains('selected') ? '☑' : '☐';
}

function getCheckedIds(listId) {
  return Array.from(document.getElementById(listId).querySelectorAll('.check-item.selected'))
    .map(el => parseInt(el.dataset.id));
}

function onFocusChange(val) {
  const movesSection  = document.getElementById('section-moves');
  const tricksSection = document.getElementById('section-tricks');
  movesSection.classList.remove('active-focus','inactive-focus');
  tricksSection.classList.remove('active-focus','inactive-focus');
  if (val && sessionCategory === 'moves') {
    movesSection.classList.add('active-focus');
  } else if (val && sessionCategory === 'tricks') {
    tricksSection.classList.add('active-focus');
  }
}

function closeModal(id) {
  document.getElementById(id).classList.remove('open');
}

// Outside clicks do not close modals — user must use Cancel or Close button

// ---- STAR RATING ----
function setRating(id, val) {
  const el = document.getElementById(id);
  el.dataset.val = val;
  el.querySelectorAll('.star').forEach(s => s.classList.toggle('active', parseInt(s.dataset.v) <= val));
}

function getRating(id) { return parseInt(document.getElementById(id).dataset.val) || 0; }
function renderStars(n) { return '★'.repeat(n) + '☆'.repeat(5 - n); }
function formatDate(d) {
  const dt = new Date(d + 'T12:00:00');
  return dt.toLocaleDateString('en-US', { weekday:'short', year:'numeric', month:'short', day:'numeric' });
}

// ---- SESSIONS ----
async function saveSession() {
  const date = document.getElementById('s-date').value;
  if (!date) { alert('Please select a date.'); return; }
  await api('POST', '/sessions', {
    date,
    duration: parseInt(document.getElementById('s-duration').value) || 0,
    title: document.getElementById('s-title').value.trim() || 'Practice Session',
    focus: document.getElementById('s-focus').value,
    notes: document.getElementById('s-notes').value.trim(),
    rating: getRating('s-rating'),
    move_ids: getCheckedIds('s-moves-list'),
    trick_ids: getCheckedIds('s-tricks-list'),
  });
  closeModal('modal-session');
  resetSessionForm();
  await loadAll();
}

function resetSessionForm() {
  ['s-duration','s-title','s-notes'].forEach(id => { const el = document.getElementById(id); if (el) el.value = ''; });
  document.getElementById('s-focus').value = '';
  onFocusChange('');
  setRating('s-rating', 0);
  msReset();
  document.querySelectorAll('#s-moves-list .check-item, #s-tricks-list .check-item').forEach(el => {
    el.classList.remove('selected');
    el.querySelector('.check-icon').textContent = '☐';
  });
  goToSessionStep1();
}

async function deleteSession(id) {
  await api('DELETE', '/sessions/' + id);
  closeModal('modal-view-session');
  await loadAll();
}

// ---- EDIT SESSION ----
function openEditSession(id) {
  const s = sessions.find(x => x.id === id);
  if (!s) return;
  document.getElementById('es-id').value       = s.id;
  document.getElementById('es-date').value     = s.date;
  document.getElementById('es-duration').value = s.duration_mins || 0;
  document.getElementById('es-title').value    = s.title || '';
  document.getElementById('es-focus').value    = s.focus || '';
  document.getElementById('es-notes').value    = s.notes || '';
  setRating('es-rating', s.rating || 0);
  closeModal('modal-view-session');
  document.getElementById('modal-edit-session').classList.add('open');
}

async function saveSessionEdit() {
  const id = parseInt(document.getElementById('es-id').value);
  const body = {
    date:     document.getElementById('es-date').value,
    duration: parseInt(document.getElementById('es-duration').value) || 0,
    title:    document.getElementById('es-title').value.trim() || 'Practice Session',
    focus:    document.getElementById('es-focus').value.trim(),
    notes:    document.getElementById('es-notes').value.trim(),
    rating:   getRating('es-rating'),
  };
  if (!body.date) { alert('Please select a date.'); return; }
  const res = await api('PUT', '/sessions/' + id, body);
  if (!res) return;  // api() already alerted
  closeModal('modal-edit-session');
  await loadAll();
}

function viewSession(id) {
  const s = sessions.find(x => x.id === id);
  if (!s) return;
  document.getElementById('vs-title').textContent = s.title;
  const linkedMoves  = (s.linked_moves  || []).map(m => `<span class="tag tag-practiced">${escapeHTML(m.name)}</span>`).join('');
  const linkedTricks = (s.linked_tricks || []).map(t => `<span class="tag tag-practiced">${escapeHTML(t.name)}</span>`).join('');
  document.getElementById('vs-body').innerHTML = `
    <div class="grid-2" style="margin-bottom:12px">
      <div><span style="color:var(--text3);font-size:10px;text-transform:uppercase;letter-spacing:.1em">Date</span><br><span>${escapeHTML(formatDate(s.date))}</span></div>
      <div><span style="color:var(--text3);font-size:10px;text-transform:uppercase;letter-spacing:.1em">Duration</span><br><span>${s.duration_mins ? escapeHTML(s.duration_mins + ' min') : '—'}</span></div>
    </div>
    ${s.focus ? `<div class="form-group"><span style="color:var(--text3);font-size:10px;text-transform:uppercase;letter-spacing:.1em">Focus</span><br><span class="tag">${escapeHTML(s.focus)}</span></div>` : ''}
    ${linkedMoves  ? `<div class="form-group"><span style="color:var(--text3);font-size:10px;text-transform:uppercase;letter-spacing:.1em">Moves Practiced</span><br><div style="margin-top:4px">${linkedMoves}</div></div>` : ''}
    ${linkedTricks ? `<div class="form-group"><span style="color:var(--text3);font-size:10px;text-transform:uppercase;letter-spacing:.1em">Tricks Practiced</span><br><div style="margin-top:4px">${linkedTricks}</div></div>` : ''}
    ${s.notes ? `<div class="form-group"><span style="color:var(--text3);font-size:10px;text-transform:uppercase;letter-spacing:.1em">Notes</span><br><p style="color:var(--text2);font-size:12px;font-style:italic;margin-top:4px">${escapeHTML(s.notes)}</p></div>` : ''}
    <div><span style="color:var(--accent)">${renderStars(s.rating)}</span></div>
  `;
  document.getElementById('vs-delete-btn').onclick = async () => {
    if (await appConfirm('Delete this session? It will be moved to Recently Deleted in Settings.')) deleteSession(id);
  };
  document.getElementById('vs-edit-btn').onclick = () => openEditSession(id);
  document.getElementById('modal-view-session').classList.add('open');
}

function renderSessions(list, containerId, limit) {
  const target = document.getElementById(containerId);
  if (!target) return;
  const data = limit ? list.slice(0, limit) : list;
  if (!data.length) { target.innerHTML = ''; return; }
  target.innerHTML = data.map(s => {
    const d = new Date(s.date + 'T12:00:00');
    const notesPreview = s.notes ? escapeHTML(s.notes.slice(0,80)) + (s.notes.length>80?'…':'') : '';
    const practiced = [
      ...(s.linked_tricks || []).map(t => t.name),
      ...(s.linked_moves  || []).map(m => m.name),
    ];
    const practicedTags = practiced.length
      ? `<div class="session-practiced">${practiced.map(n => `<span class="tag tag-practiced">${escapeHTML(n)}</span>`).join('')}</div>`
      : '';
    return `<div class="session-item" onclick="viewSession(${s.id})">
      <div class="session-date"><div class="day">${d.getDate()}</div><div class="month">${d.toLocaleString('default',{month:'short'})}</div></div>
      <div class="session-info">
        <div class="title">${escapeHTML(s.title)}</div>
        <div class="meta">
          ${s.duration_mins ? `<span>◷ ${escapeHTML(s.duration_mins + ' min')}</span>` : ''}
          ${s.focus ? `<span class="tag">${escapeHTML(s.focus)}</span>` : ''}
        </div>
        ${practicedTags}
        ${notesPreview ? `<div class="notes">${notesPreview}</div>` : ''}
      </div>
      <div class="session-rating">${renderStars(s.rating)}</div>
    </div>`;
  }).join('');
}

// ---- MOVES ----
const DIFF_LETTER = { easy: 'E', medium: 'M', difficult: 'D' };
const DIFF_NAME   = { easy: 'Easy', medium: 'Medium', difficult: 'Difficult' };

function clearMoveForm() {
  ['m-id','m-name','m-source','m-notes'].forEach(id => { const el = document.getElementById(id); if (el) el.value = ''; });
  document.getElementById('m-category').value   = 'Control';
  document.getElementById('m-level').value      = 'beginner';
  document.getElementById('m-difficulty').value = '';
  setRating('m-rating', 0);
}

async function saveMove() {
  const name = document.getElementById('m-name').value.trim();
  if (!name) { alert('Please enter a sleight name.'); return; }
  await api('POST', '/moves', {
    id: document.getElementById('m-id').value ? parseInt(document.getElementById('m-id').value) : null,
    name,
    category:   document.getElementById('m-category').value,
    level:      document.getElementById('m-level').value,
    difficulty: document.getElementById('m-difficulty').value,
    source:     document.getElementById('m-source').value.trim(),
    notes:      document.getElementById('m-notes').value.trim(),
    rating:     getRating('m-rating'),
  });
  closeModal('modal-move');
  await loadAll();
}

function editMove(id) {
  const m = moves.find(x => x.id === id);
  if (!m) return;
  document.getElementById('m-id').value         = m.id;
  document.getElementById('m-name').value       = m.name;
  document.getElementById('m-category').value   = m.category;
  document.getElementById('m-level').value      = m.level;
  document.getElementById('m-difficulty').value = m.difficulty || '';
  document.getElementById('m-source').value     = m.source || '';
  document.getElementById('m-notes').value      = m.notes  || '';
  setRating('m-rating', m.rating);
  document.getElementById('modal-move').classList.add('open');
}

async function deleteMove(id) {
  if (!await appConfirm('Delete this sleight? You can restore it from Settings → Recently Deleted.')) return;
  await api('DELETE', '/moves/' + id);
  await loadAll();
}

const VALID_MOVE_LEVELS = new Set(['beginner','developing','proficient','performance']);
function moveCardHTML(m, showActions) {
  const safeLevel = VALID_MOVE_LEVELS.has(m.level) ? m.level : 'beginner';
  const count = Number(m.practice_count) || 0;
  const lastPracticed = m.last_practiced
    ? `<span class="item-practiced">Last practiced: ${escapeHTML(m.last_practiced)}</span>`
    : '<span class="item-practiced">Never practiced</span>';
  const cardClass = showActions ? 'item-card is-clickable' : 'item-card';
  const cardClick = showActions ? `onclick="openMoveDetail(${m.id})"` : '';
  const stop = 'onclick="event.stopPropagation();';
  const diffLetter = DIFF_LETTER[m.difficulty] || '';
  const diffName   = DIFF_NAME[m.difficulty]   || '';
  const diffBadge  = diffLetter
    ? `<span class="diff-badge diff-${m.difficulty}" title="${escapeHTML(diffName)}">${diffLetter}</span>`
    : '';
  return `<div class="${cardClass}" ${cardClick}>
    <div class="item-header">
      ${diffBadge}
      <div class="item-name">${escapeHTML(m.name)}</div>
      <div class="item-category">${escapeHTML(m.category)}</div>
      <span class="level-badge level-${safeLevel}">${escapeHTML(m.level)}</span>
    </div>
    <div class="item-meta">
      <span>Confidence: <span style="color:var(--accent)">${renderStars(m.rating)}</span></span>
      ${m.source ? `<span>📖 ${escapeHTML(m.source)}</span>` : ''}
      ${lastPracticed}
      <span class="practice-count" title="Total times practised">${count}× practised</span>
    </div>
    ${showActions ? `<div class="item-actions">
      <button class="btn btn-sm" ${stop}showMoveHistory(${m.id})">History</button>
      <button class="btn btn-sm" ${stop}editMove(${m.id})">Edit</button>
      <button class="btn btn-sm btn-danger" ${stop}deleteMove(${m.id})">Delete</button>
    </div>` : ''}
  </div>`;
}

function buildAlphaIndexFor(activeLetters, indexId, letterPrefix) {
  const idx = document.getElementById(indexId);
  if (!idx) return;
  const all = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split('');
  idx.innerHTML = all.map(l => {
    const has = activeLetters.includes(l);
    return `<a href="#${letterPrefix}-${l}" class="${has ? 'alpha-active' : 'alpha-empty'}"
      onclick="${has ? `event.preventDefault();document.getElementById('${letterPrefix}-${l}').scrollIntoView({behavior:'smooth',block:'start'})` : 'event.preventDefault()'}">
      ${l}</a>`;
  }).join('');
}

function renderMoves(containerId, list) {
  const target = document.getElementById(containerId);
  if (!target) return;
  if (!list.length) {
    target.innerHTML = '<div style="color:var(--text3);font-size:12px;padding:10px 0">No sleights tracked yet.</div>';
    if (containerId === 'moves-list') buildAlphaIndexFor([], 'moves-alpha-index', 'moves-letter');
    return;
  }
  const showActions = containerId === 'moves-list';
  if (!showActions) {
    target.innerHTML = list.map(m => moveCardHTML(m, false)).join('');
    return;
  }
  const sorted = [...list].sort((a, b) => a.name.localeCompare(b.name));
  const groups = {};
  sorted.forEach(m => {
    const letter = m.name[0].toUpperCase();
    if (!groups[letter]) groups[letter] = [];
    groups[letter].push(m);
  });
  let html = '';
  Object.keys(groups).sort().forEach(letter => {
    html += `<div class="tricks-letter-heading" id="moves-letter-${letter}">${letter}</div>`;
    html += groups[letter].map(m => moveCardHTML(m, true)).join('');
  });
  target.innerHTML = html;
  buildAlphaIndexFor(Object.keys(groups), 'moves-alpha-index', 'moves-letter');
}

function filterMoves() {
  const q = document.getElementById('moves-search').value.trim().toLowerCase();
  const filtered = q ? moves.filter(m => m.name.toLowerCase().includes(q) || (m.category || '').toLowerCase().includes(q) || (m.notes || '').toLowerCase().includes(q)) : moves;
  renderMoves('moves-list', filtered);
  if (q && filtered.length === 0) {
    document.getElementById('moves-list').innerHTML = `<div class="tricks-no-results">No sleights match "<strong>${escapeHTML(q)}</strong>"</div>`;
    buildAlphaIndexFor([], 'moves-alpha-index', 'moves-letter');
  }
}

// ---- TRICKS ----
const METHOD_LETTER = { self_working: 'S', mnemonics: 'M', fluffy: 'F', knucklebusters: 'K' };
const METHOD_NAME   = { self_working: 'Self-working', mnemonics: 'Mnemonics', fluffy: 'Fluffy', knucklebusters: 'Knucklebusters' };

function clearTrickForm() {
  ['t-id','t-name','t-moves','t-source','t-notes','t-link'].forEach(id => { const el = document.getElementById(id); if (el) el.value = ''; });
  document.getElementById('t-type').value       = 'Trick';
  document.getElementById('t-status').value     = 'learning';
  document.getElementById('t-method').value     = '';
  document.getElementById('t-difficulty').value = '';
  setRating('t-rating', 0);
}

async function saveTrick() {
  const name = document.getElementById('t-name').value.trim();
  if (!name) { alert('Please enter a trick name.'); return; }
  await api('POST', '/tricks', {
    id: document.getElementById('t-id').value ? parseInt(document.getElementById('t-id').value) : null,
    name,
    type:       document.getElementById('t-type').value,
    status:     document.getElementById('t-status').value,
    method:     document.getElementById('t-method').value,
    difficulty: document.getElementById('t-difficulty').value,
    link:       document.getElementById('t-link').value.trim(),
    moves_used: document.getElementById('t-moves').value.trim(),
    source:     document.getElementById('t-source').value.trim(),
    notes:      document.getElementById('t-notes').value.trim(),
    rating:     getRating('t-rating'),
  });
  closeModal('modal-trick');
  await loadAll();
}

function editTrick(id) {
  const t = tricks.find(x => x.id === id);
  if (!t) return;
  document.getElementById('t-id').value         = t.id;
  document.getElementById('t-name').value       = t.name;
  document.getElementById('t-type').value       = t.type;
  document.getElementById('t-status').value     = t.status;
  document.getElementById('t-method').value     = t.method || '';
  document.getElementById('t-difficulty').value = t.difficulty || '';
  document.getElementById('t-link').value       = t.link   || '';
  document.getElementById('t-moves').value  = t.moves_used || '';
  document.getElementById('t-source').value = t.source || '';
  document.getElementById('t-notes').value  = t.notes  || '';
  setRating('t-rating', t.rating);
  document.getElementById('modal-trick').classList.add('open');
}

// ---- TRICK DETAIL PAGE ----
let currentTrickId = null;
let trickDetailDirty = false;

function openTrickDetail(id) {
  const t = tricks.find(x => x.id === id);
  if (!t) return;
  currentTrickId = id;
  trickDetailDirty = false;

  document.getElementById('td-name').textContent = t.name;
  const badge = document.getElementById('td-status-badge');
  badge.className = 'level-badge ' + (statusBadgeClass[t.status] || 'level-learning');
  badge.textContent = t.status;
  const mBadge = document.getElementById('td-method-badge');
  if (t.method && METHOD_LETTER[t.method]) {
    mBadge.style.display = '';
    mBadge.className = 'method-badge method-' + t.method;
    mBadge.textContent = METHOD_LETTER[t.method];
    mBadge.title = METHOD_NAME[t.method];
  } else {
    mBadge.style.display = 'none';
  }
  const dBadge = document.getElementById('td-difficulty-badge');
  if (t.difficulty && DIFF_LETTER[t.difficulty]) {
    dBadge.style.display = '';
    dBadge.className = 'diff-badge diff-' + t.difficulty;
    dBadge.textContent = DIFF_LETTER[t.difficulty];
    dBadge.title = DIFF_NAME[t.difficulty];
  } else {
    dBadge.style.display = 'none';
  }

  document.getElementById('td-type').value       = t.type   || 'Trick';
  document.getElementById('td-status').value     = t.status || 'learning';
  document.getElementById('td-method').value     = t.method || '';
  document.getElementById('td-difficulty').value = t.difficulty || '';
  document.getElementById('td-source').value     = t.source || '';
  document.getElementById('td-link').value       = t.link   || '';
  document.getElementById('td-moves').value      = t.moves_used || '';
  document.getElementById('td-notes').value      = t.notes  || '';
  setRating('td-rating', t.rating || 0);
  document.getElementById('td-last').textContent  = t.last_practiced || 'Never practiced';
  document.getElementById('td-count').textContent = (Number(t.practice_count) || 0) + '×';

  const tutBtn = document.getElementById('td-tutorial-btn');
  const safeLink = safeUrl(t.link);
  if (safeLink) {
    tutBtn.style.display = '';
    tutBtn.onclick = () => window.open(safeLink, '_blank', 'noopener,noreferrer');
  } else {
    tutBtn.style.display = 'none';
  }
  document.getElementById('td-history-btn').onclick = () => showTrickHistory(id);
  document.getElementById('td-delete-btn').onclick  = async () => {
    if (await appConfirm('Delete this trick? You can restore it from Settings → Recently Deleted.')) {
      await api('DELETE', '/tricks/' + id);
      currentTrickId = null;
      nav('tricks');
      await loadAll();
    }
  };

  // Track edits so we can warn before navigating away with unsaved changes.
  ['td-type','td-status','td-method','td-difficulty','td-source','td-link','td-moves','td-notes'].forEach(fid => {
    const el = document.getElementById(fid);
    el.oninput = el.onchange = () => { trickDetailDirty = true; };
  });

  nav('trick-detail');
}

async function saveTrickDetail() {
  if (currentTrickId === null) return;
  const body = {
    id:         currentTrickId,
    name:       document.getElementById('td-name').textContent,
    type:       document.getElementById('td-type').value,
    status:     document.getElementById('td-status').value,
    method:     document.getElementById('td-method').value,
    difficulty: document.getElementById('td-difficulty').value,
    source:     document.getElementById('td-source').value.trim(),
    link:       document.getElementById('td-link').value.trim(),
    moves_used: document.getElementById('td-moves').value.trim(),
    notes:      document.getElementById('td-notes').value,
    rating:     getRating('td-rating'),
  };
  const res = await api('POST', '/tricks', body);
  if (!res) return;
  trickDetailDirty = false;
  const msg = document.getElementById('td-saved-msg');
  msg.style.display = 'inline';
  setTimeout(() => { msg.style.display = 'none'; }, 1800);
  await loadAll();
}

function resetTrickDetail() {
  if (currentTrickId !== null) openTrickDetail(currentTrickId);
}

// ---- MOVE DETAIL PAGE ----
let currentMoveId = null;
let moveDetailDirty = false;

function openMoveDetail(id) {
  const m = moves.find(x => x.id === id);
  if (!m) return;
  currentMoveId = id;
  moveDetailDirty = false;

  const safeLevel = VALID_MOVE_LEVELS.has(m.level) ? m.level : 'beginner';
  document.getElementById('md-name').textContent = m.name;
  const badge = document.getElementById('md-level-badge');
  badge.className = 'level-badge level-' + safeLevel;
  badge.textContent = m.level;
  const dBadge = document.getElementById('md-difficulty-badge');
  if (m.difficulty && DIFF_LETTER[m.difficulty]) {
    dBadge.style.display = '';
    dBadge.className = 'diff-badge diff-' + m.difficulty;
    dBadge.textContent = DIFF_LETTER[m.difficulty];
    dBadge.title = DIFF_NAME[m.difficulty];
  } else {
    dBadge.style.display = 'none';
  }

  document.getElementById('md-category').value   = m.category || 'Other';
  document.getElementById('md-level').value      = safeLevel;
  document.getElementById('md-difficulty').value = m.difficulty || '';
  document.getElementById('md-source').value     = m.source   || '';
  document.getElementById('md-notes').value      = m.notes    || '';
  setRating('md-rating', m.rating || 0);
  document.getElementById('md-last').textContent  = m.last_practiced || 'Never practiced';
  document.getElementById('md-count').textContent = (Number(m.practice_count) || 0) + '×';

  document.getElementById('md-history-btn').onclick = () => showMoveHistory(id);
  document.getElementById('md-delete-btn').onclick  = async () => {
    if (await appConfirm('Delete this sleight? You can restore it from Settings → Recently Deleted.')) {
      await api('DELETE', '/moves/' + id);
      currentMoveId = null;
      nav('moves');
      await loadAll();
    }
  };

  ['md-category','md-level','md-difficulty','md-source','md-notes'].forEach(fid => {
    const el = document.getElementById(fid);
    el.oninput = el.onchange = () => { moveDetailDirty = true; };
  });

  nav('move-detail');
}

async function saveMoveDetail() {
  if (currentMoveId === null) return;
  const body = {
    id:         currentMoveId,
    name:       document.getElementById('md-name').textContent,
    category:   document.getElementById('md-category').value,
    level:      document.getElementById('md-level').value,
    difficulty: document.getElementById('md-difficulty').value,
    source:     document.getElementById('md-source').value.trim(),
    notes:      document.getElementById('md-notes').value,
    rating:     getRating('md-rating'),
  };
  const res = await api('POST', '/moves', body);
  if (!res) return;
  moveDetailDirty = false;
  const msg = document.getElementById('md-saved-msg');
  msg.style.display = 'inline';
  setTimeout(() => { msg.style.display = 'none'; }, 1800);
  await loadAll();
}

function resetMoveDetail() {
  if (currentMoveId !== null) openMoveDetail(currentMoveId);
}

async function markPracticed(id) {
  const t = tricks.find(x => x.id === id);
  if (t && t.last_practiced !== todayLocal()) {
    // Optimistic: bump locally so the card updates instantly. The server
    // dedupes silently if today already has a synthetic session.
    t.practice_count = (t.practice_count || 0) + 1;
    t.last_practiced = todayLocal();
    updateAll();
  }
  await api('POST', '/tricks/' + id + '/practiced');
  await loadAll();
}

async function deleteTrick(id) {
  if (!await appConfirm('Delete this trick? You can restore it from Settings → Recently Deleted.')) return;
  await api('DELETE', '/tricks/' + id);
  await loadAll();
}

const statusBadgeClass = {
  learning: 'level-learning', drilling: 'level-drilling',
  performance: 'level-performance', retired: 'level-retired'
};

function trickCardHTML(t, showActions) {
  const badgeClass = statusBadgeClass[t.status] || 'level-learning';
  const safeLink = safeUrl(t.link);
  const movesTags = t.moves_used
    ? t.moves_used.split(',').map(m => `<span class="tag">${escapeHTML(m.trim())}</span>`).join('')
    : '';
  const practicedMeta = t.last_practiced
    ? `<span class="item-practiced">Last practiced: ${escapeHTML(t.last_practiced)}</span>`
    : '<span class="item-practiced">Never practiced</span>';
  const count = Number(t.practice_count) || 0;
  // On the main library, the card body itself navigates to the detail page.
  // Action buttons stop propagation so they don't double-fire.
  const cardClass = showActions ? 'item-card is-clickable' : 'item-card';
  const cardClick = showActions ? `onclick="openTrickDetail(${t.id})"` : '';
  const stop = 'onclick="event.stopPropagation();';
  const methodLetter = METHOD_LETTER[t.method] || '';
  const methodName   = METHOD_NAME[t.method]   || '';
  const methodBadge  = methodLetter
    ? `<span class="method-badge method-${t.method}" title="${escapeHTML(methodName)}">${methodLetter}</span>`
    : '';
  const diffLetter = DIFF_LETTER[t.difficulty] || '';
  const diffName   = DIFF_NAME[t.difficulty]   || '';
  const diffBadge  = diffLetter
    ? `<span class="diff-badge diff-${t.difficulty}" title="${escapeHTML(diffName)}">${diffLetter}</span>`
    : '';
  return `<div class="${cardClass}" ${cardClick}>
    <div class="item-header">
      ${diffBadge}
      <div class="item-name">${escapeHTML(t.name)}</div>
      ${methodBadge}
      <div class="item-category">${escapeHTML(t.type)}</div>
      <span class="level-badge ${badgeClass}">${escapeHTML(t.status)}</span>
    </div>
    <div class="item-meta">
      <span>Rating: <span style="color:var(--accent)">${renderStars(t.rating)}</span></span>
      ${t.source ? `<span>✍ ${escapeHTML(t.source)}</span>` : ''}
      ${practicedMeta}
      <span class="practice-count" title="Total times practised">${count}× practised</span>
    </div>
    ${movesTags ? `<div style="margin-top:6px">${movesTags}</div>` : ''}
    ${showActions ? `<div class="item-actions">
      ${safeLink ? `<a href="${escapeHTML(safeLink)}" target="_blank" rel="noopener noreferrer" class="item-link btn btn-sm" onclick="event.stopPropagation()">▶ Tutorial</a>` : ''}
      <button class="btn btn-sm" ${stop}showTrickHistory(${t.id})">History</button>
      <button class="btn btn-sm" ${stop}editTrick(${t.id})">Edit</button>
      <button class="btn btn-sm btn-danger" ${stop}deleteTrick(${t.id})">Delete</button>
    </div>` : ''}
  </div>`;
}

function renderTricks(containerId, list) {
  const target = document.getElementById(containerId);
  if (!target) return;
  if (!list.length) {
    target.innerHTML = '<div style="color:var(--text3);font-size:12px;padding:10px 0">No tricks tracked yet.</div>';
    if (containerId === 'tricks-list') buildAlphaIndex([]);
    return;
  }
  const showActions = containerId === 'tricks-list';
  if (!showActions) {
    target.innerHTML = list.map(t => trickCardHTML(t, false)).join('');
    return;
  }
  // Alphabetical grouped render for the main tricks page
  const sorted = [...list].sort((a, b) => a.name.localeCompare(b.name));
  const groups = {};
  sorted.forEach(t => {
    const letter = t.name[0].toUpperCase();
    if (!groups[letter]) groups[letter] = [];
    groups[letter].push(t);
  });
  let html = '';
  Object.keys(groups).sort().forEach(letter => {
    html += `<div class="tricks-letter-heading" id="tricks-letter-${letter}">${letter}</div>`;
    html += groups[letter].map(t => trickCardHTML(t, true)).join('');
  });
  target.innerHTML = html;
  buildAlphaIndex(Object.keys(groups));
}

function buildAlphaIndex(activeLetters) {
  buildAlphaIndexFor(activeLetters, 'tricks-alpha-index', 'tricks-letter');
}

function filterTricks() {
  const q = document.getElementById('tricks-search').value.trim().toLowerCase();
  const filtered = q ? tricks.filter(t => t.name.toLowerCase().includes(q) || (t.type || '').toLowerCase().includes(q) || (t.notes || '').toLowerCase().includes(q)) : tricks;
  renderTricks('tricks-list', filtered);
  if (q && filtered.length === 0) {
    document.getElementById('tricks-list').innerHTML = `<div class="tricks-no-results">No tricks match "<strong>${escapeHTML(q)}</strong>"</div>`;
    buildAlphaIndex([]);
  }
}

// ---- DASHBOARD RENDER ----
function buildChart(data) {
  const chart = document.getElementById('dash-chart');
  if (!chart || !data) return;
  const max = Math.max(...data.map(d => d.count), 1);
  chart.innerHTML = data.map((d, i) => {
    const h = d.count ? Math.max(8, Math.round((d.count / max) * 56)) : 4;
    const isToday = i === data.length - 1;
    return `<div class="chart-bar ${d.count>0?'has-data':''} ${isToday?'today':''}" style="height:${h}px" title="${escapeHTML(d.date + ': ' + d.count + ' session(s)')}"></div>`;
  }).join('');
}

// ---- HISTORY MODAL ----
async function showMoveHistory(id) {
  const data = await api('GET', `/moves/${id}/history`);
  if (!data) return;
  _renderHistory(data, 'Sleight');
}

async function showTrickHistory(id) {
  const data = await api('GET', `/tricks/${id}/history`);
  if (!data) return;
  _renderHistory(data, 'Trick');
}

function _renderHistory(data, kind) {
  const item = data.item;
  const title = `${escapeHTML(item.name)} — ${kind} history`;
  document.getElementById('hist-title').innerHTML = title;
  const sessions = data.sessions || [];
  const totalMins = sessions.reduce((acc, s) => acc + (s.duration_mins || 0), 0);
  const summary = `
    <div style="display:flex;gap:18px;margin-bottom:14px;font-size:12px;color:var(--text2)">
      <span><strong style="color:var(--text)">${sessions.length}</strong> session${sessions.length===1?'':'s'}</span>
      <span><strong style="color:var(--text)">${totalMins}</strong> min total</span>
      ${item.last_practiced ? `<span>Last: <strong style="color:var(--text)">${escapeHTML(item.last_practiced)}</strong></span>` : ''}
    </div>`;
  const sparkline = _historySparkline(sessions);
  const list = sessions.length
    ? sessions.map(s => `
        <div class="session-item" onclick="closeModal('modal-history');viewSession(${s.id})">
          <div class="session-date">
            <div class="day">${new Date(s.date+'T12:00:00').getDate()}</div>
            <div class="month">${new Date(s.date+'T12:00:00').toLocaleString('default',{month:'short'})}</div>
          </div>
          <div class="session-info">
            <div class="title">${escapeHTML(s.title)}</div>
            <div class="meta">${s.duration_mins ? `<span>◷ ${s.duration_mins} min</span>` : ''}</div>
          </div>
          <div class="session-rating">${renderStars(s.rating)}</div>
        </div>`).join('')
    : '<div style="color:var(--text3);font-size:12px;padding:12px 0">No sessions logged for this item yet.</div>';
  document.getElementById('hist-body').innerHTML = summary + sparkline + list;
  document.getElementById('modal-history').classList.add('open');
}

function _historySparkline(sessions) {
  // 12 weekly bars, most recent on the right.
  if (!sessions.length) return '';
  const today = new Date();
  const weeks = Array.from({length: 12}, (_, i) => {
    const end = new Date(today);
    end.setDate(today.getDate() - i*7);
    const start = new Date(end);
    start.setDate(end.getDate() - 6);
    return { start, end, count: 0 };
  });
  sessions.forEach(s => {
    const d = new Date(s.date + 'T12:00:00');
    const w = weeks.find(w => d >= w.start && d <= w.end);
    if (w) w.count++;
  });
  weeks.reverse();
  const max = Math.max(...weeks.map(w => w.count), 1);
  const bars = weeks.map(w => {
    const h = w.count ? Math.max(6, Math.round((w.count/max)*40)) : 3;
    return `<div class="chart-bar ${w.count>0?'has-data':''}" style="height:${h}px" title="${w.start.toISOString().slice(0,10)} – ${w.end.toISOString().slice(0,10)}: ${w.count}"></div>`;
  }).join('');
  return `<div style="font-size:10px;letter-spacing:.08em;text-transform:uppercase;color:var(--text3);margin-bottom:6px">Weekly practice (last 12 weeks)</div>
          <div class="chart" style="margin-bottom:14px">${bars}</div>`;
}

// ---- TRASH ----
async function refreshTrash() {
  const target = document.getElementById('trash-list');
  if (!target) return;
  const data = await api('GET', '/trash');
  if (!data) return;
  const items = [];
  data.sessions.forEach(s => items.push({ kind: 'session', label: `${s.date} — ${s.title}`, id: s.id }));
  data.moves.forEach(m   => items.push({ kind: 'move',    label: `${m.name} (${m.category})`, id: m.id }));
  data.tricks.forEach(t  => items.push({ kind: 'trick',   label: `${t.name} (${t.type})`, id: t.id }));
  if (!items.length) {
    target.innerHTML = '<div style="color:var(--text3);font-size:12px;padding:8px 0">Nothing in the trash. Deleted items appear here.</div>';
    return;
  }
  target.innerHTML = items.map(it => `
    <div class="trash-row" style="display:flex;align-items:center;gap:10px;padding:8px 12px;border:1px solid var(--border);border-radius:6px">
      <span style="flex:1;font-size:12px"><span style="color:var(--text3);text-transform:uppercase;font-size:10px;letter-spacing:.08em;margin-right:8px">${it.kind}</span>${escapeHTML(it.label)}</span>
      <button class="btn btn-sm" onclick="restoreTrashed('${it.kind}', ${it.id})">Restore</button>
      <button class="btn btn-sm btn-danger" onclick="purgeTrashed('${it.kind}', ${it.id})">Remove forever</button>
    </div>`).join('');
}

const TRASH_PATHS = {
  session: { restore: id => `/sessions/${id}/restore`, purge: null },
  move:    { restore: id => `/moves/${id}/restore`,    purge: id => `/moves/${id}/purge` },
  trick:   { restore: id => `/tricks/${id}/restore`,   purge: id => `/tricks/${id}/purge` },
};

async function restoreTrashed(kind, id) {
  const path = TRASH_PATHS[kind].restore(id);
  await api('POST', path);
  await refreshTrash();
  await loadAll();
}

async function purgeTrashed(kind, id) {
  if (kind === 'session') {
    alert('Sessions in the trash are kept indefinitely so practice history stays intact. To clear them, delete the underlying database manually.');
    return;
  }
  if (!await appConfirm('Permanently remove this from the database? This cannot be undone.', { okLabel: 'Remove forever' })) return;
  const path = TRASH_PATHS[kind].purge(id);
  await api('DELETE', path);
  await refreshTrash();
  await loadAll();
}

// ---- SETTINGS ----
async function saveBrushUpDays() {
  const val = parseInt(document.getElementById('setting-brushup-days').value);
  if (!val || val < 1) return;
  await api('POST', '/settings', { key: 'brush_up_days', value: val });
  const msg = document.getElementById('setting-saved-msg');
  msg.style.display = 'inline';
  setTimeout(() => { msg.style.display = 'none'; }, 2000);
  // Only the dashboard cutoff and brush-up list are affected — skip the full
  // sessions/moves/tricks reload.
  const [d, st] = await Promise.all([api('GET', '/dashboard'), api('GET', '/settings')]);
  dashData = d || {};
  settings = st || {};
  updateAll();
}

// ---- UPDATE ALL ----
function updateAll() {
  const d = dashData;

  // Header pills
  document.getElementById('hdr-sessions').textContent = sessions.length;
  document.getElementById('hdr-moves').textContent    = moves.length;
  document.getElementById('hdr-tricks').textContent   = tricks.length;
  document.getElementById('hdr-hours').textContent    = (d.total_hours || 0) + 'h';

  // Nav badges
  document.getElementById('nav-sessions-count').textContent = sessions.length;
  document.getElementById('nav-moves-count').textContent    = moves.length;
  document.getElementById('nav-tricks-count').textContent   = tricks.length;

  // Dashboard stat cards
  document.getElementById('dash-sessions').textContent   = d.total_sessions || 0;
  document.getElementById('dash-hours').textContent      = d.total_hours    || 0;
  document.getElementById('dash-moves').textContent      = d.total_moves    || 0;
  document.getElementById('dash-tricks').textContent     = d.total_tricks   || 0;
  document.getElementById('dash-last-session').textContent = d.last_session_date ? 'Last: ' + formatDate(d.last_session_date) : 'No sessions yet';
  document.getElementById('dash-avg-session').textContent  = d.avg_mins ? d.avg_mins + ' min avg per session' : '— avg per session';
  document.getElementById('dash-moves-perf').textContent   = (d.perf_moves || 0) + ' performance ready';
  document.getElementById('dash-tricks-perf').textContent  = (d.perf_tricks || 0) + ' performance ready';

  // Page labels
  document.getElementById('sessions-count-label').textContent = sessions.length + ' session' + (sessions.length!==1?'s':'');
  document.getElementById('moves-count-label').textContent    = moves.length + ' sleight' + (moves.length!==1?'s':'');
  document.getElementById('tricks-count-label').textContent   = tricks.length + ' trick' + (tricks.length!==1?'s':'');

  // Render lists
  renderSessions(sessions, 'dash-recent-sessions', 3);
  renderSessions(sessions, 'sessions-list', 0);
  renderMoves('dash-moves-list', d.moves_needing_work || []);
  renderMoves('moves-list', moves);
  renderTricks('dash-tricks-list', d.tricks_in_progress || []);
  renderTricks('tricks-list', tricks);
  buildChart(d.thirty_days);
  updateFreqStats(d.thirty_days);
}

// ---- HEADER CLOCK ----
function tickClock() {
  const now = new Date();
  const t = document.getElementById('hdr-time');
  const dEl = document.getElementById('hdr-date');
  if (!t || !dEl) return;
  const hh = String(now.getHours()).padStart(2, '0');
  const mm = String(now.getMinutes()).padStart(2, '0');
  t.textContent = `${hh}:${mm}`;
  dEl.textContent = now.toLocaleDateString('en-US', { weekday: 'short', day: 'numeric', month: 'short' });
}

// ---- PRACTICE FREQUENCY STATS ----
function updateFreqStats(thirtyDays) {
  const el = id => document.getElementById(id);
  if (!el('freq-week')) return;
  const data = Array.isArray(thirtyDays) ? thirtyDays : [];
  const ids = ['freq-week','freq-month','freq-streak','freq-min-day','freq-min-month','freq-best'];
  if (!data.length) {
    ids.forEach(i => { el(i).textContent = '0'; });
    return;
  }
  const total    = data.reduce((acc, d) => acc + (d.count   || 0), 0);
  const totalMin = data.reduce((acc, d) => acc + (d.minutes || 0), 0);
  const weekAvg  = (total    / (data.length / 7)).toFixed(1).replace(/\.0$/, '');
  const minDay   = (totalMin / data.length     ).toFixed(1).replace(/\.0$/, '');
  // Streak: count back from today through consecutive days with at least 1 session.
  let streak = 0;
  for (let i = data.length - 1; i >= 0; i--) {
    if ((data[i].count || 0) > 0) streak++;
    else break;
  }
  const best = data.reduce((m, d) => Math.max(m, d.count || 0), 0);
  el('freq-week').textContent      = weekAvg;
  el('freq-month').textContent     = total;
  el('freq-streak').textContent    = streak;
  el('freq-min-day').textContent   = minDay;
  el('freq-min-month').textContent = totalMin;
  el('freq-best').textContent      = best;
}

// ---- MODAL SESSION TIMER ----
let msInterval = null, msSecs = 0, msState = 'idle';

function msFmt(s) { const p = n => String(n).padStart(2,'0'); return `${p(Math.floor(s/3600))}:${p(Math.floor((s%3600)/60))}:${p(s%60)}`; }

function msSetUI(state) {
  msState = state;
  const d = document.getElementById('modal-timer-display');
  const st = document.getElementById('modal-timer-status');
  if (!d) return;
  document.getElementById('ms-start-btn').style.display  = state==='idle'    ? '' : 'none';
  document.getElementById('ms-pause-btn').style.display  = state==='running' ? '' : 'none';
  document.getElementById('ms-resume-btn').style.display = state==='paused'  ? '' : 'none';
  document.getElementById('ms-stop-btn').style.display   = (state==='running'||state==='paused') ? '' : 'none';
  const labels = { idle:'Ready', running:'Practicing…', paused:'Paused', stopped:'Done — duration filled in' };
  const colors = { idle:'var(--text3)', running:'var(--green)', paused:'var(--accent)', stopped:'var(--green)' };
  st.textContent = labels[state] || '';
  st.style.color = colors[state] || 'var(--text3)';
  d.style.color = state==='paused' ? 'var(--text2)' : 'var(--accent)';
}

function msReset() { clearInterval(msInterval); msSecs=0; msState='idle'; const d=document.getElementById('modal-timer-display'); if(d) d.textContent='00:00:00'; msSetUI('idle'); }
function msStart()  { if(msState!=='idle') return; msInterval=setInterval(()=>{ msSecs++; const d=document.getElementById('modal-timer-display'); if(d) d.textContent=msFmt(msSecs); },1000); msSetUI('running'); }
function msPause()  { if(msState!=='running') return; clearInterval(msInterval); msSetUI('paused'); }
function msResume() { if(msState!=='paused') return; msInterval=setInterval(()=>{ msSecs++; const d=document.getElementById('modal-timer-display'); if(d) d.textContent=msFmt(msSecs); },1000); msSetUI('running'); }
function msStop()   { if(msState!=='running'&&msState!=='paused') return; clearInterval(msInterval); document.getElementById('s-duration').value=Math.max(1,Math.round(msSecs/60)); msSetUI('stopped'); }

// ---- STANDALONE TIMER ----
let timerInterval = null, timerSeconds = 0, timerState = 'idle';

function timerFmt(s) { const p=n=>String(n).padStart(2,'0'); return `${p(Math.floor(s/3600))}:${p(Math.floor((s%3600)/60))}:${p(s%60)}`; }

function timerSetUI(state) {
  timerState = state;
  document.getElementById('timer-start-btn').style.display  = state==='idle'    ? '' : 'none';
  document.getElementById('timer-pause-btn').style.display  = state==='running' ? '' : 'none';
  document.getElementById('timer-resume-btn').style.display = state==='paused'  ? '' : 'none';
  document.getElementById('timer-stop-btn').style.display   = (state==='running'||state==='paused') ? '' : 'none';
  document.getElementById('timer-log-area').style.display   = state==='stopped' ? '' : 'none';
  const labels = { idle:'Ready', running:'Practicing…', paused:'Paused', stopped:'Session complete' };
  const colors = { idle:'var(--text3)', running:'var(--green)', paused:'var(--accent)', stopped:'var(--red)' };
  const lbl = document.getElementById('timer-status-label');
  lbl.textContent = labels[state] || '';
  lbl.style.color = colors[state] || 'var(--text3)';
  document.getElementById('timer-display').style.color = state==='paused' ? 'var(--text2)' : 'var(--accent)';
}

function timerStart()  { if(timerState!=='idle') return; timerInterval=setInterval(()=>{ timerSeconds++; document.getElementById('timer-display').textContent=timerFmt(timerSeconds); },1000); timerSetUI('running'); }
function timerPause()  { if(timerState!=='running') return; clearInterval(timerInterval); timerSetUI('paused'); }
function timerResume() { if(timerState!=='paused') return; timerInterval=setInterval(()=>{ timerSeconds++; document.getElementById('timer-display').textContent=timerFmt(timerSeconds); },1000); timerSetUI('running'); }
function timerStop()   { if(timerState!=='running'&&timerState!=='paused') return; clearInterval(timerInterval); const mins=Math.max(1,Math.round(timerSeconds/60)); document.getElementById('timer-stopped-msg').textContent=`Recorded: ${timerFmt(timerSeconds)} (${mins} min). Add a name and log it.`; timerSetUI('stopped'); }
function timerReset()  { clearInterval(timerInterval); timerSeconds=0; document.getElementById('timer-display').textContent='00:00:00'; timerSetUI('idle'); }

async function logTimerSession() {
  const name = document.getElementById('timer-session-name').value.trim() || 'Practice Session';
  const dur  = Math.max(1, Math.round(timerSeconds / 60));
  await api('POST', '/sessions', { date: todayLocal(), duration: dur, title: name, notes: 'Logged via timer.' });
  document.getElementById('timer-session-name').value = '';
  timerReset();
  await loadAll();
  alert(`Session logged: "${name}" — ${dur} minutes`);
}

// ---- INIT ----
tickClock();
setInterval(tickClock, 30 * 1000);
loadAll();
