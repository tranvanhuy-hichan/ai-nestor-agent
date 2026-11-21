import { useEffect, useRef, useState, type ReactNode } from 'react'
import { useQuery } from '@tanstack/react-query'
import { ArrowRight, Check, CheckCircle2, Circle, Download, FileText, PartyPopper, RotateCcw, SkipForward, TriangleAlert } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { AgentMark } from '@/components/ui/AgentMark'
import { api } from '@/lib/api'
import type { Assistant, FormFlow, FormStep } from '@/lib/assistants'
import { t } from '@/lib/i18n.ts'
import type { FileEntry, PlanItem } from '@/lib/types'
import { cn } from '@/lib/utils'
import { MessageView } from '../chat/MessageView'
import { PlanCard } from '../chat/PlanCard'
import { useChat } from '../chat/useChat'
import { ResultFiles } from './ResultFiles'
import { WorkflowWaiting } from './WorkflowWaiting'
import { FieldGrid, initialValues, isFilled, storedFiles, type Files, type Values } from './fields'

type Saved = { sid: string | null; idx: number; done: string[]; starts: Record<string, number>; baseline?: Record<string, Record<string, string>> }
const EMPTY: Saved = { sid: null, idx: 0, done: [], starts: {} }
const key = (a: string, f: string) => `wf:${a}:${f}`
const load = (k: string): Saved => { try { return { ...EMPTY, ...JSON.parse(localStorage.getItem(k) || '{}') } } catch { return EMPTY } }
const draftValues = (k: string, idx: number, fields: FormStep['fields']): Values => {
  try {
    const saved = JSON.parse(localStorage.getItem(`${k}:draft:${idx}`) || '{}')
    return { ...initialValues(fields), ...Object.fromEntries(Object.entries(saved).filter(([, v]) => typeof v === 'string')) } as Values
  } catch { return initialValues(fields) }
}
const save = (k: string, v: Saved) => { try { localStorage.setItem(k, JSON.stringify(v)) } catch { /* private mode */ } }

/** Ghép câu lệnh của bước với các ô đã điền thành một yêu cầu rõ ràng cho trợ lý. */
function buildPrompt(step: FormStep, n: number, total: number, values: Values, uploaded: Record<string, string[]>): string {
  const lines = step.fields.flatMap((f) => {
    let v = f.type === 'file' ? (uploaded[f.key] ?? []).join(', ') : (values[f.key] ?? '').trim()
    if (f.type === 'cv-profile' && v) {
      const p = JSON.parse(v)
      const data = Object.fromEntries(Object.entries(p.data ?? {}).filter(([key]) => p.visible?.includes(key) && !p.skipped?.includes(key)))
      v = JSON.stringify({ template: p.template, data, skipped_sections: p.skipped, tone: p.tone })
    }
    return v ? [`- ${t(f.label)}: ${v}`] : []
  })
  return [`[${t('Bước {n}/{total}: {label}', { n, total, label: t(step.label) })}]`, t(step.task), lines.join('\n')].filter(Boolean).join('\n\n')
}

function Stepper({ steps, idx, done, vertical = false }: { steps: FormStep[]; idx: number; done: string[]; vertical?: boolean }) {
  return (
    <ol className={cn("flex shrink-0 gap-1.5", vertical && "flex-col gap-0")} aria-label={t('Các bước của quy trình')}>
      {steps.map((s, i) => {
        const isDone = done.includes(s.id), cur = i === idx
        return (
          <li key={s.id} aria-current={cur ? 'step' : undefined} className={cn('relative flex shrink-0 items-start gap-2 text-[13px]', vertical ? 'pb-4 text-xs leading-relaxed last:pb-0' : 'items-center whitespace-nowrap rounded-full border px-2.5 py-1', cur ? (vertical ? 'font-medium text-accent' : 'border-accent bg-accent/10 font-medium') : isDone ? 'border-ok/40 text-fg/80' : 'border-line text-muted')}>
            {vertical && i < steps.length - 1 && <span aria-hidden className="absolute bottom-0 left-[7px] top-4 w-px bg-line" />}
            {isDone ? <CheckCircle2 className="mt-0.5 size-4 shrink-0 text-ok" /> : cur ? <span className="mt-0.5 grid size-4 shrink-0 place-items-center rounded-full bg-accent text-[10px] font-bold text-accent-fg">{i + 1}</span> : <Circle className="mt-0.5 size-4 shrink-0" />}
            {t(s.label)}{s.optional && <span className="text-xs text-muted">({t('tùy chọn')})</span>}
          </li>
        )
      })}
    </ol>
  )
}

