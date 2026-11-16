"""Bộ tool xử lý văn bản và bảng tính cho các skill: điền mẫu Word, gộp báo cáo Excel, tổng hợp điểm, đổi PDF,
so sánh văn bản, theo dõi hạn xử lý, rà tên địa danh cũ, kiểm tra bảng tính kế toán."""
import csv
import difflib
import json
import re
import shutil
import subprocess
import tempfile
import unicodedata
from datetime import date, datetime, timedelta
from pathlib import Path

from .tools import _resolve, tool

MAX_DOCS = 500
MAX_ROWS = 20000
ERRORS = ("#REF!", "#DIV/0!", "#N/A", "#NAME?", "#VALUE!", "#NUM!", "#NULL!")


# ============================== tiện ích dùng chung ==============================
def _norm(s) -> str:
    """Chữ thường, bỏ dấu tiếng Việt, mọi ký tự không phải chữ-số thành khoảng trắng."""
    s = unicodedata.normalize("NFD", str(s if s is not None else "").lower().replace("đ", "d"))
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def _rd(ctx, path: str, exts: tuple[str, ...] = ()) -> Path:
    if not path or not str(path).strip():
        raise ValueError("Thiếu đường dẫn file.")
    p = _resolve(ctx, path, "read")
    if not p.is_file():
        raise FileNotFoundError(f"Không tìm thấy file: {path}")
    if exts and p.suffix.lower() not in exts:
        raise ValueError(f"File '{p.name}' phải có đuôi {' hoặc '.join(exts)}.")
    return p


def _wr(ctx, path: Path | str) -> Path:
    p = _resolve(ctx, str(path), "write")
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def _safe_name(s: str, default: str = "van-ban") -> str:
    s = re.sub(r"[^\w\- ]+", "_", str(s), flags=re.UNICODE).strip(" _.") or default
    return re.sub(r"\s+", "-", s)[:80]


def _json_arg(value, what: str):
    if isinstance(value, str):
        try:
            return json.loads(value)
        except json.JSONDecodeError as e:
            raise ValueError(f"{what} không phải JSON hợp lệ ({e.msg}).") from e
    return value


def _to_num(v):
    """Số thật -> float; chuỗi trông như số (1.234,5 hoặc 1,234.5) -> float; còn lại None."""
    if isinstance(v, bool):
        return None
    if isinstance(v, (int, float)):
        return float(v)
    if not isinstance(v, str):
        return None
    t = v.strip().replace(" ", "").replace(" ", "")
    if not t or not re.fullmatch(r"[-+]?[\d.,]+%?", t):
        return None
    t = t.rstrip("%")
    if "." in t and "," in t:
        dec = "," if t.rfind(",") > t.rfind(".") else "."
        t = t.replace("." if dec == "," else ",", "").replace(dec, ".")
    elif "," in t:
        t = t.replace(",", "") if re.fullmatch(r"[-+]?\d{1,3}(,\d{3})+", t) else t.replace(",", ".")
    elif "." in t and re.fullmatch(r"[-+]?\d{1,3}(\.\d{3})+", t):
        t = t.replace(".", "")
    try:
        return float(t)
    except ValueError:
        return None


def _is_text(v) -> bool:
    return isinstance(v, str) and bool(v.strip()) and _to_num(v) is None


def _parse_date(v):
    if isinstance(v, datetime):
        return v.date()
    if isinstance(v, date):
        return v
    if not isinstance(v, str):
        return None
    t = v.strip()
    for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%d.%m.%Y", "%Y-%m-%d", "%d/%m/%y", "%Y/%m/%d"):
        try:
            return datetime.strptime(t[:10] if fmt.endswith("Y") and len(t) > 10 else t, fmt).date()
        except ValueError:
            continue
    return None


def _fmt_cell(v) -> str:
    if v is None:
        return ""
    if isinstance(v, datetime):
        return v.strftime("%d/%m/%Y")
    if isinstance(v, date):
        return v.strftime("%d/%m/%Y")
    if isinstance(v, float) and v.is_integer():
        return str(int(v))
    return str(v)


def _match_header(h: str, cands: list[str]) -> int | None:
    """Tìm tên cột chuẩn gần nhất (so sánh không dấu): trùng khít, chứa nhau (>=2 từ), hoặc giống >= 0.8."""
    hn = _norm(h)
    if not hn:
        return None
    if hn in cands:
        return cands.index(hn)
    ht = set(hn.split())
    for i, c in enumerate(cands):
        ct = set(c.split())
        small, big = (ht, ct) if len(ht) <= len(ct) else (ct, ht)
        if len(small) >= 2 and small <= big:
            return i
    best, bi = 0.0, None
    for i, c in enumerate(cands):
        r = difflib.SequenceMatcher(None, hn, c).ratio()
        if r > best:
            best, bi = r, i
    return bi if best >= 0.8 else None


def _header_row(grid: list[list]) -> int | None:
    """Dòng tiêu đề bảng: dòng đầu tiên có nhiều ô chữ (bỏ qua dòng tiêu đề lớn chỉ có 1 ô)."""
    counts = [sum(_is_text(c) for c in row) for row in grid[:40]]
    mx = max(counts or [0])
    if mx < 2:
        return None
    for i, n in enumerate(counts):
        if n >= max(2, 0.6 * mx) and i + 1 < len(grid) and any(c is not None and str(c).strip() for c in grid[i + 1]):
            return i
    return None


def _grid(ws) -> list[list]:
    return [list(r) for r in ws.iter_rows(values_only=True, max_row=MAX_ROWS)]


def _table(ws):
    """(chỉ số dòng tiêu đề, danh sách tiêu đề, [(số dòng Excel, giá trị)]) hoặc None."""
    g = _grid(ws)
    h = _header_row(g)
    if h is None:
        return None
    headers = [str(c).strip() if c is not None else "" for c in g[h]]
    rows = [(h + 2 + i, r) for i, r in enumerate(g[h + 1:])]
    return h, headers, rows


def _is_total_row(vals) -> bool:
    for v in vals:
        if _is_text(v):
            n = _norm(v)
            return n.startswith(("tong", "cong ", "total")) or n == "cong"
        if v is not None and str(v).strip():
            continue
    return False


def _read_records(p: Path) -> list[dict]:
    """Đọc .xlsx/.csv: dòng tiêu đề -> tên trường; mỗi dòng sau là một bản ghi."""
    if p.suffix.lower() == ".csv":
        text = p.read_text(encoding="utf-8-sig", errors="replace")
        try:
            dialect = csv.Sniffer().sniff(text[:2000], delimiters=",;\t")
        except csv.Error:
            dialect = csv.excel
        rows = [list(r) for r in csv.reader(text.splitlines(), dialect)]
    else:
        from openpyxl import load_workbook
        wb = load_workbook(p, data_only=True, read_only=True)
        rows = [list(r) for r in wb.worksheets[0].iter_rows(values_only=True, max_row=MAX_ROWS)]
    h = next((i for i, r in enumerate(rows) if sum(1 for c in r if c is not None and str(c).strip()) >= 1), None)
    if h is None:
        raise ValueError(f"File '{p.name}' không có dữ liệu.")
    heads = [str(c).strip() if c is not None else "" for c in rows[h]]
    out = []
    for r in rows[h + 1:]:
        if not any(c is not None and str(c).strip() for c in r):
            continue
        out.append({heads[i]: r[i] for i in range(min(len(heads), len(r))) if heads[i]})
    return out


