import { useState } from 'react'
import { Link, Navigate, useNavigate, useParams, useSearchParams } from 'react-router-dom'
import { CheckCircle2, FileText, History, MessageSquare, PackageCheck, Shuffle, Sparkles } from 'lucide-react'
import { Loading } from '@/components/ui/misc'
import { assistantIcon } from '@/lib/assistantIcons'
import { FALLBACK_ASSISTANTS, useAssistants, type Assistant, type FormFlow } from '@/lib/assistants'
import { t, tk } from '@/lib/i18n.ts'
import { useConfig, useSessions } from '@/lib/queries'
import { BrandIcon, detectBrand } from '@/components/ui/BrandIcon'
import { cn, timeAgo } from '@/lib/utils'
import { ExamShufflePanel } from './ExamShufflePanel'
import { FlowRunner } from './FlowRunner'

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
  return (
    <label className="flex h-9 items-center gap-2 rounded-lg border border-line bg-panel px-2.5 text-sm text-muted transition hover:border-accent/60">
      <BrandIcon brand={detectBrand(active)} className="size-4 shrink-0" />
      <span className="sr-only">{t('Mô hình AI')}</span>
      <select value={active} onChange={(e) => set(e.target.value)} aria-label={t('Mô hình AI')} className="max-w-[16rem] cursor-pointer truncate bg-transparent text-fg outline-none">
        {providers.map((id) => <option key={id} value={id} className="bg-panel">{cfg.providers[id].model || id}{id === cfg.default_provider ? '' : ` · ${id}`}</option>)}
      </select>
    </label>
  )
}

function Side({ title, icon: Icon, children }: { title: string; icon: typeof Sparkles; children: React.ReactNode }) {
  return (
    <section className="rounded-xl border border-line bg-panel px-4 py-3">
      <h2 className="mb-2 flex items-center gap-2 text-[13px] font-semibold uppercase tracking-wide text-muted"><Icon className="size-3.5 text-accent" />{title}</h2>
      {children}
    </section>
  )
}

/** Cột bên phải: gợi ý bắt đầu nhanh, sản phẩm nhận được, tiêu chí tự kiểm, các lần làm gần đây của chức năng. */
function SidePanel({ a }: { a: Assistant }) {
  const nav = useNavigate()
  const sessions = useSessions()
  const recent = (sessions.data ?? []).filter((s) => s.assistant === a.id).slice(0, 5)
  const dels = (a.deliverables ?? []).filter((d) => d !== 'none')
  return (
    <aside className="hidden min-h-0 space-y-3 overflow-y-auto pr-1 xl:col-start-2 xl:row-start-2 xl:block">
      {a.starters.length > 0 && (
        <Side title={t('Bắt đầu nhanh')} icon={Sparkles}>
          <ul className="space-y-1.5">
            {a.starters.map((s) => (
              <li key={s}><button onClick={() => nav('/chat', { state: { assistant: a.id, prompt: s } })} className="w-full rounded-lg border border-line px-3 py-2 text-left text-sm transition hover:border-accent/60 hover:bg-accent/5">{t(s)}</button></li>
            ))}
          </ul>
        </Side>
      )}
      {dels.length > 0 && (
        <Side title={t('Bạn sẽ nhận được')} icon={PackageCheck}>
          <ul className="space-y-1 text-sm">{dels.map((d) => <li key={d} className="flex gap-2"><FileText className="mt-0.5 size-4 shrink-0 text-accent" /><span>{t(d)}</span></li>)}</ul>
        </Side>
      )}
      {(a.done_criteria ?? []).length > 0 && (
        <Side title={t('Trợ lý tự kiểm trước khi giao')} icon={CheckCircle2}>
          <ul className="space-y-1.5 text-sm text-fg/85">{a.done_criteria!.map((c) => <li key={c} className="flex gap-2"><CheckCircle2 className="mt-0.5 size-4 shrink-0 text-ok" /><span>{t(c)}</span></li>)}</ul>
        </Side>
      )}
      <Side title={t('Việc gần đây')} icon={History}>
        {recent.length === 0 ? <p className="text-sm text-muted">{t('Chưa có việc nào với chức năng này.')}</p> : (
          <ul className="divide-y divide-line/70">
            {recent.map((s) => (
              <li key={s.id}><Link to={`/chat?session=${s.id}`} className="flex items-center justify-between gap-3 py-2 text-sm transition hover:text-accent"><span className="truncate">{s.title || t('Cuộc trò chuyện mới')}</span><span className="shrink-0 text-xs text-muted">{timeAgo(s.updated)}</span></Link></li>
            ))}
          </ul>
        )}
      </Side>
    </aside>
  )
}

