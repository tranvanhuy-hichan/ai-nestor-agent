"""Form chuc nang cho tung tro ly: moi tro ly la mot trang rieng tren thanh ben (Chuc nang).

FORMS[id] = {"intro": cau gioi thieu, "tasks": [tac vu], "panels": [ten panel dac biet]}
Mot tac vu = {"id", "label", "task" (cau mo dau gui cho tro ly), "fields": [truong nhap], "submit" (nhan nut)}.
Truong nhap = {"key", "label", "type": text|textarea|select|number|file, "required", "placeholder", "options", "accept", "multiple", "hint"}.
Trang chuc nang ghep: task + moi truong da dien thanh dong "- Nhan: gia tri"; file dinh kem duoc tai len phien truoc khi chay.
Tro ly khong co form rieng van co form chung (xem DEFAULT_FORM).
"""

KINDS = ("text", "textarea", "select", "number", "file", "cv-template", "cv-profile")
PANELS = ("exam-shuffle",)

_OFFICE = ".docx,.xlsx,.pptx,.pdf,.csv,.txt,.md"
_DOC = ".docx,.pdf,.txt,.md"
_SHEET = ".xlsx,.csv"


def text(key, label, ph="", req=False, hint=""):
    return {"key": key, "label": label, "type": "text", "required": req, "placeholder": ph, "hint": hint}


def area(key, label, ph="", req=False, hint=""):
    return {"key": key, "label": label, "type": "textarea", "required": req, "placeholder": ph, "hint": hint}


def sel(key, label, options, req=False, hint=""):
    return {"key": key, "label": label, "type": "select", "required": req, "options": list(options), "hint": hint}


def num(key, label, ph="", req=False, hint=""):
    return {"key": key, "label": label, "type": "number", "required": req, "placeholder": ph, "hint": hint}


def file(key, label, accept=_OFFICE, multiple=False, req=False, hint=""):
    return {"key": key, "label": label, "type": "file", "required": req, "accept": accept, "multiple": multiple, "hint": hint}


def task(id, label, task, fields, submit="Bắt đầu"):
    return {"id": id, "label": label, "task": task, "fields": fields, "submit": submit}


_NOTE = area("note", "Yêu cầu thêm", "Điều gì đặc biệt cần lưu ý? (không bắt buộc)")

DEFAULT_FORM = {
    "intro": "Mô tả việc bạn cần, có thể đính kèm tài liệu liên quan.",
    "tasks": [task("chung", "Giao việc", "Hãy giúp tôi việc sau.", [area("yeu_cau", "Bạn cần gì?", "Mô tả ngắn gọn kết quả bạn muốn nhận", True), file("tep", "Tài liệu đính kèm", multiple=True)], "Giao việc")],
    "panels": [],
}

