import { useState } from 'react'
import { Plus } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { Page, PageHeader } from '@/components/ui/misc'
import { t } from '@/lib/i18n.ts'
import { KanbanBoard } from './KanbanBoard'
import { RunBoard } from './RunHistory'

/** Trang rieng cho bang Kanban (tach khoi "Giao viec nhanh"), giong cach Hermes cho Kanban hẳn 1 muc o sidebar. */
export function KanbanPage() {
  const [adding, setAdding] = useState(false)
  return (
    <Page>
      <PageHeader title={t('Bảng Kanban')} subtitle={t('Lên kế hoạch việc, kéo-thả sắp xếp, rồi giao cho Nestor chạy nền.')}
        action={<Button variant="primary" onClick={() => setAdding(true)}><Plus className="size-4" />{t('Thẻ mới')}</Button>} />
      <KanbanBoard adding={adding} onAddingChange={setAdding} />
      <RunBoard />
    </Page>
  )
}
