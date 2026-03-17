import { useQuery } from '@tanstack/react-query'
import { analyticsApi, studentsApi, dashboardApi, examsApi } from '@/utils/api'
import { StatCard, PageSpinner } from '@/components/ui'
import { BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, Tooltip, ResponsiveContainer, LineChart, Line, Legend } from 'recharts'
import { Download } from 'lucide-react'

const COLORS = ['#4f8ef7','#22c55e','#f97316','#a855f7','#ef4444','#f59e0b','#06b6d4']

export default function Reports() {
  const { data: demo, isLoading }  = useQuery({ queryKey: ['demographics'],   queryFn: analyticsApi.demographics })
  const { data: exams }            = useQuery({ queryKey: ['exams-list'],      queryFn: () => examsApi.list({}) })

  if (isLoading) return <PageSpinner/>

  return (
    <div>
      <div className="page-header">
        <div><h1 className="page-title">Reports & Analytics</h1><p className="page-sub">School-wide insights</p></div>
      </div>

      {/* Quick download cards */}
      <div className="grid grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
        {[
          { icon:'👨‍🎓', label:'Student Register',   sub:'Full admission list',         href:'/api/exports/students/' },
          { icon:'✅',    label:'Attendance Report', sub:'Monthly attendance register', href:'/api/exports/attendance/' },
          { icon:'💳',    label:'Fee Collection',    sub:'Payment ledger',              href:'/api/exports/fee-collection/' },
          { icon:'📝',    label:'Exam Results',      sub:'Marksheet export',            href:'/api/exports/exam-results/' },
          { icon:'📊',    label:'Analytics PDF',     sub:'Dashboard summary',           href:'#' },
          { icon:'📚',    label:'Library Report',    sub:'Borrowed & overdue',          href:'#' },
        ].map(r => (
          <a key={r.label} href={r.href} download={r.href.startsWith('/api')}
            className="card hover:border-accent transition-colors cursor-pointer flex items-start gap-4 no-underline group">
            <div className="text-3xl">{r.icon}</div>
            <div className="flex-1">
              <p className="font-semibold text-primary text-sm group-hover:text-accent transition-colors">{r.label}</p>
              <p className="text-xs text-muted mt-0.5">{r.sub}</p>
            </div>
            <Download size={16} className="text-muted group-hover:text-accent transition-colors flex-shrink-0 mt-0.5"/>
          </a>
        ))}
      </div>

      {/* Charts */}
      {demo && (
        <div className="grid lg:grid-cols-2 gap-5">
          <div className="card">
            <h3 className="text-sm font-semibold text-primary mb-4">Students by Grade</h3>
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={demo.by_grade} margin={{left:-20}}>
                <XAxis dataKey="grade" tick={{fontSize:11,fill:'#6b7a99'}} axisLine={false} tickLine={false}/>
                <YAxis tick={{fontSize:11,fill:'#6b7a99'}} axisLine={false} tickLine={false}/>
                <Tooltip contentStyle={{fontSize:12,borderRadius:8}}/>
                <Bar dataKey="count" radius={[4,4,0,0]}>
                  {demo.by_grade.map((_,i) => <Cell key={i} fill={COLORS[i%COLORS.length]}/>)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="card">
            <h3 className="text-sm font-semibold text-primary mb-4">Gender Distribution</h3>
            <div className="flex items-center justify-center gap-8 h-48">
              <ResponsiveContainer width={180} height={180}>
                <PieChart>
                  <Pie data={demo.by_gender} dataKey="count" nameKey="label" cx="50%" cy="50%"
                    innerRadius={50} outerRadius={80} paddingAngle={3}>
                    {demo.by_gender.map((_,i) => <Cell key={i} fill={COLORS[i]}/>)}
                  </Pie>
                  <Tooltip contentStyle={{fontSize:12,borderRadius:8}}/>
                </PieChart>
              </ResponsiveContainer>
              <div className="space-y-3">
                {demo.by_gender.map((g,i) => (
                  <div key={g.gender} className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full" style={{background:COLORS[i]}}/>
                    <span className="text-sm text-primary font-medium">{g.label}</span>
                    <span className="text-sm text-muted ml-2">{g.count}</span>
                  </div>
                ))}
                <div className="pt-2 border-t border-slate-100">
                  <span className="text-xs text-muted">Total active: </span>
                  <span className="text-xs font-semibold text-primary">{demo.total_active}</span>
                </div>
              </div>
            </div>
          </div>

          <div className="card lg:col-span-2">
            <h3 className="text-sm font-semibold text-primary mb-4">Monthly Admissions Trend</h3>
            <ResponsiveContainer width="100%" height={200}>
              <LineChart data={demo.admission_trend} margin={{left:-20,right:10}}>
                <XAxis dataKey="label" tick={{fontSize:11,fill:'#6b7a99'}} axisLine={false} tickLine={false}/>
                <YAxis tick={{fontSize:11,fill:'#6b7a99'}} axisLine={false} tickLine={false}/>
                <Tooltip contentStyle={{fontSize:12,borderRadius:8}}/>
                <Line type="monotone" dataKey="admissions" stroke="#4f8ef7" strokeWidth={2}
                  dot={{r:4,fill:'#4f8ef7'}} activeDot={{r:6}}/>
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}
    </div>
  )
}
