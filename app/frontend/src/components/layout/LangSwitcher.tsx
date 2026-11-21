import { Check } from 'lucide-react'
import { cn } from '@/lib/utils'
import { setLang, t, useLang, type Lang } from '@/lib/i18n.ts'

const OPTIONS: { id: Lang; label: string }[] = [
  { id: 'vi', label: 'Tiếng Việt' },
  { id: 'en', label: 'English' },
]

export function LangSwitcher({ expanded }: { expanded?: boolean }) {
  const lang = useLang()
  const next = lang === 'vi' ? OPTIONS[1] : OPTIONS[0]
  const switchLabel = t('Chuyển sang {name}', { name: next.label })
  return (
    <>
      {expanded !== false && <div role="group" aria-label={t('Ngôn ngữ')}
        className={cn('grid-cols-2 gap-1 rounded-xl border border-line bg-bg/70 p-1', expanded === undefined ? 'hidden md:grid' : 'grid')}>
        {OPTIONS.map(({ id, label }) => (
          <button key={id} type="button" onClick={() => setLang(id)} aria-pressed={lang === id} lang={id}
            className={cn('flex h-7 items-center justify-center gap-1 rounded-lg px-1 text-xs font-medium transition focus-visible:outline-2 focus-visible:outline-accent',
              lang === id ? 'bg-accent/15 text-accent' : 'text-muted hover:bg-panel2 hover:text-fg')}>
            {lang === id && <Check className="size-3 shrink-0" aria-hidden />}
            {label}
          </button>
        ))}
      </div>}
      {expanded !== true && <button type="button" onClick={() => setLang(next.id)} title={switchLabel} aria-label={switchLabel}
        className={cn('grid h-9 w-full place-items-center rounded-lg text-xs font-semibold text-muted transition hover:bg-panel2 hover:text-fg', expanded === undefined && 'md:hidden')}>
        {lang.toUpperCase()}
      </button>}
    </>
  )
}
