import { coreFeatures, searchableText } from '@/lib/featureCatalog'
import { useState } from 'react'
import { Link } from 'react-router-dom'
import { SearchBox } from '@/components/ui/SearchBox'
import { assistantIcon } from '@/lib/assistantIcons'
import { FALLBACK_ASSISTANTS, GROUP_ORDER, useAssistants } from '@/lib/assistants'
import { t } from '@/lib/i18n.ts'

/** Danh mục tất cả chức năng, gom theo nhóm người dùng. */
export function FeatureHub() {
  const list = coreFeatures(useAssistants().data ?? FALLBACK_ASSISTANTS)
  const [q, setQ] = useState('')
  const norm = (s: string) => searchableText(t(s))
  const shown = list.filter((a) => !q.trim() || norm(a.name).includes(searchableText(q.trim())) || norm(a.description).includes(searchableText(q.trim())))
  const groups = [...GROUP_ORDER, ...new Set(shown.map((a) => a.group).filter((g) => !GROUP_ORDER.includes(g)))]
  return (
    <div className="flex h-full min-h-0 flex-col overflow-hidden px-4 py-3 sm:px-6 lg:px-8">
      <div className="mb-3 flex shrink-0 flex-wrap items-center gap-3">
        <div className="min-w-0 flex-1"><h1 className="text-lg font-semibold tracking-tight">{t('Chức năng')}</h1><p className="line-clamp-1 text-sm text-muted">{t('Chọn việc cần làm, xem đầu ra và duyệt kết quả theo từng bước.')}</p></div>
        <div className="w-60 shrink-0 [&>div]:!w-full"><SearchBox value={q} onChange={setQ} placeholder={t('Tìm chức năng…')} label={t('Tìm chức năng')} /></div>
      </div>
      <div className="min-h-0 flex-1 gap-x-4 overflow-y-auto md:columns-2 xl:columns-4">
        {groups.map((g) => {
          const items = shown.filter((a) => a.group === g)
          return items.length === 0 ? null : (
            <section key={g} className="mb-3 min-w-0 break-inside-avoid">
              <h2 className="mb-1.5 text-[12px] font-semibold uppercase tracking-wide text-muted">{t(g)}</h2>
              <div className="space-y-1">
                {items.map((a) => {
                  const Icon = assistantIcon(a.icon)
                  return (
                    <Link key={a.id} to={`/f/${a.id}`} title={t(a.description)} className="flex items-center gap-2 rounded-lg border border-line bg-panel p-3 text-sm transition hover:border-accent/60 focus-visible:outline-2 focus-visible:outline-accent">
                      <span className="grid size-6 shrink-0 place-items-center rounded-md bg-accent/10 text-accent"><Icon className="size-3.5" /></span>
                      <span className="min-w-0 flex-1">
                        <span className="block font-medium">{t(a.name)}</span>
                        <span className="mt-1 block text-xs text-muted">{t(a.description)}</span>
                        {(a.deliverables ?? []).some((d) => d !== 'none') && <span className="mt-2 block text-xs text-accent">{t('Đầu ra')}: {(a.deliverables ?? []).filter((d) => d !== 'none').slice(0, 2).map((d) => t(d)).join(' · ')}</span>}
                        {a.form && <span className="mt-1 block text-xs text-muted">{t('{n} quy trình', { n: a.form.flows.length })}</span>}
                      </span>
                    </Link>
                  )
                })}
              </div>
            </section>
          )
        })}
        {shown.length === 0 && <p className="text-sm text-muted">{t('Không có chức năng nào khớp.')}</p>}
      </div>
    </div>
  )
}
