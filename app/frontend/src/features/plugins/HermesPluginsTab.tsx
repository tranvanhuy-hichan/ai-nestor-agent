import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import {
  AppWindow,
  Bot,
  Box,
  Cpu,
  Database,
  ExternalLink,
  Globe,
  Info,
  Mic,
  Package,
  Search,
  Sparkles,
  Terminal,
  Wrench,
  type LucideIcon,
} from 'lucide-react'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { Modal } from '@/components/ui/Modal'
import { EmptyState, ErrorNote, Loading } from '@/components/ui/misc'
import { Pagination } from '@/components/ui/Pagination'
import { api } from '@/lib/api'
import { t, useLang } from '@/lib/i18n'
import type { HermesCatalogResponse, HermesPlugin } from '@/lib/types'
import { cn } from '@/lib/utils'

const CAT_ICONS: Record<string, LucideIcon> = {
  all: Package,
  tools: Wrench,
  desktop: AppWindow,
  automation: Bot,
  models: Cpu,
  memory: Database,
  general: Box,
  platform: Terminal,
  web: Globe,
  voice: Mic,
  other: Sparkles,
}

export function HermesPluginModal({
  plugin,
  onClose,
}: {
  plugin: HermesPlugin | null
  onClose: () => void
}) {
  if (!plugin) return null

  const tools = plugin.capabilities?.provides_tools ?? []
  const envs = plugin.capabilities?.requires_env ?? []

  return (
    <Modal
      open={true}
      onClose={onClose}
      wide
      title={
        <div>
          <div>{plugin.title || plugin.name}</div>
          <div className="text-xs font-normal text-muted mt-0.5">
            @{plugin.maintainer || 'hermes'} {plugin.version ? `· v${plugin.version}` : ''}
          </div>
        </div>
      }
      footer={
        <div className="flex w-full items-center justify-between">
          <div className="text-xs text-muted">
            {plugin.tier === 'official' ? (
              <span className="text-ok font-medium">{t('Plugin chính thức')}</span>
            ) : (
              <span>{t('Plugin cộng đồng Hermes')}</span>
            )}
          </div>
          <div className="flex items-center gap-2">
            {plugin.repo && (
              <a
                href={plugin.repo}
                target="_blank"
                rel="noreferrer noopener"
                className="inline-flex items-center gap-1.5 rounded-lg border border-line bg-panel2 px-3 py-1.5 text-xs font-medium text-text hover:bg-panel"
              >
                <ExternalLink className="size-3.5" />
                <span>GitHub</span>
              </a>
            )}
            <Button variant="primary" onClick={onClose}>
              {t('Đóng')}
            </Button>
          </div>
        </div>
      }
    >
      <div className="space-y-4">
        <div className="flex flex-wrap items-center gap-2">
          {plugin.category && (
            <Badge tone="neutral">
              {plugin.category.toUpperCase()}
            </Badge>
          )}
          {plugin.tier && (
            <Badge tone={plugin.tier === 'official' ? 'ok' : 'info'}>
              {plugin.tier === 'official' ? t('Chính thức') : t('Cộng đồng')}
            </Badge>
          )}
          {tools.length > 0 && (
            <Badge tone="info">
              {t('{n} công cụ', { n: tools.length })}
            </Badge>
          )}
        </div>

        <div>
          <h4 className="text-xs font-semibold uppercase tracking-wider text-muted">
            {t('Mô tả')}
          </h4>
          <p className="mt-1 text-sm leading-relaxed text-text whitespace-pre-wrap">
            {plugin.description || t('Không có mô tả chi tiết.')}
          </p>
        </div>

        {tools.length > 0 && (
          <div>
            <h4 className="text-xs font-semibold uppercase tracking-wider text-muted">
              {t('Các công cụ cung cấp')} ({tools.length})
            </h4>
            <div className="mt-1.5 flex flex-wrap gap-1.5 max-h-36 overflow-y-auto rounded-lg border border-line bg-panel2 p-2">
              {tools.map((tool) => (
                <span
                  key={tool}
                  className="rounded bg-panel px-2 py-0.5 font-mono text-xs text-text border border-line"
                >
                  {tool}
                </span>
              ))}
            </div>
          </div>
        )}

        {envs.length > 0 && (
          <div>
            <h4 className="text-xs font-semibold uppercase tracking-wider text-warn">
              {t('Biến môi trường / Khóa API yêu cầu')}
            </h4>
            <div className="mt-1.5 flex flex-wrap gap-1.5">
              {envs.map((env) => (
                <span
                  key={env}
                  className="rounded bg-warn/10 text-warn border border-warn/20 px-2 py-0.5 font-mono text-xs"
                >
                  {env}
                </span>
              ))}
            </div>
          </div>
        )}

        <div className="rounded-xl border border-line bg-panel2/50 p-3 text-xs text-muted">
          <div className="flex items-center gap-1.5 font-semibold text-text mb-1">
            <Info className="size-4 text-accent" />
            <span>{t('Cách kích hoạt trong Nestor')}</span>
          </div>
          <p>
            {t(
              'Plugin này thuộc hệ sinh thái Hermes Portable Plugins v1. Bạn có thể kết nối công cụ này qua mục MCP server hoặc dùng dòng lệnh "nestor run" với cấu hình tương ứng.'
            )}
          </p>
          {plugin.docs_url && (
            <a
              href={plugin.docs_url}
              target="_blank"
              rel="noreferrer noopener"
              className="mt-2 inline-flex items-center gap-1 text-accent hover:underline"
            >
              <ExternalLink className="size-3" />
              <span>{t('Xem hướng dẫn thiết lập từ tác giả')}</span>
            </a>
          )}
        </div>
      </div>
    </Modal>
  )
}

