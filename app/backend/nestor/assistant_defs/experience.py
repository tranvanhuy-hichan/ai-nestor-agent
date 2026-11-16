"""Domain acceptance and handoff contracts for the curated feature catalogue."""
from copy import deepcopy

# Input checks describe what the agent must resolve before producing a final artifact.
CONTRACTS = {
    'van-thu-nd30': ('Mẫu cơ quan và thông tin trình ký', ['Đủ cơ quan, loại văn bản, nội dung và người ký hoặc ghi rõ chỗ chưa xác nhận', 'Phân biệt căn cứ đã kiểm chứng với thông tin cần bổ sung'], 'Bàn giao bản Word, kết quả rà thể thức và danh sách thông tin cần xác nhận trước khi trình ký.'),
    'van-ban-dang-hd05': ('Mẫu cấp ủy và hướng dẫn gốc', ['Xác định đúng hệ thống văn bản Đảng và cấp ban hành', 'Đối chiếu mẫu đơn vị cung cấp, không trộn thể thức hành chính'], 'Bàn giao dự thảo Word và bảng điểm cần đối chiếu với hướng dẫn gốc; không tuyên bố đã được phê duyệt.'),
    'tong-hop-bao-cao': ('Bộ báo cáo và quy tắc đối chiếu', ['Kiểm kê đủ file và đơn vị, kỳ báo cáo, đơn vị tính', 'Liệt kê dữ liệu thiếu, trùng và chênh lệch, không tự sửa nguồn'], 'Bàn giao bảng tổng hợp có công thức, nguồn từng chỉ tiêu, bảng sai lệch và báo cáo chung.'),
    'ra-soat-the-thuc': ('Dự thảo và phạm vi kiểm tra', ['Chốt chuẩn thể thức và phạm vi rà', 'Giữ nguyên file gốc, phân biệt lỗi xác định với điểm cần người có thẩm quyền kiểm tra'], 'Bàn giao báo cáo có vị trí lỗi và cách sửa; nếu có bản sửa, đặt tên phiên bản mới và nêu các lỗi còn mở.'),
    'bien-ban-hop': ('Nguồn cuộc họp và nhiệm vụ', ['Đủ tên họp, thời gian, thành phần và nguồn ghi nhận', 'Phân biệt ý kiến, kết luận và việc được giao; không suy diễn người phụ trách hoặc hạn'], 'Bàn giao biên bản và bảng nhiệm vụ gồm việc, người phụ trách, hạn, thông tin chưa xác nhận.'),
    'ke-toan': ('Nguồn số liệu và quy tắc tính', ['Chốt kỳ, đơn vị tiền, khóa ghép và dung sai', 'Kiểm kê dòng nguồn, dòng trùng, thiếu và tổng kiểm soát trước/sau xử lý'], 'Bàn giao Excel có dữ liệu gốc, công thức, kết quả đối chiếu và nhật ký thay đổi; nêu rõ chênh lệch chưa xử lý.'),
    'nhan-su': ('Mẫu và dữ liệu nhân sự', ['Kiểm tra dữ liệu từng dòng và biến trong mẫu', 'Không tự thêm quyền lợi, điều khoản hoặc thông tin cá nhân còn thiếu'], 'Bàn giao tài liệu, danh sách dòng thành công/thất bại và các điều khoản cần đơn vị xác nhận; không tự gửi hoặc đăng tuyển.'),
    'quan-ly-du-an': ('Phạm vi, nguồn lực và tiến độ', ['Chốt mục tiêu, phạm vi bao gồm/không bao gồm, nguồn lực và mốc bắt buộc', 'Mỗi việc có đầu ra, người phụ trách, hạn và phụ thuộc; số liệu tiến độ có ngày cập nhật'], 'Bàn giao kế hoạch, sổ rủi ro và danh sách quyết định còn mở, cùng hướng dẫn cập nhật tiến độ kỳ tiếp theo.'),
    'giao-an': ('Mẫu bài dạy và điều kiện lớp', ['Chốt môn/lớp, bộ sách, thời lượng và yêu cầu cần đạt', 'Mỗi hoạt động có nhiệm vụ, sản phẩm và cách đánh giá; học liệu phù hợp điều kiện lớp'], 'Bàn giao giáo án và học liệu đã chọn, bảng phân bổ thời gian và các điều chỉnh giáo viên cần xem trước khi dạy.'),
    'ra-de-cham-bai': ('Đặc tả đề và quy tắc chấm', ['Đối chiếu từng câu với ma trận, tổng điểm và thời lượng', 'Tách đề học sinh khỏi đáp án; giải thử, kiểm tra mã đề và phép tính điểm'], 'Bàn giao đề, đáp án/thang điểm và ma trận hoặc bảng điểm theo quy trình; liệt kê câu cần giáo viên duyệt.'),
    'gia-su': ('Buổi học theo mức hiểu', ['Xác định môn/lớp và điểm người học đang vướng', 'Giữ lựa chọn gợi ý hay lời giải, đối chiếu bài làm trước khi nhận xét'], 'Kết thúc bằng điều đã hiểu, lỗi cần tránh và bài tự luyện có đáp án riêng; đề xuất nội dung buổi sau.'),
    'on-thi': ('Kế hoạch ôn và theo dõi lỗi', ['Chốt ngày thi, quỹ giờ thực tế và mục tiêu từng môn', 'Đề luyện bám phạm vi; chấm dựa trên bài nộp và thang điểm, không tự suy ra đáp án thiếu'], 'Bàn giao lịch khả thi, bảng lỗi và thay đổi lộ trình sau luyện đề; nêu việc cần làm ở buổi tiếp theo.'),
    'ngoai-ngu': ('Buổi luyện theo mục tiêu', ['Xác định trình độ và mục tiêu sử dụng tiếng Anh', 'Phân biệt câu gốc, câu sửa và giải thích; hội thoại chờ phản hồi người học'], 'Bàn giao bài sửa, từ vựng trong ngữ cảnh, lịch ôn và mục tiêu luyện tiếp; không tuyên bố đã đánh giá phát âm khi chỉ có văn bản.'),
    'viet-bai-nghien-cuu': ('Đề bài, bản nháp và nguồn', ['Chốt yêu cầu giảng viên, độ dài và chuẩn trích dẫn', 'Giữ luận điểm người viết, đánh dấu nguồn chưa xác minh và dữ kiện thiếu'], 'Bàn giao dàn ý hoặc bản góp ý, bảng nguồn có đường dẫn, danh sách việc tác giả cần hoàn thiện; không bịa tài liệu hoặc kết quả.'),
    'slide-thuyet-trinh': ('Bộ slide và kịch bản nói', ['Chốt người nghe, mục tiêu, thông điệp và thời lượng', 'Giữ đủ luận điểm và dữ liệu gốc, ghi nguồn biểu đồ; không thu nhỏ chữ để nhét nội dung'], 'Bàn giao PowerPoint, ghi chú diễn giả, kịch bản và câu hỏi phản biện theo quy trình; có phân bổ thời gian từng phần.'),
    'cv-viec-lam': ('Hồ sơ và mẫu CV đã chọn', ['Đối chiếu đủ từng kinh nghiệm, dự án và kỹ năng với form gốc', 'Biên tập câu chữ chuyên nghiệp nhưng giữ dữ kiện, số liệu và mục đã bỏ qua'], 'Bàn giao CV PDF/HTML, tóm tắt phần đã biên tập và các dữ kiện cần người dùng xác nhận; không tự nộp hồ sơ.'),
    'tai-chinh-ca-nhan': ('Ngân sách và giả định tính toán', ['Chốt kỳ, thu nhập ròng, chi cố định, nợ và mục tiêu', 'Tách dữ liệu thật khỏi giả định; không tự đoán lãi suất, phí hoặc thu nhập'], 'Bàn giao bảng tính có công thức, giả định và kịch bản, hướng dẫn cập nhật số thực tế; không tư vấn mua sản phẩm đầu tư cụ thể.'),
}


