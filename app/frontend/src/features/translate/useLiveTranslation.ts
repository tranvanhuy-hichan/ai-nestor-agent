import { useEffect, useRef, useState } from 'react'
import { captureSourceError, exposeCaptureHandle } from './captureSource'
import { captureSupportReason } from './captureSupport'
import { speechSegments } from '../chat/speech'

export type Caption = { id: number; start: number; end: number; text: string; translations: Record<string, string> }
export type Settings = { source: string; targets: string[]; transcriber: string; translator: string; captureCurrentTab?: boolean }
export function useLiveTranslation(voice: string) {
  const [running, setRunning] = useState(false)
  const [starting, setStarting] = useState(false)
  const [pending, setPending] = useState(0)
  const [captions, setCaptions] = useState<Caption[]>([])
  const [draft, setDraft] = useState('')
  const [error, setError] = useState('')
  const [voiceError, setVoiceError] = useState('')
  const [voiceReady, setVoiceReady] = useState(false)
  const voiceWindow = useRef<Window | null>(null), outputAudio = useRef<HTMLAudioElement | null>(null)
  const [captureHandle] = useState(() => `argus-translation-${crypto.randomUUID()}`)
  const handleExposed = useRef(false)
  const [level, setLevel] = useState(false)
  const live = useRef(false), epoch = useRef(0), voiceRef = useRef(voice)
  const capture = useRef<(() => void) | null>(null), abort = useRef(new AbortController())
  const [speaker] = useState(() => ({ current: new Audio() }))
  const spoken = useRef<{ text: string; lang: string; audio?: Promise<Blob | null> }[]>([])
  const currentTab = useRef(false)
  const voiceFailed = useRef(false)
  const speaking = useRef(false), audioUrl = useRef(''), voiceEpoch = useRef(0)
  const stopVoice = () => {
    voiceEpoch.current++; spoken.current = []; speaking.current = false
    for (const audio of [speaker.current, outputAudio.current]) {
      if (audio) { audio.onended = null; audio.onerror = null; audio.onplay = null; audio.pause(); audio.removeAttribute('src'); audio.load() }
    }
    if (audioUrl.current) URL.revokeObjectURL(audioUrl.current)
    audioUrl.current = ''
  }
  const prepareVoice = () => {
    setVoiceError('')
    if (voiceWindow.current && !voiceWindow.current.closed) { voiceWindow.current.focus(); return }
    const popup = window.open('/translation-audio.html', `argus-voice-${crypto.randomUUID()}`, 'popup,width=460,height=310')
    if (!popup) { setVoiceError('Trình duyệt đang chặn cửa sổ giọng dịch. Hãy cho phép cửa sổ bật lên rồi bấm mở giọng dịch lại.'); return }
    voiceWindow.current = popup
  }
  useEffect(() => {
    handleExposed.current = exposeCaptureHandle(captureHandle)
    const timer = window.setInterval(() => {
      const popup = voiceWindow.current
      if (!popup) return
      const unavailable = () => {
        stopVoice(); outputAudio.current = null; voiceWindow.current = null; setVoiceReady(false)
        if (live.current && currentTab.current && voiceRef.current) { voiceFailed.current = true; setVoiceError('Cửa sổ giọng dịch đã đóng hoặc chuyển trang. Phụ đề vẫn chạy; bấm Mở cửa sổ giọng dịch để nghe tiếp.') }
      }
      if (popup.closed) { unavailable(); return }
      try {
        if (popup.location.href === 'about:blank') return
        if (popup.location.origin !== location.origin || popup.location.pathname !== '/translation-audio.html') { unavailable(); return }
        const audio = popup.document.getElementById('translation-output') as HTMLAudioElement | null
        if (audio && outputAudio.current !== audio) { stopVoice(); outputAudio.current = audio; voiceFailed.current = false; setVoiceReady(true); setVoiceError('') }
      } catch { unavailable() }
    }, 300)
    return () => { clearInterval(timer); voiceWindow.current?.close(); voiceWindow.current = null; outputAudio.current = null }
  }, [captureHandle])
  useEffect(() => { voiceRef.current = voice; voiceFailed.current = false; setVoiceError(''); stopVoice() }, [voice])
  const loadSpeech = async (item: { text: string; lang: string }) => {
    try {
      const response = await fetch('/api/speech', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ text: item.text, lang: item.lang }), signal: abort.current.signal })
      if (!response.ok) return null
      const blob = await response.blob()
      return blob.size && blob.type.startsWith('audio/') ? blob : null
    } catch { return null }
  }
  const primeSpeech = () => { const next = spoken.current[0]; if (next && !next.audio) next.audio = loadSpeech(next) }
  const readNext = async () => {
    if (speaking.current || !spoken.current.length) return
    speaking.current = true
    const generation = voiceEpoch.current
    const item = spoken.current.shift()!
    try {
      const pendingAudio = item.audio ?? loadSpeech(item)
      primeSpeech()
      const blob = await pendingAudio
      if (!blob) throw new Error('speech')
      if (generation !== voiceEpoch.current) return
      if (audioUrl.current) URL.revokeObjectURL(audioUrl.current)
      audioUrl.current = URL.createObjectURL(blob)
      const audio = currentTab.current ? outputAudio.current : speaker.current
      if (!audio || (currentTab.current && (!voiceWindow.current || voiceWindow.current.closed))) throw new Error('output window closed')
      audio.src = audioUrl.current
      audio.defaultPlaybackRate = 1.15; audio.playbackRate = 1.15; audio.preservesPitch = true
      audio.onended = () => { speaking.current = false; void readNext() }
      audio.onerror = () => { stopVoice(); voiceFailed.current = true; setVoiceError('Không phát được giọng dịch. Phụ đề vẫn tiếp tục.') }
      audio.onplay = () => { if (generation === voiceEpoch.current) setVoiceError('') }
      try { await audio.play() } catch (e) {
        if ((e as { name?: string } | null)?.name === 'NotAllowedError' && currentTab.current) { setVoiceError('Bấm Phát trong cửa sổ Giọng dịch Argus để bật âm thanh. Phụ đề vẫn tiếp tục.'); return }
        throw e
      }
    } catch { if (generation === voiceEpoch.current) { stopVoice(); voiceFailed.current = true; setVoiceError('Không phát được giọng dịch. Phụ đề vẫn tiếp tục.') } }
  }
  const stop = () => { live.current = false; setRunning(false); setLevel(false); capture.current?.(); capture.current = null }
  const dispose = () => { epoch.current++; live.current = false; capture.current?.(); capture.current = null; abort.current.abort(); stopVoice() }
  useEffect(() => {
    const leave = () => { dispose(); voiceWindow.current?.close() }
    window.addEventListener('pagehide', leave)
    return () => { window.removeEventListener('pagehide', leave); leave() }
  }, [])
  const start = async (settings: Settings) => {
    dispose(); abort.current = new AbortController()
    const generation = epoch.current
    voiceFailed.current = false; currentTab.current = !!settings.captureCurrentTab
    setStarting(true); setError(''); setVoiceError(''); setPending(0)
    try {
      const supportError = captureSupportReason()
      if (supportError) throw new Error(supportError)
      if (settings.captureCurrentTab && voiceRef.current && (!outputAudio.current || !voiceWindow.current || voiceWindow.current.closed)) throw new Error('Bấm Mở cửa sổ giọng dịch trước khi bắt đầu để giọng dịch không bị thu lại.')
      // Capture only a tab. Embedded playback sends speech to a separate, uncaptured window.
      const stream = await navigator.mediaDevices.getDisplayMedia({ video: { displaySurface: 'browser' }, audio: true, selfBrowserSurface: settings.captureCurrentTab ? 'include' : 'exclude', ...(settings.captureCurrentTab ? { preferCurrentTab: true } : {}), systemAudio: 'exclude', monitorTypeSurfaces: 'exclude', surfaceSwitching: 'exclude' } as DisplayMediaStreamOptions)
      if (generation !== epoch.current) { stream.getTracks().forEach((t) => t.stop()); return }
      capture.current = () => stream.getTracks().forEach((t) => t.stop())
      const sourceError = captureSourceError(stream, !!settings.captureCurrentTab, captureHandle, handleExposed.current)
      if (sourceError) { stream.getTracks().forEach((t) => t.stop()); throw new Error(sourceError) }
      if (!stream.getAudioTracks().length) { stream.getTracks().forEach((t) => t.stop()); throw new Error(settings.captureCurrentTab ? 'Chưa chia sẻ âm thanh. Chọn tab Argus này và bật “Chia sẻ âm thanh của tab”.' : 'Chưa chia sẻ âm thanh. Chọn tab YouTube và bật “Chia sẻ âm thanh của tab”.') }
      const mime = ['audio/webm;codecs=opus', 'audio/ogg;codecs=opus', 'audio/mp4'].find((m) => MediaRecorder.isTypeSupported(m))
      if (!mime) { stream.getTracks().forEach((t) => t.stop()); throw new Error('Không có định dạng thu âm phù hợp trên trình duyệt này.') }
      capture.current = () => stream.getTracks().forEach((t) => t.stop())
      const audio = new MediaStream(stream.getAudioTracks())
      const context = new AudioContext(), analyser = context.createAnalyser()
      const source = context.createMediaStreamSource(audio); source.connect(analyser)
      capture.current = () => { stream.getTracks().forEach((t) => t.stop()); void context.close() }
      await context.resume()
      if (generation !== epoch.current) { stream.getTracks().forEach((t) => t.stop()); void context.close(); return }
      const samples = new Float32Array(analyser.fftSize)
      let sound = false, lastSound = 0, processing = false, previous = '', segmentStart = 0
      let nextId = 1, translating = 0
      const origin = performance.now(), queue: { blob: Blob; start: number; end: number }[] = []
      const history = { source: '', translation: {} as Record<string, string> }
      const sync = () => setPending(queue.length + (processing ? 1 : 0) + translating)
      const patch = (id: number, lang: string, text: string) => setCaptions((p) => p.map((c) => (c.id === id ? { ...c, translations: { ...c.translations, [lang]: text } } : c)))
      // Stream one language: words appear as the model produces them.
      const streamTranslation = async (id: number, lang: string, text: string, prevSource: string, prevTranslation: string) => {
        translating++; sync()
        let out = ''
        try {
          const response = await fetch('/api/live-translate/stream', { method: 'POST', headers: { 'Content-Type': 'application/json' }, signal: abort.current.signal,
            body: JSON.stringify({ text, target: lang, translator: settings.translator, previous_source: prevSource, previous_translation: prevTranslation, refine: true }) })
          if (!response.ok || !response.body) throw new Error('stream')
          const reader = response.body.getReader(), decoder = new TextDecoder()
          let buffer = ''
          for (;;) {
            const { done, value } = await reader.read()
            if (done) break
            buffer += decoder.decode(value, { stream: true })
            const lines = buffer.split('\n'); buffer = lines.pop() ?? ''
            for (const line of lines) {
              if (!line.trim()) continue
              const event = JSON.parse(line)
              if (event.error) throw new Error(event.error)
              if (event.delta && generation === epoch.current) { out += event.delta; history.translation[lang] = out; patch(id, lang, out) }
            }
          }
          if (!out.trim() && generation === epoch.current) { out = text; patch(id, lang, out) } // model returned nothing: keep the source visible
          const lang0 = voiceRef.current
          if (lang0 === lang && out.trim() && !voiceFailed.current && generation === epoch.current) {
            const parts = speechSegments(out)
            if (spoken.current.length + parts.length > 6) { stopVoice(); voiceFailed.current = true; setVoiceError('Giọng dịch đang chậm hơn video. Đã tạm ngừng giọng; phụ đề vẫn tiếp tục. Tắt rồi chọn lại giọng để nghe tiếp.') }
            else { spoken.current.push(...parts.map((t) => ({ text: t, lang }))); primeSpeech(); void readNext() }
          }
        } catch (e) {
          if (generation === epoch.current && !(e instanceof DOMException && e.name === 'AbortError')) patch(id, lang, out || '⚠ Chưa dịch được câu này')
        } finally { translating--; if (generation === epoch.current) sync() }
        return out
      }
      const buffer = { text: '', start: 0, end: 0, language: '' }
      let idleTimer = 0, chain: Promise<unknown> = Promise.resolve()
      const flushSentence = () => {
        clearTimeout(idleTimer)
        if (!buffer.text || generation !== epoch.current) return
        const { text, start, end, language } = buffer
        buffer.text = ''; setDraft('')
        const id = nextId++
        translating++; sync()
        // Strictly sequential: the next sentence waits for this one to finish.
        chain = chain.then(async () => {
          if (generation !== epoch.current) return
          const prevSource = history.source, prevTr = { ...history.translation }
          history.source = text
          setCaptions((p) => [...p, { id, start, end, text, translations: Object.fromEntries(settings.targets.map((t) => [t, ''])) }])
          await Promise.all(settings.targets.map((lang) => {
            const base = lang.toLowerCase().split('-')[0]
            if (language && (language === base || language.startsWith(base))) { patch(id, lang, text); return null }
            return streamTranslation(id, lang, text, prevSource, prevTr[lang] ?? '')
          }))
        }).finally(() => { translating--; if (generation === epoch.current) sync() })
      }
      const drain = async () => {
        if (processing) return
        processing = true
        try {
          while (queue.length && generation === epoch.current) {
            const item = queue.shift()!
            sync()
            const encoded = await new Promise<string>((resolve, reject) => { const reader = new FileReader(); reader.onload = () => resolve(String(reader.result).split(',')[1]); reader.onerror = reject; reader.readAsDataURL(item.blob) })
            const response = await fetch('/api/live-translate/transcribe', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ source: settings.source, transcriber: settings.transcriber, audio: encoded, mime: mime.split(';')[0], context: previous }), signal: abort.current.signal })
            const result = await response.json()
            if (!response.ok) throw new Error(typeof result.detail === 'string' ? result.detail : 'Không nhận diện được âm thanh.')
            if (generation !== epoch.current) break
            const text = String(result.text || '').trim()
            if (!text) continue
            const norm = (v: string) => v.toLowerCase().replace(/[^\p{L}\p{N}]+/gu, '')
            if (norm(text) === norm(buffer.text.split(' ').slice(-12).join(' ')) || norm(text) === norm(history.source)) continue // repeated hallucination
            if (!buffer.text) buffer.start = item.start
            buffer.text = `${buffer.text} ${text}`.trim(); buffer.end = item.end; buffer.language = String(result.language || '').toLowerCase()
            previous = `${previous} ${text}`.trim().slice(-400)
            setDraft(buffer.text)
            clearTimeout(idleTimer)
            // A sentence is translated only when complete, so meaning is whole and order is preserved.
            if (/[.!?。？！…]["'”’)\]]*$/.test(text) || buffer.text.length > 260) flushSentence()
            else idleTimer = window.setTimeout(flushSentence, 2500)
          }
        } catch (e) {
          if (generation === epoch.current && !(e instanceof DOMException && e.name === 'AbortError')) { setError(e instanceof Error ? e.message : 'Không dịch được âm thanh.'); stop(); dispose(); setPending(0) }
        } finally {
          processing = false
          if (generation === epoch.current) { sync(); if (queue.length) void drain(); else if (!live.current) flushSentence() }
        }
      }
      live.current = true; setCaptions([]); setDraft(''); setRunning(true)
      let recorder: MediaRecorder | null = null
      const record = () => {
        if (!live.current || generation !== epoch.current) return
        sound = false; lastSound = performance.now(); segmentStart = (performance.now() - origin) / 1000
        recorder = new MediaRecorder(audio, { mimeType: mime, audioBitsPerSecond: 64000 })
        const chunks: Blob[] = []
        recorder.ondataavailable = (e) => { if (e.data.size) chunks.push(e.data) }
        recorder.onerror = () => { setError('Thu âm bị gián đoạn. Hãy chia sẻ lại tab YouTube.'); stop() }
        recorder.onstop = () => {
          if (generation !== epoch.current) return
          const end = (performance.now() - origin) / 1000
          if (sound && chunks.length && generation === epoch.current) {
            queue.push({ blob: new Blob(chunks, { type: mime }), start: segmentStart, end })
            while (queue.length > 4) queue.shift() // stay realtime: skip the oldest audio rather than fall behind
            sync(); void drain()
          }
          record()
        }
        recorder.start()
      }
      const meter = window.setInterval(() => {
        analyser.getFloatTimeDomainData(samples)
        const now = performance.now(), audible = Math.sqrt(samples.reduce((n, v) => n + v * v, 0) / samples.length) > .008
        sound ||= audible; if (audible) lastSound = now
        setLevel(audible)
        // Realtime: cut at a short breath after ~1.5s, or at 3.5s at the latest.
        const duration = (now - origin) / 1000 - segmentStart
        if (recorder?.state === 'recording' && (duration >= 3.5 || (duration >= 1.5 && sound && now - lastSound >= 300))) recorder.stop()
      }, 100)
      capture.current = () => { clearInterval(meter); if (generation === epoch.current) setPending((p) => Math.max(1, p)); if (recorder?.state === 'recording') recorder.stop(); stream.getTracks().forEach((t) => t.stop()); void context.close() }
      stream.getVideoTracks()[0]?.addEventListener('capturehandlechange', () => {
        const changed = captureSourceError(stream, !!settings.captureCurrentTab, captureHandle, handleExposed.current)
        if (changed && live.current) { setError(changed); stop(); dispose(); setPending(0) }
      })
      stream.getTracks().forEach((t) => t.addEventListener('ended', () => { if (live.current) stop() }))
      record()
    } catch (e) {
      if (generation === epoch.current) { capture.current?.(); capture.current = null; setError(e instanceof DOMException && e.name === 'NotAllowedError' ? 'Bạn chưa cho phép chia sẻ tab. Bấm bắt đầu để thử lại.' : e instanceof Error ? e.message : 'Không mở được âm thanh.') }
    } finally { if (generation === epoch.current) setStarting(false) }
  }
  return { running, starting, pending, captions, draft, error, voiceError, voiceReady, prepareVoice, level, start, stop, stopVoice }
}
