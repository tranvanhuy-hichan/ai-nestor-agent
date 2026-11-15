import { lazy, Suspense, useRef, useState } from 'react'
import { FileText, Upload, X } from 'lucide-react'
import { Field, Input, Select, Textarea } from '@/components/ui/Form'
import type { FormField } from '@/lib/assistants'
import { t } from '@/lib/i18n.ts'
import { cn } from '@/lib/utils'

const CvProfileForm = lazy(() => import('@/components/cv/CvProfileForm'))
const CvTemplatePicker = lazy(() => import('@/components/cv/CvTemplatePicker'))

export type Values = Record<string, string>
export type Files = Record<string, File[]>
export const storedFiles = (values: Values, key: string): string[] => { try { const v = JSON.parse(values[`_uploaded:${key}`] || '[]'); return Array.isArray(v) ? v.filter((p): p is string => typeof p === 'string') : [] } catch { return [] } }

function FileField({ f, files, onChange }: { f: FormField; files: File[]; onChange: (v: File[]) => void }) {
  const input = useRef<HTMLInputElement>(null)
  const [over, setOver] = useState(false)
  const add = (list: FileList | File[]) => { const next = [...list]; if (next.length) onChange(f.multiple ? [...files, ...next] : [next[0]]) }
  return (
    <div>
      <div role="button" tabIndex={0} aria-label={t(f.label)} onClick={() => input.current?.click()} onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') input.current?.click() }}
        onDragOver={(e) => { e.preventDefault(); setOver(true) }} onDragLeave={() => setOver(false)} onDrop={(e) => { e.preventDefault(); setOver(false); add(e.dataTransfer.files) }}
        className={cn('flex cursor-pointer items-center gap-3 rounded-lg border-2 border-dashed px-4 py-3 text-sm transition', over ? 'border-accent bg-accent/10' : 'border-line bg-bg hover:border-accent/60')}>
        <input ref={input} type="file" multiple={f.multiple} accept={f.accept} className="hidden" onChange={(e) => { if (e.target.files) add(e.target.files); e.target.value = '' }} />
        <Upload className="size-4 shrink-0 text-accent" />
        <span className="text-muted">{f.multiple ? t('Chọn hoặc kéo thả nhiều file vào đây') : t('Chọn hoặc kéo thả file vào đây')}</span>
      </div>
      {files.length > 0 && (
        <ul className="mt-2 space-y-1">
          {files.map((x, i) => (
            <li key={x.name + i} className="flex items-center gap-2 rounded-md bg-panel2 px-2.5 py-1.5 text-sm">
              <FileText className="size-4 shrink-0 text-accent" /><span className="min-w-0 flex-1 truncate">{x.name}</span>
              <button type="button" aria-label={t('Bỏ {name}', { name: x.name })} onClick={() => onChange(files.filter((_, j) => j !== i))} className="text-muted hover:text-fg"><X className="size-3.5" /></button>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}

export function renderField(f: FormField, values: Values, files: Files, set: (k: string, v: string) => void, setFiles: (k: string, v: File[]) => void) {
  const label = t(f.label) + (f.required ? ' *' : '')
  const hint = f.hint ? t(f.hint) : undefined
  const ph = f.placeholder ? t(f.placeholder) : undefined
  const v = values[f.key] ?? ''
  if (f.type === 'cv-template') return <div><p className="mb-2 text-sm font-medium">{label}</p><Suspense fallback={<p>Đang tải mẫu CV…</p>}><CvTemplatePicker value={v} onChange={(id) => set(f.key, id)} /></Suspense></div>
  if (f.type === 'cv-profile') return <div><h3 className="mb-2 text-sm font-medium">{label}</h3><Suspense fallback={<p>Đang tải hồ sơ…</p>}><CvProfileForm template={values.mau_cv ?? ''} value={v} onChange={(data) => set(f.key, data)} /></Suspense></div>
  if (f.type === 'file') return <Field key={f.key} label={label} hint={hint}><FileField f={f} files={files[f.key] ?? []} onChange={(x) => { setFiles(f.key, x); if (!f.multiple) set(`_uploaded:${f.key}`, '[]') }} />{storedFiles(values, f.key).map((path) => <span key={path} className="mt-2 flex items-center gap-2 rounded-md bg-panel2 px-3 py-2 text-xs"><FileText className="size-3.5 text-accent" /><span className="min-w-0 flex-1 truncate">{path.split('/').pop()} · {t('Đã tải lên, sẽ dùng lại')}</span><button type="button" aria-label={t('Bỏ {name}', { name: path })} onClick={() => set(`_uploaded:${f.key}`, JSON.stringify(storedFiles(values, f.key).filter((p) => p !== path)))}><X className="size-3.5" /></button></span>)}</Field>
  if (f.type === 'textarea') return <Field key={f.key} label={label} hint={hint}><Textarea rows={5} value={v} placeholder={ph} onChange={(e) => set(f.key, e.target.value)} className="font-sans text-sm" /></Field>
  if (f.type === 'select') return (
    <Field key={f.key} label={label} hint={hint}>
      <Select value={v} onChange={(e) => set(f.key, e.target.value)}>
        {!f.required && <option value="">{t('Không chọn')}</option>}
        {(f.options ?? []).map((o) => <option key={o} value={o}>{t(o)}</option>)}
      </Select>
    </Field>
  )
  return <Field key={f.key} label={label} hint={hint}><Input type={f.type === 'number' ? 'number' : 'text'} min={f.type === 'number' ? 0 : undefined} value={v} placeholder={ph} onChange={(e) => set(f.key, e.target.value)} /></Field>
}


/** Lưới ô nhập: ô ngắn nằm cạnh nhau, ô dài và ô tải file chiếm cả hàng. */
export function FieldGrid({ fields, values, files, setValue, setFiles }: { fields: FormField[]; values: Values; files: Files; setValue: (k: string, v: string) => void; setFiles: (k: string, v: File[]) => void }) {
  return (
    <div className="grid gap-x-5 gap-y-4 md:grid-cols-2">
      {fields.map((f) => <div key={f.key} className={cn((f.type === 'textarea' || f.type === 'file' || f.type === 'cv-template' || f.type === 'cv-profile') && 'md:col-span-2')}>{renderField(f, values, files, setValue, setFiles)}</div>)}
    </div>
  )
}

export const isFilled = (f: FormField, values: Values, files: Files) => {
  if (f.type === 'file') return (files[f.key]?.length ?? 0) > 0 || storedFiles(values, f.key).length > 0
  if (f.type === 'cv-profile') {
    try { const p = JSON.parse(values[f.key] || '{}'); return p.template === values.mau_cv && p.complete === true } catch { return false }
  }
  return !!(values[f.key] ?? '').trim()
}
export const initialValues = (fields: FormField[]): Values => Object.fromEntries(fields.filter((f) => f.type === 'select' && f.required).map((f) => [f.key, f.options?.[0] ?? '']))
