import { FileImage, FileSpreadsheet, FileText, Paperclip, Plus, X } from 'lucide-react'
import { useEffect, useRef, useState, type ReactNode } from 'react'
import { useQuery } from '@tanstack/react-query'
import { api } from '@/lib/api'
import { t } from '@/lib/i18n.ts'
import { searchableText } from '@/lib/featureCatalog'
import { errMsg } from '@/lib/utils'
import { imageUrl, useSessionId } from './session'
import { attachmentAccept, isAttachmentImage, type AttachmentDraft, type SelectedDocument } from './useAttachments'

const mb = (size: number) => size >= 1024 ** 2 ? `${(size / 1024 ** 2).toFixed(1)} MB` : `${Math.max(1, Math.ceil(size / 1024))} KB`
const MAX_DOCUMENTS = 100
type LibraryDocument = SelectedDocument & { category_id: string; chunks: number; status: string }

function FileIcon({ name }: { name: string }) {
  const Icon = isAttachmentImage(name) ? FileImage : /\.(xlsx|csv)$/i.test(name) ? FileSpreadsheet : FileText
  return <Icon className="size-4 shrink-0 text-muted" />
}

export function AttachmentPreview({ draft }: { draft: AttachmentDraft }) {
  if (!draft.uploads.length && !draft.documents.length) return null
  return <div className="flex max-h-48 flex-wrap gap-1.5 overflow-y-auto px-2 py-2">
    {draft.uploads.map((file) => (
      <div key={file.id} className="flex max-w-full items-center gap-2 rounded-lg border border-line bg-bg px-2 py-1 text-xs">
        {file.sid && file.path && isAttachmentImage(file.name)
          ? <ImagePreview url={imageUrl(file.sid, file.path)} name={file.name} />
          : <FileIcon name={file.name} />}
        <div className="min-w-0">
          <p className="truncate" title={file.name}>{file.name}</p>
          <p className="text-muted">{mb(file.size)}</p>
          {file.error && <p role="alert" className="text-bad">{file.error}</p>}
          {!file.path && !file.error && <progress className="block w-24" max={1} value={file.progress < 1 ? file.progress : undefined} aria-label={t('Đang tải lên…')} />}
        </div>
        <Remove name={file.name} onClick={() => draft.remove(file.id)} />
      </div>
    ))}
    {draft.documents.map((doc) => (
      <div key={doc.id} className="flex max-w-full items-center gap-2 rounded-lg border border-line bg-bg px-2 py-1 text-xs">
        <FileText className="size-4 shrink-0 text-muted" />
        <span className="truncate" title={doc.name}>{doc.name}</span>
        <Remove name={doc.name} onClick={() => draft.setDocuments((docs) => docs.filter((item) => item.id !== doc.id))} />
      </div>
    ))}
  </div>
}

function Remove({ name, onClick }: { name: string; onClick: () => void }) {
  return <button type="button" onClick={onClick} aria-label={t('Bỏ {name}', { name })} className="shrink-0 rounded p-1 text-muted hover:bg-panel2 hover:text-fg"><X className="size-3" /></button>
}

function ImagePreview({ url, name, history = false }: { url: string; name: string; history?: boolean }) {
  const dialog = useRef<HTMLDialogElement>(null)
  return <>
    <button type="button" title={name} onClick={() => dialog.current?.showModal()} aria-label={t('Xem ảnh {name}', { name })}>
      <img src={url} alt={name} loading="lazy" className={history ? 'max-h-48 max-w-full rounded-lg object-contain' : 'size-10 rounded object-cover'} />
    </button>
    <dialog ref={dialog} className="m-auto max-w-[95vw] rounded-xl border border-line bg-panel p-2 text-fg backdrop:bg-black/70">
      <div className="flex items-center justify-between gap-2 px-2 pb-2">
        <span className="truncate text-sm">{name}</span>
        <button type="button" onClick={() => dialog.current?.close()} aria-label={t('Đóng')} className="p-1"><X className="size-4" /></button>
      </div>
      <img src={url} alt={name} className="max-h-[83vh] max-w-full object-contain" />
    </dialog>
  </>
}

