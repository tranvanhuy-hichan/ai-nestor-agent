import { useRef, useState } from 'react'
import { NavLink, Outlet, useLocation } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { NotebookText, Bell, Blocks, Cable, FileSearch, Clock, Code2, Columns3, Gauge, Sparkles, Wrench, FolderCog, ListTodo, House, LayoutDashboard, LogOut, MessageSquare, Moon, Plug, Puzzle, Settings, LayoutGrid, ChevronDown, Sun, type LucideIcon } from 'lucide-react'
import { setTheme, useAppearance } from '@/lib/appearance'
import { api } from '@/lib/api'
import { t, tk } from '@/lib/i18n.ts'
import { AgentLogo, AgentOwl } from '@/components/ui/AgentMark'
import { LangSwitcher } from './LangSwitcher'
import { CODE_MODE } from '@/lib/features'
import { cn } from '@/lib/utils'

type NavItem = { to: string; label: string; icon: LucideIcon; hint: string }
const TOP: NavItem[] = [
  { to: '/', label: tk('Trang chủ'), icon: House, hint: tk('Tổng quan và việc nên làm tiếp') },
  { to: '/chat', label: tk('Trò chuyện'), icon: MessageSquare, hint: tk('Nói chuyện và giao việc cho agent') },
  { to: '/f', label: tk('Công cụ'), icon: LayoutGrid, hint: tk('Mỗi trợ lý chuyên trách một trang riêng') },
]
type NavGroup = { title: string; items: NavItem[] }

const PRIMARY_GROUPS: NavGroup[] = [
  { title: tk('Công việc'), items: [
    ...(CODE_MODE ? [{ to: '/code', label: tk('Lập trình'), icon: Code2, hint: tk('Mở một dự án và nhờ agent viết code') }] : []),
    { to: '/tasks', label: tk('Tác vụ'), icon: ListTodo, hint: tk('Việc dài agent làm ngầm') },
    { to: '/kanban', label: tk('Kanban'), icon: Columns3, hint: tk('Bảng việc kéo-thả, giao cho Nestor chạy nền') },
    { to: '/automations', label: tk('Tự động hóa'), icon: Clock, hint: tk('Việc lặp theo lịch') },
    { to: '/notifications', label: tk('Hộp thư'), icon: Bell, hint: tk('Thông báo từ agent') },
  ] },
  { title: tk('Nội dung & kiến thức'), items: [
    { to: '/skills', label: tk('Kỹ năng'), icon: Puzzle, hint: tk('Dạy agent làm thêm việc mới') },
    { to: '/pages', label: tk('Sổ tay'), icon: NotebookText, hint: tk('Ghi chú và tài liệu của bạn, agent đọc và viết được') },
    { to: '/documents', label: tk('Tài liệu'), icon: FileSearch, hint: tk('Hỏi đáp trên hợp đồng, báo cáo, bảng tính của bạn') },
  ] },
]

const ADMIN_GROUPS: NavGroup[] = [
  { title: tk('Kết nối & tiện ích'), items: [
    { to: '/plugins', label: tk('Tiện ích'), icon: Blocks, hint: tk('Nối GitHub, Notion, Canva… chỉ bằng một cú bấm') },
    { to: '/integrations', label: tk('Kết nối'), icon: Cable, hint: tk('Telegram, API, công cụ ngoài') },
  ] },
  { title: tk('Trợ lý của tôi'), items: [
    { to: '/profiles', label: tk('Hồ sơ trợ lý'), icon: Sparkles, hint: tk('Cấu hình trợ lý tùy chỉnh') },
    { to: '/workspace', label: tk('Tính cách & trí nhớ'), icon: FolderCog, hint: tk('Agent là ai và nhớ gì về bạn') },
  ] },
  { title: tk('Hệ thống'), items: [
    { to: '/providers', label: tk('Mô hình AI'), icon: Plug, hint: tk('Bộ não của agent: Gemini, Ollama…') },
    { to: '/gateway', label: tk('Sức khỏe hệ thống'), icon: Gauge, hint: tk('Tài nguyên và nhật ký máy chủ') },
    { to: '/activity', label: tk('Thống kê'), icon: LayoutDashboard, hint: tk('Agent đã làm gì, tốn bao nhiêu') },
  ] },
]

/**
 * NavRow:
 *  - chatMode=false (trang bình thường): responsive md: như cũ
 *  - chatMode=true: icon luôn hiện, text fade in/out bằng opacity để animate mượt
 */
