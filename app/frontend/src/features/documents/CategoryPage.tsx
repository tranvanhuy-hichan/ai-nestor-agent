import { useEffect, useRef, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { ArrowLeft, Check, Copy, Download, ExternalLink, File as FileIcon, FileSearch, FileSpreadsheet, FileText, FolderUp, Layers, LoaderCircle, MoreVertical, Presentation, ScanSearch, Send, Sparkles, Square, Trash2, Upload } from 'lucide-react'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { Field, Textarea } from '@/components/ui/Form'
import { Modal } from '@/components/ui/Modal'
import { ErrorNote, Loading, Page } from '@/components/ui/misc'
import { useToast } from '@/components/ui/Toast'
import { api } from '@/lib/api'
import { t } from '@/lib/i18n.ts'
import type { KbCategory, KbDoc } from '@/lib/types'
import { cn, errMsg, timeAgo } from '@/lib/utils'
import { MessageView } from '@/features/chat/MessageView'
import { SessionContext } from '@/features/chat/session'
import { useChat } from '@/features/chat/useChat'
import { useConfig } from '@/lib/queries'

interface KbList { docs: KbDoc[]; stats: { docs: number; chunks: number; indexing: number }; supported: string[]; semantic: string | null }
interface ChunkItem { id: number; ord: number; loc: string; text: string }

const icon = (ext: string) => (ext === '.xlsx' || ext === '.xlsm' || ext === '.csv' || ext === '.tsv' ? FileSpreadsheet : ext === '.pptx' ? Presentation : ext === '.pdf' || ext === '.docx' || ext === '.txt' || ext === '.md' ? FileText : FileIcon)
const size = (n: number) => (n >= 1 << 20 ? `${(n / (1 << 20)).toFixed(1)} MB` : `${Math.max(1, Math.round(n / 1024))} KB`)

type Item = { file: File; name: string }

async function walk(entry: FileSystemEntry, prefix = ''): Promise<Item[]> {
  if (entry.isFile) {
    const file = await new Promise<File>((res, rej) => (entry as FileSystemFileEntry).file(res, rej))
    return [{ file, name: prefix + file.name }]
  }
  const reader = (entry as FileSystemDirectoryEntry).createReader()
  const out: Item[] = []
  for (;;) {
    const batch = await new Promise<FileSystemEntry[]>((res, rej) => reader.readEntries(res, rej))
    if (!batch.length) break
    for (const e of batch) if (!e.name.startsWith('.')) out.push(...(await walk(e, `${prefix}${entry.name}/`)))
  }
  return out
}

function ChunksModal({ doc, onClose }: { doc: KbDoc | null; onClose: () => void }) {
  const toast = useToast()
  const [copiedId, setCopiedId] = useState<number | null>(null)
  const q = useQuery({
    queryKey: ['kb-chunks', doc?.id],
    queryFn: () => api.get<{ doc: KbDoc; chunks: ChunkItem[] }>(`/api/knowledge/${doc!.id}/chunks`),
    enabled: !!doc,
  })
  const copyChunk = (id: number, text: string) => {
    navigator.clipboard.writeText(text)
    setCopiedId(id)
    setTimeout(() => setCopiedId(null), 1500)
    toast(t('Đã chép đoạn trích'))
  }
  return (
    <Modal open={!!doc} onClose={onClose} wide title={doc ? `${t('Đoạn trích:')} ${doc.name}` : ''} footer={<Button onClick={onClose}>{t('Đóng')}</Button>}>
      {q.isLoading ? <Loading /> : q.error ? <p className="text-sm text-bad">{errMsg(q.error)}</p> : (
        <div className="space-y-4 max-h-[60vh] overflow-y-auto pr-1">
          {q.data?.chunks.length === 0 ? <p className="py-6 text-center text-sm text-muted">{t('Tài liệu này chưa có đoạn trích nào.')}</p> : q.data?.chunks.map((c) => (
            <div key={c.id} className="rounded-lg border border-line bg-panel2/50 p-3.5 text-xs">
              <div className="mb-2 flex items-center justify-between font-mono text-[11px] text-muted">
                <span className="font-semibold text-accent">#{c.ord + 1} {c.loc ? `· ${c.loc}` : ''}</span>
                <button onClick={() => copyChunk(c.id, c.text)} className="flex items-center gap-1 rounded px-1.5 py-0.5 hover:bg-panel hover:text-fg">
                  {copiedId === c.id ? <Check className="size-3 text-ok" /> : <Copy className="size-3" />}{copiedId === c.id ? t('Đã chép') : t('Chép')}
                </button>
              </div>
              <p className="whitespace-pre-wrap break-words leading-relaxed text-fg">{c.text}</p>
            </div>
          ))}
        </div>
      )}
    </Modal>
  )
}

const store = {
  get: (k: string) => { try { return localStorage.getItem(k) } catch { return null } },
  set: (k: string, v: string) => { try { localStorage.setItem(k, v) } catch { /* che do rieng tu */ } },
}

/** Menu ba chấm gom các hành động của 1 tài liệu (xem, xem đoạn trích, tải về, xóa). */
function DocRowMenu({ doc, onPreviewChunks, onDelete }: { doc: KbDoc; onPreviewChunks: () => void; onDelete: () => void }) {
  const [open, setOpen] = useState(false)
  const box = useRef<HTMLDivElement>(null)
  useEffect(() => {
    if (!open) return
    const down = (e: MouseEvent) => { if (!box.current?.contains(e.target as Node)) setOpen(false) }
    document.addEventListener('mousedown', down)
    return () => document.removeEventListener('mousedown', down)
  }, [open])
  return (
    <div ref={box} className="relative shrink-0">
      <button onClick={() => setOpen((o) => !o)} aria-haspopup="menu" aria-expanded={open} aria-label={t('Thêm tùy chọn')} title={t('Thêm tùy chọn')}
        className="rounded p-1.5 text-muted hover:bg-panel2 hover:text-fg"><MoreVertical className="size-4" /></button>
      {open && (
        <div role="menu" className="fade-in absolute right-0 top-full z-20 mt-1 w-52 rounded-xl border border-line bg-panel p-1.5 shadow-2xl">
          <a role="menuitem" href={`/api/knowledge/${doc.id}/file?inline=true`} target="_blank" rel="noreferrer" onClick={() => setOpen(false)}
            className="flex w-full items-center gap-2.5 rounded-lg px-2.5 py-2 text-left text-sm hover:bg-panel2"><ExternalLink className="size-4 text-muted" />{t('Xem file gốc')}</a>
          <button role="menuitem" onClick={() => { setOpen(false); onPreviewChunks() }}
            className="flex w-full items-center gap-2.5 rounded-lg px-2.5 py-2 text-left text-sm hover:bg-panel2"><Layers className="size-4 text-muted" />{t('Xem các đoạn trích')}</button>
          <a role="menuitem" href={`/api/knowledge/${doc.id}/file`} download onClick={() => setOpen(false)}
            className="flex w-full items-center gap-2.5 rounded-lg px-2.5 py-2 text-left text-sm hover:bg-panel2"><Download className="size-4 text-muted" />{t('Tải về file gốc')}</a>
          <button role="menuitem" onClick={() => { setOpen(false); onDelete() }}
            className="flex w-full items-center gap-2.5 rounded-lg px-2.5 py-2 text-left text-sm text-bad hover:bg-bad/10"><Trash2 className="size-4" />{t('Xóa tài liệu')}</button>
        </div>
      )}
    </div>
  )
}

function loadCategoryChat(categoryId: string, create = false) {
  const previous = [store.get(`kb-chat-${categoryId}`)].filter((sid): sid is string => !!sid)
  return api.post<{ id: string | null }>(`/api/knowledge/categories/${categoryId}/chat`, { create, previous })
}

/** Khung chat ben phai, gioi han dung trong pham vi tai lieu cua 1 danh muc (kieu NotebookLM). */
function CategoryChat({ categoryId, categoryName, width, onWidth }: { categoryId: string; categoryName: string; width: number; onWidth: (w: number) => void }) {
  const cfg = useConfig()
  const chat = useChat()
  const [text, setText] = useState('')
  const [preparing, setPreparing] = useState(false)
  const [ready, setReady] = useState(false)
  const [loadError, setLoadError] = useState<unknown>(null)
  const [attempt, setAttempt] = useState(0)
  const [provider, setProvider] = useState<string | null>(() => store.get('kb-chat-provider'))
  const openChat = chat.open
  const scroller = useRef<HTMLDivElement>(null)
  const mounted = useRef(false)
  const stick = useRef(true)
  const drag = useRef(false)

  useEffect(() => {
    mounted.current = true
    let cancelled = false
    void loadCategoryChat(categoryId).then(async ({ id }) => {
      if (cancelled) return
      if (id) await openChat(id)
      if (!cancelled) setReady(true)
    }).catch((error: unknown) => { if (!cancelled) setLoadError(error) })
    return () => { cancelled = true; mounted.current = false }
  }, [categoryId, openChat, attempt])
  useEffect(() => { const el = scroller.current; if (el && stick.current) el.scrollTop = el.scrollHeight }, [chat.items, chat.status])

  const provs = cfg.data?.config.providers ?? {}
  const active = provider && provs[provider] ? provider : (cfg.data?.config.default_provider ?? null)
  const pickProvider = (id: string) => { setProvider(id); store.set('kb-chat-provider', id) }
  const submit = async (v: string) => {
    if (!v.trim() || !ready || loadError || chat.busy || preparing) return
    setPreparing(true)
    try {
      const { id } = await loadCategoryChat(categoryId, true)
      if (!id || !mounted.current) return
      if (id !== chat.sessionId) await openChat(id)
      if (!mounted.current) return
      store.set(`kb-chat-${categoryId}`, id)
      setText('')
      stick.current = true
      await chat.send(v, active, [], { context: `kb-category:${categoryId}`, permission: 'guarded' })
    } catch (error) {
      if (mounted.current) setLoadError(error)
    } finally {
      if (mounted.current) setPreparing(false)
    }
  }

  return (
    <SessionContext.Provider value={chat.sessionId}>
      <aside aria-label={t('Hỏi đáp về danh mục này')} style={{ width }} className="relative hidden shrink-0 flex-col border-l border-line bg-panel md:flex">
        <div role="separator" aria-orientation="vertical" aria-label={t('Kéo để đổi độ rộng')}
          onPointerDown={(e) => { drag.current = true; e.currentTarget.setPointerCapture(e.pointerId) }}
          onPointerMove={(e) => { if (drag.current) onWidth(Math.min(window.innerWidth * 0.65, Math.max(320, window.innerWidth - e.clientX))) }}
          onPointerUp={(e) => { drag.current = false; e.currentTarget.releasePointerCapture(e.pointerId) }}
          className="group absolute left-0 top-0 z-10 flex h-full w-3 -translate-x-1/2 cursor-col-resize items-center justify-center touch-none">
          <div className="h-full w-px bg-line transition group-hover:w-1 group-hover:bg-accent" />
        </div>
        <header className="shrink-0 border-b border-line px-4 pb-3 pt-4">
          <div className="flex items-start gap-3">
            <span className="grid size-10 shrink-0 place-items-center rounded-xl bg-accent/12 text-accent"><Sparkles className="size-5" /></span>
            <div className="min-w-0 flex-1">
              <h2 className="flex items-center gap-2 text-sm font-semibold">{t('Hỏi đáp về danh mục này')}{chat.busy && <LoaderCircle className="size-3.5 shrink-0 animate-spin text-accent" />}</h2>
              <p className="mt-0.5 truncate text-xs text-muted" title={categoryName}>{categoryName}</p>
            </div>
          </div>
        </header>
        <div ref={scroller} onScroll={(e) => { const el = e.currentTarget; stick.current = el.scrollHeight - el.scrollTop - el.clientHeight < 80 }} className="min-h-0 flex-1 overflow-y-auto">
          <div className="space-y-4 p-4">
            {loadError ? <div className="space-y-2">
              <ErrorNote error={loadError} />
              <Button size="sm" onClick={() => { setLoadError(null); setReady(false); setAttempt((n) => n + 1) }}>{t('Thử lại')}</Button>
            </div> : !ready ? <Loading /> : chat.items.length === 0 ? (
              <p className="text-sm leading-relaxed text-muted">{t('Hỏi bất cứ điều gì về các tài liệu trong danh mục này. Câu trả lời chỉ dựa trên tài liệu ở đây, kèm nguồn trích dẫn.')}</p>
            ) : chat.items.map((it) => (
              <MessageView key={it.key} item={it} sid={chat.sessionId ?? undefined} onDecide={(aid, ok) => void chat.decide(aid, ok)} onAnswer={(q, a) => void chat.answer(q, a)} onUndo={() => void chat.undo()} onOpenFile={() => undefined} canAct={!chat.busy} />
            ))}
            {chat.busy && chat.status && <p className="flex items-center gap-2 text-xs text-muted" role="status"><LoaderCircle className="size-3.5 animate-spin text-accent" />{chat.status}</p>}
          </div>
        </div>
        <form className="border-t border-line bg-panel p-4" onSubmit={(e) => { e.preventDefault(); void submit(text) }}>
          <div className="rounded-xl border border-line bg-bg shadow-sm transition focus-within:border-accent focus-within:ring-2 focus-within:ring-accent/12">
            <textarea value={text} onChange={(e) => setText(e.target.value)} rows={2} placeholder={t('Hỏi về tài liệu trong danh mục này… (Enter để gửi)')} aria-label={t('Nhắn cho agent')}
              onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey && !e.nativeEvent.isComposing) { e.preventDefault(); void submit(text) } }}
              className="block min-h-12 w-full resize-none bg-transparent px-3 pt-2.5 text-sm focus:outline-none" />
            <div className="flex items-center justify-between gap-2 px-2 pb-2">
              <select value={active ?? ''} onChange={(e) => pickProvider(e.target.value)} aria-label={t('Chọn model')} title={t('Chọn model')}
                className="min-w-0 max-w-[15rem] flex-1 truncate rounded-md border border-transparent bg-transparent px-1.5 py-1 text-xs text-muted hover:border-line hover:text-fg focus:outline-none">
                {Object.entries(provs).map(([id, c]) => <option key={id} value={id}>{id}{c.model ? ` · ${c.model}` : ''}</option>)}
              </select>
              {chat.busy
                ? <Button type="button" size="sm" onClick={chat.stop} aria-label={t('Dừng')}><Square className="size-3.5" /></Button>
                : <Button type="submit" size="sm" variant="primary" disabled={!text.trim() || preparing || !ready || !!loadError} aria-label={t('Gửi')}><Send className="size-3.5" /></Button>}
            </div>
          </div>
        </form>
      </aside>
    </SessionContext.Provider>
  )
}

