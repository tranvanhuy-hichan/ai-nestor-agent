import { coreFeatures } from '@/lib/featureCatalog'
import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { ArrowRight, ArrowUp, Bell, BookOpen, CalendarClock, Download, FileSpreadsheet, FileText, History, MessageSquare, Presentation, LayoutGrid, File as FileIcon, type LucideIcon } from 'lucide-react'
import { AgentLogoStacked } from '@/components/ui/AgentMark'
import { assistantIcon } from '@/lib/assistantIcons'
import { Loading, Page } from '@/components/ui/misc'
import { api } from '@/lib/api'
import { FALLBACK_ASSISTANTS, FEATURED, GROUP_ORDER, useAssistants, type Assistant } from '@/lib/assistants'
import { t, tk } from '@/lib/i18n.ts'
import { useConfig, useSessions } from '@/lib/queries'
import type { FileEntry, NotificationItem } from '@/lib/types'
import { cn, timeAgo } from '@/lib/utils'

const OFFICE = /\.(docx|xlsx|pptx|pdf)$/i
const fileIcon = (n: string) => (/\.xlsx$/i.test(n) ? FileSpreadsheet : /\.pptx$/i.test(n) ? Presentation : /\.(docx|pdf)$/i.test(n) ? FileText : FileIcon)

const QUICK: { to: string; icon: LucideIcon; label: string; hl?: boolean }[] = [
  { to: '/f', icon: LayoutGrid, label: tk('Tất cả chức năng'), hl: true },
  { to: '/tasks', icon: History, label: tk('Việc đã làm') },
  { to: '/automations', icon: CalendarClock, label: tk('Lịch tự động') },
  { to: '/documents', icon: BookOpen, label: tk('Tài liệu') },
]

/** Trợ lý hiện sẵn ở tab "Tất cả"; phần còn lại mở bằng nút "Xem tất cả". */

type Result = { sid: string; path: string; mtime: number }

function useRecentFiles() {
  const sessions = useSessions()
  const top = (sessions.data ?? []).slice(0, 8).map((s) => s.id)
  return useQuery({
    queryKey: ['recent-office-files', top.join(',')],
    enabled: top.length > 0,
    queryFn: async () => {
      const lists = await Promise.all(top.map((sid) => api.get<FileEntry[]>(`/api/sessions/${sid}/files`).then((fs) => fs.filter((f) => !f.dir && OFFICE.test(f.path)).map((f) => ({ sid, path: f.path, mtime: f.mtime })), () => [] as Result[])))
      return lists.flat().sort((a, b) => b.mtime - a.mtime).slice(0, 8)
    },
  })
}

function AssistantCard({ a, onPick }: { a: Assistant; onPick: (a: Assistant) => void }) {
  const Icon = assistantIcon(a.icon)
  return (
    <button onClick={() => onPick(a)} title={t(a.description)} className={cn('flex items-center gap-3 rounded-lg border px-3 py-2.5 text-left transition hover:border-accent/60', 'border-line bg-bg')}>
      <span className="grid size-9 shrink-0 place-items-center rounded-md bg-accent/10 text-accent"><Icon className="size-[18px]" /></span>
      <span className="min-w-0">
        <span className="block truncate text-sm font-medium">{t(a.name)}</span>
        <span className="line-clamp-1 text-xs text-fg/75">{t(a.description)}</span>
      </span>
    </button>
  )
}

function Block({ title, to, cta, children }: { title: string; to?: string; cta?: string; children: React.ReactNode }) {
  return (
    <section className="flex h-full flex-col rounded-xl border border-line bg-panel px-4 py-3">
      <div className="mb-1 flex items-baseline justify-between">
        <h2 className="text-[13px] font-semibold uppercase tracking-wide text-muted">{title}</h2>
        {to && <Link to={to} className="flex items-center gap-1 text-xs text-accent hover:underline">{cta}<ArrowRight className="size-3" /></Link>}
      </div>
      <div className="divide-y divide-line/70">{children}</div>
    </section>
  )
}
const rowCls = 'flex items-center justify-between gap-3 py-2.5 text-sm'
const Muted = ({ children }: { children: React.ReactNode }) => <p className="py-3 text-sm text-muted">{children}</p>

