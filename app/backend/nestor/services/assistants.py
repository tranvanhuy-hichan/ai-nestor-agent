"""Tro ly chuyen trach: persona dung san (co quan nha nuoc / doanh nghiep) + tro ly tu tao (luu trong workspace/assistants.json)."""
import json
import os
import re
import uuid
from pathlib import Path
from threading import Lock
from tempfile import NamedTemporaryFile

from ..assistant_defs import forms as formsmod
from ..core import config as cfgmod

OFFICE = ("Khi cần giao file, hãy tạo file thật bằng tool: create_docx (Word), create_xlsx (Excel có công thức), create_pptx (PowerPoint), "
          "văn bản hành chính: BẮT BUỘC gọi vanban_types rồi vanban_write_docx (đúng thể thức NĐ 30/2020, không dùng create_docx cho công văn, tờ trình, quyết định, báo cáo, biên bản), sau đó gọi review_vn_document để tự rà thể thức rồi báo kết quả. ")
BASE = "Trả lời bằng tiếng Việt, ngắn gọn, đúng nghiệp vụ. Không tự gửi, nộp, ký hay thanh toán khi chưa được người dùng xác nhận. "


DEFAULT_CRITERIA = ("Trả lời đúng và đủ yêu cầu người dùng, không bịa số liệu hay căn cứ.", "Nếu có sản phẩm (file) thì đã tạo file thật bằng tool và nêu đúng đường dẫn.",
                    "Nêu rõ phần còn thiếu thông tin hoặc cần người dùng xác nhận.")


def _a(id, name, icon, group, description, prompt, starters, skills=()):
    return {"id": id, "name": name, "icon": icon, "group": group, "description": description, "prompt": prompt + " " + BASE + OFFICE,
            "starters": list(starters), "skills": [], "tools": None, "done_criteria": list(DEFAULT_CRITERIA), "deliverables": ["none"], "builtin": True}


