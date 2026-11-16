"""Quy trinh nghiep vu nhom hoc sinh: gia su (chan doan -> giang -> tu lam -> chua -> tu luyen -> tom tat), on thi."""
from .forms import _DOC, _SHEET, _OFFICE, _NOTE, area, file, flow, num, sel, step, text

_IMG = ".png,.jpg,.jpeg,.pdf,.docx"
_MUC = ["Em tự làm, gợi ý từng nấc", "Xem lời giải đầy đủ"]
_AN = "Không hỏi tên trường, địa chỉ, số điện thoại của em."


def _tu_luyen(sid="tu-luyen", mon_tool="kiểm tra đáp án bằng run_script nếu là bài tính toán"):
    return step(sid, "Bài tự luyện và tóm tắt", "Ba bài tăng dần độ khó, đáp án đặt riêng ở cuối, kèm phần tóm tắt những điều cần nhớ.",
                "Theo những gì đã học trong cuộc trò chuyện này, tạo file .docx bằng create_docx gồm: (1) 3 bài tự luyện tăng dần độ khó đúng dạng em vừa học (dễ, vừa, hơi khó), "
                f"(2) đáp án và hướng giải ngắn đặt riêng ở trang cuối ({mon_tool}), (3) 'Cần nhớ' tối đa 5 ý bằng lời dễ hiểu và danh sách lỗi em hay mắc. Không đưa đáp án ngay cạnh đề.",
                [sel("so_bai", "Số bài tự luyện", ["3 bài", "5 bài"])],
                ["Có đúng số bài, tăng dần độ khó, cùng dạng với bài vừa học", "Đáp án nằm riêng ở cuối file, không lộ cạnh đề", "Phần 'Cần nhớ' ngắn, em đọc là hiểu"], ["docx"], "Tạo bài tự luyện")


# ---------------------------------------------------------------- gia-su
_GIA_SU = {"intro": "Quy trình của một buổi gia sư: biết em đang hổng chỗ nào, giảng và gợi ý từng nấc (không đưa đáp án ngay), em tự làm, chữa lỗi sai, rồi bài tự luyện và tóm tắt cần nhớ.", "flows": [
    flow("hoc-bai", "Học một bài / khái niệm mới", "Từ câu hỏi nhỏ để biết em hiểu đến đâu, đến bài tự luyện kèm đáp án riêng.", [
        step("chan-doan", "Biết em đang ở đâu", "Hỏi vài câu ngắn để biết em đã hiểu đến đâu trước khi giảng.",
             "Đây là học sinh nhỏ tuổi: giọng thân thiện, không hỏi thông tin cá nhân. CHƯA giảng và CHƯA tạo file. Chỉ đặt 2-3 câu hỏi kiểm tra nhỏ, dễ trả lời (có lựa chọn) về bài/khái niệm dưới đây để xác định em hổng ở đâu, rồi ghi lại mức hiểu của em (bằng remember nếu cần).",
             [text("mon", "Môn, lớp", "VD: Toán 7", True), text("bai", "Bài / khái niệm em chưa hiểu", "VD: nhân hai số nguyên âm", True),
              area("da_hieu", "Em đã hiểu đến đâu? Em vướng ở đâu?", "Em kể ngắn cũng được"), file("anh", "Ảnh bài/đề trong sách (nếu có)", _IMG, True)],
             ["Câu hỏi kiểm tra ngắn, đúng lớp, không có thông tin cá nhân", "Nêu được em đang hổng ở ý nào"], [], "Bắt đầu"),
        step("giang", "Giảng và giải mẫu", "Giảng bằng ví dụ gần gũi, giải mẫu một bài đủ bước và nói rõ vì sao làm vậy.",
             "Dựa vào câu trả lời của em và thông tin đã có trong cuộc trò chuyện này, giảng khái niệm bằng ngôn ngữ đơn giản đúng lớp, kèm một ví dụ gần gũi, rồi giải mẫu MỘT bài đủ bước, mỗi bước nói rõ lý do. Kết thúc bằng một câu hỏi nhỏ để em nói lại bằng lời của mình. Chưa tạo file.",
             [sel("cach", "Em thích", ["Giảng ngắn gọn", "Giảng kỹ, nhiều ví dụ"]), area("tra_loi", "Em trả lời các câu hỏi vừa rồi (nếu chưa trả lời)", "", False)],
             ["Có ví dụ gần gũi và giải mẫu từng bước, có lý do mỗi bước", "Dùng từ ngữ đúng lớp, không thuật ngữ quá tầm", "Có câu hỏi để em tự diễn đạt lại"], [], "Giảng cho em"),
        step("tu-lam", "Em tự làm (gợi ý theo nấc)", "Cho một bài tương tự để em tự làm; gợi ý tăng dần, chỉ đưa đáp án khi em đã thử.",
             "Ra MỘT bài tương tự bài mẫu để em tự làm. Chưa đưa đáp án. Nếu em chọn gợi ý, chuẩn bị 3 mức gợi ý (1: nhắc công thức/ý chính; 2: nêu hướng làm; 3: chỉ chỗ dễ sai) và chỉ đưa từng mức khi em xin. Nếu em đã gửi bài làm thì xem ở bước sau.",
             [sel("muc", "Em muốn", _MUC, True), sel("do_kho", "Độ khó bài này", ["Bằng bài mẫu", "Hơi khó hơn"])],
             ["Bài đúng dạng bài mẫu, vừa sức", "Chưa lộ đáp án; gợi ý chia nấc, không bỏ qua nấc nào"], [], "Cho em bài"),
        step("chua", "Chữa bài của em", "Chỉ chỗ đúng, chỗ sai, giải thích vì sao sai và lỗi điển hình.",
             "Đọc bài làm của em (dùng view_image nếu là ảnh), khen đúng chỗ cụ thể, chỉ từng chỗ sai kèm vì sao sai và cách sửa, nêu lỗi điển hình cùng dạng. Kiểm tra lại các phép tính bằng run_script nếu có tính toán. Chưa tạo file.",
             [file("bai_lam", "Ảnh/File bài làm của em", _IMG, False, True), area("em_nghi", "Em nghĩ mình sai ở đâu?")],
             ["Mỗi lỗi có vị trí cụ thể và lý do, không chỉ 'sai rồi'", "Có ít nhất một điểm em làm tốt được khen cụ thể", "Phép tính trong lời chữa đã kiểm lại"], [], "Chữa bài"),
        _tu_luyen()]),
    flow("chua-bai", "Chữa bài em đã làm", "Em có sẵn bài làm: tìm lỗi, hiểu lỗi, rồi luyện đúng dạng đó.", [
        step("doc", "Đọc bài và chỉ lỗi", "Chỉ ra chỗ đúng, chỗ sai và vì sao sai (chưa đưa lời giải đúng đầy đủ nếu em muốn tự sửa).",
             "Đọc bài làm đính kèm (dùng view_image nếu là ảnh), nêu chỗ làm đúng, chỉ từng chỗ sai kèm lý do. Nếu em chọn tự sửa thì chỉ gợi ý hướng sửa, chưa đưa đáp án; nếu em chọn xem lời giải thì giải đủ bước. Kiểm lại phép tính bằng run_script khi cần. Chưa tạo file.",
             [file("bai_lam", "Ảnh/File bài làm", _IMG, False, True), text("mon", "Môn, lớp", "", True), file("de", "Đề bài (nếu bài làm không có đề)", _IMG, True), sel("cach", "Em muốn", ["Em tự sửa, gợi ý thôi", "Xem lời giải đúng"], True)],
             ["Lỗi được chỉ đúng vị trí, có lý do", "Đúng ý em chọn (gợi ý hay lời giải)"], [], "Chữa bài"),
        step("sua", "Em sửa lại và hiểu lỗi", "Em thử sửa; trợ lý nhận xét và phân loại lỗi (hiểu sai, tính sai, cẩu thả).",
             "Dựa trên các lỗi vừa chỉ, nhận xét bản sửa của em (nếu có) và phân loại từng lỗi: hiểu sai kiến thức, sai kỹ năng, hay cẩu thả. Với mỗi loại, nêu một cách tránh cụ thể. Chưa tạo file.",
             [area("ban_sua", "Em sửa lại thế nào?", "Em viết ngắn cách sửa")], ["Mỗi lỗi được xếp một loại rõ ràng", "Cách tránh lỗi cụ thể, em làm theo được"], [], "Nhận xét bản sửa", True),
        _tu_luyen("luyen")])], "panels": []}

