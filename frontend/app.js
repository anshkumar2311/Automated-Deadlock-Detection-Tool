'use strict';

const API_BASE = 'http://localhost:5000/api';

const state = {
  availableResources: [],
  lastResult: null,
  simSteps: [],
  simIndex: 0,
};

const $ = id => document.getElementById(id);

document.addEventListener('DOMContentLoaded', () => {
  addResource();
  addProcess();
  bindNav();
  bindTabs();
});

function bindNav() {
  $('btn-detect')?.addEventListener('click', runDetection);
  $('btn-detect-mobile')?.addEventListener('click', runDetection);
  $('btn-sample')?.addEventListener('click', loadSample);
  $('btn-sample-mobile')?.addEventListener('click', loadSample);
  $('btn-clear')?.addEventListener('click', clearAll);
  $('btn-clear-mobile')?.addEventListener('click', clearAll);
  $('btn-add-resource')?.addEventListener('click', () => addResource());
  $('btn-add-process')?.addEventListener('click', () => addProcess());
  $('btn-simulate')?.addEventListener('click', openSimulation);
  $('btn-report')?.addEventListener('click', downloadReport);
  $('sim-modal-close')?.addEventListener('click', closeSimModal);
  $('sim-prev')?.addEventListener('click', simPrev);
  $('sim-next')?.addEventListener('click', simNext);
}

function bindTabs() {
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => switchTab(btn.dataset.tab));
  });
}

function switchTab(name) {
  document.querySelectorAll('.tab-btn').forEach(b => {
    b.classList.toggle('tab-active', b.dataset.tab === name);
    b.setAttribute('aria-selected', b.dataset.tab === name ? 'true' : 'false');
  });
  document.querySelectorAll('.tab-panel').forEach(p => {
    p.hidden = p.id !== `tab-${name}`;
  });
}

function addResource(data = {}) {
  const container = $('resources-container');
  const row = document.createElement('div');
  row.className = 'resource-row';
  row.innerHTML = `
    <input type="text" class="res-id" placeholder="e.g. R1"
           value="${esc(data.rid || '')}" autocomplete="off" aria-label="Resource ID" />
    <input type="number" class="res-inst" placeholder="1"
           value="${esc(String(data.instances ?? 1))}" min="1" aria-label="Instances" />
    <button class="btn-remove" title="Remove" aria-label="Remove resource">&times;</button>
  `;
  row.querySelector('.btn-remove').addEventListener('click', () => {
    if (container.children.length > 1) { row.remove(); syncResources(); }
    else flashRow(row);
  });
  row.querySelector('.res-id').addEventListener('input', syncResources);
  container.appendChild(row);
  syncResources();
}

function syncResources() {
  const ids = [];
  document.querySelectorAll('#resources-container .res-id').forEach(inp => {
    const v = inp.value.trim();
    if (v) ids.push(v);
  });
  state.availableResources = ids;
  document.querySelectorAll('.multi-select').forEach(ms => ms._refresh && ms._refresh());
}

function addProcess(data = {}) {
  const container = $('processes-container');
  const card = document.createElement('div');
  card.className = 'process-card';
  card.innerHTML = `
    <div class="process-card-header">
      <input type="text" class="proc-pid process-pid-input" placeholder="e.g. P1"
             value="${esc(data.pid || '')}" autocomplete="off" aria-label="Process ID" />
      <button class="btn-remove" title="Remove" aria-label="Remove process">&times;</button>
    </div>
    <div class="process-fields">
      <div class="field-group">
        <label class="field-label">Allocated</label>
        <div class="multi-select" data-field="allocated"></div>
      </div>
      <div class="field-group">
        <label class="field-label">Requested</label>
        <div class="multi-select" data-field="requested"></div>
      </div>
      <div class="field-group">
        <label class="field-label">Max Need</label>
        <div class="multi-select" data-field="max_need"></div>
      </div>
    </div>
  `;
  card.querySelector('.btn-remove').addEventListener('click', () => {
    if (container.children.length > 1) card.remove();
    else flashRow(card);
  });
  container.appendChild(card);

  initMultiSelect(card.querySelector('[data-field="allocated"]'), data.allocated || []);
  initMultiSelect(card.querySelector('[data-field="requested"]'), data.requested || []);
  initMultiSelect(card.querySelector('[data-field="max_need"]'), data.max_need || []);
}

