import type { ComponentType } from 'react';
import type { CvProps } from '../parts';
import type { CvFieldId } from '@/lib/cv/fields';
import { clinical, diagonal, formal, infographic, numbered, portfolio, student, threeCol } from './d';

type Def = { id: string; name: string; tagline: string; tags: string[]; fields: CvFieldId[]; accent: string; photo: boolean; Component: ComponentType<CvProps> };
const D = (id: string, name: string, tagline: string, fields: CvFieldId[], accent: string, Component: ComponentType<CvProps>, tags: string[]): Def => ({ id, name, tagline, tags, fields, accent, photo: true, Component });

const info = [
  D('chi-so-xanh', 'Chỉ số xanh', 'Dải số liệu nổi bật, kinh nghiệm theo dòng thời gian', ['marketing', 'quanly'], '#2563eb', infographic({ hdr: 'dark', dark: '#0f172a' }), ['Số liệu', '2 cột']),
  D('tang-truong', 'Tăng trưởng', 'Đầu trang sáng, số liệu thành tích to rõ', ['quanly', 'dichvu'], '#16a34a', infographic({ hdr: 'light' }), ['Số liệu', '2 cột']),
  D('doanh-so', 'Doanh số', 'Đầu trang cam rực, kỹ năng dạng vòng', ['marketing', 'dichvu'], '#ea580c', infographic({ hdr: 'accent' }), ['Số liệu', '2 cột']),
  D('du-lieu', 'Dữ liệu', 'Đầu trang tím thẫm, kỹ năng thanh tiến độ', ['cntt', 'taichinh'], '#7c3aed', infographic({ hdr: 'dark', dark: '#2e1065', skill: 'bar' }), ['Số liệu', '2 cột']),
];
const tri = [
  D('ba-cot-den', 'Ba cột đen', 'Cột đen, nội dung giữa, kỹ năng cột phải', ['cntt', 'kythuat'], '#22c55e', threeCol({ dark: '#111827' }), ['3 cột']),
  D('ba-cot-navy', 'Ba cột navy', 'Ba cột gọn gàng tông navy', ['cntt', 'quanly'], '#38bdf8', threeCol({ dark: '#0f2a4a', skill: 'dots' }), ['3 cột']),
  D('ba-cot-tim', 'Ba cột tím', 'Ba cột tông tím, kỹ năng dạng vòng', ['thietke', 'cntt'], '#c084fc', threeCol({ dark: '#2e1065', skill: 'ring' }), ['3 cột']),
  D('ba-cot-nau', 'Ba cột nâu', 'Ba cột tông nâu ấm', ['kythuat', 'dichvu'], '#f59e0b', threeCol({ dark: '#3b2a1a' }), ['3 cột']),
];
const num = [
  D('so-thu-tu', 'Đánh số', 'Tên khổng lồ, mục đánh số 01, 02, 03', ['thietke', 'marketing'], '#e11d48', numbered(), ['1 cột', 'Tối giản']),
  D('so-xanh', 'Đánh số xanh', 'Gọn, nhiều khoảng trắng, hợp tài chính', ['taichinh', 'cntt'], '#0ea5e9', numbered({ skill: 'dots' }), ['1 cột', 'ATS']),
  D('so-luc', 'Đánh số lục', 'Nhẹ nhàng cho y tế và nhân sự', ['yte', 'nhansu'], '#059669', numbered(), ['1 cột']),
];
const port = [
  D('anh-lon-den', 'Ảnh lớn đen', 'Ảnh chân dung lớn bên trái, tên đè lên ảnh', ['thietke', 'marketing'], '#f43f5e', portfolio({ dark: '#18181b' }), ['Ảnh lớn']),
  D('anh-lon-xanh', 'Ảnh lớn xanh', 'Cột ảnh xanh dương, trẻ trung', ['sinhvien', 'marketing'], '#1d4ed8', portfolio(), ['Ảnh lớn']),
  D('anh-lon-cam', 'Ảnh lớn cam', 'Cột ảnh cam ấm, thân thiện với khách', ['dichvu', 'thietke'], '#ea580c', portfolio(), ['Ảnh lớn']),
  D('anh-lon-ngoc', 'Ảnh lớn ngọc', 'Cột ảnh ngọc bích dịu mắt', ['nhansu', 'yte'], '#0f766e', portfolio({ skill: 'dots' }), ['Ảnh lớn']),
];
const clin = [
  D('lam-sang', 'Lâm sàng', 'Khung hộp, chứng chỉ hành nghề lên đầu', ['yte'], '#0891b2', clinical(), ['Y tế', '1 cột']),
  D('lam-sang-luc', 'Lâm sàng lục', 'Khung hộp tông xanh lục', ['yte', 'nhansu'], '#059669', clinical({ skill: 'bar' }), ['Y tế', '1 cột']),
  D('giang-day', 'Giảng dạy', 'Khung hộp tông tím cho giáo viên, giảng viên', ['yte', 'nhansu'], '#7c3aed', clinical({ skill: 'chips' }), ['Giáo dục']),
];
const form = [
  D('trang-trong', 'Trang trọng', 'Bảng liên hệ kẻ ô, hai cột có đường chia', ['taichinh', 'quanly'], '#1e3a8a', formal(), ['Trang trọng', 'ATS']),
  D('ke-toan', 'Kế toán', 'Gọn, đều, dễ đối chiếu số liệu', ['taichinh'], '#0f766e', formal(), ['Trang trọng', 'ATS']),
  D('phap-ly', 'Pháp lý', 'Tông đỏ rượu nghiêm cẩn', ['taichinh', 'nhansu'], '#7f1d1d', formal(), ['Trang trọng']),
];
const diag = [
  D('cheo-xanh', 'Chéo xanh', 'Đầu trang vát chéo, ảnh đè lên mép', ['sinhvien', 'cntt'], '#0ea5e9', diagonal({ dark: '#1e3a8a' }), ['Nổi bật']),
  D('cheo-cam', 'Chéo cam', 'Gradient cam đỏ, nổi bật', ['marketing', 'dichvu', 'sinhvien'], '#f97316', diagonal({ dark: '#be123c' }), ['Nổi bật']),
  D('cheo-tim', 'Chéo tím', 'Gradient tím chàm cho sáng tạo', ['thietke', 'sinhvien'], '#8b5cf6', diagonal({ dark: '#312e81' }), ['Nổi bật']),
];
const stu = [
  D('sv-xanh', 'Sinh viên xanh', 'Mục tiêu nghề nghiệp, học vấn đứng đầu', ['sinhvien'], '#2563eb', student(), ['Sinh viên']),
  D('sv-hong', 'Sinh viên hồng', 'Tươi sáng, nhấn vào hoạt động ngoại khoá', ['sinhvien', 'nhansu'], '#ec4899', student(), ['Sinh viên']),
  D('sv-luc', 'Sinh viên lục', 'Trong trẻo, hợp ngành y, giáo dục', ['sinhvien', 'yte'], '#16a34a', student({ skill: 'bar' }), ['Sinh viên']),
  D('thuc-tap-sinh', 'Thực tập sinh', 'Cam vàng năng động cho ứng viên thực tập', ['sinhvien', 'dichvu'], '#f59e0b', student(), ['Sinh viên']),
];

/** 29 structurally different designs, interleaved by family so the gallery opens with variety. */
export const DISTINCT_TEMPLATES: Def[] = (() => {
  const fam = [info, tri, num, port, clin, form, diag, stu];
  const out: Def[] = [];
  for (let i = 0; i < 4; i++) for (const f of fam) if (f[i]) out.push(f[i]);
  return out;
})();
