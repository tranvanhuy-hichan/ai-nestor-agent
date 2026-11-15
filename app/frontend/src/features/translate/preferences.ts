export const TRANSLATE_PREFS_KEY = 'youtube-translate:preferences:v1'
const LANGUAGES = new Set(['vi', 'en', 'ja', 'ko', 'zh-CN', 'fr', 'de', 'es'])
export type TranslatePreferences = { url: string; source: string; targets: string[]; translator: string; voice: string; download: string; follow: boolean; settingsOpen: boolean; showOriginal: boolean; playback: 'embedded' | 'external'; wide: boolean }
const defaults: TranslatePreferences = { url: '', source: 'auto', targets: ['vi', 'en'], translator: '', voice: 'vi', download: 'vi', follow: true, settingsOpen: false, showOriginal: true, playback: 'embedded', wide: false }
export function loadTranslatePreferences(): TranslatePreferences {
  try {
    const p = JSON.parse(localStorage.getItem(TRANSLATE_PREFS_KEY) || 'null')
    if (!p || typeof p !== 'object' || Array.isArray(p)) return { ...defaults }
    const targets = Array.isArray(p.targets) ? [...new Set<string>(p.targets.filter((v: unknown) => typeof v === 'string' && LANGUAGES.has(v)))].slice(0, 4) : [...defaults.targets]
    return {
      url: typeof p.url === 'string' && p.url.length <= 2048 ? p.url : '',
      source: p.source === 'auto' || LANGUAGES.has(p.source) ? p.source : 'auto',
      targets,
      translator: typeof p.translator === 'string' && p.translator.length <= 128 ? p.translator : '',
      voice: typeof p.voice === 'string' && targets.includes(p.voice) ? p.voice : '',
      download: p.download === 'original' || LANGUAGES.has(p.download) ? p.download : 'vi',
      follow: typeof p.follow === 'boolean' ? p.follow : true,
      wide: typeof p.wide === 'boolean' ? p.wide : false,
      playback: p.playback === 'external' ? 'external' : 'embedded',
      showOriginal: typeof p.showOriginal === 'boolean' ? p.showOriginal : true,
      settingsOpen: typeof p.settingsOpen === 'boolean' ? p.settingsOpen : false,
    }
  } catch { return { ...defaults } }
}
