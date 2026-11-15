import { useEffect, useState } from 'react'
import { LoaderCircle, Sparkles } from 'lucide-react'
import { BrandIcon, detectBrand } from '@/components/ui/BrandIcon'
import { AgentMark, AgentOwl } from '@/components/ui/AgentMark'
import { t } from '@/lib/i18n.ts'

/** Indeterminate activity, never a fabricated percentage or completed business step. */
export function WorkflowWaiting({ status, label, compact = false }: { status?: string | null; label: string; compact?: boolean }) {
  const [seconds, setSeconds] = useState(0)
  useEffect(() => {
    const start = Date.now()
    const timer = window.setInterval(() => setSeconds(Math.floor((Date.now() - start) / 1000)), 1000)
    return () => window.clearInterval(timer)
  }, [])
  const elapsed = seconds < 60 ? `${seconds}s` : `${Math.floor(seconds / 60)}:${String(seconds % 60).padStart(2, '0')}`
  const message = status || t('Đang chuẩn bị nội dung…')
  const brand = detectBrand(status)
  if (compact) return <div className="flex items-start gap-2">
    {brand ? <span role="img" aria-label={brand} className="mt-0.5 grid size-8 shrink-0 place-items-center rounded-lg border border-line bg-panel"><BrandIcon brand={brand} className="size-5" /></span> : <AgentMark size="sm" />}
    <div className="flex min-w-0 flex-1 items-center gap-2.5 rounded-lg border border-accent/15 bg-accent/5 px-3 py-2.5 text-xs" role="status" aria-live="polite">
    <LoaderCircle className="workflow-spinner size-3.5 shrink-0 text-accent" />
    <span className="min-w-0 flex-1 break-words text-muted">{message}</span><span className="shrink-0 tabular-nums text-muted/70" aria-hidden>{elapsed}</span>
    </div>
  </div>
  return <div className="relative flex min-h-[340px] h-full flex-col items-center justify-center overflow-hidden rounded-lg px-4 py-8 sm:px-8">
    <div className="pointer-events-none absolute h-64 w-64 rounded-full bg-accent/[.07] blur-3xl" aria-hidden />
    <div className="relative mb-6 grid size-28 shrink-0 place-items-center" aria-hidden>
      <span className="workflow-orbit absolute inset-0 rounded-full border border-accent/15 border-t-accent/70" />
      <span className="workflow-orbit-reverse absolute inset-3 rounded-full border border-accent/10 border-b-accent/50" />
      <span className="workflow-breathe grid size-16 place-items-center rounded-2xl border border-accent/20 bg-panel shadow-lg shadow-accent/10"><AgentOwl className="h-9" /></span>
      <span className="absolute right-0 top-5 size-2 rounded-full bg-accent shadow-sm shadow-accent" />
    </div>
    <div className="relative w-full max-w-md text-center">
      <div className="mb-2 flex items-center justify-center gap-2"><Sparkles className="size-3.5 text-accent" /><span className="text-[11px] font-medium uppercase tracking-[.16em] text-accent">{t('Argus đang làm việc')}</span></div>
      <h3 className="text-base font-semibold tracking-tight sm:text-lg">{t(label)}</h3>
      <p role="status" aria-live="polite" className="mt-2 break-words text-xs leading-relaxed text-muted">{message}</p>
      <div className="mt-3 flex items-center justify-center gap-2 text-xs text-muted/70"><span className="flex gap-1" aria-hidden>{[0,1,2].map((i) => <span key={i} className="workflow-dot size-1 rounded-full bg-accent" style={{ animationDelay: `${i * 160}ms` }} />)}</span><span aria-hidden>{elapsed}</span><span>{t('Kết quả sẽ xuất hiện tại đây')}</span></div>
      <div className="mt-7 space-y-2.5 rounded-xl border border-line/60 bg-panel/50 p-4 text-left" aria-hidden>
        <div className="workflow-shimmer mb-4 h-2 w-2/5 rounded-full" />
        <div className="workflow-shimmer h-1.5 w-full rounded-full" />
        <div className="workflow-shimmer h-1.5 w-5/6 rounded-full" style={{ animationDelay: '.15s' }} />
        <div className="workflow-shimmer h-1.5 w-3/5 rounded-full" style={{ animationDelay: '.3s' }} />
      </div>
    </div>
  </div>
}