# ---------------------------------------------------------------- on-thi
_DE = ".png,.jpg,.jpeg,.pdf,.docx"
_ON_THI = {"intro": "Quy trình ôn thi: chẩn đoán điểm yếu và quỹ thời gian, lập lộ trình theo số ngày còn lại, luyện đề đúng cấu trúc, chấm và lập bảng lỗi sai, rồi điều chỉnh lộ trình.", "flows": [
    flow("on-thi-tong-the", "Ôn thi từ đầu đến điều chỉnh", "Chẩn đoán, lộ trình, đề luyện, chấm bài và cập nhật lộ trình theo kết quả.", [
        step("chan-doan", "Chẩn đoán và quỹ thời gian", "Chốt kỳ thi, ngày thi, quỹ giờ mỗi ngày, môn và điểm yếu; tính số buổi học thực tế.",
             "Xác định thông tin ôn thi dưới đây, tính số ngày còn lại và số buổi thực tế (trừ ngày nghỉ) bằng run_script. Cấu trúc đề phải lấy từ thông báo chính thức (kb_search/web_search, nêu nguồn), không chắc ghi 'cần kiểm chứng'. Nếu quỹ thời gian quá ít, nói thật và đề xuất trọng tâm. CHƯA lập lịch, chưa tạo file. Không hỏi thông tin cá nhân của em.",
             [text("ky_thi", "Kỳ thi", "VD: thi vào lớp 10, cuối kỳ I", True), text("ngay_thi", "Ngày thi hoặc số ngày còn lại", "VD: còn 45 ngày", True), text("mon", "Các môn cần ôn và điểm mục tiêu", "VD: Toán, Văn, Anh; mục tiêu 8", True),
              num("gio_hoc", "Số giờ học mỗi ngày", "2.5", True), text("ngay_nghi", "Ngày nghỉ cố định", "VD: chủ nhật"), area("diem_yeu", "Môn/chương em yếu", "VD: hình học, đọc hiểu"), file("tai_lieu", "Đề cương, đề cũ, bài kiểm tra gần đây", _DE, True)],
             ["Số ngày và số buổi thực tế tính đúng (có trừ ngày nghỉ)", "Cấu trúc đề có nguồn hoặc ghi 'cần kiểm chứng'", "Điểm yếu và rủi ro (quỹ thời gian) được nêu thẳng"], [], "Chẩn đoán"),
        step("lo-trinh", "Lộ trình theo số ngày", "Lịch ôn 3 giai đoạn, tổng giờ mỗi ngày khớp quỹ giờ, kèm bảng theo dõi % hoàn thành.",
             "Theo thông tin đã có trong cuộc trò chuyện này, lập lộ trình chia 3 giai đoạn (củng cố nền khoảng 50%, luyện dạng bài khoảng 30%, luyện đề và tổng ôn khoảng 20%), ưu tiên chủ đề điểm cao và em yếu, có ngày nghỉ và thời gian vận động. Tạo file .xlsx bằng create_xlsx gồm lịch theo ngày (môn, nội dung, thời lượng, mục tiêu) và bảng theo dõi có công thức % hoàn thành. Kiểm tra tổng giờ mỗi ngày bằng run_script. Không hứa điểm số, không khuyên thức khuya.",
             [sel("kieu", "Em muốn lịch", ["Vừa sức, có nhiều ngày nghỉ", "Dày hơn, ít nghỉ"])],
             ["Tổng giờ mỗi ngày không vượt quỹ giờ em có", "Môn/chương yếu được xếp sớm và nhiều buổi hơn", "Có ngày nghỉ và bảng % hoàn thành chạy bằng công thức"], ["xlsx"], "Lập lộ trình"),
        step("luyen-de", "Luyện đề", "Đề luyện đúng cấu trúc đã chốt, kèm đáp án và thang điểm đặt riêng.",
             "Ra một đề luyện đúng cấu trúc đã chốt ở các bước trước, theo phạm vi và mức độ dưới đây, tạo file .docx bằng create_docx. Đáp án và thang điểm đặt ở trang riêng cuối file, thang điểm cộng đúng tổng (kiểm tra bằng run_script). Không đoán đề thi thật, không chép đề có bản quyền.",
             [text("mon", "Môn", "", True), text("pham_vi", "Phạm vi (chương/bài)", "", True), num("so_cau", "Số câu", "15"), sel("muc", "Mức độ", ["Cơ bản", "Vừa", "Nâng cao", "Giống đề thật"], True), num("phut", "Thời gian làm (phút)", "45")],
             ["Cấu trúc và thời lượng khớp thông tin đã chốt", "Thang điểm cộng đúng tổng", "Đáp án ở trang riêng, không lộ cạnh đề"], ["docx"], "Ra đề"),
        step("cham", "Chấm và bảng lỗi sai", "Chấm bài em làm, phân loại lỗi (kiến thức, kỹ năng, cẩu thả, thời gian) và cách khắc phục.",
             "Chấm bài làm đính kèm theo đáp án và thang điểm của đề vừa ra (dùng view_image nếu là ảnh), tính điểm bằng run_script, lập bảng lỗi sai: câu, lỗi, nhóm lỗi (kiến thức, kỹ năng, cẩu thả, thời gian), cách khắc phục. Ghi thành file .docx bằng create_docx. Nhận xét tích cực, không hứa điểm thi.",
             [file("bai_lam", "Ảnh/File bài làm của em", _DE, False, True), num("thoi_gian", "Em làm hết bao nhiêu phút?", "")],
             ["Điểm tính đúng theo thang, cộng khớp", "Mỗi lỗi có nhóm lỗi và cách khắc phục cụ thể", "Có nhận xét về thời gian làm bài"], ["docx"], "Chấm bài"),
        step("dieu-chinh", "Điều chỉnh lộ trình", "Cập nhật lộ trình theo bảng lỗi sai: dồn thời gian vào nhóm lỗi nặng, giữ tổng giờ.",
             "Dựa vào bảng lỗi sai và điểm vừa chấm, điều chỉnh lộ trình còn lại: tăng thời gian cho nhóm lỗi nhiều nhất, giảm phần đã vững, giữ tổng giờ mỗi ngày không vượt quỹ giờ và còn ngày nghỉ. Tạo lại file .xlsx bằng create_xlsx (giữ nguyên phần đã học xong). Nói rõ chỗ nào đổi và vì sao.",
             [sel("tinh_trang", "Em đang thấy", ["Ổn, theo kịp", "Hơi quá tải", "Căng thẳng, mệt"], True)],
             ["Chỉ rõ đã đổi gì so với lộ trình cũ và lý do", "Tổng giờ vẫn khớp quỹ giờ; nếu em mệt thì có giảm tải hoặc khuyên nói chuyện với thầy cô, gia đình"], ["xlsx"], "Cập nhật lộ trình")]),
    flow("cham-nhanh", "Chấm một bài luyện có sẵn", "Em đã làm xong một đề: chấm và lập bảng lỗi sai.", [
        step("cham", "Chấm bài", "Chấm theo đáp án em cung cấp, tính điểm bằng tính toán.",
             "Chấm bài làm đính kèm theo đề/đáp án đính kèm (dùng view_image nếu là ảnh); nếu thiếu đáp án thì giải trước và nói rõ độ chắc chắn. Tính điểm bằng run_script. Chưa tạo file.",
             [file("bai_lam", "Bài làm của em", _DE, False, True), file("de", "Đề và đáp án", _DE, True), text("mon", "Môn, thang điểm", "VD: Toán, thang 10", True)],
             ["Điểm cộng đúng với thang", "Câu sai được chỉ cụ thể"], [], "Chấm"),
        step("loi-sai", "Bảng lỗi sai", "Phân loại lỗi và cách khắc phục, ghi thành file.",
             "Từ kết quả chấm vừa rồi, lập bảng lỗi sai (câu, lỗi, nhóm lỗi: kiến thức, kỹ năng, cẩu thả, thời gian; cách khắc phục) và ghi thành file .docx bằng create_docx kèm 3 việc nên làm trong tuần tới.",
             [], ["Mỗi lỗi có nhóm và cách khắc phục", "3 việc tuần tới cụ thể, làm được trong quỹ giờ"], ["docx"], "Lập bảng lỗi")])], "panels": []}

