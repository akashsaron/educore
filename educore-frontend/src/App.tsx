import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import { useAuthStore } from '@/store/authStore'
import { AppLayout } from '@/components/layout/AppLayout'
import { Suspense, lazy } from 'react'
import { PageSpinner } from '@/components/ui'
import Login from '@/pages/Login'

// Lazy-loaded pages
const Dashboard     = lazy(() => import('@/pages/dashboard/Dashboard'))
const Students      = lazy(() => import('@/pages/students/Students'))
const Fees          = lazy(() => import('@/pages/fees/Fees'))
const Teachers      = lazy(() => import('@/pages/teachers/Teachers'))
const Attendance    = lazy(() => import('@/pages/attendance/Attendance'))
const Exams         = lazy(() => import('@/pages/exams/Exams'))
const Library       = lazy(() => import('@/pages/library/Library'))
const Transport     = lazy(() => import('@/pages/transport/Transport'))
const Announcements = lazy(() => import('@/pages/announcements/Announcements'))
const Reports       = lazy(() => import('@/pages/reports/Reports'))
const Settings      = lazy(() => import('@/pages/settings/Settings'))
const Classes       = lazy(() => import('@/pages/classes/Classes'))
const Timetable     = lazy(() => import('@/pages/timetable/Timetable'))

const qc = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 2 * 60 * 1000,
      retry:     1,
    },
  },
})

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const isLoggedIn = useAuthStore(s => s.isLoggedIn)
  return isLoggedIn ? <>{children}</> : <Navigate to="/login" replace />
}

export default function App() {
  return (
    <QueryClientProvider client={qc}>
      <BrowserRouter>
        <Suspense fallback={<PageSpinner />}>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route element={<ProtectedRoute><AppLayout /></ProtectedRoute>}>
              <Route index          element={<Dashboard />} />
              <Route path="students"      element={<Students />} />
              <Route path="teachers"      element={<Teachers />} />
              <Route path="classes"       element={<Classes />} />
              <Route path="timetable"     element={<Timetable />} />
              <Route path="exams"         element={<Exams />} />
              <Route path="attendance"    element={<Attendance />} />
              <Route path="fees"          element={<Fees />} />
              <Route path="library"       element={<Library />} />
              <Route path="transport"     element={<Transport />} />
              <Route path="announcements" element={<Announcements />} />
              <Route path="reports"       element={<Reports />} />
              <Route path="settings"      element={<Settings />} />
              <Route path="*"             element={<Navigate to="/" replace />} />
            </Route>
          </Routes>
        </Suspense>
        <Toaster position="top-right" toastOptions={{
          style: { fontSize: 13, borderRadius: 10, boxShadow: '0 4px 20px rgba(0,0,0,0.1)' }
        }} />
      </BrowserRouter>
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  )
}
