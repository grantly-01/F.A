/**
 * Funding Aggregator — API Client
 */
const API_BASE = window.location.hostname === 'localhost' && window.location.port === '3000'
  ? 'http://localhost:8000' : '';
const API_V1 = `${API_BASE}/api/v1`;

const api = {
  _token: localStorage.getItem('access_token'),
  _refreshToken: localStorage.getItem('refresh_token'),

  _headers() {
    const h = { 'Content-Type': 'application/json' };
    if (this._token) h['Authorization'] = `Bearer ${this._token}`;
    return h;
  },

  setTokens(access, refresh) {
    this._token = access;
    this._refreshToken = refresh;
    localStorage.setItem('access_token', access);
    localStorage.setItem('refresh_token', refresh);
  },

  clearTokens() {
    this._token = null;
    this._refreshToken = null;
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  },

  isAuthenticated() { return !!this._token; },

  async _fetch(url, options = {}) {
    const res = await fetch(url, { ...options, headers: { ...this._headers(), ...options.headers } });
    if (res.status === 401 && this._refreshToken) {
      const refreshed = await this.refreshToken();
      if (refreshed) {
        return fetch(url, { ...options, headers: { ...this._headers(), ...options.headers } });
      }
    }
    return res;
  },

  // Auth
  async register(data) {
    const res = await fetch(`${API_V1}/auth/register`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) });
    return res;
  },
  async login(data) {
    const res = await fetch(`${API_V1}/auth/login`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) });
    if (res.ok) {
      const tokens = await res.json();
      this.setTokens(tokens.access_token, tokens.refresh_token);
      return { ok: true, data: tokens };
    }
    return { ok: false, data: await res.json() };
  },
  async refreshToken() {
    try {
      const res = await fetch(`${API_V1}/auth/refresh`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ refresh_token: this._refreshToken }) });
      if (res.ok) { const t = await res.json(); this.setTokens(t.access_token, t.refresh_token); return true; }
    } catch(e) {}
    this.clearTokens();
    return false;
  },
  async getProfile() {
    const res = await this._fetch(`${API_V1}/users/me`);
    return res.ok ? res.json() : null;
  },

  // Grants
  async getGrants(params = {}) {
    const qs = new URLSearchParams();
    Object.entries(params).forEach(([k,v]) => { if(v !== null && v !== undefined && v !== '') qs.set(k,v); });
    const res = await fetch(`${API_V1}/grants/?${qs}`);
    return res.ok ? res.json() : { items: [], total: 0, page: 1, pages: 0 };
  },
  async getGrant(id) {
    const res = await fetch(`${API_V1}/grants/${id}`);
    return res.ok ? res.json() : null;
  },
  async getStats() {
    const res = await fetch(`${API_V1}/grants/stats`);
    return res.ok ? res.json() : { total_grants: 0, active_grants: 0, total_sources: 0 };
  },
  async getCategories() {
    const res = await fetch(`${API_V1}/grants/categories`);
    return res.ok ? res.json() : [];
  },
  async getSources() {
    const res = await fetch(`${API_V1}/grants/sources`);
    return res.ok ? res.json() : [];
  },
  async toggleFavorite(grantId) {
    const res = await this._fetch(`${API_V1}/grants/${grantId}/favorite`, { method: 'POST' });
    return res.ok ? res.json() : null;
  },

  // AI
  async aiSearch(query) {
    const res = await this._fetch(`${API_V1}/ai/search`, { method: 'POST', body: JSON.stringify({ query, max_results: 20 }) });
    return res.ok ? res.json() : { items: [], total: 0 };
  },
  async aiAnalyze(grantId) {
    const res = await this._fetch(`${API_V1}/ai/analyze/${grantId}`, { method: 'POST' });
    return res.ok ? res.json() : null;
  },
};
