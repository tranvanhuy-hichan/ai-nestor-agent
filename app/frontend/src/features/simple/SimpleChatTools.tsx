import { useState } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { Check, Pin, CircleCheck, CircleDashed, Loader, Users, type LucideIcon } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { useToast } from '@/components/ui/Toast'
import { api } from '@/lib/api'
import { t } from '@/lib/i18n.ts'
import { errMsg } from '@/lib/utils'
import { SkillDraftButton } from './SkillDraftButton'

type Member = { role: string; status: string; task?: string }
type TeamStatus = { members?: Member[] }

const STATUS: Record<string, { Icon: LucideIcon; cls: string }> = {
  done: { Icon: CircleCheck, cls: 'text-ok' }, running: { Icon: Loader, cls: 'animate-spin text-accent' }, working: { Icon: Loader, cls: 'animate-spin text-accent' },
}
const WAITING = { Icon: CircleDashed, cls: 'text-muted' }

/** Tiến độ tổ công tác (nếu phiên này đang có nhiều trợ lý phối hợp). Không có API thì không hiện gì. */
function TeamProgress({ sid, busy }: { sid: string; busy: boolean }) {
  const q = useQuery({ queryKey: ['team', sid], queryFn: () => api.get<TeamStatus>(`/api/sessions/${sid}/team`), refetchInterval: busy ? 3000 : false, retry: false })
  const m = q.data?.members
  if (!m?.length) return null
  return (
    <div className="flex items-center gap-1.5 rounded-lg bg-panel2 px-2 py-1 text-xs text-muted" title={m.map((x) => `${x.role}: ${x.task ?? x.status}`).join('\n')}>
      <Users className="size-3.5" />
      {m.map((x) => { const { Icon, cls } = STATUS[x.status] ?? WAITING; return <span key={x.role} className="flex items-center gap-1"><Icon className={`size-3.5 ${cls}`} />{x.role}</span> })}
    </div>
  )
}

/** Nút "Làm như lần trước" (lưu thành kỹ năng) và "Ghi nhớ yêu cầu" (lưu thành quy tắc) cho chế độ Đơn giản. */
export function SimpleChatTools({ sid, busy }: { sid: string; busy: boolean }) {
  const toast = useToast()
  const [saved, setSaved] = useState(false)
  const distill = useMutation({
    mutationFn: () => api.post(`/api/sessions/${sid}/distill`, { kind: 'rule' }),
    onSuccess: () => { setSaved(true); toast(t('Đã ghi nhớ thành quy tắc cho các lần sau.')) },
    onError: (e) => toast(errMsg(e), 'bad'),
  })
  return (
    <div className="flex shrink-0 items-center gap-1.5">
      <TeamProgress sid={sid} busy={busy} />
      <SkillDraftButton key={sid} sid={sid} busy={busy} />
      <Button size="sm" className="shrink-0 whitespace-nowrap" disabled={busy} loading={distill.isPending} onClick={() => distill.mutate()} aria-label={t('Ghi nhớ quy tắc')} title={t('Ghi nhớ một yêu cầu cố định, ví dụ: văn bản của phòng luôn ký thừa lệnh')}>
        {saved ? <Check className="size-3.5" /> : <Pin className="size-3.5" />}<span className="hidden 2xl:inline">{t('Ghi nhớ quy tắc')}</span>
      </Button>
    </div>
  )
}