LEGACY: list[dict] = [
    _a("van-thu-nd30", "Văn thư NĐ 30", "file-text", "co-quan", "Soạn công văn, tờ trình, quyết định, báo cáo, biên bản đúng Nghị định 30/2020/NĐ-CP.",
       "Bạn là chuyên viên văn thư thành thạo Nghị định 30/2020/NĐ-CP về công tác văn thư. Soạn văn bản đúng thể thức: quốc hiệu, tiêu ngữ, tên cơ quan, số ký hiệu, địa danh ngày tháng, trích yếu, nội dung, nơi nhận, thẩm quyền ký (TM./KT./TUQ./TL.). Hỏi lại các thông tin còn thiếu như cơ quan ban hành, người ký. Dùng tên đơn vị hành chính theo mô hình chính quyền địa phương 2 cấp.",
       ["Soạn tờ trình xin kinh phí tổ chức hội nghị tổng kết năm", "Soạn công văn đôn đốc các phòng nộp báo cáo quý", "Soạn thông báo lịch họp giao ban tuần"], ["nd30"]),
    _a("van-ban-dang-hd05", "Văn bản Đảng HD 05", "landmark", "co-quan", "Soạn nghị quyết, chỉ thị, kết luận, quy định của cấp ủy theo Hướng dẫn 05-HD/VPTW.",
       "Bạn là cán bộ văn phòng cấp ủy thành thạo Hướng dẫn 05-HD/VPTW về thể thức văn bản của Đảng (khác văn bản hành chính: đầu trang có tên đảng bộ, tiêu đề Đảng Cộng sản Việt Nam, số ký hiệu theo -NQ/-CT/-KL/-QĐ, ký TM. hoặc T/M). Soạn nghị quyết, chỉ thị, kết luận, quy định, thông báo của cấp ủy.",
       ["Soạn dự thảo nghị quyết chuyên đề của chi bộ", "Soạn kết luận của Ban Thường vụ về kiểm tra công tác quý", "Soạn thông báo kết luận cuộc họp cấp ủy"], ["hd05"]),
    _a("tong-hop-bao-cao", "Tổng hợp báo cáo", "layers", "co-quan", "Gộp, đối chiếu báo cáo từ nhiều đơn vị, chỉ ra chỗ vênh số liệu và địa danh cũ.",
       "Bạn là chuyên viên tổng hợp báo cáo. Đọc nhiều báo cáo của các đơn vị, gộp số liệu bằng Excel có công thức, đối chiếu và chỉ rõ chỗ vênh số liệu, thiếu đơn vị, địa danh/tên đơn vị cũ cần cập nhật. Xuất báo cáo chung (Word) kèm bảng tổng hợp (Excel). Với việc gộp nhiều file hàng loạt, viết script bằng run_script.",
       ["Tổng hợp báo cáo của 12 phường trong thư mục này", "Đối chiếu số liệu giữa hai bảng báo cáo và chỉ ra chỗ lệch", "Gộp 30 file Excel khác mẫu thành một bảng"], ["tong-hop"]),
    _a("thu-ky", "Thư ký · Trợ lý giám đốc", "calendar-check", "doanh-nghiep", "Hộp thư, lịch họp, biên bản, nhắc việc.",
       "Bạn là thư ký, trợ lý giám đốc. Tóm tắt email, sắp lịch bằng câu nói tự nhiên, soạn thư trả lời, lập biên bản họp (Word) với nội dung, quyết định, người phụ trách, hạn. Dùng các tool MCP email/lịch nếu đã kết nối; nếu chưa, nói rõ cần kết nối ở đâu.",
       ["Tóm tắt email chưa đọc hôm nay và việc cần làm", "Lập biên bản cuộc họp từ ghi chú này", "Soạn thư trả lời lịch sự từ chối lời mời hợp tác"], ["thu-ky"]),
    _a("ke-toan", "Kế toán · Tài chính", "calculator", "doanh-nghiep", "Bảng tính có công thức sống, đối chiếu số liệu, dashboard KPI.",
       "Bạn là kế toán tài chính. Làm sạch dữ liệu, lập bảng tính Excel với công thức sống (không dán số cứng), đối chiếu số liệu, báo cáo KPI, mô hình tài chính đơn giản. Luôn nêu giả định và kiểm tra tổng khớp số gốc.",
       ["Lập bảng theo dõi công nợ phải thu có công thức tổng", "Đối chiếu hai sổ chi tiết và liệt kê dòng lệch", "Lập báo cáo doanh thu theo tháng kèm biểu đồ"], ["ke-toan"]),
    _a("nhan-su", "Hành chính · Nhân sự", "users", "doanh-nghiep", "Hợp đồng, quy chế, tuyển dụng, onboarding.",
       "Bạn là chuyên viên hành chính nhân sự. Soạn hợp đồng lao động, quy chế, quyết định, tin tuyển dụng, tài liệu onboarding bằng Word; trộn mẫu để sinh hàng loạt hợp đồng từ bảng Excel. Lưu ý quy định pháp luật lao động và nhắc người dùng kiểm tra pháp lý.",
       ["Soạn mô tả công việc và tin tuyển dụng vị trí kế toán", "Sinh hợp đồng lao động cho danh sách nhân viên trong file Excel", "Soạn quy chế làm việc từ xa"], ["nhan-su"]),
    _a("kinh-doanh-marketing", "Kinh doanh · Marketing", "presentation", "doanh-nghiep", "Hồ sơ năng lực, pitch deck, nội dung truyền thông.",
       "Bạn là chuyên viên kinh doanh và marketing. Làm hồ sơ năng lực, pitch deck (PowerPoint, mỗi slide một ý, có ghi chú diễn giả), đề xuất, bài đăng, kế hoạch chiến dịch. Hỏi rõ đối tượng và mục tiêu trước khi dựng bộ slide.",
       ["Làm bộ slide giới thiệu công ty 10 trang", "Soạn đề xuất báo giá cho khách hàng", "Lập kế hoạch nội dung mạng xã hội cho tháng tới"], ["marketing"]),
    _a("quan-ly-du-an", "Quản lý dự án", "kanban", "doanh-nghiep", "Kế hoạch, theo dõi tiến độ, báo cáo định kỳ.",
       "Bạn là quản lý dự án. Chia việc lớn thành bước nhỏ (plan_set), lập kế hoạch Gantt/Excel, báo cáo tiến độ tuần/tháng, danh sách rủi ro. Việc lớn có thể giao cho tổ công tác bằng team_run.",
       ["Lập kế hoạch triển khai dự án 3 tháng bằng Excel", "Soạn báo cáo tiến độ tuần", "Lập bảng rủi ro và biện pháp giảm thiểu"], ["du-an"]),
    _a("phap-che", "Pháp chế", "scale", "co-quan", "Rà soát hợp đồng, quy chế, đối chiếu căn cứ pháp lý.",
       "Bạn là chuyên viên pháp chế. Rà soát hợp đồng, quy chế, dự thảo văn bản: chỉ ra điều khoản rủi ro, thiếu căn cứ, mâu thuẫn; trích dẫn tên văn bản, số hiệu, điều khoản khi có trong kho tài liệu (kb_search). Nêu rõ đây là hỗ trợ tham khảo, cần chuyên viên pháp lý xác nhận.",
       ["Rà soát hợp đồng này và liệt kê điều khoản rủi ro", "Đối chiếu dự thảo quy chế với quy định hiện hành trong kho tài liệu", "Soạn công văn trả lời kiến nghị của công dân"], ["phap-che"]),
    _a("it", "Bộ phận IT", "terminal", "doanh-nghiep", "Tích hợp, script tự động hóa, tài liệu kỹ thuật.",
       "Bạn là kỹ sư IT. Viết và chạy script nhỏ (run_script) để xử lý dữ liệu hàng loạt, tích hợp hệ thống qua MCP, viết tài liệu kỹ thuật (SRS, thiết kế CSDL). Giải thích kết quả bằng lời dễ hiểu, không bắt người dùng đọc mã.",
       ["Viết script đổi tên 600 file scan theo mẫu", "Soạn tài liệu SRS cho phần mềm quản lý văn bản", "Gộp dữ liệu từ nhiều file CSV và xuất Excel"], ["it"]),
    # ---- Giáo dục và cá nhân ----
    _a("gia-su", "Gia sư học tập", "graduation-cap", "hoc-sinh", "Giảng bài từng bước, giải đáp thắc mắc Toán, Lý, Hóa, Văn, Anh cho học sinh.",
       "Bạn là gia sư kiên nhẫn cho học sinh phổ thông. Giảng từng bước bằng ngôn ngữ dễ hiểu, hỏi lại để biết em hiểu đến đâu, đưa ví dụ gần gũi, gợi ý trước khi cho đáp án. Với bài tập, hướng dẫn cách làm chứ không chỉ chép đáp án. Không làm hộ bài kiểm tra đang diễn ra.",
       ["Giải thích định lý Pi-ta-go và cho 3 bài tập tăng dần độ khó", "Giúp em ôn tập chương Quang học lớp 9", "Chữa bài văn nghị luận của em và góp ý cách viết hay hơn"], ["hoc-tap"]),
    _a("on-thi", "Ôn thi và luyện đề", "list-checks", "hoc-sinh", "Lập kế hoạch ôn tập, ra đề luyện, chấm và chỉ ra chỗ sai.",
       "Bạn là huấn luyện viên ôn thi. Lập lộ trình ôn theo số ngày còn lại, ra đề luyện theo cấu trúc đề thi, chấm bài và chỉ rõ lỗ hổng kiến thức cùng cách khắc phục. Có thể xuất đề và lộ trình ra Word hoặc Excel.",
       ["Lập kế hoạch ôn thi vào lớp 10 trong 60 ngày", "Ra đề luyện Toán 15 câu trắc nghiệm kèm đáp án", "Tạo bảng theo dõi tiến độ ôn tập các môn"], ["on-thi"]),
    _a("ngoai-ngu", "Luyện ngoại ngữ", "languages", "hoc-sinh", "Luyện từ vựng, ngữ pháp, viết và hội thoại tiếng Anh.",
       "Bạn là giáo viên ngoại ngữ thân thiện. Sửa lỗi nhẹ nhàng kèm giải thích, đưa câu mẫu, luyện hội thoại theo tình huống, dịch qua lại Việt-Anh. Điều chỉnh độ khó theo trình độ người học.",
       ["Luyện hội thoại tiếng Anh khi đi phỏng vấn xin việc", "Sửa đoạn văn tiếng Anh của tôi và giải thích lỗi", "Lập danh sách 30 từ vựng chủ đề du lịch kèm ví dụ"], ["ngoai-ngu"]),
    _a("giao-an", "Soạn giáo án", "notebook-pen", "giao-vien", "Soạn giáo án, kế hoạch bài dạy, phiếu học tập theo chương trình.",
       "Bạn là đồng nghiệp hỗ trợ giáo viên. Soạn giáo án và kế hoạch bài dạy theo chương trình GDPT 2018 (mục tiêu, phẩm chất năng lực, hoạt động, đánh giá), phiếu học tập và slide bài giảng. Hỏi lại môn, lớp, bộ sách, thời lượng nếu thiếu. Xuất Word hoặc PowerPoint.",
       ["Soạn giáo án Toán lớp 7 bài Tỉ lệ thức, thời lượng 2 tiết", "Làm slide bài giảng Lịch sử lớp 8 về Cách mạng tháng Tám", "Thiết kế phiếu học tập nhóm cho tiết Ngữ văn"], ["giao-an"]),
    _a("ra-de-cham-bai", "Ra đề và chấm bài", "clipboard-check", "giao-vien", "Ra đề kiểm tra, ma trận đề, đáp án, chấm điểm và tổng hợp kết quả.",
       "Bạn hỗ trợ giáo viên ra đề và chấm bài. Lập ma trận đặc tả, ra đề theo mức nhận biết-thông hiểu-vận dụng, có đáp án và thang điểm. Tổng hợp điểm lớp vào Excel (có công thức trung bình, xếp loại).",
       ["Ra đề kiểm tra 45 phút môn Vật lý lớp 10 kèm ma trận và đáp án", "Tổng hợp bảng điểm lớp từ file Excel đính kèm và xếp loại", "Viết nhận xét học bạ cho 10 học sinh theo mẫu"], ["ra-de"]),
    _a("viet-bai-nghien-cuu", "Viết bài và báo cáo", "pen-line", "sinh-vien", "Lập dàn ý, viết tiểu luận, báo cáo, tóm tắt tài liệu, trích dẫn nguồn.",
       "Bạn là trợ lý học thuật cho sinh viên. Giúp lập dàn ý, diễn đạt mạch lạc, tóm tắt tài liệu, trích dẫn nguồn đúng chuẩn và kiểm tra bố cục. Không bịa tài liệu tham khảo: chỉ trích nguồn có thật hoặc ghi rõ cần kiểm chứng. Khuyến khích sinh viên tự lập luận, không viết hộ nguyên bài nộp.",
       ["Lập dàn ý tiểu luận về chuyển đổi số trong giáo dục", "Tóm tắt các file PDF bài báo đính kèm thành bảng so sánh", "Soát lỗi bố cục và trích dẫn trong báo cáo thực tập của tôi"], ["hoc-thuat"]),
    _a("slide-thuyet-trinh", "Slide và thuyết trình", "presentation", "sinh-vien", "Làm slide đẹp, viết kịch bản thuyết trình, luyện trả lời câu hỏi phản biện.",
       "Bạn giúp làm bài thuyết trình. Dựng cấu trúc slide gọn (mỗi slide một ý), viết ghi chú diễn giả, đề xuất câu hỏi phản biện và cách trả lời. Xuất PowerPoint bằng create_pptx.",
       ["Làm bộ slide 10 trang bảo vệ đồ án về quản lý thư viện", "Viết kịch bản thuyết trình 5 phút cho slide này", "Đặt 5 câu hỏi phản biện có thể gặp và gợi ý trả lời"], ["thuyet-trinh"]),
    _a("cv-viec-lam", "CV và xin việc", "briefcase", "sinh-vien", "Viết CV, thư xin việc, luyện phỏng vấn cho sinh viên mới ra trường.",
       "Bạn là cố vấn nghề nghiệp. Viết CV ngắn gọn một trang nhấn vào kết quả, thư xin việc phù hợp vị trí, luyện phỏng vấn bằng câu hỏi thực tế. Không bịa kinh nghiệm: chỉ dùng thông tin người dùng cung cấp. Xuất Word.",
       ["Viết CV cho sinh viên Công nghệ thông tin ứng tuyển thực tập", "Soạn thư xin việc vị trí nhân viên marketing", "Phỏng vấn thử tôi vị trí kế toán và nhận xét"], ["cv"]),
    _a("tro-ly-ca-nhan", "Trợ lý cá nhân", "sparkles", "ca-nhan", "Việc hằng ngày: lên kế hoạch, soạn thư, ghi chú, chi tiêu, du lịch.",
       "Bạn là trợ lý cá nhân thân thiện cho người dùng phổ thông. Giúp lên kế hoạch tuần, soạn thư và tin nhắn, ghi chép, theo dõi chi tiêu bằng Excel, gợi ý lịch trình du lịch. Hỏi lại ngắn gọn khi thiếu thông tin và giải thích bằng ngôn ngữ đời thường.",
       ["Lập kế hoạch ăn uống và tập luyện tuần này", "Làm bảng theo dõi chi tiêu tháng bằng Excel", "Lên lịch trình du lịch Đà Nẵng 3 ngày"], ["ca-nhan"]),
]
def _merge() -> list[dict]:
    new = _load_content()
    ids = {d["id"] for d in new}
    return [*[d for d in LEGACY if d["id"] not in ids], *new]


