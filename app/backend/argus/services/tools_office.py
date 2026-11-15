"""Tool tao file van phong that: .docx, .xlsx (co cong thuc), .pptx va van ban hanh chinh theo ND 30/2020."""
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

from ..core import config as cfgmod
from .tools import DENIED, _resolve, tool

MAX_ROWS = 50000


def _out(ctx, path: str, ext: str) -> Path:
    if not path or not path.strip():
        raise ValueError("Thiếu đường dẫn file.")
    p = _resolve(ctx, path if path.lower().endswith(ext) else path + ext, "write")
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def _json(value, what: str):
    if isinstance(value, str):
        try:
            return json.loads(value)
        except json.JSONDecodeError as e:
            raise ValueError(f"{what} không phải JSON hợp lệ: {e}") from e
    return value


def _fill_docx(doc, content: str) -> None:
    """Markdown don gian: #/##/### tieu de, '- ' gach dau dong, '1. ' danh so, bang '| a | b |', con lai la doan van. **dam** duoc ho tro."""
    import re
    lines, i = content.splitlines(), 0

    def runs(par, text):
        for k, part in enumerate(re.split(r"\*\*(.+?)\*\*", text)):
            if part:
                par.add_run(part).bold = bool(k % 2)

    while i < len(lines):
        ln = lines[i].rstrip()
        if ln.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r":?-{2,}:?", c) for c in cells):
                    rows.append(cells)
                i += 1
            if rows:
                t = doc.add_table(rows=len(rows), cols=max(len(r) for r in rows))
                t.style = "Table Grid"
                for r, row in enumerate(rows):
                    for c, v in enumerate(row):
                        cell = t.cell(r, c)
                        cell.text = v
                        if r == 0:
                            for run in cell.paragraphs[0].runs:
                                run.bold = True
            continue
        m = re.match(r"(#{1,3})\s+(.*)", ln)
        if m:
            doc.add_heading(m.group(2), level=len(m.group(1)))
        elif re.match(r"[-*]\s+", ln):
            runs(doc.add_paragraph(style="List Bullet"), re.sub(r"^[-*]\s+", "", ln))
        elif re.match(r"\d+[.)]\s+", ln):
            runs(doc.add_paragraph(style="List Number"), re.sub(r"^\d+[.)]\s+", "", ln))
        elif ln.strip():
            runs(doc.add_paragraph(), ln)
        i += 1


_ADMIN_TITLE = re.compile(r"^\s*#*\s*\**\s*(BÁO CÁO|TỜ TRÌNH|CÔNG VĂN|QUYẾT ĐỊNH|BIÊN BẢN|KẾ HOẠCH|THÔNG BÁO|GIẤY MỜI|NGHỊ QUYẾT|CÔNG ĐIỆN|GIẤY GIỚI THIỆU|CHỈ THỊ|KẾT LUẬN|QUY CHẾ|QUY ĐỊNH|HƯỚNG DẪN|ĐỀ ÁN|PHƯƠNG ÁN)\b", re.M | re.I)
_ADMIN_HINT = re.compile(r"(Kính gửi|UBND|Ủy ban nhân dân|Cộng hòa xã hội|Chủ đầu tư|cơ quan ban hành|Nơi nhận|Căn cứ (Luật|Nghị định|Thông tư|Quyết định))", re.I)


def _looks_administrative(text: str) -> str:
    """Nhan dien van ban hanh chinh: tieu de la ten loai van ban + co dau hieu co quan/nha nuoc. Tra ve ly do ngan, rong = khong."""
    head = text.strip().splitlines()[:3]
    m = next((x for x in (_ADMIN_TITLE.match(h) for h in head) if x), None)
    h = _ADMIN_HINT.search(text)
    if m and h:
        return f"tiêu đề '{m.group(1)}' và có '{h.group(1)}'"
    return ""


@tool("create_docx", "Dựng file Word (.docx) thật bằng blocks có cấu trúc native: tiêu đề, đoạn văn, danh sách, bảng. Ưu tiên blocks, không dùng Markdown cho yêu cầu mới. Dùng cho báo cáo, biên bản, hợp đồng. KHÔNG dùng cho văn bản hành chính của cơ quan nhà nước (công văn, tờ trình, quyết định, báo cáo gửi cấp trên, biên bản, kế hoạch, thông báo, giấy mời): loại đó phải dùng vanban_types rồi vanban_write_docx để đúng thể thức NĐ 30/2020.",
      {"path": ("string", "đường dẫn file, vd bao-cao.docx"), "content": ("string", "Đầu vào Markdown cũ, chỉ để tương thích. Với yêu cầu mới dùng blocks."), "blocks": ("string", 'JSON mảng khối Word native: [{"type":"heading","text":"Mục","level":1},{"type":"paragraph","text":"Nội dung đầy đủ"},{"type":"bullets","items":["Ý 1","Ý 2"]},{"type":"table","rows":[["Cột A","Cột B"],["Dữ liệu","Giá trị"]]}]. Không dùng ký hiệu Markdown; paragraph có thể dùng runs:[{text,bold,italic}].'), "title": ("string", "tiêu đề lớn đầu trang (tùy chọn)"),
       "khong_phai_van_ban_hanh_chinh": ("boolean", "chỉ đặt true khi chắc chắn đây KHÔNG phải văn bản hành chính nhà nước")},
      required=["path"], risk="file")
