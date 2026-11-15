import { useState, type ReactNode } from 'react'
import { Link, Navigate, useParams, useSearchParams } from 'react-router-dom'
import { CheckCircle2, FileText, History, MessageSquare, PackageCheck, Shuffle, ChevronDown, ChevronRight, type LucideIcon } from 'lucide-react'
import { Loading } from '@/components/ui/misc'
import { assistantIcon } from '@/lib/assistantIcons'
import { FALLBACK_ASSISTANTS, useAssistants, type Assistant, type FormFlow } from '@/lib/assistants'
import { t, tk } from '@/lib/i18n.ts'
import { useConfig, useSessions } from '@/lib/queries'
import { BrandIcon, detectBrand } from '@/components/ui/BrandIcon'
import { cn, timeAgo } from '@/lib/utils'
import { ExamShufflePanel } from './ExamShufflePanel'
import { FlowRunner } from './FlowRunner'
import { PlanCard } from '../chat/PlanCard'
import type { PlanItem } from '@/lib/types'

const SHUFFLE = 'exam-shuffle'
const DEFAULT_FLOW: FormFlow = { id: 'chung', label: tk('Giao việc'), desc: tk('Hãy giúp tôi việc sau.'), steps: [{ id: 'chung', label: tk('Giao việc'), goal: tk('Mô tả việc cần làm, có thể đính kèm tài liệu.'), task: tk('Hãy giúp tôi việc sau.'), review: [tk('Kết quả đúng yêu cầu'), tk('Có file nếu yêu cầu cần file')], produces: [], fields: [{ key: 'yeu_cau', label: tk('Bạn cần gì?'), type: 'textarea', required: true }, { key: 'tep', label: tk('Tài liệu đính kèm'), type: 'file', multiple: true }] }] }

const MODEL_KEY = 'feature:provider'
function useFeatureProvider() {
  const cfg = useConfig()
  const [saved, setSaved] = useState<string | null>(() => { try { return localStorage.getItem(MODEL_KEY) } catch { return null } })
  const providers = cfg.data ? Object.keys(cfg.data.config.providers) : []
  const active = saved && providers.includes(saved) ? saved : (cfg.data?.config.default_provider ?? null)
  const set = (id: string) => { setSaved(id); try { localStorage.setItem(MODEL_KEY, id) } catch { /* private mode */ } }
  return { active, set, providers, cfg: cfg.data?.config }
}

/** Chọn mô hình AI cho cả trang chức năng (nhớ lựa chọn giữa các lần mở). */
function ModelSelect({ active, set, providers, cfg }: ReturnType<typeof useFeatureProvider>) {
  if (!cfg || providers.length === 0 || !active) return null
  return <label className="relative block cursor-pointer rounded-xl border border-accent/25 bg-accent/[.06] px-3 py-2.5 transition hover:border-accent/60 focus-within:ring-2 focus-within:ring-accent/30">
    <span className="mb-1 flex items-center justify-between gap-2 text-[10px] font-semibold uppercase tracking-wider text-muted">{t('Mô hình AI')}<span className="max-w-28 truncate text-[9px] font-normal tracking-normal">{active}</span></span>
    <span className="flex items-start gap-2"><BrandIcon brand={detectBrand(active)} className="mt-0.5 size-4 shrink-0" /><span className="min-w-0 flex-1 break-words text-xs font-medium leading-relaxed">{cfg.providers[active]?.model || active}</span><ChevronDown className="mt-0.5 size-3.5 shrink-0 text-muted" /></span>
    <select value={active} onChange={(e) => set(e.target.value)} aria-label={t('Mô hình AI')} className="absolute inset-0 h-full w-full cursor-pointer opacity-0">
      {providers.map((id) => <option key={id} value={id} className="bg-panel text-fg">{cfg.providers[id].model || id} · {id}</option>)}
    </select>
  </label>

}