function initMultiSelect(container, initial = []) {
  const selected = new Set(initial);

  const trigger = document.createElement('div');
  trigger.className = 'ms-trigger';
  trigger.setAttribute('tabindex', '0');
  trigger.setAttribute('role', 'button');
  trigger.innerHTML = `
    <div class="ms-values"></div>
    <svg class="ms-arrow" width="12" height="12" viewBox="0 0 24 24" fill="none"
         stroke="currentColor" stroke-width="2.5" aria-hidden="true">
      <polyline points="6 9 12 15 18 9"></polyline>
    </svg>
  `;

  const dropdown = document.createElement('div');
  dropdown.className = 'ms-dropdown';

  container.appendChild(trigger);
  container.appendChild(dropdown);

  function renderTrigger() {
    const valDiv = trigger.querySelector('.ms-values');
    valDiv.innerHTML = '';
    if (selected.size === 0) {
      valDiv.innerHTML = '<span class="ms-placeholder">Select resources…</span>';
    } else {
      selected.forEach(v => {
        const tag = document.createElement('span');
        tag.className = 'ms-tag';
        tag.innerHTML = `${esc(v)}<button class="ms-tag-remove" data-v="${esc(v)}" aria-label="Remove ${esc(v)}">&times;</button>`;
        tag.querySelector('.ms-tag-remove').addEventListener('click', e => {
          e.stopPropagation();
          selected.delete(v);
          renderTrigger();
          renderDropdown();
        });
        valDiv.appendChild(tag);
      });
    }
  }

  function renderDropdown() {
    dropdown.innerHTML = '';
    if (state.availableResources.length === 0) {
      dropdown.innerHTML = '<div class="ms-empty">No resources defined yet</div>';
      return;
    }
    state.availableResources.forEach(rid => {
      const opt = document.createElement('div');
      opt.className = 'ms-option';
      opt.setAttribute('role', 'option');
      opt.innerHTML = `
        <input type="checkbox" ${selected.has(rid) ? 'checked' : ''} aria-label="${esc(rid)}" />
        <span>${esc(rid)}</span>
      `;
      opt.addEventListener('click', () => {
        selected.has(rid) ? selected.delete(rid) : selected.add(rid);
        renderTrigger();
        renderDropdown();
      });
      dropdown.appendChild(opt);
    });
  }

  function open() {
    closeAllDropdowns();
    dropdown.classList.add('open');
    trigger.classList.add('open');
    renderDropdown();
  }

  function close() {
    dropdown.classList.remove('open');
    trigger.classList.remove('open');
  }

  trigger.addEventListener('click', () => {
    dropdown.classList.contains('open') ? close() : open();
  });

  trigger.addEventListener('keydown', e => {
    if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); dropdown.classList.contains('open') ? close() : open(); }
    if (e.key === 'Escape') close();
  });

  container._refresh = () => {
    [...selected].forEach(v => { if (!state.availableResources.includes(v)) selected.delete(v); });
    renderTrigger();
  };

  container._getValues = () => [...selected];

  renderTrigger();
}

function closeAllDropdowns() {
  document.querySelectorAll('.ms-dropdown.open').forEach(d => d.classList.remove('open'));
  document.querySelectorAll('.ms-trigger.open').forEach(t => t.classList.remove('open'));
}

document.addEventListener('click', e => {
  if (!e.target.closest('.multi-select')) closeAllDropdowns();
});

function collectData() {
  const resources = [];
  document.querySelectorAll('#resources-container .resource-row').forEach(row => {
    const rid = row.querySelector('.res-id').value.trim();
    const instances = parseInt(row.querySelector('.res-inst').value, 10) || 1;
    if (rid) resources.push({ rid, instances });
  });

  const processes = [];
  document.querySelectorAll('#processes-container .process-card').forEach(card => {
    const pid = card.querySelector('.proc-pid').value.trim();
    const allocated = card.querySelector('[data-field="allocated"]')._getValues();
    const requested = card.querySelector('[data-field="requested"]')._getValues();
    const max_need  = card.querySelector('[data-field="max_need"]')._getValues();
    if (pid) processes.push({ pid, allocated, requested, max_need });
  });

  return { resources, processes };
}