def create_docx(ctx, path, content="", title="", khong_phai_van_ban_hanh_chinh=False, blocks=""):
    from docx import Document
    from .docx_blocks import compose, decorate, validate, text_of
    native = _json(blocks, 'blocks') if blocks else None
    if native is not None:
        validate(native)
        if content: raise ValueError('Chỉ dùng blocks hoặc content, không trộn hai nguồn nội dung.')
        content_for_review = text_of(native)
    else:
        content_for_review = content
        if not content.strip(): raise ValueError('Cần blocks chứa nội dung tài liệu.')
        if ctx.session_id:
            from . import sessions
            if (sessions.get(ctx.session_id) or {}).get('assistant'):
                raise ValueError('Yêu cầu mới phải dựng Word native bằng blocks (heading, paragraph, bullets, table), không chuyển Markdown. Giữ đầy đủ nội dung và gọi lại với blocks.')
    if not khong_phai_van_ban_hanh_chinh:
        why = _looks_administrative(f"{title}\n{content_for_review}")
        if why:
            raise ValueError(f"Nội dung này giống văn bản hành chính ({why}) nên KHÔNG tạo bằng create_docx vì sẽ sai thể thức NĐ 30/2020. "
                             "Hãy gọi vanban_types(document_type_key=...) rồi vanban_write_docx để có quốc hiệu, tiêu ngữ, số ký hiệu, nơi nhận, chữ ký đúng chuẩn. "
                             "Nếu thật sự không phải văn bản hành chính nhà nước, gọi lại với khong_phai_van_ban_hanh_chinh=true.")
    p = _out(ctx, path, ".docx")
    doc = Document()
    from docx.shared import Mm, Pt, RGBColor
    section = doc.sections[0]
    section.page_width, section.page_height = Mm(210), Mm(297)
    section.top_margin = section.bottom_margin = Mm(20)
    section.left_margin = section.right_margin = Mm(22)
    from docx.oxml.ns import qn
    for style_name in ['Normal', 'Title', 'Heading 1', 'Heading 2', 'Heading 3', 'List Bullet', 'List Number']:
        fonts = doc.styles[style_name].element.get_or_add_rPr().get_or_add_rFonts()
        for key in list(fonts.attrib):
            if 'theme' in key.lower(): del fonts.attrib[key]
        for script in ('ascii', 'hAnsi', 'eastAsia', 'cs'):
            fonts.set(qn('w:' + script), 'Arial')
    normal = doc.styles['Normal']
    normal.font.name, normal.font.size = 'Arial', Pt(11)
    normal.paragraph_format.line_spacing = 1.15
    normal.paragraph_format.space_after = Pt(6)
    for level, size in [(1,16),(2,14),(3,12)]:
        heading = doc.styles[f'Heading {level}']
        heading.font.name, heading.font.size = 'Arial', Pt(size)
        heading.font.color.rgb = RGBColor.from_string('17365D')
        heading.paragraph_format.keep_with_next = True
    if title:
        cover = doc.add_heading(title, 0)
        cover.paragraph_format.space_after = Pt(14)
        for run in cover.runs:
            run.font.name = 'Arial'
            run.font.size = Pt(24)
            run.font.color.rgb = RGBColor.from_string('17365D')
        from docx.oxml import OxmlElement
        from docx.oxml.ns import qn
        borders = OxmlElement('w:pBdr')
        bottom = OxmlElement('w:bottom')
        for key, value in [('val','single'),('sz','12'),('color','17365D'),('space','8')]:
            bottom.set(qn('w:' + key), value)
        borders.append(bottom)
        cover._p.get_or_add_pPr().append(borders)
    if native is not None:
        compose(doc, native)
    else:
        _fill_docx(doc, content)
    decorate(doc)
    doc.save(p)
    return f"Đã tạo {p.name} ({p.stat().st_size} byte) tại {p}."


@tool("create_xlsx", "Tạo file Excel (.xlsx) thật. 'sheets' là JSON {\"Tên sheet\": [[hàng1...],[hàng2...]]}; ô là chuỗi bắt đầu bằng '=' sẽ thành công thức sống (vd \"=SUM(B2:B10)\"). Hàng đầu được in đậm làm tiêu đề.",
      {"path": ("string", "đường dẫn file, vd tong-hop.xlsx"), "sheets": ("string", "JSON: tên sheet -> mảng các hàng")}, risk="file")
