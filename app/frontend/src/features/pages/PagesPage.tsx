import { useEffect, useMemo, useRef, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useNavigate, useParams } from 'react-router-dom'
import { Bold, ChevronRight, Code, FilePlus, LoaderCircle, Send, Sparkles, Square, X, FileText, Heading1, Heading2, Heading3, Italic, List, ListChecks, ListOrdered, Minus, Plus, Quote, Table as TableIcon, Trash2 } from 'lucide-react'
import { EditorContent, useEditor, type Editor } from '@tiptap/react'
import StarterKit from '@tiptap/starter-kit'
import Placeholder from '@tiptap/extension-placeholder'
import { TaskItem, TaskList } from '@tiptap/extension-list'
import { Table, TableCell, TableHeader, TableRow } from '@tiptap/extension-table'
import { Markdown } from 'tiptap-markdown'
import { Button } from '@/components/ui/Button'
import { ErrorNote, Loading } from '@/components/ui/misc'
import { useToast } from '@/components/ui/Toast'
import { api } from '@/lib/api'
import { useConfig } from '@/lib/queries'
import { t, tk } from '@/lib/i18n.ts'
import { cn, errMsg } from '@/lib/utils'
import { MessageView } from '@/features/chat/MessageView'
import { SessionContext } from '@/features/chat/session'
import { useChat } from '@/features/chat/useChat'

interface PageInfo { id: string; title: string; parent: string; icon: string; order: number; updated: number }
interface PageFull extends PageInfo { content: string }

const SAVE_DELAY = 800

function Tree({ pages, parent, depth, current, open, toggle, onAdd, onDelete, onOpen }: {
  pages: PageInfo[]; parent: string; depth: number; current: string | undefined; open: Set<string>
  toggle: (id: string) => void; onAdd: (parent: string) => void; onDelete: (p: PageInfo) => void; onOpen: (id: string) => void
}) {
  return (
    <>
      {pages.filter((p) => p.parent === parent).map((p) => {
        const kids = pages.some((c) => c.parent === p.id)
        return (
          <div key={p.id}>
            <div className={cn('group flex items-center gap-1 rounded-lg py-1.5 pr-1 text-sm', current === p.id ? 'bg-accent/15 font-medium text-fg' : 'text-muted hover:bg-panel2 hover:text-fg')} style={{ paddingLeft: 4 + depth * 14 }}>
              <button type="button" aria-label={t('Mở rộng')} onClick={() => toggle(p.id)} className={cn('grid size-5 shrink-0 place-items-center rounded hover:bg-line', !kids && 'invisible')}>
                <ChevronRight className={cn('size-3.5 transition', open.has(p.id) && 'rotate-90')} />
              </button>
              <button type="button" onClick={() => onOpen(p.id)} className="flex min-w-0 flex-1 items-center gap-1.5 text-left">
                {p.icon ? <span className="shrink-0">{p.icon}</span> : <FileText className="size-3.5 shrink-0" />}
                <span className="truncate">{p.title}</span>
              </button>
              <button type="button" title={t('Thêm trang con')} onClick={() => onAdd(p.id)} className="hidden size-5 shrink-0 place-items-center rounded hover:bg-line group-hover:grid"><Plus className="size-3.5" /></button>
              <button type="button" title={t('Xóa trang')} onClick={() => onDelete(p)} className="hidden size-5 shrink-0 place-items-center rounded hover:bg-line hover:text-bad group-hover:grid"><Trash2 className="size-3.5" /></button>
            </div>
            {kids && open.has(p.id) && <Tree pages={pages} parent={p.id} depth={depth + 1} current={current} open={open} toggle={toggle} onAdd={onAdd} onDelete={onDelete} onOpen={onOpen} />}
          </div>
        )
      })}
    </>
  )
}

function B({ on, active, label, children }: { on: () => void; active?: boolean; label: string; children: React.ReactNode }) {
  return (
    <button type="button" title={label} aria-label={label} onMouseDown={(e) => e.preventDefault()} onClick={on}
      className={cn('grid size-7 place-items-center rounded hover:bg-panel2', active ? 'bg-panel2 text-accent' : 'text-muted')}>{children}</button>
  )
}