# ============================== 1. điền mẫu Word ==============================
_PH = re.compile(r"\{\{\s*([^{}|\s][^{}|]*?)\s*(?:\|\s*([^{}]*?)\s*)?\}\}")


def _replace_range(par, s: int, e: int, new: str) -> None:
    """Thay ký tự [s,e) của đoạn (đếm trên văn bản các run) bằng `new`, giữ định dạng của run chứa vị trí s."""
    off, first = 0, True
    for r in par.runs:
        t = r.text
        a, b = max(s - off, 0), min(e - off, len(t))
        if a < b:
            r.text = t[:a] + (new if first else "") + t[b:]
            first = False
        off += len(t)


def _iter_pars(doc):
    seen: set = set()  # giữ chính phần tử (không dùng id(): id lxml bị tái sử dụng khi đối tượng bị thu hồi)

    def walk(c):
        for p in c.paragraphs:
            if p._p not in seen:
                seen.add(p._p)
                yield p
        for t in getattr(c, "tables", []):
            for row in t.rows:
                done: set = set()
                for cell in row.cells:
                    if cell._tc in done:
                        continue
                    done.add(cell._tc)
                    yield from walk(cell)

    yield from walk(doc)
    for sec in doc.sections:
        for part in (sec.header, sec.footer, sec.first_page_header, sec.first_page_footer, sec.even_page_header, sec.even_page_footer):
            try:
                yield from walk(part)
            except (AttributeError, KeyError):
                continue


def _apply_filter(value, flt: str) -> str:
    text = _fmt_cell(value)
    if not flt:
        return text
    f = flt.strip()
    low = f.lower()
    if low == "upper":
        return text.upper()
    if low == "lower":
        return text.lower()
    if low == "title":
        return text.title()
    if low == "number":
        n = _to_num(value)
        return f"{n:,.0f}".replace(",", ".") if n is not None and n.is_integer() else (f"{n:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") if n is not None else text)
    if low.startswith("date:"):
        d = _parse_date(value)
        if d is None:
            return text
        fmt = f[5:].strip() or "dd/mm/yyyy"
        for a, b in (("yyyy", "%Y"), ("dd", "%d"), ("mm", "%m"), ("yy", "%y")):
            fmt = fmt.replace(a, b)
        return d.strftime(fmt)
    return text


def _lookup(rec: dict, key: str):
    if key in rec:
        return True, rec[key]
    nk = _norm(key)
    for k, v in rec.items():
        if _norm(k) == nk:
            return True, v
    return False, None


def _fill_doc(doc, rec: dict, unknown: set[str]) -> int:
    n = 0
    for par in _iter_pars(doc):
        text = "".join(r.text for r in par.runs)
        if "{{" not in text:
            continue
        for m in reversed(list(_PH.finditer(text))):
            ok, val = _lookup(rec, m.group(1))
            if not ok:
                unknown.add(m.group(1))
                continue
            _replace_range(par, m.start(), m.end(), _apply_filter(val, m.group(2) or ""))
            n += 1
    return n


@tool("docx_fill_template", "Điền dữ liệu vào mẫu Word (.docx) có các trường {{ten_truong}}, GIỮ NGUYÊN định dạng; xử lý cả trường bị tách giữa nhiều đoạn chữ, trong bảng, đầu/chân trang. "
      "Hỗ trợ bộ lọc {{truong|upper}}, {{truong|lower}}, {{truong|title}}, {{truong|number}}, {{truong|date:dd/mm/yyyy}}. Một văn bản (data là object JSON) hoặc nhiều văn bản (mảng JSON hoặc data_path là .xlsx/.csv có dòng đầu là tên trường, mỗi dòng một file). Tối đa 500 văn bản.",
      {"template_path": ("string", "đường dẫn mẫu .docx"), "data": ("string", "JSON object (1 văn bản) hoặc mảng object (nhiều văn bản)"),
       "data_path": ("string", "file .xlsx/.csv: dòng tiêu đề là tên trường, mỗi dòng sau là một văn bản"),
       "output_dir": ("string", "thư mục xuất (mặc định: <tên mẫu>-dien-mau cạnh file mẫu)"), "name_field": ("string", "tên trường dùng đặt tên file đầu ra (vd ho_ten)")},
      required=["template_path"], risk="file")
def docx_fill_template(ctx, template_path, data="", data_path="", output_dir="", name_field=""):
    from docx import Document
    tpl = _rd(ctx, template_path, (".docx",))
    if data_path:
        records = _read_records(_rd(ctx, data_path, (".xlsx", ".csv")))
    elif data:
        d = _json_arg(data, "data")
        records = [d] if isinstance(d, dict) else d
        if not isinstance(records, list) or not all(isinstance(r, dict) for r in records):
            raise ValueError("data phải là object JSON hoặc mảng các object.")
    else:
        raise ValueError("Cần data (JSON) hoặc data_path (.xlsx/.csv).")
    if not records:
        raise ValueError("Không có bản ghi dữ liệu nào để điền.")
    if len(records) > MAX_DOCS:
        raise ValueError(f"Quá nhiều văn bản ({len(records)}): tối đa {MAX_DOCS} mỗi lần. Hãy chia nhỏ dữ liệu.")
    out = _wr(ctx, output_dir) if output_dir else _wr(ctx, tpl.parent / f"{tpl.stem}-dien-mau")
    out.mkdir(parents=True, exist_ok=True)
    unknown: set[str] = set()
    files, used = [], set()
    for i, rec in enumerate(records, 1):
        doc = Document(str(tpl))
        _fill_doc(doc, rec, unknown)
        base = ""
        if name_field:
            ok, v = _lookup(rec, name_field)
            base = _safe_name(_fmt_cell(v), "") if ok else ""
        name = f"{base or f'{tpl.stem}-{i:03d}'}"
        cand, k = name, 2
        while cand in used:
            cand, k = f"{name}-{k}", k + 1
        used.add(cand)
        f = out / f"{cand}.docx"
        doc.save(str(f))
        files.append(f)
    lines = [f"Đã tạo {len(files)} văn bản trong {out}:"] + [f"- {f.name}" for f in files[:30]]
    if len(files) > 30:
        lines.append(f"… và {len(files) - 30} file nữa")
    if unknown:
        lines.append("LƯU Ý: các trường trong mẫu không có trong dữ liệu (đã để nguyên {{…}}): " + ", ".join(sorted(unknown)))
    return "\n".join(lines)