def create_xlsx(ctx, path, sheets):
    from openpyxl import Workbook
    from openpyxl.styles import Font
    from openpyxl.utils import get_column_letter
    data = _json(sheets, "sheets")
    if not isinstance(data, dict) or not data:
        raise ValueError("sheets phải là object {tên sheet: [[...]]}.")
    if sum(len(r) for r in data.values()) > MAX_ROWS:
        raise ValueError(f"Quá nhiều hàng (tối đa {MAX_ROWS}).")
    p = _out(ctx, path, ".xlsx")
    wb = Workbook()
    wb.remove(wb.active)
    for name, rows in data.items():
        ws = wb.create_sheet(str(name)[:31] or "Sheet")
        for row in rows:
            ws.append(row if isinstance(row, list) else [row])
        from openpyxl.styles import PatternFill, Alignment
        ws.freeze_panes = 'A2'
        if ws.max_row > 1:
            ws.auto_filter.ref = ws.dimensions
        for c in ws[1]:
            c.font = Font(bold=True, color='FFFFFF')
            c.fill = PatternFill('solid', fgColor='17365D')
            c.alignment = Alignment(vertical='center', wrap_text=True)
        ws.row_dimensions[1].height = 30
        ws.print_title_rows = '1:1'
        ws.sheet_properties.pageSetUpPr.fitToPage = True
        ws.page_setup.paperSize = ws.PAPERSIZE_A4
        ws.page_setup.orientation = 'landscape' if ws.max_column > 6 else 'portrait'
        ws.page_setup.fitToWidth, ws.page_setup.fitToHeight = 1, 0
        for col in range(1, ws.max_column + 1):
            width = max((len(str(c.value)) for c in ws[get_column_letter(col)] if c.value is not None and not str(c.value).startswith("=")), default=8)
            ws.column_dimensions[get_column_letter(col)].width = min(max(width + 2, 8), 60)
    wb.save(p)
    return f"Đã tạo {p.name} với {len(data)} sheet tại {p}."


@tool("create_pptx", "Tạo file PowerPoint (.pptx) thật. 'slides' là JSON mảng [{\"title\": \"...\", \"bullets\": [\"...\"], \"notes\": \"ghi chú diễn giả\"}]. Slide đầu có bullets rỗng sẽ là slide bìa.",
      {"path": ("string", "đường dẫn file, vd bao-cao.pptx"), "slides": ("string", "JSON mảng slide")}, risk="file")
def create_pptx(ctx, path, slides):
    from pptx import Presentation
    data = _json(slides, "slides")
    if not isinstance(data, list) or not data:
        raise ValueError("slides phải là mảng không rỗng.")
    p = _out(ctx, path, ".pptx")
    prs = Presentation()
    for k, s in enumerate(data):
        bullets = s.get("bullets") or []
        cover = k == 0 and not bullets
        sl = prs.slides.add_slide(prs.slide_layouts[0 if cover else 1])
        sl.shapes.title.text = s.get("title", "")
        if cover:
            if len(sl.placeholders) > 1:
                sl.placeholders[1].text = s.get("subtitle", "")
        else:
            tf = sl.placeholders[1].text_frame
            tf.text = str(bullets[0]) if bullets else ""
            for b in bullets[1:]:
                tf.add_paragraph().text = str(b)
        if s.get("notes"):
            sl.notes_slide.notes_text_frame.text = s["notes"]
    prs.save(p)
    return f"Đã tạo {p.name} với {len(data)} slide tại {p}."


