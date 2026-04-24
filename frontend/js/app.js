/**
 * Funding Aggregator — Main App (RU/KZ localized)
 */

function showToast(message, type = 'info') {
  const container = document.getElementById('toast-container');
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.textContent = message;
  container.appendChild(toast);
  setTimeout(() => toast.remove(), 4000);
}

function renderGrantCard(grant) {
  const amount = grant.amount_max ? `${Number(grant.amount_max).toLocaleString('ru-RU')} ${grant.currency || '₸'}` : '';
  const deadline = grant.deadline ? new Date(grant.deadline).toLocaleDateString('ru-RU') : '';
  const desc = grant.summary_ai || grant.description || '';
  return `
    <div class="grant-card" data-id="${grant.id}" onclick="showGrantDetail('${grant.id}')">
      <div class="grant-card-header">
        <div class="grant-card-title">${escapeHtml(grant.title)}</div>
        <span class="grant-card-source">${grant.source_name}</span>
      </div>
      <div class="grant-card-desc">${escapeHtml(desc.substring(0, 200))}</div>
      <div class="grant-card-meta">
        ${amount ? `<span class="grant-meta-item grant-amount">💰 ${amount}</span>` : ''}
        ${deadline ? `<span class="grant-meta-item grant-deadline">📅 ${deadline}</span>` : ''}
        ${grant.country ? `<span class="grant-meta-item grant-country">🌍 ${grant.country}</span>` : ''}
      </div>
    </div>`;
}

