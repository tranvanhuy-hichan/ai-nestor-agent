/** Identify Nestor tabs when Chromium exposes the Capture Handle API. */
type CaptureTrack = MediaStreamTrack & { getCaptureHandle?: () => { handle?: string; origin?: string } | null }
type CaptureDevices = MediaDevices & { setCaptureHandleConfig?: (config: { handle: string; exposeOrigin: boolean; permittedOrigins: string[] }) => void }
export function exposeCaptureHandle(handle: string) {
  try {
    const devices = navigator.mediaDevices as CaptureDevices
    if (!devices?.setCaptureHandleConfig) return false
    devices.setCaptureHandleConfig({ handle, exposeOrigin: true, permittedOrigins: [location.origin] })
    return true
  } catch { return false }
}
export function captureSourceError(stream: MediaStream, currentTab: boolean, handle: string, exposed: boolean): string | null {
  const track = stream.getVideoTracks()[0] as CaptureTrack | undefined
  const surface = track?.getSettings().displaySurface
  if (surface && surface !== 'browser') return 'Hãy chỉ chia sẻ một tab trình duyệt, không chọn cửa sổ hoặc toàn màn hình vì có thể thu lẫn giọng dịch.'
  if (track?.label.includes('Giọng dịch Nestor')) return 'Không chia sẻ cửa sổ giọng dịch. Hãy chọn tab đang phát video.'
  if (track?.getCaptureHandle && exposed) {
    let captured: ReturnType<NonNullable<CaptureTrack['getCaptureHandle']>>
    try { captured = track.getCaptureHandle() } catch { return 'Không xác định được nguồn thu. Hãy chia sẻ lại đúng tab video.' }
    if (currentTab && captured?.handle !== handle) return 'Bạn chưa chọn đúng tab video Nestor này. Hãy chọn lại tab đang phát video, không chọn cửa sổ Giọng dịch Nestor.'
    if (!currentTab && captured?.origin === location.origin) return 'Bạn đã chọn một tab Nestor. Ở chế độ Tab riêng, hãy chọn đúng tab YouTube để không thu lại giọng dịch.'
  }
  return null
}
