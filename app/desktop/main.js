// Ứng dụng desktop Nestor Agent: mở một cửa sổ riêng, bên trong là giao diện web do server Nestor (đóng gói sẵn) phục vụ.
// Người dùng không cần biết server, cổng hay dòng lệnh: bấm mở là dùng được. Dữ liệu nằm ở thư mục dữ liệu của người dùng.
const { app, BrowserWindow, Menu, nativeTheme, shell } = require('electron')
const { spawn, execFileSync } = require('node:child_process')
const fs = require('node:fs')
const path = require('node:path')

const PREFERRED_PORT = 18787 // cố định để đăng nhập OAuth của MCP còn hiệu lực ở lần mở sau
const START_TIMEOUT_MS = 90_000
const vi = app.getLocale().toLowerCase().startsWith('vi')
const L = (a, b) => (vi ? a : b)

let win = null
let server = null
let origin = null
let quitting = false
let logStream = null

function log(msg) {
  try {
    if (!logStream) logStream = fs.createWriteStream(path.join(app.getPath('userData'), 'server.log'), { flags: 'a' })
    logStream.write(`[${new Date().toISOString()}] ${msg}\n`)
  } catch { /* không ghi được nhật ký thì bỏ qua */ }
}
process.on('uncaughtException', (e) => { log(`uncaughtException: ${e.stack || e}`); })
process.on('unhandledRejection', (e) => { log(`unhandledRejection: ${e && e.stack ? e.stack : e}`) })

function serverCommand() {
  const exe = process.platform === 'win32' ? 'nestor-server.exe' : 'nestor-server'
  const packed = path.join(process.resourcesPath, 'server', exe)
  if (fs.existsSync(packed)) return { cmd: packed, args: [], cwd: path.dirname(packed) }
  if (process.env.NESTOR_SERVER) return { cmd: process.env.NESTOR_SERVER, args: [], cwd: undefined }
  // chạy từ mã nguồn (npm start): dùng Python của repo
  const backend = path.resolve(__dirname, '..', 'backend')
  const py = process.env.NESTOR_PYTHON || path.resolve(__dirname, '..', '..', '.venv', 'bin', 'python')
  return { cmd: fs.existsSync(py) ? py : 'python3', args: ['-m', 'nestor.desktop_server'], cwd: backend }
}

function startServer() {
  const dataDir = process.env.NESTOR_HOME || path.join(app.getPath('userData'), 'data')
  fs.mkdirSync(dataDir, { recursive: true })
  const { cmd, args, cwd } = serverCommand()
  log(`starting server: ${cmd} ${args.join(' ')} (data: ${dataDir})`)
  server = spawn(cmd, [...args, '--port', String(PREFERRED_PORT)], {
    cwd, windowsHide: true, stdio: ['ignore', 'pipe', 'pipe'],
    env: { ...process.env, NESTOR_HOME: dataDir, PYTHONUTF8: '1', PYTHONUNBUFFERED: '1' },
  })
  server.stderr.on('data', (d) => logStream.write(d))
  return new Promise((resolve, reject) => {
    let buf = ''
    const timer = setTimeout(() => reject(new Error(L('Server khởi động quá lâu.', 'The server took too long to start.'))), START_TIMEOUT_MS)
    server.stdout.on('data', (d) => {
      logStream.write(d)
      buf += d.toString()
      const m = buf.match(/NESTOR_READY (\d+)/)
      if (m) { clearTimeout(timer); resolve(Number(m[1])) }
    })
    server.on('error', (e) => { clearTimeout(timer); reject(e) })
    server.on('exit', (code) => {
      clearTimeout(timer)
      if (!origin) reject(new Error(L(`Server dừng với mã ${code}.`, `The server exited with code ${code}.`)))
      else if (!quitting) onServerCrashed(code)
    })
  })
}

function stopServer() {
  if (!server || server.exitCode !== null) return
  try {
    if (process.platform === 'win32') execFileSync('taskkill', ['/pid', String(server.pid), '/T', '/F'], { stdio: 'ignore' })
    else { server.kill('SIGTERM'); setTimeout(() => { try { server.kill('SIGKILL') } catch { /* đã thoát */ } }, 3000).unref() }
  } catch { /* tiến trình đã thoát */ }
}

function exitApp(restart = false) {
  if (restart) app.relaunch()
  quitting = true
  app.quit()
}

