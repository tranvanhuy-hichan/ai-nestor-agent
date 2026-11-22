import { createContext, Fragment, useContext, useState, type ReactNode } from 'react'
import { Check, Copy, Download, FileText } from 'lucide-react'
import { useQuery } from '@tanstack/react-query'
import { Button } from '@/components/ui/Button'
import { Modal } from '@/components/ui/Modal'
import { ErrorNote, Loading } from '@/components/ui/misc'
import { api } from '@/lib/api'
import { t, useLang } from '@/lib/i18n.ts'
import katex from 'katex'
import 'katex/dist/katex.min.css'

function Code({ code, lang }: { code: string; lang: string }) {
  const [copied, setCopied] = useState(false)
  return (
    <div className="my-2 overflow-hidden rounded-lg border border-line bg-bg">
      <div className="flex items-center justify-between border-b border-line px-3 py-1 text-[11px] text-muted">
        <span>{lang || 'code'}</span>
        <button
          onClick={() => {
            void navigator.clipboard.writeText(code).then(() => { setCopied(true); setTimeout(() => setCopied(false), 1500) })
          }}
          className="flex items-center gap-1 hover:text-fg"
        >
          {copied ? <Check className="size-3" /> : <Copy className="size-3" />}{copied ? t('Đã chép') : t('Chép')}
        </button>
      </div>
      <pre className="overflow-x-auto p-3 font-mono text-[12.5px] leading-relaxed"><code>{code}</code></pre>
    </div>
  )
}

export interface DocumentSource { id: string; name: string; loc?: string; chunkId?: string }
export const DocumentSourceContext = createContext<((source: DocumentSource) => void) | null>(null)