VANBAN_RULES = """QUY TẮC (skill van-ban-hanh-chinh, NĐ 30/2020):
1. Chọn đúng 1 document_type_key trong danh sách; dựng `paragraphs` theo ĐÚNG thứ tự `structure` của loại đó. Mỗi đoạn có `role` hợp lệ (không tự bịa role). Định dạng (font, cỡ, canh lề, đậm/nghiêng) do writer tự áp theo role, KHÔNG tự chỉnh.
2. Không bịa số văn bản, ngày ký, người ký, số tiền, căn cứ pháp lý: thiếu thì để "……".
3. Mỗi role một dòng một `text` (national_name, motto, issuing_org, recipient...). KHÔNG tự tách một tên cơ quan thành nhiều dòng. Riêng `summary` nhiều ý thì mỗi ý một item `summary`, mọi dòng trừ dòng cuối đặt "no_underline": true.
4. Đầu trang (mỗi dòng trong left_lines/right_lines là OBJECT {"role","text"}, KHÔNG phải chuỗi): {"layout":"two_columns","left_lines":[parent_org, issuing_org, document_number],"right_lines":[national_name, motto, place_date]}, left_width_pct 35-45 để quốc hiệu nằm trọn 1 dòng.
5. Cuối trang: Nơi nhận và chữ ký LUÔN cạnh nhau: {"layout":"two_columns","left_lines":[recipients_label, recipients_item...],"right_lines":[signature_authority, signature_name]}, left_width_pct 45-50 (kể cả khi chỉ 1 người ký). Từ 3 khối trở lên dùng multi_columns. Biên bản: THƯ KÝ trái, CHỦ TỌA phải.
6. Mục La Mã "I.", "II." dùng role section_heading (đậm), KHÔNG dùng body. Từng văn bản pháp luật dẫn chiếu dùng legal_basis (nghiêng). Nhãn "Phần thứ nhất"/"Chương I" dùng phan_chuong_label.
7. Bảng số liệu: đúng 1 item layout "table" với table_headers (hoặc table_header_groups) + toàn bộ dòng trong một mảng table_rows. Bảng từ ~6 cột: "section_orientation":"landscape" trên item đó, rồi đặt lại "portrait" ở item sau. Phụ lục luôn bắt đầu trang mới ("page_break_before": true), trừ item đổi hướng giấy.
8. Công văn (CONG_VAN): không có document_type_title, dùng summary_cong_van. Thông báo: không có legal_basis. Ký thay/thừa lệnh: thêm tiền tố TM./KT./TL./TUQ. vào signature_authority, chỉ khi người ký không phải người đứng đầu.
9. Gọi vanban_write_docx đúng một lần; đọc kết quả (applied/cảnh báo thiếu role) để đối chiếu, nếu lỗi sửa đúng chỗ rồi gọi lại tối đa 1 lần. Xong thì gọi review_vn_document. KHÔNG tự render ảnh/PDF để soi lại."""


_LINE_HELP = ('Mỗi dòng trong left_lines/right_lines/columns[].lines phải là OBJECT {"role": "...", "text": "..."}, KHÔNG phải chuỗi. '
              'Ví dụ đầu trang: {"layout":"two_columns","left_width_pct":40,"left_lines":[{"role":"issuing_org","text":"UBND PHƯỜNG A"},{"role":"document_number","text":"Số: ……/BC-UBND"}],'
              '"right_lines":[{"role":"national_name","text":"CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM"},{"role":"motto","text":"Độc lập - Tự do - Hạnh phúc"},{"role":"place_date","text":"……, ngày …… tháng …… năm ……"}]}')


def _check_paragraphs(paras) -> None:
    """Bao loi ro rang (vi tri + cach sua) thay vi de writer nem AttributeError kho hieu."""
    if not isinstance(paras, list) or not paras:
        raise ValueError("paragraphs phải là JSON mảng không rỗng.")
    errs = []

    def line(path, ln):
        if not isinstance(ln, dict):
            errs.append(f"{path} là {type(ln).__name__} ({str(ln)[:40]!r}) nhưng phải là object có role và text")
        elif not str(ln.get("role") or "").strip():
            errs.append(f"{path} thiếu role")

    for i, it in enumerate(paras):
        base = f"paragraphs[{i}]"
        if not isinstance(it, dict):
            errs.append(f"{base} phải là object, đang là {type(it).__name__}")
            continue
        layout = it.get("layout") or "paragraph"
        if layout == "two_columns":
            for side in ("left_lines", "right_lines"):
                if not isinstance(it.get(side), list) or not it.get(side):
                    errs.append(f"{base}.{side} phải là mảng không rỗng")
                    continue
                for j, ln in enumerate(it[side]):
                    line(f"{base}.{side}[{j}]", ln)
        elif layout == "multi_columns":
            for j, col in enumerate(it.get("columns") or []):
                lines = col.get("lines") if isinstance(col, dict) else col
                for k, ln in enumerate(lines or []):
                    line(f"{base}.columns[{j}].lines[{k}]", ln)
        elif layout == "table":
            if not it.get("table_rows") or not (it.get("table_headers") or it.get("table_header_groups")):
                errs.append(f"{base} (table) cần table_headers (hoặc table_header_groups) và table_rows")
        elif layout == "paragraph":
            if not str(it.get("role") or "").strip():
                errs.append(f"{base} thiếu role")
            if not isinstance(it.get("text", ""), str):
                errs.append(f"{base}.text phải là chuỗi")
        else:
            errs.append(f"{base}.layout '{layout}' không hợp lệ (paragraph, two_columns, multi_columns, table)")
    if errs:
        raise ValueError("paragraphs sai cấu trúc:\n- " + "\n- ".join(errs[:12]) + "\n" + _LINE_HELP)


def _vanban():
    from .vanban import writer
    return writer


def _required_roles(structure: list[str]) -> list[str]:
    out = []
    for item in structure or []:
        if item.endswith(("?", "*")):
            continue
        out.append(item.rstrip("+").split(":")[0])
    return out


