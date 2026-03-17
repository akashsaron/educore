import { useQuery } from '@tanstack/react-query'
import { dashboardApi, announcementsApi } from '@/utils/api'
import { StatCard, PageSpinner } from '@/components/ui'
import {
  AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, Tooltip, ResponsiveContainer, Legend
} from 'recharts'
import { format, parseISO } from 'date-fns'

const COLORS = ['#4f8ef7', '#22c55e', '#f97316', '#a855f7', '#ef4444']

export default function Dashboard() {
  const { data: stats, isLoading } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn:  dashboardApi.stats,
    refetchInterval: 60_000,
  })
  const { data: events } = useQuery({
    queryKey: ['events'],
    queryFn:  () => announcementsApi.events(),
  })
  const { data: announcements } = useQuery({
    queryKey: ['announcements-recent'],
    queryFn:  () => announcementsApi.list({ is_published: true }),
  })

  if (isLoading) return <PageSpinner />

  const today = new Date()

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="page-title">Good Morning 👋</h1>
          <p className="page-sub">{format(today, 'EEEE, MMMM d, yyyy')} · Term 2</p>
        </div>
        <div className="flex gap-2">
          <button className="btn btn-secondary btn-sm">📥 Download Report</button>
          <button className="btn btn-primary btn-sm">+ Add Student</button>
        </div>
      </div>

      {/* KPI Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard label="Total Students"    value={stats?.total_students?.toLocaleString() ?? '—'}
          sub={`Active enrollment`} color="blue" icon="👨‍🎓" />
        <StatCard label="Teaching Staff"    value={stats?.total_teachers ?? '—'}
          sub="Staff members" color="green" icon="👩‍🏫" />
        <StatCard label="Today's Attendance" value={`${stats?.attendance_today ?? '—'}%`}
          sub={`${stats?.present_today} present · ${stats?.absent_today} absent`}
          color="orange" icon="✅"
          trend={{ value: 'vs yesterday', up: (stats?.attendance_today ?? 0) >= 90 }} />
        <StatCard label="Fee Collection"
          value={`₹${((stats?.fee_collected ?? 0) / 100000).toFixed(1)}L`}
          sub={`₹${((stats?.fee_pending ?? 0) / 100000).toFixed(1)}L pending`}
          color="purple" icon="💳" />
      </div>

      {/* Charts row */}
      <div className="grid lg:grid-cols-3 gap-5">
        {/* Attendance trend */}
        <div className="card lg:col-span-2">
          <h3 className="text-sm font-semibold text-primary mb-4">📊 Monthly Attendance Trend</h3>
          <ResponsiveContainer width="100%" height={200}>
            <AreaChart data={stats?.monthly_trend ?? []} margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
              <defs>
                <linearGradient id="attGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%"  stopColor="#4f8ef7" stopOpacity={0.15} />
                  <stop offset="95%" stopColor="#4f8ef7" stopOpacity={0} />
                </linearGradient>
              </defs>
              <XAxis dataKey="month" tick={{ fontSize: 11, fill: '#6b7a99' }} axisLine={false} tickLine={false} />
              <YAxis domain={[70, 100]} tick={{ fontSize: 11, fill: '#6b7a99' }} axisLine={false} tickLine={false} />
              <Tooltip
                contentStyle={{ fontSize: 12, borderRadius: 8, border: '1px solid #e2e8f0' }}
                formatter={(v: number) => [`${v}%`, 'Attendance']}
              />
              <Area type="monotone" dataKey="rate" stroke="#4f8ef7" strokeWidth={2}
                fill="url(#attGrad)" dot={{ fill: '#4f8ef7', r: 3 }} activeDot={{ r: 5 }} />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Quick actions */}
        <div className="card">
          <h3 className="text-sm font-semibold text-primary mb-4">⚡ Quick Actions</h3>
          <div className="grid grid-cols-2 gap-2">
            {[
              { icon: '✅', label: 'Attendance',   href: '/attendance' },
              { icon: '➕', label: 'Admit Student', href: '/students' },
              { icon: '💳', label: 'Collect Fee',   href: '/fees' },
              { icon: '📝', label: 'Enter Marks',   href: '/exams' },
              { icon: '📣', label: 'Announce',       href: '/announcements' },
              { icon: '📊', label: 'Reports',        href: '/reports' },
            ].map(a => (
              <a key={a.label} href={a.href}
                className="flex flex-col items-center gap-1.5 p-3 rounded-xl border border-slate-100
                           hover:border-accent hover:bg-blue-50/50 transition-all cursor-pointer text-center">
                <span className="text-xl">{a.icon}</span>
                <span className="text-xs font-medium text-primary">{a.label}</span>
              </a>
            ))}
          </div>
        </div>
      </div>

      {/* Bottom row */}
      <div className="grid lg:grid-cols-2 gap-5">
        {/* Events */}
        <div className="card">
          <h3 className="text-sm font-semibold text-primary mb-4">📅 Upcoming Events</h3>
          <div className="space-y-3">
            {events?.results?.slice(0, 5).map(ev => (
              <div key={ev.id} className="flex items-start gap-3 py-2 border-b border-slate-50 last:border-0">
                <div className="w-10 h-10 rounded-lg bg-accent/10 flex flex-col items-center justify-center flex-shrink-0">
                  <span className="text-accent text-sm font-bold leading-none">
                    {format(parseISO(ev.start_date), 'd')}
                  </span>
                  <span className="text-accent/70 text-[10px]">
                    {format(parseISO(ev.start_date), 'MMM')}
                  </span>
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-primary truncate">{ev.title}</p>
                  <p className="text-xs text-muted">{ev.venue || ev.event_type}</p>
                </div>
                <span className={`badge-${
                  ev.event_type === 'exam' ? 'red' :
                  ev.event_type === 'holiday' ? 'orange' :
                  ev.event_type === 'sports' ? 'green' : 'blue'
                }`}>{ev.event_type}</span>
              </div>
            )) ?? (
              <p className="text-xs text-muted text-center py-8">No upcoming events</p>
            )}
          </div>
        </div>

        {/* Recent announcements */}
        <div className="card">
          <h3 className="text-sm font-semibold text-primary mb-4">📣 Recent Announcements</h3>
          <div className="space-y-1">
            {announcements?.results?.slice(0, 5).map(ann => (
              <div key={ann.id} className="py-2.5 border-b border-slate-50 last:border-0">
                <div className="flex items-start justify-between gap-2 mb-1">
                  <p className="text-sm font-medium text-primary leading-snug">{ann.title}</p>
                  <span className={`badge-${
                    ann.priority === 'urgent' ? 'red' :
                    ann.priority === 'high'   ? 'orange' : 'gray'
                  } flex-shrink-0`}>{ann.priority}</span>
                </div>
                <p className="text-xs text-muted">{ann.audience} · {ann.publish_date}</p>
              </div>
            )) ?? (
              <p className="text-xs text-muted text-center py-8">No announcements</p>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
