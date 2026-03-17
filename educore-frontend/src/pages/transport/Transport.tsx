import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { transportApi } from '@/utils/api'
import { StatCard, StatusBadge, Modal, SkeletonRows, Empty, FormField } from '@/components/ui'
import { Plus, Bus } from 'lucide-react'
import { clsx } from 'clsx'

export default function Transport() {
  const [activeTab, setTab]   = useState<'routes'|'vehicles'|'drivers'>('routes')
  const [showModal, setModal] = useState(false)

  const { data: routes, isLoading }   = useQuery({ queryKey: ['routes'],   queryFn: () => transportApi.routes.list() })
  const { data: vehicles }            = useQuery({ queryKey: ['vehicles'],  queryFn: () => transportApi.vehicles() })
  const { data: drivers }             = useQuery({ queryKey: ['drivers'],   queryFn: () => transportApi.drivers() })

  const totalStudents = routes?.results.reduce((a, r) => a + r.student_count, 0) ?? 0

  return (
    <div>
      <div className="page-header">
        <div><h1 className="page-title">Transport</h1><p className="page-sub">{routes?.count ?? '…'} routes · {totalStudents} students</p></div>
        <button onClick={() => setModal(true)} className="btn btn-primary btn-sm"><Plus size={14}/> Add Route</button>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <StatCard label="Total Routes"  value={routes?.count    ?? '—'} color="blue"/>
        <StatCard label="Vehicles"      value={vehicles?.count  ?? '—'} color="green"/>
        <StatCard label="Drivers"       value={drivers?.count   ?? '—'} color="orange"/>
        <StatCard label="Students"      value={totalStudents}            color="purple"/>
      </div>

      <div className="card">
        <div className="tabs">
          {(['routes','vehicles','drivers'] as const).map(t => (
            <button key={t} onClick={() => setTab(t)} className={`tab capitalize ${activeTab===t?'active':''}`}>{t}</button>
          ))}
        </div>

        {activeTab === 'routes' && (
          <table className="data-table">
            <thead><tr><th>Route</th><th>Code</th><th>Bus</th><th>Driver</th><th>Students</th><th>Morning</th><th>Evening</th><th>Status</th></tr></thead>
            <tbody>
              {isLoading ? <SkeletonRows rows={6} cols={8}/> :
                routes?.results.length === 0 ? <tr><td colSpan={8}><Empty/></td></tr> :
                routes?.results.map(r => (
                  <tr key={r.id}>
                    <td className="font-medium">{r.name}</td>
                    <td className="text-muted font-mono text-xs">{r.code}</td>
                    <td className="text-muted">{r.vehicle_no || '—'}</td>
                    <td>{r.driver_name || '—'}</td>
                    <td className="text-center font-medium">{r.student_count}</td>
                    <td className="text-muted">{r.morning_start}</td>
                    <td className="text-muted">{r.evening_start}</td>
                    <td><StatusBadge status={r.is_active ? 'active' : 'inactive'}/></td>
                  </tr>
                ))
              }
            </tbody>
          </table>
        )}

        {activeTab === 'vehicles' && (
          <table className="data-table">
            <thead><tr><th>Registration</th><th>Type</th><th>Capacity</th><th>Make/Model</th><th>Status</th></tr></thead>
            <tbody>
              {vehicles?.results.map(v => (
                <tr key={v.id}>
                  <td className="font-medium font-mono">{v.registration_no}</td>
                  <td className="text-muted">{v.vehicle_type}</td>
                  <td className="text-center">{v.capacity}</td>
                  <td className="text-muted">{(v as any).make_model || '—'}</td>
                  <td><StatusBadge status={v.status}/></td>
                </tr>
              ))}
            </tbody>
          </table>
        )}

        {activeTab === 'drivers' && (
          <table className="data-table">
            <thead><tr><th>Driver</th><th>License No.</th><th>License Expiry</th><th>Experience</th><th>Status</th></tr></thead>
            <tbody>
              {drivers?.results.map(d => (
                <tr key={d.id}>
                  <td className="font-medium">{d.full_name}</td>
                  <td className="text-muted font-mono">{d.license_no}</td>
                  <td className="text-muted">{d.license_expiry}</td>
                  <td className="text-muted">{(d as any).experience_yrs ?? '—'} yrs</td>
                  <td><StatusBadge status={d.is_active ? 'active' : 'inactive'}/></td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      <Modal open={showModal} onClose={() => setModal(false)} title="Add Route"
        footer={<><button onClick={() => setModal(false)} className="btn btn-secondary">Cancel</button><button className="btn btn-primary">Add Route</button></>}>
        <FormField label="Route Name" required><input className="input" placeholder="e.g. Route 5 — Indiranagar"/></FormField>
        <FormField label="Route Code" required><input className="input" placeholder="RT-05"/></FormField>
        <div className="grid grid-cols-2 gap-4">
          <FormField label="Morning Departure"><input type="time" className="input"/></FormField>
          <FormField label="Evening Departure"><input type="time" className="input"/></FormField>
          <FormField label="Vehicle">
            <select className="input"><option value="">Select vehicle</option>{vehicles?.results.map(v => <option key={v.id} value={v.id}>{v.registration_no}</option>)}</select>
          </FormField>
          <FormField label="Driver">
            <select className="input"><option value="">Select driver</option>{drivers?.results.map(d => <option key={d.id} value={d.id}>{d.full_name}</option>)}</select>
          </FormField>
        </div>
      </Modal>
    </div>
  )
}
