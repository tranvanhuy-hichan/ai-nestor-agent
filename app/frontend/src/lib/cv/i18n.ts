/** Language of the CV itself (section headings, watermark); the editor UI stays Vietnamese. */
export type CvLang = 'vi' | 'en';
export const CV_LANGS: { id: CvLang; label: string }[] = [{ id: 'vi', label: 'Tiếng Việt' }, { id: 'en', label: 'English' }];
export const cvLang = (v: unknown): CvLang => (v === 'en' ? 'en' : 'vi');

/** Vietnamese heading (as written in the templates) -> English. */
const EN: Record<string, string> = {
  'Liên hệ': 'Contact',
  'Giới thiệu': 'Profile',
  'Mục tiêu nghề nghiệp': 'Career objective',
  'Kinh nghiệm': 'Experience',
  'Kinh nghiệm làm việc': 'Work experience',
  'Học vấn': 'Education',
  'Kỹ năng': 'Skills',
  'Kỹ năng và ngoại ngữ': 'Skills & languages',
  'Chuyên môn': 'Expertise',
  'Ngoại ngữ': 'Languages',
  'Dự án': 'Projects',
  'Dự án tiêu biểu': 'Key projects',
  'Thành tích': 'Achievements',
  'Thành tích và chứng chỉ': 'Achievements & certificates',
  'Chứng chỉ': 'Certificates',
  'Chứng chỉ và giấy phép hành nghề': 'Certificates & licences',
  'Sở thích': 'Interests',
  'Khác': 'Other',
  'Hoạt động': 'Activities',
};
export const trLabel = (lang: CvLang, s: string) => (lang === 'en' ? EN[s] ?? s : s);