function Side({ title, icon: Icon, children }: { title: string; icon: LucideIcon; children: React.ReactNode }) {
  return (
    <section className="rounded-xl border border-line bg-panel px-4 py-3">
      <h2 className="mb-2 flex items-center gap-2 text-[10px] font-semibold uppercase tracking-wider text-muted"><Icon className="size-3.5" />{title}</h2>
      {children}
    </section>
  )
}

/** Cột bên trái: kế hoạch trực tiếp, sản phẩm, tiêu chí và lịch sử. */
function SidePanel({ a, plan = [], controls, steps, flow }: { a: Assistant; plan?: PlanItem[]; controls?: ReactNode; steps?: ReactNode; flow?: FormFlow }) {
  const sessions = useSessions()
  const recent = (sessions.data ?? []).filter((s) => s.assistant === a.id).slice(0, 5)
  const formats: Record<string,string> = { docx: 'Word', xlsx: 'Excel', pdf: 'PDF', pptx: 'PowerPoint', html: 'HTML' }
  const dels = flow ? flow.steps.filter((s) => s.produces.length).map((s) => `${t(s.label)} · ${s.produces.map((k) => formats[k] ?? k).join(' / ')}`) : (a.deliverables ?? []).filter((d) => d !== 'none')
  const criteria = flow?.steps.at(-1)?.review ?? a.done_criteria ?? []
  return (
    <aside className="hidden min-h-0 space-y-3 overflow-y-auto pr-1 xl:col-start-1 xl:row-start-1 xl:block">
      {controls}
      {steps && <section className="rounded-xl border border-line bg-panel px-4 py-3"><h2 className="mb-3 text-[10px] font-semibold uppercase tracking-wider text-muted">{t('Các bước thực hiện')}</h2>{steps}</section>}
      {plan.length > 0 && <div className="rounded-xl border border-line bg-panel px-4 py-3"><PlanCard items={plan} compact plain /></div>}
      {dels.length > 0 && (
        <Side title={t('Bạn sẽ nhận được')} icon={PackageCheck}>
          <ul className="space-y-2 text-xs leading-relaxed">{dels.map((d) => <li key={d} className="flex gap-2"><FileText className="mt-0.5 size-3.5 shrink-0 text-accent" /><span>{t(d)}</span></li>)}</ul>
        </Side>
      )}
      {criteria.length > 0 && (
        <Side title={t('Trợ lý tự kiểm trước khi giao')} icon={CheckCircle2}>
          <ul className="space-y-2 text-xs leading-relaxed text-fg/75">{criteria.map((c) => <li key={c} className="flex gap-2"><CheckCircle2 className="mt-0.5 size-3 shrink-0 text-muted" /><span>{t(c)}</span></li>)}</ul>
        </Side>
      )}
      <Side title={t('Việc gần đây')} icon={History}>
        {recent.length === 0 ? <p className="text-xs text-muted">{t('Chưa có việc nào với chức năng này.')}</p> : (
          <ul className="divide-y divide-line/70">
            {recent.map((s) => (
              <li key={s.id}><Link to={`/chat?session=${s.id}`} className="flex items-center justify-between gap-3 py-2 text-xs transition hover:text-accent"><span className="truncate">{s.title || t('Cuộc trò chuyện mới')}</span><span className="shrink-0 text-xs text-muted">{timeAgo(s.updated)}</span></Link></li>
            ))}
          </ul>
        )}
      </Side>
    </aside>
  )
}

