import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter } from 'react-router-dom'
import { AuthGate } from '@/features/auth/AuthGate'
import { DialogProvider } from '@/components/ui/Dialogs'
import { ToastProvider } from '@/components/ui/Toast'
import { installAppearance } from '@/lib/appearance'
import App from './App'
import './index.css'

const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false, refetchOnWindowFocus: false, staleTime: 15_000 } } })
const removeAppearanceListener = installAppearance()
import.meta.hot?.dispose(removeAppearanceListener)

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <ToastProvider>
        <DialogProvider>
          <AuthGate>
            <BrowserRouter>
              <App />
            </BrowserRouter>
          </AuthGate>
        </DialogProvider>
      </ToastProvider>
    </QueryClientProvider>
  </StrictMode>,
)
