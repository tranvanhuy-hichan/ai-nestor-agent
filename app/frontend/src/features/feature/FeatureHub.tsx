import { useState } from 'react'
import { Link } from 'react-router-dom'
import { ArrowRight, Layers, SearchX } from 'lucide-react'
import { SearchBox } from '@/components/ui/SearchBox'
import { assistantIcon } from '@/lib/assistantIcons'
import { coreFeatures, searchableText } from '@/lib/featureCatalog'
import { FALLBACK_ASSISTANTS, GROUP_ORDER, useAssistants } from '@/lib/assistants'
import { t } from '@/lib/i18n.ts'
import { cn } from '@/lib/utils'

export function FeatureHub() {
  const list = [...coreFeatures(useAssistants().data ?? FALLBACK_ASSISTANTS), { id: 'youtube-translate', name: 'Phiên dịch YouTube trực tiếp', icon: 'languages', group: 'Cá nhân', description: 'Nghe âm thanh tab YouTube, xem phụ đề nhiều ngôn ngữ và phát giọng dịch. Tải phụ đề SRT sau khi xem.', starters: [], form: { flows: [] } }]
  const [q, setQ] = useState('')
  const [group, setGroup] = useState('')
  const groups = [...GROUP_ORDER, ...new Set(list.map((a) => a.group).filter((g) => !GROUP_ORDER.includes(g)))].filter((g) => list.some((a) => a.group === g))
  const shown = list.filter((a) => (!group || a.group === group) && searchableText([t(a.name), t(a.description), ...a.starters, ...(a.form?.flows.map((f) => t(f.label)) ?? [])].join(' ')).includes(searchableText(q.trim())))
  return <div className="flex h-full min-h-0 flex-col overflow-hidden px-4 py-5 sm:px-6 lg:px-8">
    <header className="mb-5 flex shrink-0 flex-wrap items-end justify-between gap-4">
      <div><p className="mb-1.5 text-[11px] font-semibold uppercase tracking-[.16em] text-accent">ARGUS WORKSPACE</p><h1 className="text-2xl font-semibold tracking-tight">{t('Công cụ')}</h1><p className="mt-1.5 text-sm text-muted">{t('Chọn công việc. Cung cấp thông tin. Nhận kết quả hoàn chỉnh.')}</p></div>
      <div className="w-full sm:w-80 [&>div]:!w-full"><SearchBox value={q} onChange={setQ} placeholder={t('Tìm công cụ hoặc công việc…')} label={t('Tìm công cụ')} /></div>
    </header>
    <nav aria-label={t('Nhóm công cụ')} className="mb-4 flex shrink-0 gap-2 overflow-x-auto pb-2">
      {['', ...groups].map((g) => <button key={g} onClick={() => setGroup(g)} aria-pressed={group === g} className={cn('flex shrink-0 items-center gap-2 rounded-lg border px-3 py-2 text-xs font-medium transition', group === g ? 'border-accent/40 bg-accent/10 text-accent' : 'border-line bg-panel text-muted hover:border-accent/40 hover:text-fg')}>
        {g ? t(g) : t('Tất cả')}<span className="rounded bg-fg/5 px-1.5 py-0.5 text-[10px] tabular-nums">{g ? list.filter((a) => a.group === g).length : list.length}</span>
      </button>)}
    </nav>
    <div className="min-h-0 flex-1 overflow-y-auto pr-1">
      <p className="mb-3 text-xs text-muted">{t('{n} công cụ phù hợp', { n: shown.length })}</p>
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 2xl:grid-cols-3 min-[2000px]:grid-cols-4">
        {shown.map((a) => {
          const Icon = assistantIcon(a.icon)
          const formats = [...new Set(a.form?.flows.flatMap((f) => f.steps.flatMap((s) => s.produces)) ?? [])].filter((x) => ['docx','xlsx','pptx','pdf','html'].includes(x))
          const labels: Record<string,string> = { docx:'Word', xlsx:'Excel', pptx:'PowerPoint', pdf:'PDF', html:'HTML' }
          return <Link key={a.id} to={`/f/${a.id}`} className="group flex min-w-0 flex-col rounded-2xl border border-line bg-panel p-5 transition hover:border-accent/50 hover:shadow-lg hover:shadow-accent/5 focus-visible:outline-2 focus-visible:outline-accent">
            <div className="mb-4 flex items-start justify-between gap-3"><span className="grid size-11 shrink-0 place-items-center rounded-xl border border-accent/15 bg-accent/10 text-accent"><Icon className="size-5" /></span><span className="pt-1 text-[10px] font-medium uppercase tracking-wide text-muted">{t(a.group)}</span></div>
            <h2 className="text-base font-semibold tracking-tight">{t(a.name)}</h2>
            <p className="mt-2 min-h-10 text-sm leading-relaxed text-muted">{t(a.description)}</p>
            <div className="mt-4 flex min-h-6 flex-wrap gap-1.5">{formats.map((format) => <span key={format} className="rounded-md border border-line bg-bg px-2 py-1 text-[10px] font-medium text-fg/70">{labels[format]}</span>)}</div>
            <div className="mt-auto pt-4"><div className="flex items-center justify-between border-t border-line pt-3 text-xs"><span className="flex items-center gap-1.5 text-muted"><Layers className="size-3.5" />{t('{n} quy trình', { n: a.id === 'youtube-translate' ? 1 : a.form?.flows.length ?? 1 })}</span><span className="flex items-center gap-1.5 font-medium text-accent">{t('Mở công cụ')}<ArrowRight className="size-3.5 transition-transform group-hover:translate-x-1" /></span></div></div>
          </Link>
        })}
      </div>
      {!shown.length && <div className="grid min-h-60 place-content-center justify-items-center gap-3 rounded-2xl border border-dashed border-line text-muted"><SearchX className="size-8" strokeWidth={1.5} /><p className="text-sm">{t('Không có công cụ phù hợp.')}</p><button onClick={() => { setQ(''); setGroup('') }} className="text-sm text-accent">{t('Xóa bộ lọc')}</button></div>}
    </div>
  </div>
}