export function SimpleHome() {
  const nav = useNavigate()
  const cfg = useConfig()
  const assistants = useAssistants()
  const sessions = useSessions()
  const recent = useRecentFiles()
  const inbox = useQuery({ queryKey: ['notifications'], queryFn: () => api.get<{ items: NotificationItem[]; unread: number }>('/api/notifications') })
  const [text, setText] = useState('')
  const [group, setGroup] = useState('')
  const [showAll, setShowAll] = useState(false)
    if (!cfg.data) return <Loading />

  const list = coreFeatures(assistants.data ?? FALLBACK_ASSISTANTS)
  const groups = [...GROUP_ORDER, ...new Set(list.map((a) => a.group).filter((g) => !GROUP_ORDER.includes(g)))]
  const featured = list.filter((a) => FEATURED.includes(a.id))
  const shown = group ? list.filter((a) => a.group === group) : showAll ? list : featured.length >= 4 ? featured : list.slice(0, 10)
  const go = (prompt: string) => nav('/chat', { state: { prompt } })
  const open = (a: Assistant) => nav(`/f/${a.id}`)
  const hr = new Date().getHours()
  const greet = hr < 11 ? t('Chào buổi sáng') : hr < 18 ? t('Chào buổi chiều') : t('Chào buổi tối')

  return (
    <Page>
      <div className="space-y-4">
        <section className="rounded-xl border border-line bg-panel p-5">
          <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_minmax(0,2fr)] lg:items-center">
            <header className="flex items-center gap-4">
              <AgentLogoStacked />
              <div>
                <h1 className="text-2xl font-semibold tracking-tight">{greet}</h1>
                <p className="text-sm text-muted">{t('Bạn muốn tôi giúp việc gì?')}</p>
              </div>
            </header>
            <form onSubmit={(e) => { e.preventDefault(); if (text.trim()) go(text.trim()) }} className="flex items-center gap-2 rounded-lg border border-line bg-bg p-2 transition focus-within:border-accent">
              <input value={text} onChange={(e) => setText(e.target.value)} autoFocus aria-label={t('Yêu cầu')}
                placeholder={t('Ví dụ: Soạn tờ trình xin kinh phí tổ chức hội nghị tổng kết năm')}
                className="h-11 flex-1 bg-transparent px-3 text-[15px] placeholder:text-muted/70 focus:outline-none" />
              <button type="submit" disabled={!text.trim()} aria-label={t('Gửi')} className="grid size-10 place-items-center rounded-md bg-accent text-accent-fg transition hover:brightness-110 disabled:opacity-40"><ArrowUp className="size-5" /></button>
            </form>
          </div>
        </section>

        <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
          {QUICK.map(({ to, icon: Icon, label, hl }) => (
            <Link key={to} to={to} className={cn('flex items-center gap-2.5 rounded-xl border px-3.5 py-3 text-sm transition hover:border-accent/60', hl ? 'border-accent/60 bg-accent/10 font-medium' : 'border-line bg-panel')}>
              <Icon className="size-[18px] shrink-0 text-accent" /><span className="truncate">{t(label)}</span>
            </Link>
          ))}
        </div>

        <section className="rounded-xl border border-line bg-panel px-4 py-3">
          <div className="mb-3 flex flex-wrap items-center gap-2">
            <h2 className="mr-2 text-[13px] font-semibold uppercase tracking-wide text-muted">{t('Chức năng: bấm để bắt đầu')}</h2>
            {['', ...groups.filter((g) => list.some((a) => a.group === g))].map((g) => (
              <button key={g || 'all'} onClick={() => setGroup(g)} className={cn('rounded-full px-3 py-1 text-xs transition', group === g ? 'bg-accent text-accent-fg' : 'border border-line text-muted hover:border-accent/60 hover:text-fg')}>{g ? t(g) : t('Tất cả')}</button>
            ))}
          </div>
          <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
            {shown.map((a) => <AssistantCard key={a.id} a={a} onPick={open} />)}
          </div>
          {!group && !showAll && list.length > shown.length && (
            <button onClick={() => setShowAll(true)} className="mt-3 text-sm text-accent hover:underline">{t('Xem tất cả {n} trợ lý', { n: list.length })}</button>
          )}
          {!group && showAll && <button onClick={() => setShowAll(false)} className="mt-3 text-sm text-accent hover:underline">{t('Thu gọn')}</button>}
        </section>

        <div className="grid items-stretch gap-4 lg:grid-cols-3">
          <Block title={t('Hội thoại gần đây')} to="/chat" cta={t('Xem tất cả')}>
            {(sessions.data ?? []).length === 0 ? <Muted>{t('Chưa có hội thoại nào.')}</Muted> : (sessions.data ?? []).slice(0, 5).map((s) => (
              <Link key={s.id} to={`/chat?session=${s.id}`} className={cn(rowCls, 'transition hover:text-accent')}>
                <span className="flex min-w-0 items-center gap-3"><MessageSquare className="size-4 shrink-0 text-muted" /><span className="truncate">{s.title || t('Cuộc trò chuyện mới')}</span></span>
                <span className="shrink-0 text-xs text-muted">{timeAgo(s.updated)}</span>
              </Link>
            ))}
          </Block>

          <Block title={t('Kết quả gần đây')} to="/tasks" cta={t('Xem việc đã làm')}>
            {(recent.data ?? []).length === 0 ? <Muted>{t('Các file Word, Excel, PowerPoint tôi làm cho bạn sẽ hiện ở đây.')}</Muted> : (recent.data ?? []).slice(0, 5).map((f) => {
              const Icon = fileIcon(f.path)
              const name = f.path.split('/').pop() ?? f.path
              return (
                <div key={f.sid + f.path} className={rowCls}>
                  <Link to={`/chat?session=${f.sid}`} className="flex min-w-0 items-center gap-3 hover:text-accent" title={t('Mở cuộc trò chuyện tạo ra file này')}><Icon className="size-4 shrink-0 text-accent" /><span className="truncate">{name}</span></Link>
                  <a href={`/api/sessions/${f.sid}/file?path=${encodeURIComponent(f.path)}&raw=true`} download={name} aria-label={t('Tải về')} className="shrink-0 rounded-md p-1 text-accent hover:bg-panel2"><Download className="size-4" /></a>
                </div>
              )
            })}
          </Block>

          <Block title={t('Thông báo mới')} to="/notifications" cta={(inbox.data?.unread ?? 0) > 0 ? `${t('Hộp thư')} · ${inbox.data?.unread}` : t('Hộp thư')}>
            {!inbox.data?.items.length ? <Muted>{t('Không có thông báo.')}</Muted> : inbox.data.items.slice(0, 4).map((n) => (
              <Link key={n.id} to="/notifications" className="block py-2.5 transition hover:text-accent">
                <p className="flex items-center gap-2 text-sm"><Bell className={cn('size-3.5 shrink-0', n.read ? 'text-muted' : 'text-accent')} /><span className="truncate font-medium">{n.title}</span><span className="ml-auto shrink-0 text-xs text-muted">{timeAgo(n.ts)}</span></p>
                <p className="mt-0.5 line-clamp-1 pl-5 text-xs text-muted">{n.body}</p>
              </Link>
            ))}
          </Block>
        </div>
      </div>
    </Page>
  )
}
