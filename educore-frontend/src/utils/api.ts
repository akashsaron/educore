import axios, { type AxiosInstance } from 'axios'

// ── Axios instance ─────────────────────────────────────────────────────────
const api: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? '',
  headers: { 'Content-Type': 'application/json' },
  timeout: 30_000,
})

// ── Request interceptor — attach JWT ──────────────────────────────────────
api.interceptors.request.use(cfg => {
  const token = localStorage.getItem('educore_access')
  if (token) cfg.headers.Authorization = `Bearer ${token}`
  return cfg
})

// ── Response interceptor — auto-refresh on 401 ───────────────────────────
let isRefreshing = false
let queue: Array<(token: string) => void> = []

api.interceptors.response.use(
  res => res,
  async err => {
    const original = err.config
    if (err.response?.status !== 401 || original._retry) {
      return Promise.reject(err)
    }
    original._retry = true

    if (isRefreshing) {
      return new Promise(resolve => {
        queue.push((token: string) => {
          original.headers.Authorization = `Bearer ${token}`
          resolve(api(original))
        })
      })
    }

    isRefreshing = true
    const refresh = localStorage.getItem('educore_refresh')
    if (!refresh) {
      clearAuth()
      window.location.href = '/login'
      return Promise.reject(err)
    }

    try {
      const { data } = await axios.post('/api/auth/refresh/', { refresh })
      localStorage.setItem('educore_access', data.access)
      queue.forEach(cb => cb(data.access))
      queue = []
      original.headers.Authorization = `Bearer ${data.access}`
      return api(original)
    } catch {
      clearAuth()
      window.location.href = '/login'
      return Promise.reject(err)
    } finally {
      isRefreshing = false
    }
  }
)

export function clearAuth() {
  localStorage.removeItem('educore_access')
  localStorage.removeItem('educore_refresh')
}

export function setAuth(access: string, refresh: string) {
  localStorage.setItem('educore_access', access)
  localStorage.setItem('educore_refresh', refresh)
}

// ── Type helpers ──────────────────────────────────────────────────────────
export interface PaginatedResponse<T> {
  count:    number
  next:     string | null
  previous: string | null
  results:  T[]
}

type Params = Record<string, string | number | boolean | undefined | null>

const get  = <T>(url: string, params?: Params)       => api.get<T>(url, { params }).then(r => r.data)
const post = <T>(url: string, data?: unknown)         => api.post<T>(url, data).then(r => r.data)
const patch= <T>(url: string, data?: unknown)         => api.patch<T>(url, data).then(r => r.data)
const put  = <T>(url: string, data?: unknown)         => api.put<T>(url, data).then(r => r.data)
const del  = (url: string)                            => api.delete(url).then(r => r.data)

const list = <T>(url: string, params?: Params)        => get<PaginatedResponse<T>>(url, params)

// ── Auth ──────────────────────────────────────────────────────────────────
export const authApi = {
  login:   (username: string, password: string) =>
             post<{ access: string; refresh: string; user: AuthUser }>('/api/auth/login/', { username, password }),
  logout:  (refresh: string) => post('/api/auth/logout/', { refresh }),
  me:      () => get<AuthUser>('/api/core/me/'),
}

// ── Dashboard ─────────────────────────────────────────────────────────────
export const dashboardApi = {
  stats:          () => get<DashboardStats>('/api/core/dashboard/'),
  school:         () => get<SchoolProfile>('/api/core/school/1/'),
  grades:         () => get<Grade[]>('/api/core/grades/'),
  sections:       (params?: Params) => get<Section[]>('/api/core/sections/', params),
  academicYears:  () => get<AcademicYear[]>('/api/core/years/'),
}

// ── Students ──────────────────────────────────────────────────────────────
export const studentsApi = {
  list:       (params?: Params) => list<Student>('/api/students/', params),
  get:        (id: number)      => get<Student>(`/api/students/${id}/`),
  create:     (data: Partial<Student>) => post<Student>('/api/students/', data),
  update:     (id: number, data: Partial<Student>) => patch<Student>(`/api/students/${id}/`, data),
  delete:     (id: number)      => del(`/api/students/${id}/`),
  deactivate: (id: number)      => post(`/api/students/${id}/deactivate/`),
  export:     (params?: Params) => `/api/exports/students/?${new URLSearchParams(params as Record<string,string>)}`,
}

