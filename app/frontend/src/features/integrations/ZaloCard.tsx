import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { Card, CardHeader } from '@/components/ui/Card'
import { Input } from '@/components/ui/Form'
import { useToast } from '@/components/ui/Toast'
import { api } from '@/lib/api'
import { t } from '@/lib/i18n.ts'
import { errMsg } from '@/lib/utils'

export type ZaloState = { enabled?: boolean; running?: boolean; error?: string } & { oa_id?: string; app_id?: string; has_app_secret?: boolean; has_access_token?: boolean; has_webhook_secret?: boolean; webhook_path?: string }

/** Zalo OA cần vài mã từ trang quản trị Zalo; để trống ô nào thì giữ giá trị đã lưu. */
export function ZaloCard({ state }: { state?: ZaloState }) {
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
    <Card>
      <CardHeader title={t('Nhận việc qua Zalo')} hint={t('Cấu hình Zalo Official Account để nhận việc qua tin nhắn.')} />
      <div className="p-4">
      <div className="mb-3">{state?.error && <p className="mb-2 text-xs text-bad">{state.error}</p>}{state?.running ? <Badge tone="ok">{t('Đang hoạt động')}</Badge> : on ? <Badge tone="warn">{t('Đã bật, chưa kết nối')}</Badge> : <Badge>{t('Chưa kết nối')}</Badge>}</div>
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
      </div>
    </Card>
  )
}

