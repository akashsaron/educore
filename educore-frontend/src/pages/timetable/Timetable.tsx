import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { examsApi, dashboardApi } from '@/utils/api'
import { PageSpinner, Empty } from '@/components/ui'
import { clsx } from 'clsx'
import { Printer } from 'lucide-react'

const DAYS   = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday']
const SUBJ_COLORS: Record<string, string> = {
  'Mathematics':      'bg-blue-500',   'Algebra':          'bg-blue-500',
  'Science':          'bg-green-500',  'Physics':          'bg-green-600',
  'Chemistry':        'bg-teal-500',   'Biology':          'bg-emerald-500',
  'English':          'bg-purple-500', 'Literature':       'bg-purple-600',
  'Social Studies':   'bg-orange-500', 'History':          'bg-orange-600',
  'Computer Science': 'bg-cyan-500',   'Programming':      'bg-cyan-600',
  'Hindi':            'bg-pink-500',   'Art':              'bg-rose-500',
  'Sports':           'bg-yellow-500',
}
const getColor = (name: string) => {
  for (const [key, val] of Object.entries(SUBJ_COLORS)) {
    if (name.toLowerCase().includes(key.toLowerCase())) return val
  }
  return 'bg-slate-500'
}

export default function Timetable() {
  const [selSection, setSection] = useState('')
  const { data: sections } = useQuery({ queryKey: ['sections'], queryFn: () => dashboardApi.sections() })
  const { data: slots, isLoading } = useQuery({
    queryKey: ['timetable', selSection],
    queryFn:  () => examsApi.timetable({ section: selSection }),
    enabled:  !!selSection,
  })

  // Group slots by day and period
  const grid: Record<number, Record<number, typeof slots extends {results: infer T} ? T[0] : never>> = {}
  slots?.results.forEach(s => {
    if (!grid[s.day_of_week]) grid[s.day_of_week] = {}
    grid[s.day_of_week][s.period_number] = s
  })
  const maxPeriod = Math.max(0, ...Object.values(grid).flatMap(d => Object.keys(d).map(Number)))

  return (
    <div>
      <div className="page-header">
        <div><h1 className="page-title">Timetable</h1><p className="page-sub">Weekly class schedule</p></div>
        <div className="flex gap-2">
          <select className="input-sm w-48" value={selSection} onChange={e => setSection(e.target.value)}>
            <option value="">Select Section</option>
            {sections?.map(s => <option key={s.id} value={s.id}>{s.display_name}</option>)}
          </select>
          <button className="btn btn-secondary btn-sm" onClick={() => window.print()}>
            <Printer size={14}/> Print
          </button>
        </div>
      </div>

      {!selSection ? (
        <div className="card"><Empty message="Select a section to view its timetable"/></div>
      ) : isLoading ? <PageSpinner/> : (
        <div className="card overflow-x-auto">
          <table className="w-full text-xs">
            <thead>
              <tr>
                <th className="p-2 text-left text-muted font-medium w-24">Period</th>
                {DAYS.map(d => (
                  <th key={d} className="p-2 text-center font-medium text-primary">{d}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {Array.from({length: maxPeriod || 8}, (_, i) => i + 1).map(period => (
                <tr key={period} className="border-t border-slate-50">
                  <td className="p-2 text-muted text-center font-medium">P{period}</td>
                  {DAYS.map((_, dayIdx) => {
                    const dayNum = dayIdx + 1
                    const slot = grid[dayNum]?.[period]
                    return (
                      <td key={dayNum} className="p-1.5">
                        {slot ? (
                          <div className={clsx('rounded-lg p-2 text-white cursor-pointer hover:opacity-90 transition-opacity', getColor(slot.subject_name))}>
                            <div className="font-semibold leading-tight">{slot.subject_name}</div>
                            <div className="opacity-80 text-[10px] mt-0.5 truncate">{slot.teacher_name?.split(' ').slice(-1)[0]}</div>
                            {slot.start_time && (
                              <div className="opacity-70 text-[10px]">{slot.start_time.slice(0,5)}</div>
                            )}
                          </div>
                        ) : (
                          <div className="rounded-lg p-2 bg-slate-50 text-slate-300 text-center min-h-[52px]"/>
                        )}
                      </td>
                    )
                  })}
                </tr>
              ))}
            </tbody>
          </table>

          {maxPeriod === 0 && <Empty message="No timetable configured for this section"/>}

          {/* Legend */}
          {maxPeriod > 0 && (
            <div className="flex flex-wrap gap-2 pt-4 border-t border-slate-100 mt-4">
              {Object.entries(SUBJ_COLORS).slice(0,8).map(([name, color]) => (
                <div key={name} className="flex items-center gap-1.5">
                  <div className={clsx('w-3 h-3 rounded', color)}/>
                  <span className="text-xs text-muted">{name}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
