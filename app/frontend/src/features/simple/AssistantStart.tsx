import { X } from 'lucide-react'
import { AgentLogoStacked } from '@/components/ui/AgentMark'
import { assistantIcon } from '@/lib/assistantIcons'
import { FALLBACK_ASSISTANTS, useAssistants, type Assistant } from '@/lib/assistants'
import { t } from '@/lib/i18n.ts'

export function useAssistant(id?: string): Assistant | undefined {
  const list = useAssistants().data ?? FALLBACK_ASSISTANTS
  return id ? list.find((a) => a.id === id) : undefined
}

/** Chip nhỏ trên thanh chat: đang làm việc với trợ lý nào, bấm X để về chế độ tự chọn. */
export function AssistantChip({ a, onClear }: { a: Assistant; onClear: () => void }) {
  const Icon = assistantIcon(a.icon)
  return (
    <span className="flex items-center gap-1.5 rounded-full bg-accent/10 py-1 pl-2 pr-1 text-xs text-accent" title={t(a.description)}>
      <Icon className="size-3.5" />{t(a.name)}
      <button onClick={onClear} aria-label={t('Bỏ chọn')} className="grid size-4 place-items-center rounded-full hover:bg-accent/20"><X className="size-3" /></button>
    </span>
  )
}

/** Màn hình trống của chat ở chế độ Đơn giản: logo hệ thống, không gợi ý. Trợ lý đang dùng (nếu có) chỉ nhắc nhẹ một dòng. */
export function AssistantStart({ active }: { active?: Assistant }) {
  return (
    <div className="flex flex-col items-center pt-[10vh] text-center">
      <AgentLogoStacked large className="mb-5" />
      <h2 className="text-xl font-semibold">{t('Mình có thể giúp gì cho bạn?')}</h2>
      {active && <p className="mt-2 text-sm text-muted">{t('Đang dùng trợ lý {name}.', { name: t(active.name) })}</p>}
    </div>
  )
}
