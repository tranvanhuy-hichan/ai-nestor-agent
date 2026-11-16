"""Xáo trộn đề thi trắc nghiệm .docx thành nhiều mã đề, GIỮ NGUYÊN định dạng đề gốc.

Cách làm: mở lại chính file gốc cho từng mã đề, nhận diện các khối câu hỏi ("Câu 1." + đáp án A. B. C. D.), rồi
đổi chỗ các phần tử XML của khối (nên font, bảng, hình ảnh, công thức đi theo từng câu), đánh lại số câu, đánh lại chữ
A/B/C/D, thay "Mã đề". Đáp án đúng nhận diện qua dấu đánh dấu của người ra đề (gạch chân, chữ đỏ, tô nền, in đậm) hoặc
bảng đáp án thủ công.
"""
import copy
import random
import re
from pathlib import Path

from docx import Document
from docx.oxml.ns import qn
from docx.shared import Pt
from docx.text.paragraph import Paragraph
from docx.text.run import Run

Q_RE = re.compile(r"^\s*(?:Câu|CÂU|Bài|BÀI|Question)\s*(\d+)\s*[.:)]?", re.I)
OPT_RE = re.compile(r"^\s*([A-F])\s*[.)]\s*")
MARK_RE = re.compile(r"(?:(?<=\s)|^)([A-F])\s*[.)]\s*")
HEAD_RE = re.compile(r"^\s*(PHẦN|Phần|PART|Part|[IVX]{1,4}[.)]\s)")
FIXED_OPT_RE = re.compile(r"(tất cả|cả\s+[A-F]\b|\b[A-F]\s*(?:và|,)\s*[A-F]\b|đều\s+(?:đúng|sai)|không\s+có\s+(?:đáp án|phương án)|các\s+(?:đáp án|phương án)\s+(?:trên|còn lại))", re.I)
CODE_RE = re.compile(r"(Mã\s*đề(?:\s*thi)?\s*[:：]?\s*)(\d{1,4}|…+|\.{3,}|_{2,})", re.I)
KINDS = ("hl", "red", "u", "b")  # thứ tự ưu tiên khi nhận diện đáp án đúng


class ExamError(ValueError):
    pass


# ---------- tiện ích run/đoạn ----------
def _runs(par: Paragraph) -> list[Run]:
    return list(par.runs)


def _text(par: Paragraph) -> str:
    return "".join(r.text for r in _runs(par))


def _replace_range(par: Paragraph, s: int, e: int, new: str) -> None:
    """Thay ký tự [s,e) của đoạn bằng `new`, giữ định dạng của run chứa vị trí s."""
    off, first = 0, True
    for r in _runs(par):
        t = r.text
        a, b = max(s - off, 0), min(e - off, len(t))
        if a < len(t) and b > 0 and a < b or (first and s == e and off <= s <= off + len(t)):
            r.text = t[:a] + (new if first else "") + t[b:]
            first = False
        off += len(t)


def _marks(r: Run) -> set[str]:
    out = set()
    f = r.font
    if f.underline not in (None, False):
        out.add("u")
    if f.highlight_color is not None:
        out.add("hl")
    if f.bold:
        out.add("b")
    try:
        c = f.color.rgb if f.color is not None and f.color.type is not None else None
    except (AttributeError, ValueError):
        c = None
    if c is not None and c[0] >= 0xC0 and c[1] <= 0x60 and c[2] <= 0x60:
        out.add("red")
    return out


def _range_marks(par: Paragraph, s: int, e: int) -> set[str]:
    """Các kiểu đánh dấu có ở MỌI ký tự không-trắng trong [s,e) (nếu chỉ chữ cái A có gạch chân thì vẫn tính khi cả đoạn chỉ có nhãn)."""
    seen: set[str] | None = None
    anyc = False
    off = 0
    for r in _runs(par):
        t = r.text
        for i, ch in enumerate(t):
            if s <= off + i < e and not ch.isspace():
                anyc = True
                m = _marks(r)
                seen = m if seen is None else seen & m
        off += len(t)
    return seen if anyc and seen else set()


