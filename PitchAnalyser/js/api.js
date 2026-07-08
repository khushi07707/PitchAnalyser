/* ============================================================
   PitchPilotAI — API Client & Auth Manager
   Central layer for all backend communication.
   Backend: http://localhost:8000/api
   ============================================================ */

'use strict';

const API_BASE = 'http://localhost:8000/api';

/* ──────────────────────────────────────────────
   TOKEN STORAGE
────────────────────────────────────────────── */
const Auth = {
  getToken()  { return localStorage.getItem('pp_access_token'); },
  getUser()   { const u = localStorage.getItem('pp_user'); try { return JSON.parse(u); } catch { return null; } },
  setSession(token, user) {
    localStorage.setItem('pp_access_token', token);
    localStorage.setItem('pp_user', JSON.stringify(user));
  },
  clear() {
    localStorage.removeItem('pp_access_token');
    localStorage.removeItem('pp_user');
    localStorage.removeItem('pp_upload_id');
  },
  isLoggedIn() { return !!this.getToken(); }
};

/* ──────────────────────────────────────────────
   AUTH GUARD — call on every protected page
────────────────────────────────────────────── */
function requireAuth() {
  if (!Auth.isLoggedIn()) {
    window.location.href = 'login.html';
    return false;
  }
  // Populate user name in navbar if elements exist
  const user = Auth.getUser();
  if (user) {
    document.querySelectorAll('[data-user-name]').forEach(el => { el.textContent = user.full_name || user.email; });
    document.querySelectorAll('[data-user-email]').forEach(el => { el.textContent = user.email; });
    document.querySelectorAll('[data-user-initials]').forEach(el => {
      const parts = (user.full_name || user.email).split(' ');
      el.textContent = parts.length >= 2 ? parts[0][0] + parts[1][0] : parts[0].substring(0, 2);
    });
    document.querySelectorAll('[data-user-company]').forEach(el => { el.textContent = user.company || ''; });
  }
  return true;
}

/* ──────────────────────────────────────────────
   CORE FETCH WRAPPER
────────────────────────────────────────────── */
async function apiFetch(path, options = {}) {
  const token = Auth.getToken();
  const headers = { 'Content-Type': 'application/json', ...(options.headers || {}) };
  if (token) headers['Authorization'] = `Bearer ${token}`;

  // Remove Content-Type for FormData (browser sets it with boundary)
  if (options.body instanceof FormData) delete headers['Content-Type'];

  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });

  if (res.status === 401) {
    Auth.clear();
    window.location.href = 'login.html';
    return;
  }

  if (res.status === 204) return null;  // No content (DELETE)

  const data = await res.json().catch(() => ({}));

  if (!res.ok) {
    const msg = data?.detail || data?.message || `Request failed (${res.status})`;
    throw new Error(Array.isArray(msg) ? msg.map(e => e.msg || e).join(', ') : msg);
  }

  return data;
}

/* ──────────────────────────────────────────────
   AUTH ENDPOINTS
────────────────────────────────────────────── */
const API = {
  async login(email, password) {
    const data = await apiFetch('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password })
    });
    Auth.setSession(data.access_token, data.user);
    return data;
  },

  async register(payload) {
    const data = await apiFetch('/auth/register', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
    return data;
  },

  async getMe() {
    return apiFetch('/auth/me');
  },

  /* ── UPLOAD ── */
  async uploadFile(file, onProgress) {
    const token = Auth.getToken();
    return new Promise((resolve, reject) => {
      const formData = new FormData();
      formData.append('file', file);

      const xhr = new XMLHttpRequest();
      xhr.open('POST', `${API_BASE}/uploads/upload`);
      xhr.setRequestHeader('Authorization', `Bearer ${token}`);

      xhr.upload.onprogress = (e) => {
        if (e.lengthComputable && onProgress) onProgress(Math.round((e.loaded / e.total) * 100));
      };

      xhr.onload = () => {
        if (xhr.status === 201) {
          resolve(JSON.parse(xhr.responseText));
        } else {
          let msg = 'Upload failed';
          try { msg = JSON.parse(xhr.responseText)?.detail || msg; } catch {}
          reject(new Error(msg));
        }
      };

      xhr.onerror = () => reject(new Error('Network error during upload'));
      xhr.send(formData);
    });
  },

  /* ── ANALYSIS ── */
  async processUpload(uploadId) {
    return apiFetch(`/analysis/process/${uploadId}`, { method: 'POST' });
  },

  async getAnalysisStatus(uploadId) {
    return apiFetch(`/analysis/status/${uploadId}`);
  },

  /* ── DASHBOARD ── */
  async getDashboardStats()   { return apiFetch('/dashboard/stats'); },
  async getPerformanceTrend() { return apiFetch('/dashboard/performance'); },
  async getRecentReports()    { return apiFetch('/dashboard/recent'); },
  async getUserStats()        { return apiFetch('/dashboard/user-stats'); },

  /* ── REPORTS ── */
  async getReports(page = 1, limit = 10, search = '') {
    const q = new URLSearchParams({ page, limit, ...(search ? { search } : {}) });
    return apiFetch(`/reports?${q}`);
  },

  async getReportDetail(reportId) {
    return apiFetch(`/reports/${reportId}`);
  },

  async deleteReport(reportId) {
    return apiFetch(`/reports/${reportId}`, { method: 'DELETE' });
  },

  downloadPDF(reportId) {
    const token = Auth.getToken();
    const url = `${API_BASE}/reports/${reportId}/download`;
    fetch(url, { headers: { Authorization: `Bearer ${token}` } })
      .then(res => {
        if (!res.ok) {
          return res.json().then(err => {
            throw new Error(err.detail || `Server returned status ${res.status}`);
          }).catch(() => {
            throw new Error(`Server returned status ${res.status}`);
          });
        }
        return res.blob();
      })
      .then(blob => {
        const blobUrl = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = blobUrl;
        a.download = `PitchPilot_Report_${reportId}.pdf`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        // Delay revoking the ObjectURL to ensure browser initiates the download
        setTimeout(() => URL.revokeObjectURL(blobUrl), 100);
      })
      .catch(err => {
        console.error('PDF download error:', err);
        alert(`Could not download PDF: ${err.message}`);
      });
  }
};

/* ──────────────────────────────────────────────
   LOGOUT HELPER (attach to logout buttons)
────────────────────────────────────────────── */
function handleLogout() {
  Auth.clear();
  window.location.href = 'login.html';
}

// Attach logout to any [data-logout] buttons
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('[data-logout]').forEach(btn => {
    btn.addEventListener('click', (e) => { e.preventDefault(); handleLogout(); });
  });
});

// Expose globally
window.API = API;
window.Auth = Auth;
window.requireAuth = requireAuth;
window.handleLogout = handleLogout;