# ---------------------------------------------------------------- ngoai-ngu
_NN_TD = ["A1-A2", "B1", "B2", "C1"]
_NGOAI_NGU = {"intro": "Quy trình luyện ngoại ngữ: xác định trình độ và mục tiêu, luyện theo tình huống, sửa tối đa 3 lỗi quan trọng mỗi lượt (câu gốc, câu sửa, lý do, ví dụ), rồi từ vựng có lịch ôn và bài luyện cuối buổi.", "flows": [
    flow("buoi-luyen", "Một buổi luyện đầy đủ", "Từ xác định trình độ, hội thoại, sửa lỗi đến từ vựng và bài luyện cuối buổi.", [
        step("trinh-do", "Xác định trình độ và mục tiêu", "Chốt trình độ, mục tiêu và cách sửa lỗi em thích qua vài câu hỏi hoặc đoạn viết thử.",
             "Xác định trình độ (A1-C1) và mục tiêu của người học từ thông tin dưới đây, nếu cần cho 2-3 câu hỏi/viết thử ngắn (hỏi gộp bằng ask_user). Chưa sửa bài, chưa tạo file. Nêu trình độ ước lượng, độ tin cậy và cách bạn sẽ giải thích (A1-A2 có dịch tiếng Việt, từ B1 giải thích bằng tiếng Anh đơn giản rồi tóm tắt tiếng Việt). Không giả vờ nghe được âm thanh.",
             [sel("trinh_do", "Trình độ tự đánh giá", _NN_TD + ["Chưa biết"], True), text("muc_tieu", "Mục tiêu", "VD: giao tiếp, đi làm, IELTS cơ bản", True), text("chu_de", "Chủ đề quan tâm", "VD: du lịch, trường học"),
              sel("sua", "Khi nói, em muốn", ["Sửa nhẹ, không ngắt mạch", "Sửa kỹ từng lỗi"]), area("viet_thu", "Viết thử 3-5 câu (nếu muốn)", "")],
             ["Trình độ ước lượng có lý do, không khẳng định chắc khi ít dữ liệu", "Cách giải thích phù hợp trình độ"], [], "Xác định trình độ"),
        step("hoi-thoai", "Hội thoại theo tình huống", "Người học nói trước, trợ lý đáp ngắn đúng trình độ; cuối lượt tóm tắt điểm cần sửa.",
             "Đóng vai đối tác để luyện hội thoại theo tình huống dưới đây, đúng trình độ đã xác định. Em nói trước, bạn đáp ngắn và mời em nói tiếp; không ngắt mạch bằng sửa lỗi liên tục. Chưa tạo file. Phát âm chỉ mô tả bằng chữ.",
             [text("tinh_huong", "Tình huống", "VD: đặt phòng khách sạn, phỏng vấn xin việc", True), area("luot_dau", "Câu đầu tiên của em (tiếng Anh)", "Em viết thử, sai cũng không sao")],
             ["Câu trả lời ngắn, đúng trình độ", "Hội thoại đi đúng tình huống đã chọn"], [], "Bắt đầu luyện"),
        step("sua-loi", "Sửa lỗi quan trọng nhất", "Tối đa 3 lỗi: câu gốc, câu sửa, giải thích 1 dòng, câu ví dụ.",
             "Từ phần em đã nói/viết trong cuộc trò chuyện này, chọn tối đa 3 lỗi quan trọng nhất (ưu tiên lỗi lặp lại). Mỗi lỗi trình bày: câu gốc, câu sửa, giải thích 1 dòng dễ hiểu, câu ví dụ tự nhiên. Ghi thành bảng sửa lỗi .docx bằng create_docx. Nếu không chắc quy tắc hiếm gặp, nói rõ và gợi ý tra từ điển uy tín.",
             [file("bai_viet", "Bài viết cần sửa (nếu có thêm)", _DOC, True)],
             ["Không quá 3 lỗi, mỗi lỗi đủ 4 phần (gốc, sửa, lý do, ví dụ)", "Giải thích không dùng thuật ngữ ngữ pháp nặng"], ["docx"], "Sửa lỗi"),
        step("tu-vung", "Từ vựng và lịch ôn", "10-15 từ theo chủ đề kèm nghĩa, ví dụ, collocation và lịch ôn lặp lại ngắt quãng.",
             "Tạo sổ từ vựng .xlsx bằng create_xlsx cho chủ đề của buổi luyện: 10-15 từ gồm từ, loại từ, nghĩa tiếng Việt, ví dụ tự nhiên, collocation, và cột lịch ôn (ngày ôn 1, 2, 3 theo ngắt quãng, tính bằng run_script). Chọn từ phù hợp trình độ, ưu tiên từ xuất hiện trong buổi luyện.",
             [num("so_tu", "Số từ", "12"), text("chu_de", "Chủ đề từ vựng", "Mặc định theo buổi luyện")],
             ["Mỗi từ có nghĩa, ví dụ tự nhiên và collocation", "Lịch ôn ngắt quãng có ngày cụ thể", "Độ khó đúng trình độ"], ["xlsx"], "Lập sổ từ vựng"),
        step("bai-luyen", "Bài luyện cuối buổi", "Bài luyện ngắn dùng đúng các lỗi và từ vừa học, kèm đáp án đặt riêng.",
             "Tạo bài luyện cuối buổi bằng create_docx: 5-8 câu điền/viết lại/viết câu dùng đúng các lỗi và từ vựng vừa học, tăng dần độ khó; đáp án đặt riêng ở trang cuối. Tóm tắt 3 điều cần nhớ.",
             [], ["Bài luyện bám đúng lỗi và từ vừa học", "Có đáp án đặt riêng"], ["docx"], "Tạo bài luyện")]),
    flow("sua-bai-viet", "Sửa một bài viết", "Em có đoạn văn: chọn lỗi chính, sửa, rồi luyện lại.", [
        step("sua", "Sửa lỗi chính", "Chọn tối đa 3 lỗi quan trọng, mỗi lỗi có câu gốc, câu sửa, lý do, ví dụ.",
             "Đọc bài viết của người học (read_document nếu là file), chọn tối đa 3 lỗi quan trọng nhất; mỗi lỗi: câu gốc, câu sửa, giải thích 1 dòng, câu ví dụ. Khen một điểm làm tốt. Chưa tạo file.",
             [area("bai_viet", "Đoạn văn của em", "", True), sel("trinh_do", "Trình độ", _NN_TD, True), file("tep", "Hoặc tải bài viết", _DOC, True)],
             ["Không quá 3 lỗi, đủ 4 phần mỗi lỗi", "Có khen điểm tốt cụ thể"], [], "Sửa bài"),
        step("viet-lai", "Em viết lại và luyện", "Nhận xét bản viết lại và cho bài luyện đúng lỗi vừa sửa.",
             "Nhận xét bản viết lại của em (nếu có; so với bản trước bằng compare_documents nếu là file), rồi tạo bài luyện ngắn .docx bằng create_docx đúng 3 lỗi vừa sửa, đáp án ở trang cuối.",
             [area("ban_moi", "Bản viết lại của em", ""), ], ["Nhận xét nêu lỗi đã sửa được và lỗi còn lại", "Bài luyện đúng 3 lỗi vừa sửa, có đáp án riêng"], ["docx"], "Nhận xét và luyện")])], "panels": []}


