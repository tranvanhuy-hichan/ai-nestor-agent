import { useEffect, useState } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { Activity, Cpu, HardDrive, MemoryStick, Radio, RefreshCw, Search, Server, Terminal } from 'lucide-react'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { Card, CardHeader } from '@/components/ui/Card'
import { Input, Select } from '@/components/ui/Form'
import { ErrorNote, Loading, Page } from '@/components/ui/misc'
import { api, ApiError } from '@/lib/api'
import { t } from '@/lib/i18n.ts'

type Gateway = {
  pid: number; started: number; version: string; cpu: number; restart_manager: string | null
  memory_used: number; memory_total: number; disk_used: number; disk_total: number; database_bytes: number
  heartbeat: { enabled: boolean; running: boolean; last_status: string | null }
  mcp: Record<string, string>
  scheduler_running: boolean
  background: { running: number; queued: number }
  channels: Record<string, { enabled: boolean; running: boolean }>
}
type Update = { current: string; latest: string | null; available: boolean }
type Log = { id: number; ts: number; level: string; source: string; message: string }

const bytes = (n: number) => n >= 1024 ** 3 ? `${(n / 1024 ** 3).toFixed(1)} GiB` : `${(n / 1024 ** 2).toFixed(1)} MiB`

function Meter({ label, used, total, detail, icon: Icon }: { label: string; used: number; total: number; detail: string; icon: typeof Cpu }) {
  const percent = total ? Math.min(100, Math.round(used * 100 / total)) : 0
  return <Card className="space-y-3 rounded-xl p-4 sm:p-5">
    <div className="flex items-center justify-between">
      <div className="flex items-center gap-2 text-sm font-medium"><span className="grid size-8 place-items-center rounded-lg bg-accent/10 text-accent"><Icon className="size-4" /></span>{label}</div>
      <span className="text-xl font-semibold tabular-nums">{percent}%</span>
    </div>
    <progress aria-label={label} className="block h-1.5 w-full accent-accent" value={percent} max={100} />
    <p className="text-xs tabular-nums text-muted">{detail}</p>
  </Card>
}

function GatewayLogs({ paused }: { paused: boolean }) {
  const [level, setLevel] = useState('')
  const [search, setSearch] = useState('')
  const [entries, setEntries] = useState<Log[]>([])
  const [state, setState] = useState<'loading' | 'live' | 'retry'>('loading')
  useEffect(() => {
    if (paused) return
    let stream: EventSource | undefined
    const timeout = window.setTimeout(() => {
      setEntries([])
      setState('loading')
      const params = new URLSearchParams({ level, q: search })
      stream = new EventSource(`/api/gateway/logs?${params}`)
      stream.onopen = () => setState('live')
      stream.onerror = () => setState('retry')
      stream.onmessage = (event) => {
        const entry = JSON.parse(event.data) as Log
        setEntries((prev) => prev.at(-1) && prev.at(-1)!.id >= entry.id ? [entry] : [...prev.slice(-499), entry])
      }
    }, 200)
    return () => { window.clearTimeout(timeout); stream?.close() }
  }, [level, search, paused])
  return <Card className="overflow-hidden rounded-xl">
    <CardHeader title={<span className="flex items-center gap-2"><Terminal className="size-4 text-accent" />{t('Nhật ký máy chủ')}</span>} action={<Badge tone={state === 'live' ? 'ok' : 'warn'}>{state === 'live' ? t('Trực tiếp') : state === 'retry' ? t('Đang kết nối lại') : t('Đang kết nối')}</Badge>} />
    <div className="space-y-3 p-4">
      <div className="flex flex-wrap gap-2">
        <div className="relative min-w-40 flex-1"><Search className="pointer-events-none absolute left-3 top-3 size-4 text-muted" /><Input className="pl-9" aria-label={t('Tìm trong nhật ký')} placeholder={t('Tìm trong nhật ký')} value={search} onChange={(e) => setSearch(e.target.value)} /></div>
        <Select className="w-auto" aria-label={t('Mức log')} value={level} onChange={(e) => setLevel(e.target.value)}>
          <option value="">{t('Mọi mức log')}</option>
          {['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'].map((value) => <option key={value}>{value}</option>)}
        </Select>
      </div>
      <div className="max-h-[24rem] overflow-auto rounded-lg border border-line bg-bg font-mono text-xs" tabIndex={0} aria-label={t('Dòng nhật ký')}>
        {!entries.length && <p className="p-6 text-center text-muted">{t('Chưa có dòng nhật ký phù hợp.')}</p>}
        {entries.slice().reverse().map((line) => <div key={line.id} className="border-b border-line/50 px-3 py-2 last:border-b-0">
          <time className="text-muted">{new Date(line.ts * 1000).toLocaleTimeString()}</time>{' '}
          <span className={line.level === 'ERROR' || line.level === 'CRITICAL' ? 'text-bad' : line.level === 'WARNING' ? 'text-warn' : 'text-info'}>{line.level}</span>{' '}
          <span className="text-muted">{line.source}</span>{' '}
          <span className="whitespace-pre-wrap break-all">{line.message}</span>
        </div>)}
      </div>
    </div>
  </Card>
}

