/** Chế độ giao diện: 'simple' (người dùng phổ thông, mặc định) hoặc 'advanced' (đầy đủ cho lập trình viên). Lưu ở localStorage. */
import { useSyncExternalStore } from 'react'

export type UiMode = 'simple' | 'advanced'
const KEY = 'ui-mode'

function load(): UiMode {
  try { return localStorage.getItem(KEY) === 'advanced' ? 'advanced' : 'simple' } catch { return 'simple' }
}

let mode: UiMode = load()
const listeners = new Set<() => void>()

export const getUiMode = () => mode

export function setUiMode(next: UiMode) {
  if (next === mode) return
  mode = next
  try { localStorage.setItem(KEY, next) } catch { /* chế độ riêng tư */ }
  listeners.forEach((fn) => fn())
}

export function useUiMode(): UiMode {
  return useSyncExternalStore((fn) => { listeners.add(fn); return () => { listeners.delete(fn) } }, getUiMode)
}
