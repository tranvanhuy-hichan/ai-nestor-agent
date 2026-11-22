import { useDialogs } from '@/components/ui/Dialogs'
import { useState } from 'react'
import { ArrowRight, Plus, Sparkles, MessageSquare, Pencil, Trash2 } from 'lucide-react'
import { assistantIcon } from '@/lib/assistantIcons'
import { Link } from 'react-router-dom'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { Field, Input, Select, Textarea } from '@/components/ui/Form'
import { Modal } from '@/components/ui/Modal'
import { ErrorNote, Loading, Page } from '@/components/ui/misc'
import { useToast } from '@/components/ui/Toast'
import { api } from '@/lib/api'
import { GROUPS, type Assistant } from '@/lib/assistants'
import { useConfig, useSkills } from '@/lib/queries'
import { t } from '@/lib/i18n.ts'
import { errMsg } from '@/lib/utils'

type Draft = Pick<Assistant, 'id' | 'name' | 'description' | 'group' | 'icon' | 'starters' | 'done_criteria' | 'deliverables'> & {
  prompt: string; skills: string[]; providers: string[]; tools: string[] | null; scoped: boolean; env_refs?: Record<string, string>
}
const blank: Draft = { id: '', name: '', description: '', group: 'ca-nhan', icon: 'bot', starters: [], prompt: '', skills: [], providers: [], tools: null, scoped: true }

function profileId(name: string) {
  return name.toLowerCase().normalize('NFD').replace(/\p{M}/gu, '').replace(/\u0111/g, 'd')
    .replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '').slice(0, 41)
}

function toggle(list: string[], key: string) {
  return list.includes(key) ? list.filter((x) => x !== key) : [...list, key]
}

function Choices({ options, selected, change }: { options: string[]; selected: string[]; change: (value: string[]) => void }) {
  return <div className="grid max-h-48 gap-1 overflow-auto rounded-lg border border-line p-2 sm:grid-cols-2">
    {options.map((option) => <label key={option} className="flex items-center gap-2 text-sm">
      <input type="checkbox" checked={selected.includes(option)} onChange={() => change(toggle(selected, option))} />
      <span className="break-all">{option}</span>
    </label>)}
  </div>
}

