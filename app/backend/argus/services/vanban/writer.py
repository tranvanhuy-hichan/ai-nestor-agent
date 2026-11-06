#!/usr/bin/env python3
"""MCP server ghi văn bản hành chính Việt Nam (.docx) theo ĐÚNG một nguồn định dạng duy nhất:
references/formats.json (biên dịch từ Nghị định 30/2020/NĐ-CP, Phụ lục I/II/III).

Khác biệt cốt lõi so với document_intelligence_mcp.py (writer cũ, vẫn chạy song song, KHÔNG bị
sửa/xóa bởi file này): KHÔNG có bất kỳ heuristic đoán role nào (không regex/keyword suy luận
"Căn cứ ", số La Mã, "-", tên chức danh...). Mọi paragraph gửi lên PHẢI có `role` tường minh khớp
đúng 1 key trong formats.json["roles"] — role không hợp lệ bị TỪ CHỐI ngay, không cố đoán, không
ghi file. Không đọc/áp dụng bất kỳ style nào lấy từ template — mẫu (nếu có) chỉ là khung chứa
(header/footer/styles.xml giữ nguyên), không phải nguồn định dạng.
"""
import json
import os
import re
import sys
import tempfile
import zipfile
import xml.etree.ElementTree as ET


# Argus: ALLOWED_ROOT do tools_office dat truoc moi lan ghi (thu muc chua file dau ra, da qua _resolve/xin phep).
ALLOWED_ROOT = os.path.realpath(tempfile.gettempdir())
REFERENCES_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "references")
W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
W = f"{{{W_NS}}}"
ET.register_namespace("w", W_NS)

DEFAULT_FONT = "Times New Roman"