function showServerError(title, detail, canRestart = false) {
  const window = win
  if (!window || window.isDestroyed()) { exitApp(); return }
  const screen = errorScreen(title, detail, canRestart)
  const onAction = (event, url) => {
    if (url !== 'nestor-action://quit/' && url !== 'nestor-action://restart/') return
    event.preventDefault()
    if (window.webContents.getURL() !== screen) return
    exitApp(canRestart && url === 'nestor-action://restart/')
  }
  window.webContents.on('will-navigate', onAction)
  void window.loadURL(screen).then(() => {
    if (!window.isDestroyed()) window.show()
  }).catch((error) => {
    log(`error screen failed: ${error.message}`)
    exitApp()
  })
}

function onServerCrashed(code) {
  showServerError(L('Nestor đã dừng đột ngột', 'Nestor stopped unexpectedly'), L(`Mã thoát: ${code}.`, `Exit code: ${code}.`), true)
}

const img = (name) => { try { return 'data:image/png;base64,' + fs.readFileSync(path.join(__dirname, 'assets', name)).toString('base64') } catch { return '' } }

// Màn hình chào hiện ngay khi mở app, trong lúc máy chủ nội bộ khởi động: logo lớn, tên và khẩu hiệu, theo giao diện sáng/tối của hệ điều hành.
const splash = (msg) => {
  const dark = nativeTheme.shouldUseDarkColors
  const bg = dark ? '#0c0c0e' : '#ffffff'
  const fg = dark ? '#eef0f6' : '#14213d'
  const muted = dark ? '#9a9aa5' : '#5b6475'
  const mark = img(dark ? 'nestor-mark.png' : 'nestor-mark-light.png')
  const word = img('nestor-wordmark.png')
  const slogan = 'Intelligence that works the way you do.'  // luôn bằng tiếng Anh
  return 'data:text/html;charset=utf-8,' + encodeURIComponent(`<!doctype html><meta charset="utf-8"><title>Nestor</title><style>
body{margin:0;height:100vh;display:grid;place-items:center;background:${bg};color:${muted};font:16px system-ui,sans-serif;overflow:hidden}
.c{display:flex;flex-direction:column;align-items:center;text-align:center;padding:0 24px}
.mark{height:min(30vh,150px)}
.word{display:block;height:min(8vh,38px);aspect-ratio:7.33/1;margin-top:22px;background:${fg};-webkit-mask:url(${word}) center/contain no-repeat;mask:url(${word}) center/contain no-repeat}
.s{margin:30px 0 0;max-width:460px;font-size:17px;line-height:1.5}
.bar{margin-top:38px;width:160px;height:2px;border-radius:2px;background:${dark ? '#1c1c22' : '#e5e8ee'};overflow:hidden}
.bar i{display:block;width:33%;height:100%;background:#2563eb;border-radius:2px;animation:s 1.2s ease-in-out infinite}
.m{margin-top:14px;font-size:12px;opacity:.8}
@keyframes s{from{transform:translateX(-100%)}to{transform:translateX(300%)}}
</style><div class="c"><img class="mark" src="${mark}" alt=""><span class="word"></span><p class="s">${slogan}</p><div class="bar"><i></i></div><div class="m">${msg}</div></div>`)
}

const escapeHtml = (value) => String(value).replace(/[&<>"]/g, (char) => ({
  '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;',
})[char])

