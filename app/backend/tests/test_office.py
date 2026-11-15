import json

from argus.services import tools
from argus.services.tools import ToolContext


def ctx(tmp_path):
    return ToolContext(workspace=tmp_path, full_access=True)


def test_office_files(tmp_path):
    c = ctx(tmp_path)
    tools.call(c, "create_docx", {"path": "a", "content": "# T\n- x\n| a | b |\n|---|---|\n| 1 | **2** |\ntext"})
    tools.call(c, "create_xlsx", {"path": "b.xlsx", "sheets": json.dumps({"S": [["n", "v"], ["a", 1], ["b", 2], ["t", "=SUM(B2:B3)"]]})})
    tools.call(c, "create_pptx", {"path": "c.pptx", "slides": json.dumps([{"title": "Bìa"}, {"title": "A", "bullets": ["1", "2"], "notes": "n"}])})
    from docx import Document
    from openpyxl import load_workbook
    from pptx import Presentation
    assert len(Document(tmp_path / "a.docx").tables) == 1
    assert load_workbook(tmp_path / "b.xlsx")["S"]["B4"].value == "=SUM(B2:B3)"
    assert len(Presentation(tmp_path / "c.pptx").slides) == 2


def to_trinh_paragraphs():
    return [
        {"layout": "two_columns", "left_width_pct": 40,
         "left_lines": [{"role": "parent_org", "text": "UBND THÀNH PHỐ ĐÀ NẴNG"}, {"role": "issuing_org", "text": "UBND PHƯỜNG HẢI CHÂU"}, {"role": "document_number", "text": "Số: 128/TTr-UBND"}],
         "right_lines": [{"role": "national_name", "text": "CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM"}, {"role": "motto", "text": "Độc lập - Tự do - Hạnh phúc"}, {"role": "place_date", "text": "Hải Châu, ngày 02 tháng 12 năm 2026"}]},
        {"role": "document_type_title", "text": "TỜ TRÌNH"},
        {"role": "summary", "text": "Về việc đề nghị cấp kinh phí tổ chức Hội nghị tổng kết năm 2026"},
        {"role": "recipient", "text": "Kính gửi: Ủy ban nhân dân thành phố Đà Nẵng"},
        {"role": "body", "text": "Căn cứ nhu cầu thực tế, UBND phường kính trình như sau:"},
        {"role": "section_heading", "text": "I. Sự cần thiết"},
        {"role": "body", "text": "Nội dung……"},
        {"layout": "two_columns", "left_width_pct": 50,
         "left_lines": [{"role": "recipients_label", "text": "Nơi nhận:"}, {"role": "recipients_item", "text": "- Như trên;"}, {"role": "recipients_item", "text": "- Lưu: VT."}],
         "right_lines": [{"role": "signature_authority", "text": "TM. ỦY BAN NHÂN DÂN"}, {"role": "signature_authority", "text": "CHỦ TỊCH"}, {"role": "signature_name", "text": "Nguyễn Văn A"}]},
    ]


def test_vanban_writer_and_review(tmp_path):
    import json
    c = ctx(tmp_path)
    out, ok = tools.call(c, "vanban_types", {"document_type_key": "TO_TRINH"})
    assert ok and "section_heading" in out and "two_columns" in out, out
    out, ok = tools.call(c, "vanban_write_docx", {"path": "tt", "document_type_key": "TO_TRINH", "paragraphs": json.dumps(to_trinh_paragraphs()), "ngan_theo_yeu_cau": True})
    assert ok and "CẢNH BÁO" not in out, out
    from docx import Document
    text = "\n".join(c.text for t in Document(tmp_path / "tt.docx").tables for r in t.rows for c in r.cells)
    assert "CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM" in text and "TM. ỦY BAN NHÂN DÂN" in text
    out, ok = tools.call(c, "review_vn_document", {"path": "tt.docx"})
    assert ok and "[LỖI]" not in out, out


def test_vanban_rejects_bad_role(tmp_path):
    import json
    out, ok = tools.call(ctx(tmp_path), "vanban_write_docx", {"path": "x", "document_type_key": "TO_TRINH", "paragraphs": json.dumps([{"role": "bogus", "text": "a"}])})
    assert not ok and "unknown_role" in out


def test_create_docx_refuses_administrative(tmp_path):
    c = ctx(tmp_path)
    out, ok = tools.call(c, "create_docx", {"path": "bc", "content": "# BÁO CÁO ĐỀ XUẤT CHỦ TRƯƠNG ĐẦU TƯ\nChủ đầu tư: UBND phường A\nNội dung."})
    assert not ok and "vanban_write_docx" in out and not (tmp_path / "bc.docx").exists()
    out, ok = tools.call(c, "create_docx", {"path": "bc", "content": "# BÁO CÁO ĐỀ XUẤT\nChủ đầu tư: UBND", "khong_phai_van_ban_hanh_chinh": True})
    assert ok
    out, ok = tools.call(c, "create_docx", {"path": "bt", "content": "# Báo cáo thực tập\nSinh viên: An"})
    assert ok


def test_vanban_gives_clear_error_for_string_lines(tmp_path):
    import json
    bad = [{"layout": "two_columns", "left_lines": ["……", "Số: ……/BC"], "right_lines": [{"role": "national_name", "text": "CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM"}]}]
    out, ok = tools.call(ctx(tmp_path), "vanban_write_docx", {"path": "x", "document_type_key": "BAO_CAO", "paragraphs": json.dumps(bad)})
    assert not ok and "left_lines[0]" in out and "object" in out and "AttributeError" not in out, out


def test_review_accepts_placeholder_signature(tmp_path):
    import json
    c = ctx(tmp_path)
    paras = to_trinh_paragraphs()
    paras[-1]["right_lines"] = [{"role": "signature_authority", "text": "……"}, {"role": "signature_name", "text": "……"}]
    out, ok = tools.call(c, "vanban_write_docx", {"path": "ph", "document_type_key": "TO_TRINH", "paragraphs": json.dumps(paras), "ngan_theo_yeu_cau": True})
    assert ok, out
    out, _ = tools.call(c, "review_vn_document", {"path": "ph.docx"})
    assert "[LỖI] Thẩm quyền ký" not in out, out


def test_ask_user_form_and_single(tmp_path):
    import json
    from argus.services.tools import ToolContext
    seen = {}
    def asker(q, o, form=None):
        seen.update(q=q, o=o, form=form)
        return json.dumps(["Có", "Word, Excel"]) if form else "A"
    c = ToolContext(workspace=tmp_path, asker=asker)
    out, ok = tools.call(c, "ask_user", {"questions": json.dumps([{"question": "Có số hiệu chưa?", "options": ["Có", "Chưa"]}, {"question": "Định dạng?", "options": ["Word", "Excel"], "multi": True}])})
    assert ok and len(seen["form"]) == 2 and seen["form"][1]["multi"] and "Có số hiệu chưa?: Có" in out and "Word, Excel" in out, out
    out, ok = tools.call(c, "ask_user", {"question": "Chọn?", "options": ["A", "B"]})
    assert ok and "A" in out and seen["form"] is None
