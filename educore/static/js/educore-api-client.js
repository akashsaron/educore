/**
 * EduCore API Client
 * ==================
 * Drop this file into your frontend project (React / Vue / Angular / vanilla JS).
 * Works in any environment that has fetch().
 *
 * Usage:
 *   import { api, login, logout } from './educore-api-client.js'
 *
 *   // Login
 *   const { access, refresh, user } = await login('admin', 'Admin@1234')
 *
 *   // List students
 *   const { results, count } = await api.students.list({ search: 'Aarav', section: 1 })
 *
 *   // Admit student
 *   const student = await api.students.create({ first_name: 'Priya', ... })
 *
 *   // Bulk mark attendance
 *   await api.attendance.bulkMark({ section_id: 1, date: '2026-03-17', records: [...] })
 *
 *   // Download fee receipt as PDF (opens in new tab)
 *   api.reports.feeReceiptUrl(paymentId)  // returns URL string
 */

// ── Config ────────────────────────────────────────────────────────────────────
const BASE_URL = import.meta?.env?.VITE_API_URL
  ?? window.__EDUCORE_API_URL
  ?? '';                          // same-origin when served by Django

// ── Token storage ─────────────────────────────────────────────────────────────
const TOKEN_KEY   = 'educore_access';
const REFRESH_KEY = 'educore_refresh';

function getAccess()  { return localStorage.getItem(TOKEN_KEY); }
function getRefresh() { return localStorage.getItem(REFRESH_KEY); }
function setTokens(access, refresh) {
  localStorage.setItem(TOKEN_KEY, access);
  if (refresh) localStorage.setItem(REFRESH_KEY, refresh);
}
function clearTokens() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(REFRESH_KEY);
}

