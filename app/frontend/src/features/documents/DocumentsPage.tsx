import { useEffect, useRef, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { BookOpen, MessagesSquare, MoreVertical, Pencil, Plus, Trash2 } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { Field, Input } from '@/components/ui/Form'
import { Modal } from '@/components/ui/Modal'
import { SearchBox } from '@/components/ui/SearchBox'
import { EmptyState, ErrorNote, Loading, Page, PageHeader } from '@/components/ui/misc'
import { useToast } from '@/components/ui/Toast'
import { api } from '@/lib/api'
import { t } from '@/lib/i18n.ts'
import type { KbCategory, KbDoc } from '@/lib/types'
import { errMsg } from '@/lib/utils'

const fold = (s: string) => s.normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/\u0111/g, 'd').replace(/\u0110/g, 'D').toLowerCase()

function CategoryActions({ name, onRename, onDelete }: { name: string; onRename: () => void; onDelete: () => void }) {
  const [open, setOpen] = useState(false)
  const container = useRef<HTMLDivElement>(null)
  const trigger = useRef<HTMLButtonElement>(null)

  useEffect(() => {
    if (!open) return
    const closeOutside = (e: PointerEvent) => {
      if (!container.current?.contains(e.target as Node)) setOpen(false)
    }
    document.addEventListener('pointerdown', closeOutside)
    return () => document.removeEventListener('pointerdown', closeOutside)
  }, [open])

  return (
    <div ref={container} className="absolute right-2 top-1/2 -translate-y-1/2"
      onBlur={(e) => { if (!e.currentTarget.contains(e.relatedTarget)) setOpen(false) }}
      onKeyDown={(e) => {
        if (e.key === 'Escape' && open) {
          setOpen(false)
          trigger.current?.focus()
        }
      }}>
      <button ref={trigger} type="button" aria-label={t('Tùy chọn cho {name}', { name })} aria-expanded={open} title={t('Thêm tùy chọn')}
        onClick={() => setOpen(!open)} className="grid size-8 place-items-center rounded-md text-muted hover:bg-panel2 hover:text-fg">
        <MoreVertical className="size-4" />
      </button>
      {open && (
        <div className="fade-in absolute right-0 top-full z-20 mt-1 w-max min-w-36 rounded-xl border border-line bg-panel p-1.5 shadow-2xl">
          <button type="button" onClick={() => { setOpen(false); onRename() }}
            className="flex w-full items-center gap-2.5 rounded-lg px-2.5 py-2 text-left text-sm hover:bg-panel2"><Pencil className="size-4" />{t('Đổi tên')}</button>
          <button type="button" onClick={() => { setOpen(false); onDelete() }}
            className="flex w-full items-center gap-2.5 rounded-lg px-2.5 py-2 text-left text-sm text-bad hover:bg-bad/10"><Trash2 className="size-4" />{t('Xóa danh mục')}</button>
        </div>
      )}
    </div>
  )
}

