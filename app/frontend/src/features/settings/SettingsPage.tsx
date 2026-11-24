import { useDialogs } from '@/components/ui/Dialogs'
import { AppearanceCard } from '@/features/settings/AppearanceCard'
import { useId, useLayoutEffect, useRef, useState, type ReactNode } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { ArrowRight, ArrowUpRight, Bot, Brain, DatabaseBackup, Download, Globe, Image, Network, Palette, ScanText, Search, Shield, Upload, Wrench, X } from 'lucide-react'
import { api } from '@/lib/api'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { Card, CardHeader } from '@/components/ui/Card'
import { Field, Input, Select } from '@/components/ui/Form'
import { EmptyState, ErrorNote, Loading, Page } from '@/components/ui/misc'
import { Switch } from '@/components/ui/Switch'
import { useToast } from '@/components/ui/Toast'
import { useConfig, useSaveConfig } from '@/lib/queries'
import type { AppConfig, ExtraCfg, SecretsStatus, ToolInfo } from '@/lib/types'
import { errMsg } from '@/lib/utils'
import { t, tk } from '@/lib/i18n.ts'
import { SearchBox } from '@/components/ui/SearchBox'
import { paginate, Pagination } from '@/components/ui/Pagination'
import { searchableText } from '@/lib/featureCatalog'
import { EmbeddingPanel } from '@/features/providers/EmbeddingPanel'
import { OcrPanel } from '@/features/providers/OcrPanel'
import { FeaturesTab } from './FeaturesTab'

const TOOLS_PER_PAGE = 10

const RISK: Record<ToolInfo['risk'], { label: string; tone: 'ok' | 'info' | 'warn' | 'bad' }> = {
  safe: { label: tk('An toàn'), tone: 'ok' },
  file: { label: tk('Truy cập file'), tone: 'info' },
  network: { label: tk('Mạng'), tone: 'warn' },
  exec: { label: tk('Chạy lệnh'), tone: 'bad' },
  mcp: { label: 'MCP', tone: 'info' },
}

function SecretsCard({ s }: { s?: SecretsStatus }) {
  if (!s) return null
  const where = { env: t('biến môi trường NESTOR_MASTER_KEY'), keychain: t('keychain của hệ điều hành'), file: 'data/master.key', none: t('chưa có') }[s.source]
  return (
    <Card>
      <CardHeader title={t('Mã hóa khóa bí mật')} />
      <div className="space-y-3 p-5 text-sm">
        <div className="flex items-center justify-between"><span className="text-muted">{t('Khóa đã mã hóa')}</span><Badge tone="ok">{s.encrypted}</Badge></div>
        <div className="flex items-center justify-between"><span className="text-muted">{t('Khóa còn chữ thường')}</span><Badge tone={s.plaintext ? 'warn' : 'neutral'}>{s.plaintext}</Badge></div>
        <div className="flex items-center justify-between"><span className="text-muted">{t('Nơi giữ khóa chủ')}</span><span className="font-mono text-xs">{where}</span></div>
        {!s.enabled && <p className="text-warn">{t('Mã hóa đã tắt (NESTOR_ENCRYPT=0).')}</p>}
        {s.failed.length > 0 && <p className="rounded-lg border border-bad/30 bg-bad/10 px-3 py-2 text-bad">{t('{n} khóa không giải mã được (mất hoặc sai khóa chủ). Hãy nhập lại trong giao diện hoặc khôi phục khóa chủ.', { n: s.failed.length })}</p>}
        {s.enabled && s.plaintext > 0 && <p className="text-warn">{t('Còn khóa chưa mã hóa. Chạy: nestor secrets encrypt')}</p>}
        {s.source === 'file' && <p className="text-xs text-muted">{t('Hãy sao lưu khóa chủ (nestor backup --include-key --encrypt): mất nó thì không giải mã lại được các khóa.')}</p>}
      </div>
    </Card>
  )
}