function validate(data) {
  const errors = [];
  if (!data.resources.length) errors.push('At least one resource must be defined.');
  if (!data.processes.length) errors.push('At least one process must be defined.');

  const rids = new Set(data.resources.map(r => r.rid));
  const dupR = findDups(data.resources.map(r => r.rid));
  const dupP = findDups(data.processes.map(p => p.pid));
  if (dupR.length) errors.push(`Duplicate resource IDs: ${dupR.join(', ')}.`);
  if (dupP.length) errors.push(`Duplicate process IDs: ${dupP.join(', ')}.`);

  data.processes.forEach(p => {
    [...p.allocated, ...p.requested, ...p.max_need].forEach(rid => {
      if (!rids.has(rid)) errors.push(`Process "${p.pid}" references undefined resource "${rid}".`);
    });
  });

  return errors;
}

async function runDetection() {
  const data = collectData();
  const errors = validate(data);

  if (errors.length) {
    renderResults(null, errors);
    switchTab('results');
    return;
  }

  setLoading(true, 'Analyzing system state…');
  clearResults();

  try {
    const res  = await fetch(`${API_BASE}/detect`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    const json = await res.json();

    if (!res.ok || !json.success) {
      renderApiError(json);
      switchTab('results');
      return;
    }

    state.lastResult = json;
    state.simSteps   = json.simulation || [];
    renderResults(json);
    renderSimulationTab();
    renderGraph(json);
    setPostDetect(true);
    switchTab('results');
  } catch {
    renderConnError();
    switchTab('results');
  } finally {
    setLoading(false);
  }
}

async function loadSample() {
  setLoading(true, 'Loading sample…');
  try {
    const res  = await fetch(`${API_BASE}/sample`);
    const data = await res.json();

    $('resources-container').innerHTML = '';
    $('processes-container').innerHTML = '';
    state.availableResources = [];

    (data.resources || []).forEach(r => addResource(r));
    (data.processes || []).forEach(p => addProcess(p));
    clearResults();
  } catch {
    renderConnError();
  } finally {
    setLoading(false);
  }
}

function clearAll() {
  $('resources-container').innerHTML = '';
  $('processes-container').innerHTML = '';
  state.availableResources = [];
  addResource();
  addProcess();
  clearResults();
  setPostDetect(false);
}

function clearResults() {
  $('results-container').innerHTML = emptyHTML('search', 'No analysis yet', 'Configure your system and click Run Detection to begin.');
  $('simulation-container').innerHTML = emptyHTML('play', 'No simulation yet', 'Run detection first, then click Simulate to step through execution.');
  $('graph-panel').innerHTML = emptyHTML('globe', 'No graph yet', 'Run detection to generate the Resource Allocation Graph.');
  state.lastResult = null;
  state.simSteps   = [];
  state.simIndex   = 0;
}

function renderResults(data, validationErrors) {
  const el = $('results-container');

  if (validationErrors) {
    el.innerHTML = `
      <div class="alert-card">
        <p class="alert-title">Validation Error</p>
        <p class="alert-desc">Please fix the following issues before running detection:</p>
        <ul class="alert-list">${validationErrors.map(e => `<li>${esc(e)}</li>`).join('')}</ul>
      </div>`;
    return;
  }

  if (!data) return;

  const cd  = data.cycle_detection   || {};
  const ba  = data.bankers_algorithm || {};
  const gi  = data.graph_info        || {};
  const res = data.resolution        || {};
  const pre = data.prevention        || {};

  let html = data.deadlock
    ? banner('deadlock', 'Deadlock Detected', `${data.involved_processes?.length || 0} process(es) involved in a circular wait.`)
    : banner('safe', 'System is Safe', 'No deadlock detected. All processes can complete execution.');

  if (data.deadlock && data.involved_processes?.length) {
    html += `
      <div class="result-section">
        <p class="result-section-title">Involved Processes</p>
        <div class="badge-list">
          ${data.involved_processes.map(p => `<span class="badge badge-red">${esc(p)}</span>`).join('')}
        </div>
      </div>
      <hr class="result-divider" />`;
  }

  html += `
    <div class="result-section">
      <p class="result-section-title">Algorithm Results</p>
      <div class="info-grid">
        <div class="info-card">
          <p class="info-card-label">Cycle Detection</p>
          <p class="info-card-value">${cd.has_deadlock ? 'Cycle Found' : 'No Cycle'}</p>
          ${cd.cycles?.length ? `<p class="info-card-sub">${cd.cycles.length} cycle(s)</p>` : ''}
        </div>
        <div class="info-card">
          <p class="info-card-label">Banker's Algorithm</p>
          <p class="info-card-value">${(ba.state === 'unsafe' || ba.has_deadlock) ? 'Unsafe State' : 'Safe State'}</p>
          ${(!ba.has_deadlock && ba.state !== 'unsafe' && ba.safe_sequence?.length)
            ? `<p class="info-card-sub">Seq: ${ba.safe_sequence.join(' → ')}</p>` : ''}
        </div>
        <div class="info-card">
          <p class="info-card-label">Graph Nodes</p>
          <p class="info-card-value">${gi.nodes ?? '—'}</p>
        </div>
        <div class="info-card">
          <p class="info-card-label">Graph Edges</p>
          <p class="info-card-value">${gi.edges ?? '—'}</p>
        </div>
      </div>
    </div>`;

  if (cd.cycles?.length) {
    html += `<hr class="result-divider" />
    <div class="result-section">
      <p class="result-section-title">Detected Cycles</p>
      <div class="strategy-list">
        ${cd.cycles.map((c, i) => `
          <div class="strategy-card card-danger">
            <p class="strategy-card-title">Cycle ${i + 1}</p>
            <p class="strategy-card-desc">${c.map(n => esc(n)).join(' → ')}</p>
          </div>`).join('')}
      </div>
    </div>`;
  }

  if (data.deadlock && res.actions?.length) {
    html += `<hr class="result-divider" />
    <div class="result-section">
      <p class="result-section-title">Resolution</p>
      <div class="strategy-list">
        ${res.actions.map(a => `
          <div class="strategy-card card-warning">
            <p class="strategy-card-title">${esc(fmtKey(a.action))} — ${esc(a.target || '')}</p>
            <p class="strategy-card-desc">${esc(a.description || '')}</p>
          </div>`).join('')}
      </div>
    </div>`;
  }

  const strategies = Array.isArray(pre) ? pre : (pre.strategies || []);
  if (strategies.length) {
    html += `<hr class="result-divider" />
    <div class="result-section">
      <p class="result-section-title">Prevention Recommendations</p>
      <div class="strategy-list">
        ${strategies.map(s => `
          <div class="strategy-card">
            <p class="strategy-card-title">${esc(s.strategy || s.condition || '')}</p>
            <p class="strategy-card-desc">${esc(s.method || s.recommendation || s.description || '')}</p>
            ${s.impact ? `<p class="strategy-card-meta">Impact: ${esc(s.impact)}</p>` : ''}
          </div>`).join('')}
      </div>
    </div>`;
  }

  el.innerHTML = html;
}

function renderGraph(data) {
  if (data.graph_url) {
    $('graph-panel').innerHTML = `
      <div class="graph-wrap">
        <img src="http://localhost:5000${data.graph_url}?t=${Date.now()}"
             alt="Resource Allocation Graph" />
      </div>`;
  }
}

function renderApiError(json) {
  const details = json.details;
  $('results-container').innerHTML = `
    <div class="alert-card">
      <p class="alert-title">Detection Failed</p>
      <p class="alert-desc">The server could not process the request.</p>
      ${details ? `<ul class="alert-list">${(Array.isArray(details) ? details : [details]).map(d => `<li>${esc(String(d))}</li>`).join('')}</ul>` : ''}
    </div>`;
}

function renderConnError() {
  $('results-container').innerHTML = `
    <div class="alert-card">
      <p class="alert-title">Connection Error</p>
      <p class="alert-desc">Unable to reach the backend. Ensure the server is running on port 5000.</p>
    </div>`;
}

function renderSimulationTab() {
  const el = $('simulation-container');
  if (!state.simSteps.length) {
    el.innerHTML = emptyHTML('play', 'No simulation yet', 'Run detection first, then click Simulate to step through execution.');
    return;
  }

  el.innerHTML = `
    <div class="sim-tab-header">
      <p class="sim-tab-title">${state.simSteps.length} simulation steps</p>
      <button class="btn btn-primary btn-sm" id="btn-open-modal">
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>
        Step-by-Step
      </button>
    </div>
    <div class="sim-steps-list">
      ${state.simSteps.map((step, i) => `
        <div class="sim-step">
          <div class="sim-step-header">
            <div class="sim-step-num">${i + 1}</div>
            <div class="sim-step-desc">${esc(step.description)}</div>
          </div>
          ${step.detail ? `<div class="sim-step-detail">${esc(step.detail)}</div>` : ''}
          ${step.highlight?.length ? `
            <div class="sim-step-highlight">
              ${step.highlight.map(h => `<span class="badge badge-red">${esc(h)}</span>`).join('')}
            </div>` : ''}
        </div>`).join('')}
    </div>`;

  $('btn-open-modal')?.addEventListener('click', openSimModal);
}

function openSimulation() {
  switchTab('simulation');
}

function openSimModal() {
  if (!state.simSteps.length) return;
  state.simIndex = 0;
  renderModalSteps();
  $('sim-modal').hidden = false;
  updateSimControls();
}

function closeSimModal() { $('sim-modal').hidden = true; }

function renderModalSteps() {
  $('sim-steps-container').innerHTML = state.simSteps.map((step, i) => {
    const cls = i < state.simIndex ? 'step-done' : i === state.simIndex ? 'step-active' : '';
    return `
      <div class="sim-step ${cls}">
        <div class="sim-step-header">
          <div class="sim-step-num">${i + 1}</div>
          <div class="sim-step-desc">${esc(step.description)}</div>
        </div>
        ${step.detail ? `<div class="sim-step-detail">${esc(step.detail)}</div>` : ''}
        ${step.highlight?.length ? `
          <div class="sim-step-highlight">
            ${step.highlight.map(h => `<span class="badge badge-red">${esc(h)}</span>`).join('')}
          </div>` : ''}
      </div>`;
  }).join('');

  // Scroll active step into view
  const active = $('sim-steps-container').querySelector('.step-active');
  if (active) active.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
}

function simPrev() {
  if (state.simIndex > 0) { state.simIndex--; renderModalSteps(); updateSimControls(); }
}

function simNext() {
  if (state.simIndex < state.simSteps.length - 1) { state.simIndex++; renderModalSteps(); updateSimControls(); }
}

function updateSimControls() {
  $('sim-counter').textContent = `Step ${state.simIndex + 1} / ${state.simSteps.length}`;
  $('sim-prev').disabled = state.simIndex === 0;
  $('sim-next').disabled = state.simIndex === state.simSteps.length - 1;
}

async function downloadReport() {
  const data = collectData();
  const errors = validate(data);
  if (errors.length) { alert('Fix validation errors before generating a report.'); return; }

  setLoading(true, 'Generating PDF report…');
  try {
    const res = await fetch(`${API_BASE}/report`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!res.ok) { alert('Failed to generate report.'); return; }
    const blob = await res.blob();
    const url  = URL.createObjectURL(blob);
    const a    = document.createElement('a');
    a.href = url; a.download = `deadlock_report_${Date.now()}.pdf`;
    document.body.appendChild(a); a.click();
    document.body.removeChild(a); URL.revokeObjectURL(url);
  } catch { alert('Failed to download report.'); }
  finally { setLoading(false); }
}

function banner(type, title, desc) {
  return `
    <div class="status-banner banner-${type}">
      <span class="status-dot"></span>
      <div>
        <p class="status-banner-title">${esc(title)}</p>
        <p class="status-banner-desc">${esc(desc)}</p>
      </div>
    </div>`;
}

function emptyHTML(icon, title, desc) {
  const icons = {
    search: '<circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line>',
    play:   '<polygon points="5 3 19 12 5 21 5 3"></polygon>',
    globe:  '<circle cx="12" cy="12" r="10"></circle><line x1="2" y1="12" x2="22" y2="12"></line><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path>',
  };
  return `
    <div class="empty-state">
      <svg width="44" height="44" viewBox="0 0 24 24" fill="none" stroke="#94a3b8" stroke-width="1.5" aria-hidden="true">${icons[icon] || ''}</svg>
      <p class="empty-title">${esc(title)}</p>
      <p class="empty-desc">${esc(desc)}</p>
    </div>`;
}

function setLoading(on, text = 'Analyzing…') {
  $('loading-overlay').hidden = !on;
  const t = $('loading-text');
  if (t) t.textContent = text;
}

function setPostDetect(on) {
  ['btn-simulate', 'btn-report'].forEach(id => {
    const b = $(id);
    if (b) b.disabled = !on;
  });
}

function flashRow(el) {
  el.style.outline = '2px solid var(--danger)';
  setTimeout(() => { el.style.outline = ''; }, 900);
}

function findDups(arr) {
  const seen = new Set(), dups = new Set();
  arr.forEach(v => { seen.has(v) ? dups.add(v) : seen.add(v); });
  return [...dups];
}

function fmtKey(s) {
  return (s || '').replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
}

function esc(s) {
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}
