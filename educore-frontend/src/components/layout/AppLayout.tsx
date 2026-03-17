import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import { useState } from 'react'
import {
  LayoutDashboard, Users, GraduationCap, BookOpen, ClipboardCheck,
  CreditCard, School, Calendar, Truck, Megaphone, BarChart2,
  Settings, LogOut, Bell, Search, Menu, X
} from 'lucide-react'
import { useAuthStore } from '@/store/authStore'
import { clsx } from 'clsx'

const NAV = [
  { group: 'Overview',
    items: [{ to: '/', icon: LayoutDashboard, label: 'Dashboard' }] },
  { group: 'Academics',
    items: [
      { to: '/students',    icon: GraduationCap, label: 'Students',  badge: '' },
      { to: '/teachers',    icon: Users,          label: 'Teachers' },
      { to: '/classes',     icon: School,         label: 'Classes' },
      { to: '/timetable',   icon: Calendar,       label: 'Timetable' },
      { to: '/exams',       icon: ClipboardCheck, label: 'Exams & Results' },
    ] },
  { group: 'Administration',
    items: [
      { to: '/attendance',  icon: ClipboardCheck, label: 'Attendance' },
      { to: '/fees',        icon: CreditCard,     label: 'Fee Management' },
      { to: '/library',     icon: BookOpen,       label: 'Library' },
      { to: '/transport',   icon: Truck,          label: 'Transport' },
    ] },
  { group: 'Communication',
    items: [
      { to: '/announcements', icon: Megaphone, label: 'Announcements' },
    ] },
  { group: 'System',
    items: [
      { to: '/reports',  icon: BarChart2, label: 'Reports' },
      { to: '/settings', icon: Settings,  label: 'Settings' },
    ] },
]

function Sidebar({ collapsed, onClose }: { collapsed?: boolean; onClose?: () => void }) {
  const { user, logout } = useAuthStore()
  const navigate = useNavigate()

  const handleLogout = async () => {
    await logout()
    navigate('/login')
  }

  return (
    <aside className="flex flex-col h-full bg-primary w-60 flex-shrink-0">
      {/* Logo */}
      <div className="px-5 py-5 border-b border-white/10">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-accent flex items-center justify-center text-white text-lg">🎓</div>
          <div>
            <div className="font-display text-white text-lg leading-none">EduCore</div>
            <div className="text-white/40 text-[10px] uppercase tracking-widest mt-0.5">School ERP</div>
          </div>
          {onClose && (
            <button onClick={onClose} className="ml-auto text-white/40 hover:text-white lg:hidden">
              <X size={18} />
            </button>
          )}
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 overflow-y-auto py-3 px-2">
        {NAV.map(group => (
          <div key={group.group} className="mb-2">
            <p className="text-white/30 text-[10px] font-medium uppercase tracking-widest px-3 py-1.5">{group.group}</p>
            {group.items.map(item => (
              <NavLink key={item.to} to={item.to} end={item.to === '/'}
                className={({ isActive }) => clsx('nav-item', isActive && 'active')}
                onClick={onClose}>
                <item.icon size={16} className="flex-shrink-0" />
                <span className="flex-1">{item.label}</span>
              </NavLink>
            ))}
          </div>
        ))}
      </nav>

      {/* User */}
      <div className="px-3 py-4 border-t border-white/10">
        <div className="flex items-center gap-3 px-2">
          <div className="w-8 h-8 rounded-full bg-accent/30 flex items-center justify-center text-white text-xs font-bold">
            {user?.name?.split(' ').map(w => w[0]).join('').slice(0,2) ?? 'AD'}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-white text-sm font-medium truncate">{user?.name ?? 'Admin'}</p>
            <p className="text-white/40 text-xs capitalize">{user?.role?.replace('_', ' ') ?? ''}</p>
          </div>
          <button onClick={handleLogout} className="text-white/40 hover:text-danger transition-colors" title="Logout">
            <LogOut size={16} />
          </button>
        </div>
      </div>
    </aside>
  )
}

export function AppLayout() {
  const [mobileOpen, setMobileOpen] = useState(false)

  return (
    <div className="flex h-screen overflow-hidden bg-surface">
      {/* Desktop sidebar */}
      <div className="hidden lg:flex">
        <Sidebar />
      </div>

      {/* Mobile sidebar overlay */}
      {mobileOpen && (
        <div className="fixed inset-0 z-50 lg:hidden flex">
          <div className="absolute inset-0 bg-black/50" onClick={() => setMobileOpen(false)} />
          <div className="relative z-10">
            <Sidebar onClose={() => setMobileOpen(false)} />
          </div>
        </div>
      )}

      {/* Main area */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Topbar */}
        <header className="flex items-center h-14 px-5 bg-white border-b border-slate-100 gap-4 flex-shrink-0">
          <button className="lg:hidden btn-icon" onClick={() => setMobileOpen(true)}>
            <Menu size={20} />
          </button>

          <div className="relative hidden sm:block">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted" />
            <input placeholder="Search students, teachers…" className="input pl-9 w-56 text-sm" />
          </div>

          <div className="ml-auto flex items-center gap-2">
            <button className="btn-icon relative">
              <Bell size={18} className="text-muted" />
              <span className="absolute top-1.5 right-1.5 w-1.5 h-1.5 bg-danger rounded-full" />
            </button>
            <button className="btn btn-primary btn-sm hidden sm:flex">+ Quick Add</button>
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-y-auto p-5 lg:p-7">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