function Toolbar({ editor, onSubpage }: { editor: Editor; onSubpage: () => void }) {
  const c = () => editor.chain().focus()
  return (
    <div className="sticky top-0 z-10 mb-4 flex flex-wrap items-center gap-0.5 rounded-xl border border-line bg-panel/90 px-2 py-1 shadow-sm backdrop-blur">
      <B label={t('Tiêu đề 1')} active={editor.isActive('heading', { level: 1 })} on={() => c().toggleHeading({ level: 1 }).run()}><Heading1 className="size-4" /></B>
      <B label={t('Tiêu đề 2')} active={editor.isActive('heading', { level: 2 })} on={() => c().toggleHeading({ level: 2 }).run()}><Heading2 className="size-4" /></B>
      <B label={t('Tiêu đề 3')} active={editor.isActive('heading', { level: 3 })} on={() => c().toggleHeading({ level: 3 }).run()}><Heading3 className="size-4" /></B>
      <span className="mx-1 h-4 w-px bg-line" />
      <B label={t('Đậm')} active={editor.isActive('bold')} on={() => c().toggleBold().run()}><Bold className="size-4" /></B>
      <B label={t('Nghiêng')} active={editor.isActive('italic')} on={() => c().toggleItalic().run()}><Italic className="size-4" /></B>
      <B label={t('Mã')} active={editor.isActive('code')} on={() => c().toggleCode().run()}><Code className="size-4" /></B>
      <span className="mx-1 h-4 w-px bg-line" />
      <B label={t('Danh sách')} active={editor.isActive('bulletList')} on={() => c().toggleBulletList().run()}><List className="size-4" /></B>
      <B label={t('Danh sách số')} active={editor.isActive('orderedList')} on={() => c().toggleOrderedList().run()}><ListOrdered className="size-4" /></B>
      <B label={t('Danh sách việc cần làm')} active={editor.isActive('taskList')} on={() => c().toggleTaskList().run()}><ListChecks className="size-4" /></B>
      <B label={t('Trích dẫn')} active={editor.isActive('blockquote')} on={() => c().toggleBlockquote().run()}><Quote className="size-4" /></B>
      <B label={t('Bảng')} on={() => c().insertTable({ rows: 3, cols: 3, withHeaderRow: true }).run()}><TableIcon className="size-4" /></B>
      <B label={t('Đường kẻ')} on={() => c().setHorizontalRule().run()}><Minus className="size-4" /></B>
      <span className="mx-1 h-4 w-px bg-line" />
      <button type="button" title={t('Chèn trang con tại con trỏ')} onMouseDown={(e) => e.preventDefault()} onClick={onSubpage} className="flex h-7 items-center gap-1.5 rounded px-2 text-xs font-medium text-muted hover:bg-panel2 hover:text-fg"><FilePlus className="size-4" />{t('Trang con')}</button>
    </div>
  )
}

const store = {
  get: (k: string) => { try { return localStorage.getItem(k) } catch { return null } },
  set: (k: string, v: string) => { try { localStorage.setItem(k, v) } catch { /* che do rieng tu */ } },
  del: (k: string) => { try { localStorage.removeItem(k) } catch { /* che do rieng tu */ } },
}

function ancestors(pages: PageInfo[], id: string): PageInfo[] {
  const out: PageInfo[] = []
  let cur = pages.find((p) => p.id === id)
  while (cur?.parent && out.length < 20) { cur = pages.find((p) => p.id === cur!.parent); if (cur) out.unshift(cur) }
  return out
}