# ============================== 2. gộp báo cáo Excel ==============================
_KEY_NAMES = ("ma don vi", "ma so", "ma", "so hieu", "ten don vi", "don vi", "ho va ten", "ho ten", "ten", "so ky hieu")


def _col_kind(vals: list) -> str:
    ne = [v for v in vals if v is not None and str(v).strip()]
    if not ne:
        return "empty"
    nums = sum(1 for v in ne if _to_num(v) is not None)
    return "num" if nums >= 0.6 * len(ne) else "text"


@tool("excel_merge_reports", "Gộp nhiều file báo cáo Excel (.xlsx) có bố cục khác nhau thành một bảng: tự tìm dòng tiêu đề, ghép cột theo tên gần giống (không phân biệt dấu), thêm cột 'Nguồn'; "
      "kèm sheet 'Sai lệch' liệt kê cột không khớp/thiếu, khóa trùng, chữ lẫn trong cột số, tổng của từng file so với tổng sau gộp.",
      {"paths": ("string", "JSON mảng đường dẫn .xlsx hoặc danh sách cách nhau bằng dấu phẩy"), "output_path": ("string", "file .xlsx kết quả"),
       "header_hints": ("string", "tên các cột chuẩn, cách nhau bằng dấu phẩy (tùy chọn; mặc định lấy theo file đầu tiên)")},
      required=["paths", "output_path"], risk="file")
def excel_merge_reports(ctx, paths, output_path, header_hints=""):
    from openpyxl import Workbook, load_workbook
    from openpyxl.styles import Font, PatternFill
    raw = paths.strip() if isinstance(paths, str) else paths
    if isinstance(raw, str):
        raw = json.loads(raw) if raw.startswith("[") else [x.strip() for x in raw.split(",") if x.strip()]
    if not isinstance(raw, list) or len(raw) < 1:
        raise ValueError("paths phải là mảng JSON hoặc danh sách đường dẫn cách nhau bằng dấu phẩy.")
    files = [_rd(ctx, p, (".xlsx", ".xlsm")) for p in raw]
    out = _wr(ctx, output_path if str(output_path).lower().endswith(".xlsx") else f"{output_path}.xlsx")
    canon = [h.strip() for h in header_hints.split(",") if h.strip()]
    canon_n = [_norm(h) for h in canon]
    hinted = bool(canon)
    issues: list[tuple[str, str, str, str]] = []
    data: list[dict] = []  # mỗi dòng: {"src","row","vals":{ci:value}}
    stats: list[dict] = []  # tổng theo file/cột
    for f in files:
        wb = load_workbook(f, data_only=True)
        tabs = []
        for ws in wb.worksheets:
            t = _table(ws)
            if t and any(_is_text(v) or v is not None for _, r in t[2] for v in r):
                tabs.append((ws.title, t))
        if not tabs:
            issues.append(("Không đọc được", f.name, "", "không tìm thấy bảng có dòng tiêu đề"))
            continue
        for title, (_, headers, rows) in tabs:
            src = f.name if len(tabs) == 1 else f"{f.name}!{title}"
            colmap: dict[int, int] = {}
            for j, h in enumerate(headers):
                if not h:
                    continue
                ci = _match_header(h, canon_n)
                if ci is None:
                    canon.append(h)
                    canon_n.append(_norm(h))
                    ci = len(canon) - 1
                    if hinted or files.index(f) > 0 or title != tabs[0][0]:
                        issues.append(("Cột không khớp", src, h, "cột chỉ có ở file này (đã thêm thành cột mới)"))
                colmap[j] = ci
            present = set(colmap.values())
            for ci, c in enumerate(canon):
                if ci not in present and (hinted or files.index(f) > 0 or title != tabs[0][0]):
                    issues.append(("Cột thiếu", src, c, "file này không có cột này"))
            col_vals: dict[int, list] = {ci: [] for ci in present}
            reported_total: dict[int, float] = {}
            for rn, r in rows:
                vals = {colmap[j]: r[j] for j in colmap if j < len(r) and r[j] is not None and str(r[j]).strip() != ""}
                if not vals:
                    continue
                if _is_total_row(r):
                    for ci, v in vals.items():
                        n = _to_num(v)
                        if n is not None:
                            reported_total[ci] = n
                    continue
                data.append({"src": src, "row": rn, "vals": vals, "colmap": colmap, "headers": headers})
                for ci, v in vals.items():
                    col_vals[ci].append((rn, v))
            stats.append({"src": src, "col_vals": col_vals, "reported": reported_total})
    if not data:
        raise ValueError("Không gộp được dòng dữ liệu nào. Kiểm tra file có dòng tiêu đề rõ ràng không.")
    # kiểu cột chuẩn: số nếu đa số file coi là số
    kinds: dict[int, str] = {}
    for ci in range(len(canon)):
        pooled = [v for s_ in stats for _, v in s_["col_vals"].get(ci, [])]
        kinds[ci] = "num" if _col_kind(pooled) == "num" else "text"  # gộp mọi file: đa số ô là số thì là cột số
    sums_file: dict[tuple[str, int], float] = {}
    for s in stats:
        for ci, items in s["col_vals"].items():
            if kinds.get(ci) != "num":
                continue
            tot = 0.0
            for rn, v in items:
                n = _to_num(v)
                if n is None:
                    issues.append(("Chữ trong cột số", s["src"], f"{canon[ci]} (dòng {rn})", f"giá trị '{str(v)[:40]}' không phải số, bị bỏ qua khi cộng"))
                    continue
                if isinstance(v, str):
                    issues.append(("Số lưu dạng chữ", s["src"], f"{canon[ci]} (dòng {rn})", f"'{v}' lưu dạng chữ, đã đổi thành số"))
                tot += n
            sums_file[(s["src"], ci)] = tot
    # khóa trùng
    key_ci = next((canon_n.index(k) for k in _KEY_NAMES if k in canon_n), None)
    if key_ci is None:
        key_ci = next((ci for ci in range(len(canon)) if kinds.get(ci) == "text" and canon_n[ci] != "stt"), None)
    if key_ci is not None:
        seen: dict[str, list] = {}
        for d in data:
            v = d["vals"].get(key_ci)
            if v is not None:
                seen.setdefault(_norm(v), []).append(d)
        for k, ds in seen.items():
            if len(ds) > 1:
                issues.append(("Khóa trùng", "; ".join(f"{d['src']} dòng {d['row']}" for d in ds[:6]), f"{canon[key_ci]} = {_fmt_cell(ds[0]['vals'][key_ci])}", f"xuất hiện {len(ds)} lần"))
    # ghi kết quả
    wb = Workbook()
    ws = wb.active
    ws.title = "Tổng hợp"
    ws.append([*canon, "Nguồn"])
    merged_sum = {ci: 0.0 for ci in range(len(canon)) if kinds.get(ci) == "num"}
    for d in data:
        row = []
        for ci in range(len(canon)):
            v = d["vals"].get(ci)
            if kinds.get(ci) == "num" and v is not None:
                n = _to_num(v)
                if n is not None:
                    merged_sum[ci] += n
                    v = int(n) if n.is_integer() else n
            row.append(v)
        ws.append([*row, f"{d['src']} · dòng {d['row']}"])
    for c in ws[1]:
        c.font = Font(bold=True)
    for ci, tot in merged_sum.items():
        for s in stats:
            rep = s["reported"].get(ci)
            calc = sums_file.get((s["src"], ci))
            if rep is not None and calc is not None and abs(rep - calc) > 0.01:
                issues.append(("Tổng lệch", s["src"], canon[ci], f"dòng Tổng ghi {rep:g} nhưng cộng các dòng được {calc:g}"))
    for ci, tot in merged_sum.items():
        parts = [f"{s}: {v:g}" for (s, c), v in sums_file.items() if c == ci]
        total_files = sum(v for (s, c), v in sums_file.items() if c == ci)
        flag = "" if abs(total_files - tot) < 0.01 else " (LỆCH so với bảng gộp)"
        issues.append(("Tổng theo file", "; ".join(parts), canon[ci], f"tổng các file = {total_files:g}, tổng sau gộp = {tot:g}{flag}"))
    wd = wb.create_sheet("Sai lệch")
    wd.append(["Loại", "Nguồn", "Cột / vị trí", "Chi tiết"])
    for c in wd[1]:
        c.font = Font(bold=True)
    red = PatternFill("solid", fgColor="FDE2E2")
    for it in issues:
        wd.append(list(it))
        if it[0] in ("Tổng lệch", "Khóa trùng", "Không đọc được") or "LỆCH" in it[3]:
            for c in wd[wd.max_row]:
                c.fill = red
    for sh in (ws, wd):
        for col in sh.columns:
            sh.column_dimensions[col[0].column_letter].width = min(max(len(str(c.value or "")) for c in col[:60]) + 2, 60)
    wb.save(out)
    n_bad = sum(1 for i in issues if i[0] != "Tổng theo file")
    lines = [f"Đã gộp {len(data)} dòng từ {len(files)} file vào {out} (sheet 'Tổng hợp', {len(canon)} cột + Nguồn).", f"Sheet 'Sai lệch': {n_bad} điểm cần xem."]
    lines += [f"- [{i[0]}] {i[1]} · {i[2]}: {i[3]}" for i in issues[:15]]
    if len(issues) > 15:
        lines.append(f"… xem thêm trong sheet 'Sai lệch' ({len(issues)} mục)")
    return "\n".join(lines)