// ── Teachers ──────────────────────────────────────────────────────────────
export const teachersApi = {
  list:        (params?: Params) => list<Teacher>('/api/teachers/', params),
  get:         (id: number)      => get<Teacher>(`/api/teachers/${id}/`),
  create:      (data: Partial<Teacher>) => post<Teacher>('/api/teachers/', data),
  update:      (id: number, data: Partial<Teacher>) => patch<Teacher>(`/api/teachers/${id}/`, data),
  schedule:    (id: number)      => get<TimetableSlot[]>(`/api/teachers/${id}/schedule/`),
  departments: ()                => get<Department[]>('/api/teachers/departments/'),
  subjects:    (params?: Params) => get<Subject[]>('/api/teachers/subjects/', params),
  leaves: {
    list:    (params?: Params) => list<LeaveApplication>('/api/teachers/leaves/', params),
    create:  (data: Partial<LeaveApplication>) => post<LeaveApplication>('/api/teachers/leaves/', data),
    approve: (id: number) => post(`/api/teachers/leaves/${id}/approve/`),
    reject:  (id: number) => post(`/api/teachers/leaves/${id}/reject/`),
  },
}

// ── Attendance ────────────────────────────────────────────────────────────
export const attendanceApi = {
  list:          (params?: Params) => list<AttendanceRecord>('/api/attendance/', params),
  bulkMark:      (data: BulkMarkPayload) => post<{ created: number; updated: number }>('/api/attendance/bulk_mark/', data),
  todaySummary:  () => get<AttendanceSummary>('/api/attendance/today_summary/'),
  sectionReport: (params: Params)  => get<AttendanceSummaryRow[]>('/api/attendance/section_report/', params),
  holidays:      ()                => get<Holiday[]>('/api/attendance/holidays/'),
  analytics:     ()                => get<AttendanceAnalytics>('/api/analytics/attendance/'),
  exportUrl:     (sectionId: number, from: string, to: string) =>
                   `/api/exports/attendance/?section=${sectionId}&from_date=${from}&to_date=${to}`,
}

// ── Fees ──────────────────────────────────────────────────────────────────
export const feesApi = {
  invoices: {
    list:       (params?: Params) => list<FeeInvoice>('/api/fees/invoices/', params),
    get:        (id: number)      => get<FeeInvoice>(`/api/fees/invoices/${id}/`),
    create:     (data: Partial<FeeInvoice>) => post<FeeInvoice>('/api/fees/invoices/', data),
    summary:    () => get<FeeSummary>('/api/fees/invoices/summary/'),
    markOverdue:() => post('/api/fees/invoices/mark_overdue/'),
  },
  payments: {
    list:   (params?: Params) => list<FeePayment>('/api/fees/payments/', params),
    create: (data: Partial<FeePayment>) => post<FeePayment>('/api/fees/payments/', data),
    receiptUrl: (id: number)  => `/api/reports/fee-receipt/${id}/`,
  },
  structures:   (params?: Params) => list<FeeStructure>('/api/fees/structures/', params),
  categories:   () => get<FeeCategory[]>('/api/fees/categories/'),
  scholarships: (params?: Params) => list<Scholarship>('/api/fees/scholarships/', params),
  analytics:    () => get<FeeAnalytics>('/api/analytics/fees/'),
  exportUrl:    (from: string, to: string) => `/api/exports/fee-collection/?from_date=${from}&to_date=${to}`,
}

// ── Exams ─────────────────────────────────────────────────────────────────
export const examsApi = {
  list:     (params?: Params) => list<Exam>('/api/exams/', params),
  get:      (id: number)      => get<Exam>(`/api/exams/${id}/`),
  create:   (data: Partial<Exam>) => post<Exam>('/api/exams/', data),
  schedules:(params?: Params) => list<ExamSchedule>('/api/exams/schedules/', params),
  results: {
    list:        (params?: Params) => list<ExamResult>('/api/exams/results/', params),
    bulkEnter:   (data: { results: Partial<ExamResult>[] }) => post('/api/exams/results/bulk_enter/', data),
    sectionReport:(params: Params) => get<ExamResultReport>('/api/exams/results/section_report/', params),
  },
  timetable:  (params?: Params) => list<TimetableSlot>('/api/exams/timetable/', params),
  analytics:  (examId?: number) => get<ExamAnalytics>('/api/analytics/exams/', examId ? { exam_id: examId } : {}),
  resultCardUrl:(studentId: number, examId: number) => `/api/reports/result-card/${studentId}/${examId}/`,
  exportUrl:  (examId: number)  => `/api/exports/exam-results/?exam_id=${examId}`,
}