@tool("vanban_types", "BƯỚC 1 khi soạn văn bản hành chính: trả về các loại văn bản (document_type_key, cấu trúc role bắt buộc theo Mẫu NĐ 30/2020) và quy tắc dựng `paragraphs` cho vanban_write_docx. Gọi trước khi viết văn bản.",
      {"document_type_key": ("string", "chỉ lấy một loại, vd TO_TRINH, CONG_VAN (bỏ trống để liệt kê tất cả)")}, required=[], risk="safe")
def vanban_types(ctx, document_type_key=""):
    w = _vanban()
    info = w._list_document_types()
    types = info["types"]
    if document_type_key:
        key = document_type_key.strip().upper()
        if key not in types:
            raise ValueError(f"Không có loại '{document_type_key}'. Có: {', '.join(types)}")
        extra = (w.DOCUMENT_TYPES.get("types") or {}).get(key, {}).get("ghi_chu", "")
        return json.dumps({key: types[key], "ghi_chu": extra}, ensure_ascii=False, indent=1) + "\n\n" + VANBAN_RULES
    brief = {k: v["ten_day_du"] for k, v in types.items()}
    return json.dumps({"types": brief, "roles": info["roles"]}, ensure_ascii=False) + "\nGọi lại vanban_types(document_type_key=...) để xem cấu trúc chi tiết.\n\n" + VANBAN_RULES


_HEAD_LEFT = ("parent_org", "issuing_org", "document_number")
_HEAD_RIGHT = ("national_name", "motto", "place_date")
_FOOT_LEFT = ("recipients_label", "recipients_item")
_FOOT_RIGHT = ("signature_authority", "signature_name")


def _is_plain(it) -> bool:
    return isinstance(it, dict) and (it.get("layout") or "paragraph") == "paragraph" and bool(it.get("role"))


def _two_col_has(paras, roles) -> bool:
    for it in paras:
        if isinstance(it, dict) and it.get("layout") == "two_columns":
            for side in ("left_lines", "right_lines"):
                if any(isinstance(l, dict) and l.get("role") in roles for l in it.get(side) or []):
                    return True
    return False


def _normalize_layout(paras, key: str):
    """Model hay xep quoc hieu, co quan, so, ngay thang va noi nhan/chu ky thanh cac doan doc: ghep lai thanh khoi hai cot dung the thuc NĐ 30
    (co quan + so + trich yeu cong van ben trai; quoc hieu, tieu ngu, dia danh ngay thang ben phai; noi nhan ben trai, chu ky ben phai). Tra ve (paras moi, ghi chu)."""
    if not isinstance(paras, list):
        return paras, []
    out, notes = list(paras), []
    left_h = _HEAD_LEFT + (("summary_cong_van",) if key == "CONG_VAN" else ())
    blocks = [("đầu văn bản (cơ quan/số bên trái, quốc hiệu/ngày tháng bên phải)", left_h, _HEAD_RIGHT, 40)]
    if key != "BIEN_BAN":
        blocks.append(("nơi nhận (trái) và chữ ký (phải)", _FOOT_LEFT, _FOOT_RIGHT, 50))
    for label, lroles, rroles, pct in blocks:
        allr = set(lroles) | set(rroles)
        if _two_col_has(out, allr):
            continue
        idx = [i for i, it in enumerate(out) if _is_plain(it) and it.get("role") in allr]
        left = [out[i] for i in idx if out[i]["role"] in lroles]
        right = [out[i] for i in idx if out[i]["role"] in rroles]
        if not left or not right:
            continue
        first = idx[0]
        merged = {"layout": "two_columns", "left_width_pct": pct, "left_lines": [{"role": x["role"], "text": x.get("text", "")} for x in left], "right_lines": [{"role": x["role"], "text": x.get("text", "")} for x in right]}
        drop = set(idx)
        out = [merged if i == first else it for i, it in enumerate(out) if i == first or i not in drop]
        notes.append(label)
    return out, notes


_DEPTH_MIN = {**{k: 450 for k in ("TO_TRINH", "BAO_CAO", "BAO_CAO_CO_BANG", "KE_HOACH", "DE_AN", "DU_AN", "CHUONG_TRINH", "PHUONG_AN", "HUONG_DAN", "NGHI_QUYET", "QUY_CHE", "QUY_DINH", "CHI_THI", "THONG_CAO")},
              **{k: 170 for k in ("CONG_VAN", "THONG_BAO", "QUYET_DINH_TRUC_TIEP", "QUYET_DINH_GIAN_TIEP", "VAN_BAN_CO_TEN_LOAI")}}