/** Trang chức năng của một trợ lý: chọn quy trình nghiệp vụ, chạy từng bước (duyệt kết quả mỗi bước); cột phải có gợi ý, sản phẩm, tiêu chí và lịch sử. */
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

  const navigation = (choices.length > 1 && (
            <div role="tablist" aria-label={t('Quy trình')} className="flex shrink-0 gap-2">
              {choices.map((x) => (
                <button key={x.id} role="tab" aria-selected={cur === x.id} onClick={() => setSp({ flow: x.id }, { replace: true })} title={x.hint}
                  className={cn('flex shrink-0 items-center gap-2 whitespace-nowrap rounded-lg border px-3 py-1.5 text-left text-sm transition', cur === x.id ? 'border-accent bg-accent/10 font-medium' : 'border-line bg-panel hover:border-accent/60')}>
                  <span>{x.label}</span><span className="shrink-0 rounded-md bg-panel2 px-1.5 py-0.5 text-[11px] font-normal text-muted">{x.meta}</span>
                </button>
              ))}
            </div>
          ))

  return (
    <div className="flex h-full min-h-0 flex-col overflow-hidden px-4 py-3 sm:px-6 lg:px-8">
      <header className="mb-3 flex shrink-0 items-center gap-3">
        <span className="grid size-10 shrink-0 place-items-center rounded-xl bg-accent/10 text-accent"><Icon className="size-5" /></span>
        <div className="min-w-0 flex-1">
          <h1 className="truncate text-lg font-semibold leading-tight tracking-tight">{t(a.name)}</h1>
          <p className="line-clamp-1 text-sm text-muted" title={t(form.intro || a.description)}>{t(form.intro || a.description)}</p>
        </div>
        <ModelSelect {...model} />
        <Link to="/chat" state={{ assistant: a.id }} className="flex h-9 shrink-0 items-center gap-2 rounded-lg border border-line px-3 text-sm text-muted transition hover:border-accent/60 hover:text-fg"><MessageSquare className="size-4" /><span className="hidden md:inline">{t('Trò chuyện tự do')}</span></Link>
      </header>
      <div className="flex min-h-0 flex-1 flex-col gap-3">
          <div className="grid min-h-0 flex-1 gap-x-4 gap-y-3 xl:grid-cols-[minmax(0,1fr)_20rem] xl:grid-rows-[auto_minmax(0,1fr)]">
            {flow && <FlowRunner key={a.id + flow.id} a={a} flow={flow} provider={model.active} navigation={navigation} />}
            {!flow && <div className="min-w-0 overflow-x-auto xl:col-span-2">{navigation}</div>}
            {cur === SHUFFLE && <div className="h-full min-h-0 overflow-y-auto rounded-xl border border-line bg-panel p-4 xl:col-start-1 xl:row-start-2"><h2 className="mb-1 flex items-center gap-2 text-base font-semibold"><Shuffle className="size-4 text-accent" />{t('Xáo đề thành nhiều mã')}</h2><ExamShufflePanel /></div>}
            <SidePanel a={a} />
          </div>
      </div>
    </div>
  )
}
