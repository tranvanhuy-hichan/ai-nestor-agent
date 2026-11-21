import type { PlanItem } from './types'

export type ChatEvent =
  | { type: 'session'; id: string; run_id?: string }
  | { type: 'status'; text: string; tpl?: string; vars?: Record<string, string | number> }
  | { type: 'thinking'; text: string }
  | { type: 'delta'; text: string }
  | { type: 'assistant'; content: string; provider: string; usage: { prompt: number; completion: number }; duration_ms?: number }
  | { type: 'tool'; id: string; name: string; args: Record<string, unknown>; risk?: string }
  | { type: 'tool_result'; id: string; result: string; ok: boolean; duration_ms?: number; decision?: string }
  | { type: 'approval'; id: string; kind: string; detail: string }
  | { type: 'question'; id: string; question: string; options: string[]; form?: FormQuestion[] }
  | { type: 'question_done'; id: string; answer: string }
  | { type: 'turn_summary'; files: { path: string; status: string; added: number; removed: number }[] }
  | { type: 'approval_done'; id: string; ok: boolean }
  | { type: 'files' }
  | { type: 'plan'; items: PlanItem[] }
  | { type: 'service_login'; name: string; label: string }
  | { type: 'notice'; message: string; tpl?: string; vars?: Record<string, string | number> }
  | { type: 'error'; message: string; tpl?: string; vars?: Record<string, string | number> }
  | { type: 'done' }

export async function streamChat(
  body: { text: string; session: string | null; provider: string | null; attachments?: string[]; permission?: string; effort?: string; assistant?: string; context?: string },
  onEvent: (e: ChatEvent) => void,
  signal: AbortSignal,
) {
  const r = await fetch('/api/chat', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body), signal })
  return readSse(r, onEvent)
}

export type FormQuestion = { question: string; options: string[]; multi?: boolean }
export type RunState = { active: boolean; cursor: number; run_id: string | null; base_count: number; user: { text: string; attachments: string[] } | null }

async function readSse(r: Response, onEvent: (e: ChatEvent) => void) {
  if (r.status === 401) window.dispatchEvent(new Event('auth-required'))
  if (!r.ok || !r.body) throw Object.assign(new Error(`HTTP ${r.status}`), { status: r.status })
  const reader = r.body.getReader()
  const dec = new TextDecoder()
  let buf = ''
  for (;;) {
    const { done, value } = await reader.read()
    if (done) break
    buf += dec.decode(value, { stream: true })
    let i: number
    while ((i = buf.indexOf('\n\n')) >= 0) {
      const frame = buf.slice(0, i)
      buf = buf.slice(i + 2)
      if (frame.startsWith('data: ')) {
        const event = JSON.parse(frame.slice(6)) as ChatEvent
        onEvent(event)
        if (event.type === 'done') {
          void reader.cancel().catch(() => {})
          return true
        }
      }
    }
  }
  return false
}

/** Noi lai luong cua luot dang chay tren server (sau khi doi trang / doi phien). */
export async function attachChat(sid: string, runId: string, start: number, onEvent: (e: ChatEvent) => void, signal: AbortSignal, onReconnect: () => void) {
  let cursor = start
  for (let attempt = 0; attempt < 5 && !signal.aborted; attempt++) {
    if (attempt) {
      onReconnect()
      await new Promise((resolve) => setTimeout(resolve, 500 * attempt))
      if (signal.aborted) return
    }
    try {
      const url = `/api/sessions/${sid}/attach?start=${cursor}&run_id=${encodeURIComponent(runId)}`
      const complete = await readSse(await fetch(url, { signal }), (event) => {
        cursor += 1
        onEvent(event)
      })
      if (complete || signal.aborted) return
    } catch (error) {
      if (signal.aborted) return
      if (error instanceof Error && 'status' in error && [401, 403, 404, 409].includes(Number(error.status))) throw error
      if (attempt === 4) throw error
    }
  }
  if (!signal.aborted) throw new Error('Chat stream disconnected')
}