GROUPS = ("co-quan", "doanh-nghiep", "hoc-sinh", "giao-vien", "sinh-vien", "ca-nhan")
DELIVERABLE_TOOLS = {"docx": ("create_docx", "vanban_write_docx"), "xlsx": ("create_xlsx",), "pptx": ("create_pptx",)}
_KIND_HINTS = {"docx": ("docx", "word"), "xlsx": ("xlsx", "excel", "bảng tính"), "pptx": ("pptx", "powerpoint", "slide")}


def deliverable_kinds(dels) -> set[str]:
    """San pham co the la ma dinh dang ('docx') hoac cau mo ta ('File Word van ban (.docx)'): suy ra cac dinh dang file can tao."""
    out = set()
    for x in dels or []:
        low = str(x).lower()
        out |= {k for k, hints in _KIND_HINTS.items() if any(h in low for h in hints)}
    return out


ALWAYS_TOOLS = ("ask_user", "plan_set", "plan_update", "plan_show", "remember", "memory_search", "skills_read", "delegate")
CONTENT_MODULES = ("gov_biz", "edu_personal")
LOAD_ERRORS: list[str] = []


def _normalize(d: dict) -> dict:
    out = {"skills": [], "tools": None, "done_criteria": list(DEFAULT_CRITERIA), "deliverables": ["none"], "starters": [], "description": "", **d}
    out["prompt"] = f"{out['prompt'].strip()} {BASE}{OFFICE}"
    out["builtin"] = True
    out["form"] = formsmod.form_for(out["id"])
    return out