def _check_depth(paras, key: str) -> None:
    """Chan ban chi co khung: van ban hanh chinh thuc chat phai du dai noi dung. Gioi han tu theo loai."""
    need = _DEPTH_MIN.get(key)
    if not need:
        return
    words = 0
    placeholders = 0
    for it in paras if isinstance(paras, list) else []:
        if not isinstance(it, dict):
            continue
        texts = [it.get("text")] if it.get("layout", "paragraph") == "paragraph" else []
        texts += [c for row in it.get("table_rows") or [] for c in (row if isinstance(row, list) else [row])]
        for t in texts:
            if t:
                words += len(str(t).split())
                placeholders += str(t).count("cần xác nhận")
    if words < need:
        raise ValueError(f"Nội dung mới có khoảng {words} từ, quá ngắn cho loại {key} (cần tối thiểu khoảng {need} từ). Đây mới là cái khung, CHƯA đạt. "
                         "Hãy viết lại ĐẦY ĐỦ từng phần thành câu và đoạn có lập luận (sự cần thiết với số liệu thực tế, căn cứ pháp lý đã tra cứu, nội dung/quy mô/giải pháp cụ thể, tổ chức thực hiện, kiến nghị rõ ràng), dùng thông tin đã tra bằng web_search/web_fetch, rồi gọi lại vanban_write_docx. "
                         "Không dùng vài gạch đầu dòng ngắn cho phần nội dung chính.")
    if placeholders > 6:
        raise ValueError(f"Có {placeholders} chỗ ghi '(dự kiến, cần xác nhận)': quá nhiều, văn bản như chưa viết. Chỉ gắn ghi chú đó cho tối đa vài con số then chốt; những chỗ khác hãy viết nội dung cụ thể hoặc câu định tính dựa trên thông tin đã tra cứu.")


@tool("vanban_write_docx", "BƯỚC 2: tạo file .docx văn bản hành chính ĐÚNG thể thức NĐ 30/2020 từ danh sách đoạn có role tường minh. Role không hợp lệ bị từ chối. 'paragraphs' là JSON mảng [{\"role\":\"national_name\",\"text\":\"...\"}, {\"layout\":\"two_columns\",\"left_lines\":[...],\"right_lines\":[...]}, ...]. Đọc quy tắc từ vanban_types trước.",
      {"path": ("string", "đường dẫn file đầu ra, vd to-trinh.docx"), "document_type_key": ("string", "vd TO_TRINH, CONG_VAN, QUYET_DINH_TRUC_TIEP, BIEN_BAN"),
       "paragraphs": ("string", "JSON mảng các đoạn/khối"), "orientation": ("string", "portrait (mặc định) hoặc landscape cho cả văn bản"),
       "ngan_theo_yeu_cau": ("boolean", "chỉ đặt true khi người dùng yêu cầu rõ một văn bản rất ngắn; mặc định false và hệ thống từ chối bản chỉ có khung")},
      required=["path", "document_type_key", "paragraphs"], risk="file")
def vanban_write_docx(ctx, path, document_type_key, paragraphs, orientation=None, ngan_theo_yeu_cau=False):
    w = _vanban()
    paras = _json(paragraphs, "paragraphs")
    key = document_type_key.strip().upper()
    paras, merged_notes = _normalize_layout(paras, key)
    _check_paragraphs(paras)
    p = _out(ctx, path, ".docx")
    spec = (w._list_document_types()["types"]).get(key)
    if not spec:
        raise ValueError(f"document_type_key '{document_type_key}' không hợp lệ. Gọi vanban_types để xem danh sách.")
    w.ALLOWED_ROOT = str(p.parent.resolve())
    try:
        res = w._write_docx(None, p.name, paras, key, orientation or None)
    except ValueError as e:
        raise ValueError(f"Writer từ chối: {e}") from e
    except (AttributeError, KeyError, TypeError) as e:
        raise ValueError(f"Cấu trúc paragraphs chưa đúng ({type(e).__name__}: {e}). {_LINE_HELP}") from e
    if not ngan_theo_yeu_cau:
        try:
            _check_depth(paras, key)
        except ValueError:
            p.unlink(missing_ok=True)
            raise
    have = {a.get("role") for a in res.get("applied") or [] if isinstance(a, dict)}
    missing = [r for r in _required_roles(spec.get("structure") or []) if r not in have]
    summary = " | ".join(f"{a.get('role')}" for a in (res.get("applied") or [])[:60] if isinstance(a, dict))
    out = f"Đã tạo {res['file_name']} ({res['file_size']} byte) tại {res['file_path']} (loại {key}, khổ A4).\nCác role đã áp: {summary}"
    if merged_notes:
        out += "\nĐã tự ghép thành khối hai cột đúng thể thức: " + "; ".join(merged_notes) + ". Lần sau dùng layout two_columns như mẫu trong templates/."
    if missing:
        out += f"\nCẢNH BÁO: thiếu role bắt buộc theo Mẫu NĐ 30: {', '.join(missing)}. Bổ sung (hoặc để '……') rồi gọi lại tối đa 1 lần."
    return out


# ---- Rà thể thức -------------------------------------------------------------------------------
_OLD_LEVELS = re.compile(r"\b(huyện|thị xã|thị trấn|quận)\b", re.IGNORECASE)
_SIGN = re.compile(r"(TM\.|KT\.|TUQ\.|TL\.|Q\.|CHỦ TỊCH|GIÁM ĐỐC|TRƯỞNG|BÍ THƯ|CHÁNH|PHÓ|THỦ TRƯỞNG|TỔNG GIÁM ĐỐC)")


