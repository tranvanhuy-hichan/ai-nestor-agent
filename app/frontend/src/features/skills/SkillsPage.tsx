import { useMemo, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { Compass, PackagePlus, Plus, Puzzle, Settings2 } from 'lucide-react'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { EmptyState, ErrorNote, Loading, Page, PageHeader } from '@/components/ui/misc'
import { paginate, Pagination } from '@/components/ui/Pagination'
import { Switch } from '@/components/ui/Switch'
import { SearchBox } from '@/components/ui/SearchBox'
import { Tabs } from '@/components/ui/Tabs'
import { useToast } from '@/components/ui/Toast'
import { useConfig, useSaveConfig, useSkills, useSkillUpdates } from '@/lib/queries'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '@/lib/api'
import type { Skill } from '@/lib/types'
import { cn, errMsg } from '@/lib/utils'
import { CreateSkillModal } from './CreateSkillModal'
import { Discover } from './Discover'
import { Picks } from './Picks'
import { InstallHelp, binsOf } from './InstallHelp'
import { SkillModal } from './SkillModal'
import { t, tk } from '@/lib/i18n.ts'

const CATEGORIES: { id: string; label: string }[] = [
  { id: 'all', label: tk('Tất cả') },
  { id: 'dev', label: tk('Lập trình & Web') },
  { id: 'agents', label: tk('Tự động hóa & Agents') },
  { id: 'productivity', label: tk('Văn phòng & Năng suất') },
  { id: 'devops', label: tk('DevOps & MLOps') },
  { id: 'creative', label: tk('Sáng tạo & Media') },
  { id: 'research', label: tk('Nghiên cứu & Dữ liệu') },
  { id: 'security', label: tk('Bảo mật') },
  { id: 'finance', label: tk('Tài chính') },
  { id: 'communication', label: tk('Giao tiếp & MXH') },
  { id: 'tools', label: tk('Công cụ & MCP') },
  { id: 'general', label: tk('Chung') },
]

export function missingText(m: string): string {
  const [kind, ...rest] = m.split(':')
  const v = rest.join(':')
  return ({ bin: t('Thiếu lệnh: {v}', { v }), anyBin: t('Cần một trong: {v}', { v: v.replace(/\|/g, ', ') }), env: t('Thiếu biến môi trường: {v}', { v }), os: t('Chỉ hỗ trợ: {v}', { v }), config: t('Cần cấu hình riêng: {v}', { v }) } as Record<string, string>)[kind] ?? m
}

export function SkillIcon({ emoji }: { emoji?: string }) {
  return <div className="grid size-10 shrink-0 place-items-center rounded-xl bg-panel2 text-xl">{emoji || <Puzzle className="size-5 text-muted" />}</div>
}

export function SkillsPage() {
  const skills = useSkills()
  const cfg = useConfig()
  const save = useSaveConfig()
  const updates = useSkillUpdates()
  const qc = useQueryClient()
  const update = useMutation({
    mutationFn: (name: string) => api.post(`/api/skills/${name}/update`),
    onSuccess: () => { toast(t('Đã cập nhật skill')); void qc.invalidateQueries({ queryKey: ['skills'] }); void qc.invalidateQueries({ queryKey: ['skill-updates'] }) },
    onError: (e) => toast(errMsg(e), 'bad'),
  })
  const toast = useToast()
  const [params, setParams] = useSearchParams()
  const tab = params.get('tab') === 'discover' ? 'discover' : params.get('tab') === 'picks' ? 'picks' : 'installed'
  const setTab = (t: 'installed' | 'picks' | 'discover') => setParams(t === 'installed' ? {} : { tab: t }, { replace: true })
  const [filter, setFilter] = useState('')
  const [cat, setCat] = useState('all')
  const [hubInput, setHubInput] = useState('')
  const [selected, setSelected] = useState<string | null>(null)
  const [creating, setCreating] = useState(false)
  const [page, setPage] = useState(0)
  const PAGE_SIZE = 20

  const toggle = (s: Skill, enabled: boolean) => {
    if (!cfg.data) return
    const c = structuredClone(cfg.data.config)
    c.skills[s.name] = { ...(c.skills[s.name] ?? { api_key: '', env: {} }), enabled }
    save.mutate(c, { onError: (e) => toast(errMsg(e), 'bad') })
  }

  const categoryCounts = useMemo(() => {
    const counts: Record<string, number> = { all: skills.data?.length ?? 0 }
    for (const s of skills.data ?? []) {
      const c = s.category || 'general'
      counts[c] = (counts[c] || 0) + 1
    }
    return counts
  }, [skills.data])

  const list = (skills.data ?? []).filter((s) => {
    const matchesCat = cat === 'all' || (s.category || 'general') === cat
    const matchesFilter = !filter || `${s.name} ${s.description}`.toLowerCase().includes(filter.toLowerCase())
    return matchesCat && matchesFilter
  })
  const pageList = paginate(list, page, PAGE_SIZE)

  return (
    <Page>
      <PageHeader title={t('Kỹ năng')} />
      <Tabs
        value={tab}
        onChange={setTab}
        tabs={[{ id: 'installed', label: t('Đã cài'), count: skills.data?.length }, { id: 'picks', label: t('Gợi ý cho bạn') }, { id: 'discover', label: t('Khám phá ClawHub') }]}
        right={<div className="flex flex-wrap items-center gap-2">
          {tab === 'discover'
            ? <SearchBox value={hubInput} onChange={setHubInput} placeholder={t('Tìm skill trên ClawHub (vd: weather, github, notion…)')} label={t('Tìm skill')} />
            : <SearchBox value={filter} onChange={(v) => { setFilter(v); setPage(0) }} placeholder={t('Lọc skill đã cài…')} label={t('Lọc skill')} />}
          <Button variant="primary" onClick={() => setCreating(true)}><Plus className="size-4" />{t('Tạo skill')}</Button>
        </div>}
      />
      <div className="mt-5">
        {tab === 'picks' ? (
          <Picks installed={skills.data ?? []} />
        ) : tab === 'discover' ? (
          <Discover installed={skills.data ?? []} input={hubInput} />
        ) : skills.isLoading ? (
          <Loading />
        ) : skills.error ? (
          <ErrorNote error={skills.error} />
        ) : (
          <>
            <div className="mb-4 flex flex-wrap gap-1.5 overflow-x-auto pb-1">
              {CATEGORIES.map((c) => {
                const count = categoryCounts[c.id] || 0
                if (c.id !== 'all' && !count) return null
                const active = cat === c.id
                return (
                  <button
                    key={c.id}
                    onClick={() => { setCat(c.id); setPage(0) }}
                    className={cn(
                      'inline-flex items-center gap-1.5 rounded-lg border px-3 py-1.5 text-xs font-medium transition',
                      active
                        ? 'border-accent bg-accent text-accent-fg shadow-sm'
                        : 'border-line bg-panel2 text-muted hover:border-line2 hover:text-text'
                    )}
                  >
                    <span>{t(c.label)}</span>
                    <span className={cn('rounded px-1.5 py-0.5 text-[10px]', active ? 'bg-white/20 text-white' : 'bg-panel text-muted')}>
                      {count}
                    </span>
                  </button>
                )
              })}
            </div>
            {list.length === 0 ? (
              <EmptyState icon={PackagePlus} title={t('Chưa có skill nào')} action={<Button onClick={() => setTab('picks')}><Compass className="size-4" />{t('Gợi ý cho bạn')}</Button>} />
            ) : (
              <div className="overflow-hidden rounded-xl border border-line bg-panel">
                {pageList.map((s) => (
                  <div key={s.name} className="flex items-center gap-4 border-b border-line px-4 py-3.5 last:border-b-0">
                    <SkillIcon emoji={s.emoji} />
                    <div className="min-w-0 flex-1"><button onClick={() => setSelected(s.name)} className="w-full text-left">
                      <div className="flex flex-wrap items-center gap-2">
                        <span className="font-medium">{s.name}</span>
                        {s.category && s.category !== 'general' && (
                          <Badge tone="neutral">
                            {t(CATEGORIES.find((c) => c.id === s.category)?.label || s.category)}
                          </Badge>
                        )}
                        {s.origin && <Badge tone="info">ClawHub · {s.origin.owner}{s.origin.version ? ` v${s.origin.version}` : ''}</Badge>}
                        {!s.eligible && <Badge tone="warn">{t('Cần thiết lập')}</Badge>}
                        {!s.enabled && <Badge>{t('Tạm tắt')}</Badge>}
                      </div>
                      <p className="mt-0.5 line-clamp-2 text-[13px] text-muted">{s.description || t('Không có mô tả')}</p>
                      {!s.eligible && <p className="mt-1 text-xs text-warn">{s.missing.map(missingText).join(' · ')}</p>}
                    </button>{!s.eligible && <InstallHelp bins={binsOf(s.missing)} />}</div>
                    {updates.data?.find((u) => u.name === s.name) && (
                      <Button size="sm" variant="primary" loading={update.isPending && update.variables === s.name} onClick={() => update.mutate(s.name)}>{t('Cập nhật v{v}', { v: updates.data.find((u) => u.name === s.name)?.latest ?? '' })}</Button>
                    )}
                    <Button variant="ghost" size="sm" onClick={() => setSelected(s.name)} aria-label={t('Cấu hình {name}', { name: s.name })}><Settings2 className="size-4" /></Button>
                    <Switch checked={s.enabled} onChange={(v) => toggle(s, v)} label={t('Bật {name}', { name: s.name })} />
                  </div>
                ))}
                <Pagination page={page} pageSize={PAGE_SIZE} total={list.length} onPageChange={setPage} />
              </div>
            )}
          </>
        )}
      </div>
      <SkillModal name={selected} onClose={() => setSelected(null)} />
      <CreateSkillModal open={creating} onClose={() => setCreating(false)} />
    </Page>
  )
}
