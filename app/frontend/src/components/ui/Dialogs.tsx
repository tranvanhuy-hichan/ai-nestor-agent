import { createContext, useCallback, useContext, useId, useLayoutEffect, useRef, useState, type ReactNode } from 'react'
import { CircleAlert, X } from 'lucide-react'
import { t } from '@/lib/i18n.ts'
import { Button } from './Button'
import { Field, Input } from './Form'

interface ConfirmOptions {
  action: string
  title?: string
  danger?: boolean
}

interface Dialogs {
  confirmAction: (message: string, options: ConfirmOptions) => Promise<boolean>
  askText: (title: string, label: string, initial: string) => Promise<string | null>
}

type Request =
  | { kind: 'confirm'; message: string; options: ConfirmOptions; resolve: (answer: boolean) => void }
  | { kind: 'text'; title: string; label: string; initial: string; resolve: (answer: string | null) => void }

const Context = createContext<Dialogs | null>(null)

export function useDialogs() {
  const dialogs = useContext(Context)
  if (!dialogs) throw new Error('DialogProvider is required')
  return dialogs
}

function ActionDialog({ request, onClose }: { request: Request; onClose: () => void }) {
  const dialog = useRef<HTMLDialogElement>(null)
  const titleId = useId()
  const messageId = useId()
  const isConfirm = request.kind === 'confirm'
  const [value, setValue] = useState(request.kind === 'text' ? request.initial : '')

  useLayoutEffect(() => {
    const element = dialog.current
    element?.showModal()
    element?.querySelector<HTMLElement>('[data-initial-focus]')?.focus()
    return () => element?.close()
  }, [])

  const cancel = () => {
    dialog.current?.close()
    onClose()
    if (request.kind === 'confirm') request.resolve(false)
    else request.resolve(null)
  }

  return (
    <dialog ref={dialog} aria-labelledby={titleId} aria-describedby={isConfirm ? messageId : undefined}
      onCancel={(event) => { event.preventDefault(); cancel() }}
      onKeyDown={(event) => { if (event.key === 'Escape') event.stopPropagation() }}
      onClick={(event) => { if (event.target === event.currentTarget) cancel() }}
      className="fade-in fixed inset-0 m-auto w-[calc(100%_-_2rem)] max-w-md max-h-[88vh] rounded-2xl border border-line bg-panel p-0 text-fg shadow-2xl backdrop:bg-black/60 backdrop:backdrop-blur-sm">
      <form onSubmit={(event) => {
        event.preventDefault()
        dialog.current?.close()
        onClose()
        if (request.kind === 'confirm') request.resolve(true)
        else request.resolve(value)
      }}>
        <header className="flex items-center gap-3 border-b border-line px-5 py-3.5">
          {isConfirm && <CircleAlert className={request.options.danger ? 'size-5 shrink-0 text-bad' : 'size-5 shrink-0 text-accent'} />}
          <h2 id={titleId} className="min-w-0 flex-1 break-words text-base font-semibold">{isConfirm ? request.options.title ?? t('Xác nhận thao tác') : request.title}</h2>
          <button type="button" onClick={cancel} aria-label={t('Đóng')} className="rounded-md p-1 text-muted hover:bg-panel2 hover:text-fg"><X className="size-4" /></button>
        </header>
        <div className="p-5">
          {isConfirm ? <p id={messageId} className="whitespace-pre-wrap break-words text-sm text-muted">{request.message}</p> :
            <Field label={request.label}><Input data-initial-focus value={value} onChange={(event) => setValue(event.target.value)} /></Field>}
        </div>
        <footer className="flex flex-wrap justify-end gap-2 border-t border-line px-5 py-3.5">
          <Button type="button" data-initial-focus={isConfirm ? true : undefined} onClick={cancel}>{t('Hủy')}</Button>
          <Button type="submit" variant={isConfirm && request.options.danger ? 'danger' : 'primary'}>
            {isConfirm ? request.options.action : t('Lưu')}
          </Button>
        </footer>
      </form>
    </dialog>
  )
}

export function DialogProvider({ children }: { children: ReactNode }) {
  const [request, setRequest] = useState<Request | null>(null)
  const pending = useRef(false)
  const confirmAction = useCallback<Dialogs['confirmAction']>((message, options) => {
    if (pending.current) return Promise.resolve(false)
    pending.current = true
    return new Promise((resolve) => setRequest({ kind: 'confirm', message, options, resolve }))
  }, [])
  const askText = useCallback<Dialogs['askText']>((title, label, initial) => {
    if (pending.current) return Promise.resolve(null)
    pending.current = true
    return new Promise((resolve) => setRequest({ kind: 'text', title, label, initial, resolve }))
  }, [])

  return (
    <Context.Provider value={{ confirmAction, askText }}>
      {children}
      {request && <ActionDialog request={request} onClose={() => { pending.current = false; setRequest(null) }} />}
    </Context.Provider>
  )
}
