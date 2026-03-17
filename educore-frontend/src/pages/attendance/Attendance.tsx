import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { attendanceApi, studentsApi, dashboardApi } from '@/utils/api'
import { StatCard, Modal, Empty, FormField } from '@/components/ui'
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts'
import toast from 'react-hot-toast'
import { format } from 'date-fns'
import { Download, CheckSquare } from 'lucide-react'
import { clsx } from 'clsx'

type AttStatus = 'present'|'absent'|'late'|'excused'
const STATUS_COLORS: Record<AttStatus, string> = {
  present: 'bg-green-100 text-green-700 border-green-200',
  absent:  'bg-red-100   text-red-700   border-red-200',
  late:    'bg-yellow-100 text-yellow-700 border-yellow-200',
  excused: 'bg-gray-100  text-gray-600  border-gray-200',
}

export default function Attendance() {
  const today = format(new Date(), 'yyyy-MM-dd')
  const [activeTab, setTab]     = useState<'today'|'section'|'analytics'>('today')
  const [showModal, setModal]   = useState(false)
  const [selSection, setSection]= useState('')
  const [selDate, setDate]      = useState(today)
  const [markStatus, setStatuses] = useState<Record<number, AttStatus>>({})
  const qc = useQueryClient()

  const { data: summary }   = useQuery({ queryKey: ['att-today'],     queryFn: attendanceApi.todaySummary, refetchInterval: 30_000 })
  const { data: analytics } = useQuery({ queryKey: ['att-analytics'], queryFn: attendanceApi.analytics, enabled: activeTab === 'analytics' })
  const { data: sections }  = useQuery({ queryKey: ['sections'],      queryFn: () => dashboardApi.sections() })
  const { data: sectionStudents } = useQuery({
    queryKey: ['students-section', selSection],
    queryFn:  () => studentsApi.list({ section: selSection, is_active: true }),
    enabled:  !!selSection,
  })
  const { data: sectionReport } = useQuery({
    queryKey: ['att-section-report', selSection, selDate],
    queryFn:  () => attendanceApi.sectionReport({ section: selSection, from_date: selDate, to_date: selDate }),
    enabled:  !!selSection && activeTab === 'section',
  })

  const bulkMutation = useMutation({
    mutationFn: () => attendanceApi.bulkMark({
      section_id: Number(selSection), date: selDate,
      records: Object.entries(markStatus).map(([sid, status]) => ({ student_id: Number(sid), status }))
    }),
    onSuccess: (data) => { qc.invalidateQueries({ queryKey: ['att-today'] }); toast.success(`Saved — ${data.created} new, ${data.updated} updated`); setModal(false) },
    onError: () => toast.error('Failed to save attendance'),
  })

  const toggleStatus = (id: number) => {
    const cycle: AttStatus[] = ['present','absent','late','excused']
    const cur = markStatus[id] ?? 'present'
    setStatuses(prev => ({ ...prev, [id]: cycle[(cycle.indexOf(cur)+1)%cycle.length] }))
  }
  const initAll = () => {
    if (!sectionStudents) return
    const init: Record<number, AttStatus> = {}
    sectionStudents.results.forEach(s => { init[s.id] = 'present' })
    setStatuses(init)
  }

  const heatColors = ['#e2e8f0','#bfdbfe','#60a5fa','#2563eb','#1e3a8a']
  const getHeat = (r: number) => r === 0 ? heatColors[0] : r < 70 ? heatColors[1] : r < 85 ? heatColors[2] : r < 95 ? heatColors[3] : heatColors[4]

  return (
    <div>
      <div className="page-header">
        <div><h1 className="page-title">Attendance</h1><p className="page-sub">{format(new Date(),'EEEE, MMMM d, yyyy')}</p></div>
        <div className="flex gap-2">
          {selSection && <a href={attendanceApi.exportUrl(Number(selSection), selDate, selDate)} className="btn btn-secondary btn-sm" download><Download size={14}/> Export</a>}
          <button onClick={() => setModal(true)} className="btn btn-primary btn-sm"><CheckSquare size={14}/> Mark Attendance</button>
        </div>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <StatCard label="Present Today" value={summary?.present ?? '—'} color="green" sub={`${summary?.total ? Math.round((summary.present/summary.total)*100):0}%`} />
        <StatCard label="Absent"        value={summary?.absent  ?? '—'} color="red" />
        <StatCard label="Late"          value={summary?.late    ?? '—'} color="orange" />
        <StatCard label="Total Marked"  value={summary?.total   ?? '—'} color="blue" />
      </div>

      <div className="card">
        <div className="tabs">
          {(['today','section','analytics'] as const).map(t => (
            <button key={t} onClick={() => setTab(t)} className={`tab capitalize ${activeTab===t?'active':''}`}>{t}</button>
          ))}
        </div>

        {activeTab === 'today' && (
          <div>
            <div className="flex gap-3 mb-5">
              <select className="input-sm w-48" value={selSection} onChange={e => setSection(e.target.value)}>
                <option value="">All Sections</option>
                {sections?.map(s => <option key={s.id} value={s.id}>{s.display_name}</option>)}
              </select>
            </div>
            {!selSection ? <Empty message="Select a section to view attendance" /> : (
              <table className="data-table">
                <thead><tr><th>#</th><th>Student</th><th>Adm. No.</th><th>Status</th></tr></thead>
                <tbody>
                  {sectionStudents?.results.map((s, i) => (
                    <tr key={s.id}>
                      <td className="text-muted">{i+1}</td>
                      <td className="font-medium">{s.full_name}</td>
                      <td className="text-muted font-mono text-xs">{s.admission_no}</td>
                      <td><span className={clsx('badge', STATUS_COLORS[markStatus[s.id]??'present'])}>{markStatus[s.id]??'present'}</span></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        )}

        {activeTab === 'section' && (
          <div>
            <div className="flex flex-wrap gap-3 mb-5">
              <select className="input-sm w-48" value={selSection} onChange={e => setSection(e.target.value)}>
                <option value="">Select Section</option>
                {sections?.map(s => <option key={s.id} value={s.id}>{s.display_name}</option>)}
              </select>
              <input type="date" className="input-sm" value={selDate} onChange={e => setDate(e.target.value)} />
            </div>
            {!selSection ? <Empty message="Select a section and date" /> : (
              <table className="data-table">
                <thead><tr><th>Student</th><th>Present</th><th>Absent</th><th>Total</th><th>Attendance %</th></tr></thead>
                <tbody>
                  {(sectionReport as any[])?.map((r: any) => (
                    <tr key={r.student_id}>
                      <td className="font-medium">{r.student_name}</td>
                      <td className="text-success font-medium">{r.present}</td>
                      <td className="text-danger font-medium">{r.absent}</td>
                      <td className="text-muted">{r.total_days}</td>
                      <td>
                        <div className="flex items-center gap-2">
                          <div className="flex-1 h-1.5 bg-slate-100 rounded-full overflow-hidden">
                            <div className={clsx('h-full rounded-full', r.percentage>=90?'bg-success':r.percentage>=75?'bg-warning':'bg-danger')} style={{width:`${r.percentage}%`}} />
                          </div>
                          <span className="text-xs text-muted w-10 text-right">{r.percentage}%</span>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        )}

        {activeTab === 'analytics' && analytics && (
          <div className="space-y-6">
            <div>
              <h4 className="text-sm font-semibold text-primary mb-3">Monthly Trend</h4>
              <ResponsiveContainer width="100%" height={180}>
                <AreaChart data={analytics.monthly_trend} margin={{left:-20}}>
                  <defs><linearGradient id="ag" x1="0" y1="0" x2="0" y2="1"><stop offset="5%" stopColor="#4f8ef7" stopOpacity={0.2}/><stop offset="95%" stopColor="#4f8ef7" stopOpacity={0}/></linearGradient></defs>
                  <XAxis dataKey="label" tick={{fontSize:11,fill:'#6b7a99'}} axisLine={false} tickLine={false}/>
                  <YAxis domain={[70,100]} tick={{fontSize:11,fill:'#6b7a99'}} axisLine={false} tickLine={false}/>
                  <Tooltip contentStyle={{fontSize:12,borderRadius:8}} formatter={(v:number)=>[`${v}%`,'Rate']}/>
                  <Area type="monotone" dataKey="rate" stroke="#4f8ef7" strokeWidth={2} fill="url(#ag)" dot={{r:3,fill:'#4f8ef7'}}/>
                </AreaChart>
              </ResponsiveContainer>
            </div>
            <div>
              <h4 className="text-sm font-semibold text-primary mb-3">Grade-wise (%)</h4>
              <ResponsiveContainer width="100%" height={160}>
                <BarChart data={analytics.grade_summary} margin={{left:-20}}>
                  <XAxis dataKey="grade" tick={{fontSize:11,fill:'#6b7a99'}} axisLine={false} tickLine={false}/>
                  <YAxis domain={[0,100]} tick={{fontSize:11,fill:'#6b7a99'}} axisLine={false} tickLine={false}/>
                  <Tooltip contentStyle={{fontSize:12,borderRadius:8}} formatter={(v:number)=>[`${v}%`,'Rate']}/>
                  <Bar dataKey="rate" fill="#22c55e" radius={[4,4,0,0]}/>
                </BarChart>
              </ResponsiveContainer>
            </div>
            <div>
              <h4 className="text-sm font-semibold text-primary mb-3">Daily Heatmap</h4>
              <div className="flex flex-wrap gap-1.5">
                {analytics.daily_heatmap.map(d => (
                  <div key={d.date} title={`${d.date}: ${d.rate}%`}
                    className="w-8 h-8 rounded-lg flex items-center justify-center text-xs font-medium cursor-pointer hover:scale-110 transition-transform"
                    style={{background:getHeat(d.rate),color:d.rate>=85?'#fff':'#374151'}}>
                    {d.day}
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>

      <Modal open={showModal} onClose={() => setModal(false)} title="Mark Attendance" size="lg"
        footer={<>
          <button onClick={() => setModal(false)} className="btn btn-secondary">Cancel</button>
          <button onClick={() => bulkMutation.mutate()} disabled={bulkMutation.isPending || Object.keys(markStatus).length===0} className="btn btn-primary">
            {bulkMutation.isPending ? 'Saving…' : `Save (${Object.keys(markStatus).length} students)`}
          </button>
        </>}>
        <div className="grid grid-cols-2 gap-4 mb-4">
          <FormField label="Section" required>
            <select className="input" value={selSection} onChange={e => { setSection(e.target.value); setStatuses({}) }}>
              <option value="">Select section</option>
              {sections?.map(s => <option key={s.id} value={s.id}>{s.display_name}</option>)}
            </select>
          </FormField>
          <FormField label="Date" required>
            <input type="date" className="input" value={selDate} onChange={e => setDate(e.target.value)} />
          </FormField>
        </div>
        {selSection && sectionStudents ? (
          <>
            <div className="flex items-center justify-between mb-3">
              <p className="text-xs text-muted">Tap to cycle: P → A → L → E</p>
              <button onClick={initAll} className="text-xs text-accent hover:underline">Mark All Present</button>
            </div>
            <div className="grid grid-cols-3 sm:grid-cols-4 gap-2 max-h-64 overflow-y-auto">
              {sectionStudents.results.map(s => {
                const st = markStatus[s.id] ?? 'present'
                return (
                  <button key={s.id} onClick={() => toggleStatus(s.id)}
                    className={clsx('p-2.5 rounded-xl border text-center transition-all hover:scale-105', STATUS_COLORS[st])}>
                    <div className="text-xs font-bold">{s.first_name[0]}{s.last_name[0]}</div>
                    <div className="text-xs mt-0.5 truncate">{s.first_name}</div>
                    <div className="text-[10px] mt-0.5 font-semibold capitalize">{st[0].toUpperCase()}</div>
                  </button>
                )
              })}
            </div>
            {Object.keys(markStatus).length === 0 && (
              <div className="text-center mt-3"><button onClick={initAll} className="btn btn-secondary btn-sm">Load Students</button></div>
            )}
          </>
        ) : <Empty message="Select a section to load students" />}
      </Modal>
    </div>
  )
}