/** Mot trang dang mo: tieu de + trinh soan thao khoi; tu luu sau khi ngung go. Remount khi doi trang (key = id). */
function PageEditor({ page, pages, onSaved, onOpen, chatOpen, onToggleChat }: {
  page: PageFull; pages: PageInfo[]; onSaved: () => void; onOpen: (id: string) => void; chatOpen: boolean; onToggleChat: () => void
}) {
  const toast = useToast()
  const [title, setTitle] = useState(page.title)
  const [icon, setIcon] = useState(page.icon)
  const [state, setState] = useState<'saved' | 'saving' | 'error'>('saved')
  const pending = useRef<{ title?: string; icon?: string; content?: string }>({})
  const timer = useRef<ReturnType<typeof setTimeout> | undefined>(undefined)
  const alive = useRef(true)
  const [md, setMd] = useState(page.content)
  const lastMd = useRef(page.content)
  const openRef = useRef(onOpen)
  openRef.current = onOpen  // ban markdown gan nhat da biet (tu server hoac tu minh), de bo qua onUpdate khong doi gi

  const flush = async () => {
    clearTimeout(timer.current)
    const body = pending.current
    if (!Object.keys(body).length) return
    pending.current = {}
    if (alive.current) setState('saving')
    try {
      await api.put(`/api/pages/${page.id}`, body)
      if (alive.current) setState(Object.keys(pending.current).length ? 'saving' : 'saved')
      onSaved()
    } catch (e) {
      pending.current = { ...body, ...pending.current }
      if (alive.current) { setState('error'); toast(errMsg(e), 'bad') }
    }
  }
  const queue = (patch: { title?: string; icon?: string; content?: string }) => {
    pending.current = { ...pending.current, ...patch }
    setState('saving')
    clearTimeout(timer.current)
    timer.current = setTimeout(() => void flush(), SAVE_DELAY)
  }

  const editor = useEditor({
    extensions: [
      StarterKit.configure({ link: { openOnClick: false } }),
      Placeholder.configure({ placeholder: t('Viết gì đó, hoặc dùng thanh công cụ phía trên…') }),
      TaskList, TaskItem.configure({ nested: true }),
      Table, TableRow, TableHeader, TableCell,
      Markdown.configure({ html: false, tightLists: true, linkify: true, breaks: false }),
    ],
    content: page.content,
    editorProps: {
      handleClick: (_view, _pos, ev) => {  // bam vao link trang con (/pages/<ma>) thi mo trang do
        const href = (ev.target as HTMLElement).closest('a')?.getAttribute('href') ?? ''
        const m = /^\/pages\/([a-f0-9]{10})$/.exec(href)
        if (!m) return false
        ev.preventDefault()
        openRef.current(m[1])
        return true
      },
    },
    onUpdate: ({ editor: ed }) => {
      const cur = (ed.storage as unknown as { markdown: { getMarkdown: () => string } }).markdown.getMarkdown()
      if (cur === lastMd.current) return
      lastMd.current = cur
      setMd(cur)
      queue({ content: cur })
    },
  })

  // agent (hoac noi khac) vua sua trang: nap lai noi dung neu nguoi dung khong co ban sua dang cho luu
  useEffect(() => {
    if (!editor || Object.keys(pending.current).length) return
    if (page.content !== lastMd.current) {
      lastMd.current = page.content
      setMd(page.content)
      editor.commands.setContent(page.content, { emitUpdate: false })
    }
    setTitle((cur) => (cur === page.title ? cur : page.title))
    setIcon((cur) => (cur === page.icon ? cur : page.icon))
  }, [page.updated, page.content, page.title, page.icon, editor])

  useEffect(() => {
    alive.current = true
    return () => { alive.current = false; void flush() }  // luu not phan dang cho khi chuyen trang
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const addSubpage = async () => {
    if (!editor) return
    try {
      const c = await api.post<PageFull>('/api/pages', { parent: page.id })
      editor.chain().focus().insertContent([{ type: 'text', text: c.title, marks: [{ type: 'link', attrs: { href: `/pages/${c.id}` } }] }, { type: 'text', text: ' ' }]).run()
      await flush()
      onSaved()
      onOpen(c.id)
    } catch (e) { toast(errMsg(e), 'bad') }
  }

  const trail = ancestors(pages, page.id)
  const loose = pages.filter((p) => p.parent === page.id && !md.includes(`/pages/${p.id}`))  // trang con chua duoc chen link trong noi dung

  return (
    <div className="mx-auto w-full max-w-3xl px-8 pb-24 pt-6">
      <div className="mb-3 flex items-center justify-between gap-3 text-xs text-muted">
        <nav aria-label={t('Đường dẫn')} className="flex min-w-0 flex-wrap items-center gap-1">
          {trail.map((a) => (
            <span key={a.id} className="flex items-center gap-1">
              <button type="button" onClick={() => onOpen(a.id)} className="max-w-40 truncate hover:text-fg hover:underline">{a.icon} {a.title}</button><ChevronRight className="size-3" />
            </span>
          ))}
          <span className="max-w-48 truncate text-fg">{title || t('Chưa đặt tên')}</span>
        </nav>
        <div className="flex shrink-0 items-center gap-3">
          <span>{state === 'saving' ? t('Đang lưu…') : state === 'error' ? <button type="button" className="text-bad underline" onClick={() => void flush()}>{t('Lưu lỗi, bấm để thử lại')}</button> : t('Đã lưu')}</span>
          <Button size="sm" variant={chatOpen ? 'primary' : 'secondary'} onClick={onToggleChat}><Sparkles className="size-3.5" />{t('Hỏi AI')}</Button>
        </div>
      </div>
      <div className="mb-3 flex items-center gap-2">
        <input value={icon} onChange={(e) => { setIcon(e.target.value); queue({ icon: e.target.value }) }} maxLength={2} placeholder="📄" aria-label={t('Biểu tượng')}
          className="size-11 shrink-0 rounded-lg border border-transparent bg-transparent text-center text-2xl hover:border-line focus:border-accent focus:outline-none" />
        <input value={title} onChange={(e) => { setTitle(e.target.value); queue({ title: e.target.value }) }} placeholder={t('Chưa đặt tên')} aria-label={t('Tiêu đề trang')}
          className="min-w-0 flex-1 bg-transparent text-4xl font-bold tracking-tight placeholder:text-muted/40 focus:outline-none" />
      </div>
      {loose.length > 0 && (
        <div className="mb-4 flex flex-wrap items-center gap-1.5">
          <span className="text-xs text-muted">{t('Trang con')}:</span>
          {loose.map((c) => (
            <button key={c.id} type="button" onClick={() => onOpen(c.id)} className="flex items-center gap-1.5 rounded-full border border-line bg-panel px-2.5 py-1 text-xs hover:border-accent/60">
              {c.icon ? <span>{c.icon}</span> : <FileText className="size-3.5 text-muted" />}<span className="max-w-40 truncate">{c.title}</span>
            </button>
          ))}
        </div>
      )}
      {editor && <Toolbar editor={editor} onSubpage={() => void addSubpage()} />}
      <EditorContent editor={editor} className="page-editor" />
    </div>
  )
}

const CHAT_IDEAS = [tk('Tóm tắt trang này'), tk('Viết tiếp phần còn thiếu'), tk('Sửa lỗi chính tả và làm gọn câu chữ'), tk('Tạo các trang con cho từng mục chính')]

/** Chat voi agent ben phai trang: agent biet trang dang mo, doc/sua/tao trang con bang tool page_*. Moi trang giu mot hoi thoai rieng. */
function PageChat({ page, onClose }: { page: PageFull; onClose: () => void }) {
  const qc = useQueryClient()
  const chat = useChat()
  const cfg = useConfig()
  const [text, setText] = useState('')
  const [provider, setProvider] = useState<string | null>(() => store.get('pages-chat-provider'))
  const key = `page-chat-${page.id}`
  const scroller = useRef<HTMLDivElement>(null)
  const stick = useRef(true)

  useEffect(() => {
    const sid = store.get(key)
    if (sid) chat.open(sid).catch(() => store.del(key))
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [key])
  useEffect(() => { if (chat.sessionId) store.set(key, chat.sessionId) }, [chat.sessionId, key])
  useEffect(() => {  // agent vua chay xong hoac vua ghi file: nap lai cay trang va trang dang mo
    if (!chat.filesTick) return
    void qc.invalidateQueries({ queryKey: ['pages'] })
    void qc.invalidateQueries({ queryKey: ['page', page.id] })
  }, [chat.filesTick, qc, page.id])
  useEffect(() => { const el = scroller.current; if (el && stick.current) el.scrollTop = el.scrollHeight }, [chat.items, chat.status])

  const provs = cfg.data?.config.providers ?? {}
  const active = provider && provs[provider] ? provider : (cfg.data?.config.default_provider ?? null)
  const pickProvider = (id: string) => { setProvider(id); store.set('pages-chat-provider', id) }
  const submit = (v: string) => {
    if (!v.trim() || chat.busy) return
    setText('')
    stick.current = true
    void chat.send(v, active, [], { context: `page:${page.id}` })
  }

  return (
    <SessionContext.Provider value={chat.sessionId}>
      <aside className="flex w-[26rem] shrink-0 flex-col border-l border-line bg-panel/60">
        <div className="flex h-11 shrink-0 items-center justify-between border-b border-line px-3 text-sm font-semibold">
          <span className="flex items-center gap-2"><Sparkles className="size-4 text-accent" />{t('Hỏi AI về trang này')}{chat.busy && <LoaderCircle className="size-3.5 animate-spin text-accent" />}</span>
          <button type="button" aria-label={t('Đóng')} onClick={onClose} className="grid size-7 place-items-center rounded text-muted hover:bg-panel2 hover:text-fg"><X className="size-4" /></button>
        </div>
        <div ref={scroller} onScroll={(e) => { const el = e.currentTarget; stick.current = el.scrollHeight - el.scrollTop - el.clientHeight < 80 }} className="min-h-0 flex-1 overflow-y-auto">
          <div className="space-y-4 px-3 py-4">
            {chat.items.length === 0 ? (
              <div className="pt-4 text-center">
                <p className="text-sm text-muted">{t('Nhờ agent đọc, viết hoặc tổ chức trang này.')}</p>
                <div className="mt-4 grid gap-2">{CHAT_IDEAS.map((i) => <button key={i} type="button" onClick={() => submit(t(i))} className="rounded-lg border border-line bg-bg px-3 py-2 text-left text-[13px] text-muted transition hover:border-accent/60 hover:text-fg">{t(i)}</button>)}</div>
              </div>
            ) : chat.items.map((it) => (
              <MessageView key={it.key} item={it} sid={chat.sessionId ?? undefined} onDecide={(aid, ok) => void chat.decide(aid, ok)} onAnswer={(q, a) => void chat.answer(q, a)} onUndo={() => void chat.undo()} onOpenFile={() => undefined} canAct={!chat.busy} />
            ))}
            {chat.busy && chat.status && <p className="flex items-center gap-2 text-xs text-muted" role="status"><LoaderCircle className="size-3.5 animate-spin text-accent" />{chat.status}</p>}
          </div>
        </div>
        <form className="border-t border-line p-3" onSubmit={(e) => { e.preventDefault(); submit(text) }}>
          <div className="rounded-xl border border-line bg-bg focus-within:border-accent">
            <textarea value={text} onChange={(e) => setText(e.target.value)} rows={2} placeholder={t('Nhắn cho agent… (Enter để gửi)')} aria-label={t('Nhắn cho agent')}
              onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey && !e.nativeEvent.isComposing) { e.preventDefault(); submit(text) } }}
              className="block min-h-12 w-full resize-none bg-transparent px-3 pt-2.5 text-sm focus:outline-none" />
            <div className="flex items-center justify-between gap-2 px-2 pb-2">
              <select value={active ?? ''} onChange={(e) => pickProvider(e.target.value)} aria-label={t('Chọn model')} title={t('Chọn model')}
                className="min-w-0 max-w-[14rem] truncate rounded-md border border-transparent bg-transparent px-1.5 py-1 text-xs text-muted hover:border-line hover:text-fg focus:outline-none">
                {Object.entries(provs).map(([id, c]) => <option key={id} value={id}>{id}{c.model ? ` · ${c.model}` : ''}</option>)}
              </select>
              {chat.busy
                ? <Button type="button" size="sm" onClick={chat.stop} aria-label={t('Dừng')}><Square className="size-3.5" /></Button>
                : <Button type="submit" size="sm" variant="primary" disabled={!text.trim()} aria-label={t('Gửi')}><Send className="size-3.5" /></Button>}
            </div>
          </div>
        </form>
      </aside>
    </SessionContext.Provider>
  )
}

