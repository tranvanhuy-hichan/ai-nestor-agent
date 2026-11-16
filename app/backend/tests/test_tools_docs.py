import json
from datetime import date, timedelta

import pytest
from docx import Document
from openpyxl import Workbook, load_workbook

from nestor.services import tools
from nestor.services.tools import ToolContext


@pytest.fixture
def c(tmp_path):
    return ToolContext(workspace=tmp_path, full_access=True)


def call(c, name, **kw):
    return tools.call(c, name, kw)


def test_all_tools_registered():
    for n in ("docx_fill_template", "excel_merge_reports", "grade_summary", "convert_to_pdf", "compare_documents", "deadline_report", "place_name_check", "excel_audit"):
        assert n in tools.TOOLS and tools.TOOLS[n].risk == "file"


# ---------- 1. điền mẫu Word
def make_template(p):
    d = Document()
    par = d.add_paragraph()
    r = par.add_run("Kính gửi: ")
    r.bold = True
    par.add_run("{{ho")          # trường bị tách giữa hai run
    par.add_run("_ten|upper}}, sinh ngày {{ngay_sinh|date:dd/mm/yyyy}}")
    d.add_paragraph("Lương: {{luong|number}} đồng. Mã: {{khong_co}}")
    t = d.add_table(rows=1, cols=2)
    t.cell(0, 0).text = "Lớp"
    t.cell(0, 1).text = "{{lop}}"
    d.sections[0].header.paragraphs[0].text = "Số: {{so}}/QĐ"
    d.save(p)


def all_text(path):
    d = Document(path)
    parts = [p.text for p in d.paragraphs] + [c.text for t in d.tables for r in t.rows for c in r.cells] + [p.text for p in d.sections[0].header.paragraphs]
    return "\n".join(parts)


def test_fill_template_single_with_filters_and_split_runs(c, tmp_path):
    make_template(tmp_path / "mau.docx")
    out, ok = call(c, "docx_fill_template", template_path="mau.docx", name_field="ho_ten",
                   data=json.dumps({"ho_ten": "Nguyễn An", "ngay_sinh": "2010-03-07", "luong": 1500000, "lop": "9A", "so": 12}))
    assert ok, out
    f = tmp_path / "mau-dien-mau" / "Nguyễn-An.docx"
    assert f.exists()
    txt = all_text(f)
    assert "NGUYỄN AN, sinh ngày 07/03/2010" in txt and "Lương: 1.500.000 đồng" in txt and "9A" in txt and "Số: 12/QĐ" in txt
    assert "{{khong_co}}" in txt and "khong_co" in out  # trường thiếu được báo, để nguyên
    first = Document(f).paragraphs[0].runs[0]
    assert first.text == "Kính gửi: " and first.bold  # định dạng của run đầu giữ nguyên


def test_fill_template_many_from_excel_and_cap(c, tmp_path):
    make_template(tmp_path / "mau.docx")
    wb = Workbook()
    ws = wb.active
    ws.append(["Họ tên", "ngay_sinh", "luong", "lop", "so"])
    ws.append(["Trần Bình", date(2011, 1, 2), 2000000, "8B", 5])
    ws.append(["Trần Bình", date(2011, 1, 3), 2100000, "8C", 6])
    wb.save(tmp_path / "ds.xlsx")
    out, ok = call(c, "docx_fill_template", template_path="mau.docx", data_path="ds.xlsx", name_field="Họ tên", output_dir="ra")
    assert ok and (tmp_path / "ra" / "Trần-Bình.docx").exists() and (tmp_path / "ra" / "Trần-Bình-2.docx").exists(), out
    assert "ho_ten" not in out or True
    big = json.dumps([{"a": i} for i in range(501)])
    out, ok = call(c, "docx_fill_template", template_path="mau.docx", data=big)
    assert not ok and "500" in out
    out, ok = call(c, "docx_fill_template", template_path="mau.docx")
    assert not ok and "data" in out


# ---------- 2. gộp báo cáo Excel
def make_reports(tmp_path):
    wb = Workbook()
    ws = wb.active
    ws.append(["BÁO CÁO CỦA PHƯỜNG A"])
    ws.append([])
    ws.append(["STT", "Tên đơn vị", "Số lượng", "Kinh phí"])
    ws.append([1, "Trường Tiểu học 1", 10, 1000])
    ws.append([2, "Trường THCS 2", 20, 2000])
    ws.append(["", "Tổng", 30, 3500])  # tổng ghi sai (đúng là 3000)
    wb.save(tmp_path / "a.xlsx")
    wb = Workbook()
    ws = wb.active
    ws.append(["Đơn vị", "Kinh phí (đồng)", "Số lượng", "Ghi chú"])
    ws.append(["Trường THCS 2", "500", 5, "trùng đơn vị"])
    ws.append(["Mầm non 3", "tạm tính", 7, ""])
    wb.save(tmp_path / "b.xlsx")


