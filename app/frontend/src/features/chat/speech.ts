export function speechText(text: string, vi: boolean) {
  // Formula notation is visual; avoid pronouncing raw TeX commands as English words.
  const math = vi ? ' công thức toán trên màn hình ' : ' mathematical expression on screen '
  return text.replace(/```[\s\S]*?(?:```|$)/g, ' ')
    .replace(/`[^`]*`/g, ' ')
    .replace(/\[image:[^\]]*\]|\[\[src:[^\]]*\]\]|\[\^?\d+\]/g, ' ')
    .replace(/\$\$[\s\S]*?\$\$|\\\[[\s\S]*?\\\]|\\\([\s\S]*?\\\)|(?<![\\$])\$(?![\s$])[^$\n]+\$(?!\d)/g, math)
    .replace(/\[([^\]]+)\]\([^)]*\)/g, '$1')
    .replace(/https?:\/\/\S+/g, ' ')
    // Keep natural pauses between headings, paragraphs and list items.
    .replace(/^\s*[-*]\s+/gm, '')
    .replace(/[*_`#>|]/g, ' ')
    .replace(/([^.!?;:\s])[^\S\n]*\n+/g, '$1. ')
    .replace(/\n+/g, ' ')
    .replace(/\s+/g, ' ').trim()
}

/** Short segments start playing promptly and keep long answers within the API limit. */
export function speechSegments(text: string): string[] {
  const segments: string[] = []
  let rest = text.trim()
  while (rest.length > 450) {
    const head = rest.slice(0, 450)
    const sentence = [...head.matchAll(/[.!?;]\s/g)].at(-1)?.index
    const cut = sentence !== undefined && sentence > 150 ? sentence + 1 : head.lastIndexOf(' ') > 0 ? head.lastIndexOf(' ') : 450
    segments.push(rest.slice(0, cut)); rest = rest.slice(cut).trimStart()
  }
  if (rest) segments.push(rest)
  return segments
}