def _any_marks(par: Paragraph, s: int, e: int) -> set[str]:
    """Các kiểu đánh dấu xuất hiện ở BẤT KỲ ký tự không-trắng nào trong [s,e) (dùng cho nhãn A/B/C/D riêng)."""
    out: set[str] = set()
    off = 0
    for r in _runs(par):
        t = r.text
        if any(s <= off + i < e and not ch.isspace() for i, ch in enumerate(t)):
            out |= _marks(r)
        off += len(t)
    return out


def _strip_marks(par: Paragraph, kinds: set[str]) -> None:
    for r in _runs(par):
        m = _marks(r) & kinds
        if "u" in m:
            r.font.underline = False
        if "hl" in m:
            r.font.highlight_color = None
        if "red" in m:
            r.font.color.rgb = None
        if "b" in m:
            r.font.bold = False


def _clone_run(src_r, par: Paragraph, text: str):
    new = copy.deepcopy(src_r)
    for ch in list(new):
        if ch.tag != qn("w:rPr"):
            new.remove(ch)
    Run(new, par).text = text
    return new


# ---------- phân tích đề ----------
class Opt:
    def __init__(self, els):
        self.els = els  # phần tử XML (đoạn đầu là đoạn có nhãn)


class Block:
    def __init__(self, num_el, num):
        self.num_el, self.num = num_el, num
        self.stem = [num_el]
        self.opts: list[Opt] = []
        self.inline = None  # đoạn chứa mọi đáp án trên một dòng
        self.tail: list = []
        self.section = 0


def _is_p(el):
    return el.tag == qn("w:p")


def _inline_markers(text: str):
    ms = list(MARK_RE.finditer(text))
    seq = []
    for m in ms:
        if m.group(1) == chr(65 + len(seq)):
            seq.append(m)
    return seq if len(seq) >= 2 and seq[0].start() <= 3 else []


def _parse(doc):
    body = doc.element.body
    els = [el for el in body.iterchildren() if el.tag != qn("w:sectPr")]
    items: list = []  # ("fixed", [els]) | ("q", Block)
    cur: Block | None = None
    section = 0
    fixed: list = []

    def flush_fixed():
        nonlocal fixed
        if fixed:
            items.append(("fixed", fixed))
            fixed = []

    def finish():
        nonlocal cur
        if cur is None:
            return
        if cur.inline is not None or len(cur.opts) >= 2:
            cur.section = section
            flush_fixed()
            items.append(("q", cur))
        else:  # tự luận / dạng khác: giữ nguyên chỗ
            flush_fixed()
            allel = cur.stem + [e for o in cur.opts for e in o.els] + cur.tail
            items.append(("fixed", allel))
        cur = None

    for el in els:
        if _is_p(el):
            par = Paragraph(el, doc)
            t = _text(par)
            m = Q_RE.match(t)
            if m:
                finish()
                cur = Block(el, int(m.group(1)))
                continue
            if cur is not None:
                inl = _inline_markers(t)
                if cur.inline is None and not cur.tail and inl:
                    cur.inline = el
                    continue
                if OPT_RE.match(t) and cur.inline is None and not cur.tail:
                    cur.opts.append(Opt([el]))
                    continue
                if (cur.opts or cur.inline is not None) and HEAD_RE.match(t) and t.strip():
                    finish()
                    section += 1
                    fixed.append(el)
                    continue
                if cur.opts and t.strip() and not cur.tail:
                    cur.opts[-1].els.append(el)  # dòng tiếp theo của đáp án cuối
                elif cur.opts or cur.inline is not None:
                    cur.tail.append(el)
                else:
                    cur.stem.append(el)
                continue
            if HEAD_RE.match(t) and t.strip():
                section += 1
            fixed.append(el)
        else:  # bảng... đi theo khối đang mở
            if cur is not None:
                (cur.tail if (cur.opts or cur.inline is not None) else cur.stem).append(el)
            else:
                fixed.append(el)
    finish()
    flush_fixed()
    return items


def _manual(text: str | None) -> dict[int, str]:
    return {int(n): a.upper() for n, a in re.findall(r"(\d+)\s*[-:.)]?\s*([A-Fa-f])\b", text or "")}