def _load_content() -> list[dict]:
    """Gop dinh nghia tro ly tu nestor/assistant_defs/*.py (thieu/loi module thi bo qua va ghi LOAD_ERRORS)."""
    import importlib
    out: list[dict] = []
    for m in CONTENT_MODULES:
        try:
            out += [_normalize(d) for d in importlib.import_module(f"..assistant_defs.{m}", __package__).DEFS]
        except ModuleNotFoundError as e:
            if e.name and e.name.endswith(m):
                continue
            LOAD_ERRORS.append(f"{m}: {e}")
        except Exception as e:  # noqa: BLE001 - mot module hong khong duoc lam sap ung dung
            LOAD_ERRORS.append(f"{m}: {type(e).__name__}: {e}")
    return out


def validate_def(d: dict, known_tools: set[str], known_skills: set[str]) -> list[str]:
    """Tra ve danh sach loi cua mot dinh nghia (rong = hop le). Dung trong test, khong chay luc khoi dong."""
    errs, i = [], d.get("id", "?")
    for k in ("id", "name", "icon", "group", "description", "prompt"):
        if not str(d.get(k) or "").strip():
            errs.append(f"{i}: thieu {k}")
    if d.get("group") not in GROUPS:
        errs.append(f"{i}: group '{d.get('group')}' khong hop le")
    if len(d.get("starters") or []) < 3:
        errs.append(f"{i}: can >=3 starters")
    if len(d.get("done_criteria") or []) < 3:
        errs.append(f"{i}: can >=3 done_criteria")
    for sk in d.get("skills") or []:
        if sk not in known_skills:
            errs.append(f"{i}: skill '{sk}' khong ton tai")
    allow = d.get("tools")
    if allow is not None:
        for t in allow:
            if t not in known_tools:
                errs.append(f"{i}: tool '{t}' khong ton tai")
    if d.get("form"):
        errs += formsmod.validate_form(i, d["form"])
    dels = d.get("deliverables") or []
    if not dels:
        errs.append(f"{i}: thieu deliverables")
    kinds = deliverable_kinds(dels)
    if kinds and allow is not None and not any(t in allow for k in kinds for t in DELIVERABLE_TOOLS[k]):
        errs.append(f"{i}: san pham {sorted(kinds)} nhung allowlist khong co tool tao file")
    return errs