# ---------------------------------------------------------------- gia-su-toan
def _toan_luyen():
    return step("tu-luyen", "Bài luyện tương tự và tóm tắt", "3 bài tăng dần, đáp án đã kiểm tra bằng tính toán, đặt riêng ở cuối.",
                "Tạo file .docx bằng create_docx gồm 3 bài tương tự tăng dần độ khó (dễ, vừa, hơi khó), đáp án và hướng giải đặt riêng ở trang cuối. Kiểm tra đáp án từng bài bằng run_script trước khi ghi. Thêm mục 'Cần nhớ' (công thức, điều kiện) và 'Lỗi hay gặp' của dạng bài này.",
                [], ["Đáp án mỗi bài đã kiểm bằng run_script", "Đáp án ở trang riêng cuối file", "Có 'Cần nhớ' và 'Lỗi hay gặp' đúng dạng bài"], ["docx"], "Tạo bài luyện")


_TOAN = {"intro": "Quy trình gia sư Toán: đọc đề và dạng bài, nêu hướng, em tự làm có gợi ý, giải chi tiết có kiểm tra điều kiện và nghiệm bằng tính toán, chỉ lỗi sai, rồi bài luyện tương tự.", "flows": [
    flow("giai-bai", "Giải một bài Toán", "Từ đề bài đến lời giải đã kiểm tra và bài luyện tương tự.", [
        step("doc-de", "Đọc đề và chọn hướng", "Viết lại dữ kiện, yêu cầu, điều kiện; nhận dạng bài và nêu hướng (chưa giải).",
             "Đọc đề (dùng view_image nếu là ảnh). Viết lại giả thiết - cần tìm, nêu điều kiện xác định, phân loại dạng bài và nêu công thức/định lý sẽ dùng cùng lý do. CHƯA giải và chưa tạo file. Nếu đề thiếu dữ kiện hoặc ảnh mờ thì hỏi lại.",
             [area("de_bai", "Đề bài", "Gõ đề hoặc đính kèm ảnh"), file("anh", "Ảnh đề bài", ".png,.jpg,.jpeg,.pdf", True), text("lop", "Lớp, chương đang học", "VD: Toán 9, hệ phương trình", True), area("da_lam", "Em đã làm đến đâu?"), sel("che_do", "Em muốn", _MUC, True)],
             ["Giả thiết, yêu cầu và điều kiện được chép đúng đề", "Hướng làm có nêu định lý/công thức và lý do chọn", "Chưa lộ lời giải"], [], "Phân tích đề"),
        step("goi-y", "Em tự làm, gợi ý theo nấc", "Em thử làm; trợ lý chỉ cho gợi ý từng nấc khi em xin.",
             "Nếu em chọn tự làm: đưa gợi ý theo 3 nấc (nhắc công thức, nêu hướng, chỉ chỗ dễ sai), mỗi lần một nấc và chỉ khi em xin hoặc bí. Nếu em chọn xem lời giải thì bỏ qua bước này nhẹ nhàng. Chưa đưa đáp án cuối. Chưa tạo file.",
             [area("bai_lam", "Em làm đến đâu rồi?", "Gõ các bước em đã làm"), file("anh", "Ảnh bài làm", ".png,.jpg,.jpeg,.pdf", True)],
             ["Gợi ý đúng nấc, không nhảy thẳng ra đáp án", "Nhận xét đúng những bước em đã làm"], [], "Xin gợi ý", True),
        step("giai", "Lời giải chi tiết và kiểm tra", "Giải từng bước có căn cứ, đặt và kiểm tra điều kiện, thay nghiệm ngược bằng run_script.",
             "Theo đề và bài làm đã có trong cuộc trò chuyện này, trình bày lời giải đánh số bước, mỗi bước một dòng kèm căn cứ (định lý/công thức). Đặt điều kiện, loại nghiệm không thỏa. Kiểm tra bằng thế nghiệm ngược và xác minh bằng run_script (giải phương trình, thử số). Nếu kết quả khác đáp án sách thì rà lại đề, không khẳng định sách sai. Chưa tạo file.",
             [], ["Mỗi bước có lý do, không nhảy bước", "Điều kiện và loại nghiệm được nêu rõ", "Đã kiểm tra bằng run_script hoặc thế ngược, ghi kết quả kiểm tra"], [], "Giải và kiểm tra"),
        step("loi-sai", "Chỉ lỗi sai điển hình", "Nếu em đã làm: chỉ chỗ sai; luôn nêu lỗi hay gặp của dạng bài.",
             "So bài làm của em (nếu có) với lời giải đúng, chỉ từng chỗ sai kèm vì sao. Nêu 2-3 lỗi điển hình của dạng bài này (sai dấu khi chuyển vế, quên điều kiện, làm tròn sớm…). Chưa tạo file.",
             [], ["Mỗi lỗi chỉ đúng dòng em làm, có lý do", "Có danh sách lỗi hay gặp của dạng bài"], [], "Chỉ lỗi", True),
        _toan_luyen()]),
    flow("chua-bai", "Chữa bài Toán em đã làm", "Em gửi bài làm: kiểm tra từng dòng, chỉ lỗi, luyện đúng dạng.", [
        step("kiem", "Kiểm tra từng dòng", "Đọc bài làm, kiểm từng bước bằng tính toán, đánh dấu dòng đúng/sai.",
             "Đọc bài làm đính kèm (view_image nếu là ảnh). Kiểm từng dòng, tính lại bằng run_script, đánh dấu dòng đúng và dòng sai kèm lý do ngắn. Chưa đưa lời giải đầy đủ nếu em chọn tự sửa. Chưa tạo file.",
             [file("bai_lam", "Ảnh/File bài làm", ".png,.jpg,.jpeg,.pdf,.docx", False, True), area("de_bai", "Đề bài (nếu bài làm không có đề)"), text("lop", "Lớp", "", True), sel("che_do", "Em muốn", ["Em tự sửa, gợi ý thôi", "Xem lời giải đúng"], True)],
             ["Mỗi dòng sai có số dòng và lý do", "Phép tính đã tính lại bằng run_script"], [], "Kiểm tra bài"),
        step("sua", "Sửa và hiểu lỗi", "Hướng dẫn sửa và nêu lỗi điển hình, nhận xét bản em sửa.",
             "Hướng dẫn sửa theo lựa chọn của em, nêu lỗi điển hình của dạng bài, nhận xét bản em sửa lại nếu có. Chưa tạo file.",
             [area("ban_sua", "Em sửa lại thế nào?")], ["Hướng sửa khớp với lỗi đã chỉ", "Nêu lỗi điển hình để em tránh"], [], "Sửa bài"),
        _toan_luyen()])], "panels": []}


