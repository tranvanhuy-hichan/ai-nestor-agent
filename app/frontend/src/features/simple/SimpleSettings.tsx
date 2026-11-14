import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Form'
import { Loading, Page, PageHeader } from '@/components/ui/misc'
import { useToast } from '@/components/ui/Toast'
import { LangSwitcher } from '@/components/layout/LangSwitcher'
import { api } from '@/lib/api'
import { t } from '@/lib/i18n.ts'
import { useConfig } from '@/lib/queries'
import { setUiMode } from '@/lib/uiMode'
import type { TelegramStatus } from '@/lib/types'
import { errMsg } from '@/lib/utils'

type ChannelState = { enabled?: boolean; has_token?: boolean; running?: boolean; error?: string }

function Card({ title, hint, children }: { title: string; hint?: string; children: React.ReactNode }) {
  return (
    <section className="rounded-xl border border-line bg-panel p-4">
      <h2 className="text-sm font-semibold">{title}</h2>
      {hint && <p className="mt-0.5 text-xs text-muted">{hint}</p>}
      <div className="mt-3">{children}</div>
    </section>
  )
}

/** Thẻ nối kênh nhắn tin: nhập mã kết nối một lần, bật là nhận việc qua điện thoại. */
function ChannelCard({ name, title, hint, label, state, path, extra }: { name: string; title: string; hint: string; label: string; state?: ChannelState; path: string; extra?: Record<string, unknown> }) {
  const qc = useQueryClient()
  const toast = useToast()
  const [token, setToken] = useState('')
  const save = useMutation({
    mutationFn: (enabled: boolean) => api.put(path, { enabled, token, ...extra }),
    onSuccess: () => { setToken(''); void qc.invalidateQueries({ queryKey: ['channels'] }); void qc.invalidateQueries({ queryKey: ['zalo'] }); toast(t('Đã lưu')) },
    onError: (e) => toast(errMsg(e), 'bad'),
  })
  const on = !!state?.enabled
  return (
    <Card title={title} hint={hint}>
      <div className="mb-3 flex items-center gap-2">
        {state?.running ? <Badge tone="ok">{t('Đang hoạt động')}</Badge> : on ? <Badge tone="warn">{t('Đã bật, chưa kết nối')}</Badge> : <Badge>{t('Chưa kết nối')}</Badge>}
        {state?.error && <span className="text-xs text-bad">{state.error}</span>}
      </div>
      <div className="flex flex-wrap gap-2">
        <Input type="password" value={token} onChange={(e) => setToken(e.target.value)} placeholder={state?.has_token ? t('Đã lưu mã {name} (nhập để thay)', { name }) : label} className="min-w-[14rem] flex-1" />
        <Button variant="primary" loading={save.isPending} disabled={!token && !state?.has_token} onClick={() => save.mutate(true)}>{on ? t('Lưu') : t('Kết nối')}</Button>
        {on && <Button onClick={() => save.mutate(false)}>{t('Ngắt kết nối')}</Button>}
      </div>
    </Card>
  )
}


type ZaloState = ChannelState & { oa_id?: string; app_id?: string; has_app_secret?: boolean; has_access_token?: boolean; has_webhook_secret?: boolean; webhook_path?: string }

