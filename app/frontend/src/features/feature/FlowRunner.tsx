import { useEffect, useRef, useState, type ReactNode } from 'react'
import { useQuery } from '@tanstack/react-query'
import { ArrowRight, Check, CheckCircle2, Circle, Download, FileText, LoaderCircle, PartyPopper, RotateCcw, SkipForward, TriangleAlert } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { api } from '@/lib/api'
import type { Assistant, FormFlow, FormStep } from '@/lib/assistants'
import { t } from '@/lib/i18n.ts'
import type { FileEntry } from '@/lib/types'
import { cn } from '@/lib/utils'
import { MessageView } from '../chat/MessageView'
import { PlanCard } from '../chat/PlanCard'
import { useChat } from '../chat/useChat'
import { FieldGrid, initialValues, isFilled, type Files, type Values } from './fields'

type Saved = { sid: string | null; idx: number; done: string[]; starts: Record<string, number> }
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

function Stepper({ steps, idx, done }: { steps: FormStep[]; idx: number; done: string[] }) {
  return (
    <ol className="flex shrink-0 gap-1.5" aria-label={t('Các bước của quy trình')}>
      {steps.map((s, i) => {
        const isDone = done.includes(s.id), cur = i === idx
        return (
          <li key={s.id} aria-current={cur ? 'step' : undefined} className={cn('flex shrink-0 items-center gap-2 whitespace-nowrap rounded-full border px-2.5 py-1 text-[13px]', cur ? 'border-accent bg-accent/10 font-medium' : isDone ? 'border-ok/40 text-fg/80' : 'border-line text-muted')}>
            {isDone ? <CheckCircle2 className="size-4 text-ok" /> : cur ? <span className="grid size-4 place-items-center rounded-full bg-accent text-[10px] font-bold text-accent-fg">{i + 1}</span> : <Circle className="size-4" />}
            {t(s.label)}{s.optional && <span className="text-xs text-muted">({t('tùy chọn')})</span>}
          </li>
        )
      })}
    </ol>
  )
}