def _docx_text(doc) -> tuple[str, list]:
    parts = [p.text for p in doc.paragraphs]
    runs = [r for p in doc.paragraphs for r in p.runs]
    for t in doc.tables:
        for row in t.rows:
            for cell in row.cells:
                for p in cell.paragraphs:
                    parts.append(p.text)
                    runs.extend(p.runs)
    return "\n".join(x for x in parts if x.strip()), runs


@tool("review_vn_document", "Rà thể thức một file .docx văn bản hành chính theo NĐ 30/2020: quốc hiệu, tiêu ngữ, số ký hiệu, địa danh ngày tháng, trích yếu, nơi nhận, thẩm quyền ký, font chữ, địa danh/cấp hành chính cũ. Trả về danh sách [OK]/[LỖI]/[CẢNH BÁO].",
      {"path": ("string", "đường dẫn file .docx cần rà")}, risk="file")
def review_vn_document(ctx, path):
    from docx import Document
    p = _resolve(ctx, path, "read")
    if not p.is_file():
        raise FileNotFoundError(f"Không tìm thấy file: {path}")
    text, runs = _docx_text(Document(p))
    low = text.lower()
    checks = [
        ("Quốc hiệu", "CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM" in text.upper(), "thiếu dòng 'CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM'"),
        ("Tiêu ngữ", "độc lập - tự do - hạnh phúc" in re.sub(r"\s*[-–]\s*", " - ", low), "thiếu 'Độc lập - Tự do - Hạnh phúc'"),
        ("Số, ký hiệu", bool(re.search(r"Số:\s*(\d+|…+|\.{2,})\s*/\s*\S+", text)), "thiếu 'Số: .../KÝ-HIỆU' (vd Số: 128/TTr-UBND)"),
        ("Địa danh, ngày tháng", bool(re.search(r"ngày\s+\S+\s+tháng\s+\S+\s+năm\s+\S+", low)), "thiếu 'Địa danh, ngày ... tháng ... năm ...'"),
        ("Trích yếu", bool(re.search(r"V/v|Về việc|TỜ TRÌNH|BÁO CÁO|QUYẾT ĐỊNH|THÔNG BÁO|KẾ HOẠCH|BIÊN BẢN|NGHỊ QUYẾT", text)), "thiếu tên loại văn bản hoặc trích yếu (V/v, Về việc)"),
        ("Nơi nhận", "nơi nhận" in low, "thiếu khối 'Nơi nhận:'"),
        ("Thẩm quyền ký", bool(_SIGN.search(text)) or bool(re.search(r"(Nơi nhận.*?)(…{2,}|\.{4,})", text[-600:], re.S)), "thiếu chức danh người ký (TM./KT./TUQ./TL. hoặc chức vụ; nếu chưa biết hãy để '……')"),
    ]
    lines, bad = [], 0
    for name, ok, why in checks:
        lines.append(f"[OK] {name}" if ok else f"[LỖI] {name}: {why}")
        bad += not ok
    fonts = {r.font.name for r in runs if r.text.strip() and r.font.name}
    sizes = {r.font.size.pt for r in runs if r.text.strip() and r.font.size}
    warn = 0
    if fonts and fonts != {"Times New Roman"}:
        lines.append(f"[CẢNH BÁO] Font chữ phải là Times New Roman (đang có: {', '.join(sorted(fonts))})")
        warn += 1
    if sizes and (min(sizes) < 11 or max(sizes) > 16):
        lines.append(f"[CẢNH BÁO] Cỡ chữ ngoài khoảng 12-14 pt (đang có: {', '.join(f'{s:g}' for s in sorted(sizes))})")
        warn += 1
    old = sorted({m.group(1).lower() for m in _OLD_LEVELS.finditer(text)})
    if old:
        lines.append(f"[CẢNH BÁO] Có tên cấp hành chính cũ ({', '.join(old)}): từ 01/7/2025 chính quyền địa phương chỉ còn 2 cấp (tỉnh/thành phố, xã/phường), hãy kiểm tra lại")
        warn += 1
    head = "Tất cả mục kiểm tra đều đạt." if not bad else f"Có {bad} mục cần sửa trên tổng {len(checks)} mục."
    return head + (f" ({warn} cảnh báo)" if warn else "") + "\n" + "\n".join(lines)


# ---- Script hàng loạt --------------------------------------------------------------------------
@tool("run_script", "Viết một script Python vào thư mục scripts/ của phiên rồi chạy với giới hạn thời gian. Dùng cho việc hàng loạt: gộp nhiều file Excel, đổi tên file scan, lọc dữ liệu. Chỉ làm trong thư mục làm việc; luôn hỏi phép trừ chế độ Toàn quyền.",
      {"name": ("string", "tên file script, vd gop-bao-cao.py"), "code": ("string", "mã Python đầy đủ"), "timeout": ("integer", "giây tối đa (mặc định 120, tối đa 600)")},
      required=["name", "code"], risk="exec")
