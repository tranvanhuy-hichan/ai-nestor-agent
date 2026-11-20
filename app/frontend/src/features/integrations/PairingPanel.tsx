import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { Card, CardHeader } from '@/components/ui/Card'
import { ErrorNote } from '@/components/ui/misc'
import { api } from '@/lib/api'
import { t } from '@/lib/i18n.ts'

type Channel = 'telegram' | 'zalo'
type Request = { id: string; channel: Channel; user_id: string | number; name: string; expires: number }
type ChannelStatus = { enabled: boolean; running: boolean; error: string; allowed_users: (string | number)[] }
const channels: { id: Channel; name: string }[] = [{ id: 'telegram', name: 'Telegram' }, { id: 'zalo', name: 'Zalo OA' }]

export function PairingPanel() {
  const qc = useQueryClient()
  const status = useQuery({ queryKey: ['pairing-channels'], queryFn: () => api.get<Record<Channel, ChannelStatus>>('/api/channels'), refetchInterval: 4000 })
  const requests = useQuery({ queryKey: ['pairing'], queryFn: () => api.get<Request[]>('/api/channels/pairing'), refetchInterval: 3000 })
  const [codes, setCodes] = useState<Partial<Record<Channel, { code: string; expires: number }>>>({})
  const refresh = () => ['pairing', 'pairing-channels', 'channels', 'zalo'].forEach((key) => { void qc.invalidateQueries({ queryKey: [key] }) })
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
  const error = status.error ?? requests.error ?? invite.error ?? decide.error ?? remove.error
  return <Card>
    <CardHeader title={t('Ghép đôi và quyền truy cập')} />
    <div className="space-y-4 p-4">
      {error && <ErrorNote error={error} />}
      <div className="grid gap-3 sm:grid-cols-2">
        {channels.map(({ id, name }) => {
          const channel = status.data?.[id]
          const code = codes[id]
          const validCode = code && channel?.running && code.expires > Date.now()
          return <section key={id} className="space-y-2 rounded-lg border border-line p-3">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <h3 className="text-sm font-medium">{name}</h3>
              <Badge tone={channel?.error ? 'bad' : channel?.running ? 'ok' : channel?.enabled ? 'warn' : undefined}>
                {channel?.error ? t('Lỗi kết nối') : channel?.running ? t('Đang hoạt động') : channel?.enabled ? t('Đang kết nối') : t('Chưa kết nối')}
              </Badge>
            </div>
            <Button size="sm" disabled={!channel?.running || invite.isPending} onClick={() => invite.mutate(id)}>{t('Tạo mã ghép đôi')}</Button>
            {validCode && <div className="space-y-1 text-sm">
              <p className="text-muted">{t('Gửi lệnh này trong 10 phút rồi duyệt yêu cầu bên dưới.')}</p>
              <code className="break-all">/pair {code.code}</code>
            </div>}
            {channel?.allowed_users.map((user_id) => <div key={user_id} className="flex items-center justify-between gap-2 text-sm">
              <code>{user_id}</code>
              <Button size="sm" variant="ghost" disabled={remove.isPending} onClick={() => {
                if (confirm(t('Gỡ quyền của {id}?', { id: user_id }))) remove.mutate({ channel: id, user_id })
              }}>{t('Gỡ quyền')}</Button>
            </div>)}
          </section>
        })}
      </div>
      <h3 className="text-sm font-semibold">{t('Yêu cầu đang chờ')}</h3>
      {requests.data?.length === 0 && <p className="text-sm text-muted">{t('Chưa có yêu cầu ghép đôi.')}</p>}
      {requests.data?.map((request) => <div key={request.id} className="flex flex-wrap items-center justify-between gap-2 rounded-lg border border-line p-3">
        <div className="text-sm">
          <span className="font-medium">{channels.find((c) => c.id === request.channel)?.name}</span>
          {' · '}<code>{request.user_id}</code>{request.name && ` · @${request.name}`}
        </div>
        <div className="flex gap-2">
          <Button size="sm" variant="primary" disabled={decide.isPending} onClick={() => decide.mutate({ id: request.id, approve: true })}>{t('Duyệt')}</Button>
          <Button size="sm" disabled={decide.isPending} onClick={() => decide.mutate({ id: request.id, approve: false })}>{t('Từ chối')}</Button>
        </div>
      </div>)}
    </div>
  </Card>
}
