import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { libraryApi } from '@/utils/api'
import { StatCard, StatusBadge, Modal, Pagination, SearchInput, SkeletonRows, Empty, FormField } from '@/components/ui'
import toast from 'react-hot-toast'
import { BookOpen, Plus, RotateCcw } from 'lucide-react'

export default function Library() {
  const [activeTab, setTab]   = useState<'books'|'issued'|'categories'>('books')
  const [page, setPage]       = useState(1)
  const [search, setSearch]   = useState('')
  const [showModal, setModal] = useState(false)
  const qc = useQueryClient()

  const { data: stats }     = useQuery({ queryKey: ['lib-stats'],       queryFn: libraryApi.books.stats })
  const { data: books, isLoading } = useQuery({
    queryKey: ['books', page, search],
    queryFn:  () => libraryApi.books.list({ page, search: search||undefined }),
    placeholderData: prev => prev,
  })
  const { data: issues, isLoading: issueLoading } = useQuery({
    queryKey: ['issues', page],
    queryFn:  () => libraryApi.issues.list({ page }),
    enabled:  activeTab === 'issued',
    placeholderData: prev => prev,
  })
  const { data: categories } = useQuery({ queryKey: ['book-categories'], queryFn: libraryApi.categories })

  const returnMutation = useMutation({
    mutationFn: (id: number) => libraryApi.issues.returnBook(id),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['issues'] }); qc.invalidateQueries({ queryKey: ['lib-stats'] }); toast.success('Book returned') },
  })

  return (
    <div>
      <div className="page-header">
        <div><h1 className="page-title">Library</h1><p className="page-sub">{stats?.total ?? '…'} books · {stats?.borrowed ?? '…'} borrowed</p></div>
        <button onClick={() => setModal(true)} className="btn btn-primary btn-sm"><Plus size={14}/> Add Book</button>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <StatCard label="Total Books"  value={stats?.total     ?? '—'} color="blue"/>
        <StatCard label="Available"    value={stats?.available  ?? '—'} color="green"/>
        <StatCard label="Borrowed"     value={stats?.borrowed   ?? '—'} color="orange"/>
        <StatCard label="Overdue"      value={stats?.overdue    ?? '—'} color="red"/>
      </div>

      <div className="card">
        <div className="tabs">
          {(['books','issued','categories'] as const).map(t => (
            <button key={t} onClick={() => { setTab(t); setPage(1) }} className={`tab capitalize ${activeTab===t?'active':''}`}>{t}</button>
          ))}
        </div>

        {activeTab === 'books' && (
          <>
            <div className="mb-4">
              <SearchInput value={search} onChange={v => { setSearch(v); setPage(1) }} placeholder="Search title, author, ISBN…"/>
            </div>
            <table className="data-table">
              <thead><tr><th>Title</th><th>Author</th><th>Category</th><th>ISBN</th><th>Total</th><th>Available</th><th>Rack</th></tr></thead>
              <tbody>
                {isLoading ? <SkeletonRows rows={8} cols={7}/> :
                  books?.results.length === 0 ? <tr><td colSpan={7}><Empty message="No books found"/></td></tr> :
                  books?.results.map(b => (
                    <tr key={b.id}>
                      <td className="font-medium">{b.title}</td>
                      <td className="text-muted">{b.author}</td>
                      <td><span className="badge-purple">{b.category_name}</span></td>
                      <td className="text-muted font-mono text-xs">{b.isbn || '—'}</td>
                      <td className="text-center">{b.total_copies}</td>
                      <td className="text-center"><span className={b.available > 0 ? 'text-success font-medium' : 'text-danger font-medium'}>{b.available}</span></td>
                      <td className="text-muted">{b.rack_no || '—'}</td>
                    </tr>
                  ))
                }
              </tbody>
            </table>
            <Pagination count={books?.count ?? 0} page={page} onChange={setPage}/>
          </>
        )}

        {activeTab === 'issued' && (
          <>
            <table className="data-table">
              <thead><tr><th>Book</th><th>Borrower</th><th>Issued</th><th>Due Date</th><th>Status</th><th>Fine</th><th>Action</th></tr></thead>
              <tbody>
                {issueLoading ? <SkeletonRows rows={8} cols={7}/> :
                  issues?.results.length === 0 ? <tr><td colSpan={7}><Empty message="No issues found"/></td></tr> :
                  issues?.results.map(i => (
                    <tr key={i.id}>
                      <td className="font-medium max-w-xs truncate">{i.book_title}</td>
                      <td>{i.borrower_name}</td>
                      <td className="text-muted">{i.issued_on}</td>
                      <td className={i.status === 'overdue' ? 'text-danger font-medium' : 'text-muted'}>{i.due_date}</td>
                      <td><StatusBadge status={i.status}/></td>
                      <td className={Number(i.fine_amount) > 0 ? 'text-danger font-medium' : 'text-muted'}>
                        {Number(i.fine_amount) > 0 ? `₹${i.fine_amount}` : '—'}
                      </td>
                      <td>
                        {i.status !== 'returned' && (
                          <button onClick={() => returnMutation.mutate(i.id)} disabled={returnMutation.isPending}
                            className="btn btn-secondary btn-sm flex items-center gap-1">
                            <RotateCcw size={12}/> Return
                          </button>
                        )}
                      </td>
                    </tr>
                  ))
                }
              </tbody>
            </table>
            <Pagination count={issues?.count ?? 0} page={page} onChange={setPage}/>
          </>
        )}

        {activeTab === 'categories' && (
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 pt-2">
            {categories?.map((c, i) => (
              <div key={c.id} className="p-4 rounded-xl border border-slate-100 hover:border-accent transition-colors text-center cursor-pointer">
                <div className="text-2xl mb-2">{['📘','🔬','📚','📰','💻','🎭','🏛️','🌍'][i%8]}</div>
                <p className="font-medium text-primary text-sm">{c.name}</p>
              </div>
            ))}
          </div>
        )}
      </div>

      <Modal open={showModal} onClose={() => setModal(false)} title="Add New Book"
        footer={<><button onClick={() => setModal(false)} className="btn btn-secondary">Cancel</button><button className="btn btn-primary">Add Book</button></>}>
        <FormField label="Title" required><input className="input" placeholder="Book title"/></FormField>
        <FormField label="Author" required><input className="input" placeholder="Author name"/></FormField>
        <div className="grid grid-cols-2 gap-4">
          <FormField label="ISBN"><input className="input" placeholder="978-…"/></FormField>
          <FormField label="Category" required>
            <select className="input"><option value="">Select</option>{categories?.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}</select>
          </FormField>
          <FormField label="Publisher"><input className="input"/></FormField>
          <FormField label="Total Copies"><input type="number" className="input" defaultValue={1} min={1}/></FormField>
          <FormField label="Rack No."><input className="input" placeholder="A-01"/></FormField>
        </div>
      </Modal>
    </div>
  )
}
