import { useEffect, useRef, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Terminal } from '@xterm/xterm'
import { FitAddon } from '@xterm/addon-fit'
import { Unicode11Addon } from '@xterm/addon-unicode11'
import { WebglAddon } from '@xterm/addon-webgl'
import { WebLinksAddon } from '@xterm/addon-web-links'
import '@xterm/xterm/css/xterm.css'
import { Button } from '@/components/ui/Button'
import { api } from '@/lib/api'
import { t } from '@/lib/i18n.ts'

export function InteractiveTerminal({ sid }: { sid: string | null }) {
  const mount = useRef<HTMLDivElement>(null)
  const [connected, setConnected] = useState(false)
  const [running, setRunning] = useState(false)
  const status = useQuery({ queryKey: ['terminal-status'], queryFn: () => api.get<{ enabled: boolean }>('/api/terminal/status') })
  useEffect(() => {
    if (!running || !mount.current) return
    const node = mount.current
    const styles = getComputedStyle(document.documentElement)
    const terminal = new Terminal({
      cursorBlink: true,
      allowProposedApi: true,
      fontFamily: styles.getPropertyValue('--font-mono'),
      theme: { background: styles.getPropertyValue('--bg').trim(), foreground: styles.getPropertyValue('--fg').trim() },
    })
    const fit = new FitAddon()
    terminal.loadAddon(fit)
    terminal.loadAddon(new Unicode11Addon())
    terminal.unicode.activeVersion = '11'
    terminal.loadAddon(new WebLinksAddon())
    terminal.open(node)
    const webgl = new WebglAddon()
    try {
      terminal.loadAddon(webgl)
      webgl.onContextLoss(() => webgl.dispose())
    } catch { webgl.dispose() }
    const url = new URL('/api/terminal', window.location.href)
    url.protocol = location.protocol === 'https:' ? 'wss:' : 'ws:'
    if (sid) url.searchParams.set('session', sid)
    const socket = new WebSocket(url)
    socket.binaryType = 'arraybuffer'
    const resize = () => {
      fit.fit()
      if (socket.readyState === WebSocket.OPEN) socket.send(JSON.stringify({ rows: terminal.rows, cols: terminal.cols }))
    }
    const observer = new ResizeObserver(resize)
    observer.observe(node)
    socket.onopen = () => { setConnected(true); resize(); terminal.focus() }
    socket.onmessage = (event) => terminal.write(new Uint8Array(event.data))
    socket.onclose = () => { setConnected(false); terminal.writeln('\r\n' + t('Kết nối terminal đã đóng.')) }
    terminal.onData((data) => {
      if (socket.readyState === WebSocket.OPEN) socket.send(new TextEncoder().encode(data))
    })
    return () => {
      observer.disconnect()
      socket.onopen = socket.onmessage = socket.onclose = null
      socket.close()
      terminal.dispose()
      setConnected(false)
    }
  }, [running, sid])

  if (status.isPending) return <p className="p-3 text-sm text-muted">{t('Đang tải…')}</p>
  if (!status.data?.enabled) return <p className="p-3 text-sm text-muted">{t('Đặt mật khẩu Nestor và khởi động máy chủ với NESTOR_WEB_TERMINAL=1 để mở terminal.')}</p>
  return <div className="flex h-full min-h-60 flex-col bg-bg p-2">
    <div className="mb-2 flex gap-2">
      <Button size="sm" onClick={() => setRunning(!running)}>{running ? t('Đóng terminal') : t('Mở terminal')}</Button>
      {running && <span className="self-center text-xs text-muted">{connected ? t('Đã kết nối') : t('Chưa kết nối')}</span>}
    </div>
    <div ref={mount} className="min-h-0 flex-1 overflow-hidden" />
  </div>
}