def _option_ranges_inline(par: Paragraph):
    """Danh sách (start, body_end, seg_end) của từng đáp án trong đoạn có đáp án trên một dòng."""
    t = _text(par)
    ms = _inline_markers(t)
    segs = []
    for i, m in enumerate(ms):
        s = m.start(1)
        e = ms[i + 1].start(1) if i + 1 < len(ms) else len(t)
        body_end = len(t[s:e].rstrip()) + s
        segs.append((s, body_end, e))
    return segs


def _detect_answer(doc, blk: Block):
    """Trả (chỉ số đáp án đúng | None, kiểu đánh dấu | None)."""
    n = len(_option_ranges_inline(Paragraph(blk.inline, doc))) if blk.inline is not None else len(blk.opts)
    flags = []  # mỗi đáp án: tập kiểu đánh dấu
    if blk.inline is not None:
        par = Paragraph(blk.inline, doc)
        for s, be, _ in _option_ranges_inline(par):
            flags.append(_any_marks(par, s, be))
    else:
        for o in blk.opts:
            mk: set[str] = set()
            for el in o.els:
                if _is_p(el):
                    p = Paragraph(el, doc)
                    mk |= _any_marks(p, 0, len(_text(p)))
            flags.append(mk)
    for k in KINDS:
        hit = [i for i, f in enumerate(flags) if k in f]
        if len(hit) == 1 and n > 1:
            return hit[0], k
    return None, None


def _opt_text(doc, blk: Block, i: int) -> str:
    if blk.inline is not None:
        par = Paragraph(blk.inline, doc)
        s, be, _ = _option_ranges_inline(par)[i]
        return _text(par)[s:be]
    return " ".join(_text(Paragraph(e, doc)) for e in blk.opts[i].els if _is_p(e))


# ---------- áp dụng xáo trộn ----------
def _shuffle_order(rng, fixed_flags: list[bool]) -> list[int]:
    mov = [i for i, f in enumerate(fixed_flags) if not f]
    fix = [i for i, f in enumerate(fixed_flags) if f]
    for _ in range(12):
        m = mov[:]
        rng.shuffle(m)
        if m != mov or len(mov) < 2:
            break
    return m + fix


def _apply_options(doc, blk: Block, rng, strip: bool, kind: str | None, ans_idx: int | None):
    """Xáo đáp án của một khối; trả chữ cái đáp án đúng mới (hoặc '?')."""
    if blk.inline is not None:
        par = Paragraph(blk.inline, doc)
        runs = _runs(par)
        segs = _option_ranges_inline(par)
        texts = [_text(par)[s:be] for s, be, _ in segs]
        fixed = [bool(FIXED_OPT_RE.search(x)) for x in texts]
        order = _shuffle_order(rng, fixed)
        spans, off = [], 0
        for r in runs:
            spans.append((r, off, off + len(r.text)))
            off += len(r.text)

        def pieces(s, e):
            out = []
            for r, a, b in spans:
                lo, hi = max(s, a), min(e, b)
                if lo < hi:
                    out.append((r._r, r.text[lo - a:hi - a]))
            return out

        new_runs = []
        new_letter = "?"
        for k, j in enumerate(order):
            s, be, _ = segs[j]
            ps = pieces(s, be)
            if ps:
                ps[0] = (ps[0][0], chr(65 + k) + ps[0][1][1:])
            for src, txt in ps:
                new_runs.append((_clone_run(src, par, txt), j == ans_idx))
            sep_s, sep_e = segs[k][1], segs[k][2]
            for src, txt in pieces(sep_s, sep_e):
                new_runs.append((_clone_run(src, par, txt), False))
            if j == ans_idx:
                new_letter = chr(65 + k)
        for r in runs:
            par._p.remove(r._r)
        for el, is_ans in new_runs:
            par._p.append(el)
            if is_ans and strip and kind:
                _strip_marks_run(Run(el, par), {kind})
        return new_letter
    texts = [_opt_text(doc, blk, i) for i in range(len(blk.opts))]
    # bỏ nhãn "A." khi xét đáp án cố định
    fixed = [bool(FIXED_OPT_RE.search(OPT_RE.sub("", x, 1))) for x in texts]
    order = _shuffle_order(rng, fixed)
    new_opts, new_letter = [], "?"
    for k, j in enumerate(order):
        o = blk.opts[j]
        first = Paragraph(o.els[0], doc)
        t = _text(first)
        m = OPT_RE.match(t)
        if m:
            _replace_range(first, m.start(1), m.end(1), chr(65 + k))
        if j == ans_idx:
            new_letter = chr(65 + k)
            if strip and kind:
                for el in o.els:
                    if _is_p(el):
                        _strip_marks(Paragraph(el, doc), {kind})
        new_opts.append(o)
    blk.opts = new_opts
    return new_letter