function PasswordCard({ has }: { has: boolean }) {
  const qc = useQueryClient()
  const toast = useToast()
  const [current, setCurrent] = useState('')
  const [next, setNext] = useState('')
  const m = useMutation({
    mutationFn: (v: { current: string; new: string }) => api.post<{ required: boolean }>('/api/auth/password', v),
    onSuccess: (r) => { toast(r.required ? t('Đã đặt mật khẩu') : t('Đã gỡ mật khẩu')); setCurrent(''); setNext(''); void qc.invalidateQueries({ queryKey: ['config'] }); void qc.invalidateQueries({ queryKey: ['auth-status'] }) },
    onError: (e) => toast(errMsg(e), 'bad'),
  })
  return (
    <Card>
      <CardHeader title={t('Bảo mật giao diện')} hint={has ? t('Giao diện đang yêu cầu mật khẩu.') : t('Chưa đặt mật khẩu: chỉ an toàn khi chỉ mình bạn dùng máy này. Hãy đặt mật khẩu nếu mở giao diện cho mạng LAN.')} />
      <div className="grid gap-4 p-5 sm:grid-cols-2">
        {has && <Field label={t('Mật khẩu hiện tại')}><Input type="password" autoComplete="current-password" value={current} onChange={(e) => setCurrent(e.target.value)} /></Field>}
        <Field label={has ? t('Mật khẩu mới (để trống để gỡ mật khẩu)') : t('Mật khẩu mới (ít nhất 8 ký tự)')}><Input type="password" autoComplete="new-password" value={next} onChange={(e) => setNext(e.target.value)} /></Field>
        <div className="col-span-full"><Button variant={has && !next ? 'danger' : 'primary'} loading={m.isPending} disabled={has ? !current : next.length < 8} onClick={() => m.mutate({ current, new: next })}>{has ? (next ? t('Đổi mật khẩu') : t('Gỡ mật khẩu')) : t('Đặt mật khẩu')}</Button></div>
      </div>
    </Card>
  )
}

function BackupRestoreCard() {
  const { confirmAction } = useDialogs()
  const toast = useToast()
  const [restoring, setRestoring] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleRestore = async (file: File) => {
    if (!(await confirmAction(t('Khôi phục sẽ ghi đè toàn bộ dữ liệu hiện tại bằng dữ liệu trong file sao lưu. Hệ thống sẽ tự động tạo một bản sao lưu dự phòng trước khi áp dụng. Bạn có chắc chắn muốn khôi phục?'), { action: t('Khôi phục'), title: t('Khôi phục bản sao lưu'), danger: true }))) {
      return
    }
    setRestoring(true)
    try {
      const res = await fetch('/api/backup/restore', {
        method: 'POST',
        headers: { 'Content-Type': 'application/octet-stream' },
        body: file,
      })
      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: res.statusText }))
        throw new Error(err.detail || t('Lỗi khôi phục'))
      }
      toast(t('Khôi phục thành công! Đang tải lại dữ liệu...'))
      setTimeout(() => {
        window.location.reload()
      }, 1500)
    } catch (e) {
      toast(errMsg(e), 'bad')
      setRestoring(false)
    }
  }

  return (
    <Card>
      <CardHeader
        title={t('Sao lưu & Khôi phục dữ liệu')}
        hint={t('Sao lưu toàn bộ cấu hình, tài liệu, trí nhớ, cơ sở dữ liệu hội thoại và không gian làm việc.')}
      />
      <div className="p-5">
        <div className="flex flex-wrap items-center gap-3">
          <a
            href="/api/backup/download"
            download
            className="inline-flex items-center gap-2 rounded-xl border border-line bg-panel2 px-4 py-2.5 text-sm font-medium transition hover:border-accent hover:text-accent"
          >
            <Download className="size-4 text-accent" />
            {t('Tải bản sao lưu (.tar.gz)')}
          </a>

          <input
            ref={fileInputRef}
            type="file"
            hidden
            accept=".tar.gz,.enc,application/gzip"
            onChange={(e) => {
              const file = e.target.files?.[0]
              if (file) void handleRestore(file)
              e.target.value = ''
            }}
          />

          <Button
            loading={restoring}
            onClick={() => fileInputRef.current?.click()}
          >
            <Upload className="size-4" />
            {t('Khôi phục từ file')}
          </Button>
        </div>
        <p className="mt-3 text-xs text-muted">
          {t('Khi khôi phục, hệ thống tự động lưu bản sao lưu an toàn (pre-restore) để bạn có thể quay lại nếu cần.')}
        </p>
      </div>
    </Card>
  )
}


