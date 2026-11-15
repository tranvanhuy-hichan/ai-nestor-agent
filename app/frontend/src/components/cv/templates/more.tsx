import type { ComponentType } from 'react';
import type { CvProps } from '../parts';
import type { CvFieldId } from '@/lib/cv/fields';
import { mk, type Opt } from './engine';

type Def = { id: string; name: string; tagline: string; tags: string[]; fields: CvFieldId[]; accent: string; photo: boolean; Component: ComponentType<CvProps> };
const D = (id: string, name: string, tagline: string, fields: CvFieldId[], accent: string, o: Opt, tags: string[] = ['2 cột']): Def =>
  ({ id, name, tagline, fields, accent, tags, photo: true, Component: mk(o) });

/** 40 more designs on the parametric engine, mostly two columns (the layout that sells best). */
export const MORE_TEMPLATES: Def[] = [
  // two columns with a coloured side panel
  D('rieu-xanh', 'Xanh rêu', 'Cột rêu đậm, điểm nhấn xanh lá sáng', ['kythuat', 'yte', 'quanly'], '#4ade80', { layout: 'side', side: 'dark', dark: '#14532d', sideW: 33, head: 'caps', skill: 'bar', photo: 'circle', eduSide: true, nameRule: true }),
  D('hoang-hon', 'Hoàng hôn', 'Cột gradient cam đỏ ấm áp', ['marketing', 'dichvu', 'thietke'], '#f97316', { layout: 'side', side: 'gradient', dark: '#9a3412', head: 'underline', skill: 'dots', photo: 'rounded' }),
  D('lam-ngoc', 'Lam ngọc', 'Cột xanh lam sâu, ảnh dạng vòm', ['taichinh', 'quanly', 'cntt'], '#22d3ee', { layout: 'side', side: 'dark', dark: '#0c4a6e', sideRight: true, head: 'center', skill: 'bar', photo: 'arch', eduSide: true }),
  D('tim-than', 'Tím than', 'Cột tím thẫm, kỹ năng dạng nhãn', ['thietke', 'marketing', 'cntt'], '#c084fc', { layout: 'side', side: 'dark', dark: '#3b0764', head: 'box', skill: 'chips', photo: 'square' }),
  D('ruou-vang', 'Rượu vang', 'Cột đỏ rượu sang trọng', ['dichvu', 'quanly', 'marketing'], '#fb7185', { layout: 'side', side: 'dark', dark: '#4c0519', head: 'caps', skill: 'plain', photo: 'circle', eduSide: true }),
  D('than-chi', 'Than chì', 'Cột than đen, điểm nhấn vàng chanh', ['cntt', 'kythuat', 'quanly'], '#facc15', { layout: 'side', side: 'dark', dark: '#27272a', sideRight: true, head: 'bar', skill: 'dots', photo: 'square' }),
  D('bien-xanh', 'Biển xanh', 'Cột xanh biển tươi, gọn gàng', ['sinhvien', 'cntt', 'nhansu'], '#0369a1', { layout: 'side', side: 'accent', sideW: 30, head: 'underline', skill: 'bar', photo: 'circle', eduSide: true }),
  D('bac-ha', 'Bạc hà', 'Cột bạc hà nhạt, ảnh hình giọt', ['yte', 'nhansu', 'dichvu'], '#0d9488', { layout: 'side', side: 'tint', head: 'dot', skill: 'chips', photo: 'blob' }),
  D('oai-huong', 'Oải hương', 'Cột tím nhạt mộng mơ', ['thietke', 'sinhvien', 'marketing'], '#8b5cf6', { layout: 'side', side: 'tint', sideRight: true, head: 'pill', skill: 'chips', photo: 'rounded' }),
  D('san-ho', 'San hô', 'Cột san hô tươi, nổi bật', ['marketing', 'dichvu', 'sinhvien'], '#f43f5e', { layout: 'side', side: 'accent', sideW: 31, head: 'caps', skill: 'dots', photo: 'circle' }),
  D('chanh-vang', 'Chanh vàng', 'Cột vàng chanh, chữ tối dễ đọc', ['thietke', 'kythuat', 'sinhvien'], '#eab308', { layout: 'side', side: 'accent', sideInk: '#1c1917', head: 'bar', skill: 'bar', photo: 'square' }),
  D('nau-dat', 'Nâu đất', 'Nền giấy ấm, cột nâu nhạt', ['nhansu', 'quanly', 'taichinh'], '#92400e', { layout: 'side', side: 'tint', bg: '#fffaf3', head: 'underline', skill: 'plain', photo: 'circle', eduSide: true }),
  D('xanh-lo', 'Xanh lơ', 'Cột xanh lơ nhạt, tiêu đề khối', ['cntt', 'yte', 'nhansu'], '#0284c7', { layout: 'side', side: 'tint', sideRight: true, head: 'box', skill: 'bar', photo: 'rounded', eduSide: true }),
  D('ngoc-luc', 'Ngọc lục', 'Cột gradient lục bảo, kỹ năng dạng vòng', ['yte', 'kythuat', 'cntt'], '#059669', { layout: 'side', side: 'gradient', dark: '#064e3b', head: 'dot', skill: 'ring', photo: 'circle' }),
  D('hong-dao', 'Hồng đào', 'Cột hồng đào dịu, nền sáng', ['marketing', 'nhansu', 'dichvu'], '#ec4899', { layout: 'side', side: 'tint', bg: '#fffafc', head: 'pill', skill: 'bar', photo: 'blob' }),
  D('xam-bac', 'Xám bạc', 'Cột xám nhạt trung tính, hợp mọi ngành', ['taichinh', 'nhansu', 'quanly'], '#475569', { layout: 'side', side: 'light', head: 'box', skill: 'dots', photo: 'square', eduSide: true }, ['2 cột', 'ATS']),
  D('cam-chay', 'Cam cháy', 'Cột nâu cam đậm, ảnh vòm', ['thietke', 'dichvu', 'marketing'], '#fb923c', { layout: 'side', side: 'dark', dark: '#431407', head: 'center', skill: 'bar', photo: 'arch' }),
  D('cham', 'Chàm', 'Cột gradient chàm, tiêu đề in hoa', ['cntt', 'quanly', 'sinhvien'], '#4f46e5', { layout: 'side', side: 'gradient', dark: '#1e1b4b', sideRight: true, head: 'caps', skill: 'bar', photo: 'circle', eduSide: true }),
  D('xanh-mint', 'Xanh mint', 'Cột mint rộng, nền trắng sạch', ['yte', 'sinhvien', 'nhansu'], '#14b8a6', { layout: 'side', side: 'tint', sideW: 34, bg: '#f7fffd', head: 'underline', skill: 'chips', photo: 'circle' }),
  D('dat-nung', 'Đất nung', 'Cột đỏ đất nung mạnh mẽ', ['kythuat', 'quanly', 'dichvu'], '#c2410c', { layout: 'side', side: 'accent', head: 'box', skill: 'dots', photo: 'rounded' }),
  D('tiem-xanh', 'Thông xanh', 'Cột xanh thông, ánh ngọc', ['cntt', 'kythuat', 'taichinh'], '#5eead4', { layout: 'side', side: 'dark', dark: '#0f3d3e', head: 'dot', skill: 'bar', photo: 'circle', eduSide: true }),
  D('hoa-cuc', 'Hoa cúc', 'Cột vàng kem, vui và thân thiện', ['yte', 'dichvu', 'sinhvien'], '#d97706', { layout: 'side', side: 'tint', bg: '#fffdf5', head: 'pill', skill: 'dots', photo: 'blob', eduSide: true }),
  D('thep-xanh', 'Thép xanh', 'Cột xanh thép, kỹ năng dạng vòng', ['cntt', 'kythuat', 'quanly'], '#60a5fa', { layout: 'side', side: 'dark', dark: '#1e293b', sideRight: true, head: 'bar', skill: 'ring', photo: 'square' }),
  D('tia-chop', 'Tia chớp', 'Cột tím điện, năng động', ['marketing', 'cntt', 'sinhvien'], '#7c3aed', { layout: 'side', side: 'accent', head: 'caps', skill: 'bar', photo: 'rounded', eduSide: true }),
  D('nho-chin', 'Nho chín', 'Cột gradient tím hồng, ảnh vòm', ['thietke', 'marketing', 'dichvu'], '#a21caf', { layout: 'side', side: 'gradient', dark: '#3b0764', head: 'center', skill: 'dots', photo: 'arch' }),
  D('ngoc-nhat', 'Ngọc nhạt', 'Cột xám ngọc nhẹ, thanh lịch', ['yte', 'nhansu', 'taichinh'], '#0891b2', { layout: 'side', side: 'light', head: 'dot', skill: 'bar', photo: 'circle' }, ['2 cột', 'ATS']),
  D('do-son', 'Đỏ son', 'Cột đỏ son rực, ảnh vuông', ['marketing', 'dichvu', 'quanly'], '#b91c1c', { layout: 'side', side: 'accent', sideRight: true, head: 'underline', skill: 'bar', photo: 'square', eduSide: true }),
  D('ca-phe-sua', 'Cà phê sữa', 'Tông nâu kem ấm, nền giấy', ['dichvu', 'nhansu', 'thietke'], '#78350f', { layout: 'side', side: 'tint', bg: '#fbf7f1', head: 'caps', skill: 'plain', photo: 'rounded' }),

  // two columns under a header
  D('dai-duong', 'Đại dương', 'Đầu trang gradient xanh, cột phụ nhạt', ['cntt', 'sinhvien', 'marketing'], '#0891b2', { layout: 'top', hdr: 'gradient', dark: '#1e3a8a', side: 'tint', head: 'dot', skill: 'dots', photo: 'circle' }),
  D('bao-tim', 'Bão tím', 'Đầu trang tím thẫm, điểm nhấn tím sáng', ['thietke', 'cntt', 'quanly'], '#a78bfa', { layout: 'top', hdr: 'dark', dark: '#2e1065', head: 'bar', skill: 'chips', photo: 'square' }),
  D('rung-xanh', 'Rừng xanh', 'Đầu trang xanh lá, cột phụ bên trái', ['yte', 'kythuat', 'nhansu'], '#15803d', { layout: 'top', hdr: 'band', side: 'tint', asideLeft: true, head: 'underline', skill: 'bar', photo: 'circle' }),
  D('nang-som', 'Nắng sớm', 'Đầu trang vàng nhạt, ảnh vòm nổi lên', ['dichvu', 'sinhvien', 'thietke'], '#f59e0b', { layout: 'top', hdr: 'arch', side: 'tint', head: 'pill', skill: 'chips', photo: 'arch' }),
  D('cam-quyt', 'Cam quýt', 'Đầu trang cam, cột phụ xám nhạt bên trái', ['marketing', 'dichvu', 'kythuat'], '#ea580c', { layout: 'top', hdr: 'band', side: 'light', asideLeft: true, head: 'box', skill: 'bar', photo: 'rounded' }),
  D('xanh-thep', 'Xanh thép', 'Đầu trang tối, cột phụ bên trái', ['cntt', 'taichinh', 'kythuat'], '#38bdf8', { layout: 'top', hdr: 'dark', dark: '#0f172a', asideLeft: true, head: 'caps', skill: 'dots', photo: 'circle' }),
  D('hong-ruoc', 'Hồng rước', 'Đầu trang gradient hồng, ảnh hình giọt', ['marketing', 'nhansu', 'sinhvien'], '#e11d48', { layout: 'top', hdr: 'gradient', dark: '#831843', head: 'pill', skill: 'chips', photo: 'blob' }),
  D('thanh-tra', 'Thanh trà', 'Đầu trang trắng gạch chân, cột phụ bên trái', ['taichinh', 'nhansu', 'yte'], '#0f766e', { layout: 'top', hdr: 'plain', side: 'tint', asideLeft: true, head: 'dot', skill: 'bar', photo: 'circle' }, ['2 cột', 'ATS']),

  // cards and big names
  D('kem-nau', 'Kem nâu', 'Tên lớn trên nền kem, ảnh vuông bên phải', ['thietke', 'dichvu', 'marketing'], '#7c4a2d', { layout: 'bigname', bg: '#f6efe6', photo: 'square', head: 'underline', sideRight: true }, ['Pastel', '2 cột']),
  D('xanh-pastel', 'Xanh bạc hà thẻ', 'Thẻ bo góc trên nền xanh bạc hà', ['yte', 'sinhvien', 'nhansu'], '#059669', { layout: 'cards', bg: '#e7f6ef', radius: 1.2, photo: 'circle', head: 'dot' }, ['Pastel', '2 cột']),
  D('tim-pastel', 'Tím thẻ', 'Thẻ bo tròn trên nền tím phấn', ['thietke', 'marketing', 'sinhvien'], '#7c3aed', { layout: 'cards', bg: '#f1ebfb', radius: 1.6, photo: 'rounded', head: 'pill' }, ['Pastel', '2 cột']),
  D('hong-phan', 'Hồng phấn tên lớn', 'Tên lớn trên nền hồng phấn', ['marketing', 'nhansu', 'dichvu'], '#be185d', { layout: 'bigname', bg: '#fde8ee', photo: 'circle', head: 'caps' }, ['Pastel', '2 cột']),
];
