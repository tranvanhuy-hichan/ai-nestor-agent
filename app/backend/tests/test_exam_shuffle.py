import re
import zipfile

import pytest
from fastapi.testclient import TestClient
from docx import Document
from docx.enum.text import WD_COLOR_INDEX
from docx.shared import Pt, RGBColor

from argus.main import app
from argus.services import exam_shuffle as ex

# (câu hỏi, [đáp án], chỉ số đúng, kiểu: sep = mỗi đáp án một dòng | inline = một dòng)
QS = [
    ("Thủ đô của Việt Nam là gì?", ["Hà Nội", "Huế", "Đà Nẵng", "Cần Thơ"], 0, "sep"),
    ("2 + 3 bằng bao nhiêu?", ["4", "5", "6", "7"], 1, "sep"),
    ("Nước sôi ở bao nhiêu độ C?", ["50", "80", "100", "120"], 2, "sep"),
    ("Sông dài nhất Việt Nam?", ["Sông Hồng", "Sông Mê Kông", "Sông Cả", "Sông Đà"], 1, "sep"),
    ("Số nguyên tố nhỏ nhất là?", ["0", "1", "2", "3"], 2, "inline"),
    ("Hành tinh gần Mặt Trời nhất?", ["Sao Thủy", "Sao Kim", "Trái Đất", "Sao Hỏa"], 0, "inline"),
    ("Chọn phát biểu đúng về nước.", ["Nước sôi ở 100 độ C", "Nước đóng băng ở 0 độ C", "Cả A và B đều đúng"], 2, "sep"),
    ("Kim loại nào lỏng ở nhiệt độ thường?", ["Sắt", "Thủy ngân", "Đồng", "Nhôm"], 1, "inline"),
]


def make_exam(path, mark="u"):
    d = Document()
    d.styles["Normal"].font.name = "Times New Roman"
    d.sections[0].header.paragraphs[0].text = "ĐỀ KIỂM TRA     Mã đề: 000"
    d.add_paragraph("PHẦN I. TRẮC NGHIỆM")
    n = 0
    for qi, (q, opts, ans, style) in enumerate(QS):
        if qi == 4:
            d.add_paragraph("PHẦN II. TIẾP TỤC")
        n += 1
        qp = d.add_paragraph()
        qp.add_run(f"Câu {n}. ").bold = True
        qp.add_run(q)

        def mk(run):
            if mark == "u":
                run.underline = True
            elif mark == "red":
                run.font.color.rgb = RGBColor(0xFF, 0, 0)
            elif mark == "hl":
                run.font.highlight_color = WD_COLOR_INDEX.YELLOW
        if style == "sep":
            for i, o in enumerate(opts):
                p = d.add_paragraph()
                r1 = p.add_run(f"{chr(65 + i)}. ")
                r2 = p.add_run(o)
                r2.font.size = Pt(12)
                if i == ans:
                    mk(r1)
        else:
            p = d.add_paragraph()
            for i, o in enumerate(opts):
                r1 = p.add_run(f"{chr(65 + i)}. ")
                r2 = p.add_run(o + ("\t" if i < len(opts) - 1 else ""))
                if i == ans:
                    mk(r1)
    n += 1
    d.add_paragraph(f"Câu {n}. Em hãy trình bày cảm nhận về mùa xuân. (tự luận)")
    d.save(path)


def read(path):
    d = Document(path)
    return [p.text for p in d.paragraphs], d


@pytest.mark.parametrize("mark", ["u", "red", "hl"])
def test_shuffle_preserves_content_numbers_and_answers(tmp_path, mark):
    src = tmp_path / "de.docx"
    make_exam(src, mark)
    res = ex.build_versions(src, tmp_path / "out", versions=3, start_code=101)
    assert len(res["files"]) == 3 and res["codes"] == ["101", "102", "103"]
    assert res["summary"]["mcq"] == len(QS) and res["summary"]["fixed"] == 1
    orig = {q: (opts, opts[a]) for q, opts, a, _ in QS}
    seen_orders = set()
    for f, key in zip(res["files"], res["keys"]):
        lines, d = read(f)
        assert "Mã đề: 101" in d.sections[0].header.paragraphs[0].text or "Mã đề: 10" in d.sections[0].header.paragraphs[0].text
        # số câu đánh lại tuần tự, mọi câu hỏi còn đủ
        nums = [int(m.group(1)) for t in lines if (m := re.match(r"Câu (\d+)\.", t))]
        assert nums == list(range(1, len(QS) + 2))
        order = []
        for i, t in enumerate(lines):
            m = re.match(r"Câu (\d+)\. (.*)", t)
            if not m or m.group(2) not in orig:
                continue
            q = m.group(2)
            order.append(q)
            opts_all, right = orig[q]
            got = {}
            j = i + 1
            if "\t" in lines[j]:  # đáp án trên một dòng, phân tách bằng tab
                for part in re.split(r"\t", lines[j]):
                    got[part[0]] = part[3:].strip()
            else:
                for k in range(len(opts_all)):
                    got[lines[j + k][0]] = lines[j + k][3:].strip()
            assert sorted(got.values()) == sorted(opts_all), (q, got)
            assert sorted(got) == [chr(65 + k) for k in range(len(opts_all))]
            slot = int(m.group(1))
            assert got[key[slot]] == right, (q, key[slot], got)
            if "Cả A và B" in "".join(opts_all):
                assert got[chr(65 + len(opts_all) - 1)].startswith("Cả A và B")  # đáp án 'cả A và B' luôn ở cuối
        seen_orders.add(tuple(order))
        # dấu đánh dấu đáp án bị xóa khỏi đề phát cho học sinh
        for p in d.paragraphs:
            if re.match(r"[A-D]\. ", p.text) or "\t" in p.text:
                for r in p.runs:
                    assert not r.font.underline and r.font.highlight_color is None
                    assert r.font.color.rgb != RGBColor(0xFF, 0, 0) if r.font.color and r.font.color.type else True
        # câu tự luận giữ nguyên ở cuối, tiêu đề phần giữ nguyên chỗ
        assert lines[-1].startswith(f"Câu {len(QS) + 1}.") and "PHẦN I." in "\n".join(lines) and "PHẦN II." in "\n".join(lines)
    assert len(seen_orders) == 3  # các mã đề khác nhau
    assert zipfile.is_zipfile(res["answer_key"])


