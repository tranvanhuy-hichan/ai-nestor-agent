import { Card, CardHeader } from '@/components/ui/Card'
import { Field, Select } from '@/components/ui/Form'
import { Switch } from '@/components/ui/Switch'
import { fonts, themes, setFont, setLigatures, setTheme, useAppearance, type Font, type Theme } from '@/lib/appearance'
import { t } from '@/lib/i18n.ts'

export function AppearanceCard() {
  const appearance = useAppearance()
  return (
    <Card>
      <CardHeader title={t('Tùy chỉnh hiển thị')} hint={t('Thay đổi áp dụng ngay trên trình duyệt này.')} />
      <div className="grid gap-4 p-5 sm:grid-cols-2">
        <Field label={t('Bảng màu')}><Select value={appearance.theme} onChange={(e) => setTheme(e.target.value as Theme)}>
          {Object.entries(themes).map(([id, name]) => <option key={id} value={id}>{t(name)}</option>)}
        </Select></Field>
        <Field label={t('Phông chữ mã nguồn')}><Select value={appearance.font} onChange={(e) => setFont(e.target.value as Font)}>
          {Object.entries(fonts).map(([id, name]) => <option key={id} value={id}>{t(name)}</option>)}
        </Select></Field>
        <div className="flex min-w-0 items-center justify-between gap-3 rounded-lg border border-line px-3 py-2.5">
          <span className="text-sm">{t('Bật ký tự ghép trong mã nguồn')}</span>
          <Switch checked={appearance.ligatures} onChange={setLigatures} label={t('Bật ký tự ghép trong mã nguồn')} />
        </div>
        <pre className="min-w-0 overflow-auto rounded-lg bg-bg p-3 font-mono text-xs text-accent">{'items.filter(x => x.done !== false)'}</pre>
      </div>
    </Card>
  )
}