export function DocumentsPage() {
  const nav = useNavigate()
  const qc = useQueryClient()
  const toast = useToast()
  const [creating, setCreating] = useState(false)
  const [name, setName] = useState('')
  const [q, setQ] = useState('')
  const [editing, setEditing] = useState<{ mode: 'rename' | 'delete'; category: KbCategory } | null>(null)
  const [newName, setNewName] = useState('')

  const list = useQuery({ queryKey: ['kb-categories'], queryFn: () => api.get<KbCategory[]>('/api/knowledge/categories') })
  const create = useMutation({
    mutationFn: () => api.post<KbCategory>('/api/knowledge/categories', { name: name.trim() }),
    onSuccess: (cat) => { void qc.invalidateQueries({ queryKey: ['kb-categories'] }); setCreating(false); setName(''); nav(`/documents/${cat.id}`) },
    onError: (e) => toast(errMsg(e), 'bad'),
  })
  const change = useMutation({
    mutationFn: (action: NonNullable<typeof editing>) => {
      const url = `/api/knowledge/categories/${action.category.id}`
      return action.mode === 'rename' ? api.put<unknown>(url, { name: newName.trim() }) : api.del<unknown>(url)
    },
    onSuccess: async () => {
      await Promise.all([
        qc.invalidateQueries({ queryKey: ['kb-categories'] }),
        qc.invalidateQueries({ queryKey: ['kb'] }),
      ])
      setEditing(null)
    },
    onError: (e) => toast(errMsg(e), 'bad'),
  })
  const renameDisabled = !newName.trim() || newName.trim() === editing?.category.name

  const docs = useQuery({ queryKey: ['kb'], queryFn: () => api.get<{ docs: KbDoc[] }>('/api/knowledge'), enabled: q.trim().length > 0 })
  const term = fold(q.trim())
  const all = list.data ?? []
  const matchedDocs = (cid: string) => (term ? (docs.data?.docs ?? []).filter((d) => d.category_id === cid && fold(d.name).includes(term)) : [])
  const categories = term ? all.filter((c) => fold(c.name).includes(term) || matchedDocs(c.id).length > 0) : all

  return (
    <Page>
      <PageHeader title={t('Tài liệu')} action={
        <div className="flex flex-wrap gap-2">
          <Button variant="primary" onClick={() => setCreating(true)}><Plus className="size-4" />{t('Tạo danh mục')}</Button>
          <Button variant="secondary" onClick={() => nav('/chat', { state: { docs: true } })}><MessagesSquare className="size-4" />{t('Hỏi toàn bộ kho')}</Button>
        </div>
      } />
      <div className="mb-5">
        <SearchBox value={q} onChange={setQ} placeholder={t('Tìm danh mục hoặc tài liệu…')} label={t('Tìm danh mục hoặc tài liệu')} />
      </div>
      {list.isLoading ? <Loading /> : list.error ? <ErrorNote error={list.error} /> : categories.length === 0 ? (
        <div className="rounded-2xl border border-dashed border-line bg-panel/40">
          <EmptyState icon={BookOpen} title={term ? t('Không tìm thấy danh mục hoặc tài liệu.') : t('Chưa có danh mục nào')} />
        </div>
      ) : <ul className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5">
        {categories.map((cat) => (
          <li key={cat.id} className="relative min-w-0">
            <Link to={`/documents/${cat.id}`} className="flex min-w-0 items-center gap-3 rounded-xl border border-line bg-panel p-3 pr-11 transition hover:border-accent/60 hover:bg-panel2/50">
              <span className="grid size-9 shrink-0 place-items-center rounded-lg bg-accent/10 text-accent">{cat.icon || <BookOpen className="size-4" />}</span>
              <div className="min-w-0 flex-1">
                <h2 className="truncate text-sm font-semibold">{cat.name}</h2>
                <p className="truncate text-xs text-muted">{matchedDocs(cat.id)[0]?.name ?? (cat.doc_count === 1 ? t('1 tài liệu') : t('{n} tài liệu', { n: cat.doc_count }))}</p>
              </div>
            </Link>
            <CategoryActions name={cat.name}
              onRename={() => { setNewName(cat.name); setEditing({ mode: 'rename', category: cat }) }}
              onDelete={() => setEditing({ mode: 'delete', category: cat })} />
          </li>
        ))}
      </ul>}

      <Modal open={creating} onClose={() => { if (!create.isPending) setCreating(false) }} title={t('Tạo danh mục')}
        footer={<><Button onClick={() => setCreating(false)} disabled={create.isPending}>{t('Hủy')}</Button>
          <Button variant="primary" loading={create.isPending} disabled={!name.trim()} onClick={() => create.mutate()}><Plus className="size-4" />{t('Tạo')}</Button></>}>
        <Field label={t('Tên danh mục')}>
          <Input autoFocus value={name} maxLength={200} onChange={(e) => setName(e.target.value)} placeholder={t('Ví dụ: Hợp đồng dự án A')}
            onKeyDown={(e) => { if (e.key === 'Enter' && name.trim() && !create.isPending) create.mutate() }} />
        </Field>
      </Modal>
      {editing && (
        <Modal open onClose={() => { if (!change.isPending) setEditing(null) }}
          title={editing.mode === 'rename' ? t('Đổi tên danh mục') : t('Xóa danh mục')}
          footer={<><Button autoFocus={editing.mode === 'delete'} onClick={() => setEditing(null)} disabled={change.isPending}>{t('Hủy')}</Button>
            <Button variant={editing.mode === 'rename' ? 'primary' : 'danger'} loading={change.isPending}
              disabled={editing.mode === 'rename' && renameDisabled} onClick={() => change.mutate(editing)}>
              {editing.mode === 'rename' ? t('Lưu') : t('Xóa')}
            </Button></>}>
          {editing.mode === 'rename' ? (
            <Field label={t('Tên danh mục')}>
              <Input autoFocus value={newName} maxLength={200} onChange={(e) => setNewName(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.nativeEvent.isComposing && !renameDisabled && !change.isPending) change.mutate(editing)
                }} />
            </Field>
          ) : <p className="break-words text-sm text-muted">{t('Xóa danh mục “{name}” và toàn bộ tài liệu bên trong?', { name: editing.category.name })}</p>}
        </Modal>
      )}
    </Page>
  )
}