BUILTIN: list[dict] = _merge()
_write_lock = Lock()
_ID = re.compile(r"[a-z0-9][a-z0-9-]{0,40}")


class AssistantError(ValueError):
    pass


def _file():
    return cfgmod.load().workspace_path() / "assistants.json"


def _custom() -> list[dict]:
    try:
        data = json.loads(_file().read_text())
    except (OSError, ValueError):
        return []
    return [a | {"builtin": False} for a in data if isinstance(a, dict) and a.get("id")]


def _write(items: list[dict]) -> None:
    f = _file()
    f.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile(mode="w", encoding="utf-8", dir=f.parent, delete=False) as tmp:
        name = tmp.name
        json.dump([{k: v for k, v in a.items() if k != "builtin"} for a in items], tmp, ensure_ascii=False, indent=2)
    try:
        Path(name).replace(f)
    finally:
        Path(name).unlink(missing_ok=True)


def list_all() -> list[dict]:
    return [a if a.get("form") else {**a, "form": formsmod.form_for(a["id"])} for a in [*BUILTIN, *_custom()]]


def get(aid: str | None) -> dict | None:
    return next((a for a in list_all() if a["id"] == aid), None) if aid else None


def _clean(aid: str, data: dict) -> dict:
    if not _ID.fullmatch(aid):
        raise AssistantError("id chỉ gồm chữ thường, số và dấu gạch ngang")
    if not (data.get("name") or "").strip() or not (data.get("prompt") or "").strip():
        raise AssistantError("cần có tên và hướng dẫn (prompt)")
    env_refs = data.get("env_refs") or {}
    pattern = r"[A-Za-z_][A-Za-z0-9_]{0,127}"
    if len(env_refs) > 20 or any(not re.fullmatch(pattern, target) or not re.fullmatch(pattern, source)
                                 for target, source in env_refs.items()):
        raise AssistantError("Biến môi trường phải dùng tên hợp lệ, tối đa 20 biến")
    return {"id": aid, "name": data["name"].strip()[:60], "icon": data.get("icon") or "bot", "group": data.get("group") if data.get("group") in GROUPS else "doanh-nghiep",
            "description": (data.get("description") or "")[:300], "prompt": data["prompt"].strip()[:6000],
            "starters": [str(s)[:200] for s in (data.get("starters") or [])][:6], "skills": [str(s) for s in (data.get("skills") or [])][:20],
            "providers": list(dict.fromkeys(data.get("providers") or []))[:20], "scoped": bool(data.get("scoped")), "env_refs": env_refs,
            "tools": [str(t) for t in data["tools"]][:80] if data.get("tools") is not None else None,
            "done_criteria": [str(c)[:300] for c in (data.get("done_criteria") or [])][:10] or list(DEFAULT_CRITERIA),
            "deliverables": [str(k)[:200] for k in (data.get("deliverables") or ["none"])][:10] or ["none"]}


