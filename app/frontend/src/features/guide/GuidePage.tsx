import { useLayoutEffect, useRef, useState } from 'react'
import { ArrowLeft, ArrowRight, BookOpen, Search } from 'lucide-react'
import { Link, NavLink, useParams } from 'react-router-dom'
import { Card } from '@/components/ui/Card'
import { SearchBox } from '@/components/ui/SearchBox'
import { EmptyState, Page, PageHeader } from '@/components/ui/misc'
import { Markdown } from '@/features/chat/Markdown'
import { searchableText } from '@/lib/featureCatalog'
import { t, tk, useLang } from '@/lib/i18n.ts'
import { cn } from '@/lib/utils'
import english from './en.md?raw'
import vietnamese from './vi.md?raw'

interface Chapter { id: string; title: string; body: string }

function chapters(source: string): Chapter[] {
  const parts = source.split(/^# ([a-z-]+) \| (.+)$/gm)
  const items: Chapter[] = []
  for (let index = 1; index < parts.length; index += 3) {
    items.push({ id: parts[index], title: parts[index + 1].trim(), body: parts[index + 2].trim() })
  }
  return items
}

const guides = { en: chapters(english), vi: chapters(vietnamese) }

const destinations: Record<string, string> = {
  start: '/',
  chat: '/chat',
  tools: '/f',
  tasks: '/tasks',
  kanban: '/kanban',
  automations: '/automations',
  inbox: '/notifications',
  skills: '/skills',
  notebook: '/pages',
  documents: '/documents',
  ocr: '/settings?tab=ocr',
  models: '/providers',
  extensions: '/integrations',
  assistant: '/profiles',
  monitoring: '/activity',
  settings: '/settings',
  backup: '/settings?tab=backup',
}

const groups = [
  { label: tk('Bắt đầu'), ids: ['start', 'chat', 'tools'] },
  { label: tk('Công việc'), ids: ['tasks', 'kanban', 'automations', 'inbox'] },
  { label: tk('Nội dung & kiến thức'), ids: ['skills', 'notebook', 'documents', 'ocr'] },
  { label: tk('Hệ thống'), ids: ['models', 'extensions', 'assistant', 'monitoring', 'settings', 'backup'] },
]

export function GuidePage() {
  const lang = useLang()
  const { topic } = useParams()
  const [query, setQuery] = useState('')
  const heading = useRef<HTMLHeadingElement>(null)
  const items = guides[lang]
  const activeIndex = topic ? items.findIndex((chapter) => chapter.id === topic) : 0
  const active = items[activeIndex]
  const terms = searchableText(query.trim()).split(/\s+/).filter(Boolean)
  const matches = items.filter(({ title, body }) => {
    const index = searchableText(`${title} ${body}`)
    return terms.every((term) => index.includes(term))
  })
  useLayoutEffect(() => { if (topic) heading.current?.focus() }, [topic])

  return (
    <Page>
      <div className="w-full">
        <PageHeader title={t('Hướng dẫn sử dụng')} />
        <div className="grid items-start gap-5 lg:grid-cols-[17rem_minmax(0,1fr)]">
          <Card className={cn('min-w-0 p-3 lg:sticky lg:top-3 lg:max-h-[calc(100dvh-2rem)] lg:overflow-auto [&>div]:!w-full', topic && 'hidden lg:block')}>
            <SearchBox value={query} onChange={setQuery} label={t('Tìm trong hướng dẫn')} placeholder={t('Tìm trong hướng dẫn…')} />
            <nav className="mt-3 space-y-3" aria-label={t('Chủ đề hướng dẫn')}>
              {groups.map(({ label, ids }) => {
                const links = matches.filter((chapter) => ids.includes(chapter.id))
                if (!links.length) return null
                return (
                  <div key={label}>
                    <h2 className="px-2 pb-1 text-xs font-semibold text-muted">{t(label)}</h2>
                    {links.map((chapter) => (
                      <NavLink key={chapter.id} to={`/guide/${chapter.id}`}
                        aria-current={chapter.id === active?.id ? 'page' : undefined}
                        className={cn('block rounded-lg px-2.5 py-2 text-sm transition', chapter.id === active?.id
                          ? 'bg-accent/12 font-medium text-accent' : 'text-muted hover:bg-panel2 hover:text-fg')}>
                        {chapter.title}
                      </NavLink>
                    ))}
                  </div>
                )
              })}
              {!matches.length && <EmptyState icon={Search} title={t('Không tìm thấy chủ đề phù hợp.')} />}
            </nav>
          </Card>

          <section className={cn('min-w-0', !topic && 'hidden lg:block')} aria-label={t('Nội dung hướng dẫn')}>
            <Link to="/guide" className="mb-3 inline-flex items-center gap-2 text-sm text-muted hover:text-fg lg:hidden"><ArrowLeft className="size-4" />{t('Tất cả chủ đề')}</Link>
            {active ? (
              <Card className="overflow-hidden">
                <div className="border-b border-line p-4 sm:p-6">
                  <div className="flex flex-wrap items-center justify-between gap-3">
                    <h2 ref={heading} tabIndex={-1} className="min-w-0 text-lg font-semibold outline-none">{active.title}</h2>
                    <Link to={destinations[active.id]} className="inline-flex items-center gap-2 rounded-lg border border-line bg-panel2 px-3 py-2 text-xs font-medium hover:border-accent/60 hover:text-accent">
                      {t('Mở chức năng')}<ArrowRight className="size-3.5" />
                    </Link>
                  </div>
                </div>
                <article className="p-4 text-sm leading-relaxed sm:p-6 [&_li]:mb-2">
                  <Markdown text={active.body} article />
                </article>
              </Card>
            ) : (
              <EmptyState icon={BookOpen} title={t('Không tìm thấy chủ đề phù hợp.')}
                action={<Link to="/guide" className="text-sm text-accent hover:underline">{t('Tất cả chủ đề')}</Link>} />
            )}
          </section>
        </div>
      </div>
    </Page>
  )
}
