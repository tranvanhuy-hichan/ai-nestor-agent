import { useCallback, useEffect, useLayoutEffect, useRef, useState } from 'react'
import { getDocument, GlobalWorkerOptions, TextLayer, type PDFDocumentProxy, type RenderTask } from 'pdfjs-dist/legacy/build/pdf.mjs'
import worker from 'pdfjs-dist/legacy/build/pdf.worker.min.mjs?url'
import { ErrorNote, Loading } from '@/components/ui/misc'
import { t } from '@/lib/i18n.ts'
import { sourceRanges } from './sourceMatch'
import './pdf-preview.css'

GlobalWorkerOptions.workerSrc = worker
const noQuotes: string[] = []
export interface OcrWord { text: string; x: number; y: number; width: number; height: number }
const noOcrWords: OcrWord[] = []

function appendOcrMarks(layer: HTMLElement, words: OcrWord[], quotes: string[]) {
  const ranges = sourceRanges(words.map((word) => word.text), quotes)
  let offset = 0
  let rangeIndex = 0
  for (const word of words) {
    const end = offset + word.text.length
    while (ranges[rangeIndex]?.end <= offset) rangeIndex++
    if (ranges[rangeIndex]?.start < end) {
      const block = document.createElement('span')
      block.style.cssText = `left:${word.x * 100}%;top:${word.y * 100}%;width:${word.width * 100}%;height:${word.height * 100}%`
      layer.append(block)
    }
    offset = end
  }
}


function PdfPage({ pdf, page, quotes, ocrWords, onMatch }: {
  pdf: PDFDocumentProxy; page: number; quotes: string[]; ocrWords: OcrWord[]; onMatch: (page: number, highlight: Element | null) => void
}) {
  const container = useRef<HTMLDivElement>(null)
  const sheet = useRef<HTMLDivElement>(null)
  const canvas = useRef<HTMLCanvasElement>(null)
  const textLayer = useRef<HTMLDivElement>(null)
  const highlights = useRef<HTMLDivElement>(null)
  const [width, setWidth] = useState(0)
  const [error, setError] = useState<unknown>(null)

  useEffect(() => {
    const el = container.current
    if (!el) return
    const observer = new ResizeObserver(([entry]) => setWidth(Math.floor(entry.contentRect.width)))
    observer.observe(el)
    return () => observer.disconnect()
  }, [])

  useEffect(() => {
    const slot = container.current?.parentElement
    const surface = sheet.current
    const pageCanvas = canvas.current
    const layer = textLayer.current
    const marks = highlights.current
    if (!surface || !pageCanvas || !layer || !marks || !width) return
    let cancelled = false
    let render: RenderTask | undefined
    let overlay: TextLayer | undefined
    const draw = async () => {
      const source = await pdf.getPage(page)
      if (cancelled) return
      const original = source.getViewport({ scale: 1 })
      if (slot) slot.style.aspectRatio = `${original.width} / ${original.height}`
      const scale = width / original.width
      const viewport = source.getViewport({ scale })
      const ratio = Math.min(window.devicePixelRatio || 1, 2)
      pageCanvas.width = Math.ceil(viewport.width * ratio)
      pageCanvas.height = Math.ceil(viewport.height * ratio)
      surface.style.width = `${viewport.width}px`
      surface.style.height = `${viewport.height}px`
      layer.style.setProperty('--total-scale-factor', String(scale * source.userUnit))
      render = source.render({ canvas: pageCanvas, viewport, transform: [ratio, 0, 0, ratio, 0, 0] })
      overlay = new TextLayer({ textContentSource: source.streamTextContent(), container: layer, viewport })
      await Promise.all([render.promise, overlay.render()])
      if (cancelled) return
      const parts = overlay.textContentItemsStr
      const ranges = sourceRanges(parts, quotes)
      const origin = surface.getBoundingClientRect()
      let offset = 0
      let rangeIndex = 0
      for (const [i, part] of parts.entries()) {
        const end = offset + part.length
        const node = overlay.textDivs[i]?.firstChild
        while (ranges[rangeIndex]?.end <= offset) rangeIndex++
        if (node instanceof Text) {
          for (let j = rangeIndex; ranges[j]?.start < end; j++) {
            const match = ranges[j]
            const range = document.createRange()
            range.setStart(node, Math.max(0, match.start - offset))
            range.setEnd(node, Math.min(part.length, match.end - offset))
            for (const rect of range.getClientRects()) {
              const block = document.createElement('span')
              block.style.cssText = `left:${rect.left - origin.left}px;top:${rect.top - origin.top}px;width:${rect.width}px;height:${rect.height}px`
              marks.append(block)
            }
          }
        }
        offset = end
      }
      if (!marks.firstElementChild && ocrWords.length) appendOcrMarks(marks, ocrWords, quotes)
      if (quotes.length) onMatch(page, marks.firstElementChild)
    }
    void draw().catch((e: unknown) => { if (!cancelled) setError(e) })
    return () => {
      cancelled = true
      render?.cancel()
      overlay?.cancel()
      layer.replaceChildren()
      marks.replaceChildren()
    }
  }, [pdf, page, width, quotes, ocrWords, onMatch])

  return <div ref={container} className="w-full">
    {error != null && <ErrorNote error={error} />}
    <div ref={sheet} className="kb-pdf-page relative mx-auto bg-white shadow-lg">
      <canvas ref={canvas} className="block size-full" />
      <div ref={highlights} className="kb-pdf-highlights pointer-events-none absolute inset-0" aria-hidden="true" />
      <div ref={textLayer} className="kb-pdf-text textLayer" />
    </div>
  </div>
}

