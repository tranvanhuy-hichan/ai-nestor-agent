import { useState } from 'react'
import { Link2, MessageCircle, Send, Settings, UsersRound } from 'lucide-react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { Card } from '@/components/ui/Card'
import { ErrorNote } from '@/components/ui/misc'
import { api } from '@/lib/api'
import { t } from '@/lib/i18n.ts'

export type Channel = 'telegram' | 'zalo'
type Request = { id: string; channel: Channel; user_id: string | number; name: string; expires: number }
type ChannelStatus = { enabled: boolean; running: boolean; error: string; allowed_users: (string | number)[] }
export const CHANNELS = [
  { id: 'telegram', name: 'Telegram', Icon: Send, tone: 'bg-info/10 text-info' },
  { id: 'zalo', name: 'Zalo OA', Icon: MessageCircle, tone: 'bg-accent/10 text-accent' },
] as const

export function PairingPanel({ status, onConfigure }: {
  status: { telegram: ChannelStatus & { bot: string }; zalo: ChannelStatus & { oa_id?: string } }
  onConfigure: (id: Channel) => void
}) {
  const qc = useQueryClient()
  const requests = useQuery({ queryKey: ['pairing'], queryFn: () => api.get<Request[]>('/api/channels/pairing'), refetchInterval: 3000 })
  const [codes, setCodes] = useState<Partial<Record<Channel, { code: string; expires: number }>>>({})
  const refresh = () => ['pairing', 'channels'].forEach((key) => { void qc.invalidateQueries({ queryKey: [key] }) })
  const invite = useMutation({
    mutationFn: (channel: Channel) => api.post<{ code: string; expires_in: number }>(`/api/channels/${channel}/pair-code`),
    onSuccess: (result, channel) => setCodes((prev) => ({ ...prev, [channel]: { code: result.code, expires: Date.now() + result.expires_in * 1000 } })),
  })
  const decide = useMutation({
    mutationFn: ({ id, approve }: { id: string; approve: boolean }) => api.post(`/api/channels/pairing/${id}`, { approve }),
    onSettled: refresh,
  })
  const remove = useMutation({
    mutationFn: ({ channel, user_id }: { channel: Channel; user_id: string | number }) => api.post(`/api/channels/${channel}/remove-user`, { user_id }),
    onSuccess: refresh,
  })
  const error = requests.error ?? invite.error ?? decide.error ?? remove.error
  return <div className="space-y-6">
    {error && <ErrorNote error={error} />}
    <div className="grid items-start gap-4 xl:grid-cols-2">
      {CHANNELS.map(({ id, name, Icon, tone }) => {
        const channel = status[id]
        const code = codes[id]
        const validCode = code && channel.running && code.expires > Date.now()
        const account = id === 'telegram' ? status.telegram.bot : status.zalo.oa_id
        return <Card key={id} className="min-w-0">
          <div className="flex min-w-0 items-start gap-3 px-4 py-4 sm:px-5">
            <span className={`grid size-10 shrink-0 place-items-center rounded-xl ${tone}`}><Icon className="size-5" /></span>
            <div className="min-w-0 flex-1">
              <div className="flex flex-wrap items-center gap-x-2 gap-y-1">
                <h3 className="text-sm font-semibold">{name}</h3>
                <Badge tone={channel.error ? 'bad' : channel.running ? 'ok' : channel.enabled ? 'warn' : undefined}>
                  {channel.error ? t('Lỗi kết nối') : channel.running ? t('Đang hoạt động') : channel.enabled ? t('Đang kết nối') : t('Chưa kết nối')}
                </Badge>
              </div>
              {account && <p className="mt-1 truncate text-xs text-muted">{account}</p>}
              {channel.error && <p className="mt-1 break-words text-xs text-bad">{channel.error}</p>}
            </div>
            <Button size="sm" variant="ghost" onClick={() => onConfigure(id)} aria-label={t('Cấu hình {name}', { name })} title={t('Cấu hình {name}', { name })}>
              <Settings className="size-4" />
            </Button>
          </div>
          <div className="space-y-3 border-t border-line px-4 py-3 sm:px-5">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <h4 className="flex items-center gap-1.5 text-xs font-medium text-muted">
                <UsersRound className="size-4" />{t('Đã cấp quyền')} <span className="tabular-nums">{channel.allowed_users.length}</span>
              </h4>
              {channel.running && <Button size="sm" onClick={() => invite.mutate(id)} loading={invite.isPending && invite.variables === id} disabled={invite.isPending}>
                <Link2 className="size-3.5" />{t('Tạo mã ghép đôi')}
              </Button>}
            </div>
            {validCode && <div className="rounded-lg border border-accent/25 bg-accent/5 px-3 py-2 text-xs">
              <p className="text-muted">{t('Gửi lệnh này trong 10 phút rồi duyệt yêu cầu bên dưới.')}</p>
              <code className="mt-1 block break-all text-sm text-accent">/pair {code.code}</code>
            </div>}
            {channel.allowed_users.length > 0 && <ul className="divide-y divide-line overflow-hidden rounded-lg border border-line bg-bg/50">
              {channel.allowed_users.map((user_id) => <li key={user_id} className="flex min-w-0 items-center justify-between gap-2 px-3 py-1">
                <code className="truncate text-xs" title={String(user_id)}>{user_id}</code>
                <Button size="sm" variant="ghost" disabled={remove.isPending} onClick={() => {
                  if (confirm(t('Gỡ quyền của {id}?', { id: user_id }))) remove.mutate({ channel: id, user_id })
                }}>{t('Gỡ quyền')}</Button>
              </li>)}
            </ul>}
          </div>
        </Card>
      })}
    </div>
    <Card>
      <div className="flex items-center gap-2 border-b border-line px-4 py-3.5 sm:px-5">
        <h3 className="text-sm font-semibold">{t('Yêu cầu đang chờ')}</h3>
        {!!requests.data?.length && <Badge tone="accent">{requests.data.length}</Badge>}
      </div>
      {requests.data?.length === 0 && <p className="px-4 py-4 text-sm text-muted sm:px-5">{t('Chưa có yêu cầu ghép đôi.')}</p>}
      <ul className="divide-y divide-line">
        {requests.data?.map((request) => <li key={request.id} className="flex flex-wrap items-center justify-between gap-3 px-4 py-3 sm:px-5">
          <div className="min-w-0">
            <div className="flex flex-wrap items-center gap-2 text-sm">
              <span className="break-all font-medium">{request.name ? `@${request.name}` : request.user_id}</span>
              <Badge>{CHANNELS.find((channel) => channel.id === request.channel)?.name}</Badge>
            </div>
            {request.name && <code className="mt-1 block break-all text-xs text-muted">{request.user_id}</code>}
          </div>
          <div className="flex gap-2">
            <Button size="sm" variant="primary" disabled={decide.isPending} onClick={() => decide.mutate({ id: request.id, approve: true })}>{t('Duyệt')}</Button>
            <Button size="sm" disabled={decide.isPending} onClick={() => decide.mutate({ id: request.id, approve: false })}>{t('Từ chối')}</Button>
          </div>
        </li>)}
      </ul>
    </Card>
  </div>
}