/** Chạy một quy trình nghiệp vụ: từng bước giao cho trợ lý trong cùng một phiên, có duyệt kết quả trước khi sang bước sau. */
export function FlowRunner({ a, flow, provider = null, navigation, renderSidebar }: { a: Assistant; flow: FormFlow; provider?: string | null; navigation?: ReactNode; renderSidebar?: (items: PlanItem[], steps: ReactNode) => ReactNode }) {
  const k = key(a.id, flow.id)
  const chat = useChat()
  const [st, setSt] = useState<Saved>(() => load(k))
  const [values, setValues] = useState<Values>(() => draftValues(k, load(k).idx, flow.steps[Math.min(load(k).idx, flow.steps.length - 1)].fields))
  const [files, setFiles] = useState<Files>({})
  const [fix, setFix] = useState('')
  const [ticks, setTicks] = useState<string[]>([])
  const [busyUp, setBusyUp] = useState(false)
  const [err, setErr] = useState('')
  const restored = useRef(false)
  const total = flow.steps.length
  const finished = st.idx >= total
  const step = flow.steps[Math.min(st.idx, total - 1)]
  const started = st.starts[step.id] !== undefined
  const phase: 'form' | 'run' | 'review' = chat.busy || busyUp ? 'run' : started ? 'review' : 'form'

  const update = (patch: Partial<Saved>) => setSt((p) => { const n = { ...p, ...patch }; save(k, n); return n })
  useEffect(() => {
    try { localStorage.setItem(`${k}:draft:${st.idx}`, JSON.stringify(values)) } catch { /* storage unavailable */ }
  }, [a.id, k, st.idx, values])

  useEffect(() => { // quay lại trang giữa chừng thì mở lại phiên đang làm dở
    if (restored.current) return
    restored.current = true
    if (st.sid) void chat.open(st.sid).catch(() => update({ sid: null, starts: {} }))
  }, [])

  const outputs = useQuery({
    queryKey: ['wf-files', st.sid, chat.filesTick, phase],
    enabled: !!st.sid && phase !== 'form',
    queryFn: () => api.get<FileEntry[]>(`/api/sessions/${st.sid}/files`).then((fs) => fs.filter((f) => !f.dir && !f.path.startsWith('uploads/')).sort((x, y) => y.mtime - x.mtime)),
  })

  const send = (text: string, attachments: string[] = []) => chat.send(text, provider, attachments, { assistant: a.id, permission: 'guarded' })

  const run = async () => {
    setBusyUp(true); setErr('')
    try {
      let sid = st.sid
      if (!sid) {
        sid = await chat.ensureSession()
        await api.put(`/api/sessions/${sid}/assistant`, { assistant: a.id })
      }
      const uploaded: Record<string, string[]> = {}
      for (const f of step.fields.filter((x) => x.type === 'file')) {
        uploaded[f.key] = storedFiles(values, f.key)
        for (const file of files[f.key] ?? []) {
          const r = await fetch(`/api/sessions/${sid}/upload?name=${encodeURIComponent(file.name)}`, { method: 'POST', headers: { 'Content-Type': 'application/octet-stream' }, body: file })
          if (!r.ok) throw new Error(`${file.name}: ${(await r.json().catch(() => ({ detail: r.statusText }))).detail}`)
          uploaded[f.key].push((await r.json()).path)
        }
      }
      const submittedValues = { ...values, ...Object.fromEntries(Object.entries(uploaded).map(([key, paths]) => [`_uploaded:${key}`, JSON.stringify(paths)])) }
      setValues(submittedValues)
      for (const f of step.fields.filter((x) => x.type === 'cv-profile')) {
        const p = JSON.parse(values[f.key] || '{}')
        if (p.data?.photo?.startsWith('data:image/')) {
          const blob = await (await fetch(p.data.photo)).blob()
          const r = await fetch(`/api/sessions/${sid}/upload?name=cv-portrait.jpg`, { method: 'POST', headers: { 'Content-Type': 'application/octet-stream' }, body: blob })
          if (!r.ok) throw new Error(t('Không tải được ảnh chân dung'))
          p.data.photo_path = (await r.json()).path
          delete p.data.photo
          p.visible = [...(p.visible ?? []), 'photo_path']
          submittedValues[f.key] = JSON.stringify(p)
        }
      }
      const existing = await api.get<FileEntry[]>(`/api/sessions/${sid}/files`)
      const baseline = Object.fromEntries(existing.filter((f) => !f.dir).map((f) => [f.path, `${f.mtime}:${f.size}`]))
      update({ sid, baseline: { ...st.baseline, [step.id]: baseline }, starts: { ...st.starts, [step.id]: chat.items.length } })
      setBusyUp(false)
      await send(buildPrompt(step, st.idx + 1, total, submittedValues, uploaded), Object.values(uploaded).flat())
    } catch (e) {
      setErr(e instanceof Error ? e.message : String(e))
      setBusyUp(false)
    }
  }

  const advance = (skipped = false) => {
    update({ idx: st.idx + 1, done: skipped ? st.done : [...st.done, step.id] })
    const next = draftValues(k, st.idx + 1, flow.steps[st.idx + 1]?.fields ?? [])
    if (a.id === 'cv-viec-lam' && values.mau_cv && flow.steps[st.idx + 1]?.fields.some((f) => f.key === 'mau_cv')) next.mau_cv = values.mau_cv
    setValues(next); setFiles({}); setFix(''); setTicks([])
  }
  const redo = () => {
    try { for (let i = 0; i < total; i++) localStorage.removeItem(`${k}:draft:${i}`) } catch { /* storage unavailable */ }
    setValues(initialValues(flow.steps[0].fields)); setFiles({}); setTicks([]); chat.reset(); setSt(EMPTY); save(k, EMPTY); restored.current = true }
  const requestFix = () => { const text = fix.trim(); if (!text) return; setFix(''); setTicks([]); void send(`${t('Cần sửa lại bước này')}: ${text}`) }

  const missing = step.fields.filter((f) => f.required && !isFilled(f, values, files))
  const ready = missing.length === 0 && (step.fields.some((f) => f.required) || step.fields.length === 0 || step.fields.some((f) => isFilled(f, values, files)))
  const stepItems = chat.items.slice(Math.min(st.starts[step.id] ?? 0, chat.items.length))
  const lastAssistant = [...stepItems].reverse().find((i) => i.kind === 'assistant')
  const expected = step.produces.filter((ext) => ['docx', 'xlsx', 'pptx', 'pdf', 'html'].includes(ext))
  const currentFiles = (outputs.data ?? []).filter((f) => !st.baseline?.[step.id] || st.baseline[step.id][f.path] !== `${f.mtime}:${f.size}`)
  const hasArtifact = expected.length === 0 || currentFiles.some((f) => f.size > 0 && expected.some((ext) => f.path.toLowerCase().endsWith(`.${ext}`)))
  const hasError = stepItems.findLastIndex((i) => i.kind === 'error') > stepItems.findLastIndex((i) => i.kind === 'assistant')
  const reviewed = step.review.every((r) => ticks.includes(r))
  const awaitingInput = stepItems.some((i) => (i.kind === 'question' && i.answer === null) || (i.kind === 'approval' && i.status === 'pending'))
  const showReview = phase === 'review' && !awaitingInput && (!!lastAssistant || currentFiles.length > 0 || hasError)
  const showConfirmation = !!lastAssistant && !hasError && hasArtifact && step.review.length > 0
  const canAdvance = showReview && !!lastAssistant && !hasError && hasArtifact && reviewed

  if (finished) return (
    <>
    <div className="flex h-full min-h-0 flex-col justify-center gap-3 overflow-y-auto xl:col-start-2 xl:row-start-1 rounded-xl border border-ok/40 bg-ok/5 p-5">
      <div className="flex shrink-0 items-center gap-4 overflow-x-auto xl:hidden">{navigation}<Stepper steps={flow.steps} idx={total} done={st.done} /></div>
      <p className="flex items-center gap-2 text-lg font-semibold"><PartyPopper className="size-5 text-ok" />{t('Hoàn tất quy trình')}</p>
      {a.form?.experience && <p className="text-sm text-muted">{t(a.form.experience.handoff)}</p>}
      <OutputList sid={st.sid} files={outputs.data} />
      <div className="flex gap-2">
        {st.sid && <a href={`/chat?session=${st.sid}`} className="inline-flex h-9 items-center gap-2 rounded-lg border border-line px-3 text-sm hover:border-accent/60">{t('Mở cuộc trò chuyện')}</a>}
        <Button onClick={redo}><RotateCcw className="size-4" />{t('Làm lần mới')}</Button>
      </div>
    </div>
    {renderSidebar?.(chat.plan, <Stepper steps={flow.steps} idx={finished ? total : st.idx} done={st.done} vertical />)}
    </>
  )

  return (
    <div className="flex h-full min-h-0 flex-col gap-3 xl:contents">
      <div className="flex min-w-0 shrink-0 items-center gap-4 overflow-x-auto pb-1 xl:hidden">{navigation}<Stepper steps={flow.steps} idx={st.idx} done={st.done} /></div>
      <section className="flex min-h-0 min-w-0 flex-1 flex-col xl:col-start-2 xl:row-start-1 rounded-xl border border-line bg-panel p-4">
        <header className="mb-3 shrink-0">
          <h2 className="text-base font-semibold">{t('Bước {n}/{total}: {label}', { n: st.idx + 1, total, label: t(step.label) })}</h2>
          <p className="mt-0.5 line-clamp-2 text-sm text-muted" title={t(step.goal)}>{t(step.goal)}</p>
        </header>

        {phase === 'form' && (
          <form onSubmit={(e) => { e.preventDefault(); if (ready) void run() }} className="flex min-h-0 flex-1 flex-col gap-3">
            <div className="min-h-0 flex-1 space-y-4 overflow-y-auto pr-1">
              {st.idx === 0 && a.form?.experience && <div className="rounded-lg border border-accent/20 bg-accent/5 p-3 text-sm"><p className="font-medium">{t(a.form.experience.title)}</p><ul className="mt-2 list-disc space-y-1 pl-4 text-xs text-muted">{a.form.experience.checks.map((c) => <li key={c}>{t(c)}</li>)}</ul><p className="mt-2 text-xs text-muted">{t(a.form.experience.handoff)}</p></div>}
              <p className="text-xs text-muted">{t('Bản nháp được lưu trên trình duyệt. File đã tải lên sẽ được dùng lại trong phiên này.')}</p>
              {step.fields.length > 0 && <FieldGrid fields={step.fields} values={values} files={files} setValue={(kk, v) => setValues((p) => ({ ...p, [kk]: v }))} setFiles={(kk, v) => setFiles((p) => ({ ...p, [kk]: v }))} />}
              {step.fields.length === 0 && <p className="text-sm text-muted">{t('Bước này dùng kết quả của các bước trước, không cần nhập thêm.')}</p>}
              {err && <div role="alert" className="flex items-start gap-2 rounded-xl border border-bad/40 bg-bad/10 px-4 py-3 text-sm"><TriangleAlert className="mt-0.5 size-4 shrink-0 text-bad" /><span>{err}</span></div>}
            </div>
            <div className="flex shrink-0 flex-wrap items-center gap-3 border-t border-line pt-3">
              <Button type="submit" variant="primary" className="h-10 px-6" disabled={!ready}>{step.submit ? t(step.submit) : t('Chạy bước này')}<ArrowRight className="size-4" /></Button>
              {step.optional && <Button type="button" onClick={() => advance(true)}><SkipForward className="size-4" />{t('Bỏ qua bước này')}</Button>}
              {!ready && missing.length > 0 && <span className="min-w-0 truncate text-xs text-muted">{t('Cần điền: {n}', { n: missing.map((f) => t(f.label)).join(', ') })}</span>}
            </div>
          </form>
        )}

        {phase !== 'form' && (
          <div className="flex min-h-0 flex-1 flex-col gap-3">
            <div className="min-h-0 flex-1 space-y-3 overflow-y-auto rounded-lg border border-line bg-bg p-3">
              {stepItems.filter((i) => i.kind !== 'user').map((it) => (
                <div key={it.key} className="relative min-h-9">
                {it.kind !== 'assistant' && <AgentMark size="sm" className="absolute left-0 top-0" />}
                <MessageView item={it} sid={chat.sessionId} onDecide={(aid, ok) => void chat.decide(aid, ok)} onAnswer={(q, ans) => void chat.answer(q, ans)} onUndo={() => void chat.undo()}
                  onOpenFile={(path) => window.open(`/api/sessions/${st.sid}/file?path=${encodeURIComponent(path)}&raw=true`, '_blank')} canAct={!chat.busy} isLastUser={false} isLastAssistant={it === lastAssistant} />
                </div>
              ))}
              {phase === 'run' && <WorkflowWaiting status={chat.status} label={step.label} compact={stepItems.some((i) => ['assistant', 'thinking', 'tool', 'question', 'approval'].includes(i.kind))} />}
            </div>
            {chat.plan.length > 0 && <div className="max-h-48 shrink-0 overflow-y-auto xl:hidden"><PlanCard items={chat.plan} /></div>}
            {showReview && (
              <div className="max-h-[45%] shrink-0 space-y-2 overflow-y-auto rounded-lg border border-line bg-bg/50 p-2.5">
                <div className={cn("grid items-start gap-2", currentFiles.length > 0 && showConfirmation && "sm:grid-cols-2")}>
                  {currentFiles.length > 0 && <details open className="min-w-0 rounded-md border border-line bg-panel px-2.5 py-2"><summary className="cursor-pointer text-xs font-medium"><span className="ml-1">{t('Kết quả của bước này')}</span><span className="ml-2 text-[10px] text-muted">{t('{n} file', { n: currentFiles.length })}</span></summary><div className="mt-2">
                    <ResultFiles sid={st.sid} files={currentFiles} />
                  </div></details>}
                  {showConfirmation && <details className="min-w-0 rounded-md border border-line bg-panel px-2.5 py-2"><summary className="cursor-pointer text-xs font-medium"><span className="ml-1">{t('Xác nhận trước khi tiếp tục')}</span><span className={cn('ml-2 text-[10px] tabular-nums', reviewed ? 'text-ok' : 'text-muted')}>{ticks.length}/{step.review.length}</span></summary><div className="mt-2">
                    <ul className="space-y-2">{step.review.map((r) => <li key={r}><label className={cn('flex cursor-pointer items-start gap-2.5 rounded-lg border p-2.5 text-xs leading-relaxed transition', ticks.includes(r) ? 'border-ok/25 bg-ok/5' : 'border-line bg-panel')}><input type="checkbox" checked={ticks.includes(r)} onChange={() => setTicks((p) => p.includes(r) ? p.filter((x) => x !== r) : [...p,r])} className="mt-0.5 size-3.5 shrink-0 accent-[var(--accent)]" /><span>{t(r)}</span></label></li>)}</ul>
                  </div></details>}
                </div>
                {!hasArtifact && <p role="status" className="text-[11px] text-bad">{t('Chưa có file đầu ra mới của bước này. Yêu cầu trợ lý tạo đủ file trước khi duyệt.')}</p>}
                <details className="rounded-md border border-line bg-panel px-2.5 py-2"><summary className="cursor-pointer text-xs text-muted">{t('Yêu cầu chỉnh sửa')}</summary>
                <div className="mt-2 flex flex-col gap-2 sm:flex-row">
                  <input value={fix} onChange={(e) => setFix(e.target.value)} onKeyDown={(e) => { if (e.key === 'Enter' && fix.trim()) requestFix() }} placeholder={t('Ví dụ: bổ sung phân tích, sửa bố cục hoặc làm rõ một mục…')} aria-label={t('Yêu cầu sửa')} className="h-10 min-w-0 flex-1 rounded-md bg-transparent px-2 text-sm outline-none" />
                  <Button disabled={!fix.trim()} onClick={requestFix} className="shrink-0">{t('Yêu cầu sửa')}</Button>
                </div></details>
                <div className="flex flex-wrap items-center justify-between gap-2 pt-1">
                  <div className="flex flex-wrap gap-x-4 gap-y-2 text-xs"><button onClick={() => { const starts = { ...st.starts }; delete starts[step.id]; update({ starts }); setTicks([]); setErr('') }} className="text-muted hover:text-accent">{t('Chỉnh đầu vào và chạy lại')}</button><button onClick={redo} className="text-muted hover:text-fg">{t('Làm lại từ đầu')}</button></div>
                  <Button variant="primary" className="h-8 shrink-0 px-3 text-xs" disabled={!canAdvance} onClick={() => advance()}><Check className="size-4" />{st.idx + 1 >= total ? t('Duyệt và hoàn tất') : t('Duyệt, sang bước tiếp')}</Button>
                </div>
              </div>
            )}
          </div>
        )}
      </section>
      {renderSidebar?.(chat.plan, <Stepper steps={flow.steps} idx={finished ? total : st.idx} done={st.done} vertical />)}
    </div>
  )
}

