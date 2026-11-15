import type { ComponentType } from 'react';
import type { CvProps } from '../parts';
import type { CvFieldId } from '@/lib/cv/fields';
import { mk, type Opt } from './engine';

export interface CvTemplateDef {
  id: string;
  name: string;
  tagline: string;
  tags: string[];
  fields: CvFieldId[];
  accent: string;
  photo: boolean;
  Component: ComponentType<CvProps>;
}

const C = (
  id: string,
  name: string,
  tagline: string,
  fields: CvFieldId[],
  accent: string,
  tags: string[],
  o: Opt,
  photo = true
): CvTemplateDef => ({
  id,
  name,
  tagline,
  fields,
  accent,
  tags,
  photo,
  Component: mk(o),
});

/**
 * 40 Mẫu CV xin việc chuyên sâu mới (Phase 3)
 * Phân bổ chuẩn tuyển dụng Việt Nam: 2 cột hiện đại kết hợp 1 cột ATS tối ưu
 */
export const EXPANDED_CV_TEMPLATES: CvTemplateDef[] = [
  // ===== 1. NHÓM CÔNG NGHỆ THÔNG TIN (10 mẫu) =====
  C(
    'cv-software-engineer',
    'Kỹ Sư Phần Mềm',
    'Bố cục 2 cột chuyên sâu, khối Tech Stack & Projects trực quan',
    ['cntt', 'kythuat'],
    '#06b6d4',
    ['2 cột', 'Công nghệ', 'Hiện đại'],
    { layout: 'side', side: 'dark', dark: '#091e30', sideW: 32, head: 'caps', skill: 'bar', photo: 'square', eduSide: true, nameRule: true }
  ),
  C(
    'cv-fullstack-dev',
    'Fullstack Developer',
    'Phân tách rõ Frontend, Backend, Database và Hệ thống Microservices',
    ['cntt', 'kythuat'],
    '#3b82f6',
    ['2 cột', 'Công nghệ', 'Nổi bật'],
    { layout: 'top', hdr: 'dark', dark: '#1e293b', asideLeft: true, head: 'box', skill: 'chips', photo: 'circle' }
  ),
  C(
    'cv-frontend-dev',
    'Frontend Developer',
    'Thẩm mỹ cao, làm nổi bật kỹ năng React/Vue/Next.js và demo dự án',
    ['cntt', 'thietke'],
    '#10b981',
    ['2 cột', 'Trực quan', 'Sáng tạo'],
    { layout: 'side', side: 'tint', bg: '#f9fbf9', head: 'pill', skill: 'chips', photo: 'rounded', eduSide: true }
  ),
  C(
    'cv-backend-dev',
    'Backend Developer',
    'Tối giản, nhấn mạnh kiến trúc hệ thống, SQL/NoSQL và tối ưu hiệu năng',
    ['cntt', 'kythuat'],
    '#475569',
    ['1 cột', 'ATS', 'Tối giản'],
    { layout: 'single', head: 'underline', photo: 'square' },
    false
  ),
  C(
    'cv-ai-engineer',
    'Kỹ Sư AI & ML',
    'Tập trung vào Machine Learning, LLM, PyTorch và nghiên cứu thực chiến',
    ['cntt', 'kythuat'],
    '#8b5cf6',
    ['2 cột', 'AI Tech', 'Nền tối'],
    { layout: 'side', side: 'dark', dark: '#1e1138', sideRight: true, head: 'dot', skill: 'ring', photo: 'circle', eduSide: true }
  ),
  C(
    'cv-data-analyst',
    'Data Analyst',
    'Trình bày kỹ năng SQL, PowerBI, Tableau và chỉ số tăng trưởng kinh doanh',
    ['cntt', 'taichinh', 'marketing'],
    '#0284c7',
    ['2 cột', 'Dữ liệu', 'Trực quan'],
    { layout: 'top', hdr: 'band', side: 'light', head: 'bar', skill: 'bar', photo: 'circle' }
  ),
  C(
    'cv-data-scientist',
    'Data Scientist',
    'Cấu trúc học thuật kết hợp thực tế, thuật toán và phân tích Big Data',
    ['cntt', 'taichinh'],
    '#0d9488',
    ['1 cột', 'ATS', 'Học thuật'],
    { layout: 'top', hdr: 'plain', cols: 1, head: 'underline', photo: 'circle', upper: true }
  ),
  C(
    'cv-devops-engineer',
    'DevOps & Cloud',
    'Nhấn mạnh Docker, K8s, CI/CD pipeline, AWS/GCP và hạ tầng ổn định',
    ['cntt', 'kythuat'],
    '#f97316',
    ['2 cột', 'DevOps', 'Nổi bật'],
    { layout: 'side', side: 'dark', dark: '#1c1917', head: 'box', skill: 'chips', photo: 'square', eduSide: true }
  ),
  C(
    'cv-uiux-designer',
    'UI/UX Product Designer',
    'Bố cục cân đối như một tác phẩm thiết kế, liên kết Behance/Figma',
    ['thietke', 'cntt'],
    '#ec4899',
    ['2 cột', 'Sáng tạo', 'Pastel'],
    { layout: 'bigname', bg: '#fdf2f8', photo: 'blob', head: 'pill', sideRight: true }
  ),
  C(
    'cv-cybersecurity',
    'An Toàn Thông Tin',
    'Chuyên nghiệp, bảo mật thông tin, chứng chỉ quốc tế và phòng thủ mã độc',
    ['cntt', 'quanly'],
    '#1e3a8a',
    ['2 cột', 'Bảo mật', 'Trang trọng'],
    { layout: 'side', side: 'dark', dark: '#0b1329', sideW: 34, head: 'center', skill: 'dots', photo: 'square', eduSide: true }
  ),

  // ===== 2. NHÓM KINH DOANH, QUẢN LÝ & VẬN HÀNH (10 mẫu) =====
  C(
    'cv-business-analyst',
    'Business Analyst (BA)',
    'Cầu nối nghiệp vụ & kỹ thuật, kỹ năng phân tích luồng và User Story',
    ['quanly', 'cntt', 'taichinh'],
    '#0284c7',
    ['2 cột', 'Nghiệp vụ', 'ATS'],
    { layout: 'side', side: 'light', head: 'bar', skill: 'bar', photo: 'circle', eduSide: true }
  ),
  C(
    'cv-business-dev',
    'Phát Triển Kinh Doanh (BD)',
    'Nhấn mạnh mở rộng thị trường, quan hệ đối tác B2B và số liệu tăng trưởng',
    ['marketing', 'quanly'],
    '#b45309',
    ['2 cột', 'Tăng trưởng', 'Nổi bật'],
    { layout: 'top', hdr: 'gradient', dark: '#78350f', head: 'dot', skill: 'chips', photo: 'circle' }
  ),
  C(
    'cv-sales-executive',
    'Sales Executive VIP',
    'Làm nổi bật doanh số vượt KPI, kỹ năng đàm phán và chăm sóc khách hàng',
    ['marketing', 'dichvu'],
    '#dc2626',
    ['2 cột', 'Bán hàng', 'Năng động'],
    { layout: 'side', side: 'accent', sideInk: '#ffffff', sideW: 31, head: 'underline', skill: 'bar', photo: 'rounded', eduSide: true }
  ),
  C(
    'cv-marketing-manager',
    'Trưởng Phòng Marketing',
    'Chiến lược thương hiệu toàn diện, quản trị ngân sách và chỉ số ROI/ROAS',
    ['marketing', 'quanly'],
    '#9333ea',
    ['2 cột', 'Lãnh đạo', 'Sang trọng'],
    { layout: 'side', side: 'dark', dark: '#2e1065', head: 'caps', skill: 'dots', photo: 'arch', eduSide: true }
  ),
  C(
    'cv-digital-marketing',
    'Digital Marketer Pro',
    'Chạy ads đa kênh Facebook/Google/TikTok, tối ưu phễu chuyển đổi',
    ['marketing', 'cntt'],
    '#059669',
    ['2 cột', 'Digital', 'Hiệu quả'],
    { layout: 'cards', bg: '#ecfdf5', radius: 1.2, head: 'pill', photo: 'circle' }
  ),
  C(
    'cv-product-manager',
    'Product Manager (PM)',
    'Lộ trình phát triển sản phẩm (Roadmap), tư duy người dùng và tính năng mới',
    ['quanly', 'cntt'],
    '#2563eb',
    ['2 cột', 'Sản phẩm', 'Hiện đại'],
    { layout: 'side', side: 'gradient', dark: '#1e3a8a', sideRight: true, head: 'box', skill: 'bar', photo: 'square', eduSide: true }
  ),
  C(
    'cv-project-manager',
    'Project Manager (PMP)',
    'Quản trị Agile/Scrum, PMP, tiến độ bàn giao đúng hạn và quản lý rủi ro',
    ['quanly', 'kythuat'],
    '#334155',
    ['1 cột', 'ATS', 'Quản lý'],
    { layout: 'top', hdr: 'dark', dark: '#1e293b', cols: 1, head: 'underline', photo: 'circle', upper: true }
  ),
  C(
    'cv-human-resources',
    'Chuyên Viên Nhân Sự (HR)',
    'Tuyển dụng nhân tài, xây dựng văn hóa gắn kết doanh nghiệp và chính sách C&B',
    ['nhansu', 'quanly'],
    '#e11d48',
    ['2 cột', 'Nhân sự', 'Ấm áp'],
    { layout: 'side', side: 'tint', bg: '#fff5f7', head: 'dot', skill: 'chips', photo: 'circle', eduSide: true }
  ),
  C(
    'cv-customer-success',
    'Customer Success Lead',
    'Chăm sóc tài khoản khách hàng doanh nghiệp, tỷ lệ giữ chân và NPS cao',
    ['dichvu', 'marketing'],
    '#0891b2',
    ['2 cột', 'Chăm sóc', 'Thân thiện'],
    { layout: 'bigname', bg: '#f0fdfa', photo: 'rounded', head: 'underline' }
  ),
  C(
    'cv-operations-lead',
    'Trưởng Nhóm Vận Hành',
    'Tối ưu quy trình chuỗi cung ứng, giảm thiểu chi phí và tăng tốc độ xử lý',
    ['quanly', 'kythuat', 'taichinh'],
    '#475569',
    ['2 cột', 'Vận hành', 'Gọn gàng'],
    { layout: 'side', side: 'light', head: 'box', skill: 'bar', photo: 'square', eduSide: true }
  ),

  // ===== 3. NHÓM SÁNG TẠO, TRUYỀN THÔNG & NỘI DUNG (8 mẫu) =====
  C(
    'cv-graphic-designer',
    'Graphic Designer Visual',
    'Bố cục nghệ thuật, màu nhấn cá tính, showcase các chiến dịch xuất sắc',
    ['thietke', 'marketing'],
    '#f43f5e',
    ['2 cột', 'Visual', 'Sáng tạo'],
    { layout: 'side', side: 'accent', sideInk: '#ffffff', head: 'caps', skill: 'ring', photo: 'arch' }
  ),
  C(
    'cv-content-creator',
    'Content Creator Gen Z',
    'Trẻ trung, nổi bật kênh TikTok/Youtube, chỉ số tương tác và độ viral',
    ['marketing', 'sinhvien'],
    '#8b5cf6',
    ['Trực quan', 'Gen Z', 'Xu hướng'],
    { layout: 'cards', bg: '#f5f3ff', radius: 1.4, head: 'pill', photo: 'blob' }
  ),
  C(
    'cv-copywriter',
    'Copywriter & Storyteller',
    'Bút lực sắc sảo, ngôn từ tinh đọng, làm nổi bật slogan và bài PR',
    ['marketing', 'thietke'],
    '#b45309',
    ['1 cột', 'Nghệ thuật', 'Ngôn từ'],
    { layout: 'single', center: true, head: 'underline', photo: 'circle' }
  ),
  C(
    'cv-video-editor',
    'Video Editor & Motion',
    'Kỹ năng dựng Premiere/After Effects, portfolio showreel sống động',
    ['thietke', 'cntt'],
    '#06b6d4',
    ['2 cột', 'Motion', 'Nền tối'],
    { layout: 'side', side: 'dark', dark: '#082f49', sideRight: true, head: 'caps', skill: 'chips', photo: 'square', eduSide: true }
  ),
  C(
    'cv-social-media',
    'Social Media Specialist',
    'Kỹ năng quản trị Fanpage/Cộng đồng triệu follow, tăng trưởng tự nhiên',
    ['marketing', 'dichvu'],
    '#ec4899',
    ['2 cột', 'Social', 'Hiện đại'],
    { layout: 'top', hdr: 'arch', side: 'tint', head: 'pill', skill: 'chips', photo: 'circle' }
  ),
  C(
    'cv-brand-designer',
    'Brand Identity Designer',
    'Hệ thống nhận diện thương hiệu, bộ quy chuẩn Guideline và bao bì nhãn mác',
    ['thietke', 'marketing'],
    '#18181b',
    ['2 cột', 'Branding', 'Tối giản'],
    { layout: 'side', side: 'dark', dark: '#18181b', head: 'underline', skill: 'plain', photo: 'square', eduSide: true }
  ),
  C(
    'cv-event-planner',
    'Chuyên Viên Tổ Chức Sự Kiện',
    'Điều phối sự kiện quy mô, quản lý nhà thầu, xử lý linh hoạt mọi tình huống',
    ['dichvu', 'marketing'],
    '#ea580c',
    ['2 cột', 'Sự kiện', 'Nổi bật'],
    { layout: 'top', hdr: 'band', side: 'tint', asideLeft: true, head: 'bar', skill: 'bar', photo: 'rounded' }
  ),
  C(
    'cv-pr-specialist',
    'Quan Hệ Công Chúng (PR)',
    'Mối quan hệ báo chí sâu rộng, kỹ năng họp báo và xử lý khủng hoảng truyền thông',
    ['marketing', 'quanly'],
    '#1e40af',
    ['2 cột', 'Báo chí', 'Trang trọng'],
    { layout: 'side', side: 'tint', bg: '#f8fafc', head: 'center', skill: 'dots', photo: 'circle', eduSide: true }
  ),

  // ===== 4. NHÓM SINH VIÊN, THỰC TẬP SINH & NGÀNH NGHỀ ĐẶC THÙ (8 mẫu) =====
  C(
    'cv-sinh-vien-chua-kn',
    'Sinh Viên Chưa Kinh Nghiệm',
    'Tập trung hoạt động ngoại khóa, kỹ năng mềm, giải thưởng và tinh thần học hỏi',
    ['sinhvien', 'marketing'],
    '#059669',
    ['2 cột', 'Sinh viên', 'Tươi sáng'],
    { layout: 'top', hdr: 'gradient', dark: '#064e3b', head: 'dot', skill: 'chips', photo: 'circle' }
  ),
  C(
    'cv-thuc-tap-sinh',
    'Thực Tập Sinh (Internship)',
    'Nhiệt huyết, cầu thị, mục tiêu nghề nghiệp rõ ràng và khả năng thích ứng cao',
    ['sinhvien', 'cntt', 'nhansu'],
    '#3b82f6',
    ['2 cột', 'Intern', 'Gọn gàng'],
    { layout: 'side', side: 'light', head: 'underline', skill: 'bar', photo: 'circle', eduSide: true }
  ),
  C(
    'cv-sinh-vien-moi-tot-nghiep',
    'Mới Tốt Nghiệp Xuất Sắc',
    'GPA cao, đồ án tốt nghiệp ấn tượng, các kỳ thực tập thực tế tại doanh nghiệp',
    ['sinhvien', 'kythuat', 'taichinh'],
    '#f59e0b',
    ['2 cột', 'Cử nhân', 'Tự hào'],
    { layout: 'cards', bg: '#fffbeb', radius: 1.2, head: 'pill', photo: 'rounded' }
  ),
  C(
    'cv-hoc-thuat-nghien-cuu',
    'Học Thuật & Học Bổng Du Học',
    'Cấu trúc chuẩn quốc tế để nộp học bổng thạc sĩ / tiến sĩ và viện nghiên cứu',
    ['sinhvien', 'yte', 'quanly'],
    '#374151',
    ['1 cột', 'ATS', 'Quốc tế'],
    { layout: 'single', center: true, head: 'box', photo: 'circle', upper: true }
  ),
  C(
    'cv-ke-toan-tai-chinh',
    'Kế Toán Tổng Hợp & Thuế',
    'Ngăn nắp, chuẩn mực số liệu, thành thạo phần mềm MISA, báo cáo tài chính',
    ['taichinh', 'quanly'],
    '#1e3a8a',
    ['2 cột', 'Kế toán', 'Chính xác'],
    { layout: 'side', side: 'tint', sideRight: true, head: 'box', skill: 'plain', photo: 'square', eduSide: true }
  ),
  C(
    'cv-giao-vien-giang-vien',
    'Giáo Viên & Giảng Viên',
    'Phương pháp sư phạm tiên tiến, chứng chỉ IELTS/TESOL, nhiệt huyết truyền lửa',
    ['yte', 'nhansu'],
    '#0d9488',
    ['2 cột', 'Giáo dục', 'Tin cậy'],
    { layout: 'top', hdr: 'band', side: 'tint', head: 'dot', skill: 'dots', photo: 'circle' }
  ),
  C(
    'cv-du-lich-khach-san',
    'Khách Sạn & Dịch Vụ Du Lịch',
    'Ngoại ngữ lưu loát, kỹ năng giao tiếp niềm nở, nghiệp vụ lễ tân chuẩn 5 sao',
    ['dichvu', 'marketing'],
    '#e11d48',
    ['2 cột', 'Du lịch', 'Nhiệt tình'],
    { layout: 'side', side: 'tint', bg: '#fff5f5', head: 'pill', skill: 'chips', photo: 'circle', eduSide: true }
  ),
  C(
    'cv-y-te-dieu-duong',
    'Bác Sĩ & Điều Dưỡng Đa Khoa',
    'Tận tâm, chứng chỉ hành nghề y tế, kinh nghiệm lâm sàng tại các bệnh viện lớn',
    ['yte'],
    '#0284c7',
    ['1 cột', 'Y tế', 'Chuẩn mực'],
    { layout: 'single', head: 'dot', photo: 'circle' }
  ),

  // ===== 5. NHÓM PHONG CÁCH TUYỂN DỤNG ĐẶC BIỆT (4 mẫu) =====
  C(
    'cv-ats-single-column',
    'Chuẩn ATS 1 Cột Tối Giản',
    '1 cột thuần văn bản, 100% tương thích mọi bộ máy lọc hồ sơ ATS quốc tế',
    ['cntt', 'taichinh', 'quanly', 'kythuat'],
    '#1f2937',
    ['1 cột', 'ATS', 'Thuần văn bản'],
    { layout: 'single', head: 'underline', photo: 'circle', upper: true },
    false
  ),
  C(
    'cv-executive-senior',
    'Lãnh Đạo Cấp Cao C-Level',
    'Dành cho Giám đốc, Trưởng phòng 10+ năm kinh nghiệm, tông Navy uy quyền',
    ['quanly', 'taichinh'],
    '#0f2a4a',
    ['2 cột', 'Executive', 'Uy quyền'],
    { layout: 'side', side: 'dark', dark: '#0c1a2e', sideW: 35, head: 'center', skill: 'plain', photo: 'square', eduSide: true }
  ),
  C(
    'cv-clean-monochrome',
    'Monochrome Đen Trắng Quốc Tế',
    'Đen trắng thanh lịch, tối giản tuyệt đối, chuẩn mực ứng tuyển đa quốc gia',
    ['cntt', 'thietke', 'marketing'],
    '#111827',
    ['2 cột', 'Monochrome', 'Thanh lịch'],
    { layout: 'side', side: 'light', head: 'bar', skill: 'plain', photo: 'square', eduSide: true }
  ),
  C(
    'cv-two-column-accent',
    '2 Cột Cân Đối Hiện Đại',
    'Phối màu vàng nắng và than chì cân bằng hoàn hảo, nổi bật trong mắt nhà tuyển dụng',
    ['marketing', 'cntt', 'sinhvien'],
    '#f59e0b',
    ['2 cột', 'Nổi bật', 'Cân đối'],
    { layout: 'side', side: 'accent', sideInk: '#111827', sideRight: true, head: 'underline', skill: 'bar', photo: 'rounded', eduSide: true }
  ),
];
