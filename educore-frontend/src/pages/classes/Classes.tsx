import { useQuery } from '@tanstack/react-query'
import { dashboardApi } from '@/utils/api'
import { PageSpinner } from '@/components/ui'

export default function Classes() {
  const { data: grades, isLoading } = useQuery({ queryKey: ['grades-full'], queryFn: dashboardApi.grades })
  const { data: sections }          = useQuery({ queryKey: ['sections'],    queryFn: () => dashboardApi.sections() })

  if (isLoading) return <PageSpinner/>

  return (
    <div>
      <div className="page-header">
        <div><h1 className="page-title">Classes & Sections</h1><p className="page-sub">{sections?.length ?? '…'} sections across {grades?.length ?? '…'} grades</p></div>
        <button className="btn btn-primary btn-sm">+ Add Class</button>
      </div>

      <div className="grid sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {grades?.map((g, i) => {
          const gradeSections = sections?.filter(s => s.grade === g.id) ?? []
          const colors = ['#4f8ef7','#22c55e','#a855f7','#f97316','#06b6d4','#f59e0b','#ef4444']
          const color = colors[i % colors.length]
          return (
            <div key={g.id} className="card hover:shadow-md transition-shadow cursor-pointer"
              style={{borderTop: `3px solid ${color}`}}>
              <div className="flex items-start justify-between mb-3">
                <div>
                  <h3 className="font-semibold text-primary">{g.name}</h3>
                  <p className="text-xs text-muted">{gradeSections.length} sections</p>
                </div>
                <div className="w-10 h-10 rounded-xl flex items-center justify-center text-white text-sm font-bold"
                  style={{background: color}}>
                  {g.numeric_grade}
                </div>
              </div>
              <div className="flex flex-wrap gap-1.5 mb-3">
                {gradeSections.map(s => (
                  <span key={s.id} className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs font-medium bg-slate-100 text-slate-600 hover:bg-slate-200 transition-colors">
                    {g.numeric_grade}-{s.name}
                    <span className="text-[10px] text-muted">({s.student_count})</span>
                  </span>
                ))}
              </div>
              <div className="border-t border-slate-50 pt-3">
                <div className="flex justify-between text-xs text-muted">
                  <span>Total students</span>
                  <span className="font-semibold text-primary">{gradeSections.reduce((a,s) => a + s.student_count, 0)}</span>
                </div>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
