import React from 'react'
import { X, Inbox, ChevronLeft, ChevronRight, Loader2 } from 'lucide-react'
import { clsx } from 'clsx'

// ── Spinner ────────────────────────────────────────────────────────────────
export function Spinner({ size = 'md', className = '' }: { size?: 'sm'|'md'|'lg'; className?: string }) {
  const s = size === 'sm' ? 'w-4 h-4' : size === 'lg' ? 'w-8 h-8' : 'w-5 h-5'
  return <Loader2 className={clsx('animate-spin text-accent', s, className)} />
}

export function PageSpinner() {
  return (
    <div className="flex items-center justify-center h-64">
      <Spinner size="lg" />
    </div>
  )
}

// ── Badge ──────────────────────────────────────────────────────────────────
type BadgeVariant = 'green'|'red'|'blue'|'orange'|'purple'|'gray'|'yellow'
export function Badge({ children, variant = 'gray' }: { children: React.ReactNode; variant?: BadgeVariant }) {
  return <span className={`badge-${variant}`}>{children}</span>
}

export function StatusBadge({ status }: { status: string }) {
  const map: Record<string, BadgeVariant> = {
    paid: 'green', active: 'green', present: 'green', approved: 'green', returned: 'green',
    pending: 'orange', partial: 'orange', late: 'yellow', scheduled: 'blue', issued: 'blue',
    overdue: 'red', absent: 'red', rejected: 'red', inactive: 'red', lost: 'red', failed: 'red',
    ongoing: 'purple', completed: 'gray', cancelled: 'gray', waived: 'gray', holiday: 'gray',
  }
  return <Badge variant={map[status] ?? 'gray'}>{status}</Badge>
}

// ── Modal ──────────────────────────────────────────────────────────────────
interface ModalProps {
  open: boolean
  onClose: () => void
  title: string
  children: React.ReactNode
  footer?: React.ReactNode
  size?: 'sm'|'md'|'lg'
}
export function Modal({ open, onClose, title, children, footer, size = 'md' }: ModalProps) {
  if (!open) return null
  const widths = { sm: 'max-w-sm', md: 'max-w-lg', lg: 'max-w-2xl' }
  return (
    <div className="modal-overlay" onClick={e => e.target === e.currentTarget && onClose()}>
      <div className={clsx('modal-box', widths[size])}>
        <div className="flex items-center justify-between p-5 border-b border-slate-100">
          <h3 className="text-base font-semibold text-primary">{title}</h3>
          <button onClick={onClose} className="btn-icon text-muted hover:text-primary">
            <X size={18} />
          </button>
        </div>
        <div className="p-5">{children}</div>
        {footer && (
          <div className="flex justify-end gap-2 px-5 pb-5">{footer}</div>
        )}
      </div>
    </div>
  )
}

// ── Empty state ────────────────────────────────────────────────────────────
export function Empty({ message = 'No data found', icon }: { message?: string; icon?: React.ReactNode }) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-muted">
      <div className="mb-3 opacity-30">{icon ?? <Inbox size={40} />}</div>
      <p className="text-sm">{message}</p>
    </div>
  )
}

// ── Pagination ─────────────────────────────────────────────────────────────
interface PaginationProps {
  count: number; page: number; pageSize?: number; onChange: (p: number) => void
}
export function Pagination({ count, page, pageSize = 25, onChange }: PaginationProps) {
  const totalPages = Math.ceil(count / pageSize)
  if (totalPages <= 1) return null
  return (
    <div className="flex items-center justify-between px-4 py-3 border-t border-slate-100">
      <p className="text-xs text-muted">
        Showing {(page - 1) * pageSize + 1}–{Math.min(page * pageSize, count)} of {count}
      </p>
      <div className="flex gap-1">
        <button className="btn-icon disabled:opacity-30" onClick={() => onChange(page - 1)} disabled={page === 1}>
          <ChevronLeft size={16} />
        </button>
        {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
          const p = Math.max(1, Math.min(page - 2, totalPages - 4)) + i
          return (
            <button key={p} onClick={() => onChange(p)}
              className={clsx('w-8 h-8 text-xs rounded-btn transition-colors',
                p === page ? 'bg-accent text-white' : 'hover:bg-surface text-muted')}>
              {p}
            </button>
          )
        })}
        <button className="btn-icon disabled:opacity-30" onClick={() => onChange(page + 1)} disabled={page === totalPages}>
          <ChevronRight size={16} />
        </button>
      </div>
    </div>
  )
}

// ── Form components ────────────────────────────────────────────────────────
export function FormField({
  label, error, children, required
}: { label: string; error?: string; children: React.ReactNode; required?: boolean }) {
  return (
    <div className="mb-4">
      <label className="label">{label}{required && <span className="text-danger ml-0.5">*</span>}</label>
      {children}
      {error && <p className="text-xs text-danger mt-1">{error}</p>}
    </div>
  )
}

// ── Stat Card ─────────────────────────────────────────────────────────────
interface StatCardProps {
  label: string; value: string | number; sub?: string
  color?: 'blue'|'green'|'orange'|'purple'|'red'
  icon?: React.ReactNode
  trend?: { value: string; up: boolean }
}
export function StatCard({ label, value, sub, color = 'blue', icon, trend }: StatCardProps) {
  return (
    <div className={`stat-card ${color}`}>
      {icon && <div className="absolute top-4 right-4 text-3xl opacity-10">{icon}</div>}
      <p className="text-xs text-muted font-medium uppercase tracking-wide mb-2">{label}</p>
      <p className="text-2xl font-semibold text-primary leading-none mb-1">{value}</p>
      {sub && <p className="text-xs text-muted">{sub}</p>}
      {trend && (
        <p className={clsx('text-xs font-medium mt-1', trend.up ? 'text-success' : 'text-danger')}>
          {trend.up ? '▲' : '▼'} {trend.value}
        </p>
      )}
    </div>
  )
}

// ── Skeleton rows ──────────────────────────────────────────────────────────
export function SkeletonRows({ rows = 5, cols = 4 }: { rows?: number; cols?: number }) {
  return (
    <>
      {Array.from({ length: rows }).map((_, i) => (
        <tr key={i}>
          {Array.from({ length: cols }).map((_, j) => (
            <td key={j} className="px-4 py-3">
              <div className="skeleton h-4 rounded" style={{ width: `${60 + (j * 15) % 40}%` }} />
            </td>
          ))}
        </tr>
      ))}
    </>
  )
}

// ── Search Input ──────────────────────────────────────────────────────────
export function SearchInput({ value, onChange, placeholder = 'Search...' }: {
  value: string; onChange: (v: string) => void; placeholder?: string
}) {
  return (
    <div className="relative">
      <svg className="absolute left-3 top-1/2 -translate-y-1/2 text-muted w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
      </svg>
      <input
        type="text" value={value} onChange={e => onChange(e.target.value)}
        placeholder={placeholder}
        className="input pl-9 w-56 text-sm"
      />
    </div>
  )
}