FORMS: dict[str, dict] = {
    # ---------------- Cơ quan nhà nước ----------------
    "van-thu-nd30": {"intro": "Soạn văn bản hành chính đúng thể thức Nghị định 30/2020/NĐ-CP, rồi tự rà soát trước khi giao file Word.", "tasks": [
        task("soan", "Soạn văn bản", "Soạn một văn bản hành chính đúng thể thức NĐ 30/2020/NĐ-CP với thông tin sau.", [
            sel("loai", "Loại văn bản", ["Công văn", "Tờ trình", "Quyết định", "Báo cáo", "Thông báo", "Giấy mời", "Kế hoạch", "Biên bản"], True),
            text("co_quan", "Cơ quan ban hành", "VD: UBND phường An Phú", True), text("noi_nhan", "Gửi / Kính gửi", "VD: Sở Nội vụ"),
            text("trich_yeu", "Về việc (trích yếu)", "VD: xin kinh phí tổ chức hội nghị tổng kết năm", True),
            area("noi_dung", "Nội dung chính, căn cứ, số liệu", "Gạch đầu dòng các ý cần có", True), text("nguoi_ky", "Người ký, chức vụ", "VD: Chủ tịch UBND, ký TM."), file("tham_khao", "Văn bản tham khảo / căn cứ", multiple=True)], "Soạn văn bản"),
        task("sua", "Soạn lại từ bản nháp", "Đọc bản nháp đính kèm rồi trình bày lại đúng thể thức NĐ 30/2020/NĐ-CP, giữ nguyên ý.", [file("ban_nhap", "Bản nháp", _DOC, req=True), _NOTE], "Chuẩn hóa thể thức")]},
    "van-ban-dang-hd05": {"intro": "Soạn văn bản của cấp ủy đúng Hướng dẫn 05-HD/VPTW (thể thức khác văn bản hành chính).", "tasks": [
        task("soan", "Soạn văn bản Đảng", "Soạn văn bản của Đảng đúng Hướng dẫn 05-HD/VPTW với thông tin sau.", [
            sel("loai", "Loại văn bản", ["Nghị quyết", "Chỉ thị", "Kết luận", "Quy định", "Thông báo", "Báo cáo", "Kế hoạch", "Tờ trình"], True),
            text("cap_uy", "Tên cấp ủy / đảng bộ", "VD: Đảng bộ phường An Phú", True), text("trich_yeu", "Trích yếu / chuyên đề", "", True),
            area("noi_dung", "Nội dung, căn cứ, chỉ tiêu", "Gạch đầu dòng các ý cần có", True), text("nguoi_ky", "Người ký", "VD: T/M Ban Chấp hành, Bí thư"), file("tham_khao", "Tài liệu căn cứ", multiple=True)], "Soạn văn bản"),
        task("ra-soat", "Rà soát dự thảo", "Rà soát dự thảo văn bản Đảng đính kèm theo Hướng dẫn 05-HD/VPTW, nêu vị trí lỗi và đề xuất sửa.", [file("du_thao", "Dự thảo cần rà", _DOC, req=True), _NOTE], "Rà soát")]},
    "tong-hop-bao-cao": {"intro": "Gộp nhiều báo cáo thành bảng tổng hợp có công thức, chỉ ra chỗ vênh số liệu và đơn vị chưa nộp.", "tasks": [
        task("gop", "Gộp & đối chiếu", "Tổng hợp các báo cáo đính kèm thành một bảng và báo cáo chung.", [
            file("bao_cao", "Báo cáo của các đơn vị", _OFFICE, True, True, "Chọn nhiều file một lần"), file("mau", "Mẫu báo cáo chuẩn (nếu có)", _OFFICE),
            text("ky", "Kỳ báo cáo", "VD: Quý III/2026"), area("danh_sach", "Danh sách đơn vị phải nộp", "Mỗi đơn vị một dòng (để phát hiện đơn vị chưa nộp)"), _NOTE], "Tổng hợp")]},
    "ra-soat-the-thuc": {"intro": "Kiểm tra quốc hiệu, số ký hiệu, thẩm quyền ký, nơi nhận và nội dung trước khi trình ký.", "tasks": [
        task("ra-soat", "Rà soát văn bản", "Rà soát thể thức và nội dung văn bản đính kèm trước khi trình ký; nêu từng lỗi kèm vị trí và cách sửa.", [
            file("van_ban", "Văn bản cần rà", _DOC, True, True), sel("loai", "Chuẩn thể thức", ["Văn bản hành chính (NĐ 30/2020)", "Văn bản Đảng (HD 05)"]),
            sel("sua", "Sau khi rà", ["Chỉ lập báo cáo lỗi", "Lập báo cáo và xuất bản đã sửa (file mới)"])], "Rà soát")]},
    "bien-ban-hop": {"intro": "Biến ghi chú hoặc bản ghi âm đã gỡ băng thành biên bản hoàn chỉnh có kết luận và giao việc.", "tasks": [
        task("lap", "Lập biên bản", "Lập biên bản cuộc họp từ thông tin sau.", [
            text("cuoc_hop", "Tên cuộc họp", "VD: Họp giao ban tuần 46", True), text("thoi_gian", "Thời gian, địa điểm"), area("thanh_phan", "Thành phần tham dự", "Họ tên, chức vụ"),
            area("ghi_chu", "Ghi chú / nội dung đã trao đổi", "Dán ghi chú thô vào đây", False), file("tep", "Hoặc tải ghi chú / bản gỡ băng", _DOC, True), sel("co_quan", "Thể thức", ["Cơ quan nhà nước (NĐ 30)", "Doanh nghiệp / tổ chức"])], "Lập biên bản")]},
    "van-thu-den-di": {"intro": "Tóm tắt, phân loại văn bản đến, theo dõi hạn và cảnh báo văn bản quá hạn.", "tasks": [
        task("den", "Xử lý văn bản đến", "Tóm tắt và phân loại các văn bản đến đính kèm, xác định hạn xử lý và lập sổ theo dõi.", [file("van_ban", "Các văn bản đến", _OFFICE, True, True), file("so", "Sổ theo dõi hiện có (nếu có)", _SHEET), text("don_vi", "Đơn vị tiếp nhận / người xử lý")], "Phân loại"),
        task("quahan", "Cảnh báo quá hạn", "Đọc sổ theo dõi văn bản đính kèm, liệt kê văn bản sắp và đã quá hạn, soạn công văn đôn đốc nếu cần.", [file("so", "Sổ theo dõi", _SHEET, req=True), _NOTE], "Kiểm tra hạn")]},
    "chuan-hoa-sau-sap-nhap": {"intro": "Cập nhật tên đơn vị, địa danh, thẩm quyền sau sắp xếp chính quyền hai cấp (từ 01/7/2025).", "tasks": [
        task("chuan", "Chuẩn hóa văn bản", "Rà văn bản đính kèm, phát hiện tên đơn vị, địa danh, thẩm quyền cũ và đề xuất bảng đối chiếu cũ - mới.", [
            file("van_ban", "Văn bản / bảng dữ liệu", _OFFICE, True, True), file("bang_doi_chieu", "Bảng đối chiếu cũ - mới của địa phương", _SHEET),
            sel("che_do", "Chế độ", ["Chỉ liệt kê chỗ cần đổi", "Liệt kê và xuất bản đã chỉnh (file mới)"])], "Chuẩn hóa")]},
    "dau-tu-cong": {"intro": "Soạn, thẩm tra và trích xuất dữ liệu hồ sơ đầu tư công cấp xã/phường.", "tasks": [
        task("tham-tra", "Thẩm tra hồ sơ", "Thẩm tra hồ sơ đầu tư công đính kèm: kiểm tra dự toán bằng số tính lại và liệt kê điểm cần kiểm chứng.", [file("ho_so", "Hồ sơ / dự toán", _OFFICE, True, True), text("du_an", "Tên dự án"), _NOTE], "Thẩm tra"),
        task("soan", "Soạn văn bản", "Soạn văn bản đầu tư công theo thông tin sau.", [text("loai", "Loại văn bản", "VD: tờ trình chủ trương đầu tư", req=True), text("du_an", "Tên dự án", req=True), area("noi_dung", "Thông tin, số liệu chính", req=True), file("tham_khao", "Tài liệu căn cứ", multiple=True)], "Soạn văn bản")]},
    "phap-che": {"intro": "Rà hợp đồng, quy chế, dự thảo văn bản; liệt kê rủi ro kèm đề xuất sửa. Chỉ mang tính tham khảo.", "tasks": [
        task("ra-soat", "Rà soát văn bản", "Rà soát văn bản đính kèm, liệt kê điều khoản rủi ro, thiếu căn cứ, mâu thuẫn và đề xuất sửa.", [
            file("van_ban", "Hợp đồng / quy chế / dự thảo", _DOC, True, True), sel("goc_nhin", "Bạn đứng ở phía", ["Bên A / cơ quan ban hành", "Bên B / bên nhận", "Trung lập"]), area("lo_ngai", "Điều bạn lo ngại nhất", "VD: phạt vi phạm, thanh toán, chấm dứt hợp đồng")], "Rà soát"),
        task("tra-loi", "Soạn công văn trả lời", "Soạn công văn trả lời theo thông tin sau, có căn cứ pháp lý nếu tìm thấy trong kho tài liệu.", [area("van_de", "Nội dung kiến nghị / vấn đề", req=True), file("tai_lieu", "Văn bản liên quan", multiple=True)], "Soạn trả lời")]},
    # ---------------- Doanh nghiệp ----------------
    "thu-ky": {"intro": "Tóm tắt thư, soạn thư trả lời, chuẩn bị chương trình họp và sắp lịch. Không tự gửi.", "tasks": [
        task("thu", "Soạn thư trả lời", "Soạn thư trả lời lịch sự, đúng ngữ cảnh.", [area("thu_den", "Nội dung thư cần trả lời", "Dán thư vào đây", True), sel("y_dinh", "Ý định trả lời", ["Đồng ý", "Từ chối lịch sự", "Xin lùi / đổi lịch", "Hỏi thêm thông tin", "Tùy bạn đề xuất"]), sel("giong", "Giọng văn", ["Trang trọng", "Thân thiện", "Ngắn gọn"])], "Soạn thư"),
        task("hop", "Chuẩn bị cuộc họp", "Lập chương trình họp và tài liệu chuẩn bị.", [text("cuoc_hop", "Cuộc họp", "VD: họp kế hoạch quý IV", True), area("noi_dung", "Nội dung cần bàn"), text("thoi_luong", "Thời lượng, thành phần")], "Lập chương trình"),
        task("tom-tat", "Tóm tắt thư / tài liệu", "Tóm tắt các thư hoặc tài liệu sau và liệt kê việc cần làm kèm hạn.", [area("noi_dung", "Dán nội dung thư"), file("tep", "Hoặc tải tài liệu", _DOC, True)], "Tóm tắt")]},
    "ke-toan": {"intro": "Bảng tính có công thức sống, đối chiếu số liệu, báo cáo tổng hợp và biểu đồ.", "tasks": [
        task("lap-bang", "Lập bảng tính", "Lập bảng tính Excel có công thức theo yêu cầu sau.", [text("muc_dich", "Bảng dùng để làm gì", "VD: theo dõi công nợ phải thu", True), area("cot", "Các cột / chỉ tiêu cần có"), file("du_lieu", "Dữ liệu có sẵn", _SHEET), sel("bieu_do", "Biểu đồ", ["Không cần", "Có biểu đồ tổng hợp"])], "Lập bảng"),
        task("doi-chieu", "Đối chiếu số liệu", "Đối chiếu hai bảng đính kèm và liệt kê dòng lệch.", [file("bang_a", "Bảng thứ nhất (sổ A)", _SHEET, req=True), file("bang_b", "Bảng thứ hai (sổ B)", _SHEET, req=True), text("khoa", "Cột khóa đối chiếu", "VD: Mã hóa đơn"), text("dung_sai", "Sai lệch chấp nhận được", "VD: 0")], "Đối chiếu"),
        task("lam-sach", "Làm sạch dữ liệu", "Làm sạch bảng dữ liệu đính kèm (trùng lặp, định dạng, ô trống) và tóm tắt thay đổi.", [file("du_lieu", "Bảng cần làm sạch", _SHEET, req=True), _NOTE], "Làm sạch")]},
    "nhan-su": {"intro": "Tin tuyển dụng, mô tả công việc, hợp đồng và biểu mẫu từ mẫu, quy chế, tài liệu onboarding.", "tasks": [
        task("tuyen-dung", "Tin tuyển dụng / JD", "Soạn mô tả công việc và tin tuyển dụng.", [text("vi_tri", "Vị trí", req=True), area("yeu_cau", "Yêu cầu, quyền lợi, mức lương"), text("dia_diem", "Địa điểm làm việc")], "Soạn tin"),
        task("hop-dong", "Sinh hợp đồng hàng loạt", "Sinh hợp đồng/biểu mẫu hàng loạt từ mẫu và bảng danh sách đính kèm, rồi báo cáo số lượng.", [file("mau", "Mẫu hợp đồng (.docx có chỗ điền)", ".docx", req=True), file("danh_sach", "Bảng danh sách nhân viên", _SHEET, req=True)], "Sinh hợp đồng"),
        task("quy-che", "Quy chế / onboarding", "Soạn tài liệu theo yêu cầu sau.", [text("loai", "Tài liệu", "VD: quy chế làm việc từ xa", req=True), area("yeu_cau", "Quy định muốn có")], "Soạn tài liệu")]},
    "kinh-doanh-marketing": {"intro": "Hồ sơ năng lực, pitch deck, báo giá, bài đăng truyền thông.", "tasks": [
        task("slide", "Bộ slide / hồ sơ năng lực", "Làm bộ slide theo thông tin sau (mỗi slide một ý, có ghi chú diễn giả).", [text("chu_de", "Chủ đề", "VD: giới thiệu công ty", True), text("doi_tuong", "Khán giả, mục tiêu", req=True), num("so_slide", "Số slide", "10"), area("du_kien", "Dữ kiện, số liệu có sẵn"), file("tai_lieu", "Tài liệu tham khảo", multiple=True)], "Làm slide"),
        task("bai-dang", "Bài đăng & kế hoạch nội dung", "Soạn nội dung truyền thông theo thông tin sau.", [text("kenh", "Kênh", "Facebook, Zalo OA, email…", True), text("thong_diep", "Thông điệp / sản phẩm", req=True), sel("giong", "Giọng văn", ["Chuyên nghiệp", "Thân thiện", "Sôi nổi"])], "Soạn nội dung"),
        task("bao-gia", "Đề xuất báo giá", "Soạn đề xuất báo giá cho khách hàng.", [text("khach", "Khách hàng", req=True), area("hang_muc", "Hạng mục, số lượng, đơn giá", req=True)], "Soạn báo giá")]},
    "quan-ly-du-an": {"intro": "Chia việc, lập kế hoạch Gantt, theo dõi tiến độ và rủi ro, báo cáo định kỳ.", "tasks": [
        task("ke-hoach", "Lập kế hoạch dự án", "Lập kế hoạch dự án bằng Excel (Gantt, người phụ trách, mốc) theo thông tin sau.", [text("du_an", "Dự án", req=True), text("thoi_gian", "Thời gian thực hiện", "VD: 3 tháng, bắt đầu 01/12", True), area("muc_tieu", "Mục tiêu, phạm vi, nguồn lực", req=True)], "Lập kế hoạch"),
        task("bao-cao", "Báo cáo tiến độ", "Soạn báo cáo tiến độ định kỳ từ kế hoạch đính kèm.", [file("ke_hoach", "Kế hoạch hiện tại", _SHEET, req=True), area("cap_nhat", "Cập nhật tuần này"), sel("ky", "Kỳ báo cáo", ["Tuần", "Tháng"])], "Soạn báo cáo"),
        task("rui-ro", "Bảng rủi ro", "Lập bảng rủi ro và biện pháp giảm thiểu.", [area("du_an", "Mô tả dự án", req=True)], "Lập bảng rủi ro")]},
    "cham-soc-khach-hang": {"intro": "Soạn phản hồi khách hàng theo chính sách, phân loại và tổng hợp phản hồi.", "tasks": [
        task("phan-hoi", "Trả lời khách hàng", "Soạn phản hồi cho khách hàng, đúng chính sách, giọng đồng cảm.", [area("khieu_nai", "Tin nhắn / khiếu nại của khách", req=True), file("chinh_sach", "Chính sách áp dụng", _DOC), sel("giong", "Giọng điệu", ["Đồng cảm, nhẹ nhàng", "Chuyên nghiệp", "Ngắn gọn"])], "Soạn phản hồi"),
        task("tong-hop", "Tổng hợp phản hồi", "Phân loại và tổng hợp danh sách phản hồi đính kèm, rút ra vấn đề lặp lại.", [file("phan_hoi", "Bảng / file phản hồi", _OFFICE, req=True)], "Tổng hợp"),
        task("faq", "Soạn FAQ", "Soạn bản nháp câu hỏi thường gặp.", [area("san_pham", "Sản phẩm / dịch vụ và các câu khách hay hỏi", req=True)], "Soạn FAQ")]},
    "mua-sam-dau-thau": {"intro": "So sánh báo giá, kiểm tra hồ sơ dự thầu, lập checklist và bảng đối chiếu.", "tasks": [
        task("so-sanh", "So sánh báo giá", "So sánh các báo giá đính kèm theo cùng tiêu chí và nêu điểm cần làm rõ.", [file("bao_gia", "Các báo giá", _OFFICE, True, True), area("tieu_chi", "Tiêu chí ưu tiên", "VD: giá, bảo hành, tiến độ")], "So sánh"),
        task("ho-so", "Kiểm tra hồ sơ", "Lập checklist và kiểm tra hồ sơ dự thầu đính kèm.", [file("ho_so", "Hồ sơ dự thầu", _OFFICE, True, True), file("yeu_cau", "Yêu cầu hồ sơ mời thầu", _DOC)], "Kiểm tra")]},
    "it": {"intro": "Viết và chạy script xử lý dữ liệu hàng loạt, soạn tài liệu kỹ thuật. Kết quả giải thích bằng lời dễ hiểu.", "tasks": [
        task("script", "Xử lý hàng loạt", "Viết và chạy script để làm việc sau, rồi báo cáo kết quả.", [area("viec", "Việc cần tự động hóa", "VD: đổi tên 600 file scan theo mẫu", True), file("du_lieu", "Dữ liệu / file mẫu", multiple=True)], "Chạy"),
        task("tai-lieu", "Tài liệu kỹ thuật", "Soạn tài liệu kỹ thuật theo yêu cầu sau.", [text("loai", "Loại tài liệu", "SRS, thiết kế CSDL, hướng dẫn…", True), area("mo_ta", "Mô tả hệ thống", req=True)], "Soạn tài liệu")]},
    # ---------------- Giáo viên ----------------
    "giao-an": {"intro": "Soạn kế hoạch bài dạy theo GDPT 2018, phiếu học tập, rubric và slide bài giảng.", "tasks": [
        task("giao-an", "Soạn giáo án", "Soạn kế hoạch bài dạy theo chương trình GDPT 2018 (4 hoạt động, đánh giá).", [
            text("mon", "Môn", req=True), text("lop", "Lớp", req=True), text("bai", "Tên bài", req=True), text("bo_sach", "Bộ sách", "Kết nối tri thức / Chân trời sáng tạo / Cánh diều"), num("so_tiet", "Số tiết", "1"), area("ghi_chu", "Đặc điểm lớp, phương pháp muốn dùng"), file("tai_lieu", "Tài liệu / sách giáo khoa", multiple=True)], "Soạn giáo án"),
        task("phieu", "Phiếu học tập", "Thiết kế phiếu học tập cho bài sau.", [text("mon", "Môn, lớp", req=True), text("bai", "Tên bài", req=True), sel("hinh_thuc", "Hình thức", ["Cá nhân", "Nhóm", "Trò chơi"])], "Tạo phiếu"),
        task("slide", "Slide bài giảng", "Làm slide bài giảng cho bài sau.", [text("mon", "Môn, lớp", req=True), text("bai", "Tên bài", req=True), num("so_slide", "Số slide", "12")], "Làm slide")]},
    "ra-de-cham-bai": {"intro": "Ra đề theo ma trận, tạo nhiều mã đề từ đề trắc nghiệm, tổng hợp điểm lớp có xếp loại.", "tasks": [
        task("ra-de", "Ra đề và ma trận", "Lập ma trận, bảng đặc tả, đề, đáp án và thang điểm.", [
            text("mon", "Môn", req=True), text("lop", "Lớp", req=True), num("thoi_gian", "Thời gian (phút)", "45", True), sel("hinh_thuc", "Hình thức", ["Trắc nghiệm", "Tự luận", "Kết hợp 70% TN - 30% TL", "Kết hợp 50% - 50%"]), area("pham_vi", "Phạm vi nội dung", "Chương/bài", True), text("ti_le", "Tỉ lệ mức độ", "Mặc định 40-30-20-10"), file("tham_khao", "Đề cương / ma trận cũ", multiple=True)], "Ra đề"),
        task("bang-diem", "Tổng hợp điểm lớp", "Tổng hợp điểm lớp từ bảng đính kèm, tính trung bình theo hệ số và xếp loại.", [file("bang_diem", "Bảng điểm (Excel)", _SHEET, req=True), text("he_so", "Hệ số", "VD: thường xuyên 1, giữa kỳ 2, cuối kỳ 3")], "Tổng hợp"),
    ], "panels": ["exam-shuffle"]},
    "chu-nhiem-lop": {"intro": "Nhận xét học bạ khác nhau cho từng em, thư và kế hoạch họp phụ huynh, in hàng loạt từ mẫu trường.", "tasks": [
        task("nhan-xet", "Nhận xét học bạ", "Viết nhận xét học bạ riêng cho từng học sinh trong danh sách đính kèm, mỗi em một nhận xét khác nhau.", [file("danh_sach", "Danh sách + điểm + ghi chú từng em", _SHEET, req=True), file("mau", "Mẫu nhận xét của trường", _DOC), sel("hoc_ky", "Kỳ", ["Giữa học kỳ I", "Cuối học kỳ I", "Giữa học kỳ II", "Cả năm"])], "Viết nhận xét"),
        task("phu-huynh", "Họp phụ huynh", "Soạn thư mời, kế hoạch và biên bản mẫu họp phụ huynh.", [text("lop", "Lớp", req=True), text("thoi_gian", "Thời gian, địa điểm", req=True), area("noi_dung", "Nội dung cần thông báo")], "Soạn tài liệu")]},
    "giang-vien-dai-hoc": {"intro": "Đề cương học phần với CLO đo được, bài giảng, rubric 4 mức, đề thi khớp chuẩn đầu ra.", "tasks": [
        task("de-cuong", "Đề cương học phần", "Soạn đề cương học phần với chuẩn đầu ra (CLO) đo được.", [text("hoc_phan", "Học phần", req=True), text("nganh", "Ngành, số tín chỉ", req=True), area("noi_dung", "Nội dung, tài liệu chính"), file("mau", "Mẫu đề cương của trường", _DOC)], "Soạn đề cương"),
        task("rubric", "Rubric chấm", "Lập rubric 4 mức cho bài sau.", [text("bai", "Bài tập / đồ án cần chấm", req=True), area("clo", "CLO cần đo")], "Lập rubric"),
        task("bai-giang", "Bài giảng & đề thi", "Soạn bài giảng (slide) hoặc đề thi khớp CLO.", [sel("loai", "Cần", ["Slide bài giảng", "Đề thi và đáp án"], True), text("chu_de", "Chủ đề / chương", req=True), area("clo", "CLO liên quan")], "Soạn")]},
    # ---------------- Học sinh ----------------
    "gia-su": {"intro": "Giảng từng bước, giải mẫu, chữa bài làm sai và cho bài tự luyện kèm đáp án (mọi môn).", "tasks": [
        task("giang", "Giảng bài", "Giảng cho em hiểu bài này từng bước, hỏi lại để biết em hiểu đến đâu.", [text("mon", "Môn, lớp", req=True), text("bai", "Bài / khái niệm em chưa hiểu", req=True), area("da_hieu", "Em đã hiểu đến đâu?")], "Giảng cho em"),
        task("chua-bai", "Chữa bài của em", "Chữa bài làm sau của em: chỉ chỗ sai, giải thích vì sao, rồi cho bài tương tự.", [file("bai_lam", "Ảnh/File bài làm", ".png,.jpg,.jpeg,.pdf,.docx", req=True), text("mon", "Môn, lớp")], "Chữa bài")]},
    "on-thi": {"intro": "Lập lịch ôn theo số ngày còn lại, ra đề luyện đúng cấu trúc, chấm và lập bảng lỗi sai.", "tasks": [
        task("lo-trinh", "Lập lộ trình ôn", "Lập lộ trình ôn thi theo thông tin sau.", [text("ky_thi", "Kỳ thi", "VD: vào lớp 10", True), text("ngay_thi", "Ngày thi hoặc số ngày còn lại", req=True), text("mon", "Các môn cần ôn", req=True), area("diem_yeu", "Phần em yếu"), text("gio_hoc", "Số giờ học mỗi ngày")], "Lập lộ trình"),
        task("luyen-de", "Luyện đề", "Ra đề luyện tập kèm đáp án theo thông tin sau.", [text("mon", "Môn, lớp", req=True), text("pham_vi", "Phạm vi", req=True), num("so_cau", "Số câu", "15"), sel("muc", "Mức độ", ["Cơ bản", "Vừa", "Nâng cao"])], "Ra đề"),
        task("cham", "Chấm bài & lỗi sai", "Chấm bài làm đính kèm, lập bảng lỗi sai và cách khắc phục.", [file("bai_lam", "Bài làm của em", ".png,.jpg,.jpeg,.pdf,.docx", req=True), file("dap_an", "Đề / đáp án (nếu có)", _DOC)], "Chấm bài")]},
    "ngoai-ngu": {"intro": "Luyện tiếng Anh theo trình độ: sửa lỗi có giải thích, hội thoại, từ vựng có lịch ôn.", "tasks": [
        task("sua-bai", "Sửa bài viết", "Sửa đoạn văn sau, giải thích từng lỗi nhẹ nhàng.", [area("bai_viet", "Đoạn văn của bạn", req=True), sel("trinh_do", "Trình độ", ["A1-A2", "B1", "B2", "C1"])], "Sửa bài"),
        task("hoi-thoai", "Luyện hội thoại", "Đóng vai đối tác để luyện hội thoại theo tình huống sau, sửa lỗi sau mỗi lượt.", [text("tinh_huong", "Tình huống", "VD: phỏng vấn xin việc", True), sel("trinh_do", "Trình độ", ["A1-A2", "B1", "B2", "C1"])], "Bắt đầu luyện"),
        task("tu-vung", "Học từ vựng", "Lập danh sách từ vựng kèm ví dụ và lịch ôn.", [text("chu_de", "Chủ đề", "VD: du lịch", True), num("so_tu", "Số từ", "30")], "Lập danh sách")]},
    "gia-su-toan": {"intro": "Giải Toán từng dòng có căn cứ, kiểm tra nghiệm bằng tính toán, chỉ lỗi sai và cho bài luyện tương tự.", "tasks": [
        task("giai", "Giải bài Toán", "Hướng dẫn em giải bài Toán sau từng bước, kiểm tra lại đáp án bằng tính toán.", [area("de_bai", "Đề bài", "Gõ đề hoặc đính kèm ảnh", False), file("anh", "Ảnh đề bài", ".png,.jpg,.jpeg,.pdf"), text("lop", "Lớp"), sel("che_do", "Em muốn", ["Gợi ý từng bước, em tự làm", "Xem lời giải đầy đủ"])], "Giải bài")]},
    "gia-su-van": {"intro": "Phân tích đề, lập dàn ý, góp ý bài văn kèm gợi ý sửa; không viết hộ bài nộp.", "tasks": [
        task("de", "Phân tích đề, lập dàn ý", "Phân tích đề và hướng dẫn em lập dàn ý.", [area("de_bai", "Đề bài", req=True), text("lop", "Lớp"), sel("kieu", "Kiểu bài", ["Nghị luận xã hội", "Nghị luận văn học", "Tự sự", "Miêu tả", "Thuyết minh"])], "Lập dàn ý"),
        task("gop-y", "Góp ý bài viết", "Góp ý bài văn sau của em, nêu điểm mạnh, điểm cần sửa và gợi ý cụ thể (không viết hộ).", [area("bai", "Bài viết của em", req=True), file("tep", "Hoặc tải bài", _DOC), text("de_bai", "Đề bài")], "Góp ý")]},
    "gia-su-khtn": {"intro": "Giải thích hiện tượng và giải bài Lý, Hóa, Sinh có đơn vị đầy đủ, kiểm tra bảo toàn.", "tasks": [
        task("giai", "Giải bài / giải thích", "Giải thích và hướng dẫn giải bài sau có đơn vị đầy đủ.", [sel("mon", "Môn", ["Vật lý", "Hóa học", "Sinh học"], True), text("lop", "Lớp"), area("de_bai", "Đề bài / hiện tượng", "Gõ đề hoặc đính kèm ảnh"), file("anh", "Ảnh đề bài", ".png,.jpg,.jpeg,.pdf")], "Giải bài")]},
    # ---------------- Sinh viên ----------------
    "viet-bai-nghien-cuu": {"intro": "Dàn ý, tóm tắt tài liệu, góp ý bài viết và chuẩn trích dẫn. Bạn vẫn tự viết bài của mình.", "tasks": [
        task("dan-y", "Lập dàn ý", "Lập dàn ý chi tiết cho bài sau.", [text("de_tai", "Đề tài", req=True), sel("loai", "Loại bài", ["Tiểu luận", "Báo cáo thực tập", "Khóa luận", "Bài báo"]), num("so_trang", "Số trang dự kiến"), area("yeu_cau", "Yêu cầu của giảng viên")], "Lập dàn ý"),
        task("tom-tat", "Tóm tắt tài liệu", "Tóm tắt các tài liệu đính kèm thành bảng so sánh.", [file("tai_lieu", "Các bài báo / tài liệu", _OFFICE, True, True), text("cau_hoi", "Câu hỏi bạn đang tìm câu trả lời")], "Tóm tắt"),
        task("gop-y", "Góp ý bài viết", "Rà bố cục, lập luận và trích dẫn bài đính kèm, góp ý cụ thể.", [file("bai", "Bài viết", _DOC, req=True), sel("chuan", "Chuẩn trích dẫn", ["APA", "IEEE", "Harvard", "Theo quy định trường"])], "Góp ý")]},
    "slide-thuyet-trinh": {"intro": "Bộ slide gọn theo thời lượng, ghi chú diễn giả và câu hỏi phản biện kèm gợi ý trả lời.", "tasks": [
        task("slide", "Làm slide", "Làm bộ slide gọn (mỗi slide một ý, có ghi chú diễn giả).", [text("chu_de", "Chủ đề", req=True), num("thoi_luong", "Thời lượng (phút)", "10", True), text("khan_gia", "Khán giả", "Hội đồng, lớp, khách hàng…"), file("noi_dung", "Bài viết / báo cáo gốc", _DOC)], "Làm slide"),
        task("phan-bien", "Câu hỏi phản biện", "Đặt câu hỏi phản biện có thể gặp và gợi ý trả lời cho bài trình bày đính kèm.", [file("bai", "Slide hoặc báo cáo", _OFFICE, req=True)], "Tạo câu hỏi")]},
    "cv-viec-lam": {"intro": "CV một trang, thư xin việc dưới 250 từ và phỏng vấn thử. Chỉ dùng thông tin thật của bạn.", "tasks": [
        task("cv", "Viết CV", "Viết CV một trang nhấn vào kết quả, dùng đúng thông tin tôi cung cấp.", [text("vi_tri", "Vị trí ứng tuyển", req=True), area("thong_tin", "Học vấn, kinh nghiệm, kỹ năng, dự án", req=True), file("cv_cu", "CV cũ (nếu có)", _DOC), file("jd", "Mô tả công việc (JD)", _DOC)], "Viết CV"),
        task("thu", "Thư xin việc", "Viết thư xin việc dưới 250 từ.", [text("vi_tri", "Vị trí", req=True), text("cong_ty", "Công ty"), area("thong_tin", "Điểm mạnh muốn nhấn", req=True)], "Viết thư"),
        task("phong-van", "Phỏng vấn thử", "Phỏng vấn thử tôi từng câu một và nhận xét sau mỗi câu trả lời.", [text("vi_tri", "Vị trí", req=True), sel("muc", "Mức độ", ["Thực tập sinh", "Nhân viên", "Quản lý"])], "Bắt đầu phỏng vấn")]},
    "nghien-cuu-khoa-hoc": {"intro": "Từ ý tưởng đến báo cáo: câu hỏi nghiên cứu, phương pháp, phân tích số liệu thật, biểu đồ và slide bảo vệ.", "tasks": [
        task("de-cuong", "Đề cương nghiên cứu", "Lập đề cương nghiên cứu từ ý tưởng sau.", [text("y_tuong", "Ý tưởng / đề tài", req=True), text("nganh", "Ngành, cấp độ", "VD: sinh viên năm 4, kinh tế"), area("rang_buoc", "Thời gian, nguồn dữ liệu có thể có")], "Lập đề cương"),
        task("phan-tich", "Phân tích số liệu", "Phân tích số liệu đính kèm bằng script, vẽ biểu đồ và diễn giải kết quả.", [file("du_lieu", "Dữ liệu khảo sát", _SHEET, req=True), text("gia_thuyet", "Giả thuyết / câu hỏi", req=True)], "Phân tích")]},
    # ---------------- Cá nhân ----------------
    "tro-ly-ca-nhan": {"intro": "Kế hoạch tuần có thời gian đệm, danh sách việc theo ưu tiên, bản nháp thư và tin nhắn. Không tự gửi.", "tasks": [
        task("ke-hoach", "Lập kế hoạch tuần", "Lập kế hoạch tuần có thời gian đệm theo thông tin sau.", [area("viec", "Việc cần làm, hạn chót", req=True), area("co_dinh", "Lịch cố định (họp, học, đưa đón…)"), text("gio_ranh", "Khung giờ làm việc", "VD: 8h-17h")], "Lập kế hoạch"),
        task("soan", "Soạn thư / tin nhắn", "Soạn bản nháp thư hoặc tin nhắn.", [area("noi_dung", "Cần nói gì, với ai", req=True), sel("giong", "Giọng văn", ["Lịch sự", "Thân mật", "Ngắn gọn"])], "Soạn")]},
    "tai-chinh-ca-nhan": {"intro": "Ngân sách tháng, bảng theo dõi chi tiêu có công thức, kế hoạch tiết kiệm. Không tư vấn đầu tư cụ thể.", "tasks": [
        task("ngan-sach", "Lập ngân sách tháng", "Lập bảng ngân sách và theo dõi chi tiêu Excel có công thức.", [text("thu_nhap", "Thu nhập hàng tháng", req=True), area("chi_phi", "Các khoản chi cố định", "Tiền nhà, điện nước, học phí…"), text("muc_tieu", "Mục tiêu", "VD: tiết kiệm 20%")], "Lập ngân sách"),
        task("tiet-kiem", "Kế hoạch tiết kiệm / trả nợ", "Lập kế hoạch tiết kiệm hoặc trả nợ theo thông tin sau.", [text("muc_tieu", "Mục tiêu và số tiền", req=True), text("thoi_han", "Thời hạn"), area("hien_trang", "Tình hình hiện tại")], "Lập kế hoạch"),
        task("phan-tich", "Phân tích chi tiêu", "Phân loại và phân tích bảng chi tiêu đính kèm, chỉ ra khoản có thể cắt giảm.", [file("chi_tieu", "Sao kê / bảng chi tiêu", _SHEET, req=True)], "Phân tích")]},
    "du-lich": {"intro": "Lịch trình theo ngày có giờ, di chuyển, dự phòng mưa và bảng ngân sách. Giá, giờ mở cửa luôn cần xác nhận lại.", "tasks": [
        task("lich-trinh", "Lập lịch trình", "Lập lịch trình du lịch theo ngày có giờ giấc và phương án dự phòng.", [text("diem_den", "Điểm đến", req=True), num("so_ngay", "Số ngày", "3", True), text("so_nguoi", "Số người, độ tuổi", "VD: 2 người lớn, 1 bé 5 tuổi"), text("ngan_sach", "Ngân sách"), area("so_thich", "Sở thích, điều cần tránh"), text("khoi_hanh", "Đi từ đâu, khi nào")], "Lập lịch trình")]},
    "phap-ly-doi-thuong": {"intro": "Giải thích quy định bằng lời dễ hiểu, soạn đơn từ cơ bản. Điều luật đều ghi nguồn hoặc cần kiểm chứng.", "tasks": [
        task("giai-thich", "Hỏi về quy định", "Giải thích dễ hiểu tình huống pháp lý sau, nêu căn cứ và các bước tiếp theo.", [area("tinh_huong", "Tình huống của bạn", req=True), text("dia_phuong", "Tỉnh/thành")], "Giải thích"),
        task("don-tu", "Soạn đơn / thư", "Soạn đơn từ theo thông tin sau.", [text("loai", "Loại đơn", "VD: đơn khiếu nại, đơn xin cấp lại giấy tờ", True), area("noi_dung", "Thông tin cần đưa vào", req=True)], "Soạn đơn")]},
    "viet-sang-tao": {"intro": "Ý tưởng, hồ sơ nhân vật, dàn ý cốt truyện và góp ý bản thảo, giữ giọng văn của bạn.", "tasks": [
        task("y-tuong", "Ý tưởng & dàn ý", "Phát triển ý tưởng thành dàn ý cốt truyện và hồ sơ nhân vật.", [text("the_loai", "Thể loại", req=True), area("y_tuong", "Ý tưởng của bạn", req=True)], "Phát triển"),
        task("gop-y", "Góp ý bản thảo", "Góp ý bản thảo đính kèm cụ thể, giữ giọng văn của tôi.", [file("ban_thao", "Bản thảo", _DOC, req=True), area("lo_ngai", "Bạn muốn góp ý về điều gì?")], "Góp ý")]},
    "suc-khoe-dinh-duong": {"intro": "Thực đơn tuần món Việt vừa ngân sách, danh sách đi chợ, bảng thói quen. Không chẩn đoán, không kê đơn.", "tasks": [
        task("thuc-don", "Thực đơn tuần", "Lập thực đơn tuần món Việt kèm danh sách đi chợ.", [num("so_nguoi", "Số người ăn", "2", True), text("ngan_sach", "Ngân sách mỗi ngày"), area("han_che", "Dị ứng, món không ăn, mục tiêu"), text("thoi_gian", "Thời gian nấu mỗi bữa")], "Lập thực đơn"),
        task("thoi-quen", "Bảng thói quen", "Lập bảng nhật ký theo dõi thói quen.", [text("thoi_quen", "Thói quen muốn xây", "VD: ngủ trước 23h, uống đủ nước", True)], "Lập bảng")]},
}