/** Thẻ nguồn của kho tài liệu: [[src:id|tên file|vị trí]] hiện thành chip nhỏ; bấm để xem đúng đoạn trích trong một thẻ, tải file gốc là tùy chọn. */
function SourceChip({ id, name, loc: taggedLocation }: { id: string; name: string; loc: string }) {
  const openSource = useContext(DocumentSourceContext)
  const chunkId = /#chunk=(\d+)$/.exec(taggedLocation)?.[1]
  const loc = taggedLocation.replace(/#chunk=\d+$/, '')
  const params = new URLSearchParams({ loc })
  if (chunkId) params.set('chunk_id', chunkId)
  const lang = useLang()
  const [open, setOpen] = useState(false)
  const shown = lang === 'en' ? loc.replace(/^trang /, 'page ').replace(/d\u00f2ng /, 'rows ').replace(/^m\u1ee5c /, 'section ').replace(/^\u0111o\u1ea1n /, 'paragraphs ') : loc
  const ext = /\.[A-Za-z0-9]{2,5}$/.exec(name)?.[0] ?? ''
  const base = name.slice(0, name.length - ext.length)
  const short = base.length > 24 ? `${base.slice(0, 22)}…${ext}` : name
  const passage = useQuery({ queryKey: ['kb-passage', id, taggedLocation], queryFn: () => api.get<{ text: string; truncated: boolean; has_file: boolean }>(`/api/knowledge/${encodeURIComponent(id)}/passage?${params}`), enabled: open, staleTime: 600_000 })
  return (
    <>
      <button type="button" onClick={() => openSource ? openSource({ id, name, loc, chunkId }) : setOpen(true)} title={`${name} · ${loc}`}
        className="mx-0.5 inline-flex max-w-full translate-y-[-1px] items-center gap-1 rounded-md border border-line bg-panel2 px-1.5 py-px align-middle text-[11px] leading-5 text-muted transition hover:border-accent/60 hover:text-fg">
        <FileText className="size-3 shrink-0" /><span className="truncate">{short}</span><span className="shrink-0 text-accent">{shown}</span>
      </button>
      <Modal open={open} onClose={() => setOpen(false)} wide title={<span className="flex min-w-0 items-center gap-2"><FileText className="size-4 shrink-0 text-muted" /><span className="truncate">{name}</span><span className="shrink-0 text-sm font-normal text-accent">{shown}</span></span>}
        footer={<>
          <Button onClick={() => setOpen(false)}>{t('Đóng')}</Button>
          {passage.data?.has_file && <a href={`/api/knowledge/${id}/file`} target="_blank" rel="noreferrer noopener"><Button><Download className="size-4" />{t('Tải file gốc')}</Button></a>}
        </>}>
        {passage.isLoading ? <Loading /> : passage.error ? <ErrorNote error={passage.error} /> : passage.data && (
          <div>
            <p className="whitespace-pre-wrap break-words text-sm leading-relaxed">{passage.data.text || t('(không có nội dung)')}</p>
            {passage.data.truncated && <p className="mt-3 text-xs text-muted">{t('Đoạn trích dài nên chỉ hiện phần đầu. Tải file gốc để xem đầy đủ.')}</p>}
          </div>
        )}
      </Modal>
    </>
  )
}

/** Only KaTeX-generated markup is inserted; model HTML remains escaped by React. */
function MathFormula({ source, display }: { source: string; display: boolean }) {
  const html = katex.renderToString(source, { displayMode: display, throwOnError: false, strict: 'ignore', trust: false, maxSize: 20, maxExpand: 1000, output: 'htmlAndMathml' })
  return <span className={display ? 'math-display' : 'math-inline'} dangerouslySetInnerHTML={{ __html: html }} />
}

function inline(text: string): ReactNode[] {
  const re = /(`[^`\n]+`|(?<!\\)\$\$[^\n]*?\$\$|\\\[[^\n]*?\\\]|\\\([^\n]*?\\\)|(?<![\\$])\$(?![\s$])(?:\\.|[^$\n\\])+?\$(?![\d$])|\*\*[^*\n]+\*\*|\[\[src:[^\]\n]+\]\]|\[\^?\d+\]|\[[^\]\n]+\]\(https?:\/\/[^)\s]+\)|(?<![\w(\]])https?:\/\/[^\s<>)\]]*[^\s<>)\].,;:!?'\"*]|(?<![*\w])\*[^*\s][^*\n]*?\*(?![*\w]))/g
  return text.split(re).map((part, i) => {
    if (part.startsWith('$$') && part.endsWith('$$') && part.length > 4) return <MathFormula key={i} source={part.slice(2, -2)} display />
    if ((part.startsWith('\\[') && part.endsWith('\\]')) || (part.startsWith('\\(') && part.endsWith('\\)'))) return <MathFormula key={i} source={part.slice(2, -2)} display={part.startsWith('\\[')} />
    if (part.startsWith('$') && part.endsWith('$') && part.length > 2) return <MathFormula key={i} source={part.slice(1, -1)} display={false} />
    const src = /^\[\[src:([^|\]]+)\|([^|\]]+)\|([^\]]+)\]\]$/.exec(part)
    if (src) return <SourceChip key={i} id={src[1].trim()} name={src[2].trim()} loc={src[3].trim()} />
    const cite = /^\[\^?(\d+)\]$/.exec(part)
    if (cite) {
      return (
        <span
          key={i}
          title={t('Nguồn trích dẫn [{n}]', { n: cite[1] })}
          className="mx-0.5 inline-flex cursor-default items-center justify-center rounded bg-accent/15 px-1.5 py-px text-[10px] font-semibold text-accent align-super transition hover:bg-accent hover:text-accent-fg"
        >
          {cite[1]}
        </span>
      )
    }
    if (/^\*[^*\s][^*\n]*\*$/.test(part)) return <em key={i}>{inline(part.slice(1, -1))}</em>
    if (part.startsWith('`') && part.endsWith('`') && part.length > 2) return <code key={i} className="rounded bg-panel2 px-1 py-0.5 font-mono text-[12.5px]">{part.slice(1, -1)}</code>
    if (part.startsWith('**') && part.endsWith('**') && part.length > 4) return <strong key={i}>{inline(part.slice(2, -2))}</strong>
    const link = /^\[([^\]]+)\]\((https?:\/\/[^)\s]+)\)$/.exec(part)
    if (link) return <a key={i} href={link[2]} target="_blank" rel="noreferrer noopener" className="text-info underline underline-offset-2">{link[1]}</a>
    if (/^https?:\/\/\S+$/.test(part)) return <a key={i} href={part} target="_blank" rel="noreferrer noopener" className="break-all text-info underline underline-offset-2">{part}</a>
    return <Fragment key={i}>{part}</Fragment>
  })
}

const isRow = (l: string) => /^\s*\|.*\|\s*$/.test(l)
const isSeparator = (l: string) => isRow(l) && l.replace(/[|\s:-]/g, '') === '' && l.includes('-')
const cells = (l: string) => l.trim().replace(/^\|/, '').replace(/\|$/, '').split('|').map((c) => c.trim())

function Table({ head, rows, aligns }: { head: string[]; rows: string[][]; aligns: string[] }) {
  const al = (k: number) => (aligns[k] === 'center' ? 'text-center' : aligns[k] === 'right' ? 'text-right' : 'text-left')
  return (
    <div className="my-2 overflow-x-auto rounded-lg border border-line">
      <table className="w-full border-collapse text-[13px]">
        <thead className="bg-panel2"><tr>{head.map((h, k) => <th key={k} className={`border-b border-line px-3 py-2 font-semibold ${al(k)}`}>{inline(h)}</th>)}</tr></thead>
        <tbody>{rows.map((r, n) => <tr key={n} className="odd:bg-transparent even:bg-panel2/40">{head.map((_, k) => <td key={k} className={`border-b border-line/60 px-3 py-1.5 align-top ${al(k)}`}>{inline(r[k] ?? '')}</td>)}</tr>)}</tbody>
      </table>
    </div>
  )
}

/** Markdown with local math rendering; raw model HTML is never interpreted. */
export function Markdown({ text, article = false }: { text: string; article?: boolean }) {
  const blocks = text.split(/```(\w*)\n?([\s\S]*?)(?:```|$)/g)
  const out: ReactNode[] = []
  for (let i = 0; i < blocks.length; i += 3) {
    const prose = blocks[i]
    if (prose.trim()) {
      const lines = prose.replace(/(`[^`\n]+`)|(?<!\\)(\$\$[\s\S]*?\$\$|\\\[[\s\S]*?\\\])/g, (match, code: string | undefined) => code ? match : match.replace(/\n/g, ' ')).replace(/^\n+|\n+$/g, '').split('\n')
      let list: string[] = []
      let ordered = false
      const flush = (key: string) => {
        if (list.length) {
          const List = ordered ? 'ol' : 'ul'
          out.push(<List key={key} className={ordered ? 'my-2 list-decimal space-y-1 pl-5' : 'my-1.5 list-disc space-y-0.5 pl-5'}>
            {list.map((l, j) => <li key={j}>{inline(l)}</li>)}
          </List>)
        }
        list = []
      }
      for (let j = 0; j < lines.length; j++) {
        const line = lines[j]
        if (isRow(line) && j + 1 < lines.length && isSeparator(lines[j + 1])) {  // bang: dong tieu de, dong ngan cach |---|, cac dong du lieu
          flush(`ul${i}-${j}`)
          const head = cells(line)
          const aligns = cells(lines[j + 1]).map((c) => (c.startsWith(':') && c.endsWith(':') ? 'center' : c.endsWith(':') ? 'right' : 'left'))
          const rows: string[][] = []
          j += 2
          while (j < lines.length && isRow(lines[j])) rows.push(cells(lines[j++]))
          j--
          out.push(<Table key={`t${i}-${j}`} head={head} rows={rows} aligns={aligns} />)
          continue
        }
        const li = (article ? /^\s*(\d+\.|[-*])\s+(.*)$/ : /^\s*([-*])\s+(.*)$/).exec(line)
        if (li) {
          const nextOrdered = li[1].endsWith('.')
          if (list.length && nextOrdered !== ordered) flush(`list${i}-${j}`)
          ordered = nextOrdered
          list.push(li[2])
          continue
        }
        flush(`ul${i}-${j}`)
        const h = /^#{1,4}\s+(.*)$/.exec(line)
        const Heading = article ? 'h3' : 'p'
        out.push(h ? <Heading key={`${i}-${j}`} className={article ? 'mb-2 mt-5 text-base font-semibold first:mt-0' : 'mt-2 font-semibold'}>{inline(h[1])}</Heading> : line.trim() ? <p key={`${i}-${j}`}>{inline(line)}</p> : <div key={`${i}-${j}`} className="h-2" />)
      }
      flush(`ul${i}-end`)
    }
    if (i + 2 < blocks.length) out.push(<Code key={`c${i}`} lang={blocks[i + 1]} code={blocks[i + 2].replace(/\n$/, '')} />)
  }
  return <div className="space-y-0.5 break-words">{out}</div>
}