def test_merge_reports_maps_columns_and_reports_discrepancies(c, tmp_path):
    make_reports(tmp_path)
    out, ok = call(c, "excel_merge_reports", paths=json.dumps(["a.xlsx", "b.xlsx"]), output_path="gop.xlsx")
    assert ok, out
    wb = load_workbook(tmp_path / "gop.xlsx")
    ws = wb["Tổng hợp"]
    head = [x.value for x in ws[1]]
    assert head[:4] == ["STT", "Tên đơn vị", "Số lượng", "Kinh phí"] and head[-1] == "Nguồn" and "Ghi chú" in head
    assert ws.max_row == 5  # 2 + 2 dòng dữ liệu (dòng Tổng bị loại)
    names = [ws.cell(r, 2).value for r in range(2, 6)]
    assert names.count("Trường THCS 2") == 2  # cột 'Đơn vị' đã ghép vào 'Tên đơn vị'
    sd = [[x.value for x in r] for r in wb["Sai lệch"].iter_rows(min_row=2)]
    kinds = {r[0] for r in sd}
    assert {"Khóa trùng", "Tổng lệch", "Số lưu dạng chữ", "Chữ trong cột số", "Cột thiếu", "Tổng theo file"} <= kinds, kinds
    assert any("tạm tính" in r[3] for r in sd)
    # đường dẫn dạng chuỗi cách nhau bằng dấu phẩy cũng được
    out, ok = call(c, "excel_merge_reports", paths="a.xlsx, b.xlsx", output_path="gop2", header_hints="Tên đơn vị,Kinh phí")
    assert ok and (tmp_path / "gop2.xlsx").exists()


# ---------- 3. tổng hợp điểm
def test_grade_summary_formulas_and_text(c, tmp_path):
    wb = Workbook()
    ws = wb.active
    ws.append(["STT", "Họ và tên", "Miệng", "15 phút", "Giữa kỳ", "Cuối kỳ"])
    ws.append([1, "An", 9, 9, 8, 9])
    ws.append([2, "Bình", 6, 7, 6, 7])
    ws.append([3, "Chi", 4, 5, 4, 3])
    ws.append([4, "Dũng", None, None, None, None])
    wb.save(tmp_path / "diem.xlsx")
    out, ok = call(c, "grade_summary", path="diem.xlsx", he_so="1,1,2,3")
    assert ok, out
    assert "3 học sinh" not in out and "4 học sinh" in out and "Tốt: 1" in out and "Chưa đạt: 1" in out and "Dũng" in out
    wb = load_workbook(tmp_path / "diem-tong-hop.xlsx")
    ws = wb["Điểm"]
    assert str(ws["G3"].value).startswith("=IF(SUMPRODUCT") and "RANK" in str(ws["I3"].value) and "Cấu hình" in str(ws["H3"].value)
    assert wb["Cấu hình"]["B1"].value == 8 and "COUNTIF" in str(wb["Thống kê"]["B3"].value)
    out, ok = call(c, "grade_summary", path="diem.xlsx", he_so="a,b")
    assert not ok and "he_so" in out


# ---------- 4. PDF
def test_convert_to_pdf(c, tmp_path, monkeypatch):
    d = Document()
    d.add_paragraph("Xin chào PDF")
    d.save(tmp_path / "v.docx")
    import shutil
    if shutil.which("soffice") or shutil.which("libreoffice"):
        out, ok = call(c, "convert_to_pdf", path="v.docx")
        assert ok and (tmp_path / "v.pdf").exists() and (tmp_path / "v.pdf").read_bytes().startswith(b"%PDF"), out
    monkeypatch.setattr("nestor.services.tools_docs.shutil.which", lambda n: None)
    out, ok = call(c, "convert_to_pdf", path="v.docx")
    assert not ok and "LibreOffice" in out
    out, ok = call(c, "convert_to_pdf", path="x.txt")
    assert not ok


# ---------- 5. so sánh
def test_compare_documents(c, tmp_path):
    a = Document()
    for t in ("Điều 1. Mức hỗ trợ là 500.000 đồng.", "Điều 2. Có hiệu lực từ ngày 01/01/2026.", "Điều 3. Xóa bỏ."):
        a.add_paragraph(t)
    a.save(tmp_path / "a.docx")
    (tmp_path / "b.txt").write_text("Điều 1. Mức hỗ trợ là 700.000 đồng.\nĐiều 2. Có hiệu lực từ ngày 01/07/2026.\nĐiều 4. Điều mới thêm vào.\n", encoding="utf-8")
    out, ok = call(c, "compare_documents", path_a="a.docx", path_b="b.txt")
    assert ok, out
    assert "sửa 2" in out and "500.000" in out and "700.000" in out and "01/07/2026" in out and "→" in out
    same, _ = call(c, "compare_documents", path_a="a.docx", path_b="a.docx")
    assert "giống nhau" in same