/** Chạy một quy trình nghiệp vụ: từng bước giao cho trợ lý trong cùng một phiên, có duyệt kết quả trước khi sang bước sau. */
export function FlowRunner({ a, flow, provider = null, navigation }: { a: Assistant; flow: FormFlow; provider?: string | null; navigation?: ReactNode }) {
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
    if (a.id === 'cv-viec-lam') {
      try { localStorage.setItem(`${k}:draft:${st.idx}`, JSON.stringify(values)) } catch { /* storage unavailable */ }
    }
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
        uploaded[f.key] = []
        for (const file of files[f.key] ?? []) {
          const r = await fetch(`/api/sessions/${sid}/upload?name=${encodeURIComponent(file.name)}`, { method: 'POST', headers: { 'Content-Type': 'application/octet-stream' }, body: file })
          if (!r.ok) throw new Error(`${file.name}: ${(await r.json().catch(() => ({ detail: r.statusText }))).detail}`)
          uploaded[f.key].push((await r.json()).path)
        }
      }
      const submittedValues = { ...values }
      for (const f of step.fields.filter((x) => x.type === 'cv-profile')) {
        const p = JSON.parse(values[f.key] || '{}')
        if (p.data?.photo?.startsWith('data:image/')) {
          const blob = await (await fetch(p.data.photo)).blob()
          const r = await fetch(`/api/sessions/${sid}/upload?name=cv-portrait.jpg`, { method: 'POST', headers: { 'Content-Type': 'application/octet-stream' }, body: blob })
          if (!r.ok) throw new Error('Không tải được ảnh chân dung')
          p.data.photo_path = (await r.json()).path
          delete p.data.photo
          p.visible = [...(p.visible ?? []), 'photo_path']
          submittedValues[f.key] = JSON.stringify(p)
        }
      }
      update({ sid, starts: { ...st.starts, [step.id]: chat.items.length } })
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

  if (finished) return (
    <div className="flex h-full min-h-0 flex-col justify-center gap-3 overflow-y-auto xl:col-start-1 xl:row-start-2 rounded-xl border border-ok/40 bg-ok/5 p-5">
      <div className="flex shrink-0 items-center gap-4 overflow-x-auto">{navigation}<Stepper steps={flow.steps} idx={total} done={st.done} /></div>
      <p className="flex items-center gap-2 text-lg font-semibold"><PartyPopper className="size-5 text-ok" />{t('Hoàn tất quy trình')}</p>
      <OutputList sid={st.sid} files={outputs.data} />
      <div className="flex gap-2">
        {st.sid && <a href={`/chat?session=${st.sid}`} className="inline-flex h-9 items-center gap-2 rounded-lg border border-line px-3 text-sm hover:border-accent/60">{t('Mở cuộc trò chuyện')}</a>}
        <Button onClick={redo}><RotateCcw className="size-4" />{t('Làm lần mới')}</Button>
      </div>
    </div>
  )

  return (
    <div className="flex h-full min-h-0 flex-col gap-3 xl:contents">
      <div className="flex min-w-0 shrink-0 items-center gap-4 overflow-x-auto pb-1 xl:col-span-2 xl:row-start-1">{navigation}<Stepper steps={flow.steps} idx={st.idx} done={st.done} /></div>
      <section className="flex min-h-0 min-w-0 flex-1 flex-col xl:col-start-1 xl:row-start-2 rounded-xl border border-line bg-panel p-4">
        <header className="mb-3 shrink-0">
          <h2 className="text-base font-semibold">{t('Bước {n}/{total}: {label}', { n: st.idx + 1, total, label: t(step.label) })}</h2>
          <p className="mt-0.5 line-clamp-2 text-sm text-muted" title={t(step.goal)}>{t(step.goal)}</p>
        </header>

        {phase === 'form' && (
          <form onSubmit={(e) => { e.preventDefault(); if (ready) void run() }} className="flex min-h-0 flex-1 flex-col gap-3">
            <div className="min-h-0 flex-1 space-y-4 overflow-y-auto pr-1">
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
                <MessageView key={it.key} item={it} sid={chat.sessionId} onDecide={(aid, ok) => void chat.decide(aid, ok)} onAnswer={(q, ans) => void chat.answer(q, ans)} onUndo={() => void chat.undo()}
                  onOpenFile={(path) => window.open(`/api/sessions/${st.sid}/file?path=${encodeURIComponent(path)}&raw=true`, '_blank')} canAct={!chat.busy} isLastUser={false} isLastAssistant={it === lastAssistant} />
              ))}
              {phase === 'run' && <p className="flex items-center gap-2 text-xs text-muted" role="status"><LoaderCircle className="size-3.5 animate-spin text-accent" />{chat.status || t('Đang làm…')}</p>}
            </div>
            {chat.plan.length > 0 && <div className="max-h-28 shrink-0 overflow-y-auto"><PlanCard items={chat.plan} /></div>}
            {phase === 'review' && (
              <div className="shrink-0 space-y-2.5 border-t border-line pt-3">
                <OutputList sid={st.sid} files={outputs.data} compact />
                <ul className="flex flex-wrap gap-x-5 gap-y-1">
                  {step.review.map((r) => (
                    <li key={r}><label className="flex cursor-pointer items-start gap-2 text-sm"><input type="checkbox" checked={ticks.includes(r)} onChange={() => setTicks((p) => (p.includes(r) ? p.filter((x) => x !== r) : [...p, r]))} className="mt-0.5 size-4 accent-[var(--color-accent,#6366f1)]" /><span className={cn(ticks.includes(r) && 'text-fg/70 line-through')}>{t(r)}</span></label></li>
                  ))}
                </ul>
                <div className="flex flex-wrap items-center gap-2">
                  <Button variant="primary" className="h-10 px-5" onClick={() => advance()}><Check className="size-4" />{st.idx + 1 >= total ? t('Duyệt và hoàn tất') : t('Duyệt, sang bước tiếp')}</Button>
                  <input value={fix} onChange={(e) => setFix(e.target.value)} onKeyDown={(e) => { if (e.key === 'Enter' && fix.trim()) requestFix() }} placeholder={t('Chưa đạt? Nói rõ cần sửa gì, trợ lý sẽ làm lại bước này')} aria-label={t('Yêu cầu sửa')} className="h-10 min-w-[12rem] flex-1 rounded-lg border border-line bg-bg px-3 text-sm outline-none focus:border-accent" />
                  <Button disabled={!fix.trim()} onClick={requestFix}>{t('Yêu cầu sửa')}</Button>
                  <button onClick={redo} className="text-xs text-muted hover:text-fg">{t('Làm lại từ đầu')}</button>
                </div>
              </div>
            )}
          </div>
        )}
      </section>
    </div>
  )
}

function OutputList({ sid, files, compact = false }: { sid: string | null; files?: FileEntry[]; compact?: boolean }) {
  if (!sid || !files?.length) return null
  if (compact) return (
    <div className="flex flex-wrap items-center gap-2">
      <span className="text-sm font-medium">{t('File đã tạo')}:</span>
      {files.slice(0, 6).map((f) => {
        const name = f.path.split('/').pop() ?? f.path
        return <a key={f.path} href={`/api/sessions/${sid}/file?path=${encodeURIComponent(f.path)}&raw=true`} download={name} className="flex max-w-[16rem] items-center gap-1.5 rounded-md border border-line bg-bg px-2 py-1 text-xs text-accent hover:border-accent/60"><Download className="size-3.5 shrink-0" /><span className="truncate">{name}</span></a>
      })}
    </div>
  )
  return (
    <div>
      <p className="mb-1.5 text-sm font-medium">{t('File đã tạo')}</p>
      <ul className="divide-y divide-line/70 overflow-hidden rounded-lg border border-line bg-bg">
        {files.slice(0, 12).map((f) => {
          const name = f.path.split('/').pop() ?? f.path
          return (
            <li key={f.path} className="flex items-center gap-3 px-3 py-2 text-sm">
              <FileText className="size-4 shrink-0 text-accent" /><span className="min-w-0 flex-1 truncate">{name}</span>
              <a href={`/api/sessions/${sid}/file?path=${encodeURIComponent(f.path)}&raw=true`} download={name} className="flex items-center gap-1 rounded-md px-2 py-1 text-xs text-accent hover:bg-panel2"><Download className="size-3.5" />{t('Tải về')}</a>
            </li>
          )
        })}
      </ul>
    </div>
  )
}
