import type { CvLang } from './i18n';

/** CV document model, defaults and the sample CV used by the gallery and the first editor session. */

export interface CvExperience { id: string; role: string; company: string; from: string; to: string; desc: string }
export interface CvEducation { id: string; school: string; degree: string; from: string; to: string; desc: string }
export interface CvSkill { id: string; name: string; level: number }
export interface CvLanguage { id: string; name: string; level: string }
export interface CvLink { id: string; label: string; url: string }
export interface CvProject { id: string; name: string; desc: string; /** GitHub, product, demo... */ links?: CvLink[] }

export interface CvHighlight { id: string; value: string; label: string }

export interface CvData {
  name: string;
  title: string;
  email: string;
  phone: string;
  address: string;
  website: string;
  /** data: URL of a small square-ish JPEG, or '' */
  photo: string;
  summary: string;
  experience: CvExperience[];
  education: CvEducation[];
  skills: CvSkill[];
  languages: CvLanguage[];
  projects: CvProject[];
  /** one achievement / certificate per line */
  awards: string;
  /** headline numbers, e.g. "62%" / "tăng doanh thu" (shown by infographic-style templates) */
  highlights: CvHighlight[];
  /** one interest per line */
  interests: string;
}

export interface CvStyle {
  template: string;
  accent: string;
  font: string;
  /** text scale 0.85..1.15 */
  size: number;
  /** hide the photo even when one is uploaded */
  showPhoto: boolean;
  /** draw skill bars / dots / rings (off by default: self-rated scores are rarely trusted by recruiters) */
  showLevels?: boolean;
  /** language of the section headings; the text itself is whatever the user types */
  lang?: CvLang;
}

export const A4_W = 794;
export const A4_H = 1123;

export const ACCENTS = ['#0ea5e9', '#2563eb', '#4f46e5', '#7c3aed', '#db2777', '#e11d48', '#ea580c', '#d97706', '#059669', '#0d9488', '#334155', '#111827'];

let n = 0;
export const cvId = () => `i${Date.now().toString(36)}${(n++).toString(36)}`;

export const emptyCv = (): CvData => ({
  name: '', title: '', email: '', phone: '', address: '', website: '', photo: '', summary: '',
  experience: [], education: [], skills: [], languages: [], projects: [], awards: '', highlights: [], interests: '',
});

export const DEFAULT_STYLE: CvStyle = { template: 'modern', accent: '#0ea5e9', font: 'be-vietnam', size: 1, showPhoto: true, showLevels: false };

/** Neutral avatar shown in the gallery and the starter CV until a real photo is uploaded. */
export const SAMPLE_PHOTO = 'data:image/svg+xml;utf8,' + encodeURIComponent(
  '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200"><defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#cbd5e1"/><stop offset="1" stop-color="#94a3b8"/></linearGradient></defs><rect width="200" height="200" fill="url(#g)"/><circle cx="100" cy="78" r="36" fill="#f8fafc"/><path d="M30 200c0-44 30-72 70-72s70 28 70 72z" fill="#f8fafc"/></svg>',
);

export const SAMPLE_CV: CvData = {
  name: 'Nguyễn Minh Anh',
  title: 'Lập trình viên Frontend',
  email: 'minhanh@email.com',
  phone: '0901 234 567',
  address: 'Quận 1, TP. Hồ Chí Minh',
  website: 'linkedin.com/in/minhanh',
  photo: SAMPLE_PHOTO,
  summary: 'Hơn 4 năm xây dựng ứng dụng web cho thương mại điện tử và fintech. Quen làm việc theo Agile, ưu tiên trải nghiệm người dùng, hiệu năng và code dễ bảo trì. Đang tìm vị trí Senior Frontend để dẫn dắt nhóm nhỏ.',
  experience: [
    { id: 'e1', role: 'Frontend Developer', company: 'Công ty Cổ phần Sàn Việt', from: '03/2022', to: 'Hiện tại', desc: 'Xây dựng lại trang thanh toán bằng React và Next.js, giảm 35% thời gian tải trang.\nDẫn dắt nhóm 3 người, review code và hướng dẫn thành viên mới.\nTích hợp cổng thanh toán, tăng 12% tỉ lệ hoàn tất đơn hàng.' },
    { id: 'e2', role: 'Web Developer', company: 'Studio Hạ Long', from: '07/2020', to: '02/2022', desc: 'Phát triển hơn 20 website doanh nghiệp bằng JavaScript và WordPress.\nChuẩn hoá thư viện giao diện dùng chung cho 5 dự án.' },
  ],
  education: [
    { id: 'd1', school: 'Đại học Bách khoa TP.HCM', degree: 'Kỹ sư Công nghệ thông tin', from: '2016', to: '2020', desc: 'GPA 3.4/4.0, học bổng khuyến khích học tập 3 học kỳ.' },
  ],
  skills: [
    { id: 's1', name: 'React / Next.js', level: 5 }, { id: 's2', name: 'TypeScript', level: 5 }, { id: 's3', name: 'HTML / CSS', level: 5 },
    { id: 's4', name: 'Node.js', level: 4 }, { id: 's5', name: 'Figma', level: 3 }, { id: 's6', name: 'Git / CI-CD', level: 4 },
  ],
  languages: [{ id: 'l1', name: 'Tiếng Anh', level: 'IELTS 7.0' }, { id: 'l2', name: 'Tiếng Nhật', level: 'N4' }],
  projects: [
    { id: 'p1', name: 'Hệ thống quản lý bán hàng', desc: 'Ứng dụng web cho 40 cửa hàng, hơn 10.000 đơn mỗi tháng.' },
  ],
  awards: 'Nhân viên xuất sắc năm 2023\nChứng chỉ AWS Cloud Practitioner',
  highlights: [{ id: 'h1', value: '4+', label: 'năm kinh nghiệm' }, { id: 'h2', value: '20+', label: 'dự án triển khai' }, { id: 'h3', value: '-35%', label: 'thời gian tải trang' }],
  interests: 'Mã nguồn mở\nCờ vua\nChạy bộ',
};