const SECTIONS = [
  { id: 'appearance', label: tk('Giao diện'), desc: tk('Màu giao diện, phông chữ và ký tự ghép.'), Icon: Palette, terms: 'theme dark light font ligatures sang toi' },
  { id: 'agent', label: tk('Agent'), desc: tk('Model cho câu đơn giản, giới hạn bước và thư mục làm việc.'), Icon: Bot, terms: 'workspace ky nang goi y so buoc' },
  { id: 'memory', label: tk('Bộ nhớ & Ngữ cảnh'), desc: tk('Lịch sử hội thoại, tóm tắt và lập chỉ mục tin nhắn.'), Icon: Brain, terms: 'memory context auto index ngu nghia so tin nhan compact' },
  { id: 'browser', label: tk('Trình duyệt & Máy tính'), desc: tk('Chrome, chế độ chạy ẩn và điều khiển màn hình.'), Icon: Globe, terms: 'chromium headless man hinh dia chi noi bo' },
  { id: 'media', label: tk('Ảnh và hình ảnh'), desc: tk('Chọn model để tạo và đọc hình ảnh.'), Icon: Image, terms: 'vision image provider' },
  { id: 'delegation', label: tk('Agent con và việc dài'), desc: tk('Vai trò agent con, chạy song song và giới hạn tác vụ nền.'), Icon: Network, terms: 'subagent delegation do sau so buoc' },
  { id: 'tools', label: tk('Công cụ'), desc: tk('Bật, tắt công cụ và thiết lập địa chỉ ClawHub.'), Icon: Wrench, terms: 'tools clawhub mcp' },
  { id: 'security', label: tk('An toàn & Bảo mật'), desc: tk('Mật khẩu, mã hóa khóa API và quyền chạy lệnh.'), Icon: Shield, terms: 'password sandbox docker shell mang khoa bi mat xac nhan' },
  { id: 'backup', label: tk('Sao lưu & Khôi phục'), desc: tk('Tải bản sao lưu hoặc khôi phục dữ liệu từ tệp.'), Icon: DatabaseBackup, terms: 'backup restore import export' },
] as const

const MODEL_SECTIONS = [
  { id: 'embedding', label: tk('Model embedding'), desc: tk('Chọn và tải model tìm kiếm theo nghĩa.'), Icon: Brain, terms: 'ollama gemini vector semantic search' },
  { id: 'ocr', label: 'OCR', desc: tk('Cài Tesseract và bộ ngôn ngữ để đọc PDF scan.'), Icon: ScanText, terms: 'tieng viet tieng anh tesseract nhan dang chu' },
] as const

type SettingItem = (typeof SECTIONS)[number] | (typeof MODEL_SECTIONS)[number]

const GROUPS = [
  { title: tk('Cá nhân hóa'), ids: ['appearance'] },
  { title: tk('Agent & Công cụ'), ids: ['agent', 'memory', 'browser', 'media', 'delegation', 'tools'] },
  { title: tk('Mô hình & Tài liệu'), ids: ['embedding', 'ocr'] },
  { title: tk('Bảo mật & Dữ liệu'), ids: ['security', 'backup'] },
]

