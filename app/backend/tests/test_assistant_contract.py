"""Hop dong cua tro ly chuyen trach + kiem tra noi day (provider gia theo kich ban).

Luu y trung thuc: cac test kich ban chi chung minh DAY NOI dung (skill + cong chat luong nam trong system prompt, allowlist tool duoc ep,
tro ly luu theo phien, tool tao file chay duoc). Chung KHONG do chat luong tra loi cua mo hinh that.
"""
import json
import uuid

import pytest
from fastapi.testclient import TestClient

from nestor.core import config as cfgmod
from nestor.services import agent as agent_mod
from nestor.services import assistants, sessions, skills as skillmod, tools, workfiles

CONTENT = assistants._load_content()
MIN_SKILL = 800


def known():
    cfg = cfgmod.load()
    return set(tools.TOOLS), skillmod.discover(cfg)


def _need_content():
    if not CONTENT:
        pytest.skip("chua co assistant_defs/*.py (cac fork noi dung chua ghi)")


def test_no_load_errors():
    assert not assistants.LOAD_ERRORS, assistants.LOAD_ERRORS


def test_ids_unique():
    ids = [a["id"] for a in assistants.BUILTIN]
    assert len(ids) == len(set(ids))


@pytest.mark.parametrize("d", CONTENT or [None], ids=lambda d: d["id"] if d else "none")
def test_def_contract(tmp_env, d):
    _need_content()
    tool_names, skills = known()
    errs = assistants.validate_def(d, tool_names, set(skills))
    assert not errs, errs
    assert d["skills"], f"{d['id']}: moi tro ly noi dung can it nhat 1 skill di kem"
    for name in d["skills"]:
        sk = skills[name]
        assert sk.bundled, f"{name} phai la skill di kem"
        text = sk.body
        assert len(text) >= MIN_SKILL, f"{name}: SKILL.md qua ngan ({len(text)})"
        low = text.lower()
        assert "quy trình" in low, f"{name}: thieu muc quy trinh"
        assert "hỏi lại" in low or "câu hỏi" in low, f"{name}: thieu cau hoi can hoi lai"
        assert "kiểm tra" in low or "tự kiểm" in low or "checklist" in low, f"{name}: thieu muc kiem tra"
    if d["id"] == "van-thu-nd30" and d["tools"] is not None:
        assert {"vanban_types", "vanban_write_docx", "review_vn_document"} <= set(d["tools"])


def test_validate_def_catches_problems(tmp_env):
    bad = {"id": "x", "name": "n", "icon": "bot", "group": "zzz", "description": "d", "prompt": "p", "starters": ["a"], "done_criteria": ["a"],
           "skills": ["khong-co"], "tools": ["khong-co-tool"], "deliverables": ["xlsx"]}
    errs = " | ".join(assistants.validate_def(bad, set(tools.TOOLS), set()))
    for frag in ("group", "starters", "done_criteria", "skill 'khong-co'", "tool 'khong-co-tool'", "allowlist"):
        assert frag in errs


# ---------------- noi day voi provider gia
class Fake:
    def __init__(self, rule):
        self.rule = rule

    def stream(self, messages, tool_defs, effort=None):
        out = self.rule(messages, [t["name"] for t in tool_defs])
        if out.get("content"):
            yield {"type": "delta", "text": out["content"]}
        yield {"type": "final", "content": out.get("content", ""), "tool_calls": out.get("calls", []), "usage": {"prompt": 1, "completion": 1}}


def call(name, **args):
    return {"id": "c" + uuid.uuid4().hex[:6], "name": name, "args": args}


@pytest.fixture
def llm(tmp_env, monkeypatch):
    def install(rule):
        monkeypatch.setattr(agent_mod, "make_provider", lambda cfg: Fake(rule))
    return install