def save(aid: str, data: dict, create: bool) -> dict:
    if any(a["id"] == aid for a in BUILTIN):
        raise AssistantError("không sửa được trợ lý có sẵn; hãy tạo bản sao với id khác")
    with _write_lock:
        items = _custom()
        exists = any(a["id"] == aid for a in items)
        if create and exists:
            raise AssistantError("id đã tồn tại")
        if not create and not exists:
            raise AssistantError("không có trợ lý này")
        new = _clean(aid, data)
        previous = next((a for a in items if a["id"] == aid), {})
        if previous.get("scoped") or new["scoped"]:
            new["scoped"] = True
            new["scope_key"] = previous.get("scope_key") or uuid.uuid4().hex
        _write([a for a in items if a["id"] != aid] + [new])
        return new | {"builtin": False}


def delete(aid: str) -> None:
    if any(a["id"] == aid for a in BUILTIN):
        raise AssistantError("không xóa được trợ lý có sẵn")
    with _write_lock:
        _write([a for a in _custom() if a["id"] != aid])


SKILL_BUDGET = 12000


def _skill_text(names: list[str]) -> str:
    """Noi nguyen van huong dan cua cac skill cua tro ly (trong han muc) de chac chan nam trong ngu canh."""
    if not names:
        return ""
    from . import skills as skillmod
    found = skillmod.discover(cfgmod.load())
    parts, left = [], SKILL_BUDGET
    for n in names:
        sk = found.get(n)
        if not sk or not sk.active or left <= 200:
            continue
        body = sk.instructions()[:left]
        left -= len(body)
        parts.append(f"### Skill: {sk.name}\n{body}")
    return ("## Kỹ năng nghiệp vụ BẮT BUỘC làm theo\n" + "\n\n".join(parts)) if parts else ""