function OutputList({ sid, files, compact = false }: { sid: string | null; files?: FileEntry[]; compact?: boolean }) {
  if (!sid || !files?.length) return null
  if (compact) return (
    <div className="flex flex-wrap items-center gap-2">
      <span className="text-sm font-medium">{t('File đã tạo')}:</span>
      {files.map((f) => {
        const name = f.path.split('/').pop() ?? f.path
        return <a key={f.path} href={`/api/sessions/${sid}/file?path=${encodeURIComponent(f.path)}&raw=true`} download={name} className="flex max-w-[16rem] items-center gap-1.5 rounded-md border border-line bg-bg px-2 py-1 text-xs text-accent hover:border-accent/60"><Download className="size-3.5 shrink-0" /><span className="truncate">{name}</span></a>
      })}
    </div>
  )
  return (
    <div>
      <p className="mb-1.5 text-sm font-medium">{t('File đã tạo')}</p>
      <ul className="divide-y divide-line/70 overflow-hidden rounded-lg border border-line bg-bg">
        {files.map((f) => {
          const name = f.path.split('/').pop() ?? f.path
          return (
            <li key={f.path} className="flex items-center gap-3 px-3 py-2 text-sm">
              <FileText className="size-4 shrink-0 text-accent" /><span className="min-w-0 flex-1 truncate">{name}</span>
              <a href={`/api/sessions/${sid}/file?path=${encodeURIComponent(f.path)}`} target="_blank" rel="noopener noreferrer" className="text-xs text-accent hover:underline">{t('Mở file')}</a>
              <a href={`/api/sessions/${sid}/file?path=${encodeURIComponent(f.path)}&raw=true`} download={name} className="flex items-center gap-1 rounded-md px-2 py-1 text-xs text-accent hover:bg-panel2"><Download className="size-3.5" />{t('Tải về')}</a>
            </li>
          )
        })}
      </ul>
    </div>
  )
}