def step(id, label, goal, task, fields=(), review=(), produces=(), submit="Chạy bước này", optional=False):
    """Mot buoc cua quy trinh nghiep vu: muc tieu, cau lenh giao cho tro ly, o nhap, tieu chi nguoi dung duyet va loai file tao ra."""
    return {"id": id, "label": label, "goal": goal, "task": task, "fields": list(fields), "review": list(review), "produces": list(produces),
            "submit": submit, "optional": optional}


def flow(id, label, desc, steps):
    return {"id": id, "label": label, "desc": desc, "steps": list(steps)}


def _as_flows(form: dict) -> dict:
    """Form kieu cu (tasks = moi tac vu mot buoc) -> flows (moi tac vu la mot quy trinh mot buoc)."""
    if "flows" in form:
        return form
    flows = [flow(t["id"], t["label"], t["task"], [step(t["id"], t["label"], t["task"], t["task"], t["fields"], (), (), t.get("submit") or "Bắt đầu")]) for t in form.get("tasks") or []]
    return {"intro": form.get("intro", ""), "flows": flows, "panels": list(form.get("panels") or [])}


def _load_flows() -> None:
    """Quy trinh nghiep vu theo nhom (flows_*.py, moi file co FLOWS = {id: form}); thieu file thi dung form don gian o tren."""
    import importlib
    for m in ("flows_gov", "flows_biz", "flows_teacher", "flows_student", "flows_uni", "flows_personal"):
        try:
            FORMS.update(importlib.import_module(f".{m}", __package__).FLOWS)
        except ModuleNotFoundError as e:
            if not (e.name or "").endswith(m):
                raise


