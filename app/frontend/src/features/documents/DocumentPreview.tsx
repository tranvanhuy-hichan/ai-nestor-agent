import { lazy, Suspense, useEffect, useMemo, useRef, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { ArrowLeft, Download } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { ErrorNote, Loading } from '@/components/ui/misc'
import { api } from '@/lib/api'
import { t } from '@/lib/i18n.ts'
import type { KbDoc } from '@/lib/types'
import type { DocumentSource } from '@/features/chat/Markdown'
import type { OcrWord } from './PdfPreview'
import { sourceRanges } from './sourceMatch'

const WordPreview = lazy(() => import('./WordPreview'))
const PdfPreview = lazy(() => import('./PdfPreview'))
const MAX_CHUNKS = 200
const images = new Set(['.png', '.jpg', '.jpeg', '.gif', '.webp', '.avif', '.bmp'])
const audio = new Set(['.mp3', '.wav', '.ogg', '.oga'])
const video = new Set(['.mp4', '.webm'])
const office = new Set(['.doc', '.docx', '.odt', '.xls', '.xlsx', '.xlsm', '.ods', '.ppt', '.pptx', '.odp'])

export interface DocumentChunk { id: number; ord: number; loc: string; text: string }
interface DocumentContent { doc: KbDoc; chunks: DocumentChunk[] }
interface TextPreview { text: string | null; truncated: boolean }

function OriginalText({ text, ranges }: { text: string; ranges: ReturnType<typeof sourceRanges> }) {
  const first = useRef<HTMLElement>(null)
  useEffect(() => { first.current?.scrollIntoView({ block: 'center', inline: 'nearest' }) }, [ranges])
  let previous = 0
  return <pre className="whitespace-pre-wrap break-words text-sm leading-relaxed">
    {ranges.map(({ start, end }, i) => {
      if (end <= previous) return null
      const from = Math.max(previous, start)
      const before = text.slice(previous, from)
      previous = end
      return <span key={from}>{before}<mark ref={i === 0 ? first : undefined} className="rounded bg-warn/30 text-fg">{text.slice(from, end)}</mark></span>
    })}
    {text.slice(previous)}
  </pre>
}

export function DocumentPreview({ source, onClose }: { source: DocumentSource; onClose: () => void }) {
  const base = `/api/knowledge/${encodeURIComponent(source.id)}`
  const url = `${base}/file?inline=true`
  const [offset, setOffset] = useState<number | null>(null)
  const params = new URLSearchParams()
  if (offset !== null) params.set('offset', String(offset))
  else if (source.loc) {
    params.set('loc', source.loc)
    if (source.chunkId) params.set('chunk_id', source.chunkId)
  }
  const content = useQuery({
    queryKey: ['kb-preview', source.id, params.toString()],
    queryFn: () => api.get<DocumentContent>(`${base}/chunks?${params}`),
    staleTime: 30_000,
  })
  const doc = content.data?.doc
  const ext = doc?.ext ?? ''
  const pdf = ext === '.pdf'
  const word = ext === '.docx'
  const officeFile = office.has(ext)
  const image = images.has(ext)
  const sound = audio.has(ext)
  const movie = video.has(ext)
  const text = useQuery({
    queryKey: ['kb-original-text', source.id],
    queryFn: () => api.get<TextPreview>(`${base}/preview`),
    enabled: !!doc && !pdf && !image && !sound && !movie && !officeFile,
  })
  const currentChunks = content.data?.chunks
  const isTarget = (chunk: DocumentChunk) => source.chunkId ? String(chunk.id) === source.chunkId : chunk.loc === source.loc
  const quotes = useMemo(() => (currentChunks ?? [])
    .filter((chunk) => source.chunkId ? String(chunk.id) === source.chunkId : chunk.loc === source.loc)
    .map((chunk) => chunk.text), [currentChunks, source.chunkId, source.loc])
  const original = text.data?.text
  const ranges = useMemo(() => original ? sourceRanges([original], quotes) : [], [original, quotes])
  const mark = useRef<HTMLElement>(null)
  const showOriginalText = original != null && (!source.loc || ranges.length > 0)
  useEffect(() => {
    if (offset === null && !showOriginalText) mark.current?.scrollIntoView({ block: 'center', inline: 'nearest' })
  }, [currentChunks, offset, showOriginalText])
  const anchor = currentChunks?.find(isTarget)?.id
  const first = currentChunks?.[0]?.ord ?? 0
  const next = (currentChunks?.at(-1)?.ord ?? -1) + 1
  const startPage = Number(/^(?:trang|page)\s+(\d+)/i.exec(source.loc ?? '')?.[1]) || 1
  const ocr = useQuery({
    queryKey: ['kb-ocr', source.id, startPage],
    queryFn: () => api.get<{ words: OcrWord[] }>(`${base}/ocr/${startPage}`),
    enabled: pdf && !!source.loc && quotes.length > 0,
    retry: false,
  })

  return <section className="flex size-full min-h-0 min-w-0 flex-col" aria-label={t('Xem file gốc')}>
    <header className="flex shrink-0 items-center gap-2 border-b border-line bg-panel p-3">
      <Button size="sm" variant="ghost" aria-label={t('Về danh sách tài liệu')} title={t('Về danh sách tài liệu')} onClick={onClose}><ArrowLeft className="size-4" /></Button>
      <div className="min-w-0 flex-1">
        <h2 className="truncate text-sm font-semibold" title={doc?.name ?? source.name}>{doc?.name ?? source.name}</h2>
        {source.loc && <p className="truncate text-xs text-accent">{source.loc}</p>}
      </div>
      {doc && <a href={`${base}/file`} download aria-label={t('Tải file gốc')} title={t('Tải file gốc')} className="rounded-lg p-2 text-muted hover:bg-panel2 hover:text-fg"><Download className="size-4" /></a>}
    </header>
    {content.isLoading || ocr.isLoading ? <Loading /> : content.error ? <ErrorNote error={content.error} /> : word ? (
      <Suspense fallback={<Loading />}>
        <WordPreview url={`${base}/file`} name={doc?.name ?? source.name} quotes={quotes} />
      </Suspense>
    ) : pdf || officeFile ? (
      <Suspense fallback={<Loading />}>
        <PdfPreview url={officeFile ? `${base}/office-preview` : url} startPage={startPage} quotes={quotes} office={officeFile} ocrWords={ocr.data?.words} />
      </Suspense>
    ) : (
      <div className="min-h-0 flex-1 overflow-auto p-4 sm:p-5">
        {image ? <img src={url} alt={doc?.name ?? source.name} className="mx-auto max-w-full object-contain" />
          : sound ? <audio controls src={url} className="mx-auto w-full max-w-xl" />
          : movie ? <video controls src={url} className="mx-auto max-w-full" />
          : text.isLoading ? <Loading />
          : text.error ? <ErrorNote error={text.error} />
          : showOriginalText ? <>
            <OriginalText text={original} ranges={ranges} />
            {text.data?.truncated && <p className="mt-4 text-xs text-muted">{t('Bản xem trước chỉ hiển thị phần đầu. Tải file gốc để xem đầy đủ.')}</p>}
          </>
          : currentChunks?.length ? (
            <div className="space-y-3">
              <p className="text-xs text-muted">{t('Bản xem trước từ nội dung đã lập chỉ mục.')}</p>
              {currentChunks.map((chunk) => (
                <article key={chunk.id} ref={chunk.id === anchor ? mark : undefined}
                  className={`rounded-lg border p-3 ${isTarget(chunk) ? 'border-warn/50 bg-warn/10' : 'border-line bg-panel'}`}>
                  <p className="mb-1 font-mono text-xs text-muted">{chunk.loc}</p>
                  <p className="whitespace-pre-wrap break-words text-sm leading-relaxed">
                    {isTarget(chunk) ? <mark className="rounded bg-warn/30 text-fg">{chunk.text}</mark> : chunk.text}
                  </p>
                </article>
              ))}
              {(first > 0 || (currentChunks.length === MAX_CHUNKS && next < (doc?.chunks ?? 0))) && <div className="flex justify-between gap-2">
                <Button size="sm" disabled={first === 0} onClick={() => setOffset(Math.max(0, first - MAX_CHUNKS))}>{t('Trang trước')}</Button>
                <Button size="sm" disabled={next >= (doc?.chunks ?? 0)} onClick={() => setOffset(next)}>{t('Trang sau')}</Button>
              </div>}
            </div>
          ) : <p className="text-sm text-muted">{t('Định dạng này chưa có bản xem trước. Bạn có thể tải file gốc.')}</p>}
      </div>
    )}
  </section>
}