def _strip_marks_run(r: Run, kinds: set[str]) -> None:
    m = _marks(r) & kinds
    if "u" in m:
        r.font.underline = False
    if "hl" in m:
        r.font.highlight_color = None
    if "red" in m:
        r.font.color.rgb = None
    if "b" in m:
        r.font.bold = False


def _all_paragraphs(doc):
    def walk(container):
        for p in container.paragraphs:
            yield p
        for t in getattr(container, "tables", []):
            for row in t.rows:
                for cell in row.cells:
                    yield from walk(cell)
    yield from walk(doc)
    for sec in doc.sections:
        for part in (sec.header, sec.footer, sec.first_page_header, sec.first_page_footer, sec.even_page_header, sec.even_page_footer):
            try:
                yield from walk(part)
            except (AttributeError, KeyError):
                continue


def _set_code(doc, code: str) -> bool:
    done = False
    for p in _all_paragraphs(doc):
        t = _text(p)
        m = CODE_RE.search(t)
        if m:
            _replace_range(p, m.start(2), m.end(2), code)
            done = True
    if not done:
        first = doc.paragraphs[0] if doc.paragraphs else None
        newp = doc.add_paragraph()
        r = newp.add_run(f"Mã đề: {code}")
        r.bold = True
        r.font.size = Pt(13)
        newp.alignment = 2  # phải
        if first is not None:
            first._p.addprevious(newp._p)
    return done