_load_flows()


def form_for(aid: str) -> dict:
    return _as_flows(FORMS.get(aid) or DEFAULT_FORM)


def validate_form(aid: str, form: dict) -> list[str]:
    form = _as_flows(form)
    errs = []
    flows = form.get("flows") or []
    if not flows and not form.get("panels"):
        errs.append(f"{aid}: khong co quy trinh")
    fids = set()
    for fl in flows:
        fid = fl.get("id")
        if not fid or fid in fids:
            errs.append(f"{aid}: quy trinh thieu/trung id '{fid}'")
        fids.add(fid)
        if not fl.get("label") or not fl.get("desc"):
            errs.append(f"{aid}/{fid}: thieu label/desc")
        steps = fl.get("steps") or []
        if not steps:
            errs.append(f"{aid}/{fid}: khong co buoc")
        sids = set()
        for n, st in enumerate(steps):
            sid = st.get("id")
            where = f"{aid}/{fid}/{sid}"
            if not sid or sid in sids:
                errs.append(f"{where}: buoc thieu/trung id")
            sids.add(sid)
            for k in ("label", "goal", "task"):
                if not str(st.get(k) or "").strip():
                    errs.append(f"{where}: thieu {k}")
            if n == 0 and not st.get("fields"):
                errs.append(f"{where}: buoc dau phai co o nhap")
            keys = set()
            for f in st.get("fields") or []:
                if f.get("type") not in KINDS:
                    errs.append(f"{where}: kieu truong '{f.get('type')}' khong hop le")
                if f.get("key") in keys:
                    errs.append(f"{where}: trung key '{f.get('key')}'")
                keys.add(f.get("key"))
                if f.get("type") == "select" and len(f.get("options") or []) < 2:
                    errs.append(f"{where}/{f.get('key')}: select can >=2 lua chon")
    for p in form.get("panels") or []:
        if p not in PANELS:
            errs.append(f"{aid}: panel '{p}' khong hop le")
    return errs
