/**
 * Funding Aggregator — Auth Module
 */
const auth = {
  init() {
    this.bindEvents();
    this.checkAuth();
  },

  bindEvents() {
    document.getElementById('btn-login')?.addEventListener('click', () => this.showModal('login'));
    document.getElementById('btn-register')?.addEventListener('click', () => this.showModal('register'));
    document.getElementById('btn-logout')?.addEventListener('click', () => this.logout());
    document.getElementById('modal-close')?.addEventListener('click', () => this.hideModal());
    document.getElementById('auth-modal')?.addEventListener('click', (e) => { if (e.target.id === 'auth-modal') this.hideModal(); });

    document.querySelectorAll('.modal-tab').forEach(tab => {
      tab.addEventListener('click', () => this.switchTab(tab.dataset.tab));
    });

    document.getElementById('login-form')?.addEventListener('submit', (e) => { e.preventDefault(); this.handleLogin(); });
    document.getElementById('register-form')?.addEventListener('submit', (e) => { e.preventDefault(); this.handleRegister(); });
  },

  showModal(tab = 'login') {
    document.getElementById('auth-modal')?.classList.remove('hidden');
    this.switchTab(tab);
  },
  hideModal() { document.getElementById('auth-modal')?.classList.add('hidden'); },

  switchTab(tab) {
    document.querySelectorAll('.modal-tab').forEach(t => t.classList.toggle('active', t.dataset.tab === tab));
    document.getElementById('login-form')?.classList.toggle('hidden', tab !== 'login');
    document.getElementById('register-form')?.classList.toggle('hidden', tab !== 'register');
  },

  async handleLogin() {
    const username = document.getElementById('login-username').value;
    const password = document.getElementById('login-password').value;
    const result = await api.login({ username, password });
    if (result.ok) {
      this.hideModal();
      this.checkAuth();
      showToast('Welcome back!', 'success');
    } else {
      document.getElementById('login-error').textContent = result.data?.detail || 'Login failed';
      document.getElementById('login-error').classList.remove('hidden');
    }
  },

  async handleRegister() {
    const data = {
      email: document.getElementById('reg-email').value,
      username: document.getElementById('reg-username').value,
      full_name: document.getElementById('reg-fullname').value,
      password: document.getElementById('reg-password').value,
    };
    const res = await api.register(data);
    if (res.ok) {
      showToast('Account created! Signing in...', 'success');
      await api.login({ username: data.username, password: data.password });
      this.hideModal();
      this.checkAuth();
    } else {
      const err = await res.json();
      document.getElementById('register-error').textContent = err?.detail || 'Registration failed';
      document.getElementById('register-error').classList.remove('hidden');
    }
  },

  async checkAuth() {
    if (api.isAuthenticated()) {
      const profile = await api.getProfile();
      if (profile) {
        document.getElementById('auth-buttons')?.classList.add('hidden');
        document.getElementById('user-menu')?.classList.remove('hidden');
        document.getElementById('user-name').textContent = profile.username;
        return;
      }
      api.clearTokens();
    }
    document.getElementById('auth-buttons')?.classList.remove('hidden');
    document.getElementById('user-menu')?.classList.add('hidden');
  },

  logout() {
    api.clearTokens();
    this.checkAuth();
    showToast('Logged out', 'info');
  }
};