export function HermesPluginsTab({ q = '' }: { q?: string }) {
  const lang = useLang()
  const [category, setCategory] = useState('all')
  const [page, setPage] = useState(0)
  const [selectedPlugin, setSelectedPlugin] = useState<HermesPlugin | null>(null)
  const PAGE_SIZE = 24

  const query = useQuery({
    queryKey: ['hermes-plugins-catalog', q, category, page],
    queryFn: () =>
      api.get<HermesCatalogResponse>(
        `/api/plugins/catalog?q=${encodeURIComponent(q)}&category=${encodeURIComponent(category)}&page=${page}&limit=${PAGE_SIZE}`
      ),
    staleTime: 300_000,
  })

  const categories = query.data?.categories ?? []

  return (
    <div className="space-y-6">
      {/* Category filter pills */}
      <div className="flex items-center gap-1.5 overflow-x-auto pb-1">
        {categories.map((c) => {
          const active = category === c.id
          const Icon = CAT_ICONS[c.id] || Box
          const label = lang === 'en' ? c.label.en : c.label.vi
          return (
            <button
              key={c.id}
              onClick={() => {
                setCategory(c.id)
                setPage(0)
              }}
              className={cn(
                'inline-flex shrink-0 items-center gap-1.5 rounded-lg border px-3 py-1.5 text-xs font-medium transition',
                active
                  ? 'border-accent bg-accent text-accent-fg shadow-xs font-semibold'
                  : 'border-line bg-panel2 text-muted hover:border-line2 hover:text-fg'
              )}
            >
              <Icon className="size-3.5" />
              <span>{label}</span>
              <span
                className={cn(
                  'rounded px-1.5 py-0.5 text-[10px] tabular-nums',
                  active ? 'bg-white/20 text-white' : 'bg-panel text-muted'
                )}
              >
                {c.count}
              </span>
            </button>
          )
        })}
      </div>

      {/* Content Area */}
      {query.isLoading ? (
        <Loading />
      ) : query.error ? (
        <ErrorNote error={query.error} />
      ) : (query.data?.items.length ?? 0) === 0 ? (
        <EmptyState
          icon={Search}
          title={t('Không tìm thấy plugin nào')}
          hint={t('Hãy thử đổi từ khóa tìm kiếm hoặc chọn danh mục khác.')}
          action={
            <Button
              size="sm"
              onClick={() => {
                setCategory('all')
                setPage(0)
              }}
            >
              {t('Xem tất cả plugin')}
            </Button>
          }
        />
      ) : (
        <>
          <div className="flex items-center justify-between text-xs text-muted">
            <div>
              <span>{t('Hiển thị {n} trên tổng số {total} plugin', { n: query.data?.items.length ?? 0, total: query.data?.total ?? 0 })}</span>
              {q && <span className="ml-1 italic font-medium text-text">&ldquo;{q}&rdquo;</span>}
            </div>
            {category !== 'all' && (
              <button
                onClick={() => {
                  setCategory('all')
                  setPage(0)
                }}
                className="text-accent hover:underline font-medium"
              >
                {t('Xem tất cả danh mục')}
              </button>
            )}
          </div>

          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-3">
            {query.data?.items.map((p) => {
              const toolsCount = p.capabilities?.provides_tools?.length ?? 0
              const envsCount = p.capabilities?.requires_env?.length ?? 0
              return (
                <div
                  key={p.name}
                  className="flex flex-col justify-between rounded-xl border border-line bg-panel p-4 shadow-xs transition hover:border-line2 hover:shadow-sm"
                >
                  <div>
                    <div className="flex items-start justify-between gap-2">
                      <div className="min-w-0 flex-1">
                        <h4 className="font-semibold text-text truncate">
                          {p.title || p.name}
                        </h4>
                        <p className="text-xs text-muted truncate">
                          @{p.maintainer || 'hermes'} {p.version ? `· v${p.version}` : ''}
                        </p>
                      </div>
                      <Badge tone={p.tier === 'official' ? 'ok' : 'neutral'} className="shrink-0 text-[10px]">
                        {p.tier === 'official' ? t('Chính thức') : t('Cộng đồng')}
                      </Badge>
                    </div>

                    <p className="mt-2 text-xs leading-relaxed text-muted line-clamp-3">
                      {p.description || t('Không có mô tả')}
                    </p>

                    <div className="mt-3 flex flex-wrap items-center gap-1.5 text-[11px]">
                      {p.category && (
                        <span className="rounded bg-panel2 px-2 py-0.5 text-muted font-medium">
                          {p.category}
                        </span>
                      )}
                      {toolsCount > 0 && (
                        <span className="rounded bg-accent/10 px-2 py-0.5 text-accent font-medium">
                          {toolsCount} {t('công cụ')}
                        </span>
                      )}
                      {envsCount > 0 && (
                        <span className="rounded bg-warn/10 px-2 py-0.5 text-warn font-medium">
                          {t('Cần API key')}
                        </span>
                      )}
                    </div>
                  </div>

                  <div className="mt-4 flex items-center justify-between border-t border-line/60 pt-3">
                    <button
                      onClick={() => setSelectedPlugin(p)}
                      className="text-xs font-medium text-accent hover:underline flex items-center gap-1"
                    >
                      <Info className="size-3.5" />
                      <span>{t('Chi tiết')}</span>
                    </button>
                    {p.repo && (
                      <a
                        href={p.repo}
                        target="_blank"
                        rel="noreferrer noopener"
                        className="text-xs text-muted hover:text-text flex items-center gap-1 transition"
                        title={p.repo}
                      >
                        <ExternalLink className="size-3" />
                        <span>GitHub</span>
                      </a>
                    )}
                  </div>
                </div>
              )
            })}
          </div>

          <Pagination
            page={page}
            pageSize={PAGE_SIZE}
            total={query.data?.total ?? 0}
            onPageChange={setPage}
          />
        </>
      )}

      <HermesPluginModal
        plugin={selectedPlugin}
        onClose={() => setSelectedPlugin(null)}
      />
    </div>
  )
}
