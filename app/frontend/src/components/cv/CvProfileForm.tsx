import { useEffect } from 'react'
import { Field, Input, Select, Textarea } from '@/components/ui/Form'
import { schemaForTemplate, type CvInput } from '@/lib/cv/templateSchema'
import { parseProfile, profileIssues } from '@/lib/cv/profile'
import { t } from '@/lib/i18n.ts'
import CvPhotoUpload from './CvPhotoUpload'

export default function CvProfileForm({ template, value, onChange }: { template: string; value: string; onChange: (v: string) => void }) {
  useEffect(() => {
    if (!template) return
    const p = parseProfile(value)
    if (p.template === template) return
    const schema = schemaForTemplate(template)
    const next = { ...p, template }
    onChange(JSON.stringify({ ...next, complete: profileIssues(JSON.stringify(next), template, schema).length === 0, visible: [...schema.contact.map((f) => f.key), ...schema.sections.map((s) => s.key), ...(schema.photo ? ['photo'] : [])] }))
  }, [template, value, onChange])
  if (!template) return <p className="text-sm text-muted">Chọn mẫu CV phía trên để hiện các thông tin cần điền.</p>
  const schema = schemaForTemplate(template)
  const profile = parseProfile(value)
  const update = (patch: Partial<typeof profile>) => {
    const next = { ...profile, ...patch, template }
    const issues = profileIssues(JSON.stringify(next), template, schema)
    onChange(JSON.stringify({ ...next, complete: issues.length === 0, visible: [...schema.contact.map((f) => f.key), ...schema.sections.map((s) => s.key), ...(schema.photo ? ['photo'] : [])] }))
  }
  const set = (key: string, v: unknown) => update({ data: { ...profile.data, [key]: v } })
  const input = (f: CvInput, v: string, change: (v: string) => void) => <Field key={f.key} label={t(f.label)} hint={f.hint ? t(f.hint) : undefined}>{f.multiline ? <Textarea rows={4} value={v} onChange={(e) => change(e.target.value)} /> : <Input value={v} onChange={(e) => change(e.target.value)} />}</Field>
  const issues = profileIssues(value, template, schema)
  return <div className="space-y-4">
    <p className="text-sm text-muted">Các mục dưới đây lấy từ mẫu bạn đã chọn. Cứ viết ý thô; AI sẽ chỉnh cách diễn đạt, sắp xếp và điền vào CV. Mục chưa có thì chọn bỏ qua.</p>
    <div className="grid gap-3 md:grid-cols-2">{schema.contact.map((f) => input(f, String(profile.data[f.key] ?? ''), (v) => set(f.key, v)))}</div>
    {schema.photo && <CvPhotoUpload value={typeof profile.data.photo === 'string' ? profile.data.photo : ''} onChange={(photo) => set('photo', photo)} />}
    {schema.sections.map((s) => {
      const skipped = profile.skipped.includes(s.key)
      const rows = Array.isArray(profile.data[s.key]) ? profile.data[s.key] as Record<string, string>[] : []
      return <section key={s.key} className="space-y-3 rounded-lg border border-line p-3">
        <div className="flex flex-wrap items-center justify-between gap-2"><h3 className="text-sm font-semibold">{t(s.label)}</h3><label className="flex items-center gap-2 text-xs text-muted"><input type="checkbox" checked={skipped} onChange={(e) => update({ skipped: e.target.checked ? [...profile.skipped, s.key] : profile.skipped.filter((x) => x !== s.key) })} />Chưa có / bỏ qua mục này</label></div>
        {!skipped && (s.fields ? <>
          {rows.map((row, i) => <div key={row.id ?? i} className="space-y-3 rounded-md bg-bg p-3">
            <div className="flex justify-between text-xs text-muted"><span>{t(s.label)} {i + 1}</span><button type="button" onClick={() => set(s.key, rows.filter((_, n) => n !== i))} className="text-accent">Xóa mục {i + 1}</button></div>
            <div className="grid gap-3 md:grid-cols-2">{s.fields!.map((f) => <div key={f.key} className={f.multiline ? 'md:col-span-2' : ''}>{input(f, row[f.key] ?? '', (v) => set(s.key, rows.map((r, n) => n === i ? { ...r, [f.key]: v } : r)))}</div>)}</div>
          </div>)}
          <button type="button" onClick={() => set(s.key, [...rows, { id: crypto.randomUUID() }])} className="text-sm text-accent">+ Thêm {t(s.label).toLowerCase()}</button>
        </> : <Field label={t(s.label)} hint={s.hint ? t(s.hint) : undefined}><Textarea rows={3} value={String(profile.data[s.key] ?? '')} onChange={(e) => set(s.key, e.target.value)} placeholder={s.key === 'summary' ? 'Để trống để AI viết từ kinh nghiệm, học vấn và kỹ năng bạn cung cấp' : undefined} /></Field>)}
      </section>
    })}
    <Field label="Cách AI biên tập"><Select value={profile.tone} onChange={(e) => update({ tone: e.target.value })}><option>Chuyên nghiệp, tự tin</option><option>Ngắn gọn, tối ưu ATS</option><option>Nổi bật, giàu sức thuyết phục</option></Select></Field>
    <p className="text-xs text-muted">AI có thể làm nổi bật thế mạnh và viết thuyết phục hơn. Kinh nghiệm, chức danh, số liệu và chứng chỉ vẫn theo thông tin bạn cung cấp.</p>
    {issues.length > 0 && <p role="status" className="text-xs text-muted">Cần bổ sung hoặc chọn bỏ qua: {issues.join(', ')}</p>}
  </div>
}