# ---------------------------------------------------------------- gia-su-van
_VAN = {"intro": "Quy trình gia sư Ngữ văn: phân tích đề, lập dàn ý có hướng dẫn chứng, gợi ý cách viết từng đoạn, em tự viết, rồi góp ý theo tiêu chí và em tự sửa. Trợ lý không viết hộ bài nộp.", "flows": [
    flow("lam-bai", "Làm bài văn từ đề đến bản sửa", "Phân tích đề, dàn ý, em tự viết, góp ý và sửa lại.", [
        step("de", "Phân tích đề", "Tìm từ khóa, dạng bài, vấn đề cần bàn và phạm vi dẫn chứng.",
             "Phân tích đề: từ khóa, dạng bài, vấn đề cần bàn, phạm vi dẫn chứng. Chưa lập dàn ý, chưa tạo file, không viết bài. Dẫn chứng văn học chỉ nêu khi chắc chắn đúng (tác phẩm, tác giả, chi tiết); không chắc ghi 'em đối chiếu SGK'. Không hỏi thông tin cá nhân.",
             [area("de_bai", "Đề bài", "Chép nguyên văn đề", True), text("lop", "Lớp", "", True), sel("kieu", "Kiểu bài", ["Nghị luận xã hội", "Nghị luận văn học", "Đọc hiểu", "Viết đoạn", "Tự sự", "Miêu tả", "Thuyết minh"], True), file("anh", "Ảnh đề / văn bản đọc hiểu", _IMG, True)],
             ["Từ khóa và vấn đề cần bàn bám sát đề", "Dạng bài và phạm vi dẫn chứng được nêu rõ", "Không có dẫn chứng chưa chắc chắn mà không ghi chú"], [], "Phân tích đề"),
        step("dan-y", "Lập dàn ý cùng em", "Dàn ý mở - thân - kết, mỗi luận điểm kèm hướng dẫn chứng và lập luận.",
             "Hướng dẫn em lập dàn ý 3 phần; mỗi luận điểm kèm gợi ý hướng dẫn chứng và cách lập luận (chưa viết thành câu văn hoàn chỉnh). Tạo file .docx bằng create_docx. Đưa gợi ý cách viết từng đoạn theo mô hình luận điểm - lập luận - dẫn chứng - nhận xét/liên hệ. Chỉ viết mẫu MỘT đoạn ngắn để minh họa kỹ thuật, nói rõ đó là mẫu.",
             [area("y_em", "Ý em đã nghĩ (nếu có)", "Em ghi vài ý cũng được")],
             ["Mỗi luận điểm có hướng dẫn chứng cụ thể", "Chỉ có tối đa một đoạn mẫu, ghi rõ là minh họa", "Không có bài hoàn chỉnh viết hộ"], ["docx"], "Lập dàn ý"),
        step("em-viet", "Em tự viết", "Em viết bài; trợ lý chỉ trả lời câu hỏi về cách viết, không viết thay.",
             "Em sẽ tự viết bài. Ở bước này chỉ trả lời câu hỏi của em về cách mở bài, nối ý, chọn dẫn chứng; nhắc em dán bản nháp ở bước sau. Tuyệt đối không viết hộ bài. Chưa tạo file.",
             [area("cau_hoi", "Em đang vướng ở chỗ nào khi viết?")], ["Chỉ gợi ý kỹ thuật, không viết thay đoạn của em", "Trả lời đúng câu hỏi của em, ngắn gọn dễ làm theo"], [], "Hỏi cách viết", True),
        step("gop-y", "Góp ý bài viết của em", "Góp ý theo tiêu chí: đúng đề, ý, diễn đạt, trình bày; trích câu cụ thể và gợi ý viết lại.",
             "Góp ý bài của em theo 4 tiêu chí: đúng đề, đủ ý và lập luận, diễn đạt, trình bày. Nêu điểm tốt trước; mỗi điểm cần sửa trích đúng câu của em kèm gợi ý cách viết lại (không viết thay cả đoạn). Dẫn chứng sai hoặc không chắc thì ghi 'đối chiếu SGK'. Ghi nhận xét thành file .docx bằng create_docx.",
             [area("bai", "Bài viết của em", "Dán bài vào đây"), file("tep", "Hoặc tải bài", _DOC, True), text("de_bai", "Đề bài (nếu khác trên)")],
             ["Mỗi góp ý trích câu cụ thể của em và có gợi ý viết lại", "Có điểm tốt cụ thể", "Không thay em viết lại cả bài hay cả đoạn"], ["docx"], "Góp ý"),
        step("sua", "Em sửa lại và so sánh", "So bản đầu và bản sửa để em thấy tiến bộ, nêu điểm còn thiếu.",
             "Nhận xét bản em sửa lại. Nếu hai bản là file .docx thì so bằng compare_documents để chỉ phần em đã cải thiện. Nêu điều em làm tốt hơn và tối đa 2 điểm còn cần sửa. Chưa viết hộ.",
             [file("ban_moi", "Bản sửa của em", _DOC, True), area("ban_sua", "Hoặc dán bản sửa")], ["Chỉ ra tiến bộ cụ thể giữa hai bản", "Tối đa 2 điểm còn cần sửa, có gợi ý"], [], "Nhận xét bản sửa", True)]),
    flow("gop-y-nhanh", "Góp ý bài văn đã viết", "Em đã có bài: góp ý theo tiêu chí và em tự sửa.", [
        step("gop-y", "Góp ý theo tiêu chí", "Nêu điểm mạnh, điểm cần sửa trích câu cụ thể kèm gợi ý.",
             "Đọc bài (read_document hoặc view_image) và góp ý theo 4 tiêu chí: đúng đề, ý, diễn đạt, trình bày; trích câu cụ thể và gợi ý viết lại, không viết hộ. Dẫn chứng chưa chắc ghi 'đối chiếu SGK'. Ghi nhận xét thành file .docx bằng create_docx.",
             [area("bai", "Bài viết của em"), file("tep", "Hoặc tải bài", _IMG, True), text("de_bai", "Đề bài", "", True), text("lop", "Lớp")],
             ["Mỗi góp ý có câu trích và gợi ý", "Có điểm mạnh được khen cụ thể"], ["docx"], "Góp ý"),
        step("sua", "Em sửa và đọc lại", "So hai bản và chỉ phần còn cần sửa.",
             "Nhận xét bản em sửa lại, so với bản trước bằng compare_documents nếu là file .docx, nêu tiến bộ và tối đa 2 điểm còn cần sửa. Không viết hộ.",
             [area("ban_sua", "Bản em sửa"), file("ban_moi", "Hoặc tải bản sửa", _DOC, True)], ["Nêu tiến bộ cụ thể", "Điểm còn thiếu có gợi ý, không viết thay"], [], "Nhận xét", True)])], "panels": []}


