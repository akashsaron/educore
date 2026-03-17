import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { studentsApi, dashboardApi, type Student } from '@/utils/api'
import {
  StatusBadge, Modal, PageSpinner, Pagination,
  SearchInput, SkeletonRows, FormField, Empty
} from '@/components/ui'
import { UserPlus, Download, Filter } from 'lucide-react'
import toast from 'react-hot-toast'

const schema = z.object({
  first_name:    z.string().min(1, 'Required'),
  last_name:     z.string().min(1, 'Required'),
  date_of_birth: z.string().min(1, 'Required'),
  gender:        z.enum(['M','F','O']),
  section:       z.coerce.number().min(1, 'Required'),
  academic_year: z.coerce.number().min(1, 'Required'),
  admission_date:z.string().min(1, 'Required'),
  roll_number:   z.string().optional(),
  father_name:   z.string().min(1, 'Required'),
  parent_phone:  z.string().min(10, 'Valid phone required'),
  parent_email:  z.string().email('Valid email').optional().or(z.literal('')),
  address:       z.string().min(1, 'Required'),
  city:          z.string().min(1, 'Required'),
  pincode:       z.string().min(6, 'Required'),
})
type FormData = z.infer<typeof schema>

export default function Students() {
  const [page, setPage]         = useState(1)
  const [search, setSearch]     = useState('')
  const [section, setSection]   = useState('')
  const [showModal, setModal]   = useState(false)
  const [activeTab, setTab]     = useState<'all'|'active'|'inactive'>('all')
  const qc = useQueryClient()

  const { data: sections } = useQuery({ queryKey: ['sections'], queryFn: () => dashboardApi.sections() })
  const { data: years }    = useQuery({ queryKey: ['years'],    queryFn: () => dashboardApi.academicYears() })
  const currentYear        = years?.find(y => y.is_current)

  const params = {
    page, search: search || undefined,
    section: section || undefined,
    is_active: activeTab === 'active' ? true : activeTab === 'inactive' ? false : undefined,
  }
  const { data, isLoading } = useQuery({
    queryKey: ['students', params],
    queryFn:  () => studentsApi.list(params),
    placeholderData: prev => prev,
  })

  const { register, handleSubmit, reset, formState: { errors, isSubmitting } } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: {
      admission_date: new Date().toISOString().slice(0, 10),
      academic_year:  currentYear?.id,
    }
  })

  const createMutation = useMutation({
    mutationFn: (data: FormData) => studentsApi.create(data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['students'] })
      toast.success('Student admitted successfully!')
      setModal(false)
      reset()
    },
    onError: (err: any) => {
      toast.error(err?.response?.data?.message ?? 'Failed to admit student')
    }
  })

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Students</h1>
          <p className="page-sub">{data?.count?.toLocaleString() ?? '…'} enrolled students</p>
        </div>
        <div className="flex gap-2">
          <a href={studentsApi.export({ section, is_active: activeTab !== 'all' ? activeTab === 'active' : undefined })}
             className="btn btn-secondary btn-sm" download>
            <Download size={14} /> Export
          </a>
          <button onClick={() => setModal(true)} className="btn btn-primary btn-sm">
            <UserPlus size={14} /> Admit Student
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="card mb-5">
        <div className="flex flex-wrap items-center gap-3 mb-4">
          <div className="tabs !mb-0 !border-0 gap-0">
            {(['all','active','inactive'] as const).map(t => (
              <button key={t} onClick={() => { setTab(t); setPage(1) }}
                className={`tab !py-1.5 capitalize ${activeTab === t ? 'active' : ''}`}>
                {t}
              </button>
            ))}
          </div>
          <div className="ml-auto flex gap-2">
            <SearchInput value={search} onChange={v => { setSearch(v); setPage(1) }} placeholder="Search students…" />
            <select className="input-sm w-36"
              value={section} onChange={e => { setSection(e.target.value); setPage(1) }}>
              <option value="">All Sections</option>
              {sections?.map(s => (
                <option key={s.id} value={s.id}>{s.display_name}</option>
              ))}
            </select>
          </div>
        </div>

        <table className="data-table">
          <thead>
            <tr>
              <th>Student</th><th>Adm. No.</th><th>Class</th>
              <th>Parent</th><th>Phone</th><th>Admission</th><th>Status</th><th>Action</th>
            </tr>
          </thead>
          <tbody>
            {isLoading ? <SkeletonRows rows={8} cols={8} /> :
              data?.results.length === 0 ? (
                <tr><td colSpan={8}><Empty message="No students found" /></td></tr>
              ) : data?.results.map(s => (
                <tr key={s.id}>
                  <td>
                    <div className="flex items-center gap-2.5">
                      <div className="w-8 h-8 rounded-full bg-accent/15 flex items-center justify-center text-accent text-xs font-bold flex-shrink-0">
                        {s.first_name[0]}{s.last_name[0]}
                      </div>
                      <div>
                        <p className="font-medium text-primary leading-none">{s.full_name}</p>
                        <p className="text-xs text-muted mt-0.5">{s.grade_name}</p>
                      </div>
                    </div>
                  </td>
                  <td className="text-muted font-mono text-xs">{s.admission_no}</td>
                  <td><span className="badge-blue">{s.section_name}</span></td>
                  <td className="text-muted">{s.father_name}</td>
                  <td className="text-muted">{s.parent_phone}</td>
                  <td className="text-muted">{s.admission_date}</td>
                  <td><StatusBadge status={s.is_active ? 'active' : 'inactive'} /></td>
                  <td>
                    <button className="btn btn-secondary btn-sm">View</button>
                  </td>
                </tr>
              ))
            }
          </tbody>
        </table>
        <Pagination count={data?.count ?? 0} page={page} onChange={setPage} />
      </div>

      {/* Add Student Modal */}
      <Modal open={showModal} onClose={() => { setModal(false); reset() }} title="Admit New Student" size="lg"
        footer={<>
          <button onClick={() => { setModal(false); reset() }} className="btn btn-secondary">Cancel</button>
          <button onClick={handleSubmit(d => createMutation.mutate(d))} disabled={isSubmitting || createMutation.isPending} className="btn btn-primary">
            {createMutation.isPending ? 'Admitting…' : 'Admit Student'}
          </button>
        </>}>
        <div className="grid grid-cols-2 gap-x-4">
          <FormField label="First Name" error={errors.first_name?.message} required>
            <input {...register('first_name')} className="input" placeholder="First name" />
          </FormField>
          <FormField label="Last Name" error={errors.last_name?.message} required>
            <input {...register('last_name')} className="input" placeholder="Last name" />
          </FormField>
          <FormField label="Date of Birth" error={errors.date_of_birth?.message} required>
            <input {...register('date_of_birth')} type="date" className="input" />
          </FormField>
          <FormField label="Gender" error={errors.gender?.message} required>
            <select {...register('gender')} className="input">
              <option value="M">Male</option>
              <option value="F">Female</option>
              <option value="O">Other</option>
            </select>
          </FormField>
          <FormField label="Section" error={errors.section?.message} required>
            <select {...register('section')} className="input">
              <option value="">Select section</option>
              {sections?.map(s => <option key={s.id} value={s.id}>{s.display_name}</option>)}
            </select>
          </FormField>
          <FormField label="Admission Date" error={errors.admission_date?.message} required>
            <input {...register('admission_date')} type="date" className="input" />
          </FormField>
          <FormField label="Father's Name" error={errors.father_name?.message} required>
            <input {...register('father_name')} className="input" placeholder="Father full name" />
          </FormField>
          <FormField label="Parent Phone" error={errors.parent_phone?.message} required>
            <input {...register('parent_phone')} className="input" placeholder="+91 00000 00000" />
          </FormField>
          <div className="col-span-2">
            <FormField label="Parent Email" error={errors.parent_email?.message}>
              <input {...register('parent_email')} type="email" className="input" placeholder="parent@email.com" />
            </FormField>
          </div>
          <div className="col-span-2">
            <FormField label="Address" error={errors.address?.message} required>
              <input {...register('address')} className="input" placeholder="Street address" />
            </FormField>
          </div>
          <FormField label="City" error={errors.city?.message} required>
            <input {...register('city')} className="input" placeholder="City" />
          </FormField>
          <FormField label="Pincode" error={errors.pincode?.message} required>
            <input {...register('pincode')} className="input" placeholder="560001" />
          </FormField>
          <input type="hidden" {...register('academic_year')} value={currentYear?.id} />
        </div>
      </Modal>
    </div>
  )
}
