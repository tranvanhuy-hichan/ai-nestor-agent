import { useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { Page, PageHeader } from '@/components/ui/misc'
import { SearchBox } from '@/components/ui/SearchBox'
import { Tabs } from '@/components/ui/Tabs'
import { t } from '@/lib/i18n.ts'
import { ServicesTab } from '@/features/integrations/ServicesTab'
import { HermesPluginsTab } from './HermesPluginsTab'

/** Tiện ích & Plugin: Kho 2.500+ plugin Hermes offline kèm các dịch vụ đám mây MCP (Google, Notion, Canva…) */
export function PluginsPage() {
  const [params, setParams] = useSearchParams()
  const tab = params.get('tab') === 'hermes' ? 'hermes' : 'services'
  const setTab = (next: 'hermes' | 'services') => setParams(next === 'services' ? {} : { tab: next }, { replace: true })
  const [q, setQ] = useState('')

  return (
    <Page>
      <PageHeader
        title={t('Tiện ích & Plugins')}
        action={
          <SearchBox
            value={q}
            onChange={setQ}
            placeholder={
              tab === 'hermes'
                ? t('Tìm trong 2.514 plugin Hermes (vd: docker, github, obsidian…)')
                : t('Tìm dịch vụ đám mây (vd: vercel, stripe, slack…)')
            }
            label={t('Tìm tiện ích')}
          />
        }
      />
      <Tabs
        value={tab}
        onChange={setTab}
        tabs={[
          { id: 'services', label: t('Dịch vụ đám mây & OAuth') },
          { id: 'hermes', label: t('Kho 2.500+ Plugin Hermes'), count: 2514 },
        ]}
      />
      <div className="mt-5">
        {tab === 'hermes' ? <HermesPluginsTab q={q} /> : <ServicesTab q={q} />}
      </div>
    </Page>
  )
}