def run_assistant(aid, text, llm, rule):
    """Chay mot luot nhu API: system_extra + allowlist lay tu tro ly."""
    seen = {"system": [], "tools": [], "results": []}

    def wrapped(messages, names):
        seen["system"].append(messages[0]["content"])
        seen["tools"].append(names)
        seen["results"] += [m["content"] for m in messages if m["role"] == "tool"]
        return rule(messages, names)

    llm(wrapped)
    sid = sessions.create(text)
    agent_mod.run_turn(sid, text, None, lambda k, d: True, lambda ev: None, system_extra=assistants.prompt_for(aid), tool_allow=assistants.tool_allow(aid))
    return sid, seen


def need(aid):
    if not assistants.get(aid):
        pytest.skip(f"chua co tro ly {aid}")


def ntools(messages):
    return sum(m["role"] == "tool" for m in messages)


def test_van_thu_creates_nd30_docx(llm):
    need("van-thu-nd30")
    from test_office import to_trinh_paragraphs

    def rule(messages, names):
        n = ntools(messages)
        if n == 0:
            return {"calls": [call("vanban_types", document_type_key="TO_TRINH")]}
        if n == 1:
            return {"calls": [call("vanban_write_docx", path="to-trinh", document_type_key="TO_TRINH", paragraphs=json.dumps(to_trinh_paragraphs()), ngan_theo_yeu_cau=True)]}
        if n == 2:
            return {"calls": [call("review_vn_document", path="to-trinh.docx")]}
        return {"content": "1. ✓ đúng thể thức\nFile: to-trinh.docx"}

    sid, seen = run_assistant("van-thu-nd30", "Soạn tờ trình xin kinh phí", llm, rule)
    f = workfiles.workdir_for(cfgmod.load(), sid) / "to-trinh.docx"
    assert f.exists()
    assert "CỔNG CHẤT LƯỢNG" in seen["system"][0] and "✓" in seen["system"][0]
    assert any("[OK] Quốc hiệu" in r for r in seen["results"]), seen["results"]
    if assistants.get("van-thu-nd30")["skills"]:
        assert "Kỹ năng nghiệp vụ BẮT BUỘC" in seen["system"][0]


def test_ke_toan_creates_xlsx_with_formulas(llm):
    need("ke-toan")
    sheets = {"Công nợ": [["Khách", "Số tiền"], ["A", 100], ["B", 250], ["Tổng", "=SUM(B2:B3)"]]}

    def rule(messages, names):
        if ntools(messages) == 0:
            return {"calls": [call("create_xlsx", path="cong-no", sheets=json.dumps(sheets))]}
        return {"content": "✓ có công thức tổng"}

    sid, seen = run_assistant("ke-toan", "Lập bảng công nợ", llm, rule)
    from openpyxl import load_workbook
    assert load_workbook(workfiles.workdir_for(cfgmod.load(), sid) / "cong-no.xlsx")["Công nợ"]["B4"].value == "=SUM(B2:B3)"
    assert "CỔNG CHẤT LƯỢNG" in seen["system"][0]


def test_giao_an_creates_docx_or_pptx(llm):
    need("giao-an")
    a = assistants.get("giao-an")
    allow = assistants.tool_allow("giao-an")

    def rule(messages, names):
        if ntools(messages) == 0:
            if "create_docx" in names:
                return {"calls": [call("create_docx", path="giao-an", content="# Giáo án\n## Mục tiêu\n- Hiểu tỉ lệ thức")]}
            return {"calls": [call("create_pptx", path="bai-giang", slides=json.dumps([{"title": "Bài giảng"}]))]}
        return {"content": "✓ đã tạo file"}

    sid, seen = run_assistant("giao-an", "Soạn giáo án Toán 7", llm, rule)
    d = workfiles.workdir_for(cfgmod.load(), sid)
    assert (d / "giao-an.docx").exists() or (d / "bai-giang.pptx").exists()
    assert "CỔNG CHẤT LƯỢNG" in seen["system"][0]
    assert allow is None or {"create_docx", "create_pptx"} & set(allow)
    assert a["deliverables"]


