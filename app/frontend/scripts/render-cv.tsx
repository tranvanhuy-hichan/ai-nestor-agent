import { readFileSync } from 'node:fs'
import { renderToStaticMarkup } from 'react-dom/server'
import { CvDocument } from '../src/components/cv/CvDocument'
import { normalizeCv } from '../src/lib/cv/types'
import { schemaForTemplate } from '../src/lib/cv/templateSchema'
import { CV_TEMPLATES } from '../src/components/cv/templates'

const input = JSON.parse(readFileSync(0, 'utf8'))
if (process.argv.includes('--schema')) {
  process.stdout.write(JSON.stringify(Object.fromEntries(CV_TEMPLATES.map((t) => [t.id, schemaForTemplate(t.id)]))))
} else {
if (!CV_TEMPLATES.some((t) => t.id === input.template)) throw new Error('Mẫu CV không tồn tại')
const data = normalizeCv(input.data)
if (!data.name.trim()) throw new Error('CV cần họ tên thật của người dùng')
const html = renderToStaticMarkup(<CvDocument template={input.template} data={data} lang={input.lang === 'en' ? 'en' : 'vi'} />)
process.stdout.write(`<!doctype html><html lang="${input.lang === 'en' ? 'en' : 'vi'}"><head><meta charset="utf-8"><title>CV</title><meta name="viewport" content="width=device-width, initial-scale=1"><style>
@page {size:A4;margin:0} *{box-sizing:border-box} html,body{margin:0;padding:0;background:white} body{width:794px} .cv-document{overflow-wrap:anywhere} .cv-document>div{min-height:1123px} a{color:inherit} section{break-inside:auto} li{break-inside:avoid} svg{display:inline-block;vertical-align:middle} @media print{*{-webkit-print-color-adjust:exact;print-color-adjust:exact}}
</style></head><body>${html}</body></html>`)

}