// ── Library ───────────────────────────────────────────────────────────────
export const libraryApi = {
  books: {
    list:   (params?: Params) => list<Book>('/api/library/', params),
    get:    (id: number)      => get<Book>(`/api/library/${id}/`),
    create: (data: Partial<Book>) => post<Book>('/api/library/', data),
    stats:  () => get<LibraryStats>('/api/library/stats/'),
  },
  issues: {
    list:       (params?: Params) => list<BookIssue>('/api/library/issues/', params),
    create:     (data: Partial<BookIssue>) => post<BookIssue>('/api/library/issues/', data),
    returnBook: (id: number) => post(`/api/library/issues/${id}/return_book/`),
  },
  categories: () => get<BookCategory[]>('/api/library/categories/'),
}

// ── Transport ─────────────────────────────────────────────────────────────
export const transportApi = {
  routes:   {
    list:   (params?: Params) => list<Route>('/api/transport/', params),
    get:    (id: number)      => get<Route>(`/api/transport/${id}/`),
    create: (data: Partial<Route>) => post<Route>('/api/transport/', data),
  },
  vehicles: (params?: Params) => list<Vehicle>('/api/transport/vehicles/', params),
  drivers:  (params?: Params) => list<Driver>('/api/transport/drivers/', params),
  studentRoutes: {
    list:   (params?: Params) => list<StudentRoute>('/api/transport/student-routes/', params),
    assign: (data: Partial<StudentRoute>) => post<StudentRoute>('/api/transport/student-routes/', data),
  },
}

// ── Announcements ─────────────────────────────────────────────────────────
export const announcementsApi = {
  list:    (params?: Params) => list<Announcement>('/api/announcements/', params),
  create:  (data: Partial<Announcement>) => post<Announcement>('/api/announcements/', data),
  update:  (id: number, data: Partial<Announcement>) => patch<Announcement>(`/api/announcements/${id}/`, data),
  delete:  (id: number) => del(`/api/announcements/${id}/`),
  notices: () => list<Notice>('/api/announcements/notices/'),
  events:  () => list<Event>('/api/announcements/events/'),
}

// ── Analytics ─────────────────────────────────────────────────────────────
export const analyticsApi = {
  demographics: () => get<DemographicsAnalytics>('/api/analytics/demographics/'),
}

