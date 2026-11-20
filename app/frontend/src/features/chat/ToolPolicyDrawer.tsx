import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { X } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { Field, Input, Select } from '@/components/ui/Form'
import { ErrorNote, Loading } from '@/components/ui/misc'
import { api } from '@/lib/api'
import { t, tk } from '@/lib/i18n.ts'

type Policy = { enabled: boolean; approval: 'inherit' | 'ask' | 'once' | 'auto'; timeout: number | null; output_limit: number | null }
type Tool = { name: string; risk: string; timeout_supported: boolean; base_enabled: boolean; policy: Policy }
const modes: Record<Policy['approval'], string> = {
  inherit: tk('Theo quyền của phiên'), ask: tk('Hỏi mỗi lần'), once: tk('Hỏi một lần cho cùng tham số trong lượt'), auto: tk('Tự duyệt trong Chat web'),
}

function ToolPolicyForm({ tool }: { tool: Tool }) {
  const [policy, setPolicy] = useState(tool.policy)
  const qc = useQueryClient()
  const save = useMutation({
    mutationFn: () => api.put(`/api/tool-policies/${encodeURIComponent(tool.name)}`, policy),
    onSuccess: () => { void qc.invalidateQueries({ queryKey: ['tool-policies'] }); void qc.invalidateQueries({ queryKey: ['config'] }) },
  })
  const update = <K extends keyof Policy>(key: K, value: Policy[K]) => setPolicy((prev) => ({ ...prev, [key]: value }))
  return <form className="space-y-4" onSubmit={(e) => { e.preventDefault(); save.mutate() }}>
    <label className="flex items-center gap-2 text-sm">
      <input type="checkbox" checked={policy.enabled} onChange={(e) => update('enabled', e.target.checked)} />
      {t('Bật công cụ')}
    </label>
    {!tool.base_enabled && <p className="text-sm text-warn">{t('Công cụ đang tắt trong Cài đặt.')}</p>}
    <Field label={t('Phê duyệt')}>
      <Select value={policy.approval} onChange={(e) => update('approval', e.target.value as Policy['approval'])}>
        {Object.entries(modes).map(([value, label]) => <option key={value} value={value}>{t(label)}</option>)}
      </Select>
    </Field>
    {tool.timeout_supported && <Field label={t('Thời hạn tối đa (giây)')}>
      <Input type="number" min={1} max={300} value={policy.timeout ?? ''} placeholder={t('Mặc định')} onChange={(e) => update('timeout', e.target.value ? e.target.valueAsNumber : null)} />
    </Field>}
    <Field label={t('Giới hạn đầu ra (ký tự)')}>
      <Input type="number" min={100} max={100000} value={policy.output_limit ?? ''} placeholder={t('Mặc định')} onChange={(e) => update('output_limit', e.target.value ? e.target.valueAsNumber : null)} />
    </Field>
    {save.isError && <ErrorNote error={save.error} />}
    <div className="flex items-center gap-3"><Button variant="primary" type="submit" loading={save.isPending}>{t('Lưu')}</Button>
      {save.isSuccess && JSON.stringify(policy) === JSON.stringify(tool.policy) && <span role="status" className="text-sm text-ok">{t('Đã lưu')}</span>}
    </div>
  </form>
}

export function ToolPolicyDrawer({ close }: { close: () => void }) {
  const tools = useQuery({ queryKey: ['tool-policies'], queryFn: () => api.get<Tool[]>('/api/tool-policies') })
  const [query, setQuery] = useState('')
  const [selected, select] = useState('')
  const visible = (tools.data ?? []).filter((tool) => tool.name.toLowerCase().includes(query.toLowerCase()))
  const current = visible.find((tool) => tool.name === selected) ?? visible[0]
  return <div className="fixed inset-0 z-50 bg-black/60" onMouseDown={close}>
    <aside aria-modal="true" role="dialog" aria-label={t('Quyền công cụ')} onMouseDown={(e) => e.stopPropagation()}
      onKeyDown={(e) => { if (e.key === 'Escape') close() }} className="absolute inset-y-0 right-0 w-full max-w-md overflow-auto border-l border-line bg-panel p-5">
      <div className="mb-3 flex items-center justify-between">
        <h2 className="font-semibold">{t('Quyền công cụ')}</h2>
        <Button size="sm" variant="ghost" onClick={close} aria-label={t('Đóng')}><X className="size-4" /></Button>
      </div>
      <p className="mb-4 text-sm text-muted">{t('Áp dụng toàn bộ cấu hình Nestor từ lượt chạy tiếp theo.')}</p>
      <Input autoFocus aria-label={t('Tìm công cụ')} placeholder={t('Tìm công cụ')} value={query} onChange={(e) => setQuery(e.target.value)} />
      {tools.isPending && <Loading />}
      {tools.isError && <ErrorNote error={tools.error} />}
      {current && <div className="mt-3 space-y-4">
        <Select aria-label={t('Công cụ')} value={current.name} onChange={(e) => select(e.target.value)}>{visible.map((tool) => <option key={tool.name} value={tool.name}>{tool.name} · {tool.risk}</option>)}</Select>
        <ToolPolicyForm key={current.name} tool={current} />
      </div>}
      {tools.data && !current && <p className="mt-3 text-sm text-muted">{t('Không tìm thấy công cụ.')}</p>}
    </aside>
  </div>
}