def _send(payload):
    sys.stdout.write(json.dumps(payload, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def _error_response(request_id, code, message):
    _send({"jsonrpc": "2.0", "id": request_id, "error": {"code": code, "message": message}})


def _is_allowed(path):
    real = os.path.realpath(path)
    return real == ALLOWED_ROOT or real.startswith(ALLOWED_ROOT + os.sep)


# ─── Nguồn định dạng: đọc 1 lần khi tiến trình khởi động, không đổi trong suốt vòng đời ───────────

def _load_json(name):
    path = os.path.join(REFERENCES_DIR, name)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


FORMATS = _load_json("formats.json")
DOCUMENT_TYPES = _load_json("document-types.json")
ROLES = FORMATS.get("roles") or {}
NEVER_ITALIC_ROLES = set(FORMATS.get("never_italic_roles") or [])
NEVER_JUSTIFY_ROLES = set(FORMATS.get("never_justify_roles") or [])
ALWAYS_BOLD_ROLES = set(FORMATS.get("always_bold_roles") or [])
NEVER_BOLD_ROLES = set(FORMATS.get("never_bold_roles") or [])


def _resolve_document_type(document_type_key):
    """Theo `extends` trong document-types.json — trả về structure đã hợp nhất (entry con override
    field trùng tên, KHÔNG đụng field entry cha không khai báo lại)."""
    types = DOCUMENT_TYPES.get("types") or {}
    entry = types.get(document_type_key)
    if entry is None:
        return None
    if "extends" in entry:
        base = _resolve_document_type(entry["extends"]) or {}
        merged = {**base, **{k: v for k, v in entry.items() if k != "extends"}}
        return merged
    return entry


def _role_spec(role):
    spec = ROLES.get(role)
    if spec is None:
        return None
    # Áp 4 guard chốt cứng MỘT LẦN ở đây (không lặp lại trong paragraph builder) — nguồn chân lý
    # duy nhất cho các thuộc tính này là chính 4 danh sách trong formats.json, không phải giá trị
    # "align"/"bold"/"italic" ghi tay trong từng role (dù 2 bên đang nhất quán, guard này là lưới
    # an toàn nếu formats.json bị sửa sai ở 1 chỗ mà quên chỗ kia).
    resolved = dict(spec)
    if role in NEVER_ITALIC_ROLES:
        resolved["italic"] = False
    if role in NEVER_JUSTIFY_ROLES and resolved.get("align") == "justify":
        resolved["align"] = "left"
    if role in ALWAYS_BOLD_ROLES:
        resolved["bold"] = True
    if role in NEVER_BOLD_ROLES:
        resolved["bold"] = False
    return resolved


def _size_pt(spec):
    """size_pt trong formats.json có thể là số hoặc [bộ_lớn, bộ_nhỏ] (2 bộ cỡ chữ hợp lệ theo
    ND30 Mục IV.2) — luôn dùng phần tử ĐẦU TIÊN (bộ lớn) làm giá trị cố định, không suy luận chọn
    bộ nào theo ngữ cảnh vì đó lại là một dạng heuristic."""
    value = spec.get("size_pt")
    if isinstance(value, (list, tuple)) and value:
        return float(value[0])
    try:
        return float(value)
    except (TypeError, ValueError):
        return 14.0


def _apply_case(text, case):
    if case == "upper":
        return text.upper()
    return text


def _twips_from_cm(value_cm):
    if isinstance(value_cm, (list, tuple)) and value_cm:
        value_cm = value_cm[0]
    try:
        return round(float(value_cm) * 567)
    except (TypeError, ValueError):
        return None


# ─── Paragraph builder — thuần thực thi theo role_spec, KHÔNG có bất kỳ if role == "..." nào ──────

# Bề rộng ký tự trung bình (twips) theo cỡ chữ, ước lượng cho Times New Roman chữ hoa/thường tiếng
# Việt trộn lẫn — dùng để tính độ dài đường kẻ dưới (paragraph border không tự co theo text, phải
# giả lập bằng cách thu hẹp `w:ind` left/right cân đối quanh đoạn). Đây là xấp xỉ hình học, không
# phải đo font thật — đủ dùng để đường kẻ ngắn hơn dòng chữ theo đúng tỷ lệ ND30, không cần chính
# xác tuyệt đối vì bản thân ND30 chỉ yêu cầu khoảng 1/3-1/2, không phải con số cố định. Hiệu chỉnh
# bằng mắt qua kết xuất PDF thật (11.2 ước lượng quá rộng ~35%, khiến đường kẻ dưới motto dài gần
# hết cột dù lẽ ra phải khít đúng độ dài dòng chữ).
_AVG_CHAR_WIDTH_TWIPS_PER_PT = 8.3


def _estimate_text_width_twips(text, size_pt, bold):
    width = len(text) * size_pt * _AVG_CHAR_WIDTH_TWIPS_PER_PT
    if bold:
        width *= 1.06
    return width


def _build_underline_bar_xml(text_width_twips, container_width_twips, size_pt, spacing_after_twips=0):
    """Đoạn RỖNG riêng biệt chỉ để vẽ 1 đường kẻ ngang ngắn hơn dòng chữ phía trên — KHÔNG đụng vào
    `w:ind`/wrap của đoạn chứa text (nếu áp `w:ind` hẹp trực tiếp lên đoạn có chữ, Word sẽ ép chữ tự
    xuống dòng theo đúng bề rộng hẹp đó, làm vỡ dòng ngay cả với text rất ngắn — đây từng là bug).
    Cỡ chữ dùng cho `w:spacing`/border cùng size_pt của dòng phía trên để khoảng cách nhìn tự nhiên.

    `spacing_after_twips`: khoảng cách với nội dung PHÍA SAU đường kẻ — PHẢI đặt ở đây, KHÔNG đặt ở
    đoạn chứa text phía trên, nếu không đường kẻ sẽ bị đẩy lố xa khỏi dòng chữ (khoảng trắng lẽ ra
    nằm sau đường kẻ lại nằm giữa chữ và đường kẻ, trông như đường kẻ "trôi" xuống dưới)."""
    bar = ET.Element(f"{W}p")
    p_pr = ET.SubElement(bar, f"{W}pPr")
    ET.SubElement(p_pr, f"{W}jc", {f"{W}val": "center"})
    side_indent = max(0, round((container_width_twips - text_width_twips) / 2)) if container_width_twips else 0
    ind_attrs = {f"{W}left": str(side_indent), f"{W}right": str(side_indent)} if side_indent else {}
    if ind_attrs:
        ET.SubElement(p_pr, f"{W}ind", ind_attrs)
    # lineRule=exact set độ cao DÒNG, nhưng run vẫn cần font size nhỏ tương ứng — nếu để nguyên
    # size_pt gốc (13-14pt) thì dù line height ép về rất nhỏ, Word vẫn tính baseline theo font 13-14pt
    # khiến đoạn rỗng này trông như 1 dòng đầy đủ chiều cao, đẩy đường kẻ ra xa dòng chữ phía trên
    # (đây từng là bug: đường kẻ "trôi" xuống gần dòng tiếp theo thay vì sát ngay dòng có chữ).
    ET.SubElement(p_pr, f"{W}spacing", {
        f"{W}before": "0", f"{W}after": str(int(spacing_after_twips)), f"{W}line": "20", f"{W}lineRule": "exact",
    })
    p_bdr = ET.SubElement(p_pr, f"{W}pBdr")
    ET.SubElement(p_bdr, f"{W}bottom", {f"{W}val": "single", f"{W}sz": "6", f"{W}space": "1", f"{W}color": "auto"})
    run = ET.SubElement(bar, f"{W}r")
    r_pr = ET.SubElement(run, f"{W}rPr")
    ET.SubElement(r_pr, f"{W}sz", {f"{W}val": "2"})
    ET.SubElement(r_pr, f"{W}szCs", {f"{W}val": "2"})
    text_node = ET.SubElement(run, f"{W}t")
    text_node.text = ""
    return bar


def _build_paragraph_xml(item, container_width_twips=None):
    role = str(item.get("role") or "").strip()
    spec = _role_spec(role)
    if spec is None:
        raise ValueError(f"unknown_role:{role}")
    text = _apply_case(str(item.get("text") or ""), spec.get("case"))

    paragraph = ET.Element(f"{W}p")
    p_pr = ET.SubElement(paragraph, f"{W}pPr")

    align_map = {"left": "left", "right": "right", "center": "center", "justify": "both"}
    align = align_map.get(spec.get("align"))
    if align:
        ET.SubElement(p_pr, f"{W}jc", {f"{W}val": align})

    first_line_twips = _twips_from_cm(spec.get("first_line_indent_cm"))
    if first_line_twips:
        ET.SubElement(p_pr, f"{W}ind", {f"{W}firstLine": str(first_line_twips)})

    # `no_underline=true` đánh dấu đây là 1 dòng GIỮA của khối nhiều dòng cùng role (vd summary
    # nhiều dòng) — dòng giữa phải dính sát dòng sau (không spacing_after), chỉ dòng CUỐI của khối
    # mới cách biệt với nội dung tiếp theo.
    is_mid_block_line = bool(item.get("no_underline"))
    has_underline_bar = bool(spec.get("underline_paragraph") and not is_mid_block_line)
    spacing_after_twips = 0
    if spec.get("paragraph_spacing_after_pt_min") and not is_mid_block_line:
        spacing_after_twips = round(float(spec["paragraph_spacing_after_pt_min"]) * 20)
    spacing_attrs = {}
    if spec.get("paragraph_spacing_before_pt_min"):
        spacing_attrs[f"{W}before"] = str(round(float(spec["paragraph_spacing_before_pt_min"]) * 20))
    # Khi có đường kẻ dưới, spacing_after PHẢI dời sang đoạn rỗng vẽ đường kẻ (xem dưới) — nếu để ở
    # đây, khoảng cách sẽ chèn giữa CHỮ và ĐƯỜNG KẺ thay vì giữa đường kẻ và nội dung tiếp theo.
    if spacing_after_twips and not has_underline_bar:
        spacing_attrs[f"{W}after"] = str(spacing_after_twips)
    if spacing_attrs:
        ET.SubElement(p_pr, f"{W}spacing", spacing_attrs)

    underline_bar = None
    if has_underline_bar:
        # Đường kẻ ngang thật, KHÔNG BAO GIỜ dùng underline ký tự (w:u trên run) để giả — lỗi thể
        # thức nghiêm trọng theo ND30 (Phụ lục I Mục II.1.b, II.2.c, II.4b). Vẽ bằng 1 đoạn RỖNG
        # riêng ngay sau đoạn có chữ (xem _build_underline_bar_xml) thay vì border trực tiếp trên
        # chính đoạn có chữ — tránh làm hẹp vùng chứa text và khiến chữ tự xuống dòng sai.
        # `item.no_underline=true`: khi 1 role có underline_paragraph (vd summary) được dùng cho
        # NHIỀU dòng liên tiếp thuộc CÙNG 1 khối trích yếu — chỉ dòng CUỐI CÙNG của khối mới vẽ
        # đường kẻ, các dòng trước set no_underline=true để tránh nhiều đường kẻ chồng nhau.
        ratio = spec.get("underline_width_ratio")
        text_width = _estimate_text_width_twips(text, _size_pt(spec), bool(spec.get("bold")))
        # Nếu text_width ước lượng đã vượt quá container (dấu hiệu Word sẽ tự wrap nhiều dòng vì
        # item chứa text quá dài, đáng lẽ phải tách thành nhiều item ngắn hơn ở tầng gọi) — chặn
        # tại container_width_twips TRƯỚC khi nhân ratio, để đường kẻ suy biến về đúng tỷ lệ của 1
        # dòng đầy đủ thay vì phình to hơn cả trang rồi mới bị cắt (gây lệch vị trí, trông như đường
        # kẻ "trôi" khỏi dòng chữ thật).
        if container_width_twips:
            text_width = min(text_width, container_width_twips)
        fixed_ratio = ratio[0] if isinstance(ratio, (list, tuple)) and ratio else None
        target_width = text_width * fixed_ratio if fixed_ratio else text_width
        if container_width_twips:
            target_width = min(target_width, container_width_twips)
        underline_bar = _build_underline_bar_xml(
            target_width, container_width_twips, _size_pt(spec), spacing_after_twips,
        )

    run = ET.SubElement(paragraph, f"{W}r")
    r_pr = ET.SubElement(run, f"{W}rPr")
    font = str(item.get("font") or DEFAULT_FONT)
    ET.SubElement(r_pr, f"{W}rFonts", {
        f"{W}ascii": font, f"{W}hAnsi": font, f"{W}eastAsia": font, f"{W}cs": font,
    })
    size_half_pt = int(_size_pt(spec) * 2)
    ET.SubElement(r_pr, f"{W}sz", {f"{W}val": str(size_half_pt)})
    ET.SubElement(r_pr, f"{W}szCs", {f"{W}val": str(size_half_pt)})
    ET.SubElement(r_pr, f"{W}color", {f"{W}val": "000000"})

    if spec.get("bold"):
        ET.SubElement(r_pr, f"{W}b")
    if spec.get("italic"):
        ET.SubElement(r_pr, f"{W}i")

    text_node = ET.SubElement(run, f"{W}t")
    text_node.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    text_node.text = text

    info = {
        "role": role,
        "align": spec.get("align"),
        "bold": bool(spec.get("bold")),
        "italic": bool(spec.get("italic")),
        "size_pt": _size_pt(spec),
        "case": spec.get("case"),
    }
    elements = [paragraph, underline_bar] if underline_bar is not None else [paragraph]
    return elements, info


def _two_column_table_xml(left_items, right_items, left_width_pct=None, content_width=9360):
    """Khối bố cục 2 cột KHÔNG viền (đầu trang: cơ quan ban hành | quốc hiệu-tiêu ngữ; cuối trang:
    nơi nhận | chữ ký) — mỗi dòng vẫn là 1 paragraph có role riêng, đi qua _build_paragraph_xml y hệt
    paragraph đơn lẻ, chỉ khác là đặt trong 2 ô bảng không viền để căn cột.

    Mặc định 42/58 (không phải 50/50) — "CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM" (cột phải) dài hơn
    nhiều so với tên cơ quan ban hành điển hình (cột trái); chia đều 50/50 khiến quốc hiệu bị wrap
    xuống 2 dòng ở cỡ chữ 12-13pt/A4, sai thể thức ND30 (quốc hiệu luôn phải nằm trên đúng 1 dòng)."""
    try:
        left_pct = max(15, min(85, float(left_width_pct)))
    except (TypeError, ValueError):
        left_pct = 42

    # Lưới an toàn cứng cho quốc hiệu (ND30: "CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM" BẮT BUỘC 1 dòng) —
    # không chỉ dựa vào agent tự tính đúng left_width_pct (SKILL.md đã yêu cầu nhưng agent vẫn có
    # thể tính sai/bỏ qua, gây quốc hiệu wrap 2 dòng trong thực tế). Ước lượng độ rộng ký tự
    # (_estimate_text_width_twips) không đủ tin cậy cho chữ hoa có dấu tiếng Việt để tự tính ngưỡng
    # chính xác, nên dùng trần cứng theo đúng khuyến nghị ND30 trong SKILL.md thay vì tính toán:
    # nếu cột phải có role=national_name, left_pct không bao giờ được vượt quá 40 dù agent truyền gì.
    has_national_name = any(
        isinstance(item, dict) and item.get("role") == "national_name" for item in right_items
    )
    if has_national_name:
        left_pct = min(left_pct, 40)

    left_w = round(content_width * left_pct / 100)
    right_w = content_width - left_w

    table = ET.Element(f"{W}tbl")
    table_pr = ET.SubElement(table, f"{W}tblPr")
    ET.SubElement(table_pr, f"{W}tblW", {f"{W}w": "0", f"{W}type": "auto"})
    borders = ET.SubElement(table_pr, f"{W}tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        ET.SubElement(borders, f"{W}{edge}", {f"{W}val": "nil"})
    grid = ET.SubElement(table, f"{W}tblGrid")
    ET.SubElement(grid, f"{W}gridCol", {f"{W}w": str(left_w)})
    ET.SubElement(grid, f"{W}gridCol", {f"{W}w": str(right_w)})
    row = ET.SubElement(table, f"{W}tr")
    applied = []

    # Dựng trước toàn bộ elements mỗi cột để đếm số dòng thật (1 item có thể sinh ra 2 element
    # do underline_bar rỗng đi kèm) — nếu 1 cột có ÍT dòng hơn, chèn thêm dòng trống NGAY TRƯỚC
    # element cuối cùng của cột đó, để dòng cuối 2 cột (thường là document_number/place_date)
    # luôn thẳng hàng ngang nhau.
    built = []
    for items, width in ((left_items, left_w), (right_items, right_w)):
        col_elements = []
        col_applied = []
        if not items:
            col_elements.extend(_build_paragraph_xml({"text": "", "role": "body"}, width)[0])
        for line in items:
            elements, info = _build_paragraph_xml(line, width)
            col_elements.extend(elements)
            col_applied.append(info)
        built.append({"elements": col_elements, "applied": col_applied, "width": width})

    max_len = max(len(col["elements"]) for col in built)
    for col in built:
        deficit = max_len - len(col["elements"])
        if deficit > 0 and col["elements"]:
            blank_elements = []
            for _ in range(deficit):
                blank_elements.extend(_build_paragraph_xml({"text": "", "role": "body"}, col["width"])[0])
            col["elements"][-1:-1] = blank_elements

    for col in built:
        cell = ET.SubElement(row, f"{W}tc")
        cell_pr = ET.SubElement(cell, f"{W}tcPr")
        ET.SubElement(cell_pr, f"{W}tcW", {f"{W}w": str(col["width"]), f"{W}type": "dxa"})
        for element in col["elements"]:
            cell.append(element)
        applied.extend(col["applied"])
    return table, applied


def _multi_columns_table_xml(columns, content_width=9360):
    """Khối bố cục >=2 cột KHÔNG viền, chia đều theo mặc định — dùng khi cần đặt CẠNH NHAU nhiều
    hơn 2 khối (vd nơi nhận + 2 người ký trở lên trong cùng 1 hàng). `columns` là list các list dòng
    (mỗi dòng vẫn có `role` riêng, đi qua _build_paragraph_xml y hệt two_columns). Mỗi cột nhận
    `width_pct` tùy chọn để chia không đều; cột nào không set width_pct sẽ chia đều phần còn lại."""
    n = len(columns)
    if n == 0:
        return ET.Element(f"{W}tbl"), []
    explicit_total = 0.0
    explicit_count = 0
    for col in columns:
        if isinstance(col, dict) and col.get("width_pct") is not None:
            try:
                explicit_total += float(col["width_pct"])
                explicit_count += 1
            except (TypeError, ValueError):
                pass
    remaining_pct = max(0.0, 100.0 - explicit_total)
    remaining_cols = n - explicit_count
    default_pct = remaining_pct / remaining_cols if remaining_cols else 0.0

    widths = []
    for col in columns:
        pct = None
        if isinstance(col, dict):
            pct = col.get("width_pct")
        try:
            pct = float(pct) if pct is not None else default_pct
        except (TypeError, ValueError):
            pct = default_pct
        widths.append(round(content_width * pct / 100))
    # Điều chỉnh cột cuối để tổng đúng bằng content_width (tránh lệch do làm tròn từng cột).
    widths[-1] = content_width - sum(widths[:-1])

    table = ET.Element(f"{W}tbl")
    table_pr = ET.SubElement(table, f"{W}tblPr")
    ET.SubElement(table_pr, f"{W}tblW", {f"{W}w": "0", f"{W}type": "auto"})
    borders = ET.SubElement(table_pr, f"{W}tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        ET.SubElement(borders, f"{W}{edge}", {f"{W}val": "nil"})
    grid = ET.SubElement(table, f"{W}tblGrid")
    for w in widths:
        ET.SubElement(grid, f"{W}gridCol", {f"{W}w": str(w)})
    row = ET.SubElement(table, f"{W}tr")
    applied = []
    for col, width in zip(columns, widths):
        items = col.get("lines") or [] if isinstance(col, dict) else (col or [])
        cell = ET.SubElement(row, f"{W}tc")
        cell_pr = ET.SubElement(cell, f"{W}tcPr")
        ET.SubElement(cell_pr, f"{W}tcW", {f"{W}w": str(width), f"{W}type": "dxa"})
        if not items:
            for element in _build_paragraph_xml({"text": "", "role": "body"}, width)[0]:
                cell.append(element)
        for line in items:
            elements, info = _build_paragraph_xml(line, width)
            for element in elements:
                cell.append(element)
            applied.append(info)
    return table, applied


def _table_cell_xml(text, role="body"):
    cell = ET.Element(f"{W}tc")
    elements, _ = _build_paragraph_xml({"text": text, "role": role})
    for element in elements:
        cell.append(element)
    return cell


_NUMERIC_CELL_UNITS = [
    "tỷ đồng", "triệu đồng", "nghìn đồng", "tỷ", "triệu", "nghìn",
    "đồng", "vnđ", "vnd", "ngày", "gói",
]


def _looks_numeric(value) -> bool:
    text = str(value if value is not None else "").strip()
    if not text or not re.search(r"\d", text):
        return False
    stripped = text.lower()
    for unit in _NUMERIC_CELL_UNITS:
        stripped = stripped.replace(unit, "")
    stripped = stripped.strip(" ()%-")
    return bool(re.fullmatch(r"[\d.,\s]*", stripped))


def _add_cell_borders(cell_pr):
    borders = ET.SubElement(cell_pr, f"{W}tcBorders")
    for edge in ("top", "left", "bottom", "right"):
        ET.SubElement(borders, f"{W}{edge}", {f"{W}val": "single", f"{W}sz": "4", f"{W}color": "999999"})


def _header_cell_xml(text, width, colspan=1, rowspan_role=None):
    """1 ô tiêu đề bảng — `width` là độ rộng THẬT của ô (đã cộng dồn các cột bị colspan, không phải
    1 cột đơn nhân lên — các cột trong bảng không nhất thiết đồng đều). colspan>1 dựng gridSpan
    (merge ngang); rowspan_role in {"start", "continue"} dựng vMerge (merge dọc: "start" mở nhóm,
    "continue" nối tiếp ô rỗng phía trên, KHÔNG được có text riêng theo chuẩn OOXML)."""
    cell = _table_cell_xml(text if rowspan_role != "continue" else "",
                            role="table_header_cell" if "table_header_cell" in ROLES else "body")
    cell_pr = cell.find(f"{W}tcPr")
    if cell_pr is None:
        cell_pr = ET.Element(f"{W}tcPr")
        cell.insert(0, cell_pr)
    ET.SubElement(cell_pr, f"{W}tcW", {f"{W}w": str(width), f"{W}type": "dxa"})
    if colspan > 1:
        ET.SubElement(cell_pr, f"{W}gridSpan", {f"{W}val": str(colspan)})
    if rowspan_role:
        ET.SubElement(cell_pr, f"{W}vMerge", {f"{W}val": "restart" if rowspan_role == "start" else "continue"})
    _add_cell_borders(cell_pr)
    ET.SubElement(cell_pr, f"{W}vAlign", {f"{W}val": "center"})
    return cell


def _header_rows_from_groups(table_header_groups):
    """table_header_groups: list các tầng header, mỗi tầng là list ô {text, colspan?, rowspan?}.
    rowspan (số tầng ô này kéo dài xuống, mặc định 1) dùng vMerge nối các tầng dưới cùng cột.
    Trả về list các <w:tr> đã dựng đủ, đã tự chèn ô vMerge continue cho cột bị merge dọc — mỗi ô là
    tuple (col, colspan, text, rowspan_role), độ rộng thật được tính riêng bằng col_widths ở nơi gọi."""
    tier_count = len(table_header_groups)
    rows_cells = [[] for _ in range(tier_count)]
    for tier_index, group in enumerate(table_header_groups):
        col = 0
        for cell_def in group:
            text = str(cell_def.get("text", ""))
            colspan = max(1, int(cell_def.get("colspan") or 1))
            rowspan = max(1, int(cell_def.get("rowspan") or 1))
            rowspan_role = "start" if rowspan > 1 else None
            rows_cells[tier_index].append((col, colspan, text, rowspan_role))
            if rowspan > 1:
                for extra_tier in range(tier_index + 1, min(tier_index + rowspan, tier_count)):
                    rows_cells[extra_tier].append((col, colspan, text, "continue"))
            col += colspan
    # Sắp lại mỗi tầng theo thứ tự cột tăng dần (rowspan "continue" được append lệch thứ tự ở trên)
    for tier_index in range(tier_count):
        rows_cells[tier_index].sort(key=lambda item: item[0])
    return rows_cells


# PHẢI khớp đúng size_pt thật của role table_header_cell/table_body_cell trong formats.json — nếu
# lệch, min-width ước lượng ở đây sẽ sai so với độ rộng chữ THẬT Word render, làm hỏng toàn bộ mục
# đích của hàm này (chữ nhỏ hơn thân văn bản để bảng nhiều cột đủ chỗ mà không ép width quá hẹp).
_TABLE_CELL_SIZE_PT = 11
# Padding 2 bên trong ô bảng Word mặc định (~108 twips/bên khi không tự set `tcMar`) cộng biên an
# toàn nhỏ cho sai số ước lượng ký tự trung bình. Padding TUYỆT ĐỐI lớn (thử 450 twips) từng gây tác
# dụng phụ: với bảng nhiều cột (14 cột), tổng padding cộng dồn làm min_widths vượt content_width,
# đẩy vào nhánh fallback khiến bảng TRÀN LỀ PHẢI thay vì scale vừa trang — padding cố định không co
# giãn theo số cột. Vì vậy padding ở đây giữ NHỎ (chỉ bù phần `tcMar` mặc định của Word), còn biên an
# toàn chính cho việc ước lượng ký tự sai (chữ hoa rộng hơn trung bình) nằm ở hệ số nhân bên dưới.
_TABLE_CELL_WORD_PADDING_TWIPS = 150


def _longest_word_width_twips(text, bold=False):
    """Độ rộng ước lượng (twips) của TỪ DÀI NHẤT trong `text` — dùng làm min-width tuyệt đối cho 1
    cột bảng. Đây là ngưỡng CỨNG: nếu cột hẹp hơn từ dài nhất của chính nó, Word buộc phải ngắt xuống
    dòng NGAY GIỮA từ đó (không có cách nào wrap theo từ mà không tràn ô) — khác với việc chia trọng
    số theo TỔNG độ dài văn bản (không đảm bảo từng từ đơn lẻ vẫn vừa cột khi cột đó bị co hẹp).
    `bold=True` cho ô tiêu đề (in đậm rộng hơn ~6%, khớp hệ số trong `_estimate_text_width_twips`).
    Nhân thêm 1.35 làm biên an toàn cho việc `_AVG_CHAR_WIDTH_TWIPS_PER_PT` là ký tự TRUNG BÌNH —
    chữ hoa (VD "T" trong "TT") rộng hơn đáng kể so với trung bình. (Nguyên nhân CHÍNH khiến "TT"
    từng vỡ dòng dù qua ngưỡng min lý thuyết không phải do hệ số này quá thấp, mà do bảng thiếu
    `tblLayout type="fixed"` khiến Word/LibreOffice tự autofit, bỏ qua hoàn toàn width đã tính — xem
    ghi chú tại `_data_table_xml`. Hệ số 1.35 ở đây chỉ còn là biên dự phòng nhỏ, không cần bù quá
    tay như lúc chưa tìm ra nguyên nhân gốc.)"""
    words = str(text).split() or [""]
    longest = max((len(w) for w in words), default=0)
    width = longest * _TABLE_CELL_SIZE_PT * _AVG_CHAR_WIDTH_TWIPS_PER_PT * 1.35
    if bold:
        width *= 1.06
    return width + _TABLE_CELL_WORD_PADDING_TWIPS


def _compute_column_widths(col_count, content_width, table_headers, table_rows, table_header_groups):
    """Chia `content_width` cho các cột theo TRỌNG SỐ độ dài nội dung (không chia đều) — cột có
    tiêu đề/dữ liệu dài (VD "Tên gói thầu") được nhiều chỗ hơn cột ngắn (VD "TT", "Loại hợp đồng"),
    tránh chữ vỡ từng ký tự khi bảng nhiều cột như ảnh mẫu ND30 thật (cột không đồng đều).

    2 bước: (1) `min_widths` — ngưỡng CỨNG theo từ dài nhất mỗi cột (`_longest_word_width_twips`),
    đảm bảo Word không bao giờ phải ngắt giữa 1 từ dù cột đó có trọng số thấp; (2) phần `content_width`
    còn lại sau khi trừ hết min_widths được chia tiếp theo TRỌNG SỐ tổng độ dài (ưu tiên cột có nhiều
    chữ hơn được rộng thêm). Nếu tổng min_widths đã VƯỢT `content_width` (quá nhiều cột có từ dài
    trên 1 khổ giấy hẹp) — không còn chỗ để "đẹp" nữa, trả thẳng min_widths (bảng sẽ tràn lề, nhưng
    vẫn ưu tiên không vỡ từ hơn là vừa lề mà vỡ chữ)."""
    weights = [4.0] * col_count
    min_widths = [_longest_word_width_twips("TT", bold=True)] * col_count
    if table_header_groups:
        for group in table_header_groups:
            col = 0
            for cell_def in group:
                colspan = max(1, int(cell_def.get("colspan") or 1))
                text = str(cell_def.get("text", ""))
                text_len = len(text)
                per_col_weight = max(4, text_len / colspan)
                per_col_min = _longest_word_width_twips(text, bold=True) / colspan
                for offset in range(colspan):
                    if col + offset < col_count:
                        weights[col + offset] = max(weights[col + offset], per_col_weight)
                        min_widths[col + offset] = max(min_widths[col + offset], per_col_min)
                col += colspan
    else:
        for index, header in enumerate(table_headers or []):
            if index < col_count:
                weights[index] = max(weights[index], len(str(header)))
                min_widths[index] = max(min_widths[index], _longest_word_width_twips(header, bold=True))
    for row in table_rows or []:
        if not isinstance(row, (list, tuple)):
            continue
        for index, value in enumerate(row):
            if index < col_count:
                weights[index] = max(weights[index], len(str(value)))
                min_widths[index] = max(min_widths[index], _longest_word_width_twips(value))

    total_min = sum(min_widths)
    if total_min >= content_width:
        return [round(w) for w in min_widths]

    remaining = content_width - total_min
    total_weight = sum(weights)
    extra = [remaining * w / total_weight for w in weights]
    widths = [round(min_widths[i] + extra[i]) for i in range(col_count)]
    widths[-1] += content_width - sum(widths)  # bù sai số làm tròn vào cột cuối
    return widths


def _data_table_xml(table_headers, table_rows, content_width=9360, table_header_groups=None):
    """Bảng số liệu. Header đơn giản: truyền `table_headers` (list[str]) như trước. Header nhiều
    tầng (VD nhóm cột "Nguồn vốn" merge ngang trên 2 cột con "Kế hoạch"/"Thực hiện"): truyền
    `table_header_groups` — list các tầng, mỗi tầng là list {"text", "colspan"?, "rowspan"?}.
    Tổng colspan của MỌI tầng phải khớp đúng số cột thật (= độ dài dòng dữ liệu dài nhất trong
    table_rows) — sai lệch sẽ làm hỏng bảng, không có cơ chế tự sửa."""
    rows = table_rows or []
    if table_header_groups:
        col_count = max((sum(int(c.get("colspan") or 1) for c in group) for group in table_header_groups), default=0)
    else:
        col_count = len(table_headers or [])
    if col_count == 0:
        return _build_paragraph_xml({"text": "", "role": "body"})[0][0]

    table = ET.Element(f"{W}tbl")
    table_pr = ET.SubElement(table, f"{W}tblPr")
    # `tblW type="auto"` + KHÔNG có `tblLayout` khiến Word/LibreOffice tự autofit độ rộng cột theo
    # nội dung, BỎ QUA hoàn toàn `tcW`/`tblGrid` mà `_compute_column_widths` đã tính — đây là nguyên
    # nhân gốc khiến cột "TT" (2 ký tự) vẫn bị bẻ giữa dòng dù giá trị `tcW` tính được đã đủ rộng
    # (xác nhận bằng nhiều lần test convert PDF). `tblLayout type="fixed"` bắt buộc Word tôn trọng
    # đúng width cố định trong `tblGrid`/`tcW`, không tự ý co giãn theo nội dung.
    ET.SubElement(table_pr, f"{W}tblW", {f"{W}w": str(content_width), f"{W}type": "dxa"})
    ET.SubElement(table_pr, f"{W}tblLayout", {f"{W}type": "fixed"})
    ET.SubElement(table_pr, f"{W}tblLook", {
        f"{W}val": "0000", f"{W}firstRow": "1", f"{W}lastRow": "0",
        f"{W}firstColumn": "0", f"{W}lastColumn": "0", f"{W}noHBand": "0", f"{W}noVBand": "0",
    })
    borders = ET.SubElement(table_pr, f"{W}tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        ET.SubElement(borders, f"{W}{edge}", {f"{W}val": "single", f"{W}sz": "4", f"{W}color": "999999"})

    col_widths = _compute_column_widths(col_count, content_width, table_headers, rows, table_header_groups)
    grid = ET.SubElement(table, f"{W}tblGrid")
    for width in col_widths:
        ET.SubElement(grid, f"{W}gridCol", {f"{W}w": str(width)})

    if table_header_groups:
        for tier_cells in _header_rows_from_groups(table_header_groups):
            header_row = ET.SubElement(table, f"{W}tr")
            tr_pr = ET.SubElement(header_row, f"{W}trPr")
            ET.SubElement(tr_pr, f"{W}tblHeader")
            ET.SubElement(tr_pr, f"{W}cantSplit")
            for col, colspan, text, rowspan_role in tier_cells:
                width = sum(col_widths[col:col + colspan])
                header_row.append(_header_cell_xml(text, width, colspan, rowspan_role))
    else:
        headers = [str(h) for h in (table_headers or [])]
        header_row = ET.SubElement(table, f"{W}tr")
        tr_pr = ET.SubElement(header_row, f"{W}trPr")
        ET.SubElement(tr_pr, f"{W}tblHeader")
        ET.SubElement(tr_pr, f"{W}cantSplit")
        for col_index, h in enumerate(headers):
            header_row.append(_header_cell_xml(h, col_widths[col_index]))

    for row in rows:
        row_el = ET.SubElement(table, f"{W}tr")
        row_pr = ET.SubElement(row_el, f"{W}trPr")
        ET.SubElement(row_pr, f"{W}cantSplit")
        for col_index in range(col_count):
            value = row[col_index] if isinstance(row, (list, tuple)) and col_index < len(row) else ""
            cell = _table_cell_xml(value, role="table_body_cell" if "table_body_cell" in ROLES else "body")
            cell_pr = ET.Element(f"{W}tcPr")
            cell.insert(0, cell_pr)
            ET.SubElement(cell_pr, f"{W}tcW", {f"{W}w": str(col_widths[col_index]), f"{W}type": "dxa"})
            _add_cell_borders(cell_pr)
            ET.SubElement(cell_pr, f"{W}vAlign", {f"{W}val": "center"})
            row_el.append(cell)
    return table


# ─── Page setup: đúng 1 bộ margin cố định ND30 (không đọc override từ đâu khác) ────────────────────

_ND30_MARGIN_MM = {"top": 20.0, "bottom": 20.0, "left": 30.0, "right": 20.0}


def _twips_from_mm(value_mm):
    return str(round(float(value_mm) * 56.6929133858))


def _enforce_a4(section, orientation=None):
    """Áp khổ A4 + margin ND30 cho ĐÚNG 1 `sectPr` (thường là sectPr cấp body, mô tả section CUỐI
    CÙNG của văn bản) — các `sectPr` của section-break giữa văn bản (đổi hướng giấy cho phụ lục) đã
    tự đủ pgSz/pgMar khi dựng qua `_section_pr_xml`, không cần và không nên bị hàm này đụng lại."""
    page_size = section.find(f"{W}pgSz")
    if page_size is None:
        page_size = ET.SubElement(section, f"{W}pgSz")
    landscape = orientation == "landscape"
    if landscape:
        page_size.set(f"{W}orient", "landscape")
    elif page_size.get(f"{W}orient") is not None:
        del page_size.attrib[f"{W}orient"]
    page_size.set(f"{W}w", "16838" if landscape else "11906")
    page_size.set(f"{W}h", "11906" if landscape else "16838")
    margins = section.find(f"{W}pgMar")
    if margins is None:
        margins = ET.SubElement(section, f"{W}pgMar")
    for attr in ("top", "bottom", "left", "right"):
        margins.set(f"{W}{attr}", _twips_from_mm(_ND30_MARGIN_MM[attr]))


# ─── Dựng body & IO ghi file ───────────────────────────────────────────────────────────────────────

def _content_width_for(orientation):
    return 14570 if orientation == "landscape" else 9360


def _page_break_paragraph():
    """Đoạn rỗng chỉ để ngắt trang thường (KHÔNG đổi orientation/section) — dùng cho phụ lục phải
    sang trang riêng nhưng vẫn cùng hướng giấy với nội dung trước đó."""
    paragraph = ET.Element(f"{W}p")
    run = ET.SubElement(paragraph, f"{W}r")
    ET.SubElement(run, f"{W}br", {f"{W}type": "page"})
    return paragraph


def _section_pr_xml(orientation):
    """`sectPr` mô tả 1 section hoàn chỉnh (khổ giấy + margin ND30) — dùng lặp lại cho mọi section
    khi văn bản có nhiều hướng giấy khác nhau (VD thân portrait, phụ lục bảng landscape)."""
    section = ET.Element(f"{W}sectPr")
    landscape = orientation == "landscape"
    # Section KẾT THÚC bằng ngắt trang kiểu "nextPage": section kế tiếp luôn bắt đầu ở trang mới — vì vậy item đổi hướng giấy KHÔNG
    # được kèm thêm ngắt trang thủ công (xem `_build_body_blocks`), nếu không sẽ sinh trang trắng nằm giữa văn bản.
    ET.SubElement(section, f"{W}type", {f"{W}val": "nextPage"})
    ET.SubElement(section, f"{W}pgSz", {
        f"{W}w": "16838" if landscape else "11906",
        f"{W}h": "11906" if landscape else "16838",
        **({f"{W}orient": "landscape"} if landscape else {}),
    })
    margins = {attr: _twips_from_mm(_ND30_MARGIN_MM[attr]) for attr in ("top", "bottom", "left", "right")}
    ET.SubElement(section, f"{W}pgMar", {f"{W}{attr}": value for attr, value in margins.items()})
    return section


def _section_break_paragraph(ending_orientation):
    """Đoạn rỗng mang `sectPr` của section VỪA KẾT THÚC (theo OOXML, sectPr trong pPr của 1 đoạn mô
    tả section kết thúc TẠI đoạn đó, không phải section bắt đầu sau nó — dễ nhầm lẫn). Dùng khi cần
    đổi hướng giấy giữa văn bản (VD bảng nhiều cột cần khổ ngang trong khi phần còn lại khổ dọc)."""
    paragraph = ET.Element(f"{W}p")
    paragraph_pr = ET.SubElement(paragraph, f"{W}pPr")
    paragraph_pr.append(_section_pr_xml(ending_orientation))
    return paragraph


def _close_section(blocks, ending_orientation):
    """Đóng section hiện tại. Nếu block ngay trước là 1 đoạn văn thường (chưa mang sectPr) thì gắn `sectPr` vào chính đoạn đó thay vì thêm
    đoạn rỗng — đoạn rỗng thừa có thể tràn sang 1 trang trắng khi đoạn trước đã kín trang. Sau bảng (hoặc không có đoạn) mới cần đoạn rỗng."""
    last = blocks[-1] if blocks else None
    if last is not None and last.tag == f"{W}p" and last.find(f"{W}pPr/{W}sectPr") is None and last.find(f".//{W}br") is None:
        paragraph_pr = last.find(f"{W}pPr")
        if paragraph_pr is None:
            paragraph_pr = ET.Element(f"{W}pPr")
            last.insert(0, paragraph_pr)
        if paragraph_pr.find(f"{W}pPrChange") is None:
            paragraph_pr.append(_section_pr_xml(ending_orientation))
            return
    blocks.append(_section_break_paragraph(ending_orientation))


def _build_body_blocks(paragraphs, default_orientation):
    """Dựng danh sách block theo THỨ TỰ, tự chèn ngắt trang (`page_break_before`) và ngắt section đổi
    hướng giấy (`section_orientation` khác hướng hiện tại) khi item yêu cầu. `default_orientation`
    là hướng giấy ban đầu (tham số `orientation` cũ của toàn văn bản, áp dụng cho item không tự khai
    báo `section_orientation`). Trả về thêm `final_orientation` — hướng của section CUỐI CÙNG, để
    `_enforce_a4` áp đúng cho `sectPr` ở cấp body."""
    blocks = []
    applied = []
    current_orientation = default_orientation or "portrait"
    for item in paragraphs:
        value = item if isinstance(item, dict) else {"text": str(item)}
        item_orientation = value.get("section_orientation") or current_orientation
        if item_orientation not in ("portrait", "landscape"):
            item_orientation = "portrait"
        doi_huong = item_orientation != current_orientation
        if doi_huong:
            if blocks:  # item đầu tiên đổi hướng: chưa có nội dung nào để đóng — chỉ đặt hướng cho section đầu, không sinh trang trắng
                _close_section(blocks, current_orientation)
            current_orientation = item_orientation
        # Đổi hướng giấy ĐÃ tự sang trang mới (section nextPage): không chèn thêm ngắt trang thủ công, tránh trang trắng giữa văn bản.
        if value.get("page_break_before") and not doi_huong:
            blocks.append(_page_break_paragraph())
        content_width = _content_width_for(current_orientation)
        layout = value.get("layout") or "paragraph"
        if layout == "two_columns":
            table, info = _two_column_table_xml(
                value.get("left_lines") or [], value.get("right_lines") or [],
                value.get("left_width_pct"), content_width,
            )
            blocks.append(table)
            applied.extend(info)
        elif layout == "multi_columns":
            table, info = _multi_columns_table_xml(value.get("columns") or [], content_width)
            blocks.append(table)
            applied.extend(info)
        elif layout == "table":
            blocks.append(_data_table_xml(
                value.get("table_headers"), value.get("table_rows"), content_width,
                value.get("table_header_groups"),
            ))
        else:
            elements, info = _build_paragraph_xml(value, content_width)
            blocks.extend(elements)
            applied.append(info)
    return blocks, applied, current_orientation


def _replace_body(root, paragraphs, orientation=None):
    body = root.find(f"{W}body")
    if body is None:
        raise ValueError("DOCX template has no document body")
    sect_pr = body.find(f"{W}sectPr")
    for child in list(body):
        if child is not sect_pr:
            body.remove(child)
    if sect_pr is None:
        sect_pr = ET.SubElement(body, f"{W}sectPr")
    blocks, applied, final_orientation = _build_body_blocks(paragraphs, orientation)
    for index, block in enumerate(blocks):
        body.insert(index, block)
    return applied, final_orientation


def _safe_output_path(template_path, output_file_name):
    parent = os.path.dirname(os.path.realpath(template_path)) if template_path else ALLOWED_ROOT
    safe_name = re.sub(r"[^A-Za-z0-9._-]+", "-", output_file_name or "van-ban.docx")
    safe_name = safe_name.strip(".-")[:120] or "van-ban.docx"
    if not safe_name.lower().endswith(".docx"):
        safe_name += ".docx"
    output_path = os.path.realpath(os.path.join(parent, safe_name))
    if not _is_allowed(output_path) or os.path.dirname(output_path) != parent:
        raise ValueError("output_path is outside the request directory")
    return output_path


_EMPTY_DOCX_XML = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<w:document xmlns:w="{ns}"><w:body><w:sectPr/></w:body></w:document>'
).format(ns=W_NS)


def _collect_roles(paragraphs):
    """Thu thập mọi role cần validate — kể cả role nằm lồng trong left_lines/right_lines của khối
    two_columns (chỉ item `layout` mặc định/paragraph mới có role ở cấp top-level; two_columns/table
    không có role riêng, role thật nằm trong từng dòng con)."""
    roles = []
    for item in paragraphs:
        if not isinstance(item, dict):
            continue
        layout = item.get("layout") or "paragraph"
        if layout == "two_columns":
            for side in ("left_lines", "right_lines"):
                for line in item.get(side) or []:
                    if isinstance(line, dict):
                        roles.append(str(line.get("role") or "").strip())
        elif layout == "multi_columns":
            for col in item.get("columns") or []:
                lines = col.get("lines") or [] if isinstance(col, dict) else (col or [])
                for line in lines:
                    if isinstance(line, dict):
                        roles.append(str(line.get("role") or "").strip())
        elif layout == "table":
            continue
        else:
            roles.append(str(item.get("role") or "").strip())
    return roles


def _write_docx(template_path, output_file_name, paragraphs, document_type_key="", orientation=None):
    if not isinstance(paragraphs, list) or not paragraphs:
        raise ValueError("paragraphs is required and must be a non-empty array")

    # Validate TẤT CẢ role trước khi ghi bất cứ gì — reject sớm, không ghi file dở dang.
    unknown = sorted(set(_collect_roles(paragraphs)) - set(ROLES.keys()))
    if unknown:
        raise ValueError(f"unknown_role: {unknown}. allowed_roles: {sorted(ROLES.keys())}")

    output_path = _safe_output_path(template_path, output_file_name)
    temporary_path = output_path + ".tmp"

    try:
        if template_path:
            template_real = os.path.realpath(template_path)
            if not _is_allowed(template_real) or not os.path.isfile(template_real):
                raise ValueError("template_path is missing or outside allowed root")
            if not zipfile.is_zipfile(template_real):
                raise ValueError("template_path is not a valid DOCX/ZIP file")
            with zipfile.ZipFile(template_real, "r") as source, zipfile.ZipFile(temporary_path, "w", zipfile.ZIP_DEFLATED) as target:
                applied = []
                for item in source.infolist():
                    data = source.read(item.filename)
                    if item.filename == "word/document.xml":
                        root = ET.fromstring(data)
                        applied, final_orientation = _replace_body(root, paragraphs, orientation)
                        _enforce_a4(root.find(f"{W}body").find(f"{W}sectPr"), final_orientation)
                        data = ET.tostring(root, encoding="utf-8", xml_declaration=True)
                    target.writestr(item, data)
        else:
            # Không có mẫu: dựng 1 package .docx tối thiểu từ đầu (content types + rels + document.xml).
            root = ET.fromstring(_EMPTY_DOCX_XML)
            applied, final_orientation = _replace_body(root, paragraphs, orientation)
            _enforce_a4(root.find(f"{W}body").find(f"{W}sectPr"), final_orientation)
            document_xml = ET.tostring(root, encoding="utf-8", xml_declaration=True)
            with zipfile.ZipFile(temporary_path, "w", zipfile.ZIP_DEFLATED) as target:
                target.writestr("[Content_Types].xml", _MINIMAL_CONTENT_TYPES)
                target.writestr("_rels/.rels", _MINIMAL_RELS)
                target.writestr("word/document.xml", document_xml)

        with zipfile.ZipFile(temporary_path) as result:
            if "word/document.xml" not in result.namelist():
                raise ValueError("generated file is missing word/document.xml")
            result.read("word/document.xml")
        os.replace(temporary_path, output_path)
    finally:
        if os.path.exists(temporary_path):
            os.remove(temporary_path)

    return {
        "ok": True,
        "file_path": output_path,
        "file_name": os.path.basename(output_path),
        "file_size": os.path.getsize(output_path),
        "document_type_key": document_type_key,
        "page_size": "A4",
        "applied": applied,
    }


_MINIMAL_CONTENT_TYPES = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
    '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
    '<Default Extension="xml" ContentType="application/xml"/>'
    '<Override PartName="/word/document.xml" '
    'ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
    '</Types>'
)
_MINIMAL_RELS = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
    '<Relationship Id="rId1" '
    'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" '
    'Target="word/document.xml"/>'
    '</Relationships>'
)


def _convert_pdf(file_path):
    import subprocess
    import tempfile

    real = os.path.realpath(file_path)
    if not _is_allowed(real) or not os.path.isfile(real):
        raise ValueError("file_path is missing or outside allowed root")
    if not zipfile.is_zipfile(real):
        raise ValueError("file_path is not a valid DOCX/ZIP file")

    out_dir = os.path.dirname(real)
    with tempfile.TemporaryDirectory() as home_dir:
        env = {**os.environ, "HOME": home_dir}
        result = subprocess.run(
            ["soffice", "--headless", "--norestore", "--convert-to", "pdf", "--outdir", out_dir, real],
            capture_output=True, timeout=180, env=env,
        )
        pdf_path = os.path.join(out_dir, os.path.splitext(os.path.basename(real))[0] + ".pdf")
        if not os.path.exists(pdf_path):
            raise ValueError(
                f"LibreOffice convert failed (rc={result.returncode}): "
                f"{result.stderr.decode(errors='ignore')[:500]}"
            )
    if not _is_allowed(pdf_path):
        raise ValueError("converted pdf path is outside allowed root")
    return {
        "ok": True,
        "file_path": pdf_path,
        "file_name": os.path.basename(pdf_path),
        "file_size": os.path.getsize(pdf_path),
        "document_type": "pdf",
    }


def _list_document_types():
    return {"types": {k: {"ten_day_du": v.get("ten_day_du"), "structure": (_resolve_document_type(k) or {}).get("structure")}
                       for k, v in (DOCUMENT_TYPES.get("types") or {}).items()},
            "roles": sorted(ROLES.keys())}


# ─── Kho học động (learned-rules.json) — KHÁC formats.json/document-types.json: đọc lại mỗi lần
# gọi (không cache ở module-level) vì nội dung đổi liên tục qua các lượt học của skill
# `document-revision-learning`, ghi bằng temp file + os.replace để không bao giờ để lại JSON dở
# dang nếu tiến trình bị ngắt giữa chừng. ────────────────────────────────────────────────────────

_LEARNED_RULES_PATH = os.path.join(REFERENCES_DIR, "learned-rules.json")


def _read_json_file(path, fallback):
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, ValueError, TypeError):
        return fallback


def _write_json_atomic(path, value):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fd, temp_path = tempfile.mkstemp(prefix=".learned-rules-", suffix=".json", dir=os.path.dirname(path))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(value, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        os.replace(temp_path, path)
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)


def _get_learned_rules(document_type_key=""):
    """Đọc toàn bộ learned-rules.json, hoặc chỉ 1 document_type_key nếu được truyền. Trả `{}` nếu
    file chưa tồn tại — KHÔNG coi là lỗi (bình thường trước lượt học đầu tiên)."""
    data = _read_json_file(_LEARNED_RULES_PATH, {}) if os.path.exists(_LEARNED_RULES_PATH) else {}
    if not isinstance(data, dict):
        data = {}
    if document_type_key:
        return {"ok": True, "document_type_key": document_type_key, "rules": data.get(document_type_key) or {}}
    return {"ok": True, "rules": data}


def _save_learned_rules(document_type_key, rules):
    """Ghi đè đúng 1 khóa `document_type_key` trong learned-rules.json, giữ nguyên mọi khóa khác.
    `rules` phải là toàn bộ object cho khóa đó (content_pattern/legal_pattern/structure_pattern/
    format_overrides) — skill gọi tool này tự chịu trách nhiệm merge đúng observation_count/status
    theo quy tắc trong SKILL.md trước khi truyền vào đây; tool chỉ ghi, không tự merge."""
    if not document_type_key:
        raise ValueError("document_type_key phải khác rỗng")
    if not isinstance(rules, dict):
        raise ValueError("rules phải là object")
    data = _read_json_file(_LEARNED_RULES_PATH, {}) if os.path.exists(_LEARNED_RULES_PATH) else {}
    if not isinstance(data, dict):
        data = {}
    data[document_type_key] = rules
    _write_json_atomic(_LEARNED_RULES_PATH, data)
    return {"ok": True, "document_type_key": document_type_key}


TOOLS = [
    {
        "name": "van_ban_hanh_chinh_write_docx",
        "description": (
            "Tạo file DOCX văn bản hành chính Việt Nam đúng thể thức Nghị định 30/2020/NĐ-CP. "
            "Mỗi paragraph BẮT BUỘC có `role` khớp đúng 1 key trong van_ban_hanh_chinh_list_document_types "
            "(field roles) — role không hợp lệ bị từ chối ngay, KHÔNG cố đoán. Định dạng (font/cỡ/canh lề/"
            "đậm/nghiêng) luôn lấy từ formats.json, KHÔNG lấy từ template_path dù có truyền."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "template_path": {
                    "type": "string",
                    "description": "Tùy chọn — file .docx nền để giữ header/footer/styles khác; KHÔNG ảnh hưởng định dạng nội dung.",
                },
                "output_file_name": {"type": "string"},
                "document_type_key": {
                    "type": "string",
                    "description": "Key trong document-types.json (vd QUYET_DINH_TRUC_TIEP, TO_TRINH, CONG_VAN, BIEN_BAN) — dùng để ghi vào response, không bắt buộc để ghi file.",
                },
                "paragraphs": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "text": {"type": "string"},
                            "role": {"type": "string"},
                            "no_underline": {
                                "type": "boolean",
                                "description": "Với role có đường kẻ dưới mặc định (issuing_org/motto/summary/appendix_attachment_info) dùng cho NHIỀU dòng liên tiếp của CÙNG 1 khối (vd summary nhiều dòng: 'Kết quả...' + 'Công trình: ...' + 'Địa điểm: ...') — set true cho MỌI dòng TRỪ dòng CUỐI CÙNG của khối, để chỉ có đúng 1 đường kẻ ở cuối khối, không lặp lại mỗi dòng.",
                            },
                            "layout": {"type": "string", "enum": ["paragraph", "two_columns", "multi_columns", "table"]},
                            "left_lines": {"type": "array", "items": {"type": "object"}},
                            "right_lines": {"type": "array", "items": {"type": "object"}},
                            "left_width_pct": {"type": "number"},
                            "columns": {
                                "type": "array",
                                "description": "Dùng với layout=multi_columns khi cần >=2 khối đặt CẠNH NHAU trong 1 hàng (vd nơi nhận + 2 người ký trở lên). Mỗi phần tử: {lines: [...], width_pct?}. Cột không có width_pct chia đều phần trăm còn lại.",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "lines": {"type": "array", "items": {"type": "object"}},
                                        "width_pct": {"type": "number"},
                                    },
                                    "additionalProperties": False,
                                },
                            },
                            "table_headers": {"type": "array", "items": {"type": "string"}},
                            "table_header_groups": {
                                "type": "array",
                                "description": "Header nhiều tầng khi cần merge cột/hàng (vd nhóm 'Nguồn vốn' gộp ngang 2 cột con 'Kế hoạch'/'Thực hiện'). Dùng THAY cho table_headers (bỏ qua table_headers nếu có cả 2). Mỗi phần tử là 1 tầng: list ô {text, colspan?, rowspan?}. Tổng colspan của MỌI tầng phải khớp đúng số cột thật (độ dài dòng dữ liệu dài nhất trong table_rows) — sai lệch làm hỏng bảng.",
                                "items": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "text": {"type": "string"},
                                            "colspan": {"type": "integer"},
                                            "rowspan": {"type": "integer"},
                                        },
                                        "required": ["text"],
                                        "additionalProperties": False,
                                    },
                                },
                            },
                            "table_rows": {"type": "array", "items": {"type": "array", "items": {"type": "string"}}},
                            "page_break_before": {
                                "type": "boolean",
                                "description": "Ngắt sang trang MỚI ngay trước item này, giữ NGUYÊN hướng giấy hiện tại. Dùng cho phụ lục/bảng biểu đính kèm — theo thể thức ND30, phụ lục luôn bắt đầu ở trang riêng, không được nối liền ngay sau nội dung chính (VD: 'Điều 3...'/'Nơi nhận:'/chữ ký kết thúc quyết định, rồi 'PHỤ LỤC 01' phải xuống trang mới).",
                            },
                            "section_orientation": {
                                "type": "string",
                                "enum": ["portrait", "landscape"],
                                "description": "Đổi hướng giấy TỪ ITEM NÀY trở đi (áp dụng cho chính item này và mọi item sau cho tới khi có item khác đổi lại) — không cần khai báo lại ở mỗi item cùng hướng. Dùng khi bảng có NHIỀU CỘT (từ khoảng 6 cột trở lên, hoặc khi table_headers/table_header_groups quá dài khiến mỗi cột dồn hẹp) — set 'landscape' ngay tại item chứa bảng đó để bảng đủ chỗ ngang, sau đó set lại 'portrait' ở item tiếp theo (KHÔNG cần và không nên kèm page_break_before ở item đổi hướng: writer tự sang trang mới khi đổi hướng giấy, thêm ngắt trang chỉ sinh trang trắng). KHÔNG dùng tham số `orientation` (áp cho toàn văn bản) cho trường hợp chỉ 1 phần văn bản cần khổ ngang — dùng field này để chỉ đổi hướng đúng đoạn cần thiết.",
                            },
                        },
                        "additionalProperties": False,
                    },
                },
                "orientation": {
                    "type": "string",
                    "enum": ["portrait", "landscape"],
                    "description": "Hướng giấy MẶC ĐỊNH cho toàn văn bản (item không tự khai báo `section_orientation` sẽ theo hướng này). Chỉ dùng khi TOÀN BỘ văn bản cần khổ ngang; nếu chỉ 1-2 bảng/phụ lục cần khổ ngang còn phần còn lại khổ dọc, dùng `section_orientation` trên từng item thay vì set field này thành landscape.",
                },
            },
            "required": ["output_file_name", "paragraphs"],
            "additionalProperties": False,
        },
    },
    {
        "name": "van_ban_hanh_chinh_list_document_types",
        "description": "Liệt kê mọi document_type_key hợp lệ kèm structure (thứ tự role bắt buộc) và toàn bộ role hợp lệ — gọi trước khi dựng paragraphs để biết chính xác role nào được dùng.",
        "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
    },
    {
        "name": "van_ban_hanh_chinh_convert_pdf",
        "description": "Chuyển 1 file .docx (đã tạo bằng van_ban_hanh_chinh_write_docx) sang PDF bằng LibreOffice headless.",
        "inputSchema": {
            "type": "object",
            "properties": {"file_path": {"type": "string"}},
            "required": ["file_path"],
            "additionalProperties": False,
        },
    },
    {
        "name": "van_ban_hanh_chinh_learned_rules_get",
        "description": "Đọc kho quy tắc đã học từ skill document-revision-learning (references/learned-rules.json). Gọi trước khi soạn văn bản để áp dụng cách diễn đạt/định dạng đã được rút ra từ các lần người dùng sửa tay trước đó cho cùng document_type_key. Trả {} nếu chưa có lượt học nào.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "document_type_key": {
                    "type": "string",
                    "description": "Nếu truyền, chỉ trả rule của đúng loại văn bản này. Để trống để lấy toàn bộ kho.",
                },
            },
            "additionalProperties": False,
        },
    },
    {
        "name": "van_ban_hanh_chinh_learned_rules_save",
        "description": "Ghi đè quy tắc đã học cho 1 document_type_key vào references/learned-rules.json — chỉ dùng bởi skill document-revision-learning, ngay sau khi so sánh AI_GENERATED với USER_CORRECTED, KHÔNG có bước chờ người dùng duyệt. `rules` phải là toàn bộ object đã merge đúng observation_count/status (xem SKILL.md của document-revision-learning) — tool này chỉ ghi đè nguyên trạng, không tự merge hộ.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "document_type_key": {"type": "string"},
                "rules": {
                    "type": "object",
                    "description": "Object đầy đủ cho document_type_key này, ví dụ {\"content_pattern\": [...], \"format_overrides\": {...}}.",
                },
            },
            "required": ["document_type_key", "rules"],
            "additionalProperties": False,
        },
    },
]


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            request = json.loads(line)
        except Exception:
            continue
        request_id = request.get("id")
        method = request.get("method")
        params = request.get("params") or {}

        try:
            if method == "initialize":
                _send({
                    "jsonrpc": "2.0", "id": request_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {"tools": {}},
                        "serverInfo": {"name": "van-ban-hanh-chinh", "version": "0.1.0"},
                    },
                })
            elif method == "notifications/initialized":
                continue
            elif method == "tools/list":
                _send({"jsonrpc": "2.0", "id": request_id, "result": {"tools": TOOLS}})
            elif method == "tools/call":
                name = params.get("name")
                args = params.get("arguments") or {}
                if name == "van_ban_hanh_chinh_write_docx":
                    result = _write_docx(
                        str(args.get("template_path") or ""),
                        str(args.get("output_file_name") or ""),
                        args.get("paragraphs") or [],
                        document_type_key=str(args.get("document_type_key") or ""),
                        orientation=args.get("orientation"),
                    )
                elif name == "van_ban_hanh_chinh_list_document_types":
                    result = _list_document_types()
                elif name == "van_ban_hanh_chinh_convert_pdf":
                    result = _convert_pdf(str(args.get("file_path") or ""))
                elif name == "van_ban_hanh_chinh_learned_rules_get":
                    result = _get_learned_rules(str(args.get("document_type_key") or ""))
                elif name == "van_ban_hanh_chinh_learned_rules_save":
                    result = _save_learned_rules(
                        str(args.get("document_type_key") or ""),
                        args.get("rules") or {},
                    )
                else:
                    raise ValueError(f"unknown tool: {name}")
                _send({
                    "jsonrpc": "2.0", "id": request_id,
                    "result": {
                        "content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False)}],
                        "isError": False,
                    },
                })
            else:
                _error_response(request_id, -32601, f"unknown method: {method}")
        except Exception as exc:
            _send({
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [{"type": "text", "text": json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False)}],
                    "isError": True,
                },
            })


if __name__ == "__main__":
    main()