export function GatewayPage() {
  const gateway = useQuery({ queryKey: ['gateway'], queryFn: () => api.get<Gateway>('/api/gateway'), refetchInterval: 4000, retry: (count, error) => !(error instanceof ApiError && error.status === 404) && count < 2 })
  const [restarting, setRestarting] = useState<{ started: number; deadline: number } | null>(null)
  const [now, setNow] = useState(Date.now)
  const check = useMutation({ mutationFn: () => api.get<Update>('/api/gateway/updates') })
  const restart = useMutation({
    mutationFn: (started: number) => api.post('/api/gateway/restart').then(() => started),
    onSuccess: (started) => setRestarting({ started, deadline: Date.now() + 30_000 }),
  })
  useEffect(() => {
    if (!restarting) return
    const timer = window.setInterval(() => setNow(Date.now()), 1000)
    return () => window.clearInterval(timer)
  }, [restarting])
  const data = gateway.data
  const restartDone = restarting && data && data.started !== restarting.started
  const waiting = restarting && !restartDone && now < restarting.deadline
  const failed = restarting && !restartDone && !waiting
  const outdated = gateway.error instanceof ApiError && gateway.error.status === 404
  return <Page>
    <div className="w-full space-y-5 pb-8">
      <header className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <div className="mb-3 grid size-11 place-items-center rounded-xl bg-accent/10 text-accent"><Activity className="size-5" /></div>
          <h1 className="text-2xl font-semibold tracking-tight sm:text-3xl">{t('Sức khỏe hệ thống')}</h1>
        </div>
        {data && <div className="flex flex-wrap gap-2">
          <Button loading={check.isPending} onClick={() => check.mutate()}>{t('Kiểm tra cập nhật')}</Button>
          {data.restart_manager && <Button loading={restart.isPending} disabled={!!waiting}
            onClick={() => { if (confirm(t('Khởi động lại Gateway sẽ ngắt các phiên đang chạy. Tiếp tục?'))) restart.mutate(data.started) }}>
            <RefreshCw className="size-4" />{t('Khởi động lại Gateway')}
          </Button>}
        </div>}
      </header>
      {gateway.isPending && <Loading />}
      {gateway.isError && !waiting && <Card className="flex flex-wrap items-center gap-4 rounded-xl p-5">
        <span className="grid size-10 place-items-center rounded-lg bg-warn/10 text-warn"><Server className="size-5" /></span>
        <div className="min-w-52 flex-1">
          <h2 className="font-semibold">{outdated ? t('Gateway cần khởi động lại') : t('Mất kết nối với Gateway')}</h2>
          <p className="mt-1 text-sm text-muted">{outdated ? t('Giao diện đã cập nhật. Hãy khởi động lại tiến trình Gateway để tải API mới.') : gateway.error.message}</p>
        </div>
        <Button onClick={() => void gateway.refetch()} loading={gateway.isFetching}>{t('Thử lại')}</Button>
      </Card>}
      {data && !outdated && <>
        <Card className="flex flex-wrap items-center gap-3 rounded-xl p-4 sm:p-5">
          <span className="grid size-10 shrink-0 place-items-center rounded-lg bg-ok/10 text-ok"><Server className="size-5" /></span>
          <div className="mr-auto">
            <div className="flex flex-wrap items-center gap-2 font-semibold">Gateway <Badge tone={waiting ? 'warn' : gateway.isError ? 'bad' : 'ok'}>{waiting ? t('Đang khởi động lại') : gateway.isError ? t('Mất kết nối với Gateway') : t('Đang hoạt động')}</Badge></div>
            <p className="mt-1 text-xs text-muted">v{data.version} · PID {data.pid}</p>
          </div>
          <span className="rounded-lg bg-panel2 px-3 py-2 text-xs text-muted">SQLite <b className="ml-1 font-medium text-fg">{bytes(data.database_bytes)}</b></span>
          {restartDone && <p role="status" className="w-full text-sm text-ok">{t('Gateway đã khởi động lại.')}</p>}
          {failed && <p role="status" className="w-full text-sm text-bad">{t('Chưa thấy Gateway khởi động lại.')}</p>}
          {check.data && <p role="status" className="w-full text-sm text-muted">
            {check.data.available ? t('Có bản mới {version}', { version: check.data.latest ?? '' }) : check.data.latest ? check.data.latest.replace(/^v/, '') === check.data.current.replace(/^v/, '') ? t('Bạn đang dùng bản mới nhất ({version})', { version: check.data.latest }) : t('Bản phát hành mới nhất {version}', { version: check.data.latest }) : t('Chưa có bản phát hành để đối chiếu.')}
          </p>}
          {(check.error || restart.error) && <ErrorNote error={check.error ?? restart.error} />}
        </Card>
        <div className="grid gap-3 sm:grid-cols-3">
          <Meter icon={Cpu} label="CPU" used={data.cpu} total={100} detail={t('Tải bộ xử lý')} />
          <Meter icon={MemoryStick} label="RAM" used={data.memory_used} total={data.memory_total} detail={`${bytes(data.memory_used)} / ${bytes(data.memory_total)}`} />
          <Meter icon={HardDrive} label={t('Ổ đĩa')} used={data.disk_used} total={data.disk_total} detail={`${bytes(data.disk_used)} / ${bytes(data.disk_total)}`} />
        </div>
        <div className="grid items-start gap-4 xl:grid-cols-[minmax(0,1fr)_17rem]">
          <GatewayLogs paused={!!waiting || gateway.isError} />
          <Card className="overflow-hidden rounded-xl">
            <CardHeader title={<span className="flex items-center gap-2"><Radio className="size-4 text-accent" />{t('Dịch vụ')}</span>} />
            <div className="divide-y divide-line px-4 text-sm">
              <div className="flex items-center justify-between gap-2 py-3">{t('Lịch tự động')} <Badge tone={data.scheduler_running ? 'ok' : 'warn'}>{data.scheduler_running ? t('Đang chạy') : t('Đã dừng')}</Badge></div>
              <div className="flex items-center justify-between gap-2 py-3">Heartbeat <Badge tone={data.heartbeat.enabled ? 'ok' : undefined}>{data.heartbeat.running ? t('Đang chạy') : data.heartbeat.enabled ? t('Đã bật') : t('Đã tắt')}</Badge></div>
              <div className="py-3 text-xs text-muted">{t('Việc nền đang chạy {running} · Đang chờ {queued}', data.background)}</div>
              {Object.entries(data.channels).map(([name, channel]) => <div key={name} className="flex items-center justify-between gap-2 py-3">
                {name} <Badge tone={channel.running ? 'ok' : channel.enabled ? 'warn' : undefined}>{channel.running ? t('Đang chạy') : channel.enabled ? t('Chưa kết nối') : t('Đã tắt')}</Badge>
              </div>)}
            </div>
            {Object.keys(data.mcp).length > 0 && <details className="border-t border-line px-4 py-3 text-sm">
              <summary className="cursor-pointer font-medium">MCP <span className="ml-1 text-muted">{Object.values(data.mcp).filter((status) => status === 'connected').length}/{Object.keys(data.mcp).length}</span></summary>
              <ul className="mt-2 space-y-2">{Object.entries(data.mcp).map(([name, status]) => <li key={name} className="flex items-center justify-between gap-2 break-all">{name} <Badge tone={status === 'connected' ? 'ok' : undefined}>{status}</Badge></li>)}</ul>
            </details>}
          </Card>
        </div>
      </>}
    </div>
  </Page>
}
