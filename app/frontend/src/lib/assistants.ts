import { useQuery } from '@tanstack/react-query'
import { api } from '@/lib/api'
import { tk } from '@/lib/i18n.ts'

export type FormField = { key: string; label: string; type: 'text' | 'textarea' | 'select' | 'number' | 'file' | 'cv-template' | 'cv-profile'; required?: boolean; placeholder?: string; hint?: string; options?: string[]; accept?: string; multiple?: boolean }
export type FormStep = { id: string; label: string; goal: string; task: string; fields: FormField[]; review: string[]; produces: string[]; submit?: string; optional?: boolean }
export type FormFlow = { id: string; label: string; desc: string; steps: FormStep[] }
export type FeatureForm = { experience?: { title: string; checks: string[]; handoff: string }; intro?: string; flows: FormFlow[]; panels?: string[] }
export interface Assistant { builtin?: boolean; id: string; name: string; icon: string; group: string; description: string; starters: string[]; form?: FeatureForm; done_criteria?: string[]; deliverables?: string[] }

export const GROUP_GOV = tk('Cơ quan nhà nước')
export const GROUP_BIZ = tk('Doanh nghiệp')
export const GROUP_STUDENT = tk('Học sinh')
export const GROUP_TEACHER = tk('Giáo viên')
export const GROUP_UNI = tk('Sinh viên')
export const GROUP_PERSONAL = tk('Cá nhân')
/** Thứ tự và tên hiển thị của các nhóm trợ lý (slug do máy chủ trả về -> tên). */
export const GROUPS: Record<string, string> = { 'co-quan': GROUP_GOV, 'doanh-nghiep': GROUP_BIZ, 'giao-vien': GROUP_TEACHER, 'hoc-sinh': GROUP_STUDENT, 'sinh-vien': GROUP_UNI, 'ca-nhan': GROUP_PERSONAL }
/** Trợ lý hiện sẵn ở trang chủ và màn hình chat trống; các trợ lý còn lại nằm sau nút 'Xem tất cả'. */
export const FEATURED = ['van-thu-nd30', 'bien-ban-hop', 'tong-hop-bao-cao', 'ra-soat-the-thuc', 'ke-toan', 'giao-an', 'ra-de-cham-bai', 'gia-su', 'viet-bai-nghien-cuu', 'slide-thuyet-trinh']
export const GROUP_ORDER = Object.values(GROUPS)

/** Danh sách dự phòng khi máy chủ chưa trả về /api/assistants. Chuỗi được dịch lúc hiển thị bằng t(). */
export const FALLBACK_ASSISTANTS: Assistant[] = [
  { id: 'van-thu-nd30', name: tk('Văn thư'), icon: 'file-text', group: GROUP_GOV, description: tk('Soạn công văn, tờ trình, quyết định đúng thể thức NĐ 30/2020'), starters: [tk('Soạn tờ trình xin kinh phí tổ chức hội nghị tổng kết năm'), tk('Soạn công văn đề nghị báo cáo số liệu quý này')] },
  { id: 'tong-hop-bao-cao', name: tk('Tổng hợp báo cáo'), icon: 'layers', group: GROUP_GOV, description: tk('Gộp, đối chiếu báo cáo của nhiều đơn vị, chỉ ra chỗ lệch số liệu'), starters: [tk('Tổng hợp các file báo cáo đính kèm thành một báo cáo chung')] },
  { id: 'gia-su', name: tk('Gia sư học tập'), icon: 'graduation-cap', group: GROUP_STUDENT, description: tk('Giảng bài từng bước, giải đáp thắc mắc cho học sinh'), starters: [tk('Giải thích định lý Pi-ta-go và cho 3 bài tập tăng dần độ khó')] },
  { id: 'giao-an', name: tk('Soạn giáo án'), icon: 'notebook-pen', group: GROUP_TEACHER, description: tk('Soạn giáo án, kế hoạch bài dạy, phiếu học tập'), starters: [tk('Soạn giáo án Toán lớp 7 bài Tỉ lệ thức, thời lượng 2 tiết')] },
  { id: 'viet-bai-nghien-cuu', name: tk('Viết bài và báo cáo'), icon: 'pen-line', group: GROUP_UNI, description: tk('Lập dàn ý, viết tiểu luận, tóm tắt tài liệu'), starters: [tk('Lập dàn ý tiểu luận về chuyển đổi số trong giáo dục')] },
  { id: 'thu-ky', name: tk('Thư ký'), icon: 'calendar-check', group: GROUP_BIZ, description: tk('Tóm tắt email, sắp xếp lịch họp, soạn thư trả lời, nhắc việc'), starters: [tk('Soạn thư trả lời khách hàng xin lùi lịch họp'), tk('Lập lịch làm việc tuần này cho tôi')] },
  { id: 'ke-toan', name: tk('Kế toán – Tài chính'), icon: 'calculator', group: GROUP_BIZ, description: tk('Bảng tính có công thức, biểu đồ, đối chiếu số liệu'), starters: [tk('Làm sạch bảng Excel đính kèm và vẽ biểu đồ doanh thu theo tháng')] },
  { id: 'nhan-su', name: tk('Hành chính – Nhân sự'), icon: 'users', group: GROUP_BIZ, description: tk('Hợp đồng, quy chế, tin tuyển dụng, tài liệu cho nhân viên mới'), starters: [tk('Soạn tin tuyển dụng vị trí nhân viên kinh doanh')] },
  { id: 'kinh-doanh-marketing', name: tk('Kinh doanh – Marketing'), icon: 'trending-up', group: GROUP_BIZ, description: tk('Hồ sơ năng lực, slide thuyết trình, bài đăng truyền thông'), starters: [tk('Làm bộ slide giới thiệu công ty 10 trang')] },
]

export function useAssistants() {
  return useQuery({
    queryKey: ['assistants'],
    queryFn: async () => {
      try {
        const r = await api.get<Assistant[] | { assistants: Assistant[] }>('/api/assistants')
        const list = (Array.isArray(r) ? r : r.assistants)?.map((a) => ({ ...a, group: GROUPS[a.group] ?? a.group, starters: a.starters ?? [] }))
        return list?.length ? list : FALLBACK_ASSISTANTS
      } catch { return FALLBACK_ASSISTANTS }
    },
    staleTime: 60_000,
  })
}