function PdfPages({ pdf, target, highlightQuotes, originalQuotes, ocrWords }: {
  pdf: PDFDocumentProxy; target?: number; highlightQuotes: string[]; originalQuotes: string[]; ocrWords: OcrWord[]
}) {
  const scroller = useRef<HTMLDivElement>(null)
  const pendingJump = useRef<number | undefined>(undefined)
  const [nearby, setNearby] = useState<Set<number>>(() => new Set([1]))
  const [missing, setMissing] = useState(false)

  useEffect(() => {
    const root = scroller.current
    if (!root) return
    const observer = new IntersectionObserver((entries) => {
      setNearby((previous) => {
        const next = new Set(previous)
        for (const entry of entries) {
          const page = Number((entry.target as HTMLElement).dataset.page)
          if (entry.isIntersecting) next.add(page)
          else next.delete(page)
        }
        return next
      })
    }, { root, rootMargin: '100% 0px' })
    root.querySelectorAll('[data-page]').forEach((slot) => observer.observe(slot))
    return () => observer.disconnect()
  }, [pdf])

  useLayoutEffect(() => {
    const root = scroller.current
    if (!root || target === undefined) return
    const slot = root.querySelector(`[data-page="${target}"]`)
    if (!slot) return
    pendingJump.current = target
    root.scrollTop += slot.getBoundingClientRect().top - root.getBoundingClientRect().top
  }, [target])

  const onMatch = useCallback((page: number, highlight: Element | null) => {
    setMissing(highlight === null)
    const root = scroller.current
    if (!root || pendingJump.current !== page) return
    pendingJump.current = undefined
    if (highlight) {
      root.scrollTop += highlight.getBoundingClientRect().top - root.getBoundingClientRect().top - root.clientHeight / 2
    }
  }, [])

  return (
    <div ref={scroller} tabIndex={0} aria-label={t('Xem file gốc')} className="min-h-0 flex-1 overflow-auto bg-bg p-3">
      <div className="flex flex-col gap-3">
        {Array.from({ length: pdf.numPages }, (_, index) => {
          const page = index + 1
          const isTarget = page === target
          return (
            <div key={page} data-page={page} className="mx-auto w-full max-w-[1100px]">
              <div className="aspect-[210/297] bg-white shadow-lg">
                {(isTarget || nearby.has(page)) && <PdfPage pdf={pdf} page={page} quotes={isTarget ? highlightQuotes : noQuotes} ocrWords={isTarget ? ocrWords : noOcrWords} onMatch={onMatch} />}
              </div>
              {isTarget && (missing || highlightQuotes.length === 0) && originalQuotes.length > 0 && (
                <div className="mt-3 rounded-lg border border-line bg-panel p-3 text-sm">
                  <p className="mb-2 text-muted">{t('Không tìm thấy đoạn trích khớp trên trang hiển thị.')}</p>
                  {originalQuotes.map((quote, i) => <p key={i} className="mb-2 whitespace-pre-wrap"><mark className="rounded bg-warn/25 text-fg">{quote}</mark></p>)}
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}

export default function PdfPreview({ url, startPage, quotes, office = false, ocrWords = noOcrWords }: {
  url: string; startPage: number; quotes: string[]; office?: boolean; ocrWords?: OcrWord[]
}) {
  const [pdf, setPdf] = useState<PDFDocumentProxy | null>(null)
  const [located, setLocated] = useState<{ page: number; quotes: string[] } | null>(null)
  const [error, setError] = useState<unknown>(null)

  useEffect(() => {
    const abort = new AbortController()
    let load: ReturnType<typeof getDocument> | undefined
    const open = async () => {
      if (office) {
        const response = await fetch(url, { signal: abort.signal })
        if (!response.ok) {
          const failure = await response.json().catch(() => ({}))
          throw new Error(failure.detail || t('Không mở được bản xem trước Office.'))
        }
        const data = await response.arrayBuffer()
        if (abort.signal.aborted) return
        load = getDocument({ data, maxImageSize: 32_000_000 })
      } else {
        load = getDocument({ url, maxImageSize: 32_000_000 })
      }
      const doc = await load.promise
      if (!abort.signal.aborted) setPdf(doc)
    }
    void open().catch((err: unknown) => { if (!abort.signal.aborted) setError(err) })
    return () => {
      abort.abort()
      void load?.destroy().catch(() => {})
    }
  }, [url, office])

  useEffect(() => {
    if (!pdf || !office || !quotes.length) return
    let cancelled = false
    const findPage = async () => {
      // A passage can cross a page break in Word. Prefer a full match, then a
      // substantial fragment if the complete passage does not fit on one page.
      const fragments = quotes.flatMap((quote) => quote.split(/(?<=[.!?])\s+|\n+/))
        .filter((fragment) => fragment.length >= 45)
        .sort((a, b) => b.length - a.length)
      let fallback: { page: number; quote: string } | undefined
      for (let index = 1; index <= pdf.numPages && !cancelled; index++) {
        const sheet = await pdf.getPage(index)
        const text = await sheet.getTextContent()
        if (cancelled) return
        const parts = text.items.flatMap((item) => 'str' in item ? [item.str] : [])
        if (sourceRanges(parts, quotes).length) {
          setLocated({ page: index, quotes })
          return
        }
        const candidates = fragments.filter((part) => part.length > (fallback?.quote.length ?? 0))
        const firstMatch = Math.min(...sourceRanges(parts, candidates).map((match) => match.quoteIndex))
        const fragment = candidates[firstMatch]
        if (fragment) fallback = { page: index, quote: fragment }
      }
      if (cancelled) return
      setLocated(fallback ? { page: fallback.page, quotes: [fallback.quote] } : { page: startPage, quotes: noQuotes })
    }
    void findPage().catch(() => {
      if (!cancelled) setLocated({ page: startPage, quotes: noQuotes })
    })
    return () => { cancelled = true }
  }, [pdf, office, quotes, startPage])

  if (error) return <ErrorNote error={error} />
  if (!pdf) return <Loading />
  const locating = office && quotes.length > 0 && located === null
  const target = office ? located?.page : (startPage > 1 || quotes.length ? startPage : undefined)
  return <>
    {locating && <p role="status" className="px-3 pt-2 text-xs text-muted">{t('Đang tìm đoạn trích…')}</p>}
    <PdfPages pdf={pdf} target={target} highlightQuotes={office ? located?.quotes ?? noQuotes : quotes} originalQuotes={quotes} ocrWords={ocrWords} />
  </>
}