function errorScreen(title, detail, canRestart) {
  const dark = nativeTheme.shouldUseDarkColors
  const mark = img(dark ? 'nestor-mark.png' : 'nestor-mark-light.png')
  const logPath = path.join(app.getPath('userData'), 'server.log')
  return 'data:text/html;charset=utf-8,' + encodeURIComponent(`<!doctype html>
<html lang="${L('vi', 'en')}"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; img-src data:">
<title>${escapeHtml(title)}</title><style>
:root{color-scheme:${dark ? 'dark' : 'light'};--bg:${dark ? '#0e0e10' : '#f5f7fb'};--panel:${dark ? '#17171b' : '#fff'};--fg:${dark ? '#eef0f6' : '#14213d'};--muted:${dark ? '#a7a7b2' : '#5b6475'};--line:${dark ? '#303038' : '#e0e4ed'}}
*{box-sizing:border-box}
body{margin:0;min-height:100vh;display:grid;place-items:center;padding:24px;background:var(--bg);color:var(--fg);font:15px/1.5 system-ui,sans-serif}
main{width:min(100%,520px);padding:28px;border:1px solid var(--line);border-radius:18px;background:var(--panel);box-shadow:0 14px 44px #0002}
img{width:42px;height:42px;object-fit:contain}
h1{margin:12px 0 8px;font-size:22px;line-height:1.3}
p{margin:0;color:var(--muted);overflow-wrap:anywhere;white-space:pre-wrap}
.log{margin-top:16px;padding:12px;border-radius:9px;background:var(--bg)}
code{display:block;overflow-wrap:anywhere}
.actions{display:flex;flex-wrap:wrap;justify-content:flex-end;gap:8px;margin-top:24px}
a{display:inline-block;padding:8px 14px;border:1px solid var(--line);border-radius:8px;color:var(--fg);text-decoration:none;font-weight:600}
.primary{background:#2563eb;border-color:#2563eb;color:white}
a:hover{filter:brightness(1.15)}
a:focus-visible{outline:2px solid #60a5fa;outline-offset:2px}
</style><main><img src="${mark}" alt="Nestor"><h1>${escapeHtml(title)}</h1><p>${escapeHtml(detail)}</p>
<div class="log"><p>${L('Nhật ký', 'Log')}</p><code>${escapeHtml(logPath)}</code></div>
<div class="actions"><a href="nestor-action://quit/">${L('Thoát', 'Quit')}</a>
${canRestart ? `<a class="primary" href="nestor-action://restart/">${L('Khởi động lại', 'Restart')}</a>` : ''}</div></main></html>`)
}

function createWindow() {
  win = new BrowserWindow({
    width: 1360, height: 880, minWidth: 900, minHeight: 600, show: false, backgroundColor: nativeTheme.shouldUseDarkColors ? '#0c0c0e' : '#ffffff', title: 'Nestor Agent',
    icon: path.join(__dirname, 'assets', 'icon.png'), autoHideMenuBar: true,
    webPreferences: { contextIsolation: true, sandbox: true, nodeIntegration: false },
  })
  win.once('ready-to-show', () => win.show())
  win.on('closed', () => { win = null })
  // liên kết ra ngoài mở bằng trình duyệt hệ thống, không mở trong cửa sổ app
  win.webContents.setWindowOpenHandler(({ url }) => { if (/^https?:/i.test(url)) shell.openExternal(url); return { action: 'deny' } })
  win.webContents.on('will-navigate', (e, url) => { if (origin && !url.startsWith(origin)) { e.preventDefault(); if (/^https?:/i.test(url)) shell.openExternal(url) } })
  void win.loadURL(splash(L('Đang khởi động Nestor…', 'Starting Nestor…')))
}

function buildMenu() {
  Menu.setApplicationMenu(Menu.buildFromTemplate([
    ...(process.platform === 'darwin' ? [{ role: 'appMenu' }] : []),
    { role: 'editMenu' },
    { label: L('Xem', 'View'), submenu: [{ role: 'reload' }, { role: 'togglefullscreen' }, { type: 'separator' }, { role: 'resetZoom' }, { role: 'zoomIn' }, { role: 'zoomOut' }] },
    { label: L('Trợ giúp', 'Help'), submenu: [
      { label: L('Mở thư mục dữ liệu', 'Open data folder'), click: () => shell.openPath(app.getPath('userData')) },
      { label: L('Xem nhật ký', 'View log'), click: () => shell.openPath(path.join(app.getPath('userData'), 'server.log')) },
      { type: 'separator' },
      { role: 'quit' },
    ] },
  ]))
}

if (!app.requestSingleInstanceLock()) {
  app.quit()
} else {
  app.on('second-instance', () => { if (win) { if (win.isMinimized()) win.restore(); win.focus() } })
  app.whenReady().then(async () => {
    log('app ready')
    buildMenu()
    createWindow()
    log('window created')
    try {
      const port = await startServer()
      origin = `http://127.0.0.1:${port}`
      log(`server ready on ${origin}`)
      if (win) await win.loadURL(origin)
    } catch (e) {
      log(`start failed: ${e.stack || e}`)
      stopServer()
      showServerError(L('Không khởi động được Nestor', 'Nestor could not start'), e.message)
    }
  })
  app.on('window-all-closed', () => app.quit())
  app.on('before-quit', () => { quitting = true; stopServer() })
}