# ============================== 3. tổng hợp điểm lớp ==============================
_SKIP_COLS = ("stt", "tt", "lop", "ngay sinh", "ghi chu", "gioi tinh", "ma hs", "ma hoc sinh", "so thu tu")


@tool("grade_summary", "Tổng hợp điểm lớp từ file Excel (cột Họ tên + các cột điểm): điểm trung bình theo hệ số, xếp loại (mặc định Tốt ≥ 8, Khá ≥ 6,5, Đạt ≥ 5, còn lại Chưa đạt; có thể sửa ngưỡng trong sheet 'Cấu hình' của file kết quả), thứ hạng, thống kê lớp. "
      "File kết quả dùng công thức Excel thật (SUMPRODUCT, RANK, COUNTIF…) nên đổi điểm là kết quả tự cập nhật.",
      {"path": ("string", "file .xlsx bảng điểm"), "he_so": ("string", "hệ số các cột điểm theo thứ tự, vd '1,1,2,3'"), "output_path": ("string", "file .xlsx kết quả (mặc định: <tên>-tong-hop.xlsx)")},
      required=["path"], risk="file")
def grade_summary(ctx, path, he_so="1,1,2,3", output_path=""):
    from openpyxl import Workbook, load_workbook
    from openpyxl.styles import Font
    from openpyxl.utils import get_column_letter as L
    src = _rd(ctx, path, (".xlsx", ".xlsm"))
    try:
        weights = [float(x) for x in re.split(r"[,; ]+", str(he_so).strip()) if x]
    except ValueError as e:
        raise ValueError("he_so phải là các số cách nhau bằng dấu phẩy, vd '1,1,2,3'.") from e
    if not weights or any(w <= 0 for w in weights):
        raise ValueError("he_so cần ít nhất một số dương.")
    wb = load_workbook(src, data_only=True)
    t = _table(wb.worksheets[0])
    if not t:
        raise ValueError("Không tìm thấy dòng tiêu đề (cần cột Họ tên và các cột điểm).")
    _, headers, rows = t
    name_j = next((j for j, h in enumerate(headers) if "ho" in _norm(h).split() and "ten" in _norm(h).split()), None)
    if name_j is None:
        name_j = next((j for j, h in enumerate(headers) if _norm(h) in ("ten", "ho ten", "ten hoc sinh")), None)
    if name_j is None:
        raise ValueError("Không thấy cột 'Họ tên'. Hãy đặt tên cột là 'Họ và tên'.")
    score_js = [j for j, h in enumerate(headers) if h and j != name_j and _norm(h) not in _SKIP_COLS
                and _col_kind([r[j] for _, r in rows if j < len(r)]) == "num"]
    if not score_js:
        raise ValueError("Không thấy cột điểm (cột số) nào.")
    warns = []
    if len(weights) < len(score_js):
        warns.append(f"Chỉ có {len(weights)} hệ số cho {len(score_js)} cột điểm: các cột còn lại tính hệ số 1.")
        weights += [1.0] * (len(score_js) - len(weights))
    elif len(weights) > len(score_js):
        warns.append(f"Có {len(weights)} hệ số nhưng chỉ {len(score_js)} cột điểm: bỏ bớt hệ số thừa.")
        weights = weights[:len(score_js)]
    students = []
    for rn, r in rows:
        nm = r[name_j] if name_j < len(r) else None
        if nm is None or not str(nm).strip() or _is_total_row(r):
            continue
        students.append((str(nm).strip(), [(_to_num(r[j]) if j < len(r) else None) for j in score_js]))
    if not students:
        raise ValueError("Không có học sinh nào trong bảng.")
    out = _wr(ctx, output_path or src.with_name(f"{src.stem}-tong-hop.xlsx"))
    o = Workbook()
    ws = o.active
    ws.title = "Điểm"
    cfg = o.create_sheet("Cấu hình")
    cfg.append(["Ngưỡng Tốt", 8])
    cfg.append(["Ngưỡng Khá", 6.5])
    cfg.append(["Ngưỡng Đạt", 5])
    cfg.append(["(Sửa các ô trên, xếp loại ở sheet Điểm tự đổi theo)"])
    nsc = len(score_js)
    first_sc, last_sc = 3, 2 + nsc
    avg_col, rank_col, grade_col = last_sc + 1, last_sc + 2, last_sc + 3
    ws.append(["STT", "Họ và tên", *[headers[j] for j in score_js], "ĐTB", "Xếp loại", "Thứ hạng"])
    ws.append(["", "Hệ số", *weights, "", "", ""])
    for c in ws[1]:
        c.font = Font(bold=True)
    for c in ws[2]:
        c.font = Font(italic=True)
    n = len(students)
    r0, r1 = 3, 2 + n
    wr = f"${L(first_sc)}$2:${L(last_sc)}$2"
    calc = []
    for i, (nm, sc) in enumerate(students):
        r = r0 + i
        rng = f"{L(first_sc)}{r}:{L(last_sc)}{r}"
        avg_f = f'=IF(SUMPRODUCT(--({rng}<>""),{wr})=0,"",ROUND(SUMPRODUCT({rng},{wr})/SUMPRODUCT(--({rng}<>""),{wr}),1))'
        a = L(avg_col)
        grade_f = f"=IF({a}{r}=\"\",\"\",IF({a}{r}>='Cấu hình'!$B$1,\"Tốt\",IF({a}{r}>='Cấu hình'!$B$2,\"Khá\",IF({a}{r}>='Cấu hình'!$B$3,\"Đạt\",\"Chưa đạt\"))))"
        rank_f = f"=IF({a}{r}=\"\",\"\",RANK({a}{r},${a}${r0}:${a}${r1}))"
        ws.append([i + 1, nm, *sc, avg_f, grade_f, rank_f])
        got = [(s, w) for s, w in zip(sc, weights) if s is not None]
        calc.append(round(sum(s * w for s, w in got) / sum(w for _, w in got), 1) if got else None)
    st = o.create_sheet("Thống kê")
    a = L(avg_col)
    g = L(grade_col)
    st.append(["Chỉ tiêu", "Giá trị"])
    for c in st[1]:
        c.font = Font(bold=True)
    st.append(["Sĩ số", f"=COUNTA('Điểm'!B{r0}:B{r1})"])
    for lab in ("Tốt", "Khá", "Đạt", "Chưa đạt"):
        st.append([f"Số HS {lab}", f"=COUNTIF('Điểm'!{g}{r0}:{g}{r1},\"{lab}\")"])
    st.append(["ĐTB lớp", f"=ROUND(AVERAGE('Điểm'!{a}{r0}:{a}{r1}),2)"])
    st.append(["ĐTB cao nhất", f"=MAX('Điểm'!{a}{r0}:{a}{r1})"])
    st.append(["ĐTB thấp nhất", f"=MIN('Điểm'!{a}{r0}:{a}{r1})"])
    for sh, wd in ((ws, {"A": 6, "B": 28}), (st, {"A": 20, "B": 12}), (cfg, {"A": 18, "B": 10})):
        for k, v in wd.items():
            sh.column_dimensions[k].width = v
    o.save(out)
    vals = [x for x in calc if x is not None]
    th = (8, 6.5, 5)
    def grade(x):
        return "Tốt" if x >= th[0] else "Khá" if x >= th[1] else "Đạt" if x >= th[2] else "Chưa đạt"
    cnt = {k: 0 for k in ("Tốt", "Khá", "Đạt", "Chưa đạt")}
    for x in vals:
        cnt[grade(x)] += 1
    best = sorted(zip([s[0] for s in students], calc), key=lambda z: -(z[1] or -1))[:3]
    lines = [f"Đã tổng hợp {len(students)} học sinh, {nsc} cột điểm, hệ số {', '.join(f'{w:g}' for w in weights)} → {out}",
             f"ĐTB lớp {sum(vals) / len(vals):.2f} (cao nhất {max(vals):g}, thấp nhất {min(vals):g}). " + ", ".join(f"{k}: {v}" for k, v in cnt.items()) if vals else "Chưa có điểm nào để tính.",
             "Top 3: " + "; ".join(f"{n} ({v:g})" for n, v in best if v is not None)]
    lines += [f"LƯU Ý: {w}" for w in warns]
    miss = [s[0] for s, c in zip(students, calc) if c is None]
    if miss:
        lines.append(f"LƯU Ý: {len(miss)} học sinh chưa có điểm nào: {', '.join(miss[:8])}")
    return "\n".join(lines)


