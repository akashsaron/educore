import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { feesApi, type FeePayment } from '@/utils/api'
import { StatCard, StatusBadge, Modal, PageSpinner, Pagination, FormField, SkeletonRows, Empty } from '@/components/ui'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'
import { useForm } from 'react-hook-form'
import toast from 'react-hot-toast'
import { Download, Plus } from 'lucide-react'
import { format } from 'date-fns'

const PIE_COLORS = ['#4f8ef7','#22c55e','#f59e0b','#ef4444','#a855f7']

export default function Fees() {
  const [showModal, setModal]   = useState(false)
  const [activeTab, setTab]     = useState<'invoices'|'payments'|'analytics'>('invoices')
  const [page, setPage]         = useState(1)
  const qc = useQueryClient()

  const { data: summary }       = useQuery({ queryKey: ['fee-summary'],    queryFn: feesApi.invoices.summary })
  const { data: analytics }     = useQuery({ queryKey: ['fee-analytics'],  queryFn: feesApi.analytics })
  const { data: invoices, isLoading: invLoading } = useQuery({
    queryKey: ['fee-invoices', page],
    queryFn:  () => feesApi.invoices.list({ page }),
    placeholderData: prev => prev,
  })
  const { data: payments, isLoading: payLoading } = useQuery({
    queryKey: ['fee-payments', page],
    queryFn:  () => feesApi.payments.list({ page }),
    enabled:  activeTab === 'payments',
    placeholderData: prev => prev,
  })

  const today = format(new Date(), 'yyyy-MM-dd')
  const exportUrl = feesApi.exportUrl('2025-07-01', today)

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Fee Management</h1>
          <p className="page-sub">Term 2 · 2025–26</p>
        </div>
        <div className="flex gap-2">
          <a href={exportUrl} className="btn btn-secondary btn-sm" download>
            <Download size={14} /> Export
          </a>
          <button onClick={() => setModal(true)} className="btn btn-primary btn-sm">
            <Plus size={14} /> Collect Fee
          </button>
        </div>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <StatCard label="Total Due"    value={`₹${((summary?.total_due    ?? 0) / 100000).toFixed(1)}L`} color="blue"   />
        <StatCard label="Collected"    value={`₹${((summary?.total_paid   ?? 0) / 100000).toFixed(1)}L`} color="green"  sub={`${Math.round((summary?.total_paid ?? 0) / (summary?.total_due ?? 1) * 100)}% collected`} />
        <StatCard label="Pending"      value={`₹${((summary?.pending      ?? 0) / 100000).toFixed(1)}L`} color="orange" />
        <StatCard label="Overdue"      value={summary?.overdue_count ?? 0}                                color="red"    sub="students" />
      </div>

      {/* Tabs */}
      <div className="card">
        <div className="tabs">
          {(['invoices','payments','analytics'] as const).map(t => (
            <button key={t} onClick={() => { setTab(t); setPage(1) }}
              className={`tab capitalize ${activeTab === t ? 'active' : ''}`}>{t}</button>
          ))}
        </div>

        {/* Invoices tab */}
        {activeTab === 'invoices' && (
          <>
            <table className="data-table">
              <thead>
                <tr><th>Invoice No.</th><th>Student</th><th>Class</th><th>Category</th>
                    <th>Amount Due</th><th>Paid</th><th>Balance</th><th>Status</th><th>Action</th></tr>
              </thead>
              <tbody>
                {invLoading ? <SkeletonRows rows={8} cols={9} /> :
                  invoices?.results.length === 0 ? (
                    <tr><td colSpan={9}><Empty message="No invoices found" /></td></tr>
                  ) : invoices?.results.map(inv => (
                    <tr key={inv.id}>
                      <td className="font-mono text-xs text-muted">{inv.invoice_no}</td>
                      <td className="font-medium">{inv.student_name}</td>
                      <td><span className="badge-blue">{inv.section_name}</span></td>
                      <td className="text-muted">{inv.category_name}</td>
                      <td className="font-medium">₹{Number(inv.amount_due).toLocaleString()}</td>
                      <td className="text-success">₹{Number(inv.amount_paid).toLocaleString()}</td>
                      <td className={Number(inv.balance_due) > 0 ? 'text-danger font-medium' : 'text-success'}>
                        ₹{Number(inv.balance_due).toLocaleString()}
                      </td>
                      <td><StatusBadge status={inv.status} /></td>
                      <td><button className="btn btn-secondary btn-sm">View</button></td>
                    </tr>
                  ))
                }
              </tbody>
            </table>
            <Pagination count={invoices?.count ?? 0} page={page} onChange={setPage} />
          </>
        )}

        {/* Payments tab */}
        {activeTab === 'payments' && (
          <>
            <table className="data-table">
              <thead>
                <tr><th>Receipt No.</th><th>Student</th><th>Amount</th>
                    <th>Method</th><th>Date</th><th>Status</th><th>Receipt</th></tr>
              </thead>
              <tbody>
                {payLoading ? <SkeletonRows rows={8} cols={7} /> :
                  payments?.results.map(p => (
                    <tr key={p.id}>
                      <td className="font-mono text-xs text-muted">{p.receipt_no}</td>
                      <td className="font-medium">{(p as any).student_name ?? '—'}</td>
                      <td className="font-semibold text-success">₹{Number(p.amount).toLocaleString()}</td>
                      <td className="text-muted capitalize">{p.payment_method}</td>
                      <td className="text-muted">{p.paid_date}</td>
                      <td><StatusBadge status={p.status} /></td>
                      <td>
                        <a href={feesApi.payments.receiptUrl(p.id)} target="_blank" rel="noopener"
                           className="btn btn-secondary btn-sm">📄 PDF</a>
                      </td>
                    </tr>
                  ))}
              </tbody>
            </table>
            <Pagination count={payments?.count ?? 0} page={page} onChange={setPage} />
          </>
        )}

        {/* Analytics tab */}
        {activeTab === 'analytics' && analytics && (
          <div className="grid lg:grid-cols-2 gap-6 pt-2">
            <div>
              <h4 className="text-sm font-semibold mb-3 text-primary">Monthly Collection (₹)</h4>
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={analytics.monthly_collection} margin={{ left: -10 }}>
                  <XAxis dataKey="label" tick={{ fontSize: 10, fill: '#6b7a99' }} axisLine={false} tickLine={false} />
                  <YAxis tick={{ fontSize: 10, fill: '#6b7a99' }} axisLine={false} tickLine={false}
                    tickFormatter={v => `₹${(v/100000).toFixed(0)}L`} />
                  <Tooltip formatter={(v: number) => [`₹${v.toLocaleString()}`, 'Collected']}
                    contentStyle={{ fontSize: 12, borderRadius: 8 }} />
                  <Bar dataKey="collected" fill="#4f8ef7" radius={[4,4,0,0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
            <div>
              <h4 className="text-sm font-semibold mb-3 text-primary">Invoice Status Split</h4>
              <ResponsiveContainer width="100%" height={200}>
                <PieChart>
                  <Pie data={analytics.status_split} dataKey="count" nameKey="status" cx="50%" cy="50%" outerRadius={80} label={({ status, count }) => `${status} (${count})`} labelLine={false} fontSize={10}>
                    {analytics.status_split.map((_, i) => (
                      <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip contentStyle={{ fontSize: 12, borderRadius: 8 }} />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="lg:col-span-2">
              <h4 className="text-sm font-semibold mb-3 text-primary">Pending Dues by Grade (₹)</h4>
              <ResponsiveContainer width="100%" height={160}>
                <BarChart data={analytics.pending_by_grade} layout="vertical" margin={{ left: 20 }}>
                  <XAxis type="number" tick={{ fontSize: 10, fill: '#6b7a99' }} axisLine={false}
                    tickFormatter={v => `₹${(v/1000).toFixed(0)}K`} />
                  <YAxis type="category" dataKey="grade" tick={{ fontSize: 10, fill: '#6b7a99' }} axisLine={false} width={65} />
                  <Tooltip formatter={(v: number) => [`₹${v.toLocaleString()}`, 'Pending']}
                    contentStyle={{ fontSize: 12, borderRadius: 8 }} />
                  <Bar dataKey="pending" fill="#ef4444" radius={[0,4,4,0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}
      </div>

      {/* Collect Fee Modal */}
      <Modal open={showModal} onClose={() => setModal(false)} title="Collect Fee"
        footer={<>
          <button onClick={() => setModal(false)} className="btn btn-secondary">Cancel</button>
          <button className="btn btn-primary">Collect & Generate Receipt</button>
        </>}>
        <FormField label="Student Name / Admission No." required>
          <input className="input" placeholder="Search student…" />
        </FormField>
        <div className="grid grid-cols-2 gap-4">
          <FormField label="Fee Type" required>
            <select className="input">
              <option>Tuition Fee</option><option>Transport Fee</option>
              <option>Library Fee</option><option>Exam Fee</option>
            </select>
          </FormField>
          <FormField label="Amount (₹)" required>
            <input type="number" className="input" placeholder="0" />
          </FormField>
        </div>
        <FormField label="Payment Method" required>
          <select className="input">
            <option value="cash">Cash</option><option value="online">Online Transfer</option>
            <option value="upi">UPI</option><option value="cheque">Cheque</option>
          </select>
        </FormField>
        <FormField label="Transaction ID (optional)">
          <input className="input" placeholder="UTR / Cheque No." />
        </FormField>
      </Modal>
    </div>
  )
}