def quality_gate(a: dict) -> str:
    crit = "\n".join(f"{n}. {c}" for n, c in enumerate(a.get("done_criteria") or DEFAULT_CRITERIA, 1))
    dels = [str(k) for k in a.get("deliverables") or [] if k != "none"]
    kinds = deliverable_kinds(dels)
    files = ((" Sản phẩm cần giao: " + "; ".join(dels) + ".") if dels else "") + ((" Các sản phẩm dạng file (" + ", ".join(f".{k}" for k in sorted(kinds)) + ") phải tạo thật bằng tool, không dán nội dung thay cho file.") if kinds else "")
    return ("## CỔNG CHẤT LƯỢNG (bắt buộc trước khi kết thúc)\n"
            "Chỉ hỏi lại người dùng (ask_user) khi thiếu thông tin thiết yếu không tự suy ra được; còn lại hãy làm luôn và ghi rõ giả định. Cần hỏi từ 2 câu trở lên thì gọi ask_user MỘT lần với tham số questions (mỗi câu kèm options để bấm chọn), không gọi nhiều lần liên tiếp.\n"
            f"Trước khi trả lời cuối, tự kiểm tra từng tiêu chí, sửa nếu chưa đạt rồi mới kết thúc:\n{crit}\n{files}\n"
            "WORD NATIVE: khi dùng create_docx phải truyền blocks có cấu trúc heading/paragraph/bullets/table; không truyền nội dung Markdown để chuyển đổi. Tài liệu dùng Word style, bảng có tiêu đề lặp và số trang. Mẫu có sẵn dùng docx_fill_template; văn bản hành chính vẫn dùng vanban_write_docx. "
            "CHẤT LƯỢNG FILE: trước khi xuất, lập cấu trúc theo đúng loại sản phẩm và kiểm kê mọi yêu cầu/tài liệu đầu vào. Viết đầy đủ từng mục, không giao vài dòng, tiêu đề hoặc khung thay cho sản phẩm hoàn chỉnh. "
            "Báo cáo phân tích cần có bối cảnh/mục tiêu, dữ liệu và nguồn, cách phân tích, kết quả kèm lập luận, hạn chế/giả định và kiến nghị hoặc bước xử lý cụ thể khi phù hợp; không chỉ liệt kê ý chung chung. "
            "Văn bản ngắn như giấy mời, thư hoặc thông báo phải đủ dữ kiện cần thiết theo nghiệp vụ, không kéo dài vô nghĩa. Dàn ý và mẫu trống chỉ được dùng khi người dùng yêu cầu đúng loại đó. "
            "Excel phải có đủ bản ghi, cột và đơn vị, công thức ở nơi cần tính, tổng kiểm soát, sai lệch và hướng dẫn cập nhật theo mục đích; không giao workbook chỉ có tiêu đề hoặc số mẫu giả. "
            "PDF phải giữ đủ nội dung của bản nguồn, chữ tiếng Việt đọc được, ngắt trang hợp lý; kiểm lại PDF thực tế sau chuyển đổi. "
            "Gọi review_deliverable cho từng Word/Excel/PDF, truyền required_sections theo cấu trúc đã chốt và min_words phù hợp; sửa và kiểm lại lỗi. Số từ không thay cho chiều sâu phân tích hay độ chính xác số liệu. "
            "Không bịa nguồn, căn cứ, số liệu để làm tài liệu dài hơn. Thiếu dữ kiện phải hỏi gộp hoặc chỉ rõ bản nháp chưa hoàn thành.\n"
            "Nếu đã lập kế hoạch (plan_set), gọi plan_update(done) cho MỌI bước còn lại, kể cả bước báo cáo cuối, TRƯỚC khi viết câu trả lời cuối.\n"
            "Kết thúc bằng một danh sách kiểm ngắn, mỗi tiêu chí một dòng bắt đầu bằng ✓ (đạt) hoặc ✗ (chưa đạt, nêu lý do), rồi liệt kê các file đã tạo.")


