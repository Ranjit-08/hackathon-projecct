const Auth = {
  save(token, user) {
    localStorage.setItem('token', token);
    localStorage.setItem('user',  JSON.stringify(user));
  },

  get() {
    try { return JSON.parse(localStorage.getItem('user')); } catch { return null; }
  },

  token() { return localStorage.getItem('token'); },

  logout() {
    localStorage.clear();
    window.location.href = '/index.html';
  },

  requireAuth(role) {
    const user = this.get();
    if (!user || user.role !== role) {
      window.location.href = role === 'company'
        ? '/company/login.html'
        : '/user/login.html';
      return false;
    }
    return true;
  },

  redirectIfLoggedIn() {
    const user = this.get();
    if (!user) return;
    window.location.href = user.role === 'company'
      ? '/company/dashboard.html'
      : '/user/dashboard.html';
  }
};

// ── UI Helpers ────────────────────────────────────────────────────────────────
function showAlert(container, message, type = 'error') {
  const icons = { error: '⚠️', success: '✅', info: 'ℹ️' };
  container.innerHTML = `
    <div class="alert alert-${type}">
      ${icons[type] || ''} ${message}
    </div>`;
  setTimeout(() => container.innerHTML = '', 5000);
}

function setLoading(btn, loading, text = 'Loading...') {
  if (loading) {
    btn._orig = btn.innerHTML;
    btn.disabled  = true;
    btn.innerHTML = `<span class="spinner"></span> ${text}`;
  } else {
    btn.disabled  = false;
    btn.innerHTML = btn._orig || text;
  }
}