# ============================== 4. đổi sang PDF ==============================
@tool("convert_to_pdf", "Đổi file Word/Excel/PowerPoint (.docx, .xlsx, .pptx, .doc, .xls, .ppt) sang PDF bằng LibreOffice, lưu cạnh file gốc.",
      {"path": ("string", "đường dẫn file cần đổi")}, risk="file")
def convert_to_pdf(ctx, path):
    src = _rd(ctx, path, (".docx", ".xlsx", ".pptx", ".doc", ".xls", ".ppt", ".odt", ".ods", ".odp"))
    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if not soffice:
        raise RuntimeError("Máy chưa cài LibreOffice nên chưa đổi được PDF. Cài LibreOffice (sudo apt install libreoffice) rồi thử lại.")
    dest = _wr(ctx, src.with_suffix(".pdf"))
    with tempfile.TemporaryDirectory() as home:
        try:
            r = subprocess.run([soffice, "--headless", "--norestore", "--convert-to", "pdf", "--outdir", str(dest.parent), str(src)],
                               capture_output=True, text=True, timeout=180, env={**__import__("os").environ, "HOME": home})
        except subprocess.TimeoutExpired as e:
            raise RuntimeError("Đổi PDF quá 180 giây nên đã dừng. File có thể quá nặng hoặc LibreOffice bị treo.") from e
    if not dest.exists():
        raise RuntimeError(f"LibreOffice không tạo được PDF (mã {r.returncode}): {(r.stderr or r.stdout)[:300]}")
    return f"Đã đổi sang PDF: {dest} ({dest.stat().st_size} byte)."


# ============================== 5. so sánh hai văn bản ==============================
def _paragraphs(p: Path) -> list[str]:
    ext = p.suffix.lower()
    if ext == ".docx":
        from docx import Document
        d = Document(str(p))
        out = [x.text for x in d.paragraphs]
        for t in d.tables:
            for row in t.rows:
                out.append(" | ".join(c.text.strip() for c in row.cells))
    elif ext == ".pdf":
        from pypdf import PdfReader
        out = []
        for pg in PdfReader(str(p)).pages:
            out += (pg.extract_text() or "").splitlines()
    elif ext in (".txt", ".md"):
        out = p.read_text(encoding="utf-8", errors="replace").splitlines()
    else:
        raise ValueError(f"Chưa hỗ trợ so sánh file {ext} (chỉ .docx, .pdf, .txt).")
    return [re.sub(r"\s+", " ", x).strip() for x in out if x and x.strip()]


_NUM_DATE = re.compile(r"\d{1,2}/\d{1,2}/\d{2,4}|\d+(?:[.,]\d+)*")


