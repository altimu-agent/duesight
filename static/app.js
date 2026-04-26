const $ = (id) => document.getElementById(id);
const form = $('analyze-form');
const submitBtn = $('submit-btn');

let lastReport = '';
let lastCompany = '';
let elapsedTimer = null;
let elapsedStart = 0;
let stepCount = 0;

/* Preset chips ───────────────────────────────────────────── */
document.querySelectorAll('.preset-chip').forEach((chip) => {
  chip.addEventListener('click', () => {
    const data = JSON.parse(chip.dataset.preset);
    for (const [k, v] of Object.entries(data)) {
      const input = form.querySelector(`[name="${k}"]`);
      if (input) input.value = v;
    }
    form.querySelector('[name="company"]').focus();
  });
});

/* Show-more toggle for advanced fields ───────────────────── */
$('toggle-advanced').addEventListener('click', () => {
  const fields = $('advanced-fields');
  const btn = $('toggle-advanced');
  const isHidden = fields.classList.toggle('hidden');
  btn.classList.toggle('expanded', !isHidden);
  $('toggle-advanced-label').textContent = isHidden ? 'Show more details' : 'Hide details';
});

/* Elapsed timer ──────────────────────────────────────────── */
function fmtElapsed(ms) {
  const s = Math.floor(ms / 1000);
  return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, '0')}`;
}
function startElapsed() {
  stopElapsed();
  elapsedStart = Date.now();
  elapsedTimer = setInterval(() => {
    $('status-elapsed').textContent = fmtElapsed(Date.now() - elapsedStart);
  }, 500);
}
function stopElapsed() {
  if (elapsedTimer) { clearInterval(elapsedTimer); elapsedTimer = null; }
}

/* Helpers ────────────────────────────────────────────────── */
function esc(s) {
  return String(s ?? '').replace(/[&<>"']/g, (c) => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
  }[c]));
}
function slug(name) {
  return (name || lastCompany || 'report')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '') || 'report';
}

/* Comparison strip ───────────────────────────────────────── */
function appendPrimaryCard(company, website) {
  const cards = $('comparison-cards');
  cards.innerHTML = '';
  const card = document.createElement('div');
  card.className = 'border border-emerald-500/60 bg-emerald-500/5 rounded-lg p-3';
  card.innerHTML = `
    <div class="text-[10px] uppercase tracking-wider text-emerald-400 mb-1">Primary</div>
    <div class="font-semibold text-sm truncate" title="${esc(company)}">${esc(company)}</div>
    <div class="text-[11px] text-slate-400 truncate">${esc(website || ' ')}</div>
  `;
  cards.appendChild(card);
  $('comparison-section').classList.remove('hidden');
}
function appendDiscoveringPlaceholders(n = 3) {
  const cards = $('comparison-cards');
  for (let i = 0; i < n; i++) {
    const card = document.createElement('div');
    card.className = 'placeholder-card border border-slate-800 bg-slate-900/30 rounded-lg p-3 animate-pulse';
    card.innerHTML = `
      <div class="text-[10px] uppercase tracking-wider text-slate-600 mb-1">Discovering…</div>
      <div class="h-4 bg-slate-800 rounded w-3/4 mb-1.5"></div>
      <div class="h-3 bg-slate-800 rounded w-full"></div>
    `;
    cards.appendChild(card);
  }
}
function clearPlaceholders() {
  document.querySelectorAll('.placeholder-card').forEach((el) => el.remove());
}
function appendCompetitorCard({ name, tagline = '' }) {
  const cards = $('comparison-cards');
  const card = document.createElement('div');
  card.className = 'competitor-card relative border border-slate-800 bg-slate-900/30 rounded-lg p-3 transition';
  card.dataset.name = name;
  card.innerHTML = `
    <button class="dismiss-btn hidden absolute top-1.5 right-1.5 w-5 h-5 rounded text-slate-500 hover:text-red-400 hover:bg-red-500/10 transition flex items-center justify-center text-sm leading-none" title="Dismiss this competitor" type="button">×</button>
    <div class="text-[10px] uppercase tracking-wider text-slate-500 mb-1">Competitor</div>
    <div class="font-semibold text-sm truncate" title="${esc(name)}">${esc(name)}</div>
    <div class="text-[11px] text-slate-400 line-clamp-2 leading-snug">${esc(tagline || ' ')}</div>
  `;
  card.querySelector('.dismiss-btn').addEventListener('click', () => {
    card.classList.add('opacity-0', 'scale-95');
    setTimeout(() => card.remove(), 180);
  });
  cards.appendChild(card);
}
function enableDismissButtons() {
  document.querySelectorAll('.dismiss-btn').forEach((b) => b.classList.remove('hidden'));
  $('dismiss-hint').classList.remove('hidden');
}

/* Live status — task panel ───────────────────────────────── */
const PHASE_LABELS = {
  init: 'Initializing research',
  researching: 'Researching',
  summarizing: 'Summarizing',
  done: 'Report ready',
  error: 'Error',
};

function setPhase(phase, detail = '') {
  $('task-name').textContent = PHASE_LABELS[phase] || phase;
  $('task-detail').textContent = detail;
  const orb = $('task-orb');
  orb.classList.remove('done', 'error', 'summarizing');
  if (phase === 'done') orb.classList.add('done');
  else if (phase === 'error') orb.classList.add('error');
  else if (phase === 'summarizing') orb.classList.add('summarizing');
}

function setTaskState(state) {
  const orb = $('task-orb');
  orb.classList.remove('done', 'error');
  if (state !== 'working') orb.classList.add(state);
}

/* Research progress cards ────────────────────────────────── */
const DIMENSIONS = [
  { key: 'company',     label: 'Company & people' },
  { key: 'competitors', label: 'Competitors' },
  { key: 'website',     label: 'Website' },
  { key: 'financials',  label: 'Financials' },
  { key: 'trust',       label: 'Legal & trust' },
];

function initResearchGrid() {
  const grid = $('research-grid');
  grid.innerHTML = '';
  for (const d of DIMENSIONS) {
    const card = document.createElement('div');
    card.className = 'dim-card';
    card.dataset.key = d.key;
    card.dataset.state = 'pending';
    card.innerHTML = `
      <div class="dim-status"></div>
      <div class="dim-label">${esc(d.label)}</div>
      <div class="dim-summary">Awaiting…</div>
    `;
    grid.appendChild(card);
  }
  $('research-section').classList.remove('hidden');
  updateResearchCounter();
}

function updateDimCard(key, state, summary) {
  const card = document.querySelector(`.dim-card[data-key="${key}"]`);
  if (!card) return;
  card.dataset.state = state;
  if (state === 'running') {
    card.querySelector('.dim-summary').textContent = 'Researching…';
  } else if (summary) {
    card.querySelector('.dim-summary').textContent = summary;
  }
  card.querySelector('.dim-status').textContent =
    state === 'ok' ? '✓' : state === 'timeout' ? '!' : state === 'error' ? '✕' : '';
  updateResearchCounter();
}

function updateResearchCounter() {
  const cards = document.querySelectorAll('.dim-card');
  const done = [...cards].filter((c) =>
    ['ok', 'timeout', 'error'].includes(c.dataset.state)
  ).length;
  $('research-counter').textContent = `${done} of ${cards.length} done`;
}

/* Streaming chunk renderer (throttled to one rAF per chunk) ─ */
const chunkBuffers = {};
const chunkPending = {};

function appendChunkText(key, text) {
  if (!chunkBuffers[key]) chunkBuffers[key] = '';
  chunkBuffers[key] += text;
  if (chunkPending[key]) return;
  chunkPending[key] = requestAnimationFrame(() => {
    const el = document.querySelector(`.streaming-chunk[data-chunk="${key}"]`);
    if (el) el.innerHTML = marked.parse(chunkBuffers[key]);
    chunkPending[key] = null;
  });
}

function setChunkState(key, state) {
  const el = document.querySelector(`.streaming-chunk[data-chunk="${key}"]`);
  if (el) el.dataset.state = state;
}

const CHUNK_KEYS = ['snapshot_competitive', 'website_growth', 'due_diligence'];

function resetChunks() {
  for (const k of Object.keys(chunkBuffers)) delete chunkBuffers[k];
  const reportEl = $('report');
  // Self-heal: renderReport may have flattened the chunk divs into a single
  // markdown blob on the previous run.
  if (!reportEl.querySelector('.streaming-chunk')) {
    reportEl.innerHTML = '';
    for (const k of CHUNK_KEYS) {
      const div = document.createElement('div');
      div.className = 'streaming-chunk';
      div.dataset.chunk = k;
      div.dataset.state = 'pending';
      reportEl.appendChild(div);
    }
  } else {
    reportEl.querySelectorAll('.streaming-chunk').forEach((el) => {
      el.dataset.state = 'pending';
      el.innerHTML = '';
    });
  }
}
function showAlert(message) {
  const row = $('alerts-row');
  row.textContent = message;
  row.classList.add('visible');
}
function clearAlert() {
  $('alerts-row').classList.remove('visible');
  $('alerts-row').textContent = '';
}

/* Risk + verdict badges ──────────────────────────────────── */
function applyBadges(markdown) {
  const m = markdown.match(/"risk_score"\s*:\s*(\d+)/);
  const lm = markdown.match(/"risk_level"\s*:\s*"([^"]+)"/);
  const vm = markdown.match(/"verdict"\s*:\s*"([^"]+)"/);

  if (m) $('risk-score').textContent = m[1];
  if (lm) {
    const level = lm[1].trim();
    const lEl = $('risk-level');
    lEl.textContent = level;
    const palette = {
      LOW:      { text: 'text-emerald-400', card: 'border-emerald-500/40 bg-emerald-500/5', bar: 'bg-emerald-500' },
      MEDIUM:   { text: 'text-amber-400',   card: 'border-amber-500/40 bg-amber-500/5',     bar: 'bg-amber-500' },
      HIGH:     { text: 'text-orange-400',  card: 'border-orange-500/40 bg-orange-500/5',   bar: 'bg-orange-500' },
      CRITICAL: { text: 'text-red-400',     card: 'border-red-500/40 bg-red-500/5',         bar: 'bg-red-500' },
    }[level] || { text: 'text-slate-300', card: 'border-slate-800', bar: 'bg-slate-600' };
    lEl.className = `text-sm font-semibold pb-1 ${palette.text}`;
    $('risk-card').className = `rounded-xl p-5 transition border ${palette.card}`;
    if (m) {
      const bar = $('risk-bar');
      bar.className = `risk-bar-fill h-full ${palette.bar}`;
      bar.style.width = `${Math.min(100, Math.max(0, parseInt(m[1], 10)))}%`;
    }
  }
  if (vm) {
    const verdict = vm[1].trim();
    const vEl = $('verdict');
    vEl.textContent = verdict;
    const palette = {
      APPROVED:    { text: 'text-emerald-400', card: 'border-emerald-500/40 bg-emerald-500/5' },
      CONDITIONAL: { text: 'text-amber-400',   card: 'border-amber-500/40 bg-amber-500/5' },
      REJECTED:    { text: 'text-red-400',     card: 'border-red-500/40 bg-red-500/5' },
    }[verdict] || { text: 'text-slate-300', card: 'border-slate-800' };
    vEl.className = `text-3xl font-bold ${palette.text}`;
    $('verdict-card').className = `rounded-xl p-5 transition border ${palette.card}`;
  }

  $('badges-section').classList.remove('hidden');
}

/* Summary extraction ─────────────────────────────────────── */
function extractJSON(markdown) {
  const m = markdown.match(/```json\s*\n([\s\S]+?)\n```/);
  if (!m) return null;
  try { return JSON.parse(m[1]); } catch { return null; }
}
function extractRevenueLeaks(markdown) {
  const sec5 = markdown.match(/##\s*5\..*?(?=##\s*6\.|$)/s);
  if (!sec5) return [];
  return [...sec5[0].matchAll(/###\s*Leak\s*\d+:\s*(.+)/g)].map((x) => x[1].trim());
}

function renderSummary(markdown) {
  const data = extractJSON(markdown);
  const summary = data?.summary || '';
  const flags = [
    ...(data?.sections?.financial_health?.red_flags || []),
    ...(data?.sections?.legal_compliance?.red_flags || []),
    ...(data?.sections?.reputation?.red_flags || []),
  ].filter(Boolean).slice(0, 5);
  const conditions = (data?.sections?.recommendation?.conditions || []).filter(Boolean).slice(0, 4);
  const leaks = extractRevenueLeaks(markdown).slice(0, 3);

  $('summary-text').textContent = summary || 'Summary unavailable — see full report below.';

  const flagsList = $('summary-flags');
  flagsList.innerHTML = '';
  if (flags.length === 0) {
    flagsList.innerHTML = '<div class="finding-item">No major red flags surfaced.</div>';
  } else {
    for (const f of flags) {
      const div = document.createElement('div');
      div.className = 'finding-item flag';
      div.textContent = f;
      flagsList.appendChild(div);
    }
  }

  const leaksList = $('summary-leaks');
  leaksList.innerHTML = '';
  if (leaks.length === 0 && conditions.length === 0) {
    leaksList.innerHTML = '<div class="finding-item">No revenue leaks identified.</div>';
  } else {
    for (const l of leaks) {
      const div = document.createElement('div');
      div.className = 'finding-item leak';
      div.textContent = l;
      leaksList.appendChild(div);
    }
    for (const c of conditions) {
      const div = document.createElement('div');
      div.className = 'finding-item';
      div.textContent = `Condition: ${c}`;
      leaksList.appendChild(div);
    }
  }

  $('summary-section').classList.remove('hidden');
}

/* Full report disclosure toggle ──────────────────────────── */
$('disclosure-toggle').addEventListener('click', () => {
  const btn = $('disclosure-toggle');
  const wrapper = $('report-wrapper');
  const expanded = wrapper.classList.toggle('hidden') === false;
  btn.classList.toggle('expanded', expanded);
  $('disclosure-label').textContent = expanded ? 'Hide full report' : 'View full report';
});

function renderReport(markdown) {
  lastReport = markdown;
  $('report').innerHTML = marked.parse(markdown);
  $('report-section').classList.remove('hidden');
  applyBadges(markdown);
  renderSummary(markdown);
  $('summary-section').scrollIntoView({ behavior: 'smooth', block: 'start' });
}

/* SSE event handler ──────────────────────────────────────── */
function handleEvent(event) {
  const t = event.type;
  if (t === 'competitors_discovered') {
    clearPlaceholders();
    for (const c of event.competitors || []) appendCompetitorCard(c);

  } else if (t === 'dimension_started') {
    setPhase('researching', 'starting parallel research…');
    updateDimCard(event.dimension, 'running');

  } else if (t === 'dimension_completed') {
    updateDimCard(event.dimension, event.status === 'ok' ? 'ok' : event.status, event.summary_preview);
    const done = document.querySelectorAll('.dim-card[data-state="ok"], .dim-card[data-state="timeout"], .dim-card[data-state="error"]').length;
    setPhase('researching', `${done} of ${DIMENSIONS.length} dimensions done`);

  } else if (t === 'dimension_timeout') {
    updateDimCard(event.dimension, 'timeout', `Timed out after ${event.elapsed_s}s.`);

  } else if (t === 'tool_call') {
    stepCount = event.step || stepCount + 1;
    $('status-step').textContent = stepCount;
    // Don't override the phase label; dimensions cards show what's happening.

  } else if (t === 'tool_result' || t === 'reduce_chunk_started') {
    if (t === 'reduce_chunk_started') setChunkState(event.chunk, 'streaming');

  } else if (t === 'reduce_started') {
    setPhase('summarizing', 'Generating 9-section report…');
    $('report-section').classList.remove('hidden');
    $('report-wrapper').classList.remove('hidden');
    $('disclosure-toggle').classList.add('expanded');
    $('disclosure-label').textContent = 'Hide full report';
    resetChunks();

  } else if (t === 'reduce_chunk_delta') {
    appendChunkText(event.chunk, event.text);

  } else if (t === 'reduce_chunk_completed') {
    setChunkState(event.chunk, 'done');

  } else if (t === 'reduce_chunk_error') {
    setChunkState(event.chunk, 'error');
    showAlert(`Chunk ${event.chunk} failed: ${event.message}`);

  } else if (t === 'info') {
    showAlert(event.message);

  } else if (t === 'report') {
    setPhase('done', '');
    stopElapsed();
    if (event.score_info?.overrode) {
      showAlert(
        `Score reconciled: table sum=${event.score_info.table_sum} → clamped=${event.score_info.clamped}.`
      );
    }
    // Replace streamed chunks with the final reconciled markdown so badges + summary
    // extraction operate on the canonical content.
    renderReport(event.content);
    enableDismissButtons();

  } else if (t === 'error') {
    setPhase('error', event.message);
    stopElapsed();
    submitBtn.disabled = false;
    submitBtn.textContent = 'Run Analysis →';

  } else if (t === 'done') {
    submitBtn.disabled = false;
    submitBtn.textContent = 'Run Analysis →';
  }
}

/* Form submit ────────────────────────────────────────────── */
form.addEventListener('submit', async (e) => {
  e.preventDefault();
  const fd = new FormData(form);
  const company = (fd.get('company') || '').toString().trim();
  if (!company) return;
  lastCompany = company;
  const competitorsStr = (fd.get('competitors') || '').toString();
  const competitors = competitorsStr.split(',').map((s) => s.trim()).filter(Boolean);
  const body = {
    company,
    website: (fd.get('website') || '').toString().trim() || null,
    industry: (fd.get('industry') || '').toString().trim() || null,
    country: (fd.get('country') || '').toString().trim() || null,
    contract_value: fd.get('contract_value') ? parseInt(fd.get('contract_value'), 10) : null,
    competitors: competitors.length ? competitors : null,
  };

  $('status-section').classList.remove('hidden');
  $('summary-section').classList.add('hidden');
  $('report-section').classList.add('hidden');
  $('badges-section').classList.add('hidden');
  $('dismiss-hint').classList.add('hidden');
  $('report-wrapper').classList.add('hidden');
  $('disclosure-toggle').classList.remove('expanded');
  $('disclosure-label').textContent = 'View full report';
  clearAlert();
  initResearchGrid();
  resetChunks();
  setPhase('init');
  stepCount = 0;
  $('status-step').textContent = '0';
  $('status-elapsed').textContent = '0:00';
  startElapsed();

  appendPrimaryCard(body.company, body.website);
  if (competitors.length) {
    for (const name of competitors) appendCompetitorCard({ name });
  } else {
    appendDiscoveringPlaceholders(3);
  }

  submitBtn.disabled = true;
  submitBtn.textContent = 'Analyzing…';

  try {
    const resp = await fetch('/api/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    if (!resp.ok) {
      const text = await resp.text();
      throw new Error(`HTTP ${resp.status}: ${text}`);
    }

    const reader = resp.body.getReader();
    const decoder = new TextDecoder();
    let buf = '';
    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      buf += decoder.decode(value, { stream: true });
      const parts = buf.split('\n\n');
      buf = parts.pop() || '';
      for (const part of parts) {
        const line = part.trim();
        if (!line.startsWith('data: ')) continue;
        try {
          handleEvent(JSON.parse(line.slice(6)));
        } catch (err) {
          console.warn('bad event payload', line, err);
        }
      }
    }
  } catch (err) {
    setTaskState('error');
    $('task-name').textContent = 'Error';
    $('task-detail').textContent = err.message || String(err);
    stopElapsed();
    submitBtn.disabled = false;
    submitBtn.textContent = 'Run Analysis →';
  }
});

/* Download dropdown ──────────────────────────────────────── */
function downloadFile(content, filename, mime) {
  const blob = new Blob([content], { type: mime });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url; a.download = filename;
  document.body.appendChild(a); a.click(); a.remove();
  URL.revokeObjectURL(url);
}
function downloadMarkdown() {
  if (!lastReport) return;
  downloadFile(lastReport, `${slug()}-duesight.md`, 'text/markdown');
}
function downloadJSON() {
  if (!lastReport) return;
  const data = extractJSON(lastReport);
  if (!data) {
    showAlert('JSON block not found in report.');
    return;
  }
  downloadFile(JSON.stringify(data, null, 2), `${slug()}-duesight.json`, 'application/json');
}
function downloadPDF() {
  if (!lastReport) return;
  const el = $('report');
  el.classList.add('printable');
  const restore = () => el.classList.remove('printable');

  if (typeof html2pdf !== 'undefined') {
    html2pdf()
      .set({
        margin: 0.5,
        filename: `${slug()}-duesight.pdf`,
        html2canvas: { scale: 2, backgroundColor: '#ffffff' },
        jsPDF: { unit: 'in', format: 'letter', orientation: 'portrait' },
        pagebreak: { mode: ['avoid-all', 'css', 'legacy'] },
      })
      .from(el).save()
      .then(restore, restore);
  } else {
    restore();
    window.print();
  }
}

$('download-pdf').addEventListener('click', downloadPDF);
$('download-menu-toggle').addEventListener('click', (e) => {
  e.stopPropagation();
  $('download-menu').classList.toggle('visible');
});
document.addEventListener('click', () => $('download-menu').classList.remove('visible'));
$('download-md').addEventListener('click', () => { downloadMarkdown(); $('download-menu').classList.remove('visible'); });
$('download-json').addEventListener('click', () => { downloadJSON(); $('download-menu').classList.remove('visible'); });

$('reset-btn').addEventListener('click', () => {
  $('summary-section').classList.add('hidden');
  $('report-section').classList.add('hidden');
  $('badges-section').classList.add('hidden');
  $('status-section').classList.add('hidden');
  $('research-section').classList.add('hidden');
  $('comparison-section').classList.add('hidden');
  window.scrollTo({ top: 0, behavior: 'smooth' });
});
