"""Quy trinh nghiep vu nhom sinh vien (moi chuc nang: FLOWS[id] = {intro, flows, panels})."""
from .forms import _DOC, _SHEET, _OFFICE, _NOTE, area, file, flow, num, sel, step, text

_CV_EDIT = (
    " PHẢI VIẾT LẠI: sửa chính tả và câu chữ thô thành ngôn ngữ CV chuyên nghiệp, chủ động, có cấu trúc rõ. Không chép nguyên đoạn gốc. Giữ đầy đủ dữ kiện nhưng được đổi cách diễn đạt, tách câu và sắp xếp ý. Công cụ báo thiếu thì hoàn thiện bản biên tập, không chuyển về nguyên văn. "
    " GIỮ ĐỦ NỘI DUNG: không tự tóm tắt, rút gọn hoặc bỏ bất kỳ kinh nghiệm, dự án, kỹ năng, thành tích hay ý nào người dùng đã nhập. Chỉ biên tập cách diễn đạt; giữ ID từng mục. Muốn rút gọn phải hỏi người dùng trước. "
    " CV được phép nhiều trang theo lượng thông tin liên quan; không ép một trang, không thu nhỏ chữ hoặc cắt mục để đạt số trang. "
    " Hồ sơ theo mẫu được gửi dưới dạng JSON gồm template, data, skipped_sections và tone. "
    "Đây là dữ liệu người dùng chủ động điền cho mẫu đã chọn, ưu tiên dữ liệu này hơn hồ sơ cũ trong lịch sử. "
    "Biên tập TẤT CẢ các mục đã nhập: sửa chính tả, dùng động từ chủ động, diễn đạt tự tin và chuyên nghiệp, "
    "chuyển mô tả thô thành gạch đầu dòng hành động - công cụ - kết quả, chọn từ khóa phù hợp JD. "
    "Có thể làm nổi bật giá trị của công việc bằng cách diễn đạt, nhưng không nâng khống chức danh, "
    "số năm kinh nghiệm, trình độ, chứng chỉ, quy mô hay kết quả. Không tự thêm con số. "
    "Nếu summary trống và không bị bỏ qua, tự viết 2-3 câu dựa trên dữ kiện ở các mục khác. "
    "Không đưa lại mục đã chọn bỏ qua; truyền skipped_sections cho create_cv dưới dạng JSON chuỗi. "
    "Giữ nguyên họ tên, thông tin liên hệ, ngày tháng và các con số người dùng nhập; không lấy dữ liệu minh họa. "
    "Giữ photo_path nếu có, truyền vào create_cv để dùng ảnh người dùng tải lên. "
    "Bao gồm highlights:[{value,label}] và interests nếu mẫu có các mục đó và người dùng điền. "
    "Nếu thiếu dữ kiện quan trọng, gom câu hỏi bằng ask_user trước khi xuất; không để dấu chấm chờ trong CV cuối. "
    "Sau khi tạo file, tóm tắt các thay đổi cách diễn đạt và những điểm người dùng cần kiểm lại; "
    "người dùng có thể yêu cầu sửa và trợ lý phải tạo lại CV với cùng mẫu."
)

