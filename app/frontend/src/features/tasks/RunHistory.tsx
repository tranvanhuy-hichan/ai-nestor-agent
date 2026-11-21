import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { Badge } from '@/components/ui/Badge'
import { ErrorNote, Loading } from '@/components/ui/misc'
import { api } from '@/lib/api'
import { t, tk } from '@/lib/i18n.ts'
import { fmtDateTime } from '@/lib/utils'

type Status = 'running' | 'waiting' | 'ok' | 'error' | 'interrupted' | 'cancelled'
export type WorkRun = {
  id: string; kind: 'chat' | 'cron'; title: string; session_id: string | null
  trigger: 'manual' | 'scheduled'; status: Status; started: number; finished: number | null
  output: string; files: string[]
}

const labels = {
  running: [tk('Đang chạy'), 'info'], waiting: [tk('Chờ bạn phản hồi'), 'warn'],
  ok: [tk('Hoàn tất'), 'ok'], error: [tk('Lỗi'), 'bad'],
  interrupted: [tk('Bị gián đoạn'), 'warn'], cancelled: [tk('Đã hủy'), 'neutral'],
} as const

export function useRunHistory(jobId?: string, enabled = true) {
  const url = jobId ? `/api/automations/${jobId}/runs` : '/api/kanban/runs'
  return useQuery({ queryKey: ['work-runs', jobId ?? 'board'], queryFn: () => api.get<WorkRun[]>(url), enabled, refetchInterval: 3000 })
}

export function RunDetails({ run, showTitle = true }: { run: WorkRun; showTitle?: boolean }) {
  const [label, tone] = labels[run.status]
  const duration = run.finished !== null ? Math.max(0, Math.round(run.finished - run.started)) : null
  return <article className="min-w-0 space-y-2 rounded-xl border border-line bg-panel p-3">
    <div className="flex flex-wrap items-center gap-2">
      <Badge tone={tone}>{t(label)}</Badge>
      <span className="text-xs text-muted">{run.kind === 'chat' ? t('Trò chuyện') : run.trigger === 'scheduled' ? t('Theo lịch') : t('Chạy thủ công')}</span>
    </div>
    {showTitle && <h3 className="break-words text-sm font-medium">{run.title}</h3>}
    <p className="text-xs text-muted">
      {fmtDateTime(run.started)}
      {duration !== null && <span> · {t('{n} giây', { n: duration })}</span>}
    </p>
    {run.output && <details className="text-xs">
      <summary className="cursor-pointer text-muted">{t('Kết quả')}</summary>
      <p className="mt-2 max-h-48 overflow-auto whitespace-pre-wrap break-words">{run.output}</p>
    </details>}
    {run.session_id && <div className="flex flex-wrap gap-x-3 gap-y-1 text-xs">
      <Link className="text-accent hover:underline" to={`/chat?session=${run.session_id}`}>{t('Xem hội thoại')}</Link>
      {run.files.map((file) => <a key={file} className="max-w-full truncate text-accent hover:underline" title={file}
        href={`/api/sessions/${run.session_id}/file?path=${encodeURIComponent(file)}&raw=true`} download={file.split('/').pop()}>
        {file}
      </a>)}
    </div>}
  </article>
}

const lanes: { name: string; statuses: Status[] }[] = [
  { name: tk('Đang chạy'), statuses: ['running'] },
  { name: tk('Chờ bạn phản hồi'), statuses: ['waiting'] },
  { name: tk('Hoàn tất'), statuses: ['ok'] },
  { name: tk('Lỗi hoặc đã dừng'), statuses: ['error', 'interrupted', 'cancelled'] },
]

export function RunBoard() {
  const runs = useRunHistory()
  return <section className="mt-8 space-y-3">
    <h2 className="text-base font-semibold">{t('Lượt chat và automation')}</h2>
    {runs.isLoading ? <Loading /> : runs.error ? <ErrorNote error={runs.error} /> : (
      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        {lanes.map(({ name, statuses }) => {
          const cards = (runs.data ?? []).filter((run) => statuses.includes(run.status))
          return <section key={name} className="min-w-0 space-y-2 rounded-xl border border-line bg-panel2/50 p-3">
            <h3 className="text-sm font-medium">{t(name)} <span className="text-muted">{cards.length}</span></h3>
            {cards.length ? <div className="max-h-[30rem] space-y-2 overflow-auto">{cards.map((run) => <RunDetails key={run.id} run={run} />)}</div>
              : <p className="py-2 text-xs text-muted">{t('Chưa có lượt chạy')}</p>}
          </section>
        })}
      </div>
    )}
  </section>
}
