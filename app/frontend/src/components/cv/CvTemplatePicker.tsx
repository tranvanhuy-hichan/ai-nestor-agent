import { useEffect, useRef, useState } from 'react'
import { CV_TEMPLATES } from './templates'
import { CvDocument } from './CvDocument'
import { SAMPLE_CV } from '@/lib/cv/types'
import { cn } from '@/lib/utils'
import { t } from '@/lib/i18n.ts'
import { searchableText } from '@/lib/featureCatalog'

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
    <div role="radiogroup" aria-label="Mẫu CV" className="grid grid-cols-2 gap-3 lg:grid-cols-3">
      {matches.slice(0, limit).map((item) => <div key={item.id} className={cn('overflow-hidden rounded-xl border bg-bg', value === item.id ? 'border-accent ring-1 ring-accent' : 'border-line')}>
        <button type="button" role="radio" aria-checked={value === item.id} aria-label={t(item.name)} onClick={() => choose(item.id)} className="block w-full text-left focus-visible:outline-2 focus-visible:outline-accent">
          <div className="relative h-[240px] overflow-hidden bg-white" aria-hidden="true">
            <div className="pointer-events-none absolute left-1/2 top-0 origin-top-left" style={{ transform: 'scale(.214)', marginLeft: -85 }}><CvDocument template={item.id} data={SAMPLE_CV} /></div>
          </div>
          <div className="p-3"><p className="text-sm font-medium">{value === item.id ? '✓ ' : ''}{t(item.name)}</p><p className="mt-1 text-xs text-muted">{t(item.tagline)}</p><p className="mt-1 text-xs text-accent">{item.tags.join(' · ')}</p></div>
        </button>
        <button type="button" onClick={() => setPreview(item.id)} className="mb-3 ml-3 text-xs text-accent underline">{t('Xem lớn')}</button>
      </div>)}
    </div>
    {matches.length === 0 && <p className="text-sm text-muted">{t('Không có mẫu phù hợp.')}</p>}
    {matches.length > limit && <button type="button" onClick={() => setLimit(limit + 12)} className="text-sm text-accent underline">{t('Xem thêm mẫu')} ({matches.length - limit})</button>}
    {preview && <TemplatePreview template={preview} onChoose={() => { choose(preview); setPreview(null) }} onClose={() => setPreview(null)} />}
  </div>
}
