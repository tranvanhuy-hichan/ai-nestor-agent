import { useSyncExternalStore } from 'react'
import { tk } from '@/lib/i18n.ts'

export const themes = {
  dark: tk('Tối'), light: tk('Sáng'), cyberpunk: 'Cyberpunk', synthwave: 'Synthwave',
  monokai: 'Monokai', nord: 'Nord', dracula: 'Dracula', hacker: 'Hacker Green',
}
export const fonts = {
  system: tk('Hệ thống'), fira: 'Fira Code', jetbrains: 'JetBrains Mono',
}
export type Theme = keyof typeof themes
export type Font = keyof typeof fonts

const event = 'nestor-appearance'
const sessionValues = new Map<string, string>()
const read = (key: string, fallback: string) => {
  try { return sessionValues.get(key) ?? localStorage.getItem(key) ?? fallback }
  catch { return fallback }
}
const theme = (): Theme => {
  const value = read('theme', 'dark')
  return Object.hasOwn(themes, value) ? value as Theme : 'dark'
}
const font = (): Font => {
  const value = read('mono-font', 'system')
  return Object.hasOwn(fonts, value) ? value as Font : 'system'
}
const ligatures = () => read('mono-ligatures', '1') === '1'
const listen = (fn: () => void) => {
  window.addEventListener(event, fn)
  window.addEventListener('storage', fn)
  return () => { window.removeEventListener(event, fn); window.removeEventListener('storage', fn) }
}

const write = (key: string, value: string) => {
  try {
    localStorage.setItem(key, value)
    sessionValues.delete(key)
  } catch {
    sessionValues.set(key, value)
  }
  window.dispatchEvent(new Event(event))
}
export const setTheme = (value: Theme) => write('theme', value)
export const setFont = (value: Font) => write('mono-font', value)
export const setLigatures = (value: boolean) => write('mono-ligatures', value ? '1' : '0')

export function installAppearance() {
  const apply = () => {
    const root = document.documentElement
    const current = theme()
    root.classList.toggle('light', current === 'light')
    root.dataset.theme = current
    root.dataset.mono = font()
    root.dataset.ligatures = ligatures() ? 'on' : 'off'
  }
  apply()
  return listen(apply)
}

export function useAppearance() {
  return {
    theme: useSyncExternalStore(listen, theme),
    font: useSyncExternalStore(listen, font),
    ligatures: useSyncExternalStore(listen, ligatures),
  }
}
