import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Download, ExternalLink, RefreshCw, ScanText } from 'lucide-react'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { Card, CardHeader } from '@/components/ui/Card'
import { ErrorNote, Loading } from '@/components/ui/misc'
import { api } from '@/lib/api'
import { t } from '@/lib/i18n.ts'
import { CopyButton } from './EmbeddingPanel'

type OcrStatus = {
  platform: 'windows' | 'linux' | 'macos' | 'other'
  installed: boolean
  ready: boolean
  languages: string[]
  can_install: boolean
  job: { phase: 'idle' | 'running' | 'done' | 'error'; step?: 'checking' | 'engine' | 'languages'; error: string }
}

const commands = {
  windows: 'winget install --id UB-Mannheim.TesseractOCR --exact --source winget',
  linux: 'sudo apt update && sudo apt install tesseract-ocr tesseract-ocr-vie tesseract-ocr-eng',
  macos: 'brew install tesseract tesseract-lang',
  other: '',
}

export function OcrPanel() {
  const qc = useQueryClient()
  const status = useQuery({
    queryKey: ['ocr-setup'],
    queryFn: () => api.get<OcrStatus>('/api/ocr/setup'),
    refetchInterval: (query) => query.state.data?.job.phase === 'running' ? 1200 : false,
  })
  const install = useMutation({
    mutationFn: () => api.post<OcrStatus>('/api/ocr/setup'),
    onSuccess: (data) => {
      qc.setQueryData(['ocr-setup'], data)
      void qc.invalidateQueries({ queryKey: ['ocr-setup'] })
    },
  })
  const data = status.data
  const running = data?.job.phase === 'running'
  const error = install.error ?? status.error ?? (data?.job.phase === 'error' ? new Error(data.job.error) : null)

  return (
    <Card>
      <CardHeader title={t('Nhận dạng chữ từ PDF scan')} hint={t('Tesseract chạy trên máy chủ Nestor. PDF mới được OCR ở những trang thiếu lớp chữ.')}
        action={data && <Button size="sm" disabled={running} loading={status.isFetching && !running} onClick={() => { install.reset(); void status.refetch() }}>
          <RefreshCw className="size-3.5" />{t('Kiểm tra lại')}
        </Button>} />
      <div className="space-y-5 p-5">
        {status.isLoading && <Loading />}
        {data && <>
          <div className="grid gap-3 sm:grid-cols-3">
            {([
              ['Tesseract', data.installed],
              [t('Tiếng Việt'), data.languages.includes('vie')],
              [t('Tiếng Anh'), data.languages.includes('eng')],
            ] as const).map(([label, exists]) => (
              <div key={label} className="flex min-w-0 items-center justify-between gap-2 rounded-lg border border-line bg-bg p-3">
                <span className="text-sm font-medium">{label}</span>
                <Badge tone={exists ? 'ok' : 'warn'}>{exists ? t('Đã cài') : t('Chưa cài')}</Badge>
              </div>
            ))}
          </div>
          <div className="flex flex-wrap items-center gap-3">
            {data.ready ? <span className="inline-flex items-center gap-2 text-sm text-ok"><ScanText className="size-4" />{t('OCR sẵn sàng')}</span> : (
              <Button variant="primary" disabled={!data.can_install} loading={install.isPending || running} onClick={() => install.mutate()}>
                <Download className="size-4" />{data.installed ? t('Tải bộ ngôn ngữ tự động') : t('Cài OCR tự động')}
              </Button>
            )}
            {running && <span role="status" className="text-sm text-muted">
              {data.job.step === 'languages' ? t('Đang tải dữ liệu ngôn ngữ…') : t('Đang cài đặt OCR…')}
            </span>}
            {!data.ready && !running && !data.can_install && <p className="text-sm text-muted">{t('Máy chủ chưa hỗ trợ cài tự động. Xem hướng dẫn bên dưới.')}</p>}
          </div>
          {!data.ready && data.platform === 'windows' && <p className="text-xs text-muted">{t('Cài tự động dùng WinGet và có thể cần xác nhận quyền quản trị trên máy chủ Windows.')}</p>}
          {!data.ready && data.platform === 'linux' && !data.installed && <p className="text-xs text-muted">{t('Cài tự động trên Debian hoặc Ubuntu cần quyền chạy apt trên máy chủ.')}</p>}
          <details className="rounded-lg border border-line bg-panel2/50 px-4 py-3" open={!data.ready && !data.can_install ? true : undefined}>
            <summary className="cursor-pointer text-sm font-medium">{t('Hướng dẫn cài thủ công')}</summary>
            <div className="mt-3 space-y-3 text-sm text-muted">
              <p>{t('Thực hiện trên máy chạy Nestor.')}</p>
              {commands[data.platform] && <div className="flex flex-wrap items-center gap-2">
                <code className="max-w-full break-words rounded bg-bg px-2 py-1 text-xs">{commands[data.platform]}</code>
                <CopyButton text={commands[data.platform]} />
              </div>}
              {data.platform === 'windows' && <p>{t('Trong trình cài Tesseract, bật thêm dữ liệu tiếng Việt và tiếng Anh. Nếu thiếu bộ ngôn ngữ, dùng nút tải trong Nestor sau khi cài Tesseract.')}</p>}
              <a href="https://tesseract-ocr.github.io/tessdoc/Installation.html" target="_blank" rel="noreferrer"
                className="inline-flex items-center gap-1 text-accent hover:underline">
                {t('Tài liệu cài Tesseract')}<ExternalLink className="size-3" />
              </a>
              <p>{t('Sau khi cài, bấm Kiểm tra lại. Với PDF đã tải lên, mở menu ba chấm của tệp và chọn Chạy OCR.')}</p>
            </div>
          </details>
        </>}
        {error && <ErrorNote error={error} />}
      </div>
    </Card>
  )
}
