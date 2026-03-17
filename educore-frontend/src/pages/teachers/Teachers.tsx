import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { teachersApi } from '@/utils/api'
import { StatCard, StatusBadge, Modal, Pagination, SearchInput, SkeletonRows, Empty, FormField } from '@/components/ui'
import toast from 'react-hot-toast'
import { UserPlus } from 'lucide-react'

export default function Teachers() {
  const [page, setPage]       = useState(1)
  const [search, setSearch]   = useState('')
  const [deptFilter, setDept] = useState('')
  const [activeTab, setTab]   = useState<'staff'|'leaves'|'departments'>('staff')
  const [showModal, setModal] = useState(false)
  const qc = useQueryClient()

  const { data: teachers, isLoading } = useQuery({
    queryKey: ['teachers', page, search, deptFilter],
    queryFn:  () => teachersApi.list({ page, search: search || undefined, department: deptFilter || undefined }),
    placeholderData: prev => prev,
  })
  const { data: departments } = useQuery({ queryKey: ['departments'], queryFn: teachersApi.departments })
  const { data: leaves, isLoading: leavesLoading } = useQuery({
    queryKey: ['leaves', page],
    queryFn:  () => teachersApi.leaves.list({ page }),
    enabled:  activeTab === 'leaves',
  })

  const approveMutation = useMutation({
    mutationFn: (id: number) => teachersApi.leaves.approve(id),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['leaves'] }); toast.success('Leave approved') },
  })
  const rejectMutation = useMutation({
    mutationFn: (id: number) => teachersApi.leaves.reject(id),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['leaves'] }); toast.error('Leave rejected') },
  })

  return (
    <div>
      <div className="page-header">
        <div><h1 className="page-title">Teaching Staff</h1><p className="page-sub">{teachers?.count ?? '…'} staff members</p></div>
        <button onClick={() => setModal(true)} className="btn btn-primary btn-sm"><UserPlus size={14} /> Add Staff</button>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <StatCard label="Total Staff"     value={teachers?.count ?? '—'} color="blue" />
        <StatCard label="Departments"     value={departments?.length ?? '—'} color="green" />
        <StatCard label="On Leave"        value={leaves?.results.filter(l => l.status === 'approved').length ?? '—'} color="orange" />
        <StatCard label="Pending Leaves"  value={leaves?.results.filter(l => l.status === 'pending').length ?? '—'} color="purple" />
      </div>

      <div className="card">
        <div className="tabs">
          {(['staff','leaves','departments'] as const).map(t => (
            <button key={t} onClick={() => { setTab(t); setPage(1) }}
              className={`tab capitalize ${activeTab === t ? 'active' : ''}`}>{t}</button>
          ))}
        </div>

        {activeTab === 'staff' && (
          <>
            <div className="flex gap-3 mb-4">
              <SearchInput value={search} onChange={v => { setSearch(v); setPage(1) }} placeholder="Search teachers…" />
              <select className="input-sm w-44" value={deptFilter} onChange={e => { setDept(e.target.value); setPage(1) }}>
                <option value="">All Departments</option>
                {departments?.map(d => <option key={d.id} value={d.id}>{d.name}</option>)}
              </select>
            </div>
            <table className="data-table">
              <thead><tr><th>Teacher</th><th>ID</th><th>Department</th><th>Subjects</th><th>Qual.</th><th>Exp.</th><th>Status</th><th></th></tr></thead>
              <tbody>
                {isLoading ? <SkeletonRows rows={8} cols={8} /> :
                  teachers?.results.length === 0 ? <tr><td colSpan={8}><Empty /></td></tr> :
                  teachers?.results.map(t => (
                    <tr key={t.id}>
                      <td>
                        <div className="flex items-center gap-2.5">
                          <div className="w-8 h-8 rounded-full bg-green-100 flex items-center justify-center text-green-700 text-xs font-bold flex-shrink-0">
                            {t.full_name.split(' ').map((w: string) => w[0]).join('').slice(0,2)}
                          </div>
                          <div>
                            <p className="font-medium text-primary leading-none">{t.full_name}</p>
                            <p className="text-xs text-muted mt-0.5">{t.email}</p>
                          </div>
                        </div>
                      </td>
                      <td className="font-mono text-xs text-muted">{t.employee_id}</td>
                      <td>{t.department_name}</td>
                      <td><div className="flex flex-wrap gap-1">{t.subject_names.slice(0,2).map((s: string) => <span key={s} className="badge-blue">{s}</span>)}{t.subject_names.length > 2 && <span className="badge-gray">+{t.subject_names.length-2}</span>}</div></td>
                      <td className="text-muted">{t.qualification||'—'}</td>
                      <td className="text-muted">{t.experience_years}y</td>
                      <td><StatusBadge status={t.is_active ? 'active' : 'inactive'} /></td>
                      <td><button className="btn btn-secondary btn-sm">View</button></td>
                    </tr>
                  ))
                }
              </tbody>
            </table>
            <Pagination count={teachers?.count ?? 0} page={page} onChange={setPage} />
          </>
        )}

        {activeTab === 'leaves' && (
          <>
            <table className="data-table">
              <thead><tr><th>Teacher</th><th>Type</th><th>From</th><th>To</th><th>Reason</th><th>Status</th><th>Action</th></tr></thead>
              <tbody>
                {leavesLoading ? <SkeletonRows rows={6} cols={7} /> :
                  leaves?.results.length === 0 ? <tr><td colSpan={7}><Empty message="No leave applications" /></td></tr> :
                  leaves?.results.map(l => (
                    <tr key={l.id}>
                      <td className="font-medium">{l.teacher_name}</td>
                      <td><span className="badge-blue capitalize">{l.leave_type.replace('_',' ')}</span></td>
                      <td className="text-muted">{l.from_date}</td>
                      <td className="text-muted">{l.to_date}</td>
                      <td className="text-muted max-w-xs truncate">{l.reason}</td>
                      <td><StatusBadge status={l.status} /></td>
                      <td>
                        {l.status === 'pending' && (
                          <div className="flex gap-1">
                            <button onClick={() => approveMutation.mutate(l.id)} disabled={approveMutation.isPending} className="btn btn-sm bg-success text-white border-0">✓</button>
                            <button onClick={() => rejectMutation.mutate(l.id)}  disabled={rejectMutation.isPending}  className="btn btn-danger btn-sm">✗</button>
                          </div>
                        )}
                      </td>
                    </tr>
                  ))
                }
              </tbody>
            </table>
            <Pagination count={leaves?.count ?? 0} page={page} onChange={setPage} />
          </>
        )}

        {activeTab === 'departments' && (
          <div className="grid grid-cols-2 lg:grid-cols-3 gap-4 pt-2">
            {departments?.map((d, i) => (
              <div key={d.id} className="p-4 rounded-xl border border-slate-100 hover:border-accent transition-colors cursor-pointer">
                <div className="text-2xl mb-2">{['📐','🔬','📖','🌍','💻'][i%5]}</div>
                <p className="font-semibold text-primary">{d.name}</p>
                <p className="text-sm text-muted mt-1">{d.teacher_count} teachers</p>
              </div>
            ))}
          </div>
        )}
      </div>

      <Modal open={showModal} onClose={() => setModal(false)} title="Add Staff Member" size="lg"
        footer={<><button onClick={() => setModal(false)} className="btn btn-secondary">Cancel</button><button className="btn btn-primary">Add Staff</button></>}>
        <div className="grid grid-cols-2 gap-x-4">
          <FormField label="First Name" required><input className="input" /></FormField>
          <FormField label="Last Name"  required><input className="input" /></FormField>
          <FormField label="Email" required><input type="email" className="input" /></FormField>
          <FormField label="Phone"><input className="input" /></FormField>
          <FormField label="Department" required>
            <select className="input"><option value="">Select</option>{departments?.map(d => <option key={d.id} value={d.id}>{d.name}</option>)}</select>
          </FormField>
          <FormField label="Qualification"><select className="input"><option>B.Ed</option><option>M.Ed</option><option>M.Sc</option><option>Ph.D</option></select></FormField>
          <FormField label="Joining Date" required><input type="date" className="input" /></FormField>
          <FormField label="Experience (yrs)"><input type="number" className="input" min="0" /></FormField>
          <div className="col-span-2"><FormField label="Initial Password" required><input type="password" className="input" /></FormField></div>
        </div>
      </Modal>
    </div>
  )
}