function escapeHtml(str) {
  if (!str) return '';
  return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

let currentPage = 'home';
let grantsState = { page: 1, per_page: 20 };

function navigateTo(page) {
  currentPage = page;
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.getElementById(`page-${page}`)?.classList.add('active');
  document.querySelectorAll('.nav-link').forEach(l => l.classList.toggle('active', l.dataset.page === page));
  window.scrollTo(0, 0);
  if (page === 'grants') loadGrants();
  if (page === 'stats') loadStats();
}

async function loadStats() {
  try {
    const stats = await api.getStats();
    document.getElementById('stat-total').textContent = stats.total_grants || 0;
    document.getElementById('stat-active').textContent = stats.active_grants || 0;
    document.getElementById('stat-sources').textContent = stats.total_sources || 0;
    document.getElementById('stats-total').textContent = stats.total_grants || 0;
    document.getElementById('stats-active').textContent = stats.active_grants || 0;
    document.getElementById('stats-sources').textContent = stats.total_sources || 0;
  } catch(e) {}
}

async function loadGrants() {
  const container = document.getElementById('grants-list');
  container.innerHTML = '<div class="loading"><div class="spinner"></div></div>';
  const search = document.getElementById('grants-search')?.value || '';
  const source = document.getElementById('filter-source')?.value || '';
  const country = document.getElementById('filter-country')?.value || '';
  const status = document.getElementById('filter-status')?.value || 'active';
  const sortVal = document.getElementById('filter-sort')?.value || 'created_at:desc';
  const [sort_by, sort_order] = sortVal.split(':');
  try {
    const data = await api.getGrants({
      q: search || undefined, source: source || undefined,
      country: country || undefined, status: status || undefined,
      sort_by, sort_order, page: grantsState.page, per_page: grantsState.per_page,
    });
    if (data.items.length === 0) {
      container.innerHTML = `<div style="text-align:center;padding:60px;color:var(--text-muted)">${i18n.t('grants.no_results')}</div>`;
    } else {
      container.innerHTML = data.items.map(renderGrantCard).join('');
    }
    renderPagination(data);
  } catch(e) {
    container.innerHTML = `<div style="text-align:center;padding:60px;color:var(--text-muted)">${i18n.t('grants.api_error')}</div>`;
  }
}

async function loadRecentGrants() {
  try {
    const data = await api.getGrants({ per_page: 6, sort_by: 'created_at', sort_order: 'desc' });
    const container = document.getElementById('recent-grants');
    if (data.items.length > 0) {
      container.innerHTML = data.items.map(renderGrantCard).join('');
    } else {
      container.innerHTML = `<div style="text-align:center;padding:40px;color:var(--text-muted)">${i18n.t('grants.no_data')}</div>`;
    }
  } catch(e) {}
}

function renderPagination(data) {
  const container = document.getElementById('pagination');
  if (!data || data.pages <= 1) { container.innerHTML = ''; return; }
  let html = `<button ${data.page <= 1 ? 'disabled' : ''} onclick="goToPage(${data.page - 1})">← </button>`;
  for (let i = 1; i <= Math.min(data.pages, 10); i++) {
    html += `<button class="${i === data.page ? 'active' : ''}" onclick="goToPage(${i})">${i}</button>`;
  }
  html += `<button ${data.page >= data.pages ? 'disabled' : ''} onclick="goToPage(${data.page + 1})"> →</button>`;
  container.innerHTML = html;
}

function goToPage(page) { grantsState.page = page; loadGrants(); }

async function showGrantDetail(id) {
  const grant = await api.getGrant(id);
  if (!grant) return;
  const modal = document.getElementById('grant-modal');
  const detail = document.getElementById('grant-detail');
  const amount = grant.amount_max ? `${Number(grant.amount_max).toLocaleString('ru-RU')} ${grant.currency || '₸'}` : i18n.t('detail.not_specified') || 'Не указано';
  const deadline = grant.deadline ? new Date(grant.deadline).toLocaleDateString('ru-RU') : 'Не указано';
  detail.innerHTML = `
    <h2>${escapeHtml(grant.title)}</h2>
    <div class="grant-detail-meta">
      <span class="detail-badge">📍 ${grant.source_name}</span>
      <span class="detail-badge">💰 ${amount}</span>
      <span class="detail-badge">📅 ${deadline}</span>
      ${grant.country ? `<span class="detail-badge">🌍 ${grant.country}</span>` : ''}
      <span class="detail-badge">${grant.status}</span>
    </div>
    <div class="grant-detail-body">
      ${grant.summary_ai ? `<h3>${i18n.t('detail.ai_summary')}</h3><p>${escapeHtml(grant.summary_ai)}</p>` : ''}
      ${grant.description ? `<h3>${i18n.t('detail.description')}</h3><p>${escapeHtml(grant.description)}</p>` : ''}
      ${grant.eligibility ? `<h3>${i18n.t('detail.eligibility')}</h3><p>${escapeHtml(grant.eligibility)}</p>` : ''}
      ${grant.requirements ? `<h3>${i18n.t('detail.requirements')}</h3><p>${escapeHtml(grant.requirements)}</p>` : ''}
      ${grant.keywords_ai ? `<h3>${i18n.t('detail.keywords')}</h3><p>${(grant.keywords_ai.keywords||[]).map(k=>`<span class="detail-badge">${k}</span>`).join(' ')}</p>` : ''}
    </div>
    <div class="grant-detail-actions">
      <a href="${grant.source_url}" target="_blank" class="btn btn-primary">${i18n.t('detail.view_original')}</a>
      ${api.isAuthenticated() ? `<button class="btn btn-ghost" onclick="toggleFav('${grant.id}')">${i18n.t('detail.favorite')}</button>` : ''}
    </div>`;
  modal.classList.remove('hidden');
}

async function toggleFav(id) {
  const result = await api.toggleFavorite(id);
  if (result) showToast(result.favorited ? i18n.t('detail.added_fav') : i18n.t('detail.removed_fav'), 'success');
}

async function doAISearch() {
  const query = document.getElementById('ai-query')?.value;
  if (!query || query.length < 3) { showToast(i18n.t('ai.short_query'), 'error'); return; }
  const container = document.getElementById('ai-results');
  container.innerHTML = '<div class="loading"><div class="spinner"></div><p style="color:var(--text-muted);margin-top:12px">🤖 AI анализирует запрос...</p></div>';
  try {
    const data = await api.aiSearch(query);
    let html = '';
    
    // AI Knowledge Answer — always show if available
    if (data.ai_answer) {
      let sourcesHtml = '';
      if (data.ai_sources && data.ai_sources.length > 0) {
        sourcesHtml = '<div style="margin-top:24px;padding-top:16px;border-top:1px solid rgba(255,255,255,0.1)">' +
          '<h4 style="color:var(--primary);margin-bottom:12px">📌 Источники и ссылки:</h4>' +
          '<div style="display:grid;gap:10px">' +
          data.ai_sources.map(s => `
            <a href="${escapeHtml(s.url || '#')}" target="_blank" rel="noopener" 
               style="display:block;padding:12px 16px;background:rgba(139,92,246,0.1);border:1px solid rgba(139,92,246,0.2);border-radius:10px;text-decoration:none;transition:all 0.2s">
              <div style="color:var(--primary);font-weight:600;margin-bottom:4px">🔗 ${escapeHtml(s.name || s.url)}</div>
              ${s.description ? `<div style="color:var(--text-muted);font-size:13px">${escapeHtml(s.description)}</div>` : ''}
              <div style="color:rgba(255,255,255,0.3);font-size:11px;margin-top:4px">${escapeHtml(s.url || '')}</div>
            </a>`).join('') +
          '</div></div>';
      }
      html += `
        <div style="max-width:800px;margin:0 auto 30px">
          <div style="background:linear-gradient(135deg,rgba(139,92,246,0.15),rgba(59,130,246,0.1));border:1px solid rgba(139,92,246,0.2);border-radius:16px;padding:28px">
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:16px">
              <span style="font-size:24px">🤖</span>
              <h3 style="color:var(--primary);margin:0">AI Ответ</h3>
            </div>
            <div style="color:var(--text-secondary);line-height:1.8;white-space:pre-line;font-size:15px">${escapeHtml(data.ai_answer)}</div>
            ${sourcesHtml}
          </div>
        </div>`;
    }
    
    // DB grant cards — show below AI answer
    if (data.items && data.items.length > 0) {
      html += `<p style="color:var(--text-muted);margin-bottom:16px">${i18n.t('ai.found')} ${data.total}</p>` +
        '<div class="grants-grid">' + data.items.map(renderGrantCard).join('') + '</div>';
    } else if (!data.ai_answer) {
      html += `<div style="text-align:center;padding:40px;color:var(--text-muted)">${i18n.t('ai.no_results')}</div>`;
    }
    
    container.innerHTML = html;
  } catch(e) {
    container.innerHTML = `<div style="text-align:center;padding:40px;color:var(--red)">${i18n.t('ai.error')}</div>`;
  }
}

async function loadSources() {
  try {
    const sources = await api.getSources();
    const select = document.getElementById('filter-source');
    sources.forEach(s => { const opt = document.createElement('option'); opt.value = s; opt.textContent = s; select.appendChild(opt); });
  } catch(e) {}
}

// Init
document.addEventListener('DOMContentLoaded', () => {
  // i18n
  i18n.init();
  document.getElementById('lang-toggle')?.addEventListener('click', () => {
    const newLang = i18n.currentLang === 'ru' ? 'kz' : 'ru';
    i18n.setLanguage(newLang);
    // Update AI example queries for the new language
    document.querySelectorAll('.ai-example-btn').forEach(btn => {
      const key = btn.getAttribute('data-i18n');
      if (key) {
        const queryKey = key.replace('_label', '_query');
        btn.dataset.query = i18n.t(queryKey);
      }
    });
  });

  auth.init();
  loadStats();
  loadRecentGrants();
  loadSources();

  // Navigation
  document.querySelectorAll('[data-page]').forEach(el => {
    el.addEventListener('click', (e) => { e.preventDefault(); navigateTo(el.dataset.page); });
  });

  document.getElementById('nav-toggle')?.addEventListener('click', () => {
    document.getElementById('nav-links')?.classList.toggle('open');
  });

  // Hero search
  document.getElementById('hero-search-btn')?.addEventListener('click', () => {
    const q = document.getElementById('hero-search-input')?.value;
    if (q) { document.getElementById('grants-search').value = q; navigateTo('grants'); }
  });
  document.getElementById('hero-search-input')?.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') document.getElementById('hero-search-btn')?.click();
  });

  // Filters
  document.getElementById('btn-apply-filters')?.addEventListener('click', () => { grantsState.page = 1; loadGrants(); });
  document.getElementById('grants-search')?.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') { grantsState.page = 1; loadGrants(); }
  });

  // AI Search
  document.getElementById('btn-ai-search')?.addEventListener('click', doAISearch);
  document.querySelectorAll('.ai-example-btn').forEach(btn => {
    btn.addEventListener('click', () => { document.getElementById('ai-query').value = btn.dataset.query; doAISearch(); });
  });

  // Modals
  document.getElementById('grant-modal-close')?.addEventListener('click', () => { document.getElementById('grant-modal')?.classList.add('hidden'); });
  document.getElementById('grant-modal')?.addEventListener('click', (e) => { if (e.target.id === 'grant-modal') e.target.classList.add('hidden'); });
});