/** Zalo OA cần vài mã từ trang quản trị Zalo; để trống ô nào thì giữ giá trị đã lưu. */
function ZaloCard({ state }: { state?: ZaloState }) {
  const qc = useQueryClient()
  const toast = useToast()
  const [f, setF] = useState({ oa_id: '', app_id: '', app_secret: '', access_token: '', refresh_token: '', webhook_secret: '' })
  const set = (k: keyof typeof f) => (e: React.ChangeEvent<HTMLInputElement>) => setF({ ...f, [k]: e.target.value })
  const save = useMutation({
    mutationFn: (enabled: boolean) => api.put('/api/channels/zalo', { enabled, ...f, oa_id: f.oa_id || state?.oa_id || '', app_id: f.app_id || state?.app_id || '' }),
    onSuccess: () => { setF({ oa_id: '', app_id: '', app_secret: '', access_token: '', refresh_token: '', webhook_secret: '' }); void qc.invalidateQueries({ queryKey: ['zalo'] }); toast(t('Đã lưu')) },
    onError: (e) => toast(errMsg(e), 'bad'),
  })
  const on = !!state?.enabled
  const fields: [keyof typeof f, string, boolean | undefined, boolean][] = [
    ['oa_id', t('Mã Official Account (OA ID)'), !!state?.oa_id, false], ['app_id', t('App ID'), !!state?.app_id, false],
    ['app_secret', t('App Secret'), state?.has_app_secret, true], ['access_token', t('Access token'), state?.has_access_token, true],
    ['refresh_token', t('Refresh token'), undefined, true], ['webhook_secret', t('Khóa bí mật webhook'), state?.has_webhook_secret, true],
  ]
  return (
    <Card title={t('Nhận việc qua Zalo')} hint={t('Nhắn Zalo cho trợ lý để giao việc. Cần một Zalo Official Account; nhờ bộ phận IT điền các mã dưới đây một lần.')}>
      <div className="mb-3">{state?.running ? <Badge tone="ok">{t('Đang hoạt động')}</Badge> : on ? <Badge tone="warn">{t('Đã bật, chưa kết nối')}</Badge> : <Badge>{t('Chưa kết nối')}</Badge>}</div>
      <div className="grid gap-2 sm:grid-cols-2 xl:grid-cols-3">
        {fields.map(([k, label, saved, secret]) => (
          <Input key={k} type={secret ? 'password' : 'text'} value={f[k]} onChange={set(k)} placeholder={saved ? `${label} (${t('đã lưu')})` : label} />
        ))}
      </div>
      {state?.webhook_path && <p className="mt-2 text-xs text-muted">{t('Địa chỉ webhook để dán vào Zalo:')} <code>{state.webhook_path}</code>?secret=…</p>}
      <div className="mt-3 flex gap-2">
        <Button variant="primary" loading={save.isPending} onClick={() => save.mutate(true)}>{on ? t('Lưu') : t('Kết nối')}</Button>
        {on && <Button onClick={() => save.mutate(false)}>{t('Ngắt kết nối')}</Button>}
      </div>
    </Card>
  )
}

export function SimpleSettings() {
  const nav = useNavigate()
  const cfg = useConfig()
  const tg = useQuery({ queryKey: ['channels'], queryFn: () => api.get<{ telegram: TelegramStatus }>('/api/channels') })
  const zalo = useQuery({ queryKey: ['zalo'], queryFn: () => api.get<ZaloState>('/api/channels/zalo'), retry: false })
  if (!cfg.data) return <Loading />
  const c = cfg.data.config
  const def = c.providers[c.default_provider]

  return (
    <Page>
      <PageHeader title={t('Cài đặt')} subtitle={t('Những thứ cơ bản để bắt đầu. Cần tùy chỉnh sâu hơn, hãy bật chế độ Nâng cao.')} />
      <div className="grid items-start gap-4 pb-10 lg:grid-cols-2">
        <Card title={t('Ngôn ngữ')}><LangSwitcher /></Card>
        <Card title={t('Tài khoản AI')} hint={t('Bộ não giúp trợ lý làm việc.')}>
          <div className="flex flex-wrap items-center gap-3 text-sm">
            {def ? <span>{t('Đang dùng: {name}', { name: `${c.default_provider} (${def.model})` })}</span> : <span className="text-warn">{t('Chưa có tài khoản AI nào.')}</span>}
            <Button onClick={() => { setUiMode('advanced'); nav('/providers') }}>{t('Thêm hoặc đổi tài khoản AI')}</Button>
          </div>
        </Card>
        {zalo.isError ? null : (
          <div className="lg:col-span-2"><ZaloCard state={zalo.data} /></div>
        )}
        <ChannelCard name="Telegram" title={t('Nhận việc qua Telegram')} hint={t('Nhắn Telegram cho trợ lý, kể cả khi bạn không ngồi trước máy tính.')} label={t('Dán mã bot Telegram')} state={tg.data?.telegram} path="/api/channels/telegram" extra={{ api_base: tg.data?.telegram.api_base ?? 'https://api.telegram.org' }} />
      </div>
    </Page>
  )
}
