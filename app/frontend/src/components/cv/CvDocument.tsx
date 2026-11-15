import { cvTemplate } from './templates'
import { LangCtx } from './lang'
import { LevelsCtx } from './levels'
import type { CvData } from '@/lib/cv/types'

/** Shared by the template picker and the PDF renderer: the exact same store layouts. */
export function CvDocument({ template, data, lang = 'vi' }: { template: string; data: CvData; lang?: 'vi' | 'en' }) {
  const { Component, accent, photo } = cvTemplate(template)
  return <LangCtx.Provider value={lang}><LevelsCtx.Provider value={false}>
    <div className="cv-document" style={{ width: 794, minHeight: 1123, background: '#fff', fontFamily: 'Arial, sans-serif', fontSize: 13, color: '#1f2937', whiteSpace: 'pre-line' }}>
      <Component data={data} accent={accent} showPhoto={photo && !!data.photo} />
    </div>
  </LevelsCtx.Provider></LangCtx.Provider>
}
