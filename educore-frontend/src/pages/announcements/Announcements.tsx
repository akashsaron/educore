import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { announcementsApi } from '@/utils/api'
import { StatusBadge, Modal, Pagination, SkeletonRows, Empty, FormField } from '@/components/ui'
import { clsx } from 'clsx'
import toast from 'react-hot-toast'
import { Plus, Pin, Calendar } from 'lucide-react'
import { format, parseISO } from 'date-fns'

const PRIORITY_COLORS: Record<string, string> = {
  urgent: 'border-l-red-500',  high: 'border-l-orange-500',
  normal: 'border-l-blue-500', low:  'border-l-gray-300',
}

export default function Announcements() {
  const [activeTab, setTab]   = useState<'announcements'|'notices'|'events'>('announcements')
  const [showModal, setModal] = useState(false)
  const [page, setPage]       = useState(1)
  const qc = useQueryClient()

  const { data: announcements, isLoading } = useQuery({
    queryKey: ['announcements', page],
    queryFn:  () => announcementsApi.list({ page, is_published: true }),
    placeholderData: prev => prev,
  })
  const { data: notices } = useQuery({ queryKey: ['notices'], queryFn: () => announcementsApi.notices(), enabled: activeTab === 'notices' })
  const { data: events }  = useQuery({ queryKey: ['events'],  queryFn: () => announcementsApi.events(),  enabled: activeTab === 'events' })

  const createMutation = useMutation({
    mutationFn: (data: any) => announcementsApi.create(data),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['announcements'] }); toast.success('Announcement posted!'); setModal(false) },
  })

  return (
    <div>
      <div className="page-header">
        <div><h1 className="page-title">Announcements</h1><p className="page-sub">School communications</p></div>
        <button onClick={() => setModal(true)} className="btn btn-primary btn-sm"><Plus size={14}/> New Announcement</button>
      </div>

      <div className="card">
        <div className="tabs">
          {(['announcements','notices','events'] as const).map(t => (
            <button key={t} onClick={() => { setTab(t); setPage(1) }} className={`tab capitalize ${activeTab===t?'active':''}`}>{t}</button>
          ))}
        </div>

        {activeTab === 'announcements' && (
          <>
            <div className="space-y-3">
              {isLoading ? (
                [1,2,3,4].map(i => <div key={i} className="skeleton h-20 rounded-xl"/>)
              ) : announcements?.results.length === 0 ? <Empty message="No announcements"/> :
              announcements?.results.map(ann => (
                <div key={ann.id} className={clsx('border-l-4 pl-4 py-3 pr-4 rounded-r-xl bg-slate-50/60', PRIORITY_COLORS[ann.priority] ?? 'border-l-gray-300')}>
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex-1">
                      <h4 className="font-semibold text-primary text-sm">{ann.title}</h4>
                      <p className="text-xs text-muted mt-1 line-clamp-2">{ann.content}</p>
                      <div className="flex items-center gap-3 mt-2">
                        <span className="text-xs text-muted">{ann.publish_date}</span>
                        <span className="badge-gray capitalize">{ann.audience}</span>
                        <span className="text-xs text-muted">by {ann.created_by_name}</span>
                      </div>
                    </div>
                    <span className={clsx('badge flex-shrink-0', ann.priority==='urgent'?'badge-red':ann.priority==='high'?'badge-orange':'badge-gray')}>
                      {ann.priority}
                    </span>
                  </div>
                </div>
              ))}
            </div>
            <Pagination count={announcements?.count ?? 0} page={page} onChange={setPage}/>
          </>
        )}

        {activeTab === 'notices' && (
          <div className="space-y-2">
            {notices?.results.length === 0 ? <Empty message="Notice board is empty"/> :
              notices?.results.map(n => (
                <div key={n.id} className="flex items-start gap-3 py-3 border-b border-slate-50 last:border-0">
                  {n.is_pinned && <Pin size={14} className="text-accent flex-shrink-0 mt-0.5"/>}
                  <div>
                    <p className="text-sm font-medium text-primary">{n.title}</p>
                    <p className="text-xs text-muted mt-0.5 line-clamp-2">{n.content}</p>
                    <p className="text-xs text-muted mt-1">{format(parseISO(n.created_at), 'MMM d, yyyy')}</p>
                  </div>
                </div>
              ))
            }
          </div>
        )}

        {activeTab === 'events' && (
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4 pt-2">
            {events?.results.length === 0 ? <div className="col-span-3"><Empty message="No events scheduled"/></div> :
              events?.results.map(ev => {
                const typeColor: Record<string,string> = { academic:'blue', sports:'green', cultural:'purple', exam:'red', holiday:'orange', meeting:'gray', other:'gray' }
                const col = typeColor[ev.event_type] ?? 'gray'
                return (
                  <div key={ev.id} className="border border-slate-100 rounded-xl p-4 hover:border-accent transition-colors">
                    <div className="flex items-start justify-between mb-2">
                      <span className={`badge-${col} capitalize`}>{ev.event_type}</span>
                      {ev.is_holiday && <span className="badge-orange">Holiday</span>}
                    </div>
                    <h4 className="font-semibold text-primary text-sm">{ev.title}</h4>
                    <div className="flex items-center gap-1.5 mt-2 text-xs text-muted">
                      <Calendar size={12}/>
                      <span>{ev.start_date}{ev.end_date !== ev.start_date ? ` → ${ev.end_date}` : ''}</span>
                    </div>
                    {ev.venue && <p className="text-xs text-muted mt-1">📍 {ev.venue}</p>}
                  </div>
                )
              })
            }
          </div>
        )}
      </div>

      <Modal open={showModal} onClose={() => setModal(false)} title="New Announcement"
        footer={<><button onClick={() => setModal(false)} className="btn btn-secondary">Cancel</button><button className="btn btn-primary">Post</button></>}>
        <FormField label="Title" required><input className="input" placeholder="Announcement title"/></FormField>
        <FormField label="Content" required><textarea className="input" rows={4} placeholder="Write your announcement…"/></FormField>
        <div className="grid grid-cols-2 gap-4">
          <FormField label="Audience">
            <select className="input"><option value="all">Everyone</option><option value="students">Students</option><option value="teachers">Teachers</option><option value="parents">Parents</option></select>
          </FormField>
          <FormField label="Priority">
            <select className="input"><option value="normal">Normal</option><option value="high">High</option><option value="urgent">Urgent</option></select>
          </FormField>
        </div>
      </Modal>
    </div>
  )
}
