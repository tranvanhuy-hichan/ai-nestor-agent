import '@fontsource-variable/fira-code'
import '@fontsource-variable/jetbrains-mono'
import { useAppearance } from '@/lib/appearance'
import { GatewayPage } from '@/features/system/GatewayPage'
import { ProfilesPage } from '@/features/profiles/ProfilesPage'
import { lazy, Suspense, useEffect, type ReactElement } from 'react'
import { Navigate, Route, Routes } from 'react-router-dom'
import { AppLayout } from '@/components/layout/AppLayout'
import { NotificationsPage } from '@/features/notifications/NotificationsPage'
import { TasksPage } from './features/tasks/TasksPage'
import { KanbanPage } from './features/tasks/KanbanPage'
import { AutomationsPage } from '@/features/automations/AutomationsPage'
import { CodePage } from '@/features/code/CodePage'
import { ChatPage } from '@/features/chat/ChatPage'
import { HomePage } from '@/features/home/HomePage'
import { IntegrationsPage } from '@/features/integrations/IntegrationsPage'
import { PagesPage } from '@/features/pages/PagesPage'
import { DocumentsPage } from '@/features/documents/DocumentsPage'
import { PluginsPage } from '@/features/plugins/PluginsPage'
import { ProvidersPage } from '@/features/providers/ProvidersPage'
import { SettingsPage } from '@/features/settings/SettingsPage'
import { SkillsPage } from '@/features/skills/SkillsPage'
import { WorkspacePage } from '@/features/workspace/WorkspacePage'
import { ActivityPage } from '@/features/activity/ActivityPage'
import { CODE_MODE } from '@/lib/features'
import { useLang } from '@/lib/i18n.ts'
import { useUiMode } from '@/lib/uiMode'
import { FeatureHub } from '@/features/feature/FeatureHub'
import { LiveTranslatePage } from '@/features/translate/LiveTranslatePage'
import { FeaturePage } from '@/features/feature/FeaturePage'
import { SimpleHome } from '@/features/simple/SimpleHome'
import { SimpleSettings } from '@/features/simple/SimpleSettings'

// trình soạn thảo kéo theo highlight.js nên chỉ tải khi mở một dự án
const CodeWorkspace = lazy(() => import('@/features/code/CodeWorkspace').then((m) => ({ default: m.CodeWorkspace })))

export default function App() {
  const appearance = useAppearance()
  useEffect(() => {
    const root = document.documentElement
    root.classList.toggle('light', appearance.theme === 'light')
    root.dataset.theme = appearance.theme
    root.dataset.mono = appearance.font
    root.dataset.ligatures = appearance.ligatures ? 'on' : 'off'
  }, [appearance.theme, appearance.font, appearance.ligatures])
  const simple = useUiMode() === 'simple'
  // trang chỉ dành cho chế độ Nâng cao: ở chế độ Đơn giản quay về trang chủ
  const adv = (el: ReactElement) => (simple ? <Navigate to="/" replace /> : el)
  useLang() // doi ngon ngu => App render lai => toan bo cay route tao lai phan tu va cap nhat chu
  return (
    <Routes>
      {CODE_MODE && !simple && <Route path="code/:sid" element={<div className="h-full"><Suspense fallback={null}><CodeWorkspace /></Suspense></div>} />}
      {(!CODE_MODE || simple) && <Route path="code/*" element={<Navigate to="/" replace />} />}
      <Route element={<AppLayout />}>
        <Route index element={simple ? <SimpleHome /> : <HomePage />} />
        <Route path="history" element={<Navigate to="/tasks" replace />} />
        {CODE_MODE && !simple && <Route path="code" element={<CodePage />} />}
        <Route path="chat" element={<ChatPage />} />
        <Route path="profiles" element={<ProfilesPage />} />
        <Route path="gateway" element={adv(<GatewayPage />)} />
        <Route path="xao-de" element={<Navigate to="/f/ra-de-cham-bai?tab=exam-shuffle" replace />} />
        <Route path="f" element={<FeatureHub />} />
        <Route path="f/youtube-translate" element={<LiveTranslatePage />} />
        <Route path="f/:id" element={<FeaturePage />} />
        <Route path="activity" element={adv(<ActivityPage />)} />
        <Route path="dashboard" element={<Navigate to="/activity" replace />} />
        <Route path="automations" element={<AutomationsPage />} />
        <Route path="skills" element={<SkillsPage />} />
        <Route path="plugins" element={adv(<PluginsPage />)} />
        <Route path="documents" element={<DocumentsPage />} />
        <Route path="pages" element={<PagesPage />} />
        <Route path="pages/:id" element={<PagesPage />} />
        <Route path="providers" element={adv(<ProvidersPage />)} />
        <Route path="integrations" element={adv(<IntegrationsPage />)} />
        <Route path="audit" element={<Navigate to="/activity?tab=log" replace />} />
        <Route path="tasks" element={<TasksPage />} />
        <Route path="kanban" element={<KanbanPage />} />
        <Route path="notifications" element={<NotificationsPage />} />
        <Route path="workspace" element={adv(<WorkspacePage />)} />
        <Route path="settings" element={simple ? <SimpleSettings /> : <SettingsPage />} />
      </Route>
    </Routes>
  )
}
