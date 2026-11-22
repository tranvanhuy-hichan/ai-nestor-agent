// Ignore layout whitespace and discretionary hyphens inserted during PDF extraction.
function normalize(char: string) {
  return char.normalize('NFKD').toLowerCase().replace(/[\s\p{M}\u00ad\u200b-]/gu, '')
}

export function sourceRanges(parts: string[], quotes: string[]) {
  if (!quotes.some(Boolean)) return []
  const original = parts.join('')
  const offsets: number[] = []
  let text = ''
  let offset = 0
  for (const part of parts) {
    for (const char of part) {
      const token = normalize(char)
      text += token
      for (let i = 0; i < token.length; i++) offsets.push(offset)
      offset += char.length
    }
  }
  return quotes.flatMap((quote, quoteIndex) => {
    let needle = Array.from(quote, normalize).join('')
    let start = text.indexOf(needle)
    // PDF engines sometimes disagree at a line break. Match a substantial beginning
    // and ending only when both occur close together in the same source.
    if (start < 0 && needle.length >= 100) {
      const prefix = needle.slice(0, 45)
      const suffix = needle.slice(-45)
      start = text.indexOf(prefix)
      const end = start < 0 ? -1 : text.indexOf(suffix, start + prefix.length)
      if (end >= 0 && Math.abs(end + suffix.length - start - needle.length) <= 30) {
        needle = text.slice(start, end + suffix.length)
      } else start = -1
    }
    if (!needle || start < 0) return []
    const last = offsets[start + needle.length - 1]
    return [{ quoteIndex, start: offsets[start], end: last + ((original.codePointAt(last) ?? 0) > 0xffff ? 2 : 1) }]
  }).sort((a, b) => a.start - b.start)
}
