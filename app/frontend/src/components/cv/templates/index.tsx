import type { ComponentType } from 'react';
import type { CvProps } from '../parts';
import type { CvFieldId } from '@/lib/cv/fields';
import { Banner, CleanRight, Executive, Minimal, Modern } from './a';
import { Bold, Creative, Serif, Tech, Timeline } from './b';
import { Cards, Ledger, Midnight, Monogram, Ring, Soft, Split, Stripe } from './c';
import { mk } from './engine';
import { MORE_TEMPLATES } from './more';
import { DISTINCT_TEMPLATES } from './distinct';
import { EXPANDED_CV_TEMPLATES } from './expanded';

export interface CvTemplateDef {
  id: string;
  name: string;
  tagline: string;
  tags: string[];
  /** industries it suits; the first one picks the sample CV shown in the gallery */
  fields: CvFieldId[];
  /** default accent when the template is picked */
  accent: string;
  photo: boolean;
  Component: ComponentType<CvProps>;
}

const T = (id: string, name: string, tagline: string, fields: CvFieldId[], accent: string, tags: string[], Component: ComponentType<CvProps>, photo = true): CvTemplateDef =>
  ({ id, name, tagline, tags, fields, accent, photo, Component });

export const CV_TEMPLATES: CvTemplateDef[] = [
  ...DISTINCT_TEMPLATES,
  T('modern', 'Hiện đại', 'Cột bên màu nổi bật, đọc nhanh', ['cntt', 'marketing', 'kythuat'], '#0ea5e9', ['2 cột'], Modern),
  T('executive', 'Chuyên nghiệp', 'Một cột gọn gàng, hợp mọi ngành', ['quanly', 'taichinh', 'nhansu'], '#1d4ed8', ['1 cột', 'ATS'], Executive),
  T('clean', 'Thanh lịch', 'Nội dung chính bên trái, thông tin phụ bên phải', ['cntt', 'nhansu', 'yte'], '#0d9488', ['2 cột'], CleanRight),
  T('banner', 'Dải màu', 'Tiêu đề màu toàn chiều ngang', ['marketing', 'sinhvien', 'thietke'], '#7c3aed', ['2 cột'], Banner),
  T('minimal', 'Tối giản', 'Nhiều khoảng trắng, chữ nhẹ', ['thietke', 'taichinh', 'yte'], '#334155', ['1 cột', 'ATS'], Minimal, false),
  T('timeline', 'Dòng thời gian', 'Trục thời gian cho kinh nghiệm và học vấn', ['cntt', 'sinhvien', 'kythuat'], '#ea580c', ['Trực quan'], Timeline),
  T('creative', 'Sáng tạo', 'Hình khối mềm, hợp thiết kế và marketing', ['thietke', 'marketing'], '#db2777', ['Nổi bật'], Creative),
  T('tech', 'Công nghệ', 'Đầu trang tối, nhãn kiểu mã nguồn', ['cntt', 'kythuat'], '#22c55e', ['Nền tối'], Tech),
  T('serif', 'Cổ điển', 'Chữ có chân, trang trọng', ['taichinh', 'yte', 'quanly'], '#9a3412', ['1 cột'], Serif),
  T('bold', 'Mạnh mẽ', 'Tên lớn, nhãn mục ở cột trái', ['marketing', 'quanly', 'dichvu'], '#e11d48', ['Nổi bật'], Bold),
  T('soft', 'Dịu nhẹ', 'Cột bên tông nhạt, ảnh bo tròn mềm mại', ['nhansu', 'yte', 'dichvu'], '#6366f1', ['2 cột'], Soft),
  T('split', 'Chia đôi', 'Đầu trang hai khối màu tương phản', ['marketing', 'thietke'], '#f97316', ['Nổi bật'], Split),
  T('midnight', 'Đêm', 'Nền tối, chữ sáng, điểm nhấn phát sáng', ['cntt', 'thietke'], '#38bdf8', ['Nền tối'], Midnight),
  T('ledger', 'Sổ ngày', 'Cột thời gian bên trái, dễ quét mắt', ['taichinh', 'nhansu', 'quanly'], '#0f766e', ['1 cột', 'ATS'], Ledger),
  T('cards', 'Thẻ', 'Mỗi mục là một thẻ bo góc', ['sinhvien', 'nhansu'], '#2563eb', ['Trực quan'], Cards),
  T('ring', 'Vòng tròn', 'Kỹ năng dạng biểu đồ vòng', ['thietke', 'marketing', 'cntt'], '#d946ef', ['Trực quan'], Ring),
  T('monogram', 'Chữ ký', 'Khung chữ cái đầu, căn giữa trang nhã', ['nhansu', 'yte', 'taichinh'], '#a16207', ['Trang trọng'], Monogram),
  T('stripe', 'Dải cạnh', 'Dải màu dọc mép trái, tiêu đề khối đậm', ['kythuat', 'quanly', 'dichvu'], '#0891b2', ['1 cột'], Stripe),

  // parametric designs (engine.tsx)
  T('kem', 'Kem pastel', 'Tên lớn trên nền kem ấm, ảnh bo góc', ['thietke', 'marketing'], '#8b6f5c', ['Pastel', 'Nổi bật'], mk({ layout: 'bigname', bg: '#f3ebe3', photo: 'rounded', head: 'caps' })),
  T('hong-pastel', 'Hồng nhẹ', 'Tên lớn trên nền hồng phấn', ['marketing', 'nhansu', 'sinhvien'], '#db2777', ['Pastel'], mk({ layout: 'bigname', bg: '#fdf0f4', photo: 'blob', head: 'dot', sideRight: true })),
  T('cam-dat', 'Cam đất', 'Gam cam ấm áp, ảnh vuông', ['marketing', 'dichvu', 'thietke'], '#c2410c', ['Pastel'], mk({ layout: 'bigname', bg: '#fbf1e6', photo: 'square', head: 'underline' })),
  T('xanh-hop', 'Xanh hộp', 'Các mục là thẻ bo góc trên nền xanh nhạt', ['nhansu', 'sinhvien', 'yte'], '#3b82f6', ['Pastel', 'Trực quan'], mk({ layout: 'cards', bg: '#e6effc', radius: 1.1, photo: 'circle', head: 'dot' })),
  T('vang-the', 'Thẻ vàng', 'Thẻ bo tròn tông vàng nắng, nổi bật', ['thietke', 'sinhvien', 'dichvu'], '#f59e0b', ['Nổi bật'], mk({ layout: 'cards', bg: '#fff4cc', radius: 1.5, photo: 'rounded', head: 'pill' })),
  T('xam-dam', 'Xám đậm', 'Đầu trang xám đậm, một cột thanh lịch', ['taichinh', 'quanly', 'nhansu'], '#52525b', ['1 cột', 'ATS'], mk({ layout: 'top', hdr: 'dark', dark: '#3f3f46', cols: 1, head: 'underline', photo: 'square', upper: true })),
  T('navy-arch', 'Navy vòm', 'Cột navy, ảnh dạng vòm, tiêu đề căn giữa', ['quanly', 'taichinh', 'kythuat'], '#38bdf8', ['2 cột'], mk({ layout: 'side', side: 'dark', dark: '#0f2a4a', head: 'center', skill: 'bar', photo: 'arch', eduSide: true })),
  T('xanh-la', 'Xanh lá', 'Cột bên xanh lá dịu, kỹ năng dạng nhãn', ['yte', 'kythuat', 'dichvu'], '#16a34a', ['2 cột'], mk({ layout: 'side', side: 'tint', head: 'dot', skill: 'chips', photo: 'circle', eduSide: true })),
  T('do-den', 'Đỏ và đen', 'Cột đen, điểm nhấn đỏ mạnh mẽ', ['marketing', 'quanly', 'cntt'], '#dc2626', ['Nền tối', 'Nổi bật'], mk({ layout: 'side', side: 'dark', dark: '#18181b', sideRight: true, head: 'box', skill: 'dots', photo: 'square' })),
  T('vang-nang', 'Vàng nắng', 'Cột vàng chữ tối, ảnh vuông bo góc', ['thietke', 'kythuat', 'sinhvien'], '#f5b301', ['2 cột'], mk({ layout: 'side', side: 'accent', sideInk: '#1c1917', head: 'underline', skill: 'bar', photo: 'rounded' })),
  T('ngoc-bich', 'Ngọc bích', 'Dải ngọc bích, cột phụ tông nhạt', ['yte', 'nhansu', 'dichvu'], '#0f766e', ['2 cột'], mk({ layout: 'top', hdr: 'band', side: 'tint', head: 'bar', skill: 'dots', photo: 'circle' })),
  T('tim-mong', 'Tím mộng mơ', 'Đầu trang nhạt, ảnh vòm nổi lên', ['thietke', 'marketing', 'sinhvien'], '#7c3aed', ['Pastel'], mk({ layout: 'top', hdr: 'arch', side: 'tint', head: 'pill', skill: 'chips', photo: 'arch' })),
  T('sinh-vien', 'Sinh viên tươi', 'Gradient trẻ trung, bố cục rõ ràng', ['sinhvien', 'marketing'], '#06b6d4', ['2 cột'], mk({ layout: 'top', hdr: 'gradient', dark: '#4338ca', head: 'dot', skill: 'chips', photo: 'circle' })),
  T('duong-sang', 'Dương sáng', 'Cột gradient xanh dương, kỹ năng dạng vòng', ['cntt', 'sinhvien', 'thietke'], '#2563eb', ['2 cột', 'Trực quan'], mk({ layout: 'side', side: 'gradient', dark: '#1e1b4b', head: 'caps', skill: 'ring', photo: 'circle' })),
  T('ngan-hang', 'Ngân hàng', 'Dải navy nghiêm túc cho khối tài chính', ['taichinh', 'quanly'], '#1e3a8a', ['2 cột'], mk({ layout: 'top', hdr: 'band', side: 'light', head: 'box', skill: 'plain', photo: 'square', upper: true })),
  T('y-khoa', 'Y khoa', 'Sạch sẽ, tin cậy, một cột dễ đọc', ['yte'], '#0891b2', ['1 cột', 'ATS'], mk({ layout: 'single', head: 'dot', photo: 'circle' })),
  T('hoc-thuat', 'Học thuật', 'Căn giữa, tiêu đề hộp, hợp giảng viên', ['yte', 'quanly'], '#374151', ['1 cột', 'ATS'], mk({ layout: 'single', center: true, head: 'box', photo: 'circle', upper: true })),
  T('ky-su', 'Kỹ sư', 'Cột xám nhạt, kỹ năng thanh tiến độ', ['kythuat', 'cntt'], '#ea580c', ['2 cột'], mk({ layout: 'side', side: 'light', head: 'box', skill: 'bar', photo: 'square', eduSide: true })),
  T('du-lich', 'Du lịch', 'Dải san hô tươi, thân thiện với khách', ['dichvu', 'marketing'], '#f43f5e', ['2 cột'], mk({ layout: 'top', hdr: 'band', side: 'tint', head: 'pill', skill: 'chips', photo: 'blob' })),
  T('xam-kem', 'Kem xám', 'Cột phải tông kem, nền giấy ấm', ['nhansu', 'quanly', 'taichinh'], '#7c6f64', ['2 cột', 'ATS'], mk({ layout: 'side', side: 'tint', sideRight: true, bg: '#fbf8f3', head: 'underline', skill: 'plain', photo: 'circle', eduSide: true })),
  ...MORE_TEMPLATES,
  ...EXPANDED_CV_TEMPLATES,
];

export const cvTemplate = (id?: string) => CV_TEMPLATES.find((t) => t.id === id) || CV_TEMPLATES[0];