def test_gia_su_answers_without_file(llm):
    need("gia-su")

    def rule(messages, names):
        return {"content": "Bước 1: ... ✓ Em đã hiểu chưa?"}

    sid, seen = run_assistant("gia-su", "Giải thích định lý Pi-ta-go", llm, rule)
    d = workfiles.workdir_for(cfgmod.load(), sid)
    assert not [p for p in d.glob("*.*") if p.suffix in (".docx", ".xlsx", ".pptx")]
    assert "CỔNG CHẤT LƯỢNG" in seen["system"][0]
    assert sessions.messages(sid)[-1]["content"].startswith("Bước 1")


def test_skill_text_is_inlined_for_content_assistants(tmp_env):
    _need_content()
    for d in CONTENT:
        if d["skills"]:
            p = assistants.prompt_for(d["id"])
            sk = known()[1][d["skills"][0]]
            assert sk.body[:200].strip() in p or sk.instructions()[:200].strip() in p, d["id"]
            assert len(p) <= assistants.SKILL_BUDGET + 6000


def test_allowlist_is_enforced(llm):
    assistants.save("chi-doc", {"name": "Chỉ đọc", "prompt": "Chỉ đọc file.", "tools": ["read"], "starters": [], "done_criteria": ["a", "b", "c"]}, True)
    allow = set(assistants.tool_allow("chi-doc"))
    assert "read" in allow and "ask_user" in allow and "create_docx" not in allow

    def rule(messages, names):
        if ntools(messages) == 0:
            return {"calls": [call("create_docx", path="x", content="a")]}
        return {"content": "xong"}

    sid, seen = run_assistant("chi-doc", "tạo file", llm, rule)
    assert set(seen["tools"][0]) <= allow | {"plan_submit"}
    assert "create_docx" not in seen["tools"][0]
    assert any("khong co tool create_docx" in r for r in seen["results"])
    assert not (workfiles.workdir_for(cfgmod.load(), sid) / "x.docx").exists()


def test_no_allowlist_means_all_tools(tmp_env):
    assert assistants.tool_allow(None) is None and assistants.tool_allow("khong-co") is None
    allow = assistants.tool_allow("ke-toan")
    assert allow is None or "create_xlsx" in allow


# ---------------- luu tro ly theo phien (API)
def read_stream(resp):
    return [json.loads(line[6:]) for line in resp.text.splitlines() if line.startswith("data: ")]


def test_assistant_persists_per_session(llm):
    need("ke-toan")
    seen = []
    llm(lambda m, t: seen.append(m[0]["content"]) or {"content": "ok"})
    c = TestClient(__import__("nestor.main", fromlist=["app"]).app)
    evs = read_stream(c.post("/api/chat", json={"text": "chào", "assistant": "ke-toan"}))
    sid = next(e["id"] for e in evs if e["type"] == "session")
    assert c.get(f"/api/sessions/{sid}").json()["assistant"] == "ke-toan"
    assert next(s for s in c.get("/api/sessions").json() if s["id"] == sid)["assistant"] == "ke-toan"
    assert "CỔNG CHẤT LƯỢNG" in seen[-1]
    # khong gui assistant -> dung ban da luu
    read_stream(c.post("/api/chat", json={"text": "tiếp", "session": sid}))
    assert "CỔNG CHẤT LƯỢNG" in seen[-1] and "kế toán" in seen[-1].lower()
    # bo chon tren may chu
    assert c.put(f"/api/sessions/{sid}/assistant", json={"assistant": ""}).status_code == 200
    assert c.get(f"/api/sessions/{sid}").json()["assistant"] == ""
    read_stream(c.post("/api/chat", json={"text": "nữa", "session": sid}))
    assert "CỔNG CHẤT LƯỢNG" not in seen[-1]
    assert c.put(f"/api/sessions/{sid}/assistant", json={"assistant": "khong-co"}).status_code == 400
    assert c.put("/api/sessions/zzzz/assistant", json={"assistant": ""}).status_code == 404
    # gui '' cung bo chon, gui id thi chon lai
    read_stream(c.post("/api/chat", json={"text": "x", "session": sid, "assistant": "ke-toan"}))
    assert c.get(f"/api/sessions/{sid}").json()["assistant"] == "ke-toan"
    read_stream(c.post("/api/chat", json={"text": "y", "session": sid, "assistant": ""}))
    assert c.get(f"/api/sessions/{sid}").json()["assistant"] == ""


