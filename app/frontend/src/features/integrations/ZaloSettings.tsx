import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { Button } from '@/components/ui/Button'
import { Field, Input } from '@/components/ui/Form'
import { useToast } from '@/components/ui/Toast'
import { api } from '@/lib/api'
import { t } from '@/lib/i18n.ts'
import { errMsg } from '@/lib/utils'

export type ZaloState = { enabled: boolean; running: boolean; error: string; allowed_users: (string | number)[] } & { oa_id?: string; app_id?: string; has_app_secret?: boolean; has_access_token?: boolean; has_refresh_token?: boolean; has_webhook_secret?: boolean; webhook_path?: string }

/** Zalo OA cần vài mã từ trang quản trị Zalo; để trống ô nào thì giữ giá trị đã lưu. */
export function ZaloSettings({ state, onSaved }: { state: ZaloState; onSaved: () => void }) {
  const qc = useQueryClient()
  const toast = useToast()
  const [f, setF] = useState({ oa_id: '', app_id: '', app_secret: '', access_token: '', refresh_token: '', webhook_secret: '' })
  const set = (k: keyof typeof f) => (e: React.ChangeEvent<HTMLInputElement>) => setF({ ...f, [k]: e.target.value })
  const save = useMutation({
    mutationFn: (enabled: boolean) => api.put('/api/channels/zalo', { enabled, ...(enabled ? f : {}), oa_id: (enabled && f.oa_id) || state.oa_id || '', app_id: (enabled && f.app_id) || state.app_id || '' }),
    onSuccess: () => { void qc.invalidateQueries({ queryKey: ['channels'] }); void qc.invalidateQueries({ queryKey: ['pairing'] }); toast(t('Đã lưu')); onSaved() },
    onError: (e) => toast(errMsg(e), 'bad'),
  })
  const on = !!state.enabled
  const fields: [keyof typeof f, string, boolean | undefined, boolean][] = [
    ['oa_id', t('Mã Official Account (OA ID)'), !!state.oa_id, false], ['app_id', t('App ID'), !!state.app_id, false],
    ['app_secret', t('App Secret'), state.has_app_secret, true], ['access_token', t('Access token'), state.has_access_token, true],
    ['refresh_token', t('Refresh token'), state.has_refresh_token, true], ['webhook_secret', t('Khóa bí mật webhook'), state.has_webhook_secret, true],
  ]
  return (
    <div className="space-y-4">
      <p className="text-sm text-muted">{t('Cấu hình Zalo Official Account để nhận việc qua tin nhắn.')}</p>
      {state.error && <p className="text-xs text-bad">{state.error}</p>}
      <div className="grid gap-2 sm:grid-cols-2 xl:grid-cols-3">
        {fields.map(([k, label, saved, secret]) => (
          <Field key={k} label={label}><Input type={secret ? 'password' : 'text'} value={f[k]} onChange={set(k)} placeholder={saved ? `${label} (${t('đã lưu')})` : label} /></Field>
        ))}
      </div>
      {state.webhook_path && <p className="mt-2 text-xs text-muted">{t('Địa chỉ webhook để dán vào Zalo:')} <code>{state.webhook_path}</code>?secret=…</p>}
      <div className="mt-3 flex gap-2">
        <Button variant="primary" loading={save.isPending} onClick={() => save.mutate(true)}>{on ? t('Lưu') : t('Kết nối')}</Button>
        {on && <Button onClick={() => save.mutate(false)}>{t('Ngắt kết nối')}</Button>}
      </div>
    </div>
  )
}