@tool("compare_documents", "So sánh hai văn bản (.docx, .pdf, .txt) từng đoạn: liệt kê đoạn thêm, xóa, sửa và các con số, ngày tháng khác nhau. Dùng để rà bản dự thảo sửa đổi hoặc đối chiếu hai phiên bản.",
      {"path_a": ("string", "bản gốc / cũ"), "path_b": ("string", "bản mới")}, risk="file")
def compare_documents(ctx, path_a, path_b):
    a_p, b_p = _rd(ctx, path_a), _rd(ctx, path_b)
    A, B = _paragraphs(a_p), _paragraphs(b_p)
    sm = difflib.SequenceMatcher(None, A, B, autojunk=False)
    added, removed, changed, numdiff = [], [], [], []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "delete":
            removed += A[i1:i2]
        elif tag == "insert":
            added += B[j1:j2]
        elif tag == "replace":
            old, new = A[i1:i2], B[j1:j2]
            for k in range(min(len(old), len(new))):
                if difflib.SequenceMatcher(None, old[k], new[k]).ratio() >= 0.5:
                    changed.append((old[k], new[k]))
                    x, y = _NUM_DATE.findall(old[k]), _NUM_DATE.findall(new[k])
                    if x != y:
                        numdiff.append((x, y, new[k]))
                else:
                    removed.append(old[k])
                    added.append(new[k])
            removed += old[len(new):] if len(old) > len(new) else []
            added += new[len(old):] if len(new) > len(old) else []
    cut = lambda s, n=150: s if len(s) <= n else s[:n] + "…"  # noqa: E731
    ratio = sm.ratio()
    lines = [f"So sánh {a_p.name} ({len(A)} đoạn) với {b_p.name} ({len(B)} đoạn): giống {ratio * 100:.0f}%. Thêm {len(added)}, xóa {len(removed)}, sửa {len(changed)} đoạn."]
    if not (added or removed or changed):
        lines.append("Hai văn bản giống nhau về nội dung chữ.")
    for title, items in (("ĐOẠN THÊM", added), ("ĐOẠN XÓA", removed)):
        if items:
            lines.append(f"{title} (tối đa 10):")
            lines += [f"+ {cut(x)}" if title == "ĐOẠN THÊM" else f"- {cut(x)}" for x in items[:10]]
    if changed:
        lines.append("ĐOẠN SỬA (tối đa 10):")
        for old, new in changed[:10]:
            lines += [f"- {cut(old)}", f"+ {cut(new)}"]
    if numdiff:
        lines.append("SỐ / NGÀY THÁNG KHÁC NHAU (tối đa 12):")
        for x, y, ctxt in numdiff[:12]:
            lines.append(f"  {', '.join(x) or '(không có)'} → {', '.join(y) or '(không có)'}  trong: {cut(ctxt, 90)}")
    return "\n".join(lines)


# ============================== 6. theo dõi hạn xử lý văn bản ==============================
_ALIASES = {
    "so": ("so ky hieu", "so hieu", "so van ban", "so ky", "so vb"),
    "trich_yeu": ("trich yeu", "noi dung", "ve viec", "tieu de"),
    "ngay_den": ("ngay den", "ngay nhan", "ngay van ban", "ngay vb"),
    "han": ("han xu ly", "han giai quyet", "thoi han", "han tra loi", "han"),
    "nguoi": ("nguoi xu ly", "can bo xu ly", "nguoi thu ly", "chuyen vien", "nguoi phu trach", "phu trach", "xu ly"),
    "trang_thai": ("trang thai", "tinh trang", "ket qua"),
}
_DONE = ("hoan thanh", "da xu ly", "xong", "da giai quyet", "da tra loi", "da hoan", "dong")


def _find_cols(headers: list[str]) -> dict[str, int]:
    norms = [_norm(h) for h in headers]
    out: dict[str, int] = {}
    for key, aliases in _ALIASES.items():
        for al in aliases:
            j = next((i for i, n in enumerate(norms) if n == al), None)
            if j is None:
                j = next((i for i, n in enumerate(norms) if al in n and i not in out.values()), None)
            if j is not None and j not in out.values():
                out[key] = j
                break
    return out


@tool("deadline_report", "Theo dõi hạn xử lý văn bản từ sổ văn bản Excel: tìm các cột số ký hiệu, trích yếu, ngày đến, hạn xử lý, người xử lý, trạng thái (tự nhận tên cột gần giống); liệt kê văn bản QUÁ HẠN (kèm số ngày trễ), SẮP ĐẾN HẠN (≤ 3 ngày), thống kê theo người; xuất file Excel tô màu cạnh file gốc.",
      {"path": ("string", "sổ văn bản .xlsx"), "today": ("string", "ngày làm mốc dd/mm/yyyy (mặc định hôm nay)")}, required=["path"], risk="file")
