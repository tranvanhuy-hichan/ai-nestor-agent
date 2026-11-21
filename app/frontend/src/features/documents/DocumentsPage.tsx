import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { ArrowRight, BookOpen, MessagesSquare, Plus } from 'lucide-react'
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

export function DocumentsPage() {
  const nav = useNavigate()
  const qc = useQueryClient()
  const toast = useToast()
  const [creating, setCreating] = useState(false)
  const [name, setName] = useState('')
  const [q, setQ] = useState('')

  const list = useQuery({ queryKey: ['kb-categories'], queryFn: () => api.get<KbCategory[]>('/api/knowledge/categories') })
  const create = useMutation({
    mutationFn: () => api.post<KbCategory>('/api/knowledge/categories', { name: name.trim() }),
    onSuccess: (cat) => { void qc.invalidateQueries({ queryKey: ['kb-categories'] }); setCreating(false); setName(''); nav(`/documents/${cat.id}`) },
    onError: (e) => toast(errMsg(e), 'bad'),
  })

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
          <li key={cat.id} className="min-w-0">
            <Link to={`/documents/${cat.id}`} className="group flex min-w-0 items-center gap-3 rounded-xl border border-line bg-panel p-3 transition hover:border-accent/60 hover:bg-panel2/50">
              <span className="grid size-9 shrink-0 place-items-center rounded-lg bg-accent/10 text-accent">{cat.icon || <BookOpen className="size-4" />}</span>
              <div className="min-w-0 flex-1">
                <h2 className="truncate text-sm font-semibold">{cat.name}</h2>
                <p className="truncate text-xs text-muted">{matchedDocs(cat.id)[0]?.name ?? (cat.doc_count === 1 ? t('1 tài liệu') : t('{n} tài liệu', { n: cat.doc_count }))}</p>
              </div>
              <ArrowRight className="size-3.5 shrink-0 text-muted transition group-hover:translate-x-0.5 group-hover:text-accent" />
            </Link>
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
    </Page>
  )
}
