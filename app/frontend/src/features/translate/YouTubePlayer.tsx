import { ExternalLink, MonitorPlay } from 'lucide-react'

/** The video stays in YouTube's player; we only receive audio shared by the user. */
export function YouTubePlayer({ video, onExternal, locked }: { video: string; onExternal: () => void; locked: boolean }) {
  return <section aria-label="Video YouTube" className="flex min-h-0 flex-col overflow-hidden rounded-xl border border-line bg-black">
    <header className="flex shrink-0 items-center justify-between gap-2 border-b border-line bg-panel px-3 py-2"><h2 className="flex items-center gap-2 text-xs font-medium"><MonitorPlay className="size-3.5 text-accent" />Video YouTube</h2><button disabled={locked} onClick={onExternal} className="flex items-center gap-1 text-[11px] text-muted hover:text-fg disabled:opacity-40"><ExternalLink className="size-3" />Dùng tab riêng</button></header>
    <iframe key={video} title="Trình phát video YouTube" src={`https://www.youtube.com/embed/${video}?playsinline=1&rel=0`} referrerPolicy="strict-origin-when-cross-origin" allow="autoplay; encrypted-media; picture-in-picture; fullscreen" allowFullScreen className="min-h-0 w-full flex-1 border-0" />
  </section>
}
