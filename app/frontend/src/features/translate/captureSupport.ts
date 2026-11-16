/** Display capture existing does not imply that the browser can share tab audio. */
export function captureSupportReason(): string | null {
  if (/Firefox\/|FxiOS\//i.test(navigator.userAgent)) return 'Firefox hiện chưa hỗ trợ chia sẻ âm thanh tab cho chức năng này. Hãy mở cả Nestor và YouTube bằng Chrome hoặc Edge trên máy tính.'
  if (!navigator.mediaDevices?.getDisplayMedia || typeof MediaRecorder === 'undefined') return 'Trình duyệt chưa hỗ trợ thu âm tab. Hãy mở cả Nestor và YouTube bằng Chrome hoặc Edge trên máy tính.'
  return null
}