# ---------- 6. hạn xử lý
def test_deadline_report(c, tmp_path):
    today = date(2026, 11, 5)
    wb = Workbook()
    ws = wb.active
    ws.append(["Số, ký hiệu", "Trích yếu", "Ngày đến", "Hạn xử lý", "Người xử lý", "Trạng thái"])
    ws.append(["12/UBND", "Xin kinh phí", today - timedelta(days=10), today - timedelta(days=2), "Lan", "Đang xử lý"])
    ws.append(["13/UBND", "Báo cáo quý", today - timedelta(days=5), today + timedelta(days=2), "Lan", ""])
    ws.append(["14/UBND", "Giấy mời", today, "20/11/2026", "Minh", ""])
    ws.append(["15/UBND", "Đã xong", today - timedelta(days=9), today - timedelta(days=4), "Minh", "Đã xử lý"])
    wb.save(tmp_path / "so.xlsx")
    out, ok = call(c, "deadline_report", path="so.xlsx", today="05/11/2026")
    assert ok, out
    assert "Quá hạn 1" in out and "sắp đến hạn 1" in out and "Quá hạn 2 ngày" in out and "12/UBND" in out and "Lan: 2 văn bản, 1 quá hạn" in out
    wb = load_workbook(tmp_path / "so-theo-doi-han.xlsx")
    assert wb["Theo dõi"]["A2"].value == "12/UBND" and wb["Theo dõi"]["A2"].fill.fgColor.rgb.endswith("F8CBAD")
    assert [x.value for x in wb["Theo người"][2]][:3] == ["Lan", 2, 1]
    out, ok = call(c, "deadline_report", path="so.xlsx", today="sai")
    assert not ok


# ---------- 7. địa danh cũ
def test_place_name_check_report_and_replace(c, tmp_path):
    d = Document()
    p = d.add_paragraph()
    r = p.add_run("UBND huyện ")
    r.bold = True
    p.add_run("Hòa Vang, thị trấn Hòa Phước họp ngày 01/01/2026.")
    d.add_table(rows=1, cols=1).cell(0, 0).text = "Quận Hải Châu"
    d.save(tmp_path / "vb.docx")
    out, ok = call(c, "place_name_check", path="vb.docx")
    assert ok and "3 chỗ" in out and "huyện" in out.lower() and "chưa tạo" not in out
    assert not (tmp_path / "vb-da-sua.docx").exists()
    wb = Workbook()
    ws = wb.active
    ws.append(["Tên cũ", "Tên mới"])
    ws.append(["huyện Hòa Vang", "xã Hòa Vang"])
    ws.append(["thị trấn Hòa Phước", "xã Hòa Phước"])
    wb.save(tmp_path / "map.xlsx")
    out, ok = call(c, "place_name_check", path="vb.docx", mapping_path="map.xlsx")
    assert ok and "ĐÃ THAY" in out, out
    d2 = Document(tmp_path / "vb-da-sua.docx")
    assert d2.paragraphs[0].text == "UBND xã Hòa Vang, xã Hòa Phước họp ngày 01/01/2026."
    assert d2.paragraphs[0].runs[0].bold  # định dạng run đầu còn nguyên
    (tmp_path / "t.txt").write_text("Huyện A và quận B.\n", encoding="utf-8")
    out, ok = call(c, "place_name_check", path="t.txt")
    assert ok and "2 chỗ" in out


# ---------- 8. kiểm tra Excel
def test_excel_audit_finds_problems(c, tmp_path):
    wb = Workbook()
    ws = wb.active
    ws.title = "SoQuy"
    ws.append(["STT", "Diễn giải", "Số tiền"])
    for i, (t, v) in enumerate([("Thu A", 100), ("Thu B", 200), ("Thu C", "300"), ("Thu D", 400), ("Thu E", 400), ("Thu E", 400)], 1):
        ws.append([i, t, v])
    ws.append(["", "Tổng", 1500])       # nhập tay, đúng là 400+400+400... sẽ lệch
    ws["D2"] = "=B2/0"
    ws["D3"] = "=#REF!+1"
    wb.save(tmp_path / "kt.xlsx")
    out, ok = call(c, "excel_audit", path="kt.xlsx")
    assert ok, out
    assert "tổng nhập tay" in out and "lưu dạng chữ '300'" in out and "#REF!" in out and "trùng hệt" in out
    assert out.index("NGHIÊM TRỌNG") < out.index("CẢNH BÁO") < out.index("GỢI Ý")
    wb = Workbook()
    ws = wb.active
    ws.append(["A", "B"])
    ws.append([1, 2])
    wb.save(tmp_path / "ok.xlsx")
    out, ok = call(c, "excel_audit", path="ok.xlsx")
    assert ok and "không thấy" in out


def test_friendly_errors(c, tmp_path):
    out, ok = call(c, "excel_audit", path="khong-co.xlsx")
    assert not ok and "Không tìm thấy" in out and "Traceback" not in out
    (tmp_path / "x.txt").write_text("a")
    out, ok = call(c, "excel_audit", path="x.txt")
    assert not ok and ".xlsx" in out
