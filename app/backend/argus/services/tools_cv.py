"""Render the original mystore React CV templates, never generic Markdown layouts."""
import base64
import json
import shutil
import subprocess
from pathlib import Path

from .tools import tool, _resolve
from .tools_office import _out, _json


@tool("create_cv", "Tạo CV đẹp từ mẫu mystore đã được người dùng chọn. Xuất PDF A4 và HTML cùng bố cục, kèm JSON để sửa lại. KHÔNG tự chọn mẫu và KHÔNG dùng dữ liệu mẫu. data là JSON: name,title,email,phone,address,website,summary, experience:[{role,company,from,to,desc}], education:[{school,degree,from,to,desc}], skills:[{name}], languages:[{name,level}], projects:[{name,desc}], awards (chuỗi mỗi dòng một mục), highlights:[{value,label}], interests (chuỗi mỗi dòng một mục), photo_path (đường dẫn ảnh chân dung đã tải lên nếu có). Tất cả mục không có thông tin để trống; không bịa thành tích. lang=vi hoặc en.",
      {"path": ("string", "Tên file PDF, vd cv-nguyen-van-a.pdf"), "template": ("string", "ID mẫu người dùng đã chọn trong form; phải dùng đúng ID"), "data": ("string", "JSON hồ sơ thật với cấu trúc mô tả ở trên"), "lang": ("string", "vi hoặc en"), "skipped_sections": ("string", "JSON mảng các mục người dùng chọn bỏ qua, ví dụ [\"experience\",\"awards\"]") },
      required=["path", "template", "data"], risk="file")
def create_cv(ctx, path, template, data, lang="vi", skipped_sections="[]"):
    payload = _json(data, "Hồ sơ CV")
    if not isinstance(payload, dict) or not str(payload.get("name") or "").strip():
        raise ValueError("Cần họ tên thật trong data.name; hỏi người dùng nếu chưa có.")
    payload = dict(payload)
    skipped = _json(skipped_sections, "Mục bỏ qua")
    allowed_sections = {"summary", "experience", "education", "skills", "languages", "projects", "awards", "highlights", "interests"}
    if not isinstance(skipped, list) or any(not isinstance(k, str) or k not in allowed_sections for k in skipped):
        raise ValueError("Mục bỏ qua phải là mảng tên các mục CV hợp lệ.")
    for key in skipped:
        payload[key] = [] if key in {"experience", "education", "skills", "languages", "projects", "highlights"} else ""
    photo_path = payload.pop("photo_path", None)
    if photo_path:
        photo = _resolve(ctx, photo_path, "read")
        mime = {".jpg": "jpeg", ".jpeg": "jpeg", ".png": "png", ".webp": "webp"}.get(photo.suffix.lower())
        if not mime or photo.stat().st_size > 290_000:
            raise ValueError("Ảnh CV cần là JPEG, PNG hoặc WebP đã thu nhỏ dưới 290 KB.")
        payload["photo"] = f"data:image/{mime};base64," + base64.b64encode(photo.read_bytes()).decode("ascii")
    renderer = Path(__file__).resolve().parents[1] / "cv_templates" / "render.mjs"
    node = shutil.which("node")
    if not node or not renderer.exists():
        raise RuntimeError("Thiếu bộ dựng mẫu CV. Cài Node.js và chạy npm run build trong app/frontend.")
    pdf = _out(ctx, path, ".pdf")
    html = _out(ctx, str(pdf.with_suffix(".html")), ".html")
    source = _out(ctx, str(pdf.with_suffix(".json")), ".json")
    request = {"template": template, "data": payload, "lang": lang, "skipped_sections": skipped}
    result = subprocess.run([node, str(renderer)], input=json.dumps(request, ensure_ascii=False), capture_output=True, text=True, timeout=45)
    if result.returncode:
        raise ValueError("Không dựng được mẫu CV: " + result.stderr[-1200:])
    html.write_text(result.stdout, encoding="utf-8")
    source.write_text(json.dumps(request, ensure_ascii=False, indent=2), encoding="utf-8")
    # External resources are unnecessary: templates use inline styles and data images only.
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        options = {"headless": True}
        executable = shutil.which("chromium") or shutil.which("google-chrome")
        if executable:
            options["executable_path"] = executable
        browser = pw.chromium.launch(**options)
        try:
            page = browser.new_page(viewport={"width": 794, "height": 1123})
            page.route("**/*", lambda route: route.abort())
            page.set_content(result.stdout, wait_until="load")
            page.evaluate("document.fonts.ready")
            # Keep readable type. Report overflow rather than clipping or shrinking away content.
            height = page.locator('.cv-document').evaluate('(el) => el.scrollHeight')
            page.pdf(path=str(pdf), format="A4", print_background=True, prefer_css_page_size=True)
        finally:
            browser.close()
    pages_note = " Nội dung dài hơn một trang; rút gọn nội dung và chạy lại nếu cần CV một trang." if height > 1125 else ""
    return f"Đã tạo CV theo mẫu {template}:\nPDF: {pdf}\nHTML xem/in: {html}\nDữ liệu để sửa: {source}" + pages_note