export function PagesPage() {
  const { id } = useParams()
  const nav = useNavigate()
  const qc = useQueryClient()
  const toast = useToast()
  const [open, setOpen] = useState<Set<string>>(new Set())
  const [q, setQ] = useState('')
  const [chatOpen, setChatOpen] = useState(() => store.get('pages-chat') !== '0')
  const toggleChat = () => setChatOpen((v) => { store.set('pages-chat', v ? '0' : '1'); return !v })
  const list = useQuery({ queryKey: ['pages'], queryFn: () => api.get<PageInfo[]>('/api/pages') })
  const page = useQuery({ queryKey: ['page', id], queryFn: () => api.get<PageFull>(`/api/pages/${id}`), enabled: !!id, staleTime: Infinity, gcTime: 0, retry: false })
  const found = useQuery({ queryKey: ['pages-search', q], queryFn: () => api.get<(PageInfo & { snippet: string })[]>(`/api/pages/search?q=${encodeURIComponent(q)}`), enabled: q.trim().length >= 2 })

  const create = useMutation({
    mutationFn: (parent: string) => api.post<PageFull>('/api/pages', { parent }),
    onSuccess: (p) => { void qc.invalidateQueries({ queryKey: ['pages'] }); if (p.parent) setOpen((s) => new Set(s).add(p.parent)); nav(`/pages/${p.id}`) },
    onError: (e) => toast(errMsg(e), 'bad'),
  })
  const remove = useMutation({
    mutationFn: (p: PageInfo) => api.del(`/api/pages/${p.id}`),
    onSuccess: (_r, p) => { void qc.invalidateQueries({ queryKey: ['pages'] }); if (id === p.id) nav('/pages') },
    onError: (e) => toast(errMsg(e), 'bad'),
  })
  const askDelete = (p: PageInfo) => {
    const kids = (list.data ?? []).some((c) => c.parent === p.id)
    if (confirm(kids ? t('Xóa trang "{name}" và mọi trang con của nó?', { name: p.title }) : t('Xóa trang "{name}"?', { name: p.title }))) remove.mutate(p)
  }
  const toggle = (pid: string) => setOpen((s) => { const n = new Set(s); if (n.has(pid)) n.delete(pid); else n.add(pid); return n })
  const pages = useMemo(() => list.data ?? [], [list.data])
  const current = id

  return (
    <div className="flex h-full min-h-0">
      <aside className="flex w-72 shrink-0 flex-col border-r border-line bg-panel/60">
        <div className="flex items-center justify-between px-4 pb-1 pt-4">
          <h2 className="text-sm font-semibold tracking-tight">{t('Trang')}<span className="ml-2 text-xs font-normal text-muted">{pages.length}</span></h2>
          <Button size="sm" variant="primary" onClick={() => create.mutate('')} disabled={create.isPending}><Plus className="size-3.5" />{t('Trang mới')}</Button>
        </div>
        <div className="p-3 pt-2">
          <input value={q} onChange={(e) => setQ(e.target.value)} placeholder={t('Tìm trang…')} aria-label={t('Tìm trang')} className="w-full rounded-lg border border-line bg-bg px-3 py-1.5 text-sm focus:border-accent focus:outline-none" />
        </div>
        <div className="min-h-0 flex-1 overflow-y-auto px-2 pb-3">
          {list.isLoading && <Loading />}
          {list.error && <ErrorNote error={list.error} />}
          {q.trim().length >= 2
            ? (found.data ?? []).map((p) => (
                <button key={p.id} type="button" onClick={() => { nav(`/pages/${p.id}`); setQ('') }} className="block w-full rounded-md px-2 py-1.5 text-left hover:bg-panel2">
                  <span className="block truncate text-sm">{p.icon} {p.title}</span><span className="block truncate text-xs text-muted">{p.snippet}</span>
                </button>))
            : <Tree pages={pages} parent="" depth={0} current={current} open={open} toggle={toggle} onAdd={(p) => create.mutate(p)} onDelete={askDelete} onOpen={(pid) => nav(`/pages/${pid}`)} />}
          {!list.isLoading && !pages.length && <p className="px-2 py-4 text-sm text-muted">{t('Chưa có trang nào. Bấm nút bên trên để tạo trang đầu tiên, hoặc nhờ agent tạo giúp.')}</p>}
        </div>
      </aside>
      <main className="min-w-0 flex-1 overflow-y-auto">
        {!id && <div className="grid h-full place-items-center p-8 text-center"><div className="max-w-sm"><div className="mx-auto mb-4 grid size-14 place-items-center rounded-2xl bg-panel2 text-muted"><FileText className="size-7" /></div><p className="font-medium">{t('Chọn một trang ở bên trái hoặc tạo trang mới.')}</p><p className="mt-1 text-sm text-muted">{t('Viết ghi chú, tài liệu, kế hoạch; trang con lồng bên trong và agent đọc, viết giúp bạn.')}</p><Button className="mt-5" variant="primary" onClick={() => create.mutate('')}><Plus className="size-4" />{t('Tạo trang đầu tiên')}</Button></div></div>}
        {id && page.isLoading && <Loading />}
        {id && page.error && <div className="p-6"><ErrorNote error={page.error} /></div>}
        {id && page.data && <PageEditor key={page.data.id} page={page.data} pages={pages} onSaved={() => void qc.invalidateQueries({ queryKey: ['pages'] })} onOpen={(pid) => nav(`/pages/${pid}`)} chatOpen={chatOpen} onToggleChat={toggleChat} />}
      </main>
      {id && page.data && chatOpen && <PageChat key={page.data.id} page={page.data} onClose={toggleChat} />}
    </div>
  )
}
