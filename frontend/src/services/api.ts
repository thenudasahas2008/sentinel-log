const API_BASE = '/api/v1';

function getAuthHeader(): Record<string, string> {
  const token = localStorage.getItem('sentinel_token');
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export const api = {
  // Auth
  login: async (username: string, password: string) => {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    });
    if (!res.ok) throw new Error((await res.json()).detail || 'Login failed');
    return res.json();
  },

  getCurrentUser: async () => {
    const res = await fetch(`${API_BASE}/auth/me`, {
      headers: { ...getAuthHeader() }
    });
    if (!res.ok) throw new Error('Not authenticated');
    return res.json();
  },

  // Dashboard
  getDashboardStats: async () => {
    const res = await fetch(`${API_BASE}/dashboard/stats`, {
      headers: { ...getAuthHeader() }
    });
    if (!res.ok) throw new Error('Failed to fetch dashboard stats');
    return res.json();
  },

  // Events
  getEvents: async (params?: Record<string, any>) => {
    const query = new URLSearchParams(params).toString();
    const res = await fetch(`${API_BASE}/events?${query}`, {
      headers: { ...getAuthHeader() }
    });
    if (!res.ok) throw new Error('Failed to fetch events');
    return res.json();
  },

  // Alerts
  getAlerts: async (params?: Record<string, any>) => {
    const query = new URLSearchParams(params).toString();
    const res = await fetch(`${API_BASE}/alerts?${query}`, {
      headers: { ...getAuthHeader() }
    });
    if (!res.ok) throw new Error('Failed to fetch alerts');
    return res.json();
  },

  updateAlertStatus: async (alertUuid: string, status: string, notes?: string) => {
    const res = await fetch(`${API_BASE}/alerts/${alertUuid}/status`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json', ...getAuthHeader() },
      body: JSON.stringify({ status, resolution_notes: notes })
    });
    if (!res.ok) throw new Error('Failed to update alert');
    return res.json();
  },

  // Investigations
  getInvestigations: async () => {
    const res = await fetch(`${API_BASE}/investigations`, {
      headers: { ...getAuthHeader() }
    });
    if (!res.ok) throw new Error('Failed to fetch investigations');
    return res.json();
  },

  createInvestigation: async (data: any) => {
    const res = await fetch(`${API_BASE}/investigations`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...getAuthHeader() },
      body: JSON.stringify(data)
    });
    if (!res.ok) throw new Error('Failed to create investigation');
    return res.json();
  },

  addInvestigationNote: async (id: number, content: string) => {
    const res = await fetch(`${API_BASE}/investigations/${id}/notes`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...getAuthHeader() },
      body: JSON.stringify({ content })
    });
    if (!res.ok) throw new Error('Failed to add note');
    return res.json();
  },

  // IP Intelligence
  lookupIp: async (ip: string) => {
    const res = await fetch(`${API_BASE}/ip-intel/${encodeURIComponent(ip)}`, {
      headers: { ...getAuthHeader() }
    });
    if (!res.ok) throw new Error('Failed to fetch IP intelligence');
    return res.json();
  },

  // Ingestion
  uploadLogFile: async (formData: FormData) => {
    const res = await fetch(`${API_BASE}/ingestion/upload`, {
      method: 'POST',
      headers: { ...getAuthHeader() },
      body: formData
    });
    if (!res.ok) throw new Error((await res.json()).detail || 'Upload failed');
    return res.json();
  },

  // Reports
  getReports: async () => {
    const res = await fetch(`${API_BASE}/reports`, {
      headers: { ...getAuthHeader() }
    });
    if (!res.ok) throw new Error('Failed to fetch reports');
    return res.json();
  },

  generateReport: async (data: any) => {
    const res = await fetch(`${API_BASE}/reports/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...getAuthHeader() },
      body: JSON.stringify(data)
    });
    if (!res.ok) throw new Error('Failed to generate report');
    return res.json();
  },

  // Demo Mode
  generateDemoData: async () => {
    const res = await fetch(`${API_BASE}/demo/generate`, {
      method: 'POST',
      headers: { ...getAuthHeader() }
    });
    if (!res.ok) throw new Error('Failed to generate demo scenario');
    return res.json();
  },

  resetDemoData: async () => {
    const res = await fetch(`${API_BASE}/demo/reset`, {
      method: 'POST',
      headers: { ...getAuthHeader() }
    });
    if (!res.ok) throw new Error('Failed to reset demo data');
    return res.json();
  },

  // Users
  getUsers: async () => {
    const res = await fetch(`${API_BASE}/users`, {
      headers: { ...getAuthHeader() }
    });
    if (!res.ok) throw new Error('Failed to fetch users');
    return res.json();
  },

  // Audit
  getAuditLogs: async () => {
    const res = await fetch(`${API_BASE}/audit`, {
      headers: { ...getAuthHeader() }
    });
    if (!res.ok) throw new Error('Failed to fetch audit logs');
    return res.json();
  }
};