export function SentAttachments({ sid: explicitSid, paths, documentIds, onOpenFile }: {
  sid?: string | null; paths?: string[]; documentIds?: string[]; onOpenFile: (path: string) => void
}) {
  const session = useSessionId()
  const sid = explicitSid ?? session
  const docs = useQuery({ queryKey: ['attachment-library'], queryFn: fetchLibrary, enabled: Boolean(documentIds?.length), staleTime: 30_000 })
  if (!paths?.length && !documentIds?.length) return null
  const linkClass = 'flex min-w-0 items-center gap-1 rounded-md border border-line bg-panel px-2 py-1 text-xs text-muted hover:text-fg'
  return <div className="flex max-w-[85%] flex-wrap justify-end gap-1.5">
    {paths?.map((path) => {
      const name = path.split('/').pop() ?? path
      if (sid && isAttachmentImage(name)) return <ImagePreview key={path} url={imageUrl(sid, path)} name={name} history />
      if (sid && path.startsWith('.chat-attachments/')) {
        return <a key={path} className={linkClass} href={imageUrl(sid, path)} download={name}><FileIcon name={name} /><span className="truncate">{name}</span></a>
      }
      return <button type="button" key={path} className={linkClass} onClick={() => onOpenFile(path)}><FileIcon name={name} /><span className="truncate">{name}</span></button>
    })}
    {documentIds?.map((id) => {
      const doc = docs.data?.docs.find((item) => item.id === id)
      const label = doc?.name ?? t('Tài liệu đã chọn')
      return doc
        ? <a key={id} href={`/api/knowledge/${encodeURIComponent(id)}/file`} className={linkClass}><FileIcon name={label} /><span className="truncate">{label}</span></a>
        : <span key={id} className={linkClass}><FileText className="size-4" />{label}</span>
    })}
  </div>
}

const fetchLibrary = () => api.get<{ docs: LibraryDocument[] }>('/api/knowledge')
const menuItem = 'flex w-full items-center gap-2 rounded-lg px-2.5 py-2 text-left text-sm hover:bg-panel2'

export function AttachmentMenu({ draft, categoryId, children, disabled }: {
  draft: AttachmentDraft; categoryId?: string; children?: (close: () => void) => ReactNode; disabled?: boolean
}) {
  const [open, setOpen] = useState(false)
  const [picker, setPicker] = useState(false)
  const box = useRef<HTMLDivElement>(null)
  const input = useRef<HTMLInputElement>(null)
  const button = useRef<HTMLButtonElement>(null)
  useEffect(() => {
    if (!open) return
    const outside = (event: PointerEvent) => { if (!box.current?.contains(event.target as Node)) setOpen(false) }
    document.addEventListener('pointerdown', outside)
    return () => document.removeEventListener('pointerdown', outside)
  }, [open])
  const close = () => setOpen(false)
  return <div ref={box} className="relative shrink-0" onKeyDown={(e) => {
    if (e.key === 'Escape' && open) { close(); button.current?.focus() }
  }}>
    <input ref={input} type="file" accept={attachmentAccept} multiple hidden onChange={(e) => {
      draft.add([...e.currentTarget.files ?? []])
      e.currentTarget.value = ''
    }} />
    <button ref={button} type="button" disabled={disabled} onClick={() => setOpen(!open)} aria-expanded={open}
      aria-label={t('Đính kèm tệp hoặc ảnh')} title={t('Đính kèm tệp hoặc ảnh')}
      className="grid size-8 place-items-center rounded-full text-muted hover:bg-panel2 hover:text-fg disabled:opacity-40"><Plus className="size-[18px]" /></button>
    {open && !disabled && <div className="absolute bottom-full left-0 z-30 mb-2 w-64 max-w-[80vw] rounded-xl border border-line bg-panel p-1.5 shadow-2xl">
      <button type="button" onClick={() => { close(); input.current?.click() }} className={menuItem}><Paperclip className="size-4 text-muted" />{t('Đính kèm tệp hoặc ảnh')}</button>
      <button type="button" onClick={() => { close(); setPicker(true) }} className={menuItem}><FileText className="size-4 text-muted" />{t('Chọn từ Kho tài liệu (Document RAG)')}</button>
      {children?.(close)}
    </div>}
    {picker && <DocumentPicker categoryId={categoryId} selected={draft.documents} onConfirm={(docs) => { draft.setDocuments(docs); setPicker(false); button.current?.focus() }}
      onClose={() => { setPicker(false); button.current?.focus() }} />}
  </div>
}