def enhance(aid, form):
    if aid not in CONTRACTS:
        return form
    form = deepcopy(form)
    title, checks, handoff = CONTRACTS[aid]
    form['experience'] = {'title': title, 'checks': checks, 'handoff': handoff}
    for flow in form['flows']:
        steps = flow['steps']
        for index, step in enumerate(steps):
            if index == 0:
                step['task'] += '\nTrước khi làm: ' + '; '.join(checks) + '. Gom câu hỏi thiếu dữ liệu một lần; dùng lại câu trả lời đã có, không hỏi lặp.'
            if step.get('produces'):
                step['task'] += '\nCHẤT LƯỢNG SẢN PHẨM: Chốt cấu trúc chi tiết theo yêu cầu trước khi xuất. Word/PDF phải viết đầy đủ các mục, có phân tích, căn cứ từ tài liệu, nhận định và hành động cụ thể khi nghiệp vụ yêu cầu; không chỉ vài dòng hoặc dàn ý trừ khi người dùng yêu cầu dàn ý. Excel phải đủ dòng nguồn, cột, đơn vị, công thức cần thiết, đối chiếu và hướng dẫn sử dụng; không giao bảng chỉ có tiêu đề. Không bịa số liệu/nguồn để làm dài. Sau xuất gọi review_deliverable với required_sections đã chốt và min_words phù hợp loại sản phẩm, sửa lỗi rồi kiểm lại; file chưa đạt phải báo là bản nháp cần bổ sung, không báo hoàn tất. Kiểm tra lại PDF sau chuyển đổi, không chỉ file nguồn.\nBảo toàn đầu vào: kiểm kê đủ tài liệu và các mục đã nhập; không bỏ nội dung, tự đổi số liệu hoặc ghi đè bản gốc. Chỉ báo đã tạo file sau khi công cụ trả thành công và có đường dẫn thật. Nêu nội dung đã thay đổi và điểm chưa kiểm chứng.'
            if index == len(steps) - 1:
                step['task'] += '\nBàn giao cuối: ' + handoff + ' Liệt kê rõ file thực sự đã tạo, phiên bản mới nhất, việc còn mở và bước tiếp theo. Không báo hoàn tất nếu sản phẩm được yêu cầu còn thiếu.'
    return form