function NavRow({ item: { to, label, icon: Icon, hint }, unread, chatMode, expanded }: {
  item: NavItem; unread: number; chatMode?: boolean; expanded?: boolean
}) {
  if (chatMode) {
    return (
      <NavLink to={to} end={to === '/' || to === '/f'} aria-label={t(label)} title={`${t(label)} — ${t(hint)}`}
        className={({ isActive }) => cn(
          'flex h-9 items-center gap-3 rounded-lg px-2.5 text-sm font-medium transition-colors',
          isActive ? 'bg-accent/12 text-accent' : 'text-muted hover:bg-panel2 hover:text-fg',
        )}>
        <Icon className="size-[18px] shrink-0" />
        <span className={cn('whitespace-nowrap transition-opacity duration-200', expanded ? 'opacity-100' : 'opacity-0')}>
          {t(label)}
        </span>
        {unread > 0 && (
          <span className={cn('ml-auto rounded-full bg-accent px-1.5 text-[11px] font-semibold text-accent-fg whitespace-nowrap transition-opacity duration-200', expanded ? 'opacity-100' : 'opacity-0')}>
            {unread}
          </span>
        )}
      </NavLink>
    )
  }
  return (
    <NavLink to={to} end={to === '/' || to === '/f'} aria-label={t(label)} title={`${t(label)} — ${t(hint)}`}
      className={({ isActive }) => cn(
        'flex h-9 items-center gap-3 rounded-lg px-2.5 text-sm font-medium transition-colors',
        isActive ? 'bg-accent/12 text-accent' : 'text-muted hover:bg-panel2 hover:text-fg',
      )}>
      <Icon className="size-[18px] shrink-0" />
      <span className="hidden md:block">{t(label)}</span>
      {unread > 0 && <span className="ml-auto hidden rounded-full bg-accent px-1.5 text-[11px] font-semibold text-accent-fg md:block">{unread}</span>}
    </NavLink>
  )
}

