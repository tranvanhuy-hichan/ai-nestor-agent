import { memo } from 'react'
import { AgentMark } from '@/components/ui/AgentMark'
import { cn } from '@/lib/utils'
import type { Caption } from './useLiveTranslation'

const stamp = (n: number) => new Date(Math.max(0, n) * 1000).toISOString().slice(11, 19)
const accents = ['border-accent/60', 'border-emerald-400/50', 'border-violet-400/50', 'border-amber-400/50']

export const CaptionEntry = memo(function CaptionEntry({ caption, latest, languages, showOriginal, compact = false }: { caption: Caption; latest: boolean; languages: Record<string, string>; showOriginal: boolean; compact?: boolean }) {
  const entries = Object.entries(caption.translations)
  return <article className={cn('rounded-xl border p-3.5 transition-colors sm:p-4', latest ? 'border-accent/30 bg-accent/[.035]' : 'border-line/70 bg-bg/30')}>
    <header className="mb-3 flex items-center justify-between gap-3">
      <div className="flex items-center gap-2.5"><AgentMark size="sm" className="!mt-0 !size-6 !rounded-md" /><time className="font-mono text-[11px] tabular-nums text-muted">{stamp(caption.start)}<span className="mx-1.5 text-muted/40">—</span>{stamp(caption.end)}</time></div>
      {latest && <span className="rounded-full bg-accent/10 px-2 py-1 text-[10px] font-medium text-accent">Mới nhất</span>}
    </header>
    {showOriginal && <div className="mb-4 flex flex-col gap-1.5 border-b border-line/60 pb-3 sm:flex-row sm:gap-3"><span className="shrink-0 pt-0.5 text-[10px] font-medium uppercase tracking-wider text-muted/70">Bản gốc</span><p className="min-w-0 whitespace-pre-wrap break-words text-[13px] leading-relaxed text-muted">{caption.text}</p></div>}
    <div className={cn('grid gap-4', !compact && entries.length > 1 && 'md:grid-cols-2')}>
      {entries.map(([id, text], i) => <section key={id} className={cn('min-w-0 border-l-2 pl-3', accents[i % accents.length])}>
        <h3 className="mb-1.5 text-[10px] font-semibold uppercase tracking-wider text-muted">{languages[id] || id}</h3>
        <p lang={id} className="whitespace-pre-wrap break-words text-[15px] leading-7 text-fg">{text || <span className="text-muted">…</span>}</p>
      </section>)}
    </div>
  </article>
})