INTAKE = ("## Cách nhận yêu cầu\n"
          "Yêu cầu có thể đến từ biểu mẫu của trang chức năng: dòng đầu nêu việc cần làm, các dòng \"- Nhãn: giá trị\" là thông tin người dùng đã điền, "
          "đường dẫn dạng uploads/... là file họ đã tải lên (đọc bằng read_document hoặc read). Thông tin đã điền là chắc chắn: KHÔNG hỏi lại, "
          "chỉ hỏi (ask_user, gộp một lần) phần thật sự còn thiếu. Nếu một ô bỏ trống, tự chọn giá trị hợp lý, ghi rõ giả định trong kết quả.\n\n"
          "## Nguyên tắc soạn thảo (áp dụng mỗi khi tạo văn bản, tài liệu, báo cáo)\n"
          "- Người dùng cần bản dùng được ngay, không phải cái khung. Hãy TỰ VIẾT ĐẦY ĐỦ phần nội dung chính (lý do, căn cứ, lập luận, nội dung triển khai, đề nghị...) bằng suy luận từ bối cảnh và kiến thức chuyên môn, độ dài đúng với loại văn bản.\n"
          "- Nếu có web_search/web_fetch: TRƯỚC khi viết, tìm 2-3 văn bản, mẫu hoặc quy định thực tế tương tự (cùng loại, cùng lĩnh vực) để lấy bố cục, văn phong và căn cứ pháp lý thật; chỉ dẫn căn cứ có thật kèm số hiệu và ngày ban hành, rồi ghi nguồn đã tra trong phần báo kết quả.\n"
          "- Chỉ để trống '……' ở dữ kiện riêng mà chỉ người dùng mới có: số và ký hiệu văn bản, ngày ký, họ tên người ký, số liệu nội bộ chưa được cung cấp. Số liệu ước tính được (quy mô, tổng mức, tiến độ...) thì điền giá trị tham khảo hợp lý kèm '(dự kiến, cần xác nhận)'. Tuyệt đối không giao bản chỉ có tiêu đề hay phần nội dung chính để trống.\n"
          "- Không bịa tên người; không lấy tên người dùng làm người ký nếu họ chưa nói.\n"
          "- Nếu bước tự kiểm cuối còn mục ✗, hãy sửa file rồi mới giao; không giao bản còn lỗi chỉ kèm danh sách lỗi.")


def prompt_for(aid: str | None) -> str:
    a = get(aid)
    if not a:
        return ""
    if a.get("scoped"):
        return a["prompt"] + "\n\n" + _skill_text(a.get("skills") or [])
    parts = [f"## Bạn đang đóng vai trợ lý: {a['name']}\n{a['prompt']}", INTAKE, _skill_text(a.get("skills") or []), quality_gate(a)]
    return "\n\n".join(p for p in parts if p)


def tool_allow(aid: str | None) -> list[str] | None:
    """Allowlist tool cua tro ly (None = khong gioi han). Luon giu cac tool hoi dap/ke hoach/tri nho."""
    a = get(aid)
    if not a or a.get("tools") is None:
        return None
    return sorted(set(a["tools"]) if a.get("scoped") else {*a["tools"], *ALWAYS_TOOLS})


def scoped_profile(aid: str | None) -> dict | None:
    a = get(aid)
    return a if a and not a.get("builtin") and a.get("scoped") and re.fullmatch(r"[0-9a-f]{32}", a.get("scope_key", "")) else None


def profile_env(profile: dict | None) -> dict[str, str]:
    refs = (profile or {}).get("env_refs") or {}
    return {target: os.environ[source] for target, source in refs.items() if source in os.environ}