export function AppLayout() {
  const light = useAppearance().theme === 'light'
  const location = useLocation()
  const [expanded, setExpanded] = useState(false)
  const [adminOverride, setAdminOverride] = useState<{ location: string; open: boolean }>()
  const adminRoute = ADMIN_GROUPS.some((group) => group.items.some((item) => location.pathname === item.to))
  const adminOpen = adminOverride?.location === location.key ? adminOverride.open : adminRoute
  const leaveTimer = useRef<ReturnType<typeof setTimeout> | null>(null)
  const count = useQuery({ queryKey: ['notif-count'], queryFn: () => api.get<{ unread: number }>('/api/notifications/count'), refetchInterval: 15_000 })
  const auth = useQuery({ queryKey: ['auth-status'], queryFn: () => api.get<{ required: boolean }>('/api/auth/status') })
  const logout = () => { void api.post('/api/auth/logout').then(() => window.dispatchEvent(new Event('auth-required'))) }

  const compactSidebar = location.pathname.startsWith('/chat') || location.pathname.startsWith('/f/')
    || /^\/pages\/[^/]+$/.test(location.pathname) || /^\/documents\/[^/]+$/.test(location.pathname)
  const unread = count.data?.unread ?? 0

  const onEnter = () => { if (leaveTimer.current) clearTimeout(leaveTimer.current); setExpanded(true) }
  const onLeave = () => { leaveTimer.current = setTimeout(() => setExpanded(false), 180) }

  const renderGroup = (group: NavGroup, chatMode: boolean, exp: boolean) => (
    <div key={group.title} className="mt-3">
      {chatMode ? (
        <p className={cn('mb-1 overflow-hidden whitespace-nowrap px-2.5 text-[11px] font-semibold uppercase tracking-wide text-muted/70 transition-opacity duration-200', exp ? 'opacity-100' : 'opacity-0')}>{t(group.title)}</p>
      ) : (
        <>
          <p className="mb-1 hidden px-2.5 text-[11px] font-semibold uppercase tracking-wide text-muted/70 md:block">{t(group.title)}</p>
          <div className="mx-2 mb-1.5 border-t border-line md:hidden" />
        </>
      )}
      {group.items.map((item) => <NavRow key={item.to} item={item} unread={item.to === '/notifications' ? unread : 0} chatMode={chatMode} expanded={exp} />)}
    </div>
  )

  /** Keep the same navigation on the full sidebar and the compact chat rail. */
  const navContent = (chatMode: boolean, exp: boolean) => (
    <>
      {/* Logo */}
      <NavLink to="/" aria-label={t('Về trang chủ')} title={t('Về trang chủ')}
        className={cn(
          'mt-3 mb-3 flex shrink-0 items-center overflow-hidden rounded-lg outline-offset-2 transition-all duration-200 hover:opacity-80',
          chatMode ? 'mx-2 h-10 gap-3 px-0.5' : 'mx-2 md:mx-3 md:px-1',
        )}>
        {chatMode ? (
          <>
            {/* Owl icon: thu nhỏ khi collapsed, trở lại kích thước bình thường khi hover */}
            <AgentOwl className={cn('shrink-0 transition-all duration-200', exp ? 'h-9 opacity-100' : 'h-6 opacity-60')} />
            {/* Chữ NESTOR: fade + slide in khi expanded */}
            <span className={cn('overflow-hidden whitespace-nowrap transition-all duration-200', exp ? 'max-w-[9rem] opacity-100' : 'max-w-0 opacity-0')}>
              <AgentLogo className="[&>span:first-child]:hidden" />
            </span>
          </>
        ) : (
          <>
            <AgentOwl className="h-8 md:hidden" />
            <AgentLogo className="hidden md:flex" />
          </>
        )}
      </NavLink>

      {/* Nav items */}
      <nav className="flex flex-1 flex-col gap-0.5 overflow-y-auto px-2 py-2" aria-label={t('Điều hướng chính')}>
        {TOP.map((item) => <NavRow key={item.to} item={item} unread={0} chatMode={chatMode} expanded={exp} />)}
        {PRIMARY_GROUPS.map((group) => renderGroup(group, chatMode, exp))}
        <div className="mt-3 border-t border-line pt-2">
          <button type="button" onClick={() => setAdminOverride({ location: location.key, open: !adminOpen })}
            aria-label={t('Quản trị')} aria-expanded={adminOpen} aria-controls="admin-navigation" title={t('Quản trị')}
            className="flex h-9 w-full items-center gap-3 rounded-lg px-2.5 text-sm font-medium text-muted hover:bg-panel2 hover:text-fg">
            <Wrench className="size-[18px] shrink-0" />
            <span className={cn('min-w-0 flex-1 truncate text-left', chatMode ? !exp && 'hidden' : 'hidden md:block')}>{t('Quản trị')}</span>
            <ChevronDown className={cn('size-3.5 shrink-0 transition-transform', !adminOpen && '-rotate-90', chatMode ? !exp && 'hidden' : 'hidden md:block')} />
          </button>
          <div id="admin-navigation" hidden={!adminOpen}>{adminOpen && ADMIN_GROUPS.map((group) => renderGroup(group, chatMode, exp))}</div>
        </div>
      </nav>

      <div className="space-y-1.5 border-t border-line p-2">
        <div className={cn('gap-1', chatMode ? exp ? 'flex items-center' : 'grid' : 'grid md:flex md:items-center')}>
          <div className="min-w-0 flex-1">
            <NavRow item={{ to: '/settings', label: tk('Cài đặt'), icon: Settings, hint: tk('Tính năng, an toàn, mật khẩu') }} unread={0} chatMode={chatMode} expanded={exp} />
          </div>
          <button type="button" onClick={() => setTheme(light ? 'dark' : 'light')}
            aria-label={light ? t('Giao diện tối') : t('Giao diện sáng')} title={light ? t('Giao diện tối') : t('Giao diện sáng')}
            className={cn('grid h-9 shrink-0 place-items-center rounded-lg text-muted transition hover:bg-panel2 hover:text-fg focus-visible:outline-2 focus-visible:outline-accent',
              chatMode ? exp ? 'w-9' : 'w-full' : 'w-full md:w-9')}>
            {light ? <Moon className="size-[18px]" /> : <Sun className="size-[18px]" />}
          </button>
          {auth.data?.required && <button type="button" onClick={logout} aria-label={t('Đăng xuất')} title={t('Đăng xuất')}
            className={cn('grid h-9 shrink-0 place-items-center rounded-lg text-muted transition hover:bg-panel2 hover:text-fg focus-visible:outline-2 focus-visible:outline-accent',
              chatMode ? exp ? 'w-9' : 'w-full' : 'w-full md:w-9')}>
            <LogOut className="size-[18px]" />
          </button>}
        </div>
        <LangSwitcher expanded={chatMode ? exp : undefined} />
      </div>
    </>
  )

  return (
    <div className="flex h-full">
      {compactSidebar ? (
        /* Focus mode: wrapper w-14 giữ chỗ trong layout (không giật),
           aside fixed không trôi theo scroll, mở rộng mượt mà bằng CSS transition width */
        <div className="relative w-14 shrink-0">
          <aside
            onMouseEnter={onEnter}
            onMouseLeave={onLeave}
            onFocus={onEnter}
            onBlur={(event) => { if (!event.currentTarget.contains(event.relatedTarget)) onLeave() }}
            className={cn(
              'fixed inset-y-0 left-0 z-50 flex flex-col overflow-hidden border-r border-line',
              'transition-[width,background-color,box-shadow] duration-200 ease-in-out',
              expanded ? 'w-56 bg-panel shadow-2xl' : 'w-14 bg-panel/60',
            )}
          >
            {navContent(true, expanded)}
          </aside>
        </div>
      ) : (
        /* Trang thường: sidebar rộng bình thường, responsive */
        <aside className="flex w-14 shrink-0 flex-col border-r border-line bg-panel/60 md:w-56">
          {navContent(false, true)}
        </aside>
      )}
      <main className="min-w-0 flex-1 overflow-hidden"><Outlet /></main>
    </div>
  )
}