def build_versions(src: Path, outdir: Path, versions: int = 4, start_code: int = 101, keep_order: bool = False,
                   strip_marks: bool = True, manual_answers: str | None = None, seed: int | None = None) -> dict:
    src, outdir = Path(src), Path(outdir)
    if src.suffix.lower() != ".docx":
        raise ExamError("Chỉ hỗ trợ file Word .docx (không phải .doc hay PDF). Hãy lưu lại thành .docx rồi thử lại.")
    versions = max(1, min(int(versions), 20))
    manual = _manual(manual_answers)
    outdir.mkdir(parents=True, exist_ok=True)
    base_seed = seed if seed is not None else (src.stat().st_size * 31 + int(start_code))
    warnings: list[str] = []
    keys: list[dict] = []
    codes: list[str] = []
    files: list[Path] = []
    summary: dict = {}
    seen_orders: set[tuple] = set()
    for vi in range(versions):
        doc = Document(str(src))
        items = _parse(doc)
        mcq = [(idx, b) for idx, (k, b) in enumerate(items) if k == "q"]
        if not mcq:
            raise ExamError("Không tìm thấy câu trắc nghiệm nào. Đề cần có dạng 'Câu 1. …' và các đáp án A. B. C. D. (mỗi đáp án một dòng hoặc cùng một dòng).")
        answers: dict[int, tuple[int | None, str | None]] = {}
        for _, b in mcq:
            ai, kind = _detect_answer(doc, b)
            if b.num in manual:
                n = len(_option_ranges_inline(Paragraph(b.inline, doc))) if b.inline is not None else len(b.opts)
                ai, kind = (ord(manual[b.num]) - 65 if 0 <= ord(manual[b.num]) - 65 < n else None), None
            answers[id(b)] = (ai, kind)
        rng = random.Random(base_seed + vi * 7919)
        # 1) đổi chỗ các câu trong cùng phần
        slots_by_section: dict[int, list[int]] = {}
        for idx, b in mcq:
            slots_by_section.setdefault(b.section, []).append(idx)
        slot_nums = {idx: b.num for idx, b in mcq}
        for _ in range(30):
            order_map = {}
            for sec, idxs in slots_by_section.items():
                blocks = [items[i][1] for i in idxs]
                perm = blocks[:]
                if not keep_order:
                    rng.shuffle(perm)
                order_map.update({i: b for i, b in zip(idxs, perm)})
            sig = tuple(id(order_map[i]) for i in sorted(order_map))
            same_as_original = all(order_map[i] is items[i][1] for i in order_map) and len(order_map) > 1
            if keep_order or (sig not in seen_orders and not same_as_original) or len(order_map) < 3:
                seen_orders.add(sig)
                break
        for i, b in order_map.items():
            items[i] = ("q", b)
        # 2) đổi số câu, xáo đáp án
        key: dict[int, str] = {}
        for idx, b in [(i, items[i][1]) for i in sorted(order_map)]:
            slot = slot_nums[idx]
            ai, kind = answers[id(b)]
            par = Paragraph(b.num_el, doc)
            m = Q_RE.match(_text(par))
            if m:
                _replace_range(par, m.start(1), m.end(1), str(slot))
            letter = _apply_options(doc, b, rng, strip_marks, kind, ai)
            key[slot] = letter
        # 3) lắp lại thân tài liệu
        body = doc.element.body
        sect = body.find(qn("w:sectPr"))
        flat = []
        for kind_, val in items:
            if kind_ == "fixed":
                flat.extend(val)
            else:
                flat.extend(val.stem)
                if val.inline is not None:
                    flat.append(val.inline)
                for o in val.opts:
                    flat.extend(o.els)
                flat.extend(val.tail)
        for ch in list(body):
            body.remove(ch)
        for el in flat:
            body.append(el)
        if sect is not None:
            body.append(sect)
        code = str(int(start_code) + vi)
        had_code = _set_code(doc, code)
        out = outdir / f"{src.stem}-ma-{code}.docx"
        doc.save(str(out))
        files.append(out)
        codes.append(code)
        keys.append(key)
        if vi == 0:
            unknown = sorted(n for n, l in key.items() if l == "?")
            nonmcq = sum(1 for k, v in items if k == "fixed" and any(_is_p(e) and Q_RE.match(_text(Paragraph(e, doc))) for e in v))
            summary = {"questions": len(mcq) + nonmcq, "mcq": len(mcq), "sections": len(slots_by_section), "fixed": nonmcq}
            if unknown:
                warnings.append(f"Không xác định được đáp án đúng của câu {', '.join(map(str, unknown[:15]))}{'…' if len(unknown) > 15 else ''} (đề gốc không đánh dấu). Ô đáp án ghi dấu '?'. Hãy nhập 'Đáp án thủ công' (vd: 1A 2C 3B) rồi xáo lại.")
            if nonmcq:
                warnings.append(f"{nonmcq} câu không phải trắc nghiệm A/B/C/D (tự luận, đúng/sai…) được giữ nguyên vị trí, không xáo.")
            if not had_code:
                warnings.append("Đề gốc chưa có dòng 'Mã đề', đã thêm 'Mã đề: …' ở đầu trang.")
    # bảng đáp án
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font
    nums = sorted({n for k in keys for n in k})
    multi_sec = len(nums) != len({n for n in nums})
    wb = Workbook()
    ws = wb.active
    ws.title = "Đáp án"
    ws.append(["Câu", *[f"Mã đề {c}" for c in codes]])
    for n in nums:
        ws.append([n, *[k.get(n, "") for k in keys]])
    for c in ws[1]:
        c.font = Font(bold=True)
        c.alignment = Alignment(horizontal="center")
    ws.column_dimensions["A"].width = 8
    for col in "BCDEFGHIJKLMNOPQRSTUV"[:len(codes)]:
        ws.column_dimensions[col].width = 12
    key_path = outdir / f"{src.stem}-dap-an.xlsx"
    wb.save(key_path)
    return {"summary": summary, "files": files, "answer_key": key_path, "warnings": warnings, "codes": codes, "keys": keys}
