import { useEffect, useRef, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { ExternalLink, Languages, Play, Square, Download, Volume2, Radio, ArrowLeft, Settings2, Maximize2, Minimize2, X } from 'lucide-react'
import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/Button'
import { api } from '@/lib/api'
import { AgentMark } from '@/components/ui/AgentMark'
import { cn } from '@/lib/utils'
import { loadTranslatePreferences, TRANSLATE_PREFS_KEY } from './preferences'
import { YouTubePlayer } from './YouTubePlayer'
import { CaptionEntry } from './CaptionEntry'
import { captureSupportReason } from './captureSupport'
import { useLiveTranslation, type Caption } from './useLiveTranslation'

type Options = { languages: Record<string, string>; transcribers: string[]; translators: { id: string; model: string }[] }
export function youtubeId(input: string): string | null {
  try {
    const u = new URL(input)
    if (u.protocol !== 'https:' && u.protocol !== 'http:') return null
    const host = u.hostname.replace(/^www\./, '')
    const id = host === 'youtu.be' ? u.pathname.slice(1) : ['youtube.com', 'm.youtube.com'].includes(host) ? (u.searchParams.get('v') || /^\/(?:shorts|live|embed)\/([^/]+)/.exec(u.pathname)?.[1]) : null
    return id && /^[\w-]{11}$/.test(id) ? id : null
  } catch { return null }
}
function stamp(n: number) { return new Date(Math.max(0, n) * 1000).toISOString().slice(11, 19) }
function saveSrt(captions: Caption[], lang: string) {
  const time = (n: number) => `${stamp(n)},${String(Math.floor(n * 1000) % 1000).padStart(3, '0')}`
  const text = captions.map((c, i) => `${i + 1}\n${time(c.start)} --> ${time(c.end)}\n${lang === 'original' ? c.text : c.translations[lang] || ''}\n`).join('\n')
  const url = URL.createObjectURL(new Blob([text], { type: 'text/plain;charset=utf-8' }))
  const a = document.createElement('a'); a.href = url; a.download = `youtube-${lang}.srt`; a.click(); window.setTimeout(() => URL.revokeObjectURL(url), 1000)
}
export function LiveTranslatePage() {
  const options = useQuery({ queryKey: ['live-translate-options'], queryFn: () => api.get<Options>('/api/live-translate/options') })
  const [saved] = useState(loadTranslatePreferences)
  const [url, setUrl] = useState(saved.url), [source, setSource] = useState(saved.source), [targets, setTargets] = useState(saved.targets)
  const [translator, setTranslator] = useState(saved.translator), [voice, setVoice] = useState(saved.voice), [download, setDownload] = useState(saved.download), [follow, setFollow] = useState(saved.follow)
  const [showOriginal, setShowOriginal] = useState(saved.showOriginal)
  const [playback, setPlayback] = useState(saved.playback)
  const embedded = playback === 'embedded'
  const live = useLiveTranslation(voice)
  const captionsPane = useRef<HTMLDivElement>(null)
  const [settingsOpen, setSettingsOpen] = useState(saved.settingsOpen || !youtubeId(saved.url))
  const [wide, setWide] = useState(saved.wide)
  const langs = options.data?.languages ?? { vi: 'Tiếng Việt', en: 'English' }
  const model = (options.data?.translators.some((p) => p.id === translator) ? translator : '') || options.data?.translators.find((p) => p.id === 'groq')?.id || options.data?.translators[0]?.id || ''
  const transcriber = options.data?.transcribers[0] || ''
  const supportError = captureSupportReason()
  const supported = !supportError
  const locked = live.running || live.starting || live.pending > 0
  const video = youtubeId(url)
  useEffect(() => {
    try { localStorage.setItem(TRANSLATE_PREFS_KEY, JSON.stringify({ url, source, targets, translator: options.data ? model : translator, voice, download, follow, settingsOpen, showOriginal, playback, wide })) } catch { /* Private browsing / full storage must not interrupt translation. */ }
  }, [url, source, targets, translator, model, voice, download, follow, settingsOpen, showOriginal, playback, wide, options.data])
  useEffect(() => { if (download !== 'original' && live.captions.length && !live.captions.some((c) => download in c.translations)) setDownload('original') }, [live.captions, download])
  useEffect(() => { if (follow && captionsPane.current) captionsPane.current.scrollTo({ top: captionsPane.current.scrollHeight, behavior: 'smooth' }) }, [live.captions.length, live.captions[live.captions.length - 1]?.translations, live.draft, follow, wide])
  return <div className="flex h-full min-h-0 flex-col overflow-hidden px-4 py-4 sm:px-6">
    <header className="mb-3 flex shrink-0 flex-wrap items-center justify-between gap-3">
      <div className="flex items-center gap-2.5"><span className="grid size-9 place-items-center rounded-xl bg-accent/10 text-accent"><Languages className="size-4" /></span><h1 className="text-base font-semibold">Phiên dịch YouTube</h1></div>
      <div className="flex flex-wrap items-center gap-2">
        {model && <span title={options.data?.translators.find((p) => p.id === model)?.model} className="max-w-52 truncate rounded-lg border border-line px-2.5 py-2 text-[11px] text-muted">{options.data?.translators.find((p) => p.id === model)?.model}</span>}
        <button aria-expanded={settingsOpen} aria-controls="translation-settings" onClick={() => setSettingsOpen((v) => !v)} className="flex items-center gap-1.5 rounded-lg border border-line px-2.5 py-2 text-xs"><Settings2 className="size-3.5" />Tùy chọn</button>
        {embedded && video && <button aria-pressed={wide} onClick={() => setWide((v) => !v)} className={cn('flex items-center gap-1.5 rounded-lg border px-2.5 py-2 text-xs', wide ? 'border-accent/40 bg-accent/10 text-accent' : 'border-line')}>
          {wide ? <Minimize2 className="size-3.5" /> : <Maximize2 className="size-3.5" />}{wide ? 'Thu gọn' : 'Xem rộng'}
        </button>}
        {embedded && voice && <Button size="sm" aria-label="Mở cửa sổ giọng dịch" onClick={live.prepareVoice}><Volume2 className="size-3.5" />{live.voiceReady ? 'Giọng dịch đã mở' : 'Mở giọng dịch'}</Button>}
        {live.running ? <Button variant="danger" size="sm" onClick={live.stop}><Square className="size-3.5" />Dừng nghe</Button> : <Button variant="primary" size="sm" loading={live.starting} disabled={!supported || !video || !targets.length || !model || !transcriber || live.pending > 0 || (embedded && !!voice && !live.voiceReady)} onClick={() => { void live.start({ source, targets, translator: model, transcriber, captureCurrentTab: embedded }); setSettingsOpen(false) }}><Play className="size-3.5" />Bắt đầu nghe và dịch</Button>}
        <Link to="/f" className="flex items-center gap-1 px-1 text-xs text-muted hover:text-fg"><ArrowLeft className="size-3.5" />Công cụ</Link>
      </div>
    </header>
    <div className="relative grid min-h-0 flex-1 grid-rows-[minmax(0,1fr)]">
      <aside id="translation-settings" className={cn("absolute inset-y-0 left-0 z-20 w-full min-h-0 space-y-3 overflow-y-auto overscroll-contain rounded-xl border border-line bg-bg p-3 shadow-2xl sm:w-80", !settingsOpen && "hidden")}>
        <div className="flex items-center justify-between"><h2 className="text-sm font-semibold">Tùy chọn phiên dịch</h2><button aria-label="Đóng tùy chọn" onClick={() => setSettingsOpen(false)} className="rounded-lg p-1.5 text-muted hover:bg-panel2 hover:text-fg"><X className="size-4" /></button></div>
        {supportError && <p role="alert" className="rounded-xl border border-accent/30 bg-accent/5 p-4 text-sm leading-relaxed">{supportError}</p>}
        <section className="space-y-4 rounded-xl border border-line bg-panel p-4">
          <label className="block text-xs font-medium">Link YouTube<input value={url} onChange={(e) => setUrl(e.target.value)} disabled={locked} placeholder="https://www.youtube.com/watch?v=…" className="mt-2 w-full rounded-lg border border-line bg-bg px-3 py-2.5 text-sm outline-none focus:border-accent" /></label>
          <fieldset disabled={locked} className="grid grid-cols-2 gap-1 rounded-lg bg-bg p-1"><legend className="mb-2 text-xs font-medium">Cách xem video</legend>{([{ id: 'embedded', label: 'Xem tại đây' }, { id: 'external', label: 'Tab riêng' }] as const).map((mode) => <button key={mode.id} type="button" aria-pressed={playback === mode.id} onClick={() => setPlayback(mode.id)} className={cn('rounded-md px-2 py-2 text-xs font-medium transition', playback === mode.id ? 'bg-accent/15 text-accent' : 'text-muted hover:text-fg')}>{mode.label}</button>)}</fieldset>
          {url && !video && <p role="alert" className="text-xs text-bad">Link YouTube chưa hợp lệ.</p>}
          {!embedded && video && <a href={`https://www.youtube.com/watch?v=${video}`} target="_blank" rel="noreferrer" className="flex items-center justify-center gap-2 rounded-lg border border-accent/30 bg-accent/5 py-2.5 text-sm text-accent"><ExternalLink className="size-4" />Mở video ở tab riêng</a>}
          <label className="block text-xs font-medium">Ngôn ngữ video<select aria-label="Ngôn ngữ video" value={source} disabled={locked} onChange={(e) => setSource(e.target.value)} className="mt-2 w-full rounded-lg border border-line bg-bg px-3 py-2 text-sm"><option value="auto">Tự nhận diện</option>{Object.entries(langs).map(([id, label]) => <option key={id} value={id}>{label}</option>)}</select></label>
          <fieldset disabled={locked}><legend className="mb-2 text-xs font-medium">Phụ đề muốn xem <span className="text-muted">· tối đa 4</span></legend><div className="grid grid-cols-2 gap-2">{Object.entries(langs).map(([id, label]) => <label key={id} className={cn('flex cursor-pointer items-center gap-2 rounded-lg border px-2.5 py-2 text-xs', targets.includes(id) ? 'border-accent/40 bg-accent/10' : 'border-line')}><input type="checkbox" className="accent-[var(--accent)]" checked={targets.includes(id)} disabled={!targets.includes(id) && targets.length >= 4} onChange={() => { setTargets((p) => p.includes(id) ? p.filter((x) => x !== id) : [...p, id]); if (voice === id) setVoice('') }} />{label}</label>)}</div></fieldset>
          <label className="block text-xs font-medium">Model dịch<select aria-label="Model dịch" value={model} disabled={locked} onChange={(e) => setTranslator(e.target.value)} className="mt-2 w-full rounded-lg border border-line bg-bg px-3 py-2 text-xs">{options.data?.translators.map((p) => <option key={p.id} value={p.id}>{p.model} · {p.id}</option>)}</select></label>
          <label className="block text-xs font-medium"><span className="flex items-center gap-1.5"><Volume2 className="size-3.5" />Giọng đọc bản dịch</span><select aria-label="Giọng đọc bản dịch" value={voice} onChange={(e) => setVoice(e.target.value)} className="mt-2 w-full rounded-lg border border-line bg-bg px-3 py-2 text-sm"><option value="">Tắt giọng đọc</option>{targets.map((id) => <option key={id} value={id}>{langs[id]}</option>)}</select></label>
          {embedded && voice && <div className="space-y-2 rounded-lg border border-accent/20 bg-accent/5 p-3"><p className="text-[11px] leading-relaxed text-muted">Giọng dịch phát ở cửa sổ riêng để không bị thu lại cùng tiếng video. Có thể thu nhỏ cửa sổ đó.</p><p className="text-[11px] font-medium text-accent">{live.voiceReady ? 'Cửa sổ giọng dịch đã sẵn sàng.' : 'Bấm Mở giọng dịch trên thanh công cụ trước khi bắt đầu.'}</p></div>}
          <p className="text-[11px] leading-relaxed text-muted">Âm thanh gửi tới Groq để nhận diện; bản chép gửi tới model đã chọn. Bật giọng đọc sẽ gửi bản dịch tới Google. Chỉ thu tab bạn chia sẻ, không dùng micro.</p>

        </section>
        <section className="rounded-xl border border-line bg-panel p-4 text-xs leading-relaxed"><h2 className="mb-2 font-semibold">Cách bắt đầu</h2><ol className="list-decimal space-y-2 pl-4">{embedded ? <><li>Dán link, bấm phát video ở khung bên cạnh. Nếu bật giọng đọc, mở cửa sổ giọng dịch trước.</li><li>Bấm bắt đầu, chọn <strong>tab Nestor này</strong> và bật <strong>chia sẻ âm thanh của tab</strong>.</li><li>Vừa xem video, đọc phụ đề và nghe giọng dịch. Không chia sẻ cửa sổ giọng dịch hoặc toàn màn hình.</li></> : <><li>Mở video YouTube ở tab riêng và phát video.</li><li>Bấm bắt đầu, chọn đúng <strong>tab YouTube</strong> và bật <strong>chia sẻ âm thanh của tab</strong>.</li><li>Quay lại Nestor để xem phụ đề và nghe bản dịch.</li></>}</ol><p className="mt-3 text-muted">Dịch theo từng câu, lần lượt theo thứ tự: chờ người nói hết câu rồi mới dịch. Mốc SRT tính từ lúc bắt đầu nghe. Tải phụ đề trước khi rời trang để giữ lại.</p></section>
        
        {options.isError && <p role="alert" className="text-xs text-bad">Không tải được cấu hình. <button className="underline" onClick={() => void options.refetch()}>Thử lại</button></p>}
        {options.data && (!transcriber || !model) && <p role="alert" className="rounded-lg border border-line p-3 text-xs text-muted">Cần thêm Groq API có quyền nhận diện âm thanh và model API để dịch trong <Link to="/providers" className="text-accent underline">Mô hình AI</Link>.</p>}
      </aside>
      <div className={cn('grid h-full min-h-0 min-w-0 gap-3', embedded && video ? wide ? 'grid-rows-[minmax(235px,1fr)_auto]' : 'grid-rows-[minmax(235px,1fr)_minmax(150px,0.65fr)] lg:grid-cols-[minmax(0,1fr)_22rem] lg:grid-rows-[minmax(0,1fr)]' : 'grid-rows-[minmax(0,1fr)]')}>
      {embedded && video && <YouTubePlayer video={video} locked={locked} onExternal={() => setPlayback('external')} />}
      {embedded && video && wide ? <section aria-label="Bản dịch khi xem rộng" className="max-h-[28vh] min-h-0 overflow-y-auto rounded-xl border border-accent/20 bg-panel px-4 py-3">
        <div className="mb-2 flex items-center justify-between gap-2"><h2 className="flex items-center gap-2 text-xs font-medium"><AgentMark size="sm" className="!mt-0 !size-5 !rounded-md" />Bản dịch mới nhất</h2><button onClick={() => setWide(false)} className="text-[11px] text-accent">Lịch sử phụ đề</button></div>
        {live.error && <p role="alert" className="mb-2 text-xs text-bad">{live.error}</p>}{live.voiceError && <p role="status" className="mb-2 text-xs text-muted">{live.voiceError}</p>}
        {live.captions.length ? <div className={cn('grid gap-3', Object.keys(live.captions[live.captions.length - 1].translations).length > 1 && 'sm:grid-cols-2')}>{Object.entries(live.captions[live.captions.length - 1].translations).map(([id, text]) => <div key={id}><span className="mr-2 text-[10px] font-semibold text-accent">{langs[id] || id}</span><span lang={id} className="text-sm leading-relaxed">{text || '…'}</span></div>)}</div> : <p className="text-sm text-muted">{live.running ? 'Đang nghe video, chờ bản dịch…' : 'Phát video rồi bấm bắt đầu để xem bản dịch tại đây.'}</p>}
      </section> : <section className="flex h-full min-h-0 min-w-0 flex-col overflow-hidden rounded-xl border border-line bg-panel">
        <div className="flex shrink-0 flex-wrap items-center justify-between gap-3 border-b border-line px-4 py-3">
          <div className="flex min-w-0 flex-wrap items-center gap-3"><h2 className="flex items-center gap-2 text-sm font-semibold"><Languages className="size-4 text-accent" />Phụ đề trực tiếp</h2><span role="status" className={cn('flex items-center gap-1.5 rounded-full px-2 py-1 text-[10px] font-medium', live.running ? 'bg-accent/10 text-accent' : 'bg-fg/5 text-muted')}><Radio className={cn('size-3', live.running && live.level && 'text-ok')} />{live.starting ? 'Đang mở chia sẻ tab…' : live.running ? live.level ? 'Đang nhận âm thanh' : 'Đang nghe · chờ âm thanh' : live.pending ? 'Đang hoàn tất bản dịch…' : live.captions.length ? 'Đã dừng nghe' : 'Sẵn sàng phiên dịch'}</span>{live.pending > 0 && <span className="text-[11px] text-muted">{live.pending} đoạn đang xử lý</span>}</div>
          <div className="flex flex-wrap items-center gap-4 text-[11px] text-muted"><label className="flex cursor-pointer items-center gap-1.5"><input type="checkbox" className="size-3.5 accent-[var(--accent)]" checked={showOriginal} onChange={(e) => setShowOriginal(e.target.checked)} />Hiện bản gốc</label><label className="flex cursor-pointer items-center gap-1.5"><input type="checkbox" className="size-3.5 accent-[var(--accent)]" checked={follow} onChange={(e) => setFollow(e.target.checked)} />Theo dõi mới nhất</label></div>
        </div>
        {live.error && <p role="alert" className="m-3 max-h-28 shrink-0 overflow-y-auto rounded-lg border border-bad/30 bg-bad/5 p-3 text-xs text-bad">{live.error}</p>}{live.voiceError && <p role="status" className="mx-3 mt-2 max-h-20 shrink-0 overflow-y-auto text-xs text-muted">{live.voiceError}</p>}
        <div role="region" aria-label="Phụ đề trực tiếp" ref={captionsPane} className="min-h-0 flex-1 space-y-3 overflow-y-auto overscroll-contain bg-bg/20 p-3 sm:p-4">
          {!live.captions.length && !live.draft && <div className="grid min-h-72 place-content-center justify-items-center gap-3 text-center text-muted"><AgentMark /><p className="text-sm">Phụ đề và bản dịch sẽ xuất hiện tại đây</p><p className="max-w-sm text-xs leading-relaxed">{embedded ? 'Phát video, rồi chia sẻ âm thanh của tab Nestor này để bắt đầu dịch.' : 'Bạn có thể đọc nhiều ngôn ngữ cùng lúc. Giọng đọc dùng một ngôn ngữ để tránh chồng tiếng.'}</p></div>}
          {live.captions.map((caption, i) => <CaptionEntry key={caption.id} caption={caption} latest={i === live.captions.length - 1} languages={langs} showOriginal={showOriginal} compact={!!(embedded && video)} />)}
          {live.draft && <div className="rounded-xl border border-dashed border-accent/25 bg-accent/5 p-3"><p className="mb-1.5 text-xs font-medium text-accent">Đang nghe, chờ hết câu để dịch…</p><p className="whitespace-pre-wrap break-words text-xs leading-relaxed text-muted">{live.draft}</p></div>}
        </div>
        {live.captions.length > 0 && <footer className="flex shrink-0 flex-wrap items-center justify-between gap-2 border-t border-line p-3"><span className="text-xs text-muted">{live.captions.length} đoạn · thời gian tính từ lúc bắt đầu nghe</span><div className="flex gap-2"><select aria-label="Ngôn ngữ tải phụ đề" value={download} onChange={(e) => setDownload(e.target.value)} className="rounded-lg border border-line bg-bg px-2 text-xs"><option value="original">Bản gốc</option>{[...new Set(live.captions.flatMap((c) => Object.keys(c.translations)))].map((id) => <option key={id} value={id}>{langs[id]}</option>)}</select><Button size="sm" onClick={() => saveSrt(live.captions, download)}><Download className="size-3.5" />Tải SRT</Button></div></footer>}
      </section>}
      </div>
    </div>
  </div>
}