def run_script(ctx, name, code, timeout=120):
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,80}", name or "") or ".." in name:
        raise ValueError("Tên script không hợp lệ (chỉ chữ, số, '.', '_', '-').")
    timeout = max(1, min(int(timeout or 120), 600))
    if not ctx.full_access and not ctx.approve("exec", f"python scripts/{name}\n\n{code[:600]}"):
        return DENIED
    d = ctx.workdir / "scripts"
    d.mkdir(parents=True, exist_ok=True)
    f = d / name
    f.write_text(code, encoding="utf-8")
    try:
        r = subprocess.run([sys.executable, str(f)], cwd=ctx.workdir, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return f"Script chạy quá {timeout}s nên đã bị dừng."
    out = (r.stdout or "")[-6000:]
    err = (r.stderr or "")[-3000:]
    return f"Script scripts/{name} kết thúc, mã thoát {r.returncode}.\n--- stdout ---\n{out}\n--- stderr ---\n{err}"


@tool("save_script_as_skill", "Lưu một script đã chạy tốt thành skill dùng lại cho cả phòng (kèm SKILL.md mô tả).",
      {"name": ("string", "tên skill dạng chữ thường-gạch-nối, vd gop-bao-cao"), "description": ("string", "mô tả khi nào dùng skill này"), "script_path": ("string", "đường dẫn script, vd scripts/gop-bao-cao.py")}, risk="file")
def save_script_as_skill(ctx, name, description, script_path):
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{1,60}", name or ""):
        raise ValueError("Tên skill chỉ gồm chữ thường, số và dấu '-'.")
    src = _resolve(ctx, script_path, "read")
    if not src.is_file():
        raise FileNotFoundError(f"Không tìm thấy script: {script_path}")
    d = cfgmod.load().workspace_path() / "skills" / name
    (d / "scripts").mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, d / "scripts" / src.name)
    (d / "SKILL.md").write_text(
        f"---\nname: {name}\ndescription: {description.strip()}\n---\n\n# {name}\n\n{description.strip()}\n\n"
        f"Chạy script `scripts/{src.name}` (Python) bằng tool run_script: đọc mã, chép vào thư mục làm việc, sửa đường dẫn đầu vào/đầu ra cho phù hợp rồi chạy.\n", encoding="utf-8")
    return f"Đã lưu skill '{name}' tại {d}."


@tool("shuffle_exam", "Xáo đề thi trắc nghiệm .docx thành nhiều mã đề (đổi thứ tự câu hỏi trong từng phần, đổi thứ tự đáp án A/B/C/D, đánh lại số câu và 'Mã đề') và GIỮ NGUYÊN định dạng đề gốc; xuất file Word mỗi mã đề + bảng đáp án Excel. Đáp án đúng được nhận diện từ dấu gạch chân/chữ đỏ/tô nền/in đậm của đề gốc.",
      {"path": ("string", "đường dẫn đề gốc .docx"), "so_ma_de": ("integer", "số mã đề cần tạo (mặc định 4, tối đa 20)"), "ma_de_bat_dau": ("integer", "mã đề đầu tiên (mặc định 101)"),
       "giu_thu_tu_cau": ("boolean", "true nếu chỉ xáo đáp án, không đổi thứ tự câu"), "dap_an": ("string", "đáp án thủ công nếu đề gốc không đánh dấu, vd '1A 2C 3B'")},
      required=["path"], risk="file")
def shuffle_exam(ctx, path, so_ma_de=4, ma_de_bat_dau=101, giu_thu_tu_cau=False, dap_an=""):
    from . import exam_shuffle
    src = _resolve(ctx, path, "read")
    if not src.is_file():
        raise FileNotFoundError(f"Không tìm thấy đề: {path}")
    out = _resolve(ctx, str(src.parent / f"{src.stem}-xao-tron"), "write")
    try:
        res = exam_shuffle.build_versions(src, out, versions=int(so_ma_de or 4), start_code=int(ma_de_bat_dau or 101), keep_order=bool(giu_thu_tu_cau), manual_answers=dap_an or None)
    except exam_shuffle.ExamError as e:
        raise ValueError(str(e)) from e
    s = res["summary"]
    lines = [f"Đã tạo {len(res['files'])} mã đề ({', '.join(res['codes'])}) từ {s['mcq']} câu trắc nghiệm ({s['sections']} phần) trong {out}:"]
    lines += [f"- {f.name}" for f in res["files"]]
    lines.append(f"- {res['answer_key'].name} (bảng đáp án)")
    lines += [f"LƯU Ý: {w}" for w in res["warnings"]]
    return "\n".join(lines)