def test_old_database_gets_assistant_column(tmp_env):
    from nestor.core import db as dbmod
    with dbmod.db() as c:
        cols = [r["name"] for r in c.execute("PRAGMA table_info(sessions)")]
    assert "assistant" in cols


def test_bundled_skills_are_advertised_compactly_for_auto_selection(tmp_env):
    cfg = cfgmod.load()
    sk = skillmod.discover(cfg)
    block = skillmod.prompt_block(sk)
    bundled = [n for n, s in sk.items() if s.bundled]
    assert bundled and all(f"<name>{n}</name>" in block for n in bundled), "model phai thay moi skill di kem de tu chon"
    assert "skills_read" in block and "khong can nguoi dung chon skill" in block
    assert len(block) < 15000  # rut gon: khong lam phinh prompt chung
    # model goi skills_read doc duoc skill di kem
    from nestor.services import tools
    from nestor.services.tools import ToolContext
    out, ok = tools.call(ToolContext(workspace=cfg.workspace_path(), skills=sk), "skills_read", {"name": "van-thu-nd30"})
    assert ok and "vanban_write_docx" in out


def test_workspace_skill_overrides_bundled(tmp_env):
    cfg = cfgmod.load()
    bundled = [n for n, s in skillmod.discover(cfg).items() if s.bundled]
    if not bundled:
        pytest.skip("chua co skill di kem")
    n = bundled[0]
    skillmod.create(cfg, n, "ban cua workspace", "NOI DUNG RIENG CUA WORKSPACE " * 5)
    s = skillmod.discover(cfg)[n]
    assert not s.bundled and "RIENG CUA WORKSPACE" in s.body


# ---- form chuc nang (moi tro ly mot trang rieng) ----
from nestor.assistant_defs import forms as formsmod  # noqa: E402


@pytest.mark.parametrize("d", assistants.BUILTIN, ids=lambda d: d["id"])
def test_every_assistant_has_business_workflow(d):
    """Moi chuc nang co quy trinh nghiep vu that: >=1 quy trinh co tu 3 buoc, moi buoc co muc tieu va tieu chi duyet."""
    form = d.get("form")
    assert form and form["flows"], f"{d['id']}: thieu quy trinh"
    errs = formsmod.validate_form(d["id"], form)
    assert not errs, errs
    assert max(len(fl["steps"]) for fl in form["flows"]) >= 3, f"{d['id']}: can it nhat mot quy trinh tu 3 buoc"
    for fl in form["flows"]:
        for st in fl["steps"]:
            assert len(st["review"]) >= 2, f"{d['id']}/{fl['id']}/{st['id']}: can >=2 tieu chi duyet"
            assert len(st["task"]) >= 40, f"{d['id']}/{fl['id']}/{st['id']}: task qua so sai"


@pytest.mark.parametrize("d", assistants.BUILTIN, ids=lambda d: d["id"])
def test_workflow_mentions_only_real_tools_and_files(d):
    """Buoc co san pham file thi tro ly phai co tool tao file tuong ung."""
    allow = assistants.tool_allow(d["id"])
    if allow is None:
        return
    need = {"docx": ("create_docx", "vanban_write_docx", "docx_fill_template", "shuffle_exam"), "xlsx": ("create_xlsx", "grade_summary", "shuffle_exam", "run_script"), "pptx": ("create_pptx",), "pdf": ("create_cv", "convert_to_pdf"), "html": ("create_cv",)}
    for fl in d["form"]["flows"]:
        for st in fl["steps"]:
            for kind in st["produces"]:
                assert kind in need, f"{d['id']}/{st['id']}: produces '{kind}' khong hop le (docx|xlsx|pptx|pdf|html)"
                assert any(t in allow for t in need[kind]), f"{d['id']}/{st['id']}: tao .{kind} nhung allowlist khong co tool"


