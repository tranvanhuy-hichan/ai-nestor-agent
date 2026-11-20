import { ChevronLeft, ChevronRight } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { t } from '@/lib/i18n.ts'

/** Thanh phan trang dung chung: "21-40 / 134" + nut truoc/sau. Dat o cuoi danh sach dai (skill, MCP, plugin...). */
export function Pagination({ page, pageSize, total, onPageChange }: { page: number; pageSize: number; total: number; onPageChange: (p: number) => void }) {
  const pageCount = Math.max(1, Math.ceil(total / pageSize))
  if (pageCount <= 1) return null
  const from = page * pageSize + 1
  const to = Math.min((page + 1) * pageSize, total)
  return (
    <div className="flex items-center justify-between gap-3 border-t border-line px-4 py-3 text-sm">
      <span className="text-xs text-muted">{t('{from}–{to} / {total}', { from, to, total })}</span>
      <div className="flex items-center gap-1">
        <Button variant="ghost" size="sm" disabled={page === 0} onClick={() => onPageChange(page - 1)} aria-label={t('Trang trước')}>
          <ChevronLeft className="size-4" />
        </Button>
        <span className="px-2 text-xs text-muted">{t('Trang {page} / {count}', { page: page + 1, count: pageCount })}</span>
        <Button variant="ghost" size="sm" disabled={page >= pageCount - 1} onClick={() => onPageChange(page + 1)} aria-label={t('Trang sau')}>
          <ChevronRight className="size-4" />
        </Button>
      </div>
    </div>
  )
}

/** Cat mot mang theo trang hien tai; dung chung voi <Pagination>. */
export function paginate<T>(items: T[], page: number, pageSize: number): T[] {
  return items.slice(page * pageSize, page * pageSize + pageSize)
}