export function CategoryPage() {
  const { categoryId } = useParams()
  const nav = useNavigate()
  const qc = useQueryClient()
  const toast = useToast()
  const filePick = useRef<HTMLInputElement>(null)
  const dirPick = useRef<HTMLInputElement>(null)
  const [drag, setDrag] = useState(false)
  const [analyzing, setAnalyzing] = useState(false)
  const [focus, setFocus] = useState('')
  const [progress, setProgress] = useState<{ done: number; total: number } | null>(null)
  const [previewDoc, setPreviewDoc] = useState<KbDoc | null>(null)
  const [chatWidth, setChatWidth] = useState(() => {
    const saved = store.get('kb-chat-width')
    return saved ? Number(saved) : Math.round(window.innerWidth * 0.65)
  })
  useEffect(() => { store.set('kb-chat-width', String(chatWidth)) }, [chatWidth])

  const cat = useQuery({ queryKey: ['kb-categories'], queryFn: () => api.get<KbCategory[]>('/api/knowledge/categories') })
  const category = cat.data?.find((c) => c.id === categoryId)
  const list = useQuery({
    queryKey: ['kb', categoryId], enabled: !!categoryId,
    queryFn: () => api.get<KbList>(`/api/knowledge?category_id=${categoryId}`),
    refetchInterval: (q) => (q.state.data?.stats.indexing ? 1500 : 10_000),
  })
  const supported = new Set(list.data?.supported ?? [])
  const refresh = () => { void qc.invalidateQueries({ queryKey: ['kb', categoryId] }); void qc.invalidateQueries({ queryKey: ['kb-categories'] }) }

  const upload = async (items: Item[]) => {
    const ok = items.filter((i) => supported.size === 0 || supported.has('.' + (i.name.split('.').pop() ?? '').toLowerCase()))
    const skipped = items.length - ok.length
    if (!ok.length) return toast(t('Không có file nào được hỗ trợ (PDF, Word, Excel, PowerPoint, văn bản).'), 'bad')
    let added = 0, dup = 0, failed = 0
    for (let i = 0; i < ok.length; i++) {
      setProgress({ done: i, total: ok.length })
      try {
        const r = await fetch(`/api/knowledge/upload?name=${encodeURIComponent(ok[i].name)}&category_id=${categoryId}`, { method: 'POST', headers: { 'Content-Type': 'application/octet-stream' }, body: ok[i].file })
        if (!r.ok) throw new Error((await r.json().catch(() => ({ detail: r.statusText }))).detail)
        if ((await r.json()).duplicate) dup++; else added++
      } catch (e) {
        failed++
        toast(`${ok[i].name}: ${errMsg(e)}`, 'bad')
      }
    }
    setProgress(null)
    refresh()
    toast(t('Đã thêm {n} tài liệu', { n: added }) + (dup ? t(' · {n} trùng', { n: dup }) : '') + (skipped ? t(' · bỏ qua {n} file không hỗ trợ', { n: skipped }) : '') + (failed ? t(' · {n} lỗi', { n: failed }) : ''))
  }
  const onDrop = async (e: React.DragEvent) => {
    e.preventDefault()
    setDrag(false)
    const entries = [...e.dataTransfer.items].map((i) => i.webkitGetAsEntry?.()).filter((x): x is FileSystemEntry => !!x)
    const items = entries.length ? (await Promise.all(entries.map((x) => walk(x)))).flat() : [...e.dataTransfer.files].map((file) => ({ file, name: file.name }))
    void upload(items)
  }
  const fromInput = (files: FileList | null) => { if (files) void upload([...files].map((file) => ({ file, name: file.webkitRelativePath || file.name }))) }

  const analyze = useMutation({
    mutationFn: () => api.post<{ id: string }>('/api/knowledge/analyze', { focus, category_id: categoryId }),
    onSuccess: () => { toast(t('Đã bắt đầu phân tích. Kết quả sẽ có ở trang Tác vụ.')); setAnalyzing(false); setFocus(''); nav('/tasks') },
    onError: (e) => toast(errMsg(e), 'bad'),
  })
  const del = useMutation({ mutationFn: (id: string) => api.del(`/api/knowledge/${id}`), onSuccess: refresh, onError: (e) => toast(errMsg(e), 'bad') })

  if (!categoryId) return null
  if (cat.isLoading || list.isLoading) return <Loading />
  if (!category) return <Page><Link to="/documents" className="mb-4 inline-flex items-center gap-2 text-sm text-accent"><ArrowLeft className="size-4" />{t('Tài liệu')}</Link><ErrorNote error={new Error(t('Không có danh mục này'))} /></Page>

  const docs = list.data?.docs ?? []
  const stats = list.data?.stats

  return (
    <div className="flex h-full min-h-0">
      <div className="min-w-0 flex-1 overflow-y-auto">
        <div className="mx-auto w-full px-4 pb-24 pt-5 sm:px-8">
          <div className="mb-4 flex flex-wrap items-center justify-between gap-3 border-b border-line pb-4">
            <nav aria-label={t('Đường dẫn')} className="flex min-w-0 items-center gap-1.5 text-xl font-bold tracking-tight sm:text-2xl">
              <Link to="/documents" className="shrink-0 rounded-md p-1 text-muted hover:text-accent" aria-label={t('Tài liệu')} title={t('Tài liệu')}><ArrowLeft className="size-5" /></Link>
              <span className="truncate">{category.icon} {category.name}</span>
            </nav>
            <div className="flex flex-wrap gap-2">
              <Button onClick={() => filePick.current?.click()}><Upload className="size-4" />{t('Chọn file')}</Button>
              <Button onClick={() => dirPick.current?.click()}><FolderUp className="size-4" />{t('Chọn thư mục')}</Button>
              <Button disabled={!stats?.docs} title={stats?.docs ? t('Đọc kỹ tài liệu, nêu rủi ro và đề xuất phương án (chạy nền)') : t('Thêm tài liệu trước khi hỏi')} onClick={() => setAnalyzing(true)}><ScanSearch className="size-4" />{t('Phân tích tài liệu')}</Button>
            </div>
          </div>
          <input ref={filePick} type="file" multiple hidden accept={[...supported].join(',')} onChange={(e) => { fromInput(e.target.files); e.target.value = '' }} />
          <input ref={dirPick} type="file" hidden multiple {...({ webkitdirectory: '', directory: '' } as object)} onChange={(e) => { fromInput(e.target.files); e.target.value = '' }} />

          <div onDragOver={(e) => { e.preventDefault(); setDrag(true) }} onDragLeave={() => setDrag(false)} onDrop={(e) => void onDrop(e)}
            className={cn('mb-4 grid place-items-center rounded-xl border-2 border-dashed px-6 py-8 text-center transition', drag ? 'border-accent bg-accent/5' : 'border-line bg-panel')}>
            <div>
              <FileSearch className="mx-auto mb-2 size-8 text-accent" />
              <p className="font-medium">{progress ? t('Đang tải {done}/{total}…', { done: progress.done + 1, total: progress.total }) : t('Kéo thả file hoặc thư mục vào đây')}</p>
              {progress && <div className="mx-auto mt-3 h-2 w-64 overflow-hidden rounded-full bg-panel2"><div className="h-full bg-accent transition-all duration-300" style={{ width: `${Math.round(((progress.done + 1) / progress.total) * 100)}%` }} /></div>}
              <p className="mt-1 text-sm text-muted">PDF · Word · Excel (.xlsx) · PowerPoint (.pptx) · TXT · Markdown · CSV</p>
            </div>
          </div>

          {!!stats?.indexing && (
            <div className="mb-4 flex items-center gap-3 rounded-xl border border-info/30 bg-info/10 px-4 py-3 text-xs text-info">
              <span className="size-2 animate-ping rounded-full bg-info" />
              <span className="font-medium">{t('Đang phân tích đoạn trích và embedding {n} tài liệu (chạy nền)…', { n: stats.indexing })}</span>
            </div>
          )}

          <div className="rounded-xl border border-line bg-panel">
            {docs.length === 0 ? (
              <p className="p-8 text-center text-sm text-muted">{t('Chưa có tài liệu nào trong danh mục này. Kéo thả hợp đồng, báo cáo hoặc bảng tính vào ô phía trên để bắt đầu.')}</p>
            ) : docs.map((d) => {
              const Icon = icon(d.ext)
              return (
                <div key={d.id} className="flex items-start gap-3 border-b border-line px-5 py-3 last:border-b-0">
                  <Icon className="mt-0.5 size-5 shrink-0 text-muted" />
                  <div className="min-w-0 flex-1">
                    <p className="flex flex-wrap items-center gap-2"><span className="truncate font-medium" title={d.name}>{d.name}</span>
                      {d.status === 'ready' ? <Badge tone="ok">{t('Sẵn sàng')}</Badge> : d.status === 'indexing' ? <Badge tone="info">{t('Đang xử lý…')}</Badge> : <Badge tone="bad">{t('Lỗi')}</Badge>}</p>
                    <p className="mt-0.5 text-xs text-muted">{size(d.size)}{d.pages && (d.ext === '.pdf' || d.ext === '.pptx') ? ` · ${t('{n} trang', { n: d.pages })}` : ''}{d.chunks ? ` · ${t('{n} đoạn', { n: d.chunks })}` : ''} · {timeAgo(d.added)}</p>
                    {d.note && <p className={cn('mt-1 text-xs', d.status === 'error' ? 'text-bad' : 'text-warn')}>{d.note}</p>}
                  </div>
                  <DocRowMenu doc={d} onPreviewChunks={() => setPreviewDoc(d)}
                    onDelete={() => { if (confirm(t('Xóa "{name}" khỏi kho tài liệu?', { name: d.name }))) del.mutate(d.id) }} />
                </div>
              )
            })}
          </div>
        </div>
      </div>
      <CategoryChat categoryId={categoryId} categoryName={category.name} width={chatWidth} onWidth={setChatWidth} />

      <ChunksModal doc={previewDoc} onClose={() => setPreviewDoc(null)} />

      <Modal open={analyzing} onClose={() => setAnalyzing(false)} title={t('Phân tích tài liệu và đề xuất phương án')} wide
        footer={<><Button onClick={() => setAnalyzing(false)}>{t('Hủy')}</Button><Button variant="primary" loading={analyze.isPending} onClick={() => analyze.mutate()}><ScanSearch className="size-4" />{t('Bắt đầu phân tích')}</Button></>}>
        <div className="space-y-3">
          <Field label={t('Bạn muốn phân tích điều gì? (không bắt buộc)')}>
            <Textarea rows={5} value={focus} onChange={(e) => setFocus(e.target.value)} placeholder={t('Ví dụ: Phân tích rủi ro và đề xuất phương án thực hiện trong 90 ngày.')} />
          </Field>
          <p className="text-sm text-muted">{t('Nestor đọc kỹ các tài liệu trong danh mục này, rồi viết báo cáo gồm: tóm tắt, yêu cầu chính, rủi ro, các phương án, khuyến nghị và các bước thực hiện, kèm nguồn. Việc này chạy nền (có thể mất vài phút); kết quả xem ở trang Tác vụ.')}</p>
        </div>
      </Modal>
    </div>
  )
}