function DocumentPicker({ categoryId, selected, onConfirm, onClose }: {
  categoryId?: string; selected: SelectedDocument[]; onConfirm: (docs: SelectedDocument[]) => void; onClose: () => void
}) {
  const dialog = useRef<HTMLDialogElement>(null)
  const [selection, setSelection] = useState(() => new Map(selected.map((doc) => [doc.id, doc])))
  const [category, setCategory] = useState(categoryId ?? '')
  const [search, setSearch] = useState('')
  const [keyword, setKeyword] = useState('')
  useEffect(() => {
    const timer = window.setTimeout(() => setKeyword(search.trim()), 250)
    return () => window.clearTimeout(timer)
  }, [search])
  const docs = useQuery({ queryKey: ['attachment-library'], queryFn: fetchLibrary, refetchInterval: 5000 })
  const categories = useQuery({ queryKey: ['attachment-categories'], queryFn: () => api.get<{ id: string; name: string }[]>('/api/knowledge/categories') })
  const matches = useQuery({
    queryKey: ['attachment-keywords', category, keyword],
    queryFn: () => api.get<string[]>(`/api/knowledge/matches?${new URLSearchParams({ q: keyword, ...(category ? { category_id: category } : {}) })}`),
    enabled: keyword.length >= 2,
  })
  const tokens = searchableText(search.trim()).split(/\s+/)
  const contentMatches = new Set(search.trim() === keyword ? matches.data : [])
  const visible = docs.data?.docs.filter((doc) => (!category || doc.category_id === category)
    && (tokens.every((term) => searchableText(doc.name).includes(term)) || contentMatches.has(doc.id))) ?? []
  const searching = search.trim().length >= 2 && (keyword !== search.trim() || matches.isFetching)
  useEffect(() => { dialog.current?.showModal() }, [])
  return <dialog ref={dialog} onKeyDown={(e) => {
    if (e.key === 'Enter' && (e.target as HTMLElement).tagName === 'INPUT' && (e.target as HTMLInputElement).type === 'search') e.preventDefault()
  }} onCancel={(e) => { e.preventDefault(); onClose() }} aria-label={t('Chọn từ Kho tài liệu (Document RAG)')}
    className="m-auto w-[min(46rem,calc(100vw-2rem))] rounded-xl border border-line bg-panel p-0 text-fg backdrop:bg-black/60">
    <header className="border-b border-line p-4">
      <h2 className="font-semibold">{t('Chọn từ Kho tài liệu (Document RAG)')}</h2>
      <input type="search" maxLength={160} value={search} onChange={(e) => setSearch(e.target.value)} aria-label={t('Tìm tài liệu')}
        placeholder={t('Tìm theo tên hoặc từ khóa')} className="mt-3 w-full rounded-lg border border-line bg-bg px-3 py-2 text-sm" />
    </header>
    <div className="grid sm:grid-cols-[minmax(0,1fr)_minmax(0,2fr)]">
      <nav aria-label={t('Danh mục')} className="flex max-h-28 gap-1 overflow-auto border-b border-line p-2 sm:max-h-[47vh] sm:flex-col sm:border-b-0 sm:border-r">
        {!categoryId && <button type="button" aria-pressed={!category} onClick={() => setCategory('')} className="shrink-0 rounded-lg px-2 py-1.5 text-left text-sm hover:bg-panel2 aria-pressed:bg-accent/15">{t('Tất cả danh mục')}</button>}
        {categories.data?.filter((entry) => !categoryId || entry.id === categoryId).map((entry) => (
          <button key={entry.id} type="button" aria-pressed={entry.id === category} onClick={() => setCategory(entry.id)}
            className="shrink-0 rounded-lg px-2 py-1.5 text-left text-sm hover:bg-panel2 aria-pressed:bg-accent/15">{entry.name}</button>
        ))}
      </nav>
      <div className="h-[38vh] overflow-y-auto p-2 sm:h-[47vh]">
        {(categories.error || docs.error) && <p role="alert" className="p-2 text-sm text-bad">{errMsg(categories.error ?? docs.error)}</p>}
        {matches.error && <p role="alert" className="p-2 text-sm text-bad">{errMsg(matches.error)}</p>}
        {(docs.isPending || (searching && !visible.length)) && <p className="p-2 text-sm text-muted">{t('Đang tải…')}</p>}
        {!docs.isPending && !docs.error && !searching && !visible.length && <p className="p-2 text-sm text-muted">{t('Không tìm thấy tài liệu.')}</p>}
        {visible.map((doc) => {
          const ready = doc.status === 'ready' && doc.chunks > 0
          const checked = ready && selection.has(doc.id)
          return <label key={doc.id} className="flex items-center gap-2 rounded-lg px-2 py-2 text-sm hover:bg-panel2">
            <input type="checkbox" checked={checked} disabled={!ready || (!checked && selection.size >= MAX_DOCUMENTS)}
              onChange={(e) => {
                const want = e.currentTarget.checked
                setSelection((current) => {
                  const next = new Map(current)
                  if (want) next.set(doc.id, doc)
                  else next.delete(doc.id)
                  return next
                })
              }} />
            <span className="min-w-0 flex-1 break-words">{doc.name}</span>
            <span className="shrink-0 text-xs text-muted">{ready ? t('Sẵn sàng') : doc.status === 'indexing' ? t('Đang xử lý…') : doc.status === 'error' ? t('Lỗi') : t('Chỉ lưu file')}</span>
          </label>
        })}
      </div>
    </div>
    <footer className="flex flex-wrap items-center justify-end gap-2 border-t border-line p-3 text-sm">
      <span className="mr-auto text-muted">{t('Đã chọn {n} tài liệu', { n: selection.size })}</span>
      <button type="button" onClick={onClose} className="rounded-lg border border-line px-3 py-2">{t('Hủy bỏ')}</button>
      <button type="button" disabled={!docs.data || !!docs.error} onClick={() => {
        const ready = new Set(docs.data?.docs.filter((doc) => doc.status === 'ready' && doc.chunks > 0 && (!categoryId || doc.category_id === categoryId)).map((doc) => doc.id))
        onConfirm([...selection.values()].filter((doc) => ready.has(doc.id)))
      }} className="rounded-lg bg-accent px-3 py-2 text-accent-fg disabled:opacity-40">{t('Đính kèm vào đoạn chat')}</button>
    </footer>
  </dialog>
}
