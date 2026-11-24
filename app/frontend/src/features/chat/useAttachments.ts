import { useCallback, useEffect, useRef, useState, type ClipboardEvent, type DragEvent } from 'react'
import { t } from '@/lib/i18n.ts'
import { errMsg } from '@/lib/utils'

export const attachmentAccept = '.png,.jpg,.jpeg,.webp,.gif,.pdf,.docx,.xlsx,.txt,.csv,.md,.json'
export const isAttachmentImage = (name: string) => /\.(png|jpe?g|webp|gif)$/i.test(name)
export type SelectedDocument = { id: string; name: string }
type Upload = { id: number; name: string; size: number; sid?: string; path?: string; progress: number; error?: string }

function uploadFile(sid: string, file: File, signal: AbortSignal, progress: (value: number) => void) {
  return new Promise<string>((resolve, reject) => {
    const request = new XMLHttpRequest()
    const abort = () => request.abort()
    signal.addEventListener('abort', abort, { once: true })
    request.open('POST', `/api/sessions/${sid}/chat-attachment?name=${encodeURIComponent(file.name)}`)
    request.responseType = 'json'
    request.upload.onprogress = (event) => { if (event.lengthComputable) progress(event.loaded / event.total) }
    request.onload = () => {
      if (request.status === 401) window.dispatchEvent(new Event('auth-required'))
      if (request.status === 200 && request.response?.path) resolve(request.response.path)
      else reject(new Error(typeof request.response?.detail === 'string' ? request.response.detail : t('Không thể tải tệp lên.')))
    }
    request.onerror = () => reject(new Error(t('Không thể tải tệp lên.')))
    request.onabort = () => reject(new DOMException('Aborted', 'AbortError'))
    request.onloadend = () => signal.removeEventListener('abort', abort)
    request.send(file)
  })
}

export function useAttachments(getSession: () => Promise<string>) {
  const [uploads, setUploads] = useState<Upload[]>([])
  const [documents, setDocuments] = useState<SelectedDocument[]>([])
  const requests = useRef(new Map<number, AbortController>())
  const sequence = useRef(0)
  const pendingSession = useRef<Promise<string> | null>(null)
  const reset = useCallback(() => {
    requests.current.forEach((controller) => controller.abort())
    requests.current.clear()
    pendingSession.current = null
    setUploads([])
    setDocuments([])
  }, [])
  useEffect(() => () => {
    requests.current.forEach((controller) => controller.abort())
    requests.current.clear()
  }, [])
  function remove(id: number) {
    requests.current.get(id)?.abort()
    requests.current.delete(id)
    setUploads((items) => items.filter((item) => item.id !== id))
  }
  function add(files: File[]) {
    for (const file of files) {
      const id = ++sequence.current
      const controller = new AbortController()
      requests.current.set(id, controller)
      setUploads((items) => [...items, { id, name: file.name, size: file.size, progress: 0 }])
      const update = (changes: Partial<Upload>) => {
        if (!controller.signal.aborted) setUploads((items) => items.map((item) => item.id === id ? { ...item, ...changes } : item))
      }
      void (async () => {
        try {
          const session = pendingSession.current ?? (pendingSession.current = getSession())
          const sid = await session.finally(() => {
            if (pendingSession.current === session) pendingSession.current = null
          })
          if (controller.signal.aborted) return
          const path = await uploadFile(sid, file, controller.signal, (progress) => update({ progress }))
          update({ path, sid, progress: 1 })
        } catch (error) {
          update({ error: errMsg(error) })
        } finally {
          requests.current.delete(id)
        }
      })()
    }
  }
  const uploading = uploads.some((item) => !item.path && !item.error)
  const paths = uploads.flatMap((item) => item.path ? [item.path] : [])
  function dragOver(event: DragEvent) {
    if (event.dataTransfer.types.includes('Files')) event.preventDefault()
  }
  function drop(event: DragEvent) {
    if (!event.dataTransfer.files.length) return
    event.preventDefault()
    add([...event.dataTransfer.files])
  }
  function paste(event: ClipboardEvent) {
    const images = [...event.clipboardData.files].filter((file) => file.type.startsWith('image/'))
    if (!images.length) return
    event.preventDefault()
    add(images)
  }
  return { uploads, documents, setDocuments, uploading, paths, add, remove, reset, dragOver, drop, paste }
}

export type AttachmentDraft = ReturnType<typeof useAttachments>