def deadline_report(ctx, path, today=""):
    from openpyxl import Workbook, load_workbook
    from openpyxl.styles import Font, PatternFill
    src = _rd(ctx, path, (".xlsx", ".xlsm"))
    now = _parse_date(today) if today else date.today()
    if now is None:
        raise ValueError("today phải có dạng dd/mm/yyyy.")
    wb = load_workbook(src, data_only=True)
    t = _table(wb.worksheets[0])
    if not t:
        raise ValueError("Không tìm thấy dòng tiêu đề trong sổ văn bản.")
    _, headers, rows = t
    cols = _find_cols(headers)
    if "han" not in cols:
        raise ValueError("Không thấy cột hạn xử lý. Đặt tên cột là 'Hạn xử lý' (hoặc 'Hạn giải quyết').")
    get = lambda r, k: (r[cols[k]] if k in cols and cols[k] < len(r) else None)  # noqa: E731
    recs, bad_dates = [], 0
    for rn, r in rows:
        if not any(c is not None and str(c).strip() for c in r) or _is_total_row(r):
            continue
        han = _parse_date(get(r, "han"))
        status = _norm(get(r, "trang_thai"))
        done = any(d in status for d in _DONE) if status else False
        if get(r, "han") not in (None, "") and han is None:
            bad_dates += 1
        left = (han - now).days if han else None
        if done:
            tag = "Đã xử lý"
        elif left is None:
            tag = "Chưa có hạn"
        elif left < 0:
            tag = f"Quá hạn {-left} ngày"
        elif left <= 3:
            tag = f"Sắp đến hạn ({left} ngày)"
        else:
            tag = f"Còn {left} ngày"
        recs.append({"rn": rn, "row": [_fmt_cell(c) for c in r[:len(headers)]], "tag": tag, "left": left, "done": done,
                     "who": str(get(r, "nguoi") or "").strip() or "(chưa giao)", "so": _fmt_cell(get(r, "so")), "ty": _fmt_cell(get(r, "trich_yeu"))})
    over = sorted([x for x in recs if not x["done"] and x["left"] is not None and x["left"] < 0], key=lambda x: x["left"])
    soon = sorted([x for x in recs if not x["done"] and x["left"] is not None and 0 <= x["left"] <= 3], key=lambda x: x["left"])
    out_p = _wr(ctx, src.with_name(f"{src.stem}-theo-doi-han.xlsx"))
    o = Workbook()
    ws = o.active
    ws.title = "Theo dõi"
    ws.append([*headers, "Tình trạng hạn"])
    for c in ws[1]:
        c.font = Font(bold=True)
    fill_red, fill_amb, fill_grn = (PatternFill("solid", fgColor=c) for c in ("F8CBAD", "FFE699", "C6E0B4"))
    order = sorted(recs, key=lambda x: (x["done"], x["left"] is None, x["left"] if x["left"] is not None else 0))
    for x in order:
        ws.append([*x["row"], x["tag"]])
        fill = fill_grn if x["done"] else fill_red if x in over else fill_amb if x in soon else None
        if fill:
            for c in ws[ws.max_row]:
                c.fill = fill
    pe = o.create_sheet("Theo người")
    pe.append(["Người xử lý", "Tổng", "Quá hạn", "Sắp đến hạn", "Đã xử lý"])
    for c in pe[1]:
        c.font = Font(bold=True)
    people: dict[str, list[int]] = {}
    for x in recs:
        p = people.setdefault(x["who"], [0, 0, 0, 0])
        p[0] += 1
        p[1] += x in over
        p[2] += x in soon
        p[3] += x["done"]
    for who, v in sorted(people.items(), key=lambda kv: -kv[1][1]):
        pe.append([who, *v])
    for sh in (ws, pe):
        for col in sh.columns:
            sh.column_dimensions[col[0].column_letter].width = min(max(len(str(c.value or "")) for c in col[:50]) + 2, 50)
    o.save(out_p)
    lines = [f"Sổ văn bản: {len(recs)} văn bản, mốc ngày {now:%d/%m/%Y}. Quá hạn {len(over)}, sắp đến hạn {len(soon)}, đã xử lý {sum(x['done'] for x in recs)}. File tô màu: {out_p}"]
    for title, items in (("QUÁ HẠN", over), ("SẮP ĐẾN HẠN (≤ 3 ngày)", soon)):
        if items:
            lines.append(f"{title}:")
            for x in items[:20]:
                label = x["so"] or f"dòng {x['rn']}"
                lines.append(f"- {label} · {x['ty'][:70]} · {x['who']} · {x['tag']}")
            if len(items) > 20:
                lines.append(f"  … và {len(items) - 20} văn bản nữa (xem file Excel)")
    lines.append("THEO NGƯỜI: " + "; ".join(f"{w}: {v[0]} văn bản, {v[1]} quá hạn" for w, v in sorted(people.items(), key=lambda kv: -kv[1][1])[:10]))
    miss = [k for k in ("so", "trich_yeu", "ngay_den", "nguoi", "trang_thai") if k not in cols]
    if miss:
        lines.append("LƯU Ý: không thấy các cột: " + ", ".join(miss))
    if bad_dates:
        lines.append(f"LƯU Ý: {bad_dates} ô hạn không đọc được thành ngày (cần dạng dd/mm/yyyy).")
    return "\n".join(lines)


# ============================== 7. rà tên địa danh / cấp hành chính cũ ==============================
_OLD_LEVEL = re.compile(r"\b(huyện|quận|thị xã|thị trấn)\b", re.IGNORECASE)


def _read_mapping(p: Path) -> list[tuple[str, str]]:
    recs = _read_records(p)
    out = []
    for r in recs:
        vals = [str(v).strip() for v in r.values() if v is not None and str(v).strip()]
        if len(vals) >= 2:
            out.append((vals[0], vals[1]))
    if not out:
        raise ValueError("File ánh xạ cần 2 cột: tên cũ, tên mới (dòng đầu là tiêu đề).")
    return sorted(out, key=lambda x: -len(x[0]))


@tool("place_name_check", "Rà văn bản (.docx hoặc .txt) tìm cấp hành chính và địa danh đã bỏ sau 01/7/2025 (huyện, quận, thị xã, thị trấn) kèm đoạn trích. Nếu có file ánh xạ (cột tên cũ, tên mới; .xlsx hoặc .csv) thì thay tên cũ bằng tên mới và lưu bản đã sửa, giữ nguyên định dạng.",
      {"path": ("string", "văn bản .docx hoặc .txt"), "mapping_path": ("string", "file .xlsx/.csv gồm cột tên cũ, tên mới (tùy chọn)")}, required=["path"], risk="file")
def place_name_check(ctx, path, mapping_path=""):
    src = _rd(ctx, path, (".docx", ".txt"))
    mapping = _read_mapping(_rd(ctx, mapping_path, (".xlsx", ".csv"))) if mapping_path else []
    findings: list[str] = []
    counts: dict[str, int] = {}

    def scan(text: str, where: str):
        for m in _OLD_LEVEL.finditer(text):
            s, e = max(m.start() - 35, 0), min(m.end() + 35, len(text))
            findings.append(f"- {where}: …{text[s:e].strip()}… [{m.group(1)}]")

    def replace_in_text(text: str) -> str:
        for old, new in mapping:
            n = len(re.findall(re.escape(old), text, re.IGNORECASE))
            if n:
                counts[old] = counts.get(old, 0) + n
                text = re.sub(re.escape(old), new.replace("\\", "\\\\"), text, flags=re.IGNORECASE)
        return text

    if src.suffix.lower() == ".txt":
        text = src.read_text(encoding="utf-8", errors="replace")
        for i, ln in enumerate(text.splitlines(), 1):
            scan(ln, f"dòng {i}")
        out = None
        if mapping:
            out = _wr(ctx, src.with_name(f"{src.stem}-da-sua.txt"))
            out.write_text(replace_in_text(text), encoding="utf-8")
    else:
        from docx import Document
        doc = Document(str(src))
        for i, par in enumerate(_iter_pars(doc), 1):
            text = "".join(r.text for r in par.runs)
            if not text.strip():
                continue
            scan(text, f"đoạn {i}")
            for old, new in mapping:
                for m in reversed(list(re.finditer(re.escape(old), text, re.IGNORECASE))):
                    _replace_range(par, m.start(), m.end(), new)
                    counts[old] = counts.get(old, 0) + 1
                text = "".join(r.text for r in par.runs)
        out = None
        if mapping:
            out = _wr(ctx, src.with_name(f"{src.stem}-da-sua.docx"))
            doc.save(str(out))
    lines = [f"Rà {src.name}: {len(findings)} chỗ có cấp hành chính cũ (huyện, quận, thị xã, thị trấn). Từ 01/7/2025 chính quyền địa phương chỉ còn 2 cấp (tỉnh/thành phố, xã/phường/đặc khu), cần đối chiếu từng chỗ."]
    lines += findings[:30]
    if len(findings) > 30:
        lines.append(f"… và {len(findings) - 30} chỗ nữa")
    if mapping:
        if counts:
            lines.append("ĐÃ THAY: " + "; ".join(f"{k} → {dict(mapping)[k]} ({v} chỗ)" for k, v in counts.items()))
            lines.append(f"Bản đã sửa: {out}")
        else:
            lines.append("Không có tên nào trong file ánh xạ xuất hiện trong văn bản, chưa tạo bản sửa.")
    return "\n".join(lines)


