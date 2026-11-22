import { useEffect, useRef, useState } from 'react'
import { renderAsync } from 'docx-preview'
import { ErrorNote, Loading } from '@/components/ui/misc'
import { t } from '@/lib/i18n.ts'
import { sourceRanges } from './sourceMatch'

const frameMarkup = `<!doctype html>
<meta charset="utf-8">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; img-src data:; font-src data:; style-src 'unsafe-inline'; form-action 'none'; base-uri 'none'">
<style>
  body { margin: 0; padding: 12px; }
  .nestor-word-wrapper { background: transparent !important; padding: 0 !important; }
  mark[data-citation] { background: #fde047; color: inherit; }
</style>`

function highlightCitation(doc: Document, quotes: string[]) {
  const walker = doc.createTreeWalker(doc.body, NodeFilter.SHOW_TEXT, {
    acceptNode: (node) => node.parentElement?.namespaceURI === 'http://www.w3.org/1999/xhtml'
      ? NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_REJECT,
  })
  const nodes: Text[] = []
  while (walker.nextNode()) {
    const node = walker.currentNode as Text
    if (node.length) nodes.push(node)
  }
  const matches = sourceRanges(nodes.map((node) => node.data), quotes)
  let offset = 0
  let first: HTMLElement | undefined
  let matchIndex = 0
  for (const node of nodes) {
    const end = offset + node.length
    while (matches[matchIndex]?.end <= offset) matchIndex++
    const local: { start: number; end: number }[] = []
    for (let index = matchIndex; matches[index]?.start < end; index++) {
      const match = matches[index]
      const start = Math.max(0, match.start - offset)
      const finish = Math.min(node.length, match.end - offset)
      const previous = local.at(-1)
      if (previous && previous.end >= start) previous.end = Math.max(previous.end, finish)
      else local.push({ start, end: finish })
    }
    for (const { start, end: finish } of local.reverse()) {
      const range = doc.createRange()
      range.setStart(node, start)
      range.setEnd(node, finish)
      const mark = doc.createElement('mark')
      mark.dataset.citation = ''
      range.surroundContents(mark)
    }
    if (local.length && !first) first = doc.querySelector<HTMLElement>('mark[data-citation]') ?? undefined
    offset = end
  }
  return first
}

export default function WordPreview({ url, name, quotes }: { url: string; name: string; quotes: string[] }) {
  const frame = useRef<HTMLIFrameElement>(null)
  const [doc, setDoc] = useState<Document | null>(null)
  const [ready, setReady] = useState(false)
  const [missing, setMissing] = useState(false)
  const [error, setError] = useState<unknown>(null)

  useEffect(() => {
    const element = frame.current
    if (!doc || !element) return
    const abort = new AbortController()
    let resize: ResizeObserver | undefined
    const open = async () => {
      const response = await fetch(url, { signal: abort.signal })
      if (!response.ok) throw new Error(t('Không mở được tệp Word.'))
      const bytes = await response.arrayBuffer()
      if (abort.signal.aborted) return
      const style = doc.createElement('div')
      await renderAsync(bytes, doc.body, style, {
        className: 'nestor-word', ignoreLastRenderedPageBreak: false, renderAltChunks: false, useBase64URL: true,
      })
      if (abort.signal.aborted) return
      doc.head.append(...style.childNodes)
      doc.body.querySelectorAll('a[href]').forEach((link) => link.removeAttribute('href'))
      const wrapper = doc.querySelector<HTMLElement>('.nestor-word-wrapper')
      if (wrapper) {
        const fit = () => {
          const widest = Math.max(1, ...Array.from(wrapper.children, (page) => (page as HTMLElement).offsetWidth))
          wrapper.style.zoom = String(Math.max(0.05, Math.min(1, (element.clientWidth - 24) / widest)))
        }
        fit()
        resize = new ResizeObserver(fit)
        resize.observe(element)
      }
      const mark = quotes.length ? highlightCitation(doc, quotes) : undefined
      setMissing(quotes.length > 0 && !mark)
      setReady(true)
      if (mark) {
        await Promise.all([doc.fonts.ready, ...Array.from(doc.images, (img) => img.decode().catch(() => {}))])
        if (!abort.signal.aborted) {
          doc.defaultView?.scrollBy(0, mark.getBoundingClientRect().top - element.clientHeight / 2)
        }
      }
    }
    void open().catch((cause: unknown) => { if (!abort.signal.aborted) setError(cause) })
    return () => {
      abort.abort()
      resize?.disconnect()
    }
  }, [doc, url, quotes])

  return <div className="relative flex min-h-0 flex-1 flex-col bg-bg">
    {error != null ? <ErrorNote error={error} /> : !ready && <div className="absolute inset-0"><Loading /></div>}
    {missing && <p className="px-3 py-2 text-xs text-muted">{t('Không tìm thấy đoạn trích khớp trên trang hiển thị.')}</p>}
    <iframe ref={frame} title={name} sandbox="allow-same-origin" srcDoc={frameMarkup}
      onLoad={() => setDoc(frame.current?.contentDocument ?? null)}
      className={`block min-h-0 w-full flex-1 border-0 ${ready ? '' : 'invisible'}`} />
  </div>
}
