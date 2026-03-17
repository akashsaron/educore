import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { examsApi } from '@/utils/api'
import { StatusBadge, StatCard, Modal, Pagination, SkeletonRows, Empty, FormField } from '@/components/ui'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'
import { Plus, Download, FileText } from 'lucide-react'

const GRADE_COLORS = ['#22c55e','#4f8ef7','#a855f7','#f59e0b','#f97316','#ef4444','#06b6d4']

export default function Exams() {
  const [activeTab, setTab]   = useState<'exams'|'results'|'analytics'>('exams')
  const [selExam, setExam]    = useState<number|null>(null)
  const [showModal, setModal] = useState(false)
  const [page, setPage]       = useState(1)

  const { data: exams, isLoading } = useQuery({ queryKey: ['exams', page], queryFn: () => examsApi.list({ page }), placeholderData: prev => prev })
  const { data: analytics } = useQuery({ queryKey: ['exam-analytics', selExam], queryFn: () => examsApi.analytics(selExam ?? undefined), enabled: activeTab === 'analytics' })

  return (
    <div>
      <div className="page-header">
        <div><h1 className="page-title">Exams & Results</h1><p className="page-sub">Annual Examination 2025–26</p></div>
        <div className="flex gap-2">
          {selExam && <a href={examsApi.exportUrl(selExam)} className="btn btn-secondary btn-sm" download><Download size={14}/> Export Results</a>}
          <button onClick={() => setModal(true)} className="btn btn-primary btn-sm"><Plus size={14}/> Schedule Exam</button>
        </div>
      </div>

      <div className="card">
        <div className="tabs">
          {(['exams','results','analytics'] as const).map(t => (
            <button key={t} onClick={() => setTab(t)} className={`tab capitalize ${activeTab===t?'active':''}`}>{t}</button>
          ))}
        </div>

        {activeTab === 'exams' && (
          <>
            <table className="data-table">
              <thead><tr><th>Exam Name</th><th>Type</th><th>Grades</th><th>Start Date</th><th>End Date</th><th>Max Marks</th><th>Status</th><th>Action</th></tr></thead>
              <tbody>
                {isLoading ? <SkeletonRows rows={6} cols={8}/> :
                  exams?.results.length === 0 ? <tr><td colSpan={8}><Empty/></td></tr> :
                  exams?.results.map(e => (
                    <tr key={e.id} className="cursor-pointer" onClick={() => { setExam(e.id); setTab('analytics') }}>
                      <td className="font-medium">{e.name}</td>
                      <td><span className="badge-blue capitalize">{e.exam_type.replace('_',' ')}</span></td>
                      <td className="text-muted text-xs">{e.grades.length} grade{e.grades.length!==1?'s':''}</td>
                      <td className="text-muted">{e.start_date}</td>
                      <td className="text-muted">{e.end_date}</td>
                      <td className="font-medium">{e.max_marks}</td>
                      <td><StatusBadge status={e.status}/></td>
                      <td>
                        <div className="flex gap-1">
                          <button className="btn btn-secondary btn-sm" onClick={ev => { ev.stopPropagation(); setExam(e.id) }}>Results</button>
                        </div>
                      </td>
                    </tr>
                  ))
                }
              </tbody>
            </table>
            <Pagination count={exams?.count ?? 0} page={page} onChange={setPage}/>
          </>
        )}

        {activeTab === 'results' && (
          <div>
            <div className="flex gap-3 mb-5">
              <select className="input-sm w-48" value={selExam ?? ''} onChange={e => setExam(Number(e.target.value)||null)}>
                <option value="">Select Exam</option>
                {exams?.results.map(e => <option key={e.id} value={e.id}>{e.name}</option>)}
              </select>
            </div>
            {!selExam ? <Empty message="Select an exam to view results"/> : (
              <ResultsTable examId={selExam}/>
            )}
          </div>
        )}

        {activeTab === 'analytics' && (
          <div>
            <div className="flex gap-3 mb-5">
              <select className="input-sm w-56" value={selExam ?? ''} onChange={e => setExam(Number(e.target.value)||null)}>
                <option value="">All Exams</option>
                {exams?.results.map(e => <option key={e.id} value={e.id}>{e.name}</option>)}
              </select>
            </div>
            {analytics && (
              <div className="grid lg:grid-cols-2 gap-6">
                <div>
                  <h4 className="text-sm font-semibold text-primary mb-3">Grade Distribution</h4>
                  <ResponsiveContainer width="100%" height={200}>
                    <BarChart data={analytics.grade_distribution} margin={{left:-20}}>
                      <XAxis dataKey="grade" tick={{fontSize:11,fill:'#6b7a99'}} axisLine={false} tickLine={false}/>
                      <YAxis tick={{fontSize:11,fill:'#6b7a99'}} axisLine={false} tickLine={false}/>
                      <Tooltip contentStyle={{fontSize:12,borderRadius:8}}/>
                      <Bar dataKey="count" radius={[4,4,0,0]}>
                        {analytics.grade_distribution.map((_,i) => <Cell key={i} fill={GRADE_COLORS[i%GRADE_COLORS.length]}/>)}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
                <div>
                  <h4 className="text-sm font-semibold text-primary mb-3">Pass / Fail</h4>
                  <div className="flex items-center justify-center h-48 gap-8">
                    <div className="text-center">
                      <div className="text-3xl font-bold text-success">{analytics.pass_fail.passed}</div>
                      <div className="text-xs text-muted mt-1">Passed</div>
                      <div className="text-lg font-semibold text-success">{analytics.pass_fail.pass_rate}%</div>
                    </div>
                    <div className="text-center">
                      <div className="text-3xl font-bold text-danger">{analytics.pass_fail.failed}</div>
                      <div className="text-xs text-muted mt-1">Failed</div>
                      <div className="text-lg font-semibold text-danger">{(100-analytics.pass_fail.pass_rate).toFixed(1)}%</div>
                    </div>
                  </div>
                </div>
                <div className="lg:col-span-2">
                  <h4 className="text-sm font-semibold text-primary mb-3">🏆 Top Students</h4>
                  <table className="data-table">
                    <thead><tr><th>Rank</th><th>Student</th><th>Class</th><th>Total Marks</th></tr></thead>
                    <tbody>
                      {analytics.top_students.map(s => (
                        <tr key={s.rank}>
                          <td><span className="font-bold text-warning">{s.rank <= 3 ? ['🥇','🥈','🥉'][s.rank-1] : s.rank}</span></td>
                          <td className="font-medium">{s.full_name}</td>
                          <td><span className="badge-blue">{s.grade_name}-{s.section}</span></td>
                          <td className="font-semibold">{s.total}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
            {!analytics && <Empty message="Select an exam to view analytics"/>}
          </div>
        )}
      </div>

      <Modal open={showModal} onClose={() => setModal(false)} title="Schedule Exam"
        footer={<><button onClick={() => setModal(false)} className="btn btn-secondary">Cancel</button><button className="btn btn-primary">Schedule</button></>}>
        <FormField label="Exam Name" required><input className="input" placeholder="e.g. Unit Test 3"/></FormField>
        <div className="grid grid-cols-2 gap-4">
          <FormField label="Type" required>
            <select className="input"><option value="unit_test">Unit Test</option><option value="mid_term">Mid Term</option><option value="final">Final Exam</option><option value="practical">Practical</option></select>
          </FormField>
          <FormField label="Max Marks" required><input type="number" className="input" defaultValue={100}/></FormField>
          <FormField label="Start Date" required><input type="date" className="input"/></FormField>
          <FormField label="End Date"   required><input type="date" className="input"/></FormField>
        </div>
        <FormField label="Pass Marks"><input type="number" className="input" defaultValue={35}/></FormField>
      </Modal>
    </div>
  )
}

function ResultsTable({ examId }: { examId: number }) {
  const { data, isLoading } = useQuery({
    queryKey: ['exam-results', examId],
    queryFn:  () => examsApi.results.list({ schedule__exam: examId }),
  })
  if (isLoading) return <div className="py-8 text-center text-muted text-sm">Loading results…</div>
  if (!data?.results.length) return <Empty message="No results entered yet"/>
  return (
    <>
      <table className="data-table">
        <thead><tr><th>Student</th><th>Subject</th><th>Max</th><th>Obtained</th><th>%</th><th>Grade</th><th>PDF</th></tr></thead>
        <tbody>
          {data.results.map(r => (
            <tr key={r.id}>
              <td className="font-medium">{r.student_name}</td>
              <td className="text-muted">{r.subject_name}</td>
              <td className="text-muted">{r.max_marks}</td>
              <td className={r.is_absent ? 'text-muted italic' : 'font-medium'}>{r.is_absent ? 'Absent' : r.marks_obtained}</td>
              <td className="text-muted">{r.is_absent ? '—' : `${r.percentage}%`}</td>
              <td><StatusBadge status={r.is_absent ? 'absent' : r.grade === 'F' ? 'failed' : 'present'}/></td>
              <td><a href={examsApi.resultCardUrl(r.student, examId)} target="_blank" rel="noopener" className="btn btn-secondary btn-sm"><FileText size={12}/></a></td>
            </tr>
          ))}
        </tbody>
      </table>
    </>
  )
}
