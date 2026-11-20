import { Card, CardHeader } from '@/components/ui/Card'
import { Field, Select } from '@/components/ui/Form'
import { fonts, themes, setFont, setLigatures, setTheme, useAppearance, type Font, type Theme } from '@/lib/appearance'
import { t } from '@/lib/i18n.ts'

export function AppearanceCard() {
  const appearance = useAppearance()
  return <Card>
    <CardHeader title={t('Giao diện')} />
    <div className="grid gap-3 p-4 sm:grid-cols-2">
      <Field label={t('Bảng màu')}><Select value={appearance.theme} onChange={(e) => setTheme(e.target.value as Theme)}>
        {Object.entries(themes).map(([id, name]) => <option key={id} value={id}>{t(name)}</option>)}
      </Select></Field>
      <Field label={t('Phông chữ mã nguồn')}><Select value={appearance.font} onChange={(e) => setFont(e.target.value as Font)}>
        {Object.entries(fonts).map(([id, name]) => <option key={id} value={id}>{t(name)}</option>)}
      </Select></Field>
      <label className="flex gap-2 text-sm"><input type="checkbox" checked={appearance.ligatures} onChange={(e) => setLigatures(e.target.checked)} />{t('Bật ký tự ghép trong mã nguồn')}</label>
      <pre className="rounded-lg bg-bg p-2 font-mono text-xs text-accent">{'items.filter(x => x.done !== false)'}</pre>
    </div>
  </Card>
}