def test_forms_reference_only_existing_assistants():
    ids = {a["id"] for a in assistants.BUILTIN}
    assert set(formsmod.FORMS) <= ids, set(formsmod.FORMS) - ids


def test_exam_shuffle_lives_inside_exam_feature():
    ids = {a["id"] for a in assistants.BUILTIN}
    assert "xao-de-thi" not in ids  # khong con chuc nang rieng
    a = assistants.get("ra-de-cham-bai")
    assert "exam-shuffle" in a["form"]["panels"]
    assert "xao-de-thi" in a["skills"] and "shuffle_exam" in a["tools"]


def test_list_all_adds_default_form_to_custom_assistant(tmp_env):
    assistants.save("tu-tao", {"name": "Tự tạo", "prompt": "p"}, True)
    got = assistants.get("tu-tao")
    assert got["form"]["flows"], got


def test_vanban_write_docx_rejects_skeleton_but_accepts_full_draft(tmp_path):
    from nestor.services import tools_office as T
    short = [{"role": "body", "text": "Nâng cấp quốc lộ để đảm bảo an toàn giao thông."}]
    with pytest.raises(ValueError, match="quá ngắn"):
        T._check_depth(short, "TO_TRINH")
    full = [{"role": "body", "text": " ".join(["Nội dung chi tiết có lập luận và số liệu cụ thể."] * 70)}]
    T._check_depth(full, "TO_TRINH")  # khong nem loi
    T._check_depth(short, "GIAY_MOI")  # loai ngan: khong kiem
    many = full + [{"role": "body", "text": "Tổng mức 100 tỷ (dự kiến, cần xác nhận)."}] * 8
    with pytest.raises(ValueError, match="cần xác nhận"):
        T._check_depth(many, "TO_TRINH")


def test_van_thu_cannot_use_create_docx():
    assert "create_docx" not in assistants.tool_allow("van-thu-nd30") and "vanban_write_docx" in assistants.tool_allow("van-thu-nd30")


def test_create_docx_blocks_titlecase_admin_documents(tmp_path):
    from nestor.services import tools_office as T
    assert T._looks_administrative("Tờ trình đề nghị phê duyệt chủ trương\nKính gửi: Bộ Giao thông Vận tải")


def test_vanban_normalizes_header_and_footer_into_two_columns():
    from nestor.services import tools_office as T
    flat = [{"role": r, "text": r} for r in ("national_name", "motto", "issuing_org", "document_number", "place_date")]
    flat += [{"role": "document_type_title", "text": "TỜ TRÌNH"}, {"role": "body", "text": "Nội dung"},
             {"role": "recipients_label", "text": "Nơi nhận:"}, {"role": "recipients_item", "text": "- Như trên;"},
             {"role": "signature_authority", "text": "TM."}, {"role": "signature_name", "text": "…"}]
    out, notes = T._normalize_layout(flat, "TO_TRINH")
    assert len(notes) == 2 and out[0]["layout"] == "two_columns" and out[-1]["layout"] == "two_columns"
    assert [l["role"] for l in out[0]["left_lines"]] == ["issuing_org", "document_number"]
    assert [l["role"] for l in out[0]["right_lines"]] == ["national_name", "motto", "place_date"]
    assert [l["role"] for l in out[-1]["right_lines"]] == ["signature_authority", "signature_name"]
    again, n2 = T._normalize_layout(out, "TO_TRINH")
    assert n2 == [] and again == out  # da dung thi khong dong cham