// ── Core fetch wrapper ────────────────────────────────────────────────────────
async function _fetch(path, options = {}, retry = true) {
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  const token = getAccess();
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const res = await fetch(`${BASE_URL}${path}`, { ...options, headers });

  // Auto-refresh on 401
  if (res.status === 401 && retry) {
    const refreshToken = getRefresh();
    if (!refreshToken) { clearTokens(); throw new AuthError('Session expired. Please log in again.'); }
    try {
      const refreshRes = await fetch(`${BASE_URL}/api/auth/refresh/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh: refreshToken }),
      });
      if (!refreshRes.ok) throw new Error();
      const { access } = await refreshRes.json();
      setTokens(access, null);
      return _fetch(path, options, false);   // retry once with new token
    } catch {
      clearTokens();
      throw new AuthError('Session expired. Please log in again.');
    }
  }

  if (!res.ok) {
    let errData = {};
    try { errData = await res.json(); } catch {}
    throw new ApiError(errData.message || 'Request failed', res.status, errData);
  }

  if (res.status === 204) return null;
  return res.json();
}

function _get(path, params = {}) {
  const qs = new URLSearchParams(
    Object.entries(params).filter(([, v]) => v !== undefined && v !== null && v !== '')
  ).toString();
  return _fetch(`${path}${qs ? '?' + qs : ''}`);
}
function _post(path, body)          { return _fetch(path, { method: 'POST',   body: JSON.stringify(body) }); }
function _patch(path, body)         { return _fetch(path, { method: 'PATCH',  body: JSON.stringify(body) }); }
function _put(path, body)           { return _fetch(path, { method: 'PUT',    body: JSON.stringify(body) }); }
function _del(path)                 { return _fetch(path, { method: 'DELETE' }); }

// ── Custom errors ─────────────────────────────────────────────────────────────
export class ApiError extends Error {
  constructor(message, status, data = {}) {
    super(message);
    this.name    = 'ApiError';
    this.status  = status;
    this.data    = data;
    this.details = data.details || {};
  }
}
export class AuthError extends Error {
  constructor(message) { super(message); this.name = 'AuthError'; }
}

// ── Auth ──────────────────────────────────────────────────────────────────────
export async function login(username, password) {
  const data = await _post('/api/auth/login/', { username, password });
  setTokens(data.access, data.refresh);
  return data;   // { access, refresh, user: { id, username, role, name } }
}

export async function logout() {
  const refresh = getRefresh();
  if (refresh) {
    try { await _post('/api/auth/logout/', { refresh }); } catch {}
  }
  clearTokens();
}

export function getCurrentUser() {
  return _get('/api/core/me/');
}

// ── API namespaces ────────────────────────────────────────────────────────────
export const api = {

  // Core / Dashboard
  dashboard: {
    stats: ()                => _get('/api/core/dashboard/'),
    grades: ()               => _get('/api/core/grades/'),
    sections: (params = {})  => _get('/api/core/sections/', params),
    schoolProfile: ()        => _get('/api/core/school/1/'),
    updateSchool: (id, data) => _patch(`/api/core/school/${id}/`, data),
    years: ()                => _get('/api/core/years/'),
  },

  // Students
  students: {
    list:       (params = {}) => _get('/api/students/', params),
    get:        (id)          => _get(`/api/students/${id}/`),
    create:     (data)        => _post('/api/students/', data),
    update:     (id, data)    => _patch(`/api/students/${id}/`, data),
    delete:     (id)          => _del(`/api/students/${id}/`),
    deactivate: (id)          => _post(`/api/students/${id}/deactivate/`),
    stats:      ()            => _get('/api/students/stats/'),
  },

  // Teachers
  teachers: {
    list:          (params = {}) => _get('/api/teachers/', params),
    get:           (id)          => _get(`/api/teachers/${id}/`),
    create:        (data)        => _post('/api/teachers/', data),
    update:        (id, data)    => _patch(`/api/teachers/${id}/`, data),
    schedule:      (id)          => _get(`/api/teachers/${id}/schedule/`),
    departments:   ()            => _get('/api/teachers/departments/'),
    subjects:      (params = {}) => _get('/api/teachers/subjects/', params),
    leaves: {
      list:    (params = {}) => _get('/api/teachers/leaves/', params),
      create:  (data)        => _post('/api/teachers/leaves/', data),
      approve: (id)          => _post(`/api/teachers/leaves/${id}/approve/`),
      reject:  (id)          => _post(`/api/teachers/leaves/${id}/reject/`),
    },
  },

  // Attendance
  attendance: {
    list:          (params = {}) => _get('/api/attendance/', params),
    bulkMark:      (data)        => _post('/api/attendance/bulk_mark/', data),
    todaySummary:  ()            => _get('/api/attendance/today_summary/'),
    sectionReport: (params)      => _get('/api/attendance/section_report/', params),
    holidays:      (params = {}) => _get('/api/attendance/holidays/', params),
    addHoliday:    (data)        => _post('/api/attendance/holidays/', data),
  },

  // Fees
  fees: {
    invoices: {
      list:       (params = {}) => _get('/api/fees/invoices/', params),
      get:        (id)          => _get(`/api/fees/invoices/${id}/`),
      create:     (data)        => _post('/api/fees/invoices/', data),
      summary:    ()            => _get('/api/fees/invoices/summary/'),
      markOverdue:()            => _post('/api/fees/invoices/mark_overdue/'),
    },
    payments: {
      list:   (params = {}) => _get('/api/fees/payments/', params),
      create: (data)        => _post('/api/fees/payments/', data),
    },
    structures:   (params = {}) => _get('/api/fees/structures/', params),
    categories:   ()            => _get('/api/fees/categories/'),
    scholarships: (params = {}) => _get('/api/fees/scholarships/', params),
  },

  // Exams
  exams: {
    list:          (params = {}) => _get('/api/exams/', params),
    get:           (id)          => _get(`/api/exams/${id}/`),
    create:        (data)        => _post('/api/exams/', data),
    schedules:     (params = {}) => _get('/api/exams/schedules/', params),
    results: {
      list:        (params = {}) => _get('/api/exams/results/', params),
      bulkEnter:   (data)        => _post('/api/exams/results/bulk_enter/', data),
      sectionReport: (params)    => _get('/api/exams/results/section_report/', params),
    },
    timetable:     (params = {}) => _get('/api/exams/timetable/', params),
  },

  // Library
  library: {
    books: {
      list:   (params = {}) => _get('/api/library/', params),
      get:    (id)          => _get(`/api/library/${id}/`),
      create: (data)        => _post('/api/library/', data),
      stats:  ()            => _get('/api/library/stats/'),
    },
    issues: {
      list:       (params = {}) => _get('/api/library/issues/', params),
      create:     (data)        => _post('/api/library/issues/', data),
      returnBook: (id)          => _post(`/api/library/issues/${id}/return_book/`),
    },
    categories: () => _get('/api/library/categories/'),
  },

  // Transport
  transport: {
    routes:   {
      list:   (params = {}) => _get('/api/transport/', params),
      get:    (id)          => _get(`/api/transport/${id}/`),
      create: (data)        => _post('/api/transport/', data),
    },
    vehicles: (params = {}) => _get('/api/transport/vehicles/', params),
    drivers:  (params = {}) => _get('/api/transport/drivers/', params),
    stops:    (params = {}) => _get('/api/transport/stops/', params),
    studentRoutes: {
      list:   (params = {}) => _get('/api/transport/student-routes/', params),
      assign: (data)        => _post('/api/transport/student-routes/', data),
    },
  },

  // Announcements
  announcements: {
    list:    (params = {}) => _get('/api/announcements/', params),
    get:     (id)          => _get(`/api/announcements/${id}/`),
    create:  (data)        => _post('/api/announcements/', data),
    update:  (id, data)    => _patch(`/api/announcements/${id}/`, data),
    delete:  (id)          => _del(`/api/announcements/${id}/`),
    notices: (params = {}) => _get('/api/announcements/notices/', params),
    events:  (params = {}) => _get('/api/announcements/events/', params),
  },

  // PDF report URLs (use as <a href={...}> or window.open)
  reports: {
    feeReceiptUrl:      (paymentId)           => `${BASE_URL}/api/reports/fee-receipt/${paymentId}/`,
    resultCardUrl:      (studentId, examId)   => `${BASE_URL}/api/reports/result-card/${studentId}/${examId}/`,
    attendanceUrl:      (sectionId, from, to) => `${BASE_URL}/api/reports/attendance/${sectionId}/?from_date=${from}&to_date=${to}`,
  },
};

export default api;