function ProfileEditor({ initial, editing, close }: { initial: Draft; editing: boolean; close: () => void }) {
  const [draft, setDraft] = useState(initial)
  const [step, setStep] = useState(0)
  const [customId, setCustomId] = useState(false)
  const [env, setEnv] = useState(() => Object.entries(initial.env_refs ?? {}).map(([name, source]) => `${name}=${source}`).join('\n'))
  const envLines = env.split('\n').map((line) => line.trim()).filter(Boolean)
  const validEnv = envLines.length <= 20 && envLines.every((line) => /^[A-Za-z_][A-Za-z0-9_]{0,127}=[A-Za-z_][A-Za-z0-9_]{0,127}$/.test(line))
  const skills = useSkills()
  const config = useConfig()
  const policy = useQuery({ queryKey: ['tool-policies'], queryFn: () => api.get<{ name: string }[]>('/api/tool-policies') })
  const toast = useToast()
  const qc = useQueryClient()
  const save = useMutation({
    mutationFn: () => (editing ? api.put : api.post)(`/api/assistants/${draft.id}`, { ...draft, env_refs: Object.fromEntries(envLines.map((line) => line.split('='))) }),
    onSuccess: () => { void qc.invalidateQueries({ queryKey: ['profiles'] }); void qc.invalidateQueries({ queryKey: ['assistants'] }); close() },
    onError: (e) => toast(errMsg(e), 'bad'),
  })
  const valid = /^[a-z0-9][a-z0-9-]{0,40}$/.test(draft.id) && draft.name.trim() && draft.prompt.trim()
  const change = <K extends keyof Draft>(key: K, value: Draft[K]) => setDraft((prev) => ({ ...prev, [key]: value }))
  const providers = Object.keys(config.data?.config.providers ?? {})
  const availableSkills = [...new Set([...(skills.data ?? []).map((s) => s.name), ...draft.skills])]
  const availableTools = [...new Set([...(policy.data ?? []).map((tool) => tool.name), ...(draft.tools ?? [])])]
  return <Modal open wide onClose={close} title={editing ? t('Chỉnh sửa hồ sơ') : t('Tạo hồ sơ')}
    footer={<>
      {step > 0 && <Button onClick={() => setStep(0)}>{t('Quay lại')}</Button>}
      {step === 0 ? <Button variant="primary" disabled={!valid} onClick={() => setStep(1)}>{t('Tiếp tục')}</Button>
        : <Button variant="primary" loading={save.isPending} disabled={!validEnv} onClick={() => save.mutate()}>{t('Lưu')}</Button>}
    </>}>
    {step === 0 ? <div className="space-y-3">
      <div className="grid gap-3 sm:grid-cols-2">
        <Field label={t('Tên hồ sơ')}><Input maxLength={60} value={draft.name} onChange={(e) => { const name = e.target.value; setDraft({ ...draft, name, id: editing || customId ? draft.id : profileId(name) }) }} autoFocus /></Field>
        <Field label={t('Mã hồ sơ')} hint={t('Chữ thường, số và dấu gạch ngang.')}><Input maxLength={41} disabled={editing} value={draft.id} onChange={(e) => { setCustomId(true); change('id', e.target.value) }} /></Field>
      </div>
      <Field label={t('Nhóm')}><Select value={draft.group} onChange={(e) => change('group', e.target.value)}>{Object.entries(GROUPS).map(([id, label]) => <option key={id} value={id}>{t(label)}</option>)}</Select></Field>
      <Field label={t('Mô tả')}><Input maxLength={300} value={draft.description} onChange={(e) => change('description', e.target.value)} /></Field>
      <Field label={t('Hướng dẫn hệ thống')}><Textarea rows={8} maxLength={6000} value={draft.prompt} onChange={(e) => change('prompt', e.target.value)} /></Field>
    </div> : <div className="space-y-4">
      <div><h3 className="mb-1 text-sm font-medium">{t('Mô hình theo thứ tự ưu tiên')}</h3>
        <p className="mb-2 text-xs text-muted">{draft.providers.join(' → ') || t('Dùng cấu hình mặc định')}</p>
        <Choices options={[...new Set([...providers, ...draft.providers])]} selected={draft.providers} change={(value) => change('providers', value)} />
      </div>
      <div><h3 className="mb-2 text-sm font-medium">{t('Kỹ năng')}</h3>
        <Choices options={availableSkills} selected={draft.skills} change={(value) => change('skills', value)} />
      </div>
      {draft.scoped && <Field label={t('Biến môi trường cho lệnh')} hint={t('Mỗi dòng là TÊN_BIẾN=TÊN_BIẾN_MÁY_CHỦ. Giá trị được đọc trên máy chủ khi chạy lệnh.')}>
        <Textarea rows={3} value={env} onChange={(e) => setEnv(e.target.value)} placeholder="SERVICE_TOKEN=MY_SERVICE_TOKEN" />
        {!validEnv && <span className="text-xs text-bad">{t('Nhập tối đa 20 cặp tên biến hợp lệ.')}</span>}
      </Field>}
      <div>
        <label className="mb-2 flex gap-2 text-sm"><input type="checkbox" checked={draft.tools !== null} onChange={(e) => change('tools', e.target.checked ? [] : null)} />{t('Giới hạn công cụ theo danh sách')}</label>
        {draft.tools !== null && <Choices options={availableTools} selected={draft.tools} change={(value) => change('tools', value)} />}
      </div>
    </div>}
  </Modal>
}