FLOWS: dict[str, dict] = {
    "viet-bai-nghien-cuu": {"intro": "Quy trình viết bài học thuật: làm rõ đề và luận điểm, lập dàn ý, tìm và đọc nguồn thật, bạn tự viết rồi nhận góp ý, cuối cùng rà trích dẫn và bố cục. Bạn là người viết; trợ lý chỉ hướng dẫn và góp ý.", "flows": [
        flow("tu-de-den-dan-y", "Từ đề bài đến dàn ý và nguồn", "Làm rõ luận điểm, lập dàn ý và bảng tóm tắt các nguồn thật để bạn bắt tay vào viết.", [
            step("phan-tich-de", "Phân tích đề", "Chốt câu hỏi nghiên cứu hoặc luận điểm trung tâm và chuẩn trích dẫn trước khi lập dàn ý.",
                 "Phân tích đề bài và thông tin dưới đây để nêu câu hỏi nghiên cứu hoặc luận điểm trung tâm trong 1-2 câu, phạm vi bài và chuẩn trích dẫn phải dùng. Thiếu thông tin thiết yếu thì hỏi gộp một lần bằng ask_user. CHƯA lập dàn ý và CHƯA tạo file ở bước này.",
                 [text("de_tai", "Đề tài / yêu cầu của giảng viên", "VD: Chuyển đổi số trong giáo dục đại học", True),
                  sel("loai", "Loại bài", ["Tiểu luận", "Báo cáo thực tập", "Khóa luận", "Bài báo khoa học"], True),
                  text("do_dai", "Số trang hoặc số từ", "VD: 12 trang", True), sel("chuan", "Chuẩn trích dẫn", ["APA", "IEEE", "Harvard", "Theo quy định của trường", "Chưa biết"], True),
                  text("han_nop", "Hạn nộp"), area("y_tuong", "Ý tưởng hoặc quan điểm ban đầu của bạn", "Bạn nghĩ gì về đề này?"), file("yeu_cau", "Đề bài / hướng dẫn của giảng viên", _DOC, False)],
                 ["Câu hỏi hoặc luận điểm chính nêu được trong 1-2 câu và đúng ý đề bài", "Phạm vi và chuẩn trích dẫn được xác nhận rõ", "Những điểm đề bài còn mơ hồ được nêu để bạn hỏi lại giảng viên"], [], "Phân tích đề"),
            step("dan-y", "Lập dàn ý", "Lập dàn ý mở bài - thân bài - kết luận, mỗi phần phục vụ luận điểm chính.",
                 "Theo kết quả đã có trong cuộc trò chuyện này, lập dàn ý chi tiết: mở đầu (bối cảnh, vấn đề, mục tiêu), thân bài theo từng luận điểm kèm loại dẫn chứng cần có, kết luận (trả lời câu hỏi, hạn chế, hướng tiếp). Chỉ là dàn ý, KHÔNG viết thành bài hoàn chỉnh. Ghi file .docx bằng create_docx và báo đường dẫn.",
                 [area("chinh", "Điều chỉnh (nếu có)", "VD: thêm phần so sánh với Việt Nam")],
                 ["Mỗi phần của dàn ý nối được về câu hỏi hoặc luận điểm chính", "Có chỗ ghi loại dẫn chứng cần tìm cho từng luận điểm", "Dàn ý không phải bài viết sẵn để chép nộp"], ["docx"], "Lập dàn ý"),
            step("tim-nguon", "Tìm và tóm tắt nguồn", "Tìm nguồn thật theo từng luận điểm và tóm tắt vào bảng so sánh.",
                 "Theo dàn ý đã chốt, tìm tài liệu bằng web_search và web_fetch (và đọc các file bạn đính kèm bằng read_document). CHỈ liệt kê nguồn thật đã mở được, kèm đường dẫn; nguồn nào chưa chắc thì ghi 'cần kiểm chứng', tuyệt đối không bịa tác giả, năm, DOI, số trang. Ghi bảng bằng create_xlsx với cột: Nguồn, Luận điểm chính, Phương pháp, Kết quả, Hạn chế, Dùng cho mục nào.",
                 [file("tai_lieu", "Tài liệu bạn đã có (PDF, Word)", _DOC, True), num("so_nguon", "Số nguồn mong muốn", "VD: 8")],
                 ["Mỗi nguồn có đường dẫn mở được hoặc ghi rõ 'cần kiểm chứng'", "Bảng ghi rõ nguồn dùng cho mục nào của dàn ý", "Không có tác giả, năm hay DOI không kiểm chứng được"], ["xlsx"], "Tìm nguồn"),
            step("chot", "Chốt kế hoạch viết", "Liệt kê các nguồn cần bạn tự kiểm tra và kế hoạch viết từng phần.",
                 "Lập kế hoạch viết dựa trên dàn ý và bảng nguồn đã có: thứ tự viết từng phần, ước lượng số từ mỗi phần theo độ dài yêu cầu, nguồn nào bạn cần tự mở kiểm tra lại. Không viết hộ nội dung bài và không tạo file mới.", [],
                 ["Mỗi phần có số từ ước lượng, tổng khớp độ dài yêu cầu", "Các nguồn 'cần kiểm chứng' được liệt kê để bạn tự kiểm tra"], [], "Chốt kế hoạch")]),
        flow("gop-y-bai", "Góp ý bài đã viết", "Bạn đã có bài nháp: nhận góp ý cụ thể từng đoạn, rà trích dẫn và bố cục.", [
            step("doc-bai", "Đọc bài và đánh giá chung", "Đọc bài nháp và nêu nhận xét tổng thể về luận điểm, bố cục, mạch lập luận.",
                 "Đọc bài nháp đính kèm bằng read_document, nêu nhận xét tổng thể: luận điểm có rõ không, mạch lập luận, phần nào thiếu dẫn chứng, kết luận có trả lời câu hỏi mở đầu không. Giữ nguyên giọng văn của sinh viên. Chưa sửa bài và chưa tạo file.",
                 [file("bai", "Bài nháp của bạn", _DOC, False, True), text("de_tai", "Đề tài và yêu cầu", "VD: Tiểu luận 10 trang, chuẩn APA", True), sel("chuan", "Chuẩn trích dẫn", ["APA", "IEEE", "Harvard", "Theo quy định của trường"], True), _NOTE],
                 ["Nhận xét chỉ ra được điểm mạnh và điểm yếu chính, có trích câu cụ thể", "Không tự viết lại cả bài thay bạn"], [], "Đánh giá bài"),
            step("gop-y", "Góp ý từng đoạn", "Lập bảng góp ý: trích câu của bạn, vấn đề, gợi ý sửa; bạn tự sửa.",
                 "Theo đánh giá đã có, lập file nhận xét .docx bằng create_docx: mỗi góp ý gồm trích nguyên câu của sinh viên, vấn đề gặp phải (lập luận, diễn đạt, thiếu dẫn chứng, lặp ý) và gợi ý hướng sửa. Không viết lại cả đoạn thay sinh viên.", [],
                 ["Mỗi góp ý trích đúng câu trong bài của bạn kèm gợi ý sửa", "Gợi ý là hướng sửa, không phải đoạn văn viết sẵn để thay"], ["docx"], "Góp ý bài"),
            step("kiem-tra", "Rà trích dẫn và bố cục", "Kiểm tra trích dẫn trong bài khớp danh mục, đúng một chuẩn, cùng với bố cục.",
                 "Rà bài theo chuẩn trích dẫn đã chọn: mọi trích dẫn trong bài có trong danh mục và ngược lại, định dạng nhất quán, có thể dùng run_script để đếm từ và đối chiếu. Nguồn không xác minh được thì ghi 'cần kiểm chứng'. Nếu có bản nháp trước, dùng compare_documents để chỉ ra đoạn trùng hay thay đổi. Không tự thêm nguồn mới.",
                 [file("nguon_goc", "Tài liệu nguồn để đối chiếu trùng lặp (nếu có)", _DOC, True)],
                 ["Danh sách trích dẫn thiếu hoặc thừa so với danh mục được nêu cụ thể", "Đoạn nghi trùng nguồn (nếu có) được chỉ ra kèm cách diễn đạt lại và trích dẫn đúng"], [], "Rà trích dẫn")]),
    ], "panels": []},

    "slide-thuyet-trinh": {"intro": "Quy trình làm bài thuyết trình: chốt thông điệp và khung theo thời lượng, dựng slide kèm ghi chú diễn giả, chuẩn bị câu hỏi phản biện, rồi luyện và chốt theo giờ.", "flows": [
        flow("bao-ve", "Bài thuyết trình đầy đủ", "Từ nội dung gốc đến bộ slide, kịch bản nói và câu hỏi phản biện.", [
            step("khung", "Chốt thông điệp và khung", "Chốt thông điệp chính, số slide theo thời lượng và cấu trúc từng slide.",
                 "Đọc nội dung gốc (nếu có đính kèm, dùng read_document) và xác định một thông điệp chính cùng 3 ý hỗ trợ. Tính số slide theo thời lượng (khoảng 1 slide/phút) rồi đề xuất khung: slide nào, tiêu đề dạng câu khẳng định, ý chính, số liệu cần dùng. CHƯA tạo file ở bước này. Thiếu dữ liệu thì hỏi, không bịa số liệu.",
                 [text("chu_de", "Chủ đề", "VD: Bảo vệ đồ án quản lý thư viện", True), sel("doi_tuong", "Người nghe", ["Hội đồng bảo vệ", "Giảng viên và bạn học", "Nhà tuyển dụng / doanh nghiệp", "Khác"], True),
                  sel("muc_dich", "Mục đích", ["Bảo vệ", "Báo cáo", "Thuyết phục", "Giới thiệu"], True), num("thoi_luong", "Thời lượng (phút)", "VD: 10", True),
                  sel("phong_cach", "Phong cách", ["Trang trọng", "Trẻ trung"]), file("nguon", "Báo cáo hay đồ án gốc", _OFFICE, False), file("mau", "Mẫu slide của trường (nếu có)", ".pptx", False)],
                 ["Thông điệp chính nêu được trong một câu", "Số slide khớp thời lượng (khoảng 1 slide/phút)", "Mỗi slide trong khung chỉ có một ý và tiêu đề là câu khẳng định"], [], "Chốt khung"),
            step("slide", "Dựng slide và ghi chú diễn giả", "Tạo file PowerPoint, mỗi slide kèm ghi chú diễn giả có thời gian.",
                 "Theo khung đã chốt trong cuộc trò chuyện này, tạo bộ slide bằng create_pptx: mỗi slide một ý, tối đa 6 dòng, chữ nội dung từ 24 pt, ghi chú diễn giả (lời nói và thời gian) đặt trong notes. Số liệu và biểu đồ phải ghi nguồn và đơn vị; chỗ chưa có số liệu thật để '……'. Báo đường dẫn file.",
                 [area("chinh", "Điều chỉnh khung (nếu có)", "VD: thêm slide demo, bỏ slide lý thuyết")],
                 ["File .pptx đã tạo, mỗi slide tối đa 6 dòng", "Slide chính đều có ghi chú diễn giả", "Số liệu có nguồn và đơn vị, không có số liệu bịa"], ["pptx"], "Làm slide"),
            step("phan-bien", "Câu hỏi phản biện", "Chuẩn bị 5+ câu hỏi dễ gặp kèm gợi ý trả lời, kể cả câu khó.",
                 "Theo nội dung slide đã có, soạn ít nhất 5 câu hỏi phản biện mà người nghe dễ đặt ra (phương pháp, số liệu, hạn chế, tính ứng dụng) kèm gợi ý trả lời; với câu khó, đưa hướng trả lời thẳng thắn nêu hạn chế và kế hoạch cải tiến. Ghi file .docx bằng create_docx.", [],
                 ["Có từ 5 câu hỏi, bám đúng nội dung slide", "Mỗi câu có gợi ý trả lời, không bịa số liệu để chống chế"], ["docx"], "Soạn câu hỏi"),
            step("luyen", "Luyện và chốt theo giờ", "Phân bổ thời gian từng slide, cắt bớt nếu vượt giờ và xuất bản in.",
                 "Lập bảng phân bổ thời gian nói cho từng slide so với thời lượng, chỉ ra slide nên cắt hoặc gộp nếu vượt giờ (bỏ slide phụ, không thu nhỏ chữ), kèm lời nhắc luyện nói. Nếu cần bản in, xuất PDF bằng convert_to_pdf. Không thay đổi nội dung khoa học.",
                 [sel("pdf", "Xuất thêm PDF để nộp hoặc in?", ["Không", "Có"])],
                 ["Tổng thời gian các slide khớp thời lượng", "Slide đề xuất cắt (nếu có) được nêu kèm lý do"], [], "Chốt bài")]),
        flow("kich-ban", "Kịch bản và phản biện cho slide có sẵn", "Bạn đã có slide: viết kịch bản nói và câu hỏi phản biện.", [
            step("doc-slide", "Đọc slide và chốt thời lượng", "Đọc slide có sẵn, kiểm tra số slide so với thời lượng.",
                 "Đọc file slide đính kèm bằng read_document, nêu thông điệp chính suy ra từ slide, kiểm tra số slide so với thời lượng và slide nào quá dày chữ. Chưa viết kịch bản và chưa tạo file.",
                 [file("slide", "File slide", ".pptx,.pdf", False, True), num("thoi_luong", "Thời lượng (phút)", "VD: 5", True), sel("doi_tuong", "Người nghe", ["Hội đồng bảo vệ", "Giảng viên và bạn học", "Nhà tuyển dụng / doanh nghiệp", "Khác"], True)],
                 ["Thông điệp chính suy ra khớp ý bạn", "Slide quá dày được chỉ rõ số trang"], [], "Đọc slide"),
            step("kich-ban", "Viết kịch bản nói", "Kịch bản từng slide kèm thời gian, giữ đúng nội dung có trên slide.",
                 "Theo slide đã đọc, viết kịch bản nói từng slide kèm thời gian, nói ý chứ không đọc nguyên chữ trên slide. Không thêm số liệu hay kết quả không có trong tài liệu gốc; chỗ cần bạn bổ sung để '……'. Ghi file .docx bằng create_docx.", [],
                 ["Tổng thời gian khớp thời lượng", "Kịch bản không chứa số liệu ngoài tài liệu gốc"], ["docx"], "Viết kịch bản"),
            step("phan-bien", "Câu hỏi phản biện", "5+ câu hỏi dễ gặp kèm gợi ý trả lời.",
                 "Soạn ít nhất 5 câu hỏi phản biện dựa trên slide và kịch bản đã có, kèm gợi ý trả lời, có câu hỏi khó về hạn chế. Ghi file .docx bằng create_docx.", [],
                 ["Từ 5 câu hỏi bám nội dung slide", "Có gợi ý trả lời cho từng câu"], ["docx"], "Soạn câu hỏi")]),
    ], "panels": []},

    "cv-viec-lam": {"intro": "Quy trình xin việc: phân tích tin tuyển dụng, đối chiếu với thông tin thật của bạn, viết CV chuyên nghiệp và thư xin việc để bạn duyệt, rồi phỏng vấn thử có nhận xét. Chỉ dùng thông tin bạn cung cấp.", "flows": [
        flow("ung-tuyen", "Hồ sơ ứng tuyển và phỏng vấn thử", "Từ tin tuyển dụng đến CV, thư xin việc và buổi phỏng vấn thử.", [
            step("phan-tich-jd", "Phân tích tin tuyển dụng", "Rút từ khóa và yêu cầu chính của JD, đối chiếu với hồ sơ của bạn để thấy điểm mạnh và chỗ thiếu.",
                 "Phân tích JD (dán hoặc đính kèm) và hồ sơ của người dùng dưới đây: từ khóa kỹ năng, trách nhiệm chính, điểm hồ sơ đã khớp và khoảng trống. Có thể tìm hiểu công ty bằng web_search, nêu nguồn. CHƯA viết CV. Nếu chưa có hồ sơ, chỉ phân tích JD và liệt kê thông tin cần chuẩn bị; người dùng đã chọn mẫu và sẽ điền hồ sơ theo mẫu ở bước tiếp theo, không yêu cầu nhập toàn bộ hồ sơ tại bước này. Thiếu thông tin thì để trống, tuyệt đối không bịa kinh nghiệm, bằng cấp, số liệu.",
                 [{"key": "mau_cv", "label": "Chọn mẫu CV", "type": "cv-template", "required": True}, text("vi_tri", "Vị trí ứng tuyển", "VD: Thực tập sinh marketing", True), text("cong_ty", "Tên công ty", "", True), area("jd", "Nội dung JD", "Dán mô tả công việc", True),
                  area("ho_so", "Hồ sơ tóm tắt (nếu có)", "Có thể để trống; bạn sẽ điền hồ sơ theo mẫu ở bước tiếp theo"),
                  file("cv_cu", "CV cũ (nếu có)", _DOC, False), sel("ngon_ngu", "Ngôn ngữ CV", ["Tiếng Việt", "Tiếng Anh"], True)],
                 ["Từ khóa và yêu cầu chính của JD được liệt kê đúng", "Khoảng trống của hồ sơ được nêu, không tự lấp bằng thông tin bịa", "Danh sách câu hỏi thêm về thành tích và số liệu để bạn trả lời"], [], "Phân tích JD"),
            step("cv", "Viết CV chuyên nghiệp", "CV đầy đủ: tóm tắt, kinh nghiệm hoặc dự án có kết quả, học vấn, kỹ năng.",
                 "Theo JD và hồ sơ đã có trong cuộc trò chuyện này, dùng create_cv với template đúng ID mẫu người dùng chọn dưới đây để xuất CV PDF và HTML theo mẫu mystore, lang theo ngôn ngữ đã chọn. data là JSON hồ sơ thật: name,title,email,phone,address,website,summary,experience:[{role,company,from,to,desc}],education:[{school,degree,from,to,desc}],skills:[{name}],languages:[{name,level}],projects:[{name,desc}],awards. KHÔNG dùng create_docx để dựng CV. Nội dung đầy đủ, giữ mọi chi tiết đã nhập; được phép nhiều trang: Giới thiệu giữ đủ ý người dùng viết, kinh nghiệm và dự án giữ đủ mọi mục và mọi ý chi tiết, không giới hạn số gạch đầu dòng, học vấn, kỹ năng, giải thưởng. Chỉ dùng thông tin và con số người dùng đã cung cấp; chưa có thì hỏi hoặc bỏ qua theo lựa chọn của người dùng. Không đưa số CCCD hay thông tin nhạy cảm. Báo đường dẫn file." + _CV_EDIT,
                 [{"key": "mau_cv", "label": "Chọn mẫu CV", "type": "cv-template", "required": True}, {"key": "ho_so_cv", "label": "Thông tin cho mẫu CV đã chọn", "type": "cv-profile", "required": True}, area("bo_sung", "Thành tích và số liệu bổ sung (nếu có)", "VD: dự án làm cho 200 người dùng thử")],
                 ["Mọi thông tin trong CV đều do bạn cung cấp, chỗ thiếu thì hỏi hoặc bỏ qua theo lựa chọn của người dùng", "Độ dài phù hợp hồ sơ, không ép một trang; từ khóa JD xuất hiện tự nhiên", "Mỗi gạch đầu dòng có hành động và kết quả khi có dữ kiện"], ["pdf", "html"], "Tạo CV theo mẫu"),
            step("thu", "Thư xin việc", "Thư 3 đoạn, không quá 250 từ, đúng tên công ty và vị trí.",
                 "Viết thư xin việc 3 đoạn (vì sao vị trí này, bạn mang gì, kêu gọi hành động) không quá 250 từ, đúng tên công ty và vị trí đã nêu, chỉ dùng thông tin đã có trong cuộc trò chuyện này. Ghi file .docx bằng create_docx. Chưa gửi đi đâu.", [],
                 ["Thư không quá 250 từ", "Đúng tên công ty và vị trí; không có thông tin ngoài hồ sơ bạn đưa"], ["docx"], "Viết thư"),
            step("chot-ho-so", "Rà và chốt hồ sơ", "Kiểm tra lần cuối chính tả, nhất quán và từng thông tin so với sự thật.",
                 "Rà CV và thư xin việc: chính tả, định dạng nhất quán, tên công ty, từ khóa JD. Liệt kê từng con số và thành tích trong CV để người dùng tự xác nhận là đúng sự thật. CV đã có PDF từ create_cv; đối chiếu nội dung với CV cũ bằng read_document. Nếu cần PDF thư xin việc, xuất thư bằng convert_to_pdf. Không tự nộp hồ sơ.",
                 [sel("pdf", "Xuất PDF để nộp?", ["Không", "Có"])],
                 ["Danh sách con số và thành tích để bạn xác nhận là thật", "Không còn lỗi chính tả hay sai tên công ty"], [], "Chốt hồ sơ"),
            step("phong-van", "Phỏng vấn thử", "Trợ lý hỏi 8-10 câu theo JD, từng câu bạn trả lời rồi nhận xét theo STAR.",
                 "Phỏng vấn thử theo vị trí: hỏi từng câu một (khoảng 8-10 câu gồm giới thiệu bản thân, điểm mạnh yếu, tình huống STAR, lý do chọn công ty), đợi người dùng trả lời bằng ask_user rồi nhận xét câu đó (rõ ràng, có ví dụ và kết quả thật, độ dài 60-90 giây) trước khi sang câu sau. Không bịa câu trả lời thay người dùng.",
                 [sel("so_cau", "Số câu hỏi", ["5", "8", "10"]), sel("cap_do", "Mức độ", ["Cơ bản", "Khó hơn, có câu hỏi sâu"])],
                 ["Mỗi câu trả lời có nhận xét cụ thể kèm gợi ý cải thiện", "Câu hỏi bám đúng JD và hồ sơ thật của bạn"], [], "Bắt đầu phỏng vấn", True)]),
        flow("sua-cv", "Sửa CV có sẵn", "Bạn đã có CV: chỉnh cho đúng vị trí mới, độ dài phù hợp nội dung.", [
            step("doc-cv", "Đọc CV và đối chiếu JD", "Đối chiếu CV hiện tại với JD để biết cần sửa gì.",
                 "Đọc CV đính kèm bằng read_document và JD dưới đây, nêu điểm cần sửa: từ khóa thiếu, gạch đầu dòng chỉ mô tả nhiệm vụ mà chưa có kết quả, nội dung thừa. Chưa tạo file. Không thêm thông tin bạn chưa cung cấp.",
                 [{"key": "mau_cv", "label": "Chọn mẫu CV", "type": "cv-template", "required": True}, file("cv", "CV hiện tại", _DOC, False, True), text("vi_tri", "Vị trí ứng tuyển", "", True), text("cong_ty", "Tên công ty", "", True), area("jd", "Nội dung JD", "", True)],
                 ["Danh sách điểm cần sửa cụ thể, trích dòng trong CV", "Câu hỏi bổ sung số liệu thật để bạn trả lời"], [], "Phân tích CV"),
            step("cv-moi", "Viết lại CV", "CV mới đủ thông tin, chỉ dùng thông tin thật.",
                 "Viết lại CV theo các điểm đã nêu bằng create_cv, template đúng ID mẫu người dùng chọn dưới đây, xuất PDF và HTML. data theo cấu trúc công cụ, lang theo ngôn ngữ hồ sơ. Không dùng create_docx để dựng CV. Nội dung đầy đủ, được phép nhiều trang, chỉ dùng thông tin có trong CV cũ và các câu trả lời của người dùng; chỗ thiếu thì hỏi hoặc bỏ qua theo lựa chọn của người dùng. Liệt kê các nội dung đã đổi so với bản cũ." + _CV_EDIT, [{"key": "mau_cv", "label": "Chọn mẫu CV", "type": "cv-template", "required": True}, {"key": "ho_so_cv", "label": "Thông tin cho mẫu CV đã chọn", "type": "cv-profile", "required": True}, area("bo_sung", "Thông tin bổ sung", "Thành tích, số liệu thật")],
                 ["Độ dài phù hợp hồ sơ, không giới hạn một trang, không thông tin nào ngoài hồ sơ bạn đưa", "Bảng so sánh cho thấy rõ những gì đã đổi"], ["pdf", "html"], "Tạo lại CV theo mẫu")]),
    ], "panels": []},

    "nghien-cuu-khoa-hoc": {"intro": "Quy trình nghiên cứu khoa học: chọn đề tài và câu hỏi khả thi, tổng quan tài liệu, thiết kế phương pháp, phân tích số liệu thật bằng script, rồi viết báo cáo. Bạn tự thu thập số liệu; trợ lý không bao giờ tạo số liệu giả.", "flows": [
        flow("de-cuong-den-bao-cao", "Từ ý tưởng đến đề cương nghiên cứu", "Chọn đề tài khả thi, tổng quan tài liệu thật và thiết kế phương pháp, xuất đề cương.", [
            step("de-tai", "Chọn đề tài và câu hỏi", "Biến ý tưởng thành câu hỏi nghiên cứu và giả thuyết đo lường được trong nguồn lực có.",
                 "Đánh giá ý tưởng dưới đây và đề xuất câu hỏi nghiên cứu cùng giả thuyết (H0 và H1) kiểm chứng được, có tính khả thi theo thời gian và nguồn lực. Nếu đề tài quá rộng, đề xuất thu hẹp. Thiếu thông tin thì hỏi gộp một lần bằng ask_user. Chưa tạo file. Nghiên cứu có người tham gia, trẻ em hoặc động vật: nhắc yêu cầu đạo đức và xin phép.",
                 [sel("cap", "Cấp", ["KHKT học sinh", "NCKH sinh viên"], True), text("linh_vuc", "Lĩnh vực", "VD: Môi trường, tin học", True), area("y_tuong", "Ý tưởng ban đầu", "Bạn muốn tìm hiểu điều gì?", True),
                  text("thoi_gian", "Thời gian thực hiện", "VD: 3 tháng", True), area("nguon_luc", "Nguồn lực (thiết bị, mẫu, kinh phí)", "VD: phòng thí nghiệm trường, 50 bạn tham gia khảo sát"), file("yeu_cau", "Yêu cầu của cuộc thi hoặc khoa", _DOC, False)],
                 ["Câu hỏi nghiên cứu rõ và đo lường được", "Giả thuyết kiểm chứng được và khả thi trong thời gian và nguồn lực", "Rủi ro đạo đức hay an toàn (nếu có) được nêu rõ"], [], "Chốt đề tài"),
            step("tong-quan", "Tổng quan tài liệu", "Tìm 5-10 nguồn thật và so sánh luận điểm, phương pháp, kết quả, khoảng trống.",
                 "Theo câu hỏi nghiên cứu đã chốt, tìm 5-10 nguồn bằng web_search và web_fetch. CHỈ ghi nguồn thật đã mở được, kèm đường dẫn; chưa chắc thì ghi 'cần kiểm chứng', không bịa tác giả, năm, DOI. Lập bảng bằng create_xlsx với cột Nguồn, Luận điểm, Phương pháp, Kết quả, Khoảng trống, rồi nêu khoảng trống mà đề tài lấp.",
                 [file("tai_lieu", "Tài liệu bạn đã có", _DOC, True)],
                 ["Mỗi nguồn có đường dẫn mở được hoặc ghi 'cần kiểm chứng'", "Khoảng trống nghiên cứu được nêu và liên hệ với câu hỏi của bạn"], ["xlsx"], "Tổng quan"),
            step("phuong-phap", "Thiết kế phương pháp", "Xác định biến, cỡ mẫu, cách đo, kế hoạch phân tích và đạo đức.",
                 "Theo đề tài và tổng quan đã có, thiết kế phương pháp: biến độc lập, phụ thuộc, kiểm soát; nhóm đối chứng; cỡ mẫu và lý do; cách thu thập và đo; kiểm định dự kiến theo loại biến (nêu giả định); đạo đức nghiên cứu. Chưa có số liệu nên KHÔNG đưa kết quả. Ghi đề cương .docx bằng create_docx. Không hướng dẫn thí nghiệm nguy hiểm.",
                 [area("chinh", "Điều chỉnh (nếu có)", "VD: cỡ mẫu tối đa 40")],
                 ["Biến, cỡ mẫu và cách đo được nêu cụ thể", "Có nhóm đối chứng hoặc lý do không cần", "Có mục đạo đức và hạn chế dự kiến, không có kết quả bịa"], ["docx"], "Thiết kế phương pháp"),
            step("chot", "Chốt kế hoạch thu thập", "Bảng việc cần bạn tự làm và mẫu bảng ghi số liệu.",
                 "Lập kế hoạch thu thập số liệu theo phương pháp đã chốt: các bước bạn tự thực hiện, cột cần ghi, đơn vị. Tạo bảng trống để nhập số liệu bằng create_xlsx (chỉ có tiêu đề cột và đơn vị, KHÔNG điền dữ liệu mẫu giả).", [],
                 ["Bảng ghi số liệu chỉ có tiêu đề cột và đơn vị, không có số bịa", "Các bước thu thập khớp với phương pháp"], ["xlsx"], "Chốt kế hoạch")]),
        flow("phan-tich-so-lieu", "Phân tích số liệu thật và viết báo cáo", "Bạn đã có số liệu: làm sạch, phân tích bằng script, vẽ biểu đồ, viết kết luận đúng mức.", [
            step("lam-sach", "Kiểm tra và làm sạch số liệu", "Đọc số liệu, tìm thiếu sót và giá trị bất thường, xác nhận câu hỏi và giả thuyết.",
                 "Đọc file số liệu đính kèm bằng run_script: cấu trúc, số mẫu, giá trị thiếu, giá trị bất thường, loại biến. Nêu giả định và vấn đề phát hiện, hỏi người dùng nên xử lý thế nào, không tự sửa hay thêm số liệu. Chưa phân tích kết luận.",
                 [file("so_lieu", "File số liệu của bạn", _SHEET, False, True), text("cau_hoi", "Câu hỏi nghiên cứu", "", True), area("gia_thuyet", "Giả thuyết", "H0 và H1 nếu có"), area("mo_ta", "Mô tả cách thu thập và ý nghĩa các cột", "", True)],
                 ["Số mẫu, giá trị thiếu và bất thường được báo đúng theo file", "Mọi chỗ sửa dữ liệu chỉ thực hiện sau khi bạn đồng ý"], [], "Kiểm tra dữ liệu"),
            step("phan-tich", "Phân tích thống kê", "Thống kê mô tả, kiểm định phù hợp, biểu đồ có nhãn trục và đơn vị.",
                 "Theo số liệu và quyết định đã có trong cuộc trò chuyện này, phân tích bằng run_script: thống kê mô tả, kiểm định phù hợp loại biến (nêu và kiểm tra giả định), báo p-value và cỡ hiệu ứng, vẽ biểu đồ có nhãn trục và đơn vị. Ghi kết quả và biểu đồ vào file .xlsx bằng create_xlsx và nêu rõ mã đã chạy. Không chọn lọc kết quả có lợi.",
                 [sel("kiem_dinh", "Kiểm định bạn muốn dùng", ["Để trợ lý đề xuất", "So sánh hai nhóm", "So sánh nhiều nhóm", "Tương quan / hồi quy", "Chi bình phương / tỉ lệ"])],
                 ["Có mã run_script và kết quả đi kèm", "Giả định kiểm định được nêu và kiểm tra", "Biểu đồ có nhãn trục và đơn vị"], ["xlsx"], "Phân tích"),
            step("dien-giai", "Diễn giải và hạn chế", "Kết luận không vượt quá số liệu; nêu hạn chế và bước tiếp theo.",
                 "Diễn giải kết quả đã phân tích: có bác bỏ được H0 hay không, cỡ hiệu ứng; phân biệt tương quan với nhân quả; nêu hạn chế (cỡ mẫu, thiết kế, sai lệch) và hướng tiếp theo. Chưa viết báo cáo hoàn chỉnh.", [],
                 ["Kết luận không mạnh hơn bằng chứng số liệu cho phép", "Hạn chế được nêu thẳng, gồm cả cỡ mẫu"], [], "Diễn giải"),
            step("bao-cao", "Viết báo cáo", "Báo cáo theo cấu trúc chuẩn từ kết quả đã có; bạn bổ sung và kiểm chứng.",
                 "Theo đề cương, kết quả phân tích và diễn giải đã có trong cuộc trò chuyện này, lập khung báo cáo bằng create_docx gồm tóm tắt, giới thiệu, phương pháp, kết quả (đúng số liệu thật), thảo luận, hạn chế, tài liệu tham khảo. Tài liệu tham khảo chỉ gồm nguồn thật đã tìm được, nguồn chưa chắc ghi 'cần kiểm chứng'. Phần diễn đạt để bạn tự hoàn thiện.", [],
                 ["Số liệu trong báo cáo khớp kết quả đã phân tích", "Tài liệu tham khảo có thật hoặc ghi 'cần kiểm chứng'", "Hạn chế được nêu trong báo cáo"], ["docx"], "Viết báo cáo"),
            step("phan-bien", "Chuẩn bị phản biện", "Câu hỏi hội đồng dễ hỏi kèm gợi ý trả lời trung thực.",
                 "Soạn ít nhất 5 câu hỏi phản biện mà hội đồng có thể hỏi về đề tài, phương pháp, cỡ mẫu, kết quả và hạn chế, kèm gợi ý trả lời trung thực dựa trên số liệu thật. Không đề xuất che giấu hạn chế.", [],
                 ["Từ 5 câu hỏi sát đề tài", "Gợi ý trả lời dựa trên số liệu và hạn chế thật"], [], "Chuẩn bị phản biện", True)]),
    ], "panels": []},
}
