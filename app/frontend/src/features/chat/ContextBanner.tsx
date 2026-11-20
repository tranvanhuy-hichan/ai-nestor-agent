import { useEffect, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Button } from '@/components/ui/Button'
import { Textarea } from '@/components/ui/Form'
import { Modal } from '@/components/ui/Modal'
import { useToast } from '@/components/ui/Toast'
import { api } from '@/lib/api'
import { t } from '@/lib/i18n.ts'
import { errMsg } from '@/lib/utils'

export function ContextBanner({ sid, size, busy, provider, newSession }: {
  sid: string; size: number; busy: boolean; provider: string; newSession: () => void
}) {
  const qc = useQueryClient()
  const toast = useToast()
  const [note, setNote] = useState<string | null>(null)
  const queryKey = ['session-usage', sid]
  const query = useQuery({
    queryKey, queryFn: () => api.get<{ context_used: number; context_window: number | null }>(`/api/sessions/${sid}/usage`),
    refetchInterval: busy ? 3000 : false,
  })
  useEffect(() => { if (!busy) void qc.invalidateQueries({ queryKey: ['session-usage', sid] }) }, [busy, size, qc, sid])
  const mutate = useMutation({
    mutationFn: ({ action, note }: { action: 'compact' | 'highlights'; note?: string }) =>
      api.post<{ note?: string }>(`/api/sessions/${sid}/context`, { action, provider, note }),
    onSuccess: (result, arg) => {
      if (arg.action === 'highlights' && !arg.note) setNote(result.note ?? '')
      else {
        setNote(null)
        toast(arg.action === 'compact' ? t('Đã tóm tắt ngữ cảnh') : t('Đã lưu vào bộ nhớ'))
        void qc.invalidateQueries({ queryKey })
      }
    },
    onError: (error) => toast(errMsg(error), 'bad'),
  })
  const used = query.data?.context_used ?? 0
  const limit = query.data?.context_window ?? 0
  if (!limit || used / limit < 0.8) return null
  return <div className="mx-3 mb-2 flex flex-wrap items-center gap-2 rounded-lg border border-warn/40 bg-warn/10 px-3 py-2">
    <p role="status" className="mr-auto text-sm text-warn">{t('Lượt gần nhất đã dùng {percent}% cửa sổ ngữ cảnh', { percent: Math.round(used * 100 / limit) })}</p>
    <Button size="sm" disabled={busy || mutate.isPending} onClick={() => mutate.mutate({ action: 'compact' })}>{t('Tóm tắt ngữ cảnh')}</Button>
    <Button size="sm" disabled={busy || mutate.isPending} onClick={() => mutate.mutate({ action: 'highlights' })}>{t('Lưu điểm nhấn')}</Button>
    <Button size="sm" disabled={busy || mutate.isPending} onClick={newSession}>{t('Phiên mới')}</Button>
    <Modal open={note !== null} onClose={() => setNote(null)} title={t('Lưu điểm nhấn vào bộ nhớ')}
      footer={<Button variant="primary" loading={mutate.isPending} disabled={busy || !note?.trim()} onClick={() => mutate.mutate({ action: 'highlights', note: note ?? '' })}>{t('Lưu')}</Button>}>
      <Textarea rows={8} maxLength={4000} aria-label={t('Điểm nhấn')} value={note ?? ''} onChange={(e) => setNote(e.target.value)} />
    </Modal>
  </div>
}