const str = (v: unknown, max: number) => (typeof v === 'string' ? v.slice(0, max) : '');
const arr = <T,>(v: unknown, max: number, f: (x: Record<string, unknown>) => T): T[] =>
  Array.isArray(v) ? v.slice(0, max).filter((x) => x && typeof x === 'object').map((x) => f(x as Record<string, unknown>)) : [];

/** Any stored / imported JSON -> a complete CvData (bad fields dropped, text capped). */
export function normalizeCv(raw: unknown): CvData {
  const r = raw && typeof raw === 'object' ? (raw as Record<string, unknown>) : {};
  const photo = typeof r.photo === 'string' && /^data:image\/(jpeg|png|webp);base64,/.test(r.photo) && r.photo.length < 400_000 ? r.photo : '';
  return {
    name: str(r.name, 80), title: str(r.title, 100), email: str(r.email, 100), phone: str(r.phone, 30), address: str(r.address, 140), website: str(r.website, 140),
    photo, summary: str(r.summary, 1200),
    experience: arr(r.experience, 12, (x) => ({ id: str(x.id, 20) || cvId(), role: str(x.role, 100), company: str(x.company, 100), from: str(x.from, 20), to: str(x.to, 20), desc: str(x.desc, 1200) })),
    education: arr(r.education, 8, (x) => ({ id: str(x.id, 20) || cvId(), school: str(x.school, 120), degree: str(x.degree, 120), from: str(x.from, 20), to: str(x.to, 20), desc: str(x.desc, 600), links: arr(x.links, 5, (l) => ({ id: str(l.id, 20) || cvId(), label: str(l.label, 30), url: safeUrl(l.url) })).filter((l) => l.url) })),
    skills: arr(r.skills, 20, (x) => ({ id: str(x.id, 20) || cvId(), name: str(x.name, 60), level: Math.min(5, Math.max(1, Math.round(Number(x.level)) || 3)) })),
    languages: arr(r.languages, 8, (x) => ({ id: str(x.id, 20) || cvId(), name: str(x.name, 40), level: str(x.level, 40) })),
    projects: arr(r.projects, 8, (x) => ({ id: str(x.id, 20) || cvId(), name: str(x.name, 100), desc: str(x.desc, 600), links: arr(x.links, 5, (l) => ({ id: str(l.id, 20) || cvId(), label: str(l.label, 30), url: safeUrl(l.url) })).filter((l) => l.url) })),
    awards: str(r.awards, 800),
    highlights: arr(r.highlights, 4, (x) => ({ id: str(x.id, 20) || cvId(), value: str(x.value, 12), label: str(x.label, 40) })),
    interests: str(r.interests, 300),
  };
}

/** Only http(s) links are kept; a bare domain such as github.com/x gets https:// in front. Anything else becomes ''. */
export function safeUrl(v: unknown): string {
  let u = typeof v === 'string' ? v.trim().slice(0, 300) : '';
  if (!u || /\s/.test(u)) return '';
  if (!/^[a-z][a-z0-9+.-]*:/i.test(u)) u = /^[\w-]+(\.[\w-]+)+([/?#:]|$)/.test(u) ? `https://${u}` : '';
  return /^https?:\/\/[^/]+\.[^/]+/i.test(u) ? u : '';
}
/** Short text to show for a link: host and path without scheme, www and trailing slash. */
export const shortUrl = (u: string) => u.replace(/^https?:\/\/(www\.)?/i, '').replace(/\/$/, '');
export const lines = (s: string) => s.split('\n').map((l) => l.replace(/^[\s•\-–*]+/, '').trim()).filter(Boolean);
export const dateRange = (from: string, to: string) => [from, to].filter(Boolean).join(' – ');
export const contactList = (d: CvData) => [d.email, d.phone, d.address, d.website].filter(Boolean);