function SettingCards({ items }: { items: readonly SettingItem[] }) {
  return (
    <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4">
      {items.map(({ id, label, desc, Icon }) => (
          <Link key={id} to={`?tab=${id}`}
            className="group flex min-w-0 items-center gap-3 rounded-xl border border-line bg-panel p-4 transition hover:border-accent/50 hover:bg-panel2">
            <span className="grid size-9 shrink-0 place-items-center rounded-lg bg-accent/10 text-accent"><Icon className="size-4" /></span>
            <span className="min-w-0 flex-1"><span className="block text-sm font-semibold">{t(label)}</span><span className="mt-1 block text-xs leading-relaxed text-muted">{t(desc)}</span></span>
            <ArrowRight aria-hidden className="size-4 shrink-0 text-muted group-hover:text-accent" />
          </Link>
      ))}
    </div>
  )
}

function SettingsDialog({ title, onClose, children, footer, wide }: {
  title: string; onClose: () => void; children: ReactNode; footer?: ReactNode; wide: boolean
}) {
  const element = useRef<HTMLDialogElement>(null)
  const titleId = useId()
  const closeButton = useRef<HTMLButtonElement>(null)

  useLayoutEffect(() => {
    const dialog = element.current
    dialog?.showModal()
    closeButton.current?.focus()
    return () => dialog?.close()
  }, [])

  return (
    <dialog ref={element} aria-labelledby={titleId}
      onCancel={(event) => { event.preventDefault(); onClose() }}
      onClick={(event) => { if (event.target === event.currentTarget) onClose() }}
      className={`fixed inset-0 m-auto max-h-[88dvh] w-[calc(100%_-_1.5rem)] overflow-hidden rounded-2xl border border-line bg-panel p-0 text-fg shadow-2xl backdrop:bg-black/60 backdrop:backdrop-blur-sm ${wide ? 'max-w-2xl' : 'max-w-lg'}`}>
      <div className="flex max-h-[88dvh] flex-col">
        <header className="flex shrink-0 items-center justify-between gap-3 border-b border-line px-4 py-3 sm:px-5">
          <h2 id={titleId} className="text-base font-semibold">{title}</h2>
          <button ref={closeButton} type="button" onClick={onClose} aria-label={t('Đóng')} className="rounded-md p-1.5 text-muted hover:bg-panel2 hover:text-fg">
            <X className="size-4" />
          </button>
        </header>
        <div className="min-h-0 overflow-y-auto p-3 sm:p-4">{children}</div>
        {footer && <footer className="shrink-0 border-t border-line px-4 py-3 sm:px-5">{footer}</footer>}
      </div>
    </dialog>
  )
}

function extraConfig({ browser, memory, media, computer, agents }: AppConfig): ExtraCfg {
  return { browser, memory, media, computer, agents }
}

