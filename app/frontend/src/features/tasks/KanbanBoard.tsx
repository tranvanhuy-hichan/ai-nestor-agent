import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { GripVertical, Plus, Play, RotateCcw, Trash2 } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { Textarea, Input } from '@/components/ui/Form'
import { Modal } from '@/components/ui/Modal'
import { ErrorNote, Loading } from '@/components/ui/misc'
import { useToast } from '@/components/ui/Toast'
import { api } from '@/lib/api'
import type { KanbanCard } from '@/lib/types'
import { cn, errMsg, timeAgo } from '@/lib/utils'
import { t, tk } from '@/lib/i18n.ts'

/** Bang Kanban ca nhan: cot "Viec can lam" la the tinh (keo-tha sap xep/xoa), 3 cot con lai
 * phan anh dung trang thai job that cua jobs.py (khong co the gia, khong co worker rieng). */
const COLUMNS: { id: KanbanCard['status']; label: string; hint: string }[] = [
  { id: 'todo', label: tk('Việc cần làm'), hint: tk('Kéo để sắp xếp. Bấm Giao việc để Nestor bắt đầu.') },
  { id: 'running', label: tk('Đang làm'), hint: tk('Nestor đang xử lý.') },
  { id: 'blocked', label: tk('Chặn / Lỗi'), hint: tk('Dừng, lỗi hoặc bị huỷ. Có thể giao lại.') },
  { id: 'done', label: tk('Đã xong'), hint: tk('Hoàn tất.') },
]

function NewCardDialog({ onClose }: { onClose: () => void }) {
  const toast = useToast()
  const qc = useQueryClient()
  const [title, setTitle] = useState('')
  const [body, setBody] = useState('')
  const create = useMutation({
    mutationFn: () => api.post('/api/kanban', { title, body }),
    onSuccess: () => { void qc.invalidateQueries({ queryKey: ['kanban'] }); onClose() },
    onError: (e) => toast(errMsg(e), 'bad'),
  })
  return (
    <Modal open onClose={onClose} title={t('Thẻ mới')} wide footer={
      <Button variant="primary" loading={create.isPending} disabled={!title.trim()} onClick={() => create.mutate()}>
        <Plus className="size-4" />{t('Thêm thẻ')}
      </Button>
    }>
      <div className="space-y-3">
        <Input value={title} onChange={(e) => setTitle(e.target.value)} placeholder={t('Tiêu đề việc…')} autoFocus
          onKeyDown={(e) => { if (e.key === 'Enter' && title.trim()) create.mutate() }} />
        <Textarea value={body} onChange={(e) => setBody(e.target.value)} rows={12} placeholder={t('Mô tả chi tiết (tuỳ chọn) — sẽ là nội dung giao cho Nestor')} />
      </div>
    </Modal>
  )
}

function CardDetail({ card, onClose, onChanged }: { card: KanbanCard; onClose: () => void; onChanged: () => void }) {
  const toast = useToast()
  const [title, setTitle] = useState(card.title)
  const [body, setBody] = useState(card.body)
  const save = useMutation({
    mutationFn: () => api.patch(`/api/kanban/${card.id}`, { title, body }),
    onSuccess: () => { toast(t('Đã lưu')); onChanged() },
    onError: (e) => toast(errMsg(e), 'bad'),
  })
  const dispatch = useMutation({
    mutationFn: () => api.post(`/api/kanban/${card.id}/dispatch`, {}),
    onSuccess: () => { toast(t('Đã giao việc cho Nestor')); onChanged(); onClose() },
    onError: (e) => toast(errMsg(e), 'bad'),
  })
  const retry = useMutation({
    mutationFn: () => api.post(`/api/kanban/${card.id}/retry`, {}),
    onSuccess: () => { onChanged() },
    onError: (e) => toast(errMsg(e), 'bad'),
  })
  const del = useMutation({
    mutationFn: () => api.del(`/api/kanban/${card.id}`),
    onSuccess: () => { toast(t('Đã xoá')); onChanged(); onClose() },
    onError: (e) => toast(errMsg(e), 'bad'),
  })
  const editable = card.status === 'todo'
  return (
    <Modal open onClose={onClose} title={t('Thẻ việc')} wide footer={
      <>
        <Button variant="ghost" onClick={() => del.mutate()} loading={del.isPending}><Trash2 className="size-4" />{t('Xoá')}</Button>
        {card.status === 'blocked' && <Button onClick={() => retry.mutate()} loading={retry.isPending}><RotateCcw className="size-4" />{t('Giao lại')}</Button>}
        {editable && <Button variant="secondary" onClick={() => save.mutate()} loading={save.isPending} disabled={title === card.title && body === card.body}>{t('Lưu')}</Button>}
        {editable && <Button variant="primary" onClick={() => dispatch.mutate()} loading={dispatch.isPending}><Play className="size-4" />{t('Giao việc')}</Button>}
      </>
    }>
      <div className="space-y-3">
        <Input value={title} onChange={(e) => setTitle(e.target.value)} disabled={!editable} placeholder={t('Tiêu đề')} />
        <Textarea value={body} onChange={(e) => setBody(e.target.value)} disabled={!editable} rows={10} placeholder={t('Mô tả')} />
        {card.job && (
          <div className="rounded-lg border border-line bg-panel2/40 p-3 text-sm">
            <p className="text-muted">{t('Trạng thái việc')}: <span className="font-medium text-fg">{card.job.status}</span></p>
            {card.job.progress && <p className="mt-1 truncate text-xs text-muted">{card.job.progress}</p>}
            {card.job.error && <p className="mt-1 text-xs text-bad">{card.job.error}</p>}
            {card.job.session_id && <Link to={`/chat?session=${card.job.session_id}`} className="mt-1.5 inline-block text-xs text-accent hover:underline">{t('Xem agent đã làm thế nào')}</Link>}
          </div>
        )}
      </div>
    </Modal>
  )
}

