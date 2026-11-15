import { useEffect, useId, useRef, useState } from 'react'
import { Camera, Check, ImagePlus, LoaderCircle, Trash2, Upload } from 'lucide-react'
import { cn } from '@/lib/utils'
import { t } from '@/lib/i18n.ts'

export default function CvPhotoUpload({ value, onChange }: { value: string; onChange: (photo: string) => void }) {
  const input = useRef<HTMLInputElement>(null)
  const sequence = useRef(0)
  const dragDepth = useRef(0)
  const change = useRef(onChange)
  change.current = onChange
  const id = useId()
  const [dragging, setDragging] = useState(false)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  useEffect(() => () => { sequence.current++ }, [])

  const load = async (file?: File) => {
    if (!file) return
    const request = ++sequence.current
    setError('')
    if (file.size > 2_000_000 || !['image/jpeg', 'image/png', 'image/webp'].includes(file.type)) {
      setBusy(false)
      setError(t('Chọn ảnh JPEG, PNG hoặc WebP dưới 2 MB'))
      return
    }
    setBusy(true)
    const url = URL.createObjectURL(file)
    try {
      const image = new Image()
      image.src = url
      await image.decode()
      const ratio = Math.min(1, 512 / Math.max(image.naturalWidth, image.naturalHeight))
      const canvas = document.createElement('canvas')
      canvas.width = Math.max(1, Math.round(image.naturalWidth * ratio))
      canvas.height = Math.max(1, Math.round(image.naturalHeight * ratio))
      const context = canvas.getContext('2d')!
      context.fillStyle = '#fff'
      context.fillRect(0, 0, canvas.width, canvas.height)
      context.drawImage(image, 0, 0, canvas.width, canvas.height)
      if (request === sequence.current) change.current(canvas.toDataURL('image/jpeg', 0.85))
    } catch {
      if (request === sequence.current) setError(t('Không đọc được ảnh, vui lòng chọn ảnh khác'))
    } finally {
      URL.revokeObjectURL(url)
      if (request === sequence.current) setBusy(false)
    }
  }
  const remove = () => { sequence.current++; setBusy(false); setError(''); change.current(''); if (input.current) input.current.value = '' }

  return <section aria-labelledby={`${id}-label`} className="space-y-2">
    <div className="flex items-center gap-2"><h3 id={`${id}-label`} className="text-[13px] font-medium text-fg/85">{t('Ảnh chân dung')}</h3><span className="rounded-full bg-panel2 px-2 py-0.5 text-[11px] text-muted">{t('Không bắt buộc')}</span></div>
    <div onDragEnter={(e) => { e.preventDefault(); dragDepth.current++; setDragging(true) }} onDragOver={(e) => { e.preventDefault(); e.dataTransfer.dropEffect = 'copy' }} onDragLeave={(e) => { e.preventDefault(); if (--dragDepth.current <= 0) { dragDepth.current = 0; setDragging(false) } }} onDrop={(e) => { e.preventDefault(); dragDepth.current = 0; setDragging(false); void load(e.dataTransfer.files[0]) }}
      className={cn('flex flex-col items-start gap-4 rounded-xl border border-dashed p-4 transition sm:flex-row sm:items-center', dragging ? 'border-accent bg-accent/10 ring-2 ring-accent/20' : error ? 'border-bad/50 bg-bad/5' : 'border-fg/20 bg-bg hover:border-accent/50')}>
      <input ref={input} type="file" accept="image/jpeg,image/png,image/webp" aria-label={t('Chọn ảnh chân dung')} className="hidden" onChange={(e) => { void load(e.target.files?.[0]); e.target.value = '' }} />
      <button type="button" onClick={() => input.current?.click()} aria-label={t(value ? 'Đổi ảnh chân dung' : 'Chọn ảnh chân dung')} aria-describedby={`${id}-hint`} className="group relative grid h-28 w-24 shrink-0 place-items-center overflow-hidden rounded-lg border border-line bg-panel2 outline-none focus-visible:ring-2 focus-visible:ring-accent">
        {value ? <><img src={value} alt={t('Ảnh chân dung đã chọn')} className="size-full object-cover" /><span className="absolute inset-x-0 bottom-0 flex items-center justify-center gap-1 bg-black/60 py-1 text-[10px] text-white"><Camera className="size-3" />{t('Đổi ảnh')}</span></> : <div className="flex flex-col items-center gap-2 text-muted"><ImagePlus className="size-7 text-accent/75" strokeWidth={1.5} /><span className="text-[10px]">{t('Ảnh hồ sơ')}</span></div>}
      </button>
      <div className="min-w-0 flex-1 space-y-2.5">
        <div><p className="text-sm font-medium">{dragging ? t('Thả ảnh vào đây') : value ? t('Ảnh của bạn đã sẵn sàng') : t('Thêm ảnh để hoàn thiện CV')}</p><p id={`${id}-hint`} className="mt-1 text-xs leading-relaxed text-muted">{t('Chọn ảnh rõ mặt, ánh sáng tốt. JPG, PNG hoặc WebP, tối đa 2 MB.')}</p></div>
        <div className="flex flex-wrap items-center gap-2">
          <button type="button" onClick={() => input.current?.click()} className="inline-flex h-9 items-center gap-2 rounded-lg border border-accent/25 bg-accent/10 px-3 text-xs font-medium text-accent transition hover:bg-accent/20 focus-visible:outline-2 focus-visible:outline-accent"><Upload className="size-3.5" />{t(value ? 'Chọn ảnh khác' : 'Chọn ảnh từ máy')}</button>
          {value ? <button type="button" onClick={remove} className="inline-flex h-9 items-center gap-1.5 rounded-lg px-2 text-xs text-muted transition hover:bg-bad/10 hover:text-bad"><Trash2 className="size-3.5" />{t('Xóa ảnh')}</button> : <span className="text-xs text-muted">{t('hoặc kéo thả ảnh vào khung này')}</span>}
        </div>
        <div aria-live="polite">{busy ? <p className="flex items-center gap-1.5 text-xs text-muted"><LoaderCircle className="size-3 animate-spin" />{t('Đang xử lý ảnh…')}</p> : value && !error ? <p className="flex items-center gap-1.5 text-xs text-ok"><Check className="size-3" />{t('Ảnh sẽ được dùng trong mẫu CV đã chọn')}</p> : null}</div>
      </div>
    </div>
    {error && <p role="alert" className="text-xs text-bad">{error}</p>}
  </section>
}
