import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { ArrowRight, CircleCheck, CircleX } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { Field, Input } from '@/components/ui/Form'
import { ErrorNote, Loading } from '@/components/ui/misc'
import { Modal } from '@/components/ui/Modal'
import { useToast } from '@/components/ui/Toast'
import { api } from '@/lib/api'
import type { TelegramStatus } from '@/lib/types'
import { errMsg } from '@/lib/utils'
import { t } from '@/lib/i18n.ts'
import { CHANNELS, PairingPanel, type Channel } from './PairingPanel'
import { ZaloSettings, type ZaloState } from './ZaloSettings'
import { T } from '@/lib/T.tsx'

function TelegramSettings({ tg, onSaved }: { tg: TelegramStatus; onSaved: () => void }) {
  const qc = useQueryClient()
  const toast = useToast()
  const [token, setToken] = useState('')
  const [test, setTest] = useState<{ ok: boolean; text: string } | null>(null)
  const save = useMutation({
    mutationFn: (enabled: boolean) => api.put('/api/channels/telegram', { enabled, token: enabled ? token : '', api_base: tg.api_base ?? 'https://api.telegram.org' }),
    onSuccess: () => { void qc.invalidateQueries({ queryKey: ['channels'] }); void qc.invalidateQueries({ queryKey: ['pairing'] }); toast(t('Đã lưu cấu hình Telegram')); onSaved() },
    onError: (e) => toast(errMsg(e), 'bad'),
  })
  const doTest = useMutation({
    mutationFn: () => api.post<{ ok: boolean; bot?: string; error?: string }>('/api/channels/telegram/test', { token, api_base: tg.api_base ?? 'https://api.telegram.org' }),
    onError: (error) => setTest({ ok: false, text: errMsg(error) }),
    onSuccess: (r) => setTest({ ok: r.ok, text: r.ok ? t('Token hợp lệ, bot {bot}', { bot: r.bot ?? '' }) : r.error ?? t('lỗi') }),
  })

  return (
    <div className="space-y-4">
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
        {tg.enabled && <Button disabled={save.isPending} onClick={() => save.mutate(false)}>{t('Tắt Telegram')}</Button>}
        {test && <span className={`flex items-center gap-1.5 text-sm ${test.ok ? 'text-ok' : 'text-bad'}`}>{test.ok ? <CircleCheck className="size-4" /> : <CircleX className="size-4" />}{test.text}</span>}
      </div>
    </div>
  )
}

export function ChannelsTab({ choosing, onClosePicker }: { choosing: boolean; onClosePicker: () => void }) {
  const channels = useQuery({
    queryKey: ['channels'],
    queryFn: () => api.get<{ telegram: TelegramStatus; zalo: ZaloState }>('/api/channels'),
    refetchInterval: 4000,
  })
  const [editing, setEditing] = useState<Channel | null>(null)
  const configure = (id: Channel) => { onClosePicker(); setEditing(id) }

  if (channels.isLoading) return <Loading />
  if (!channels.data) return <ErrorNote error={channels.error ?? t('không tải được')} />
  const status = channels.data
  return <>
    <PairingPanel status={status} onConfigure={configure} />
    {choosing && <Modal open onClose={onClosePicker} title={t('Thêm kênh')}>
      <div className="grid gap-3 sm:grid-cols-2">
        {CHANNELS.map(({ id, name, Icon, tone }) => {
          const configured = id === 'telegram' ? status.telegram.has_token : !!(status.zalo.oa_id || status.zalo.has_access_token || status.zalo.has_refresh_token)
          return <button key={id} type="button" onClick={() => configure(id)}
            className="flex items-center gap-3 rounded-xl border border-line bg-panel2/50 p-3 text-left hover:border-accent/60">
            <span className={`grid size-10 shrink-0 place-items-center rounded-xl ${tone}`}><Icon className="size-5" /></span>
            <span className="min-w-0 flex-1">
              <span className="block text-sm font-semibold">{name}</span>
              <span className="block text-xs text-muted">{configured ? t('Cài đặt') : t('Chưa kết nối')}</span>
            </span>
            <ArrowRight className="size-4 shrink-0 text-muted" />
          </button>
        })}
      </div>
    </Modal>}
    {editing && <Modal open wide={editing === 'zalo'} onClose={() => setEditing(null)}
      title={t('Cấu hình {name}', { name: CHANNELS.find((channel) => channel.id === editing)?.name ?? '' })}>
      {editing === 'telegram'
        ? <TelegramSettings tg={status.telegram} onSaved={() => setEditing(null)} />
        : <ZaloSettings state={status.zalo} onSaved={() => setEditing(null)} />}
    </Modal>}
  </>
}