/** Trang chức năng của một trợ lý: chọn quy trình nghiệp vụ, chạy từng bước (duyệt kết quả mỗi bước); cột trái chứa chọn quy trình, các bước, kế hoạch và thông tin phụ. */
export function FeaturePage() {
  const { id } = useParams()
  const q = useAssistants()
  const [sp, setSp] = useSearchParams()
  const model = useFeatureProvider()
  if (q.isLoading) return <Loading />
  const a = (q.data ?? FALLBACK_ASSISTANTS).find((x) => x.id === id)
  if (!a) return <Navigate to="/f" replace />
  const Icon = assistantIcon(a.icon)
  const form = a.form ?? { flows: [DEFAULT_FLOW] }
  const flows = form.flows.length || form.panels?.length ? form.flows : [DEFAULT_FLOW]
  const choices = [
    ...flows.map((x) => ({ id: x.id, label: t(x.label), hint: t(x.desc), meta: t('{n} bước', { n: x.steps.length }) })),
    ...(form.panels ?? []).map((p) => ({ id: p, label: p === SHUFFLE ? t('Xáo đề thành nhiều mã') : p, hint: t('Tải đề .docx, nhận các mã đề và bảng đáp án'), meta: t('Công cụ') })),
  ]
  const cur = choices.find((x) => x.id === (sp.get('tab') ?? sp.get('flow')))?.id ?? choices[0]?.id
  const flow = flows.find((x) => x.id === cur)

  const navigation = choices.length > 1 && <nav aria-label={t('Bạn muốn làm gì?')} className="space-y-1 rounded-lg bg-bg/60 p-1">
    {choices.map((x) => <button key={x.id} onClick={() => setSp({ flow: x.id }, { replace: true })} aria-current={cur === x.id ? 'page' : undefined} title={x.hint} className={cn('flex w-full items-start gap-2 rounded-md border px-2.5 py-2 text-left transition', cur === x.id ? 'border-accent/25 bg-accent/10 text-accent' : 'border-transparent text-muted hover:bg-panel hover:text-fg')}>
      <span className="min-w-0 flex-1"><span className="block text-xs font-medium leading-relaxed">{x.label}</span></span>
      <span className="mt-0.5 shrink-0 text-[10px] opacity-60">{x.meta}</span>
    </button>)}
  </nav>
  const controls = <section className="rounded-xl border border-line bg-panel p-3">
    <div className="mb-3 flex items-center gap-2.5"><span className="grid size-9 shrink-0 place-items-center rounded-xl bg-accent/10 text-accent"><Icon className="size-4" /></span><h1 className="min-w-0 text-sm font-semibold leading-snug" title={t(form.intro || a.description)}>{t(a.name)}</h1></div>
    <div className="mb-4 hidden xl:block"><ModelSelect {...model} /></div>
    {navigation && <div><p className="mb-2 text-[10px] font-semibold uppercase tracking-wider text-muted">{t('Bạn muốn làm gì?')}</p>{navigation}</div>}
    <Link to="/chat" state={{ assistant: a.id }} className="mt-3 flex items-center justify-center gap-2 rounded-lg border border-line py-2 text-xs text-muted transition hover:border-accent/40 hover:text-accent"><MessageSquare className="size-3.5" />{t('Trò chuyện tự do')}<ChevronRight className="size-3" /></Link>
  </section>

  return (
    <div className="flex h-full min-h-0 flex-col overflow-hidden px-4 py-3 sm:px-6 lg:px-8">
      <div className="mb-2 shrink-0 space-y-2 xl:hidden"><ModelSelect {...model} /><details className="rounded-lg border border-line px-3 py-2"><summary className="cursor-pointer text-sm font-medium">{t(a.name)}</summary><div className="mt-2">{controls}</div></details></div>
      <div className="flex min-h-0 flex-1 flex-col gap-3">
          <div className="grid min-h-0 flex-1 gap-x-4 gap-y-3 xl:grid-cols-[16rem_minmax(0,1fr)] xl:grid-rows-[minmax(0,1fr)]">
            {flow && <FlowRunner key={a.id + flow.id} a={a} flow={flow} provider={model.active} renderSidebar={(plan, steps) => <SidePanel a={a} plan={plan} controls={controls} steps={steps} flow={flow} />} />}
            {cur === SHUFFLE && <div className="h-full min-h-0 overflow-y-auto rounded-xl border border-line bg-panel p-4 xl:col-start-2 xl:row-start-1"><h2 className="mb-1 flex items-center gap-2 text-base font-semibold"><Shuffle className="size-4 text-accent" />{t('Xáo đề thành nhiều mã')}</h2><ExamShufflePanel /></div>}
            {!flow && <SidePanel a={a} controls={controls} />}
          </div>
      </div>
    </div>
  )
}
