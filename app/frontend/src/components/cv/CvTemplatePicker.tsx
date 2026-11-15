import { useEffect, useRef, useState } from 'react'
import { Check, Eye } from 'lucide-react'
import { CV_TEMPLATES } from './templates'
import { CvDocument } from './CvDocument'
import { SAMPLE_CV } from '@/lib/cv/types'
import { cn } from '@/lib/utils'
import { t } from '@/lib/i18n.ts'
import { searchableText } from '@/lib/featureCatalog'

/** Scale the A4 document to its actual card width, including after resize. */
function CvThumbnail({ template }: { template: string }) {
  const frame = useRef<HTMLDivElement>(null)
  const [width, setWidth] = useState(0)
  useEffect(() => {
    const el = frame.current
    if (!el) return
    const observer = new ResizeObserver(([entry]) => setWidth(entry.contentRect.width))
    observer.observe(el)
    return () => observer.disconnect()
  }, [])
  return <div ref={frame} data-cv-thumbnail className="relative aspect-[794/1123] w-full overflow-hidden bg-white shadow-sm" aria-hidden="true">
    <div className="pointer-events-none absolute left-0 top-0 origin-top-left" style={{ transform: `scale(${width / 794})` }}><CvDocument template={template} data={SAMPLE_CV} /></div>
  </div>
}

function TemplatePreview({ template, onChoose, onClose }: { template: string; onChoose: () => void; onClose: () => void }) {
  const dialog = useRef<HTMLDialogElement>(null)
  useEffect(() => { dialog.current?.showModal() }, [])
  return <dialog ref={dialog} aria-label="Xem trước mẫu CV" onCancel={onClose} onClose={onClose} className="fixed inset-0 m-auto h-[95vh] w-[95vw] max-w-[880px] max-h-none rounded-xl border border-line bg-panel p-4 text-fg backdrop:bg-black/80">
    <div className="flex h-full flex-col">
      <div className="mb-3 flex shrink-0 justify-end gap-3"><button type="button" onClick={onChoose} className="rounded-lg bg-accent px-4 py-2 text-accent-fg">{t('Chọn mẫu này')}</button><button type="button" onClick={onClose} className="rounded-lg border border-line px-4 py-2">{t('Đóng')}</button></div>
      <div className="min-h-0 flex-1 overflow-auto"><div className="mx-auto w-[794px] shadow-xl"><CvDocument template={template} data={SAMPLE_CV} /></div></div>
    </div>
  </dialog>
}

export default function CvTemplatePicker({ value, onChange }: { value: string; onChange: (id: string) => void }) {
  const [expanded, setExpanded] = useState(!value)
  const choose = (id: string) => { onChange(id); setExpanded(false) }
  const [query, setQuery] = useState('')
  const [limit, setLimit] = useState(12)
  const [preview, setPreview] = useState<string | null>(null)
  const selected = CV_TEMPLATES.find((x) => x.id === value)
  const matches = CV_TEMPLATES.filter((x) => searchableText(`${x.id} ${t(x.name)} ${x.name} ${x.tagline} ${x.tags.join(' ')}`).includes(searchableText(query)))
  if (selected && !expanded) return <div className="space-y-2 rounded-lg border border-accent/40 bg-accent/5 p-3">
    <p className="text-sm font-medium">{t('Đã chọn')}: {t(selected.name)}</p><p className="text-xs text-muted">{t(selected.tagline)}</p>
    <div className="flex gap-4 text-sm text-accent"><button type="button" onClick={() => setExpanded(true)}>Đổi mẫu CV</button><button type="button" onClick={() => setPreview(selected.id)}>{t('Xem lớn')}</button></div>
    {preview && <TemplatePreview template={preview} onChoose={() => { choose(preview); setPreview(null) }} onClose={() => setPreview(null)} />}
  </div>
  return <div className="space-y-3">
    <p className="text-sm text-muted">{t('Chọn mẫu trước khi tạo CV. Nội dung trong ảnh chỉ là ví dụ, không đưa vào hồ sơ của bạn.')}</p>
    <input aria-label={t('Tìm mẫu CV')} placeholder={t('Tìm mẫu: tối giản, ATS, hiện đại…')} value={query} onChange={(e) => { setQuery(e.target.value); setLimit(12) }} className="h-10 w-full rounded-lg border border-line bg-bg px-3 text-sm" />
    {selected && <p role="status" className="text-sm text-accent">{t('Đã chọn')}: {t(selected.name)}</p>}
    <div role="radiogroup" aria-label="Mẫu CV" className="grid gap-4" style={{ gridTemplateColumns: 'repeat(auto-fill, minmax(min(100%, 240px), 1fr))' }}>
      {matches.slice(0, limit).map((item) => <div key={item.id} className={cn('group flex flex-col overflow-hidden rounded-xl border bg-bg transition hover:border-accent/60', value === item.id ? 'border-accent ring-2 ring-accent/30' : 'border-line')}>
        <button type="button" role="radio" aria-checked={value === item.id} aria-label={t(item.name)} onClick={() => choose(item.id)} className="block w-full text-left focus-visible:outline-2 focus-visible:outline-accent">
          <div className="relative border-b border-line bg-panel2 p-3">
            <CvThumbnail template={item.id} />
            {value === item.id && <span className="absolute right-5 top-5 grid size-7 place-items-center rounded-full bg-accent text-accent-fg shadow"><Check className="size-4" /></span>}
          </div>
          <div className="px-4 pt-3"><p className="text-sm font-semibold">{t(item.name)}</p><p className="mt-1 min-h-8 text-xs leading-relaxed text-muted">{t(item.tagline)}</p></div>
        </button>
        <div className="mt-auto px-4 pb-4 pt-2">
          <div className="mb-3 flex flex-wrap gap-1.5">{item.tags.map((tag) => <span key={tag} className="rounded-md bg-panel2 px-2 py-1 text-[11px] text-muted">{tag}</span>)}</div>
          <div className="flex gap-2">
            <button type="button" onClick={() => choose(item.id)} className={cn('flex h-9 flex-1 items-center justify-center gap-1.5 rounded-lg text-xs font-medium transition', value === item.id ? 'bg-accent text-accent-fg' : 'border border-accent/30 bg-accent/10 text-accent hover:bg-accent/20')}>{value === item.id && <Check className="size-3.5" />}{t(value === item.id ? 'Đã chọn' : 'Chọn mẫu này')}</button>
            <button type="button" onClick={() => setPreview(item.id)} aria-label={`${t('Xem lớn')}: ${t(item.name)}`} className="flex h-9 items-center justify-center gap-1.5 rounded-lg border border-line px-3 text-xs text-muted transition hover:border-accent/60 hover:text-fg"><Eye className="size-3.5" />{t('Xem lớn')}</button>
          </div>
        </div>
      </div>)}
    </div>
    {matches.length === 0 && <p className="text-sm text-muted">{t('Không có mẫu phù hợp.')}</p>}
    {matches.length > limit && <button type="button" onClick={() => setLimit(limit + 12)} className="text-sm text-accent underline">{t('Xem thêm mẫu')} ({matches.length - limit})</button>}
    {preview && <TemplatePreview template={preview} onChoose={() => { choose(preview); setPreview(null) }} onClose={() => setPreview(null)} />}
  </div>
}
