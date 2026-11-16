import { useRef, useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { Download, FileArchive, FileText, KeyRound, Minus, Plus, Shuffle, TriangleAlert, Upload, X } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { t } from '@/lib/i18n.ts'
import { cn } from '@/lib/utils'

type OutFile = { name: string; size: number; url: string }
type Result = { id: string; summary: { questions: number; mcq: number; sections: number; fixed: number }; files: OutFile[]; answer_key: OutFile | null; zip: OutFile | null; warnings: string[] }

const kb = (n: number) => (n >= 1048576 ? `${(n / 1048576).toFixed(1)} MB` : `${Math.max(1, Math.round(n / 1024))} KB`)

async function shuffle(f: { file: File; versions: number; start: number; keep: boolean; strip: boolean; answers: string }): Promise<Result> {
  const fd = new FormData()
  fd.append('file', f.file)
  fd.append('versions', String(f.versions))
  fd.append('start_code', String(f.start))
  fd.append('keep_order', String(f.keep))
  fd.append('strip_marks', String(f.strip))
  if (f.answers.trim()) fd.append('answers', f.answers.trim())
  const r = await fetch('/api/exam/shuffle', { method: 'POST', body: fd })
  if (r.status === 404) throw new Error(t('Máy chủ chưa hỗ trợ tính năng này, hãy khởi động lại Nestor.'))
  if (r.status === 401) { window.dispatchEvent(new Event('auth-required')); throw new Error(t('Cần đăng nhập lại.')) }
  const body = await r.json().catch(() => null)
  if (!r.ok) throw new Error(typeof body?.detail === 'string' ? body.detail : t('Không xáo được đề. Hãy kiểm tra file đúng định dạng .docx rồi thử lại.'))
  return body as Result
}

function FileRow({ f, icon: Icon, hl }: { f: OutFile; icon: typeof FileText; hl?: boolean }) {
  return (
    <li className={cn('flex items-center gap-3 px-4 py-2.5 text-sm', hl && 'bg-accent/10')}>
      <Icon className="size-4 shrink-0 text-accent" />
      <span className="min-w-0 flex-1 truncate font-medium">{f.name}</span>
      <span className="hidden text-xs text-fg/70 sm:block">{kb(f.size)}</span>
      <a href={f.url} download={f.name} className="flex items-center gap-1 rounded-lg px-2 py-1 text-xs text-accent hover:bg-panel2"><Download className="size-3.5" />{t('Tải về')}</a>
    </li>
  )
}

export function ExamShufflePanel() {
  const input = useRef<HTMLInputElement>(null)
  const [file, setFile] = useState<File | null>(null)
  const [over, setOver] = useState(false)
  const [versions, setVersions] = useState(4)
  const [start, setStart] = useState(101)
  const [keep, setKeep] = useState(false)
  const [strip, setStrip] = useState(true)
  const [manual, setManual] = useState(false)
  const [answers, setAnswers] = useState('')
  const [badFile, setBadFile] = useState('')
  const run = useMutation({ mutationFn: shuffle })

  const pick = (f?: File | null) => {
    run.reset()
    if (!f) return
    if (!/\.docx$/i.test(f.name)) { setFile(null); setBadFile(t('Chỉ nhận file Word .docx. Nếu đề là .doc hoặc PDF, hãy mở bằng Word và "Lưu thành" .docx trước.')); return }
    setBadFile('')
    setFile(f)
  }
  const r = run.data

  return (
    <div>
      <p className="mb-4 text-sm text-muted">{t('Tải một đề gốc lên, nhận lại nhiều mã đề đã xáo trộn câu hỏi và thứ tự đáp án, giữ nguyên định dạng của đề gốc.')}</p>
      <div className="space-y-4">
        <div role="button" tabIndex={0} aria-label={t('Chọn file đề thi')}
          onClick={() => input.current?.click()} onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') input.current?.click() }}
          onDragOver={(e) => { e.preventDefault(); setOver(true) }} onDragLeave={() => setOver(false)}
          onDrop={(e) => { e.preventDefault(); setOver(false); pick(e.dataTransfer.files[0]) }}
          className={cn('flex cursor-pointer flex-col items-center gap-2 rounded-2xl border-2 border-dashed px-6 py-10 text-center transition', over ? 'border-accent bg-accent/10' : 'border-line bg-panel hover:border-accent/60')}>
          <input ref={input} type="file" accept=".docx" className="hidden" onChange={(e) => { pick(e.target.files?.[0]); e.target.value = '' }} />
          {file ? (
            <>
              <FileText className="size-9 text-accent" />
              <p className="font-medium">{file.name}</p>
              <p className="text-xs text-fg/70">{kb(file.size)} · {t('Bấm để chọn file khác')}</p>
            </>
          ) : (
            <>
              <Upload className="size-9 text-accent" />
              <p className="text-base font-medium">{t('Kéo thả file đề thi (.docx) vào đây')}</p>
              <p className="text-sm text-fg/70">{t('hoặc bấm để chọn file trên máy')}</p>
            </>
          )}
        </div>
        {badFile && <p className="flex items-start gap-2 rounded-lg border border-bad/40 bg-bad/10 px-3 py-2 text-sm"><X className="mt-0.5 size-4 shrink-0 text-bad" />{badFile}</p>}

        <section className="space-y-4 rounded-xl border border-line bg-panel p-4">
          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <p className="mb-1.5 text-sm font-medium">{t('Số mã đề')}</p>
              <div className="flex items-center gap-2">
                <button type="button" aria-label={t('Giảm')} disabled={versions <= 2} onClick={() => setVersions(versions - 1)} className="grid size-9 place-items-center rounded-lg border border-line hover:bg-panel2 disabled:opacity-40"><Minus className="size-4" /></button>
                <span className="w-10 text-center text-lg font-semibold">{versions}</span>
                <button type="button" aria-label={t('Tăng')} disabled={versions >= 12} onClick={() => setVersions(versions + 1)} className="grid size-9 place-items-center rounded-lg border border-line hover:bg-panel2 disabled:opacity-40"><Plus className="size-4" /></button>
              </div>
            </div>
            <div>
              <label htmlFor="start-code" className="mb-1.5 block text-sm font-medium">{t('Mã đề bắt đầu từ')}</label>
              <input id="start-code" type="number" min={1} max={9999} value={start} onChange={(e) => setStart(Math.max(1, Number(e.target.value) || 1))} className="h-9 w-28 rounded-lg border border-line bg-bg px-3 text-sm outline-none focus:border-accent" />
            </div>
          </div>
          <label className="flex items-start gap-2.5 text-sm"><input type="checkbox" checked={keep} onChange={(e) => setKeep(e.target.checked)} className="mt-0.5 size-4 accent-[var(--color-accent,#6366f1)]" /><span>{t('Giữ nguyên thứ tự câu hỏi')}<span className="block text-xs text-fg/70">{t('Chỉ xáo thứ tự đáp án A, B, C, D trong từng câu.')}</span></span></label>
          <label className="flex items-start gap-2.5 text-sm"><input type="checkbox" checked={strip} onChange={(e) => setStrip(e.target.checked)} className="mt-0.5 size-4 accent-[var(--color-accent,#6366f1)]" /><span>{t('Xóa dấu đánh dấu đáp án trong đề phát cho học sinh')}<span className="block text-xs text-fg/70">{t('Gạch chân, tô đỏ hoặc tô màu đáp án đúng sẽ được bỏ khỏi các mã đề; đáp án nằm riêng trong bảng đáp án.')}</span></span></label>
          {manual ? (
            <div>
              <label htmlFor="answers" className="mb-1.5 block text-sm font-medium">{t('Đáp án thủ công')}</label>
              <textarea id="answers" rows={3} value={answers} onChange={(e) => setAnswers(e.target.value)} placeholder="1A 2C 3B 4D …" className="w-full rounded-lg border border-line bg-bg px-3 py-2 font-mono text-sm outline-none focus:border-accent" />
              <p className="mt-1 text-xs text-fg/70">{t('Mỗi câu một cặp số câu và chữ cái đáp án đúng, cách nhau bằng dấu cách, theo đề gốc.')}</p>
            </div>
          ) : <button type="button" onClick={() => setManual(true)} className="text-sm text-accent hover:underline">{t('Đề gốc không đánh dấu đáp án?')}</button>}
        </section>

        <div className="rounded-xl border border-line bg-panel px-4 py-3 text-sm text-fg/80">
          <p className="mb-1 font-medium text-fg">{t('Đề cần có dạng')}</p>
          <p>{t('Mỗi câu bắt đầu bằng "Câu 1.", "Câu 2."… và có các đáp án A. B. C. D. Đáp án đúng được đánh dấu bằng gạch chân, chữ đỏ hoặc tô màu trong đề gốc. Phần tự luận được giữ nguyên vị trí.')}</p>
        </div>

        <Button variant="primary" className="h-11 px-6 text-base" disabled={!file} loading={run.isPending} onClick={() => file && run.mutate({ file, versions, start, keep, strip, answers })}>
          <Shuffle className="size-4" />{run.isPending ? t('Đang xáo đề…') : t('Xáo đề')}
        </Button>

        {run.isError && (
          <div role="alert" className="flex items-start gap-2 rounded-xl border border-bad/40 bg-bad/10 px-4 py-3 text-sm">
            <TriangleAlert className="mt-0.5 size-4 shrink-0 text-bad" />
            <div><p className="font-medium">{t('Chưa xáo được đề')}</p><p className="mt-0.5 text-fg/80">{(run.error as Error).message}</p></div>
          </div>
        )}

        {r && (
          <section className="space-y-3" aria-live="polite">
            <p className="text-sm">{t('Đã tạo {n} mã đề từ {q} câu hỏi ({m} câu trắc nghiệm, {s} phần).', { n: r.files.length, q: r.summary.questions, m: r.summary.mcq, s: r.summary.sections })}</p>
            {r.warnings.length > 0 && (
              <div className="rounded-xl border border-warn/50 bg-warn/10 px-4 py-3 text-sm">
                <p className="mb-1 flex items-center gap-2 font-medium"><TriangleAlert className="size-4 text-warn" />{t('Lưu ý khi dùng')}</p>
                <ul className="list-disc space-y-0.5 pl-5 text-fg/85">{r.warnings.map((w) => <li key={w}>{w}</li>)}</ul>
              </div>
            )}
            <ul className="divide-y divide-line/70 overflow-hidden rounded-xl border border-line bg-panel">
              {r.answer_key && <FileRow f={r.answer_key} icon={KeyRound} hl />}
              {r.files.map((f) => <FileRow key={f.name} f={f} icon={FileText} />)}
            </ul>
            {r.zip && <a href={r.zip.url} download={r.zip.name} className="inline-flex h-10 items-center gap-2 rounded-lg bg-accent px-4 text-sm font-medium text-accent-fg hover:brightness-110"><FileArchive className="size-4" />{t('Tải tất cả (.zip)')}</a>}
          </section>
        )}
      </div>
    </div>
  )
}