function CardTile({ card, draggable, onDrop, onOpen }: { card: KanbanCard; draggable: boolean; onDrop?: (fromId: string) => void; onOpen: () => void }) {
  const [over, setOver] = useState(false)
  return (
    <div
      draggable={draggable}
      onDragStart={(e) => e.dataTransfer.setData('text/kanban-card', card.id)}
      onDragOver={(e) => { if (onDrop) { e.preventDefault(); setOver(true) } }}
      onDragLeave={() => setOver(false)}
      onDrop={(e) => {
        setOver(false)
        const fromId = e.dataTransfer.getData('text/kanban-card')
        if (onDrop && fromId && fromId !== card.id) onDrop(fromId)
      }}
    >
      <Card className={cn('cursor-pointer p-3 transition hover:border-muted/60', over && 'border-accent')} onClick={onOpen}>
        <div className="flex items-start gap-2">
          {draggable && <GripVertical className="mt-0.5 size-4 shrink-0 text-muted/50" />}
          <div className="min-w-0 flex-1">
            <p className="truncate text-sm font-medium">{card.title}</p>
            {card.body && <p className="mt-0.5 line-clamp-2 text-xs text-muted">{card.body}</p>}
            {card.job?.progress && <p className="mt-1 truncate text-xs text-accent">{card.job.progress}</p>}
            {card.job?.error && <p className="mt-1 truncate text-xs text-bad">{card.job.error}</p>}
            <p className="mt-1.5 text-[11px] text-muted/70">{timeAgo(card.updated)}</p>
          </div>
        </div>
      </Card>
    </div>
  )
}

export function KanbanBoard({ adding, onAddingChange }: { adding: boolean; onAddingChange: (v: boolean) => void }) {
  const qc = useQueryClient()
  const toast = useToast()
  const [selected, setSelected] = useState<string | null>(null)
  const q = useQuery({
    queryKey: ['kanban'],
    queryFn: () => api.get<KanbanCard[]>('/api/kanban'),
    refetchInterval: (s) => (s.state.data?.some((c) => c.status === 'running') ? 1500 : 8000),
  })
  const refresh = () => void qc.invalidateQueries({ queryKey: ['kanban'] })
  const cards = q.data ?? []
  const reorder = useMutation({
    mutationFn: ({ fromId, beforeId }: { fromId: string; beforeId: string | null }) => api.post(`/api/kanban/${fromId}/reorder`, { before_id: beforeId }),
    onSuccess: refresh,
    onError: (e) => toast(errMsg(e), 'bad'),
  })
  const selectedCard = cards.find((c) => c.id === selected) ?? null

  if (q.isLoading) return <Loading />
  if (q.error) return <ErrorNote error={q.error} />

  return (
    <div>
      <p className="mb-4 text-sm text-muted">{t('Thẻ "Việc cần làm" chưa chạy gì — bấm vào thẻ rồi "Giao việc" để Nestor bắt đầu.')}</p>
      {adding && <NewCardDialog onClose={() => onAddingChange(false)} />}
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {COLUMNS.map((col) => {
          const list = cards.filter((c) => c.status === col.id)
          const canAdd = col.id === 'todo'
          return (
            <div key={col.id} className="min-w-0">
              <div className="mb-2 flex items-center gap-2">
                <h3 className="text-sm font-semibold">{t(col.label)}</h3>
                <span className="rounded-md bg-panel2 px-1.5 py-0.5 text-[11px] text-muted">{list.length}</span>
                <div className="flex-1" />
                <button
                  onClick={() => canAdd && onAddingChange(true)}
                  disabled={!canAdd}
                  aria-label={t('Thêm thẻ vào {col}', { col: t(col.label) })}
                  title={canAdd ? t('Thêm thẻ vào {col}', { col: t(col.label) }) : t('Thêm thẻ trực tiếp vào đây — kéo thẻ từ Việc cần làm thay vào đó.')}
                  className={cn('rounded-md p-1 transition', canAdd ? 'text-muted hover:bg-panel2 hover:text-fg' : 'cursor-not-allowed text-muted/30')}
                >
                  <Plus className="size-3.5" />
                </button>
              </div>
              <p className="mb-2 text-[11px] text-muted/70">{t(col.hint)}</p>
              <div
                className="min-h-16 space-y-2 rounded-xl border border-dashed border-line/60 p-1.5"
                onDragOver={(e) => col.id === 'todo' && e.preventDefault()}
                onDrop={(e) => {
                  if (col.id !== 'todo') return
                  const fromId = e.dataTransfer.getData('text/kanban-card')
                  if (fromId) reorder.mutate({ fromId, beforeId: null })
                }}
              >
                {list.length === 0 && <p className="px-2 py-3 text-center text-xs text-muted/60">{t('— trống —')}</p>}
                {list.map((c) => (
                  <CardTile key={c.id} card={c} draggable={col.id === 'todo'}
                    onDrop={col.id === 'todo' ? (fromId) => reorder.mutate({ fromId, beforeId: c.id }) : undefined}
                    onOpen={() => setSelected(c.id)} />
                ))}
              </div>
            </div>
          )
        })}
      </div>
      {selectedCard && <CardDetail card={selectedCard} onClose={() => setSelected(null)} onChanged={refresh} />}
    </div>
  )
}