export function SettingsPage() {
  const cfg = useConfig()
  const save = useSaveConfig()
  const toast = useToast()
  const [agentEdit, setAgentEdit] = useState<AppConfig['agent'] | null>(null)
  const [attachmentEdit, setAttachmentEdit] = useState<AppConfig['chat_attachments'] | null>(null)
  const [hubEdit, setHubEdit] = useState<string | null>(null)
  const [extraEdit, setExtraEdit] = useState<ExtraCfg | null>(null)
  const [query, setQuery] = useState('')
  const [toolQuery, setToolQuery] = useState('')
  const [toolPage, setToolPage] = useState(0)
  const [params, setParams] = useSearchParams()
  const requested = params.get('tab')
  const items = [...SECTIONS, ...MODEL_SECTIONS]
  const active = items.find((section) => section.id === (requested === 'features' ? 'browser' : requested))
  const tab = active?.id
  const searching = !!query.trim()

  if (cfg.error && !cfg.data) return <Page><ErrorNote error={cfg.error} /></Page>
  if (!cfg.data) return <Loading />
  const { config, tools, secrets } = cfg.data
  const agent = agentEdit ?? config.agent
  const attachments = attachmentEdit ?? config.chat_attachments
  const hub = hubEdit ?? config.clawhub_url
  const extra = extraEdit ?? extraConfig(config)
  const dirty = attachments.image_max_mb !== config.chat_attachments.image_max_mb || attachments.file_max_mb !== config.chat_attachments.file_max_mb || JSON.stringify(agent) !== JSON.stringify(config.agent) || hub !== config.clawhub_url || JSON.stringify(extra) !== JSON.stringify(extraConfig(config))
  const reset = () => { setAgentEdit(null); setAttachmentEdit(null); setHubEdit(null); setExtraEdit(null) }
  const num = (k: 'max_steps' | 'max_history' | 'compact_chars') => (e: React.ChangeEvent<HTMLInputElement>) => setAgentEdit({ ...agent, [k]: Number(e.target.value) })
  const searchWords = searchableText(query.trim()).split(/\s+/).filter(Boolean)
  const matches = items.filter(({ label, desc, terms }) => {
    const index = searchableText([t(label), t(desc), terms].join(' '))
    return searchWords.every((word) => index.includes(word))
  })
  const clearSearch = () => setQuery('')
  const saveChanges = () => save.mutate({ ...config, ...extra, agent, chat_attachments: attachments, clawhub_url: hub }, {
    onSuccess: () => { reset(); toast(t('Đã lưu cài đặt')) }, onError: (e) => toast(errMsg(e), 'bad'),
  })
  const closeSettings = () => { if (!save.isPending) setParams({}, { replace: true }) }
  const saveBar = dirty && (
    <div className="flex flex-wrap items-center justify-between gap-3">
      <p role="status" className="text-sm font-medium">{t('Có thay đổi chưa lưu')}</p>
      <div className="flex flex-wrap gap-2">
        <Button disabled={save.isPending} onClick={reset}>{t('Bỏ thay đổi')}</Button>
        <Button variant="primary" loading={save.isPending} onClick={saveChanges}>{t('Lưu thay đổi')}</Button>
      </div>
    </div>
  )
  const filteredTools = tools.filter((tool) => searchableText(`${tool.name} ${t(tool.description)}`).includes(searchableText(toolQuery.trim())))
  const page = Math.min(toolPage, Math.max(0, Math.ceil(filteredTools.length / TOOLS_PER_PAGE) - 1))

  return (
    <Page>
      <div>
        <header className="mb-5 flex flex-wrap items-center justify-between gap-3">
          <h1 className="text-xl font-semibold tracking-tight">{t('Cài đặt')}</h1>
          <SearchBox value={query} onChange={setQuery} placeholder={t('Tìm cài đặt…')} label={t('Tìm cài đặt')} />
        </header>
        {searching ? (
          <section aria-label={t('Kết quả tìm cài đặt')}>
            <div className="mb-3 flex items-center justify-between gap-2">
              <h2 className="text-sm font-semibold">{t('Kết quả tìm cài đặt')}</h2>
              <Button size="sm" variant="ghost" onClick={clearSearch}>{t('Xóa tìm kiếm')}</Button>
            </div>
            {matches.length ? <SettingCards items={matches} /> : <EmptyState icon={Search} title={t('Không tìm thấy mục cài đặt.')} />}
          </section>
        ) : (
          <div className="space-y-6">
            {GROUPS.map(({ title, ids }) => (
              <section key={title}>
                <h2 className="mb-3 text-sm font-semibold text-muted">{t(title)}</h2>
                <SettingCards items={items.filter((item) => ids.includes(item.id))} />
              </section>
            ))}
          </div>
        )}
        {active && (
          <SettingsDialog key={tab} title={t(active.label)} onClose={closeSettings} footer={saveBar}
            wide={tab === 'security' || tab === 'tools' || tab === 'browser' || tab === 'delegation' || tab === 'embedding' || tab === 'ocr'}>
            <fieldset disabled={save.isPending} className="min-w-0 space-y-3">
            {tab === 'appearance' && <AppearanceCard />}
            {tab === 'ocr' && <OcrPanel />}
            {tab === 'embedding' && <EmbeddingPanel memory={extra.memory}
              onChange={(patch) => setExtraEdit({ ...extra, memory: { ...extra.memory, ...patch } })} providerInfo={config.providers} isDirty={dirty} />}
            {tab === 'agent' && <Card>
              <CardHeader title={t('Thực thi')} action={<Link to="/providers" className="inline-flex items-center gap-1 text-sm text-accent hover:underline">{t('Mô hình AI')}<ArrowUpRight className="size-4" /></Link>} />
              <div className="grid gap-4 p-5 sm:grid-cols-2 xl:grid-cols-3">
                <div className="-mx-5 flex flex-wrap items-center justify-between gap-4 border-b border-line/60 px-5 pb-4 col-span-full">
                  <div className="max-w-md">
                    <p className="text-sm font-medium">{t('Model nhanh cho câu đơn giản')}</p>
                    <p className="text-xs text-muted">{t('Khi đang dùng model mặc định, câu ngắn và đơn giản (chào hỏi, hỏi đáp nhanh) sẽ dùng model này để nhanh và rẻ hơn. Việc code, file, nhiều bước vẫn dùng model chính.')}</p>
                  </div>
                  <Select value={agent.fast_provider ?? ''} onChange={(e) => setAgentEdit({ ...agent, fast_provider: e.target.value })} className="w-56">
                    <option value="">{t('Tắt')}</option>
                    {Object.keys(config.providers).filter((n) => n !== config.default_provider).map((n) => <option key={n} value={n}>{n}</option>)}
                  </Select>
                </div>
                <div className="-mx-5 flex items-center justify-between gap-4 border-b border-line/60 px-5 pb-4 last:border-b-0 last:pb-0 col-span-full">
                  <p className="text-sm font-medium">{t('Gợi ý tạo kỹ năng từ việc lặp lại')}</p>
                  <Switch checked={agent.suggest_habits} onChange={(v) => setAgentEdit({ ...agent, suggest_habits: v })} label={t('Gợi ý kỹ năng')} />
                </div>
                <Field label={t('Dung lượng tối đa mỗi ảnh đính kèm (MB)')}>
                  <Input type="number" min={1} value={attachments.image_max_mb} onChange={(e) => setAttachmentEdit({ ...attachments, image_max_mb: Number(e.target.value) })} />
                </Field>
                <Field label={t('Dung lượng tối đa mỗi tệp đính kèm (MB)')}>
                  <Input type="number" min={1} value={attachments.file_max_mb} onChange={(e) => setAttachmentEdit({ ...attachments, file_max_mb: Number(e.target.value) })} />
                </Field>
                <Field label={t('Số bước tối đa mỗi lượt')}><Input type="number" min={1} max={50} value={agent.max_steps} onChange={num('max_steps')} /></Field>
                <div className="col-span-full"><Field label={t('Thư mục workspace')}><Input value={agent.workspace} onChange={(e) => setAgentEdit({ ...agent, workspace: e.target.value })} /></Field></div>
              </div>
            </Card>}
            {tab === 'memory' && <Card>
              <CardHeader title={t('Ngữ cảnh hội thoại')} />
              <div className="grid gap-4 p-5 sm:grid-cols-2">
                <Field label={t('Số tin nhắn gửi kèm')}><Input type="number" min={4} max={500} value={agent.max_history} onChange={num('max_history')} /></Field>
                <div className="col-span-full"><Field label={t('Tóm tắt hội thoại khi vượt quá (ký tự)')}><Input type="number" min={4000} step={1000} value={agent.compact_chars} onChange={num('compact_chars')} /></Field></div>
              </div>
            </Card>}
            {(tab === 'browser' || tab === 'memory' || tab === 'media' || tab === 'delegation') && (
              <FeaturesTab section={tab} value={extra} onChange={setExtraEdit} providers={Object.keys(config.providers)} tools={tools.map((tool) => tool.name)} />
            )}
            {tab === 'tools' && (
              <>
                <Card>
                  <CardHeader title={t('Công cụ')} />
                  <div className="px-5 py-3"><SearchBox value={toolQuery} onChange={(value) => { setToolQuery(value); setToolPage(0) }} placeholder={t('Tìm công cụ…')} label={t('Tìm công cụ')} /></div>
                  {!filteredTools.length && <p className="px-5 pb-4 text-sm text-muted">{t('Không có công cụ phù hợp.')}</p>}
                  <div className="divide-y divide-line">
                    {paginate(filteredTools, page, TOOLS_PER_PAGE).map((tool) => (
                      <div key={tool.name} className="flex items-center gap-4 px-5 py-3">
                        <div className="min-w-0 flex-1">
                          <div className="flex items-center gap-2"><span className="font-mono text-[13px] font-medium">{tool.name}</span><Badge tone={RISK[tool.risk].tone}>{t(RISK[tool.risk].label)}</Badge></div>
                          <p className="text-xs text-muted">{t(tool.description)}</p>
                        </div>
                        <Switch checked={agent.tools_enabled[tool.name] !== false} onChange={(v) => setAgentEdit({ ...agent, tools_enabled: { ...agent.tools_enabled, [tool.name]: v } })} label={t('Bật tool {name}', { name: tool.name })} />
                      </div>
                    ))}
                  </div>
                  <Pagination page={page} pageSize={TOOLS_PER_PAGE} total={filteredTools.length} onPageChange={setToolPage} />
                </Card>
                <Card><CardHeader title="ClawHub" /><div className="p-5"><Field label="URL"><Input value={hub} onChange={(e) => setHubEdit(e.target.value)} /></Field></div></Card>
              </>
            )}
            {tab === 'security' && (
              <>
                <Card>
                  <CardHeader title={t('An toàn khi chạy lệnh')} />
                  <div className="grid gap-4 p-5 sm:grid-cols-2">
                    <div className="-mx-5 flex items-center justify-between gap-4 border-b border-line/60 px-5 pb-4 last:border-b-0 last:pb-0 col-span-full">
                      <div>
                        <p className="text-sm font-medium">{t('Xác nhận trước khi chạy lệnh shell')}</p>
                      </div>
                      <Switch checked={agent.confirm_exec} onChange={(v) => setAgentEdit({ ...agent, confirm_exec: v })} label={t('Xác nhận lệnh shell')} />
                    </div>
                    <Field label={t('Sandbox chạy lệnh (Docker)')}><Select value={agent.exec_sandbox} onChange={(e) => setAgentEdit({ ...agent, exec_sandbox: e.target.value as 'none' | 'docker' })}><option value="none">{t('Tắt (chạy trực tiếp trên máy)')}</option><option value="docker">Docker</option></Select></Field>
                    <Field label={t('Image')}><Input value={agent.sandbox_image} disabled={agent.exec_sandbox !== 'docker'} onChange={(e) => setAgentEdit({ ...agent, sandbox_image: e.target.value })} className="font-mono" /></Field>
                    <div className="-mx-5 flex items-center justify-between gap-4 border-b border-line/60 px-5 pb-4 last:border-b-0 last:pb-0 col-span-full">
                      <div><p className="text-sm font-medium">{t('Cho phép container dùng mạng')}</p></div>
                      <Switch checked={agent.sandbox_network} onChange={(v) => setAgentEdit({ ...agent, sandbox_network: v })} label={t('Mạng trong sandbox')} disabled={agent.exec_sandbox !== 'docker'} />
                    </div>
                  </div>
                </Card>
                <PasswordCard has={config.auth.has_password} />
                <SecretsCard s={secrets} />
              </>
            )}
            {tab === 'backup' && <BackupRestoreCard />}
            </fieldset>
          </SettingsDialog>
        )}
        {!active && dirty && <div className="sticky bottom-0 z-10 mt-5 rounded-xl border border-accent/30 bg-panel p-3 shadow-xl sm:px-4">{saveBar}</div>}
      </div>
    </Page>
  )
}