# ============================== 8. kiểm tra bảng tính kế toán ==============================
_LOOKS_NUM = re.compile(r"^\s*[-+]?\d{1,3}(?:[.,]\d{3})+(?:[.,]\d+)?\s*$|^\s*[-+]?\d+(?:[.,]\d+)?\s*$")


@tool("excel_audit", "Kiểm tra bảng tính Excel cho kế toán: ô lỗi công thức (#REF!, #DIV/0!…), số lưu dạng chữ, dòng Tổng nhập tay hoặc công thức SUM không khớp các ô phía trên, ô trống trong cột gần như đầy đủ, dòng trùng lặp. Trả danh sách theo mức độ ưu tiên kèm địa chỉ ô.",
      {"path": ("string", "file .xlsx cần kiểm tra")}, required=["path"], risk="file")
def excel_audit(ctx, path):
    from openpyxl import load_workbook
    src = _rd(ctx, path, (".xlsx", ".xlsm"))
    wf = load_workbook(src, data_only=False)
    wv = load_workbook(src, data_only=True)
    high: list[str] = []
    mid: list[str] = []
    low: list[str] = []
    for ws in wf.worksheets:
        wsv = wv[ws.title]
        tag = f"[{ws.title}]"
        grid_v = _grid(wsv)
        grid_f = _grid(ws)
        # 1) lỗi công thức
        for r, row in enumerate(grid_f, 1):
            for c, v in enumerate(row, 1):
                cached = grid_v[r - 1][c - 1] if r - 1 < len(grid_v) and c - 1 < len(grid_v[r - 1]) else None
                addr = f"{tag}!{ws.cell(r, c).coordinate}"
                if isinstance(cached, str) and cached.strip() in ERRORS:
                    high.append(f"{addr}: ô báo lỗi {cached.strip()}" + (f" (công thức {v})" if isinstance(v, str) and v.startswith("=") else ""))
                elif isinstance(v, str) and v.startswith("=") and "#REF!" in v:
                    high.append(f"{addr}: công thức tham chiếu bị hỏng (#REF!): {v[:60]}")
        # 2) số lưu dạng chữ
        ncols = max((len(r) for r in grid_v), default=0)
        for c in range(ncols):
            col = [(r, row[c]) for r, row in enumerate(grid_v) if c < len(row) and row[c] is not None]
            n_num = sum(1 for _, v in col if isinstance(v, (int, float)) and not isinstance(v, bool))
            if n_num >= 2:
                for r, v in col:
                    if isinstance(v, str) and _LOOKS_NUM.match(v):
                        mid.append(f"{tag}!{ws.cell(r + 1, c + 1).coordinate}: số lưu dạng chữ '{v.strip()}' (không được cộng trong SUM)")
        # 3) dòng Tổng
        for r, row in enumerate(grid_v):
            if not any(_is_text(v) and _norm(v).startswith(("tong", "cong")) for v in row[:3]):
                continue
            for c, v in enumerate(row):
                if not isinstance(v, (int, float)) or isinstance(v, bool):
                    continue
                above = []
                k = r - 1
                while k >= 0 and c < len(grid_v[k]) and isinstance(grid_v[k][c], (int, float)) and not isinstance(grid_v[k][c], bool):
                    above.append(grid_v[k][c])
                    k -= 1
                if len(above) < 2:
                    continue
                expect = sum(above)
                fcell = grid_f[r][c] if c < len(grid_f[r]) else None
                addr = f"{tag}!{ws.cell(r + 1, c + 1).coordinate}"
                if isinstance(fcell, str) and fcell.startswith("="):
                    m = re.fullmatch(r"=SUM\(\$?([A-Z]+)\$?(\d+):\$?([A-Z]+)\$?(\d+)\)", fcell.replace(" ", ""), re.I)
                    if m and (int(m.group(4)) < r or int(m.group(2)) > k + 2):
                        mid.append(f"{addr}: {fcell} chưa phủ hết các ô phía trên (các số liên tiếp từ dòng {k + 2} đến {r}), tổng đúng phải là {expect:g}")
                elif abs(v - expect) > 0.5:
                    high.append(f"{addr}: tổng nhập tay {v:g} nhưng cộng các ô phía trên được {expect:g} (lệch {v - expect:+g})")
                else:
                    low.append(f"{addr}: tổng {v:g} nhập tay (không dùng công thức SUM), nên đổi thành =SUM(...)")
        # 4) ô trống trong cột gần đầy đủ + 5) dòng trùng
        tb = _table(wsv)
        if tb:
            h, headers, rows = tb
            data_rows = [(rn, r) for rn, r in rows if any(c is not None and str(c).strip() for c in r) and not _is_total_row(r)]
            if len(data_rows) >= 5:
                for j, hd in enumerate(headers):
                    if not hd:
                        continue
                    empties = [rn for rn, r in data_rows if j >= len(r) or r[j] is None or str(r[j]).strip() == ""]
                    if empties and len(empties) / len(data_rows) <= 0.2:
                        addrs = ", ".join(ws.cell(rn, j + 1).coordinate for rn in empties[:8])
                        low.append(f"{tag} cột '{hd}': {len(empties)} ô trống trong cột gần như đã điền đủ ({addrs}{'…' if len(empties) > 8 else ''})")
                skip = 1 if headers and _norm(headers[0]) in ("stt", "tt") else 0
                seen: dict[tuple, int] = {}
                for rn, r in data_rows:
                    key = tuple(_norm(c) if isinstance(c, str) else c for c in r[skip:len(headers)])
                    if sum(1 for x in key if x not in (None, "")) < 2:
                        continue
                    if key in seen:
                        low.append(f"{tag} dòng {rn} trùng hệt dòng {seen[key]}")
                    else:
                        seen[key] = rn
    total = len(high) + len(mid) + len(low)
    if total == 0:
        return f"Đã kiểm tra {src.name}: không thấy ô lỗi, số lưu dạng chữ, tổng lệch hay dòng trùng."
    lines = [f"Kiểm tra {src.name}: {len(high)} vấn đề nghiêm trọng, {len(mid)} cảnh báo, {len(low)} gợi ý."]
    for title, items in (("NGHIÊM TRỌNG (sai số liệu)", high), ("CẢNH BÁO", mid), ("GỢI Ý", low)):
        if items:
            lines.append(f"{title}:")
            lines += [f"- {x}" for x in items[:15]]
            if len(items) > 15:
                lines.append(f"  … và {len(items) - 15} mục nữa")
    return "\n".join(lines)