// ── Type definitions ──────────────────────────────────────────────────────
export interface AuthUser {
  id: number; username: string; name: string; role: string; email: string
}
export interface DashboardStats {
  total_students: number; total_teachers: number; attendance_today: number
  present_today: number; absent_today: number
  fee_collected: number; fee_pending: number
  monthly_trend: { month: string; rate: number }[]
}
export interface SchoolProfile {
  id: number; name: string; board: string; principal_name: string
  city: string; phone: string; email: string
}
export interface Grade { id: number; name: string; numeric_grade: number; order: number; sections_count: number }
export interface Section { id: number; display_name: string; grade: number; grade_name: string; name: string; student_count: number }
export interface AcademicYear { id: number; name: string; start_date: string; end_date: string; is_current: boolean }
export interface Student {
  id: number; admission_no: string; first_name: string; last_name: string
  full_name: string; section: number; section_name: string; grade_name: string
  date_of_birth: string; gender: string; blood_group: string
  father_name: string; mother_name: string; parent_phone: string; parent_email: string
  address: string; city: string; pincode: string
  roll_number: string; admission_date: string; academic_year: number
  is_active: boolean; photo: string | null; remarks: string
}
export interface Teacher {
  id: number; employee_id: string; full_name: string; department: number
  department_name: string; subject_names: string[]; qualification: string
  experience_years: number; joining_date: string; phone: string; email: string
  is_active: boolean
}
export interface Department { id: number; name: string; teacher_count: number }
export interface Subject { id: number; name: string; code: string; department: number; department_name: string }
export interface LeaveApplication {
  id: number; teacher: number; teacher_name: string; leave_type: string
  from_date: string; to_date: string; reason: string; status: string; applied_at: string
}
export interface AttendanceRecord {
  id: number; student: number; student_name: string; section_name: string
  date: string; status: string; remarks: string
}
export interface BulkMarkPayload {
  section_id: number; date: string
  records: { student_id: number; status: string; remarks?: string }[]
}
export interface AttendanceSummary { date: string; present: number; absent: number; late: number; total: number }
export interface AttendanceSummaryRow {
  student_id: number; student_name: string; admission_no: string
  total_days: number; present: number; absent: number; percentage: number
}
export interface Holiday { id: number; date: string; name: string; holiday_type: string }
export interface AttendanceAnalytics {
  monthly_trend: { label: string; rate: number; present: number; total: number }[]
  grade_summary: { grade: string; rate: number }[]
  daily_heatmap: { date: string; day: number; rate: number; present: number; absent: number }[]
}
export interface FeeInvoice {
  id: number; invoice_no: string; student: number; student_name: string
  section_name: string; category_name: string; amount_due: number
  amount_paid: number; balance_due: number; status: string
  due_date: string; payments: FeePayment[]
}
export interface FeePayment {
  id: number; receipt_no: string; invoice: number; amount: number
  payment_method: string; paid_date: string; status: string
}
export interface FeeSummary {
  total_due: number; total_paid: number; this_month: number
  pending: number; overdue_count: number
}
export interface FeeStructure {
  id: number; academic_year: number; grade: number; grade_name: string
  category: number; category_name: string; term: string; amount: number; due_date: string
}
export interface FeeCategory { id: number; name: string; is_mandatory: boolean }
export interface Scholarship { id: number; student: number; student_name: string; name: string; amount: number; awarded_date: string }
export interface FeeAnalytics {
  monthly_collection: { label: string; collected: number }[]
  by_category: { category: string; total: number }[]
  status_split: { status: string; count: number; amount: number }[]
  pending_by_grade: { grade: string; pending: number }[]
}
export interface Exam {
  id: number; name: string; exam_type: string; academic_year: number
  grades: number[]; start_date: string; end_date: string; status: string
  max_marks: number; pass_marks: number
  schedules: ExamSchedule[]
}
export interface ExamSchedule {
  id: number; exam: number; subject: number; subject_name: string
  grade: number; grade_name: string; date: string; start_time: string
  end_time: string; max_marks: number; pass_marks: number; venue: string
}
export interface ExamResult {
  id: number; schedule: number; student: number; student_name: string
  subject_name: string; admission_no: string; marks_obtained: number
  max_marks: number; percentage: number; grade: string; is_absent: boolean
}
export interface ExamResultReport {
  stats: { avg: number; highest: number; lowest: number; passed: number; total: number }
  results: ExamResult[]
}
export interface TimetableSlot {
  id: number; section: number; section_name: string; subject: number; subject_name: string
  teacher: number; teacher_name: string; day_of_week: number; day_name: string
  period_number: number; start_time: string; end_time: string
}
export interface ExamAnalytics {
  grade_distribution: { grade: string; count: number }[]
  subject_averages: { subject: string; avg: number }[]
  top_students: { rank: number; full_name: string; section: string; grade_name: string; total: number }[]
  pass_fail: { total: number; passed: number; failed: number; pass_rate: number }
}
export interface Book {
  id: number; title: string; author: string; isbn: string; category: number
  category_name: string; publisher: string; total_copies: number; available: number; rack_no: string
}
export interface BookIssue {
  id: number; book: number; book_title: string; borrower: number; borrower_name: string
  issued_on: string; due_date: string; returned_on: string | null
  status: string; fine_amount: number
}
export interface BookCategory { id: number; name: string }
export interface LibraryStats { total: number; available: number; borrowed: number; overdue: number }
export interface Route {
  id: number; name: string; code: string; vehicle: number; vehicle_no: string
  driver: number; driver_name: string; morning_start: string; evening_start: string
  student_count: number; is_active: boolean; stops: RouteStop[]
}
export interface RouteStop { id: number; route: number; stop_name: string; order: number; pickup_time: string; drop_time: string }
export interface Vehicle { id: number; registration_no: string; vehicle_type: string; capacity: number; status: string }
export interface Driver { id: number; full_name: string; license_no: string; license_expiry: string; is_active: boolean }
export interface StudentRoute { id: number; student: number; student_name: string; route: number; route_name: string; stop: number; stop_name: string; is_active: boolean }
export interface Announcement {
  id: number; title: string; content: string; priority: string
  audience: string; is_published: boolean; publish_date: string
  created_by_name: string; expiry_date: string | null
}
export interface Notice { id: number; title: string; content: string; is_pinned: boolean; created_at: string }
export interface Event { id: number; title: string; event_type: string; start_date: string; end_date: string; venue: string; is_holiday: boolean }
export interface DemographicsAnalytics {
  by_grade: { grade: string; count: number }[]
  by_gender: { gender: string; label: string; count: number }[]
  admission_trend: { label: string; admissions: number }[]
  total_active: number; total_inactive: number
}

export default api
