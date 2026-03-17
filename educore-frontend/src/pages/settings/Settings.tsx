import { useQuery } from '@tanstack/react-query'
import { dashboardApi } from '@/utils/api'
import { FormField } from '@/components/ui'
import toast from 'react-hot-toast'

export default function Settings() {
  const { data: school } = useQuery({ queryKey: ['school'], queryFn: dashboardApi.school })
  const { data: years }  = useQuery({ queryKey: ['years'],  queryFn: dashboardApi.academicYears })

  return (
    <div>
      <div className="page-header">
        <div><h1 className="page-title">Settings</h1><p className="page-sub">School configuration</p></div>
      </div>

      <div className="grid lg:grid-cols-2 gap-5">
        <div className="card">
          <h3 className="text-sm font-semibold text-primary mb-5">🏫 School Profile</h3>
          <FormField label="School Name" required>
            <input className="input" defaultValue={school?.name ?? ''} placeholder="School name"/>
          </FormField>
          <FormField label="Principal Name" required>
            <input className="input" defaultValue={school?.principal_name ?? ''} placeholder="Principal name"/>
          </FormField>
          <div className="grid grid-cols-2 gap-4">
            <FormField label="Board">
              <select className="input" defaultValue={school?.board ?? 'CBSE'}>
                <option value="CBSE">CBSE</option><option value="ICSE">ICSE</option>
                <option value="STATE">State Board</option><option value="IB">IB</option>
              </select>
            </FormField>
            <FormField label="City">
              <input className="input" defaultValue={school?.city ?? ''} placeholder="City"/>
            </FormField>
          </div>
          <FormField label="Phone"><input className="input" defaultValue={school?.phone ?? ''}/></FormField>
          <FormField label="Email"><input type="email" className="input" defaultValue={school?.email ?? ''}/></FormField>
          <button onClick={() => toast.success('School profile saved!')} className="btn btn-primary mt-2">Save Changes</button>
        </div>

        <div className="space-y-5">
          <div className="card">
            <h3 className="text-sm font-semibold text-primary mb-5">⚙️ System Preferences</h3>
            <FormField label="Current Academic Year">
              <select className="input">
                {years?.map(y => <option key={y.id} value={y.id} selected={y.is_current}>{y.name}</option>)}
              </select>
            </FormField>
            <div className="grid grid-cols-2 gap-4">
              <FormField label="School Start Time">
                <input type="time" className="input" defaultValue="08:00"/>
              </FormField>
              <FormField label="School End Time">
                <input type="time" className="input" defaultValue="15:30"/>
              </FormField>
            </div>
            <button onClick={() => toast.success('Settings updated!')} className="btn btn-primary mt-2">Update Settings</button>
          </div>

          <div className="card">
            <h3 className="text-sm font-semibold text-primary mb-5">🔔 Notification Preferences</h3>
            {[
              { label: 'Fee overdue alerts',       desc: 'Email parents when fee is overdue' },
              { label: 'Attendance below 75%',     desc: 'Weekly low-attendance alert to parents' },
              { label: 'Birthday notifications',   desc: 'Daily birthday email to parents' },
              { label: 'Library overdue reminders',desc: 'Email borrowers with overdue books' },
            ].map(n => (
              <div key={n.label} className="flex items-start justify-between py-3 border-b border-slate-50 last:border-0">
                <div>
                  <p className="text-sm font-medium text-primary">{n.label}</p>
                  <p className="text-xs text-muted mt-0.5">{n.desc}</p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer ml-4 flex-shrink-0">
                  <input type="checkbox" defaultChecked className="sr-only peer"/>
                  <div className="w-10 h-5 bg-slate-200 rounded-full peer peer-checked:bg-accent transition-colors after:content-[''] after:absolute after:top-0.5 after:left-0.5 after:bg-white after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:after:translate-x-5"/>
                </label>
              </div>
            ))}
            <button onClick={() => toast.success('Notification preferences saved!')} className="btn btn-secondary btn-sm mt-3">Save Preferences</button>
          </div>
        </div>
      </div>
    </div>
  )
}