export function ProfilesPage() {
  const { confirmAction } = useDialogs()
  const query = useQuery({ queryKey: ['profiles'], queryFn: () => api.get<(Draft & { builtin: boolean })[]>('/api/assistants') })
  const [editor, setEditor] = useState<{ draft: Draft; editing: boolean } | null>(null)
  const qc = useQueryClient()
  const toast = useToast()
  const remove = useMutation({
    mutationFn: (id: string) => api.del(`/api/assistants/${id}`),
    onSuccess: () => { void qc.invalidateQueries({ queryKey: ['profiles'] }); void qc.invalidateQueries({ queryKey: ['assistants'] }) },
    onError: (e) => toast(errMsg(e), 'bad'),
  })
  const profiles = query.data?.filter((p) => !p.builtin) ?? []
  const templates = query.data?.filter((p) => p.builtin) ?? []
  const featured = ['van-thu-nd30', 'ke-toan', 'gia-su'].flatMap((id) => templates.filter((p) => p.id === id))
  const [showAll, setShowAll] = useState(false)
  const create = () => setEditor({ draft: blank, editing: false })
  return <Page>
    <div className="w-full space-y-8 pb-8">
      <header className="relative overflow-hidden rounded-2xl border border-line bg-panel px-5 py-7 sm:px-8 sm:py-9">
        <div aria-hidden className="pointer-events-none absolute -right-24 -top-44 size-96 rounded-full bg-accent/15 blur-3xl" />
        <div className="relative flex flex-wrap items-end justify-between gap-5">
          <div>
            <span className="mb-4 inline-grid size-11 place-items-center rounded-xl bg-accent/12 text-accent"><Sparkles className="size-5" /></span>
            <h1 className="text-2xl font-semibold tracking-tight sm:text-3xl">{t('Hồ sơ trợ lý')}</h1>
            <p className="mt-2 max-w-xl text-sm leading-relaxed text-muted">{t('Mỗi hồ sơ là một cách làm việc của Nestor. Ví dụ, bạn có thể dùng hồ sơ Văn thư để soạn công văn với hướng dẫn, kỹ năng và bộ nhớ riêng.')}</p>
          </div>
          <Button variant="primary" onClick={create}><Plus className="size-4" />{t('Tạo hồ sơ')}</Button>
        </div>
      </header>

      {query.isPending && <Loading />}
      {query.isError && <ErrorNote error={query.error} />}
      {query.data && <section aria-labelledby="my-profiles">
        <h2 id="my-profiles" className="mb-3 text-base font-semibold">{t('Hồ sơ của bạn')}</h2>
        {profiles.length === 0 ? <div className="flex flex-wrap items-center gap-4 rounded-xl border border-dashed border-line p-5">
          <span className="grid size-10 shrink-0 place-items-center rounded-lg bg-panel2 text-muted"><MessageSquare className="size-5" /></span>
          <div><p className="font-medium">{t('Chưa có hồ sơ tùy chỉnh.')}</p><p className="mt-1 text-sm text-muted">{t('Tạo hồ sơ từ đầu hoặc chọn một mẫu bên dưới để chỉnh theo nhu cầu.')}</p></div>
        </div> : <div className="grid gap-3 md:grid-cols-2">{profiles.map((profile) => {
          const Icon = assistantIcon(profile.icon)
          return <Card key={profile.id} className="flex flex-col gap-4 p-4">
            <div className="flex gap-3">
              <span className="grid size-10 shrink-0 place-items-center rounded-lg bg-accent/10 text-accent"><Icon className="size-5" /></span>
              <div><h3 className="font-semibold">{profile.name}</h3>{profile.description && <p className="mt-1 text-sm text-muted">{profile.description}</p>}</div>
            </div>
            <div className="mt-auto flex items-center gap-2 border-t border-line pt-3">
              <Link to={`/chat?profile=${encodeURIComponent(profile.id)}`} className="mr-auto inline-flex items-center gap-2 rounded-lg px-2 py-1.5 text-sm font-medium text-accent hover:bg-accent/10">{t('Trò chuyện')}<ArrowRight className="size-4" /></Link>
              <Button size="sm" variant="ghost" aria-label={t('Sửa')} onClick={() => setEditor({ draft: { ...profile, skills: profile.skills ?? [], providers: profile.providers ?? [] }, editing: true })}><Pencil className="size-4" /></Button>
              <Button size="sm" variant="ghost" aria-label={t('Xóa')} disabled={remove.isPending} onClick={async () => { if (await confirmAction(t('Xóa hồ sơ {name}?', { name: profile.name }), { action: t('Xóa'), danger: true })) remove.mutate(profile.id) }}><Trash2 className="size-4" /></Button>
            </div>
          </Card>
        })}</div>}
      </section>}
      {templates.length > 0 && <section aria-labelledby="profile-templates">
        <div className="mb-3 flex items-center justify-between gap-2">
          <h2 id="profile-templates" className="text-base font-semibold">{t('Mẫu trợ lý')}</h2>
          {templates.length > featured.length && <Button size="sm" variant="ghost" onClick={() => setShowAll(!showAll)}>{showAll ? t('Thu gọn') : t('Xem tất cả mẫu')}</Button>}
        </div>
        <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">{(showAll || !featured.length ? templates : featured).map((template) => {
          const Icon = assistantIcon(template.icon)
          return <button key={template.id} onClick={() => setEditor({ draft: { ...template, id: `${profileId(template.name).slice(0, 33)}-ca-nhan`, scoped: true, providers: [] }, editing: false })}
            className="group flex flex-col items-start gap-3 rounded-xl border border-line bg-panel p-5 text-left transition hover:border-accent/55 hover:bg-panel2 focus-visible:outline-2 focus-visible:outline-accent">
            <span className="grid size-10 place-items-center rounded-lg bg-accent/10 text-accent"><Icon className="size-5" /></span>
            <span className="font-semibold">{template.name}</span>
            <span className="line-clamp-3 text-sm leading-relaxed text-muted">{template.description}</span>
            <span className="mt-auto flex items-center gap-2 pt-1 text-sm font-medium text-accent">{t('Dùng mẫu')}<ArrowRight className="size-4 transition group-hover:translate-x-0.5" /></span>
          </button>
        })}</div>
      </section>}
      {editor && <ProfileEditor initial={editor.draft} editing={editor.editing} close={() => setEditor(null)} />}
    </div>
  </Page>
}
