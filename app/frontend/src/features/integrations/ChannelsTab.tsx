import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { CircleCheck, CircleX, Send } from 'lucide-react'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { Card, CardHeader } from '@/components/ui/Card'
import { Field, Input } from '@/components/ui/Form'
import { ErrorNote, Loading } from '@/components/ui/misc'
import { Switch } from '@/components/ui/Switch'
import { useToast } from '@/components/ui/Toast'
import { api } from '@/lib/api'
import type { TelegramStatus } from '@/lib/types'
import { errMsg } from '@/lib/utils'
import { t } from '@/lib/i18n.ts'
import { PairingPanel } from './PairingPanel'
import { ZaloCard, type ZaloState } from './ZaloCard'
import { T } from '@/lib/T.tsx'

export function ChannelsTab() {
  const qc = useQueryClient()
  const toast = useToast()
  const q = useQuery({ queryKey: ['channels'], queryFn: () => api.get<{ telegram: TelegramStatus }>('/api/channels'), refetchInterval: 4000 })
  const [token, setToken] = useState('')
  const zalo = useQuery({ queryKey: ['zalo'], queryFn: () => api.get<ZaloState>('/api/channels/zalo'), refetchInterval: 4000 })
  const [test, setTest] = useState<{ ok: boolean; text: string } | null>(null)
  const refresh = () => { void qc.invalidateQueries({ queryKey: ['channels'] }) }
  const tg = q.data?.telegram

  const save = useMutation({
    mutationFn: (enabled: boolean) => api.put('/api/channels/telegram', { enabled, token, api_base: tg?.api_base ?? 'https://api.telegram.org' }),
    onSuccess: () => { toast(t('Đã lưu cấu hình Telegram')); setToken(''); refresh() },
    onError: (e) => toast(errMsg(e), 'bad'),
  })
  const doTest = useMutation({
    mutationFn: () => api.post<{ ok: boolean; bot?: string; error?: string }>('/api/channels/telegram/test', { token, api_base: tg?.api_base ?? 'https://api.telegram.org' }),
    onSuccess: (r) => setTest({ ok: r.ok, text: r.ok ? t('Token hợp lệ, bot {bot}', { bot: r.bot ?? '' }) : r.error ?? t('lỗi') }),
  })

  if (q.isLoading) return <Loading />
  if (q.error || !tg) return <ErrorNote error={q.error ?? t('không tải được')} />

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader
          title={<span className="flex items-center gap-2"><Send className="size-4" />Telegram {tg.running ? <Badge tone="ok">{t('Đang chạy {bot}', { bot: tg.bot ?? '' })}</Badge> : tg.enabled ? <Badge tone="bad">{t('Lỗi')}</Badge> : <Badge>{t('Đã tắt')}</Badge>}</span>}
          action={<Switch checked={tg.enabled} onChange={(v) => save.mutate(v)} label={t('Bật Telegram')} disabled={!tg.has_token && !token} />}
        />
        <div className="space-y-4 p-5">
          {tg.error && <p className="rounded-lg border border-bad/30 bg-bad/10 px-3 py-2 font-mono text-xs text-bad">{tg.error}</p>}
          <ol className="list-decimal space-y-1 pl-5 text-sm text-muted">
            <li><T k="Mở Telegram, chat với {bot}, gửi {cmd} và làm theo để nhận token." v={{ bot: <b className="text-fg">@BotFather</b>, cmd: <code className="font-mono">/newbot</code> }} /></li>
            <li><T k="Dán token vào ô bên dưới, bấm {test} rồi {save}." v={{ test: <b className="text-fg">{t('Thử')}</b>, save: <b className="text-fg">{t('Lưu và bật')}</b> }} /></li>
            <li><T k="Bấm {gen}, rồi gửi {cmd} cho bot để gửi yêu cầu cấp quyền." v={{ gen: <b className="text-fg">{t('Tạo mã ghép đôi')}</b>, cmd: <code className="font-mono">{t('/pair mã')}</code> }} /></li>
          </ol>
          <Field label={tg.has_token ? t('Token bot (đã lưu, để trống nếu không đổi)') : t('Token bot')}><Input type="password" autoComplete="off" value={token} onChange={(e) => setToken(e.target.value)} placeholder="123456:ABC-DEF…" /></Field>
          <div className="flex flex-wrap items-center gap-3">
            <Button loading={doTest.isPending} disabled={!token && !tg.has_token} onClick={() => { setTest(null); doTest.mutate() }}>{t('Thử')}</Button>
            <Button variant="primary" loading={save.isPending} disabled={!token && !tg.has_token} onClick={() => save.mutate(true)}>{t('Lưu và bật')}</Button>
            {test && <span className={`flex items-center gap-1.5 text-sm ${test.ok ? 'text-ok' : 'text-bad'}`}>{test.ok ? <CircleCheck className="size-4" /> : <CircleX className="size-4" />}{test.text}</span>}
          </div>
        </div>
      </Card>

      <ZaloCard state={zalo.data} />
      <PairingPanel />
    </div>
  )
}
