import { AttachmentMenu, AttachmentPreview } from '@/features/chat/Attachments'
import { useAttachments } from '@/features/chat/useAttachments'
import { useDialogs } from '@/components/ui/Dialogs'
import { useEffect, useRef, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { ArrowLeft, ArrowRight, BookOpen, Download, FilePenLine, ImagePlus, Upload, Bold, ListTree, Redo2, Undo2, ChevronRight, Code, FilePlus, LoaderCircle, Send, Sparkles, Square, X, FileText, Heading1, Heading2, Heading3, Italic, List, ListChecks, ListOrdered, Maximize2, Minimize2, Minus, MessageSquare, Plus, Quote, Table as TableIcon, Trash2, ChevronsDownUp } from 'lucide-react'
import { EditorContent, useEditor, type Editor, type JSONContent } from '@tiptap/react'
import Image from '@tiptap/extension-image'
import StarterKit from '@tiptap/starter-kit'
import Placeholder from '@tiptap/extension-placeholder'
import { TaskItem, TaskList } from '@tiptap/extension-list'
import { Table, TableCell, TableHeader, TableRow } from '@tiptap/extension-table'
import { CodeBlockLowlight } from '@tiptap/extension-code-block-lowlight'
import { createLowlight, common } from 'lowlight'
import { Button } from '@/components/ui/Button'
import { Field, Input } from '@/components/ui/Form'
import { EmptyState, ErrorNote, Loading, Page, PageHeader } from '@/components/ui/misc'
import { Modal } from '@/components/ui/Modal'
import { SearchBox } from '@/components/ui/SearchBox'
import { useToast } from '@/components/ui/Toast'
import { api } from '@/lib/api'
import { useConfig } from '@/lib/queries'
import { t, tk } from '@/lib/i18n.ts'
import { cn, errMsg, fmtDateTime } from '@/lib/utils'
import { MessageView } from '@/features/chat/MessageView'
import { SessionContext } from '@/features/chat/session'
import { useChat } from '@/features/chat/useChat'
import { Toggle } from './extensions/toggle'
import { Callout } from './extensions/callout'
import { PageLink } from './extensions/pageLink'
import { SlashCommand, type SlashItem } from './extensions/slashCommand'

const lowlight = createLowlight(common)

const EMPTY_DOC: JSONContent = { type: 'doc', content: [{ type: 'paragraph' }] }

interface PageInfo { id: string; title: string; parent: string; icon: string; order: number; updated: number; fullWidth: boolean }
interface PageFull extends PageInfo { content: JSONContent }

function PageIcon({ icon }: { icon: string }) {
  return icon.startsWith('/api/pages/assets/') ? <img src={icon} alt="" className="inline-block size-5 shrink-0 rounded object-cover" /> : <span className="shrink-0">{icon}</span>
}

const SAVE_DELAY = 800

function B({ on, active, disabled, label, children }: { on: () => void; active?: boolean; disabled?: boolean; label: string; children: React.ReactNode }) {
  return (
    <button type="button" title={label} aria-label={label} disabled={disabled} aria-pressed={active} onMouseDown={(e) => e.preventDefault()} onClick={on}
      className={cn('grid size-7 place-items-center rounded hover:bg-panel2 disabled:opacity-35', active ? 'bg-panel2 text-accent' : 'text-muted')}>{children}</button>
  )
}

function insertToggle(editor: Editor) {
  editor.chain().focus().insertContent({ type: 'toggle', attrs: { open: true }, content: [{ type: 'paragraph' }, { type: 'paragraph' }] }).run()
}
function insertCallout(editor: Editor) {
  editor.chain().focus().insertContent({ type: 'callout', attrs: { icon: '💡', color: 'gray' }, content: [{ type: 'paragraph' }] }).run()
}

function Toolbar({ editor, onSubpage, onImage }: { editor: Editor; onSubpage: () => void; onImage: () => void }) {
  const c = () => editor.chain().focus()
  return (
    <div className="sticky top-0 z-10 mb-4 flex flex-wrap items-center gap-0.5 rounded-xl border border-line bg-panel/90 px-2 py-1 shadow-sm backdrop-blur">
      <B label={t('Hoàn tác')} disabled={!editor.can().undo()} on={() => c().undo().run()}><Undo2 className="size-4" /></B>
      <B label={t('Làm lại')} disabled={!editor.can().redo()} on={() => c().redo().run()}><Redo2 className="size-4" /></B>
      <span className="mx-1 h-4 w-px bg-line" />
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
      <B label={t('Khối gập')} active={editor.isActive('toggle')} on={() => insertToggle(editor)}><ChevronsDownUp className="size-4" /></B>
      <B label={t('Khối ghi chú nổi bật')} active={editor.isActive('callout')} on={() => insertCallout(editor)}><MessageSquare className="size-4" /></B>
      <B label={t('Khối mã')} active={editor.isActive('codeBlock')} on={() => c().toggleCodeBlock().run()}><Code className="size-4" /></B>
      <B label={t('Chèn ảnh')} on={onImage}><ImagePlus className="size-4" /></B>
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

function useMediaQuery(q: string) {
  const [m, setM] = useState(() => window.matchMedia(q).matches)
  useEffect(() => {
    const mq = window.matchMedia(q)
    const on = () => setM(mq.matches)
    mq.addEventListener('change', on)
    return () => mq.removeEventListener('change', on)
  }, [q])
  return m
}

function loadNotebookChat(pageId: string, notebookId: string, create = false) {
  const previous = [...new Set([notebookId, pageId])].flatMap((id) =>
    [store.get(`page-chat-${id}-draft`), store.get(`page-chat-${id}`)].filter((sid): sid is string => !!sid))
  return api.post<{ id: string | null }>(`/api/pages/${pageId}/chat`, { create, previous })
}

function ancestors(pages: PageInfo[], id: string): PageInfo[] {
  const out: PageInfo[] = []
  let cur = pages.find((p) => p.id === id)
  while (cur?.parent && out.length < 20) { cur = pages.find((p) => p.id === cur!.parent); if (cur) out.unshift(cur) }
  return out
}

/** Mot trang dang mo: tieu de + trinh soan thao khoi; tu luu sau khi ngung go. Remount khi doi trang (key = id). */
function PageEditor({ page, pages, onSaved, onOpen, chatOpen, onToggleChat, onDelete }: {
  page: PageFull; pages: PageInfo[]; onSaved: () => void; onOpen: (id: string) => void; chatOpen: boolean; onToggleChat: () => void; onDelete: (title: string) => void
}) {
  const toast = useToast()
  const { askText } = useDialogs()
  const imageInput = useRef<HTMLInputElement>(null)
  const logoInput = useRef<HTMLInputElement>(null)
  const [uploading, setUploading] = useState(false)
  const [title, setTitle] = useState(page.title)
  const [icon, setIcon] = useState(page.icon)
  const [fullWidth, setFullWidth] = useState(page.fullWidth)
  const [chatWidth, setChatWidth] = useState(() => Number(store.get('pages-chat-width') || '420'))
  useEffect(() => { store.set('pages-chat-width', String(chatWidth)) }, [chatWidth])
  const [state, setState] = useState<'saved' | 'saving' | 'error'>('saved')
  const saving = useRef<Promise<boolean> | null>(null)
  const [draft, setDraft] = useState(false)
  const [subpagePosition, setSubpagePosition] = useState<number | null>(null)
  const [subpageTitle, setSubpageTitle] = useState('')
  const [creatingSubpage, setCreatingSubpage] = useState(false)
  const pending = useRef<{ title?: string; icon?: string; content?: JSONContent; fullWidth?: boolean }>({})
  const timer = useRef<ReturnType<typeof setTimeout> | undefined>(undefined)
  const alive = useRef(true)
  const lastContent = useRef(page.content)
  const openRef = useRef(onOpen)
  openRef.current = onOpen  // ban noi dung gan nhat da biet (tu server hoac tu minh), de bo qua onUpdate khong doi gi
  const pagesRef = useRef(pages)
  pagesRef.current = pages

  const flush = async (): Promise<boolean> => {
    clearTimeout(timer.current)
    if (saving.current) return await saving.current && await flush()
    const body = pending.current
    if (!Object.keys(body).length) return true
    pending.current = {}
    if (alive.current) setState('saving')
    saving.current = api.put(`/api/pages/${page.id}`, body).then(() => {
      if (alive.current) setState(Object.keys(pending.current).length ? 'saving' : 'saved')
      onSaved()
      return true
    }).catch((error) => {
      pending.current = { ...body, ...pending.current }
      if (alive.current) { setState('error'); toast(errMsg(error), 'bad') }
      return false
    }).finally(() => { saving.current = null })
    return await saving.current && (!Object.keys(pending.current).length || await flush())
  }
  const queue = (patch: { title?: string; icon?: string; content?: JSONContent; fullWidth?: boolean }) => {
    pending.current = { ...pending.current, ...patch }
    setState('saving')
    clearTimeout(timer.current)
    timer.current = setTimeout(() => void flush(), SAVE_DELAY)
  }

  const slashItems = (query: string): SlashItem[] => {
    const items: SlashItem[] = [
      { key: 'h1', label: t('Tiêu đề 1'), hint: 'h1', run: (ed) => ed.chain().focus().toggleHeading({ level: 1 }).run() },
      { key: 'h2', label: t('Tiêu đề 2'), hint: 'h2', run: (ed) => ed.chain().focus().toggleHeading({ level: 2 }).run() },
      { key: 'h3', label: t('Tiêu đề 3'), hint: 'h3', run: (ed) => ed.chain().focus().toggleHeading({ level: 3 }).run() },
      { key: 'bullet', label: t('Danh sách'), run: (ed) => ed.chain().focus().toggleBulletList().run() },
      { key: 'ordered', label: t('Danh sách số'), run: (ed) => ed.chain().focus().toggleOrderedList().run() },
      { key: 'task', label: t('Danh sách việc cần làm'), run: (ed) => ed.chain().focus().toggleTaskList().run() },
      { key: 'toggle', label: t('Khối gập'), run: (ed) => insertToggle(ed) },
      { key: 'callout', label: t('Khối ghi chú nổi bật'), run: (ed) => insertCallout(ed) },
      { key: 'code', label: t('Khối mã'), run: (ed) => ed.chain().focus().toggleCodeBlock().run() },
      { key: 'quote', label: t('Trích dẫn'), run: (ed) => ed.chain().focus().toggleBlockquote().run() },
      { key: 'table', label: t('Bảng'), run: (ed) => ed.chain().focus().insertTable({ rows: 3, cols: 3, withHeaderRow: true }).run() },
      { key: 'divider', label: t('Đường kẻ'), run: (ed) => ed.chain().focus().setHorizontalRule().run() },
      { key: 'subpage', label: t('Trang con'), run: (ed) => { setSubpageTitle(''); setSubpagePosition(ed.state.selection.to) } },
    ]
    const q = query.trim().toLowerCase()
    return q ? items.filter((i) => i.label.toLowerCase().includes(q) || i.key.includes(q)) : items
  }

  const editor = useEditor({
    shouldRerenderOnTransaction: true,
    extensions: [
      StarterKit.configure({ link: { openOnClick: false }, codeBlock: false }),
      Placeholder.configure({ placeholder: t('Viết gì đó, hoặc gõ "/" để chèn khối…') }),
      Image,
      TaskList, TaskItem.configure({ nested: true }),
      Table, TableRow, TableHeader, TableCell,
      CodeBlockLowlight.configure({ lowlight }),
      Toggle,
      Callout.configure({ editIcon: (current) => askText(t('Đổi biểu tượng'), t('Emoji cho khối này:'), current) }),
      PageLink.configure({
        onOpen: (pageId: string) => openRef.current(pageId),
        resolveTitle: (pageId: string) => pagesRef.current.find((p) => p.id === pageId)?.title,
      }),
      SlashCommand.configure({ items: slashItems }),
    ],
    content: page.content,
    editorProps: {
      attributes: { 'aria-label': t('Nội dung ghi chú') },
      handlePaste: (_view, event) => {
        const images = Array.from(event.clipboardData?.files ?? []).filter((f) => f.type.startsWith('image/'))
        if (!images.length) return false
        event.preventDefault()
        void insertImages(images)
        return true
      },
      handleDrop: (view, event, _slice, moved) => {
        const images = Array.from(event.dataTransfer?.files ?? []).filter((f) => f.type.startsWith('image/'))
        if (moved || !images.length) return false
        event.preventDefault()
        const pos = view.posAtCoords({ left: event.clientX, top: event.clientY })
        if (pos) editor?.commands.setTextSelection(pos.pos)
        void insertImages(images)
        return true
      },
    },
    onUpdate: ({ editor: ed }) => {
      const cur = ed.getJSON()
      lastContent.current = cur
      queue({ content: cur })
    },
  })

  const uploadImage = async (file: File) => {
    if (file.size > 10 * 1024 * 1024) throw new Error(t('Ảnh vượt quá 10 MB'))
    const data = await new Promise<string>((resolve, reject) => {
      const reader = new FileReader()
      reader.onload = () => resolve(String(reader.result).split(',')[1])
      reader.onerror = () => reject(new Error(t('Không đọc được ảnh')))
      reader.readAsDataURL(file)
    })
    return (await api.post<{ url: string }>('/api/pages/assets', { data })).url
  }
  const insertImages = async (files: File[]) => {
    setUploading(true)
    try {
      for (const file of files) {
        const url = await uploadImage(file)
        if (alive.current) editor?.chain().focus().setImage({ src: url, alt: file.name }).run()
      }
    } catch (e) { toast(errMsg(e), 'bad') }
    finally { if (alive.current) setUploading(false) }
  }
  const uploadLogo = async (file: File) => {
    setUploading(true)
    try {
      const url = await uploadImage(file)
      if (alive.current) { setIcon(url); queue({ icon: url }) }
    } catch (e) { toast(errMsg(e), 'bad') }
    finally { if (alive.current) setUploading(false) }
  }

  // agent (hoac noi khac) vua sua trang: nap lai noi dung neu nguoi dung khong co ban sua dang cho luu
  useEffect(() => {
    if (!editor || saving.current || Object.keys(pending.current).length) return
    if (JSON.stringify(page.content) !== JSON.stringify(lastContent.current)) {
      lastContent.current = page.content
      editor.commands.setContent(page.content ?? EMPTY_DOC, { emitUpdate: false })
    }
    setTitle((cur) => (cur === page.title ? cur : page.title))
    setIcon((cur) => (cur === page.icon ? cur : page.icon))
    setFullWidth((cur) => (cur === page.fullWidth ? cur : page.fullWidth))
  }, [page.updated, page.content, page.title, page.icon, page.fullWidth, editor])

  useEffect(() => {
    alive.current = true
    return () => { alive.current = false; void flush() }  // luu not phan dang cho khi chuyen trang
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const insertSubpage = (child: PageInfo, position: number) => {
    if (!editor || editor.isDestroyed) return
    const pos = Math.min(position, editor.state.doc.content.size)
    const resolved = editor.state.doc.resolve(pos)
    const link = { type: 'pageLink', attrs: { pageId: child.id, title: child.title } }
    const inCode = resolved.parent.type.name === 'codeBlock'
    const insertAt = inCode ? resolved.after() : pos
    const inserted = editor.commands.insertContentAt(insertAt, link)
    if (inserted) {
      setSubpagePosition(null)
      editor.commands.focus()
    }
  }

  const addSubpage = async (position: number) => {
    if (creatingSubpage) return
    setCreatingSubpage(true)
    try {
      const child = await api.post<PageFull>('/api/pages', { parent: page.id, title: subpageTitle.trim() })
      onSaved()
      if (alive.current) insertSubpage(child, position)
    } catch (e) { toast(errMsg(e), 'bad') }
    finally { if (alive.current) setCreatingSubpage(false) }
  }

  const trail = ancestors(pages, page.id)
  const children = pages.filter((p) => p.parent === page.id)

  const headings: { pos: number; level: number; text: string }[] = []
  editor?.state.doc.descendants((node, pos) => {
    if (node.type.name === 'heading' && node.textContent.trim()) {
      headings.push({ pos, level: node.attrs.level, text: node.textContent })
    }
  })
  const jumpToHeading = (pos: number) => {
    const node = editor?.view.nodeDOM(pos)
    if (node instanceof HTMLElement) node.scrollIntoView({ block: 'start' })
    editor?.chain().focus(undefined, { scrollIntoView: false }).setTextSelection(pos + 1).run()
  }

  const [exporting, setExporting] = useState(false)
  const exportMarkdown = async () => {
    if (exporting) return
    setExporting(true)
    try {
      const { markdown } = await api.get<{ markdown: string }>(`/api/pages/${page.id}/export`)
      const name = title.trim().replace(/\s+/g, ' ') || t('Chưa đặt tên')
      const filename = name.normalize('NFC').replace(/[^\p{L}\p{N}\p{M} ._-]+/gu, '-').slice(0, 100).replace(/^[ .-]+|[ .-]+$/g, '')
      const heading = name.replace(/[\\*_#[\]<>]/g, '\\$&')
      const url = URL.createObjectURL(new Blob([`# ${heading}\n\n`, markdown, markdown.endsWith('\n') ? '' : '\n'], {
        type: 'text/markdown;charset=utf-8',
      }))
      const link = document.createElement('a')
      link.href = url
      link.download = `${filename || page.id}.md`
      document.body.append(link)
      link.click()
      link.remove()
      setTimeout(() => URL.revokeObjectURL(url), 1000)
    } catch (e) { toast(errMsg(e), 'bad') }
    finally { if (alive.current) setExporting(false) }
  }

  return (
    <>
      <div className="min-w-0 flex-1 overflow-y-auto">
        <div className={cn('mx-auto w-full px-4 pb-24 pt-5 sm:px-8', fullWidth ? 'max-w-none' : 'max-w-4xl')}>
          <div className="mb-6 flex flex-wrap items-center justify-between gap-3 border-b border-line pb-4 text-xs text-muted">
            <nav aria-label={t('Đường dẫn')} className="flex min-w-0 flex-wrap items-center gap-1">
              <Link to="/pages" className="inline-flex items-center gap-1.5 rounded-md px-1 py-1 font-medium hover:text-accent">
                <ArrowLeft className="size-3.5" />{t('Sổ tay')}
              </Link>
              {trail.length > 0 && <ChevronRight className="size-3 shrink-0" aria-hidden />}
              {trail.map((a) => (
                <span key={a.id} className="flex items-center gap-1">
                  <button type="button" onClick={() => onOpen(a.id)} className="max-w-40 truncate hover:text-fg hover:underline"><PageIcon icon={a.icon} /> {a.title}</button><ChevronRight className="size-3" />
                </span>
              ))}

            </nav>
            <div className="flex shrink-0 items-center gap-2 sm:gap-3">
              <span aria-live="polite">{state === 'saving' ? t('Đang lưu…') : state === 'error' ? <button type="button" className="text-bad underline" onClick={() => void flush()}>{t('Lưu lỗi, bấm để thử lại')}</button> : t('Đã lưu')}</span>
              <Button size="sm" variant="ghost" aria-label={fullWidth ? t('Xem dạng cơ bản (độ rộng vừa phải)') : t('Xem ghi chú theo chiều rộng tối đa')} title={fullWidth ? t('Thu hẹp lại độ rộng cơ bản') : t('Mở rộng toàn bộ chiều ngang màn hình')}
                onClick={() => { const next = !fullWidth; setFullWidth(next); queue({ fullWidth: next }) }}>
                {fullWidth ? <Minimize2 className="size-4" /> : <Maximize2 className="size-4" />}
              </Button>
              <Button size="sm" variant="ghost" aria-label={t('Xuất Markdown')} title={t('Tải file Markdown (.md)')} loading={exporting} onClick={() => void exportMarkdown()}>
                <Download className="size-4" /><span className="hidden sm:inline">{t('Xuất Markdown')}</span>
              </Button>
              <Button size="sm" variant="ghost" aria-label={t('Xóa ghi chú')} title={t('Xóa ghi chú')} disabled={state === 'saving'} onClick={() => onDelete(title)}><Trash2 className="size-4" /></Button>
              <Button size="sm" variant={chatOpen ? 'primary' : 'secondary'} onClick={onToggleChat} aria-pressed={chatOpen}><Sparkles className="size-3.5" />{t('Hỏi AI')}</Button>
            </div>
          </div>
          <div className="mb-3 flex items-center gap-2">
            {icon.startsWith('/api/pages/assets/') ? <button type="button" aria-label={t('Xóa logo')} onClick={() => { setIcon(''); queue({ icon: '' }) }}><img src={icon} alt="" className="size-11 rounded-lg object-cover" /></button> : <input value={icon} onChange={(e) => { setIcon(e.target.value); queue({ icon: e.target.value }) }} maxLength={32} placeholder="📄" aria-label={t('Biểu tượng')}
              className="size-11 shrink-0 rounded-lg border border-transparent bg-transparent text-center text-2xl hover:border-line focus:border-accent focus:outline-none" />}
            <button type="button" title={t('Tải logo')} aria-label={t('Tải logo')} disabled={uploading} onClick={() => logoInput.current?.click()} className="text-muted hover:text-fg"><Upload className="size-4" /></button>
            <input value={title} onChange={(e) => { setTitle(e.target.value); queue({ title: e.target.value }) }} placeholder={t('Chưa đặt tên')} aria-label={t('Tiêu đề ghi chú')}
              className="min-w-0 flex-1 bg-transparent text-2xl font-bold tracking-tight sm:text-4xl placeholder:text-muted/40 focus:outline-none" />
          </div>
          <input ref={imageInput} type="file" accept="image/png,image/jpeg,image/gif,image/webp" multiple hidden onChange={(e) => { void insertImages(Array.from(e.target.files ?? [])); e.target.value = '' }} />
          <input ref={logoInput} type="file" accept="image/png,image/jpeg,image/gif,image/webp" hidden onChange={(e) => { const f = e.target.files?.[0]; if (f) void uploadLogo(f); e.target.value = '' }} />
          {uploading && <p role="status" className="mb-2 text-sm text-muted">{t('Đang lưu ảnh…')}</p>}
          {editor && <Toolbar editor={editor} onSubpage={() => { setSubpageTitle(''); setSubpagePosition(editor.state.selection.to) }} onImage={() => imageInput.current?.click()} />}
          {!!headings.length && <details className="mb-4 rounded-xl border border-line bg-panel/60 px-3 py-2">
            <summary className="cursor-pointer select-none text-sm font-medium">
              <ListTree className="mx-1 inline size-4 text-accent" />{t('Mục lục')}
            </summary>
            <nav aria-label={t('Mục lục')} className="mt-2 space-y-0.5">
              {headings.map(({ pos, level, text }) => <button key={pos} type="button" onClick={() => jumpToHeading(pos)}
                className="block w-full truncate rounded-md py-1.5 pr-2 text-left text-sm text-muted hover:bg-panel2 hover:text-fg"
                style={{ paddingLeft: 10 + (level - 1) * 12 }}>{text}</button>)}
            </nav>
          </details>}
          <EditorContent editor={editor} className="page-editor [&_.ProseMirror]:min-h-60 [&_.ProseMirror_:is(h1,h2,h3,h4,h5,h6)]:scroll-mt-16" />
        </div>
      </div>
      {subpagePosition !== null && <Modal open title={t('Trang con')} onClose={() => { if (!creatingSubpage) setSubpagePosition(null) }}>
        <form onSubmit={(event) => { event.preventDefault(); void addSubpage(subpagePosition) }} className="space-y-3">
          <Field label={t('Tên trang con')}>
            <Input autoFocus value={subpageTitle} maxLength={200} disabled={creatingSubpage} onChange={(event) => setSubpageTitle(event.target.value)} placeholder={t('Chưa đặt tên')} />
          </Field>
          <Button type="submit" variant="primary" loading={creatingSubpage}><Plus className="size-4" />{t('Tạo và chèn')}</Button>
        </form>
        {children.length > 0 && <ul className="mt-5 divide-y divide-line border-t border-line">
          {children.map((child) => <li key={child.id} className="flex min-w-0 items-center gap-3 py-2">
            <Link to={`/pages/${child.id}`} title={child.title} className="flex min-w-0 flex-1 items-center gap-2 text-sm hover:text-accent">
              {child.icon ? <PageIcon icon={child.icon} /> : <FileText className="size-4 shrink-0 text-muted" />}
              <span className="truncate">{child.title}</span>
            </Link>
            <Button size="sm" disabled={creatingSubpage} aria-label={t('Chèn trang {name}', { name: child.title })}
              onClick={() => insertSubpage(child, subpagePosition)}>{t('Chèn')}</Button>
          </li>)}
        </ul>}
      </Modal>}
      {chatOpen && <PageChat page={{ ...page, title }} notebookId={trail[0]?.id ?? page.id} onClose={onToggleChat} draft={draft}
        onToggleDraft={() => setDraft((current) => !current)} beforeSend={flush} width={chatWidth} onWidth={setChatWidth}
        onInsert={(text) => {
          if (editor?.commands.insertContentAt(editor.state.doc.content.size, text.trim())) toast(t('Đã chèn vào ghi chú'))
        }} />}
    </>
  )
}

const CHAT_IDEAS = [
  { label: tk('Tóm tắt ghi chú này'), Icon: ListTree },
  { label: tk('Viết tiếp phần còn thiếu'), Icon: FilePenLine },
  { label: tk('Sửa lỗi chính tả và làm gọn câu chữ'), Icon: Italic },
]

/** Chat voi agent ben phai trang: agent biet trang dang mo, doc/sua/tao trang con bang tool page_*. Moi trang giu mot hoi thoai rieng. */
function PageChat({ page, notebookId, onClose, draft, onToggleDraft, beforeSend, onInsert, width, onWidth }: {
  page: PageFull; notebookId: string; onClose: () => void; draft: boolean; onToggleDraft: () => void
  beforeSend: () => Promise<boolean>; onInsert: (text: string) => void; width: number; onWidth: (w: number) => void
}) {
  const qc = useQueryClient()
  const chat = useChat()
  const cfg = useConfig()
  const [text, setText] = useState('')
  const [preparing, setPreparing] = useState(false)
  const [ready, setReady] = useState(false)
  const [loadError, setLoadError] = useState<unknown>(null)
  const [attempt, setAttempt] = useState(0)
  const drag = useRef(false)
  const wide = useMediaQuery('(min-width: 1280px)')
  const [provider, setProvider] = useState<string | null>(() => store.get('pages-chat-provider'))
  const openChat = chat.open
  const scroller = useRef<HTMLDivElement>(null)
  const mounted = useRef(false)
  const stick = useRef(true)

  useEffect(() => {
    mounted.current = true
    let cancelled = false
    void loadNotebookChat(page.id, notebookId).then(async ({ id }) => {
      if (cancelled) return
      if (id) await openChat(id)
      if (!cancelled) setReady(true)
    }).catch((error: unknown) => { if (!cancelled) setLoadError(error) })
    return () => { cancelled = true; mounted.current = false }
  }, [page.id, notebookId, openChat, attempt])
  useEffect(() => {  // agent vua chay xong hoac vua ghi file: nap lai cay trang va trang dang mo
    if (!chat.filesTick) return
    void qc.invalidateQueries({ queryKey: ['pages'] })
    void qc.invalidateQueries({ queryKey: ['page', page.id] })
  }, [chat.filesTick, qc, page.id])
  useEffect(() => { const el = scroller.current; if (el && stick.current) el.scrollTop = el.scrollHeight }, [chat.items, chat.status])

  const provs = cfg.data?.config.providers ?? {}
  const ideas = [...CHAT_IDEAS, { label: draft ? tk('Đề xuất trang con cho từng mục chính') : tk('Tạo và chèn trang con theo từng mục'), Icon: FilePlus }]
  const active = provider && provs[provider] ? provider : (cfg.data?.config.default_provider ?? null)
  const pickProvider = (id: string) => { setProvider(id); store.set('pages-chat-provider', id) }
  const attachmentDraft = useAttachments(async () => {
    const { id } = await loadNotebookChat(page.id, notebookId, true)
    if (!id) throw new Error(t('Không thể mở hội thoại.'))
    return id
  })
  const submit = async (v: string) => {
    if (!v.trim() || !ready || loadError || chat.busy || preparing || attachmentDraft.uploading) return
    setPreparing(true)
    try {
      if (!await beforeSend() || !mounted.current) return
      const { id } = await loadNotebookChat(page.id, notebookId, true)
      if (!id || !mounted.current) return
      if (id !== chat.sessionId) await openChat(id)
      if (!mounted.current) return
      setText('')
      stick.current = true
      const paths = attachmentDraft.paths
      const documentIds = attachmentDraft.documents.map((doc) => doc.id)
      attachmentDraft.reset()
      await chat.send(v, active, paths, { document_ids: documentIds, context: `${draft ? 'page-draft' : 'page'}:${page.id}`, permission: draft ? 'readonly' : 'guarded' })
    } catch (error) {
      if (mounted.current) setLoadError(error)
    } finally {
      if (mounted.current) setPreparing(false)
    }
  }

  return (
    <SessionContext.Provider value={chat.sessionId}>
      <aside aria-label={t('Hỏi AI về ghi chú này')} style={wide ? { width } : undefined}
        className="fixed inset-y-0 right-0 z-[60] flex w-full max-w-[27rem] shrink-0 flex-col border-l border-line bg-panel shadow-2xl xl:relative xl:inset-auto xl:z-auto xl:max-w-none xl:shadow-none">
        {wide && <div role="separator" aria-orientation="vertical" aria-label={t('Kéo để đổi độ rộng')}
          onPointerDown={(e) => { drag.current = true; e.currentTarget.setPointerCapture(e.pointerId) }}
          onPointerMove={(e) => { if (drag.current) onWidth(Math.min(window.innerWidth * 0.45, Math.max(320, window.innerWidth - e.clientX))) }}
          onPointerUp={(e) => { drag.current = false; e.currentTarget.releasePointerCapture(e.pointerId) }}
          className="group absolute left-0 top-0 z-10 flex h-full w-3 -translate-x-1/2 cursor-col-resize items-center justify-center touch-none">
          <div className="h-full w-px bg-line transition group-hover:w-1 group-hover:bg-accent" />
        </div>}
        <header className="shrink-0 border-b border-line px-4 pb-3 pt-4">
          <div className="flex items-start gap-3">
            <span className="grid size-10 shrink-0 place-items-center rounded-xl bg-accent/12 text-accent"><Sparkles className="size-5" /></span>
            <div className="min-w-0 flex-1">
              <h2 className="flex items-center gap-2 text-sm font-semibold">{t('Hỏi AI về ghi chú này')}{chat.busy && <LoaderCircle className="size-3.5 shrink-0 animate-spin text-accent" />}</h2>
              <p className="mt-0.5 truncate text-xs text-muted" title={page.title}>{page.title || t('Chưa đặt tên')}</p>
            </div>
            <button type="button" aria-label={t('Đóng')} onClick={onClose} className="grid size-8 shrink-0 place-items-center rounded-lg text-muted hover:bg-panel2 hover:text-fg"><X className="size-4" /></button>
          </div>
          <div className="mt-3 grid grid-cols-2 gap-1 rounded-xl border border-line bg-bg/70 p-1" role="group" aria-label={t('Cách dùng AI')}>
            <Button size="sm" variant={draft ? 'secondary' : 'ghost'} disabled={chat.busy || preparing} onClick={() => { if (!draft) onToggleDraft() }} aria-pressed={draft}
              className={cn('w-full whitespace-nowrap', draft && 'border-transparent bg-accent/12 text-accent')}><FileText className="size-3.5 shrink-0" />{t('Xem bản nháp')}</Button>
            <Button size="sm" variant={draft ? 'ghost' : 'secondary'} disabled={chat.busy || preparing} onClick={() => { if (draft) onToggleDraft() }} aria-pressed={!draft}
              className={cn('w-full whitespace-nowrap', !draft && 'border-transparent bg-accent/12 text-accent')}><FilePenLine className="size-3.5 shrink-0" />{t('Sửa trực tiếp')}</Button>
          </div>
        </header>
        <div ref={scroller} onScroll={(e) => { const el = e.currentTarget; stick.current = el.scrollHeight - el.scrollTop - el.clientHeight < 80 }} className="min-h-0 flex-1 overflow-y-auto">
          <div className="space-y-4 p-4">
            {loadError ? <div className="space-y-2">
              <ErrorNote error={loadError} />
              <Button size="sm" onClick={() => { setLoadError(null); setReady(false); setAttempt((n) => n + 1) }}>{t('Thử lại')}</Button>
            </div> : !ready ? <Loading /> : chat.items.length === 0 ? (
              <div className="space-y-3">
                <p className="text-sm leading-relaxed text-muted">{draft ? t('Xem phản hồi rồi chọn nội dung để chèn vào ghi chú.') : t('AI có thể sửa nội dung hoặc tạo trang con.')}</p>
                <div className="grid gap-2">{ideas.map(({ label, Icon }) => (
                  <button key={label} type="button" disabled={preparing || chat.busy} onClick={() => void submit(t(label))}
                    className="group flex items-center gap-2.5 rounded-xl border border-line bg-bg/70 px-3 py-2.5 text-left text-sm transition hover:border-accent/50 hover:bg-accent/5 disabled:opacity-50">
                    <span className="grid size-8 shrink-0 place-items-center rounded-lg bg-accent/10 text-accent"><Icon className="size-4" /></span>
                    <span className="min-w-0 flex-1">{t(label)}</span><ArrowRight className="size-3.5 shrink-0 text-muted group-hover:text-accent" />
                  </button>
                ))}</div>
              </div>
            ) : chat.items.map((it) => (
              <div key={it.key}>
                <MessageView item={it} sid={chat.sessionId ?? undefined} onDecide={(aid, ok) => void chat.decide(aid, ok)} onAnswer={(q, a) => void chat.answer(q, a)} onUndo={() => void chat.undo()} onOpenFile={() => undefined} canAct={!chat.busy} />
                {draft && it.kind === 'assistant' && !it.streaming && !!it.text.trim() && (
                  <Button size="sm" variant="ghost" onClick={() => onInsert(it.text)}><Plus className="size-3.5" />{t('Chèn cuối ghi chú')}</Button>
                )}
              </div>
            ))}
            {chat.busy && chat.status && <p className="flex items-center gap-2 text-xs text-muted" role="status"><LoaderCircle className="size-3.5 animate-spin text-accent" />{chat.status}</p>}
          </div>
        </div>
        <form onDragOver={attachmentDraft.dragOver} onDrop={ready && !loadError && !preparing ? attachmentDraft.drop : undefined} className="border-t border-line bg-panel p-4" onSubmit={(e) => { e.preventDefault(); void submit(text) }}>
          <div className="rounded-xl border border-line bg-bg shadow-sm transition focus-within:border-accent focus-within:ring-2 focus-within:ring-accent/12">
            <AttachmentPreview draft={attachmentDraft} />
            <textarea onPaste={ready && !loadError && !preparing ? attachmentDraft.paste : undefined} value={text} onChange={(e) => setText(e.target.value)} rows={2} placeholder={t('Nhắn cho agent… (Enter để gửi)')} aria-label={t('Nhắn cho agent')}
              onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey && !e.nativeEvent.isComposing) { e.preventDefault(); void submit(text) } }}
              className="block min-h-12 w-full resize-none bg-transparent px-3 pt-2.5 text-sm focus:outline-none" />
            <div className="flex items-center justify-between gap-2 px-2 pb-2">
              <AttachmentMenu draft={attachmentDraft} disabled={!ready || !!loadError || preparing} />
              <select value={active ?? ''} onChange={(e) => pickProvider(e.target.value)} aria-label={t('Chọn model')} title={t('Chọn model')}
                className="min-w-0 max-w-[15rem] flex-1 truncate rounded-md border border-transparent bg-transparent px-1.5 py-1 text-xs text-muted hover:border-line hover:text-fg focus:outline-none">
                {Object.entries(provs).map(([id, c]) => <option key={id} value={id}>{id}{c.model ? ` · ${c.model}` : ''}</option>)}
              </select>
              {chat.busy
                ? <Button type="button" size="sm" onClick={chat.stop} aria-label={t('Dừng')}><Square className="size-3.5" /></Button>
                : <Button type="submit" size="sm" variant="primary" disabled={!text.trim() || attachmentDraft.uploading || preparing || !ready || !!loadError} aria-label={t('Gửi')}><Send className="size-3.5" /></Button>}
            </div>
          </div>
        </form>
      </aside>
    </SessionContext.Provider>
  )
}

export function PagesPage() {
  const { confirmAction } = useDialogs()
  const { id } = useParams()
  const nav = useNavigate()
  const qc = useQueryClient()
  const toast = useToast()
  const [q, setQ] = useState('')
  const [chatOpen, setChatOpen] = useState(() => store.get('pages-chat') === '1')
  const toggleChat = () => setChatOpen((current) => { store.set('pages-chat', current ? '0' : '1'); return !current })
  const list = useQuery({ queryKey: ['pages'], queryFn: () => api.get<PageInfo[]>('/api/pages') })
  const page = useQuery({ queryKey: ['page', id], queryFn: () => api.get<PageFull>(`/api/pages/${id}`), enabled: !!id, staleTime: Infinity, gcTime: 0, retry: false })
  const search = q.trim()
  const searching = !id && search.length >= 2
  const found = useQuery({
    queryKey: ['pages-search', search],
    queryFn: () => api.get<(PageInfo & { snippet?: string })[]>(`/api/pages/search?q=${encodeURIComponent(search)}`),
    enabled: searching,
  })

  const refresh = () => {
    void qc.invalidateQueries({ queryKey: ['pages'] })
    void qc.invalidateQueries({ queryKey: ['pages-search'] })
  }
  const create = useMutation({
    mutationFn: () => api.post<PageFull>('/api/pages', { parent: '' }),
    onSuccess: (entry) => { refresh(); nav(`/pages/${entry.id}`) },
    onError: (error) => toast(errMsg(error), 'bad'),
  })
  const remove = useMutation({
    mutationFn: (entry: PageInfo) => api.del(`/api/pages/${entry.id}`),
    onSuccess: (_result, entry) => { refresh(); nav(entry.parent ? `/pages/${entry.parent}` : '/pages', { replace: true }) },
    onError: (error) => toast(errMsg(error), 'bad'),
  })
  const pages = list.data ?? []
  const askDelete = async (entry: PageInfo) => {
    const hasChildren = pages.some((child) => child.parent === entry.id)
    const question = hasChildren ? t('Xóa ghi chú "{name}" và mọi trang con của nó?', { name: entry.title }) : t('Xóa ghi chú "{name}"?', { name: entry.title })
    if (!remove.isPending && await confirmAction(question, { action: t('Xóa'), danger: true })) remove.mutate(entry)
  }
  if (id) {
    if (page.isLoading) return <Loading />
    if (page.error) return <Page><Link to="/pages" className="mb-4 inline-flex items-center gap-2 text-sm text-accent"><ArrowLeft className="size-4" />{t('Sổ tay')}</Link><ErrorNote error={page.error} /></Page>
    const entry = page.data
    return entry ? <div className="flex h-full min-h-0">
      <PageEditor key={entry.id} page={entry} pages={pages} onSaved={refresh} onOpen={(pid) => nav(`/pages/${pid}`)}
        chatOpen={chatOpen} onToggleChat={toggleChat} onDelete={(title) => askDelete({ ...entry, title: title || t('Chưa đặt tên') })} />
    </div> : null
  }

  const roots = pages.filter((entry) => !entry.parent)
  const entries: (PageInfo & { snippet?: string })[] = searching ? found.data ?? [] : roots
  const loading = searching ? found.isLoading : list.isLoading
  const error = searching ? found.error : list.error
  return <Page>
    <PageHeader title={t('Sổ tay')} action={
      <Button variant="primary" loading={create.isPending} onClick={() => create.mutate()}><Plus className="size-4" />{t('Tạo sổ tay')}</Button>
    } />
    <div className="mb-5">
      <SearchBox value={q} onChange={setQ} placeholder={t('Tìm ghi chú…')} label={t('Tìm ghi chú')} />
    </div>
    {loading ? <Loading /> : error ? <ErrorNote error={error} /> : entries.length === 0 ? (
      <div className="rounded-2xl border border-dashed border-line bg-panel/40">
        <EmptyState icon={BookOpen} title={searching ? t('Không tìm thấy ghi chú.') : t('Chưa có sổ tay')} />
      </div>
    ) : <ul className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5">
      {entries.map((entry) => {
        const childCount = pages.filter((child) => child.parent === entry.id).length
        return <li key={entry.id} className="min-w-0">
          <Link to={`/pages/${entry.id}`} className="group flex min-w-0 items-center gap-3 rounded-xl border border-line bg-panel p-3 transition hover:border-accent/60 hover:bg-panel2/50">
            <span className="grid size-9 shrink-0 place-items-center rounded-lg bg-accent/10 text-accent">
              {entry.icon ? <PageIcon icon={entry.icon} /> : <BookOpen className="size-4" />}
            </span>
            <div className="min-w-0 flex-1">
              <h2 className="truncate text-sm font-semibold">{entry.title}</h2>
              <p className="truncate text-xs text-muted">{entry.snippet || (childCount > 0 ? (childCount === 1 ? t('1 trang con') : t('{n} trang con', { n: childCount })) : fmtDateTime(entry.updated))}</p>
            </div>
            <ArrowRight className="size-3.5 shrink-0 text-muted transition group-hover:translate-x-0.5 group-hover:text-accent" />
          </Link>
        </li>
      })}
    </ul>}
  </Page>
}
