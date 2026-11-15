import { renderToStaticMarkup } from 'react-dom/server'
import { CvDocument } from '@/components/cv/CvDocument'
import { CV_TEMPLATES } from '@/components/cv/templates'
import { emptyCv, type CvData } from './types'

export type CvInput = { key: string; label: string; hint?: string; multiline?: boolean }
export type CvSection = { key: string; label: string; fields?: CvInput[]; hint?: string }
export const CONTACT_FIELDS: CvInput[] = [
  { key: 'name', label: 'Họ và tên' }, { key: 'title', label: 'Vị trí / chức danh ứng tuyển' },
  { key: 'email', label: 'Email' }, { key: 'phone', label: 'Số điện thoại' },
  { key: 'address', label: 'Địa chỉ', hint: 'Chỉ cần tỉnh / thành phố' }, { key: 'website', label: 'Website / LinkedIn / Portfolio' },
]
export const CV_SECTIONS: CvSection[] = [
  { key: 'summary', label: 'Giới thiệu bản thân', hint: 'Viết vài ý về thế mạnh, định hướng. Có thể để AI viết từ các mục bên dưới.' },
  { key: 'experience', label: 'Kinh nghiệm làm việc', fields: [{ key: 'role', label: 'Chức danh' }, { key: 'company', label: 'Công ty / tổ chức' }, { key: 'from', label: 'Từ tháng/năm' }, { key: 'to', label: 'Đến tháng/năm' }, { key: 'desc', label: 'Công việc và kết quả', multiline: true, hint: 'Bạn thực sự làm gì? Dùng công cụ nào? Kết quả hoặc quy mô nếu biết. AI sẽ biên tập thành gạch đầu dòng.' }] },
  { key: 'education', label: 'Học vấn', fields: [{ key: 'school', label: 'Trường học' }, { key: 'degree', label: 'Ngành học / bằng cấp' }, { key: 'from', label: 'Từ năm' }, { key: 'to', label: 'Đến năm' }, { key: 'desc', label: 'Thông tin học tập', multiline: true, hint: 'GPA, đồ án, học bổng nếu có' }] },
  { key: 'skills', label: 'Kỹ năng', fields: [{ key: 'name', label: 'Kỹ năng / công cụ', hint: 'Chỉ ghi kỹ năng bạn có thể trao đổi trong phỏng vấn' }] },
  { key: 'languages', label: 'Ngoại ngữ', fields: [{ key: 'name', label: 'Ngôn ngữ' }, { key: 'level', label: 'Trình độ / chứng chỉ', hint: 'Ghi mức thực tế, không bắt buộc có chứng chỉ' }] },
  { key: 'projects', label: 'Dự án', fields: [{ key: 'name', label: 'Tên dự án' }, { key: 'desc', label: 'Vai trò, công nghệ và kết quả', multiline: true, hint: 'Bạn đóng góp phần nào? Có sản phẩm hoặc kết quả gì?' }] },
  { key: 'awards', label: 'Thành tích và chứng chỉ', hint: 'Mỗi dòng một mục: tên, đơn vị cấp, năm. Không có thì chọn bỏ qua.' },
  { key: 'highlights', label: 'Số liệu nổi bật', fields: [{ key: 'value', label: 'Con số thực tế', hint: 'Ví dụ: 3 dự án học tập, 2 năm kinh nghiệm. Không tự ước lượng.' }, { key: 'label', label: 'Ý nghĩa con số' }] },
  { key: 'interests', label: 'Sở thích', hint: 'Mỗi dòng một sở thích phù hợp, không bắt buộc' },
]
const marker = (key: string) => `CVINPUT_${key.toUpperCase()}_END`
const cache = new Map<string, { contact: CvInput[]; sections: CvSection[]; photo: boolean }>()

/** Discover fields from the actual template output, including parametric store layouts. */
export function schemaForTemplate(template: string) {
  const cached = cache.get(template)
  if (cached) return cached
  const def = CV_TEMPLATES.find((x) => x.id === template)
  if (!def) return { contact: [], sections: [], photo: false }
  const probe = emptyCv() as unknown as Record<string, unknown>
  for (const f of CONTACT_FIELDS) probe[f.key] = marker(f.key)
  for (const s of CV_SECTIONS) probe[s.key] = s.fields ? [{ id: s.key, ...Object.fromEntries(s.fields.map((f) => [f.key, marker(s.key + '_' + f.key)])) }] : marker(s.key)
  probe.website = 'https://cvinput_website_end.example.com'
  probe.photo = 'data:image/png;base64,Q1ZJTlBVVF9QSE9UTw=='
  const html = renderToStaticMarkup(<CvDocument template={template} data={probe as unknown as CvData} />).toLowerCase()
  const sections = CV_SECTIONS.map((s) => ({ ...s, fields: s.fields?.filter((f) => html.includes(marker(s.key + '_' + f.key).toLowerCase())) })).filter((s) => s.fields ? s.fields.length > 0 : html.includes(marker(s.key).toLowerCase()))
  const schema = { contact: CONTACT_FIELDS.filter((f) => html.includes(marker(f.key).toLowerCase())), sections, photo: def.photo && html.includes('q1zjtlbvvf9qse9utw==') }
  cache.set(template, schema)
  return schema
}
