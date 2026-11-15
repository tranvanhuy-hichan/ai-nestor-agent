import type { Assistant } from './assistants'

// Keep legacy records available for existing URLs and sessions.
const CORE = new Set([
  'van-thu-nd30', 'van-ban-dang-hd05', 'tong-hop-bao-cao', 'ra-soat-the-thuc', 'bien-ban-hop',
  'ke-toan', 'nhan-su', 'quan-ly-du-an', 'giao-an', 'ra-de-cham-bai',
  'gia-su', 'on-thi', 'ngoai-ngu', 'viet-bai-nghien-cuu', 'slide-thuyet-trinh', 'cv-viec-lam', 'tai-chinh-ca-nhan',
])
export function coreFeatures(list: Assistant[]): Assistant[] {
  return list.filter((a) => CORE.has(a.id) || a.builtin === false)
}
export function searchableText(value: string): string {
  return value.normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/đ/g, 'd').replace(/Đ/g, 'D').toLowerCase()
}