def test_questions_stay_within_their_section(tmp_path):
    src = tmp_path / "de.docx"
    make_exam(src)
    res = ex.build_versions(src, tmp_path / "o", versions=2)
    first_half = {q for q, *_ in QS[:4]}
    for f in res["files"]:
        lines, _ = read(f)
        p2 = next(i for i, t in enumerate(lines) if "PHẦN II" in t)
        before = {m.group(1) for t in lines[:p2] if (m := re.match(r"Câu \d+\. (.*)", t))}
        assert before == first_half


def test_keep_order_only_shuffles_options(tmp_path):
    src = tmp_path / "de.docx"
    make_exam(src)
    res = ex.build_versions(src, tmp_path / "o", versions=2, keep_order=True)
    for f in res["files"]:
        lines, _ = read(f)
        qs = [m.group(1) for t in lines if (m := re.match(r"Câu \d+\. (.*)", t))]
        assert qs[:len(QS)] == [q for q, *_ in QS]


def test_manual_answers_and_unmarked_exam(tmp_path):
    src = tmp_path / "de.docx"
    make_exam(src, mark="none")
    res = ex.build_versions(src, tmp_path / "o", versions=2)
    assert any("Không xác định được đáp án" in w for w in res["warnings"])
    manual = " ".join(f"{i + 1}{chr(65 + a)}" for i, (_, _, a, _) in enumerate(QS))
    res = ex.build_versions(src, tmp_path / "o2", versions=2, manual_answers=manual)
    assert not any("Không xác định" in w for w in res["warnings"])
    assert all("?" not in k.values() for k in res["keys"])


def test_rejects_non_docx_and_empty(tmp_path):
    (tmp_path / "x.pdf").write_bytes(b"%PDF")
    with pytest.raises(ex.ExamError):
        ex.build_versions(tmp_path / "x.pdf", tmp_path / "o")
    d = Document()
    d.add_paragraph("Chỉ là văn bản thường.")
    d.save(tmp_path / "e.docx")
    with pytest.raises(ex.ExamError):
        ex.build_versions(tmp_path / "e.docx", tmp_path / "o")


@pytest.fixture
def client(tmp_env):
    return TestClient(app, headers={"host": "localhost"})


def test_shuffle_exam_tool_and_api(tmp_env, client):
    from argus.services import tools
    from argus.services.tools import ToolContext
    ws = tmp_env
    make_exam(ws / "de.docx")
    out, ok = tools.call(ToolContext(workspace=ws, full_access=True), "shuffle_exam", {"path": "de.docx", "so_ma_de": 3})
    assert ok and "3 mã đề" in out and (ws / "de-xao-tron" / "de-ma-101.docx").exists(), out
    with open(ws / "de.docx", "rb") as f:
        r = client.post("/api/exam/shuffle", files={"file": ("de thi.docx", f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}, data={"versions": "2", "start_code": "301"})
    assert r.status_code == 200, r.text
    j = r.json()
    assert len(j["files"]) == 2 and j["answer_key"]["name"].endswith("dap-an.xlsx") and j["summary"]["mcq"] == len(QS)
    for e in [*j["files"], j["answer_key"], j["zip"]]:
        g = client.get(e["url"])
        assert g.status_code == 200 and len(g.content) == e["size"]
    assert client.get(f"/api/exam/{j['id']}/file/..%2Fx").status_code in (404, 400)
    bad = client.post("/api/exam/shuffle", files={"file": ("x.pdf", b"%PDF", "application/pdf")})
    assert bad.status_code == 400 and "docx" in bad.json()["detail"].lower()
    empty = client.post("/api/exam/shuffle", files={"file": ("e.docx", open(ws / "de.docx", "rb").read()[:100], "application/octet-stream")})
    assert empty.status_code == 400
