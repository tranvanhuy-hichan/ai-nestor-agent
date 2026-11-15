export type ProfileSchema = { contact: { key: string; label: string }[]; sections: { key: string; label: string; fields?: { key: string }[] }[] }
export type CvProfile = { template: string; data: Record<string, unknown>; skipped: string[]; tone: string }
export function parseProfile(value: string): CvProfile {
  try { const v = JSON.parse(value); return { template: typeof v.template === 'string' ? v.template : '', data: v.data && typeof v.data === 'object' ? v.data : {}, skipped: Array.isArray(v.skipped) ? v.skipped : [], tone: v.tone || 'Chuyên nghiệp, tự tin' } } catch { return { template: '', data: {}, skipped: [], tone: 'Chuyên nghiệp, tự tin' } }
}
export function profileIssues(value: string, template: string, schema: ProfileSchema): string[] {
  const p = parseProfile(value)
  if (!template || p.template !== template) return ['Chọn mẫu và hoàn thiện hồ sơ theo mẫu']
  const issues: string[] = []
  for (const key of ['name', 'title']) if (schema.contact.some((f) => f.key === key) && !String(p.data[key] ?? '').trim()) issues.push(schema.contact.find((f) => f.key === key)!.label)
  if (schema.contact.some((f) => f.key === 'email' || f.key === 'phone') && !String(p.data.email ?? '').trim() && !String(p.data.phone ?? '').trim()) issues.push('Email hoặc số điện thoại')
  for (const s of schema.sections) {
    if (p.skipped.includes(s.key) || s.key === 'summary') continue
    const v = p.data[s.key]
    if (s.fields) {
      const core: Record<string, string[]> = { experience: ['role', 'company', 'desc'], education: ['school', 'degree'], skills: ['name'], languages: ['name'], projects: ['name', 'desc'], highlights: ['value', 'label'] }
      const required = s.fields.filter((f) => core[s.key]?.includes(f.key))
      if (!Array.isArray(v) || !v.length || v.some((row) => !(required.length ? required.every((f) => String(row?.[f.key] ?? '').trim()) : s.fields!.some((f) => String(row?.[f.key] ?? '').trim())))) issues.push(s.label)
    } else if (!String(v ?? '').trim()) issues.push(s.label)
  }
  return issues
}
