import { Volume2, VolumeX } from 'lucide-react'
import { useEffect, useRef, useState, useSyncExternalStore } from 'react'
import { t, useLang } from '@/lib/i18n.ts'
import { speechText, speechSegments } from './speech'
import { imagePaths, imageUrl, useSessionId } from './session'

export function Images({ text, onOpen }: { text: string; onOpen?: (p: string) => void }) {
  const sid = useSessionId()
  const paths = imagePaths(text)
  if (!sid || !paths.length) return null
  return (
    <div className="my-2 flex flex-wrap gap-2">
      {paths.map((p) => (
        <button key={p} onClick={() => onOpen?.(p)} className="overflow-hidden rounded-lg border border-line bg-panel" title={p}>
          <img src={imageUrl(sid, p)} alt={p} loading="lazy" className="max-h-80 max-w-full object-contain" />
        </button>
      ))}
    </div>
  )
}

let stopReading: (() => void) | null = null
const SPEECH_RATE_EVENT = 'nestor-speech-rate'
const RATES = [1, 1.15, 1.3, 1.5]
const storedRate = () => { try { const n = Number(localStorage.getItem('speech:rate')); return RATES.includes(n) ? n : 1.15 } catch { return 1.15 } }
const subscribeRate = (listener: () => void) => {
  window.addEventListener(SPEECH_RATE_EVENT, listener); window.addEventListener('storage', listener)
  return () => { window.removeEventListener(SPEECH_RATE_EVENT, listener); window.removeEventListener('storage', listener) }
}


/** Audio playback does not depend on browser speech-synthesis voices. */
export function SpeakButton({ text }: { text: string }) {
  const uiLang = useLang()
  const rate = useSyncExternalStore(subscribeRate, storedRate, () => 1.15)
  const audioRef = useRef<HTMLAudioElement | null>(null)
  useEffect(() => { if (audioRef.current) { audioRef.current.defaultPlaybackRate = rate; audioRef.current.playbackRate = rate } }, [rate])
  const [on, setOn] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const current = useRef<(() => void) | null>(null)
  useEffect(() => () => current.current?.(), [])
  const toggle = async () => {
    if (current.current) { current.current(); return }
    stopReading?.()
    const controller = new AbortController()
    const audio = new Audio()
    audioRef.current = audio
    audio.defaultPlaybackRate = rate
    audio.playbackRate = rate
    audio.preservesPitch = true
    let cancelled = false
    let url: string | null = null
    const stop = () => {
      cancelled = true
      controller.abort()
      audio.onended = null; audio.onerror = null
      audio.pause(); audio.removeAttribute('src'); audio.load()
      if (url) { URL.revokeObjectURL(url); url = null }
      if (current.current === stop) current.current = null
      if (stopReading === stop) stopReading = null
      audioRef.current = null
      setOn(false); setLoading(false)
    }
    current.current = stop; stopReading = stop
    setError(''); setOn(true)
    const vi = /[\u0300-\u036f\u0111]/i.test(text.normalize('NFD')) || uiLang === 'vi'
    const segments = speechSegments(speechText(text, vi))
    let idx = 0
    // Fetch one segment ahead while the current segment plays, avoiding a network pause.
    const fetchSegment = async (i: number): Promise<Blob | null> => {
      try {
        const response = await fetch('/api/speech', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ text: segments[i], lang: vi ? 'vi' : 'en' }), signal: controller.signal })
        if (!response.ok) return null
        const blob = await response.blob()
        return blob.size && blob.type.startsWith('audio/') ? blob : null
      } catch { return null }
    }
    let pending = segments.length ? fetchSegment(0) : null
    const playNext = async () => {
      if (cancelled) return
      if (idx >= segments.length) { stop(); return }
      setLoading(true)
      try {
        const blob = await pending
        if (cancelled) return
        if (!blob) throw new Error('speech request failed')
        idx++
        if (url) URL.revokeObjectURL(url)
        url = URL.createObjectURL(blob)
        audio.src = url
        await audio.play()
        if (!cancelled) { setLoading(false); pending = idx < segments.length ? fetchSegment(idx) : null }
      } catch {
        if (!cancelled) { stop(); setError(t('Không thể phát giọng đọc. Vui lòng kiểm tra mạng, âm lượng và thử lại.')) }
      }
    }
    audio.onended = () => void playNext()
    audio.onerror = () => { if (!cancelled) { stop(); setError(t('Không thể phát giọng đọc. Vui lòng kiểm tra mạng, âm lượng và thử lại.')) } }
    await playNext()
  }
  const Icon = on ? VolumeX : Volume2
  return <span className="inline-flex max-w-full flex-wrap items-center gap-2"><button onClick={() => void toggle()} title={t('Giọng Google. Nội dung được gửi tới Google để tạo âm thanh khi bạn bấm đọc.')} className="flex items-center gap-1 hover:text-fg" aria-pressed={on}><Icon className="size-3" />{on ? t('Dừng đọc') : t('Đọc to')}</button><select aria-label={t('Tốc độ đọc')} title={t('Tốc độ đọc')} value={rate} onChange={(e) => { try { localStorage.setItem('speech:rate', e.target.value); window.dispatchEvent(new Event(SPEECH_RATE_EVENT)) } catch { /* storage unavailable */ } }} className="rounded border border-line bg-panel px-1 py-0.5 text-[10px] text-muted outline-none focus:border-accent">{RATES.map((r) => <option key={r} value={r}>{r}×</option>)}</select>{loading && <span role="status" className="text-xs text-muted">{t('Đang tạo giọng đọc…')}</span>}{error && <span role="status" className="max-w-md text-xs text-muted">{error}</span>}</span>
}
