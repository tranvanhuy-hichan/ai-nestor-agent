import { Download, ExternalLink, FileText, FileSpreadsheet, Presentation } from 'lucide-react'
import type { FileEntry } from '@/lib/types'
import { t } from '@/lib/i18n.ts'

export function ResultFiles({ sid, files }: { sid: string | null; files: FileEntry[] }) {
  if (!sid || !files.length) return null
  return <div className="max-h-40 space-y-2 overflow-y-auto pr-1">{files.map((f) => {
    const name = f.path.split('/').pop() ?? f.path
    const ext = name.split('.').pop()?.toLowerCase() ?? ''
    const Icon = ext === 'xlsx' ? FileSpreadsheet : ext === 'pptx' ? Presentation : FileText
    const size = f.size < 1024 ? `${f.size} B` : f.size < 1048576 ? `${(f.size/1024).toFixed(1)} KB` : `${(f.size/1048576).toFixed(1)} MB`
    const url = `/api/sessions/${sid}/file?path=${encodeURIComponent(f.path)}&raw=true`
    return <div key={f.path} className="flex min-w-0 items-center gap-3 rounded-lg border border-line bg-bg p-2">
      <span className="grid size-8 shrink-0 place-items-center rounded-lg bg-accent/10 text-accent"><Icon className="size-4" /></span>
      <div className="min-w-0 flex-1"><p className="break-words text-xs font-medium" title={name}>{name}</p><p className="mt-1 text-[10px] uppercase tracking-wide text-muted">{ext} · {size}</p></div>
      <a href={url} target="_blank" rel="noopener noreferrer" aria-label={`${t('Mở file')}: ${name}`} title={t('Mở file')} className="rounded-md border border-line p-2 text-muted hover:text-accent"><ExternalLink className="size-3.5" /></a>
      <a href={url} download={name} aria-label={`${t('Tải về')}: ${name}`} title={t('Tải về')} className="rounded-md bg-accent/10 p-2 text-accent hover:bg-accent/20"><Download className="size-3.5" /></a>
    </div>
  })}</div>
}