# ---------------------------------------------------------------- gia-su-khtn
def _khtn_luyen():
    return step("tu-luyen", "Bài luyện, tóm tắt công thức", "3 bài tăng dần, đáp án có đơn vị đã kiểm tra, kèm bảng tóm tắt công thức/đơn vị.",
                "Tạo file .docx bằng create_docx gồm: 3 bài tương tự tăng dần độ khó, đáp án có đơn vị đặt riêng ở trang cuối (tính và kiểm tra bằng run_script, kiểm tra bậc độ lớn), bảng tóm tắt công thức và đổi đơn vị của dạng bài, và 'Lỗi hay gặp' (nhầm đơn vị, quên đổi nhiệt độ, cân bằng sai hệ số, lẫn mol và gam…). Hằng số lấy từ SGK hoặc nguồn tra cứu, nêu nguồn.",
                [], ["Đáp án mỗi bài có đơn vị và đã kiểm bằng run_script", "Đáp án ở trang riêng cuối file", "Bảng công thức/đơn vị đúng dạng bài"], ["docx"], "Tạo bài luyện")


_KHTN = {"intro": "Quy trình gia sư Lý - Hóa - Sinh: liệt kê dữ kiện kèm đơn vị, chọn định luật/phản ứng, em tự làm có gợi ý, giải từng bước có đơn vị, kiểm tra bảo toàn bằng tính toán, rồi bài luyện và tóm tắt công thức.", "flows": [
    flow("giai-bai", "Giải bài tập tính toán", "Từ đề bài đến lời giải có đơn vị, kiểm tra bảo toàn và bài luyện.", [
        step("du-kien", "Dữ kiện, đơn vị, định luật", "Liệt kê dữ kiện kèm đơn vị, đổi đơn vị, chọn định luật hoặc phản ứng và điều kiện áp dụng (chưa giải).",
             "Đọc đề (view_image nếu là ảnh). Liệt kê dữ kiện kèm đơn vị, đổi về đơn vị phù hợp, chọn định luật/công thức/phản ứng và điều kiện áp dụng kèm lý do. CHƯA giải và chưa tạo file. Hóa: nêu phương trình, chưa tính mol. Thiếu hằng số thì hỏi hoặc tra SGK/nguồn và nêu nguồn.",
             [sel("mon", "Môn", ["Vật lý", "Hóa học", "Sinh học"], True), text("lop", "Lớp", "", True), area("de_bai", "Đề bài", "Gõ đề hoặc đính kèm ảnh"), file("anh", "Ảnh đề bài / hình vẽ", ".png,.jpg,.jpeg,.pdf", True), sel("che_do", "Em muốn", _MUC, True)],
             ["Mọi dữ kiện có đơn vị và đã đổi đúng", "Định luật/phản ứng và điều kiện áp dụng đúng với đề", "Chưa lộ lời giải"], [], "Phân tích đề"),
        step("em-lam", "Em tự làm, gợi ý theo nấc", "Em thử giải; gợi ý từng nấc khi em xin.",
             "Nếu em chọn tự làm: gợi ý 3 nấc (nhắc công thức, nêu hướng thay số, chỉ chỗ dễ nhầm đơn vị) mỗi lần một nấc khi em xin. Chưa đưa đáp án cuối, chưa tạo file.",
             [area("bai_lam", "Em làm đến đâu rồi?"), file("anh", "Ảnh bài làm", ".png,.jpg,.jpeg,.pdf", True)], ["Gợi ý đúng nấc", "Nhận xét đúng bước em đã làm"], [], "Xin gợi ý", True),
        step("giai", "Giải từng bước có đơn vị", "Nêu định luật rồi thay số, ghi đơn vị mỗi bước, cân bằng phương trình trước khi tính mol.",
             "Giải từng bước theo dữ kiện đã chốt trong cuộc trò chuyện này: nêu định luật rồi thay số, ghi đơn vị ở mỗi bước. Hóa: cân bằng phương trình và kiểm tra số nguyên tử trước khi tính mol. Chưa tạo file.",
             [], ["Mỗi bước có đơn vị, kết quả có đơn vị", "Phương trình hóa học (nếu có) đã cân bằng", "Công thức đúng với lớp của em"], [], "Giải bài"),
        step("kiem-tra", "Kiểm tra bảo toàn và độ hợp lý", "Tính lại bằng run_script, kiểm tra đơn vị, bậc độ lớn, bảo toàn (khối lượng, năng lượng, điện tích).",
             "Kiểm tra lại kết quả bằng run_script (tính lại, kiểm tra đơn vị và bậc độ lớn) và kiểm tra bảo toàn phù hợp (khối lượng, năng lượng, điện tích). Kết quả vô lý (âm, vượt vận tốc ánh sáng…) thì rà lại đề và đơn vị. Kết luận thêm một câu giải thích hiện tượng bằng lời dễ hiểu và hỏi em một câu dự đoán 'nếu đổi điều kiện thì sao'. Chưa tạo file.",
             [], ["Có kết quả run_script hoặc tính hai cách", "Nêu bảo toàn nào đã kiểm tra", "Có giải thích hiện tượng bằng lời dễ hiểu"], [], "Kiểm tra"),
        _khtn_luyen()]),
    flow("giai-thich", "Giải thích hiện tượng, khái niệm", "Mô tả - nguyên nhân - ví dụ - em dự đoán, rồi bài luyện.", [
        step("quan-sat", "Mô tả và nguyên nhân", "Mô tả hiện tượng bằng lời thường rồi nêu nguyên nhân ở mức lớp em.",
             "Mô tả hiện tượng/khái niệm bằng lời thường, nêu nguyên nhân khoa học ở mức đúng lớp, một ví dụ đời sống tương tự. Nếu liên quan thí nghiệm: chỉ nhắc thí nghiệm an toàn có thầy cô giám sát, từ chối chi tiết điều chế chất độc, cháy nổ. Không chắc thì nói và nhờ em đối chiếu SGK. Chưa tạo file.",
             [sel("mon", "Môn", ["Vật lý", "Hóa học", "Sinh học"], True), text("lop", "Lớp", "", True), text("hien_tuong", "Hiện tượng / khái niệm em muốn hiểu", "VD: vì sao nước sôi ở 100 °C", True), area("da_hieu", "Em đã hiểu đến đâu?")],
             ["Giải thích đúng mức lớp, không thuật ngữ vượt lớp", "Có ví dụ đời sống", "Không có hướng dẫn thí nghiệm nguy hiểm"], [], "Giải thích"),
        step("du-doan", "Em dự đoán", "Hỏi em dự đoán khi đổi điều kiện và nhận xét câu trả lời.",
             "Đặt cho em một câu dự đoán 'nếu đổi điều kiện X thì điều gì xảy ra, vì sao' rồi nhận xét câu trả lời của em, sửa chỗ hiểu sai. Chưa tạo file.",
             [area("du_doan", "Em dự đoán thế nào?")], ["Nhận xét đúng ý em nói, sửa chỗ hiểu sai", "Chưa đưa đáp án trước khi em trả lời"], [], "Nhận xét", True),
        _khtn_luyen()])], "panels": []}

FLOWS: dict[str, dict] = {"gia-su": _GIA_SU, "on-thi": _ON_THI, "ngoai-ngu": _NGOAI_NGU, "gia-su-toan": _TOAN, "gia-su-van": _VAN, "gia-su-khtn": _KHTN}
