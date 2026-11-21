import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { BookmarkPlus } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { Field, Input, Select, Textarea } from '@/components/ui/Form'
import { Modal } from '@/components/ui/Modal'
import { useToast } from '@/components/ui/Toast'
import { api } from '@/lib/api'
import { t } from '@/lib/i18n.ts'
import { errMsg } from '@/lib/utils'

type SkillText = { name: string; description: string; body: string }
type Candidate = SkillText & { revision: string }
type Draft = SkillText & { matches: Candidate[] }

export function SkillDraftButton({ sid, busy }: { sid: string; busy: boolean }) {
  const toast = useToast()
  const qc = useQueryClient()
  const [draft, setDraft] = useState<Draft | null>(null)
  const [target, setTarget] = useState('')
  const current = draft?.matches.find((entry) => entry.name === target)
  const generate = useMutation({
    mutationFn: () => api.post<Draft>(`/api/sessions/${sid}/skill-draft`, {}),
    onSuccess: (result) => {
      setDraft(result)
      setTarget(result.matches.find((entry) => entry.name === result.name)?.name ?? '')
    },
    onError: (error) => toast(errMsg(error), 'bad'),
  })
  const save = useMutation({
    mutationFn: (value: SkillText & { revision?: string }) => api.post('/api/skills/draft/save', value),
    onSuccess: () => {
      setDraft(null)
      void qc.invalidateQueries({ queryKey: ['skills'] })
      toast(t('Đã lưu kỹ năng'))
    },
    onError: (error) => toast(errMsg(error), 'bad'),
  })
  const close = () => { if (!save.isPending) setDraft(null) }
  return <>
    <Button size="sm" className="shrink-0 whitespace-nowrap" disabled={busy} loading={generate.isPending} onClick={() => generate.mutate()} aria-label={t('Lưu thành kỹ năng')} title={t('Tạo bản nháp kỹ năng từ hội thoại')}>
      <BookmarkPlus className="size-3.5" /><span className="hidden 2xl:inline">{t('Lưu thành kỹ năng')}</span>
    </Button>
    {draft && <Modal open wide onClose={close} title={t('Xem trước kỹ năng')}
      footer={<><Button onClick={close} disabled={save.isPending}>{t('Hủy')}</Button>
        <Button variant="primary" loading={save.isPending}
          disabled={(!current && !/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(draft.name)) || !draft.description.trim() || !draft.body.trim()}
          onClick={() => save.mutate({ name: current?.name ?? draft.name, description: draft.description, body: draft.body, revision: current?.revision })}>
          {current ? t('Cập nhật kỹ năng') : t('Lưu kỹ năng mới')}
        </Button></>}>
      <div className="space-y-3">
        {!!draft.matches.length && <Field label={t('Lưu vào')}>
          <Select value={target} onChange={(event) => setTarget(event.target.value)}>
            <option value="">{t('Kỹ năng mới')}</option>
            {draft.matches.map((entry) => <option key={entry.name}>{entry.name}</option>)}
          </Select>
        </Field>}
        {!current && <Field label={t('Tên kỹ năng')}>
          <Input value={draft.name} maxLength={80} onChange={(event) => setDraft({ ...draft, name: event.target.value })} />
        </Field>}
        <div className={current ? 'grid gap-4 sm:grid-cols-2' : ''}>
          {current && <div className="min-w-0 space-y-3 rounded-xl border border-line bg-panel2 p-3">
            <h3 className="text-sm font-semibold">{t('Kỹ năng hiện tại')}</h3>
            <p className="text-sm text-muted">{current.description}</p>
            <pre className="max-h-72 overflow-auto whitespace-pre-wrap break-words text-xs">{current.body}</pre>
          </div>}
          <div className="min-w-0 space-y-3">
            <Field label={t('Mô tả')}><Input value={draft.description} maxLength={500} onChange={(event) => setDraft({ ...draft, description: event.target.value })} /></Field>
            <Field label={t('Bản nháp Markdown')}><Textarea rows={12} className="font-mono text-xs" value={draft.body} maxLength={100_000} onChange={(event) => setDraft({ ...draft, body: event.target.value })} /></Field>
          </div>
        </div>
      </div>
    </Modal>}
  </>
}
