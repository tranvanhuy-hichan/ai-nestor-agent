"""Self-Healing Tool Calls: Chẩn đoán và sinh hướng dẫn tự sửa lỗi tham số công cụ theo chuẩn Hermes Agent.

Khi mô hình gọi tool nhưng truyền sai tham số (thiếu field, sai kiểu dữ liệu, sai tên tham số, JSON lỗi),
hệ thống không chỉ báo lỗi cụt ngủn mà cung cấp Rich Diagnostic Message kèm schema chuẩn và ví dụ mẫu,
giúp mô hình tự vá lỗi (Self-Correction) ngay trong lượt gọi kế tiếp.
"""
from __future__ import annotations

import difflib
import json
import re
from typing import Any


def diagnose_tool_call(tool_name: str, tdef: Any, args: dict[str, Any], err: Exception) -> str:
    """Tạo thông báo chẩn đoán chi tiết giúp mô hình tự sửa lỗi tham số."""
    if not tdef:
        return f"[LỖI CÔNG CỤ] Không tìm thấy công cụ '{tool_name}' trong hệ thống."

    params_schema = getattr(tdef, "parameters", {}) or {}
    if isinstance(params_schema, dict) and "properties" in params_schema:
        properties = params_schema.get("properties", {})
        required_params = list(params_schema.get("required", []))
    else:
        properties = params_schema if isinstance(params_schema, dict) else {}
        required_params = list(properties.keys())

    diagnostics: list[str] = []
    diagnostics.append(f"❌ [LỖI THAM SỐ CÔNG CỤ '{tool_name}']: {type(err).__name__}: {err}")

    # Trích xuất tên tham số bị thiếu từ TypeError nếu có
    err_str = str(err)
    missing_from_err = re.findall(r"required (?:positional )?argument:? '(\w+)'", err_str)
    missing_from_schema = [k for k in required_params if k not in args or args[k] is None]
    missing = list(dict.fromkeys(missing_from_err + missing_from_schema))

    if missing:
        diagnostics.append(f"⚠️ THIẾU THAM SỐ BẮT BUỘC: {', '.join(f'`{m}`' for m in missing)}")

    # 2. Kiểm tra tham số bị viết sai tên (Typo / Misnamed arguments)
    valid_names = list(properties.keys())
    unknown_args = [k for k in args if k not in valid_names]
    typo_hints = []
    for unk in unknown_args:
        matches = difflib.get_close_matches(unk, valid_names, n=2, cutoff=0.4)
        if matches:
            typo_hints.append(f"Bạn đã truyền `{unk}`, có phải bạn muốn truyền `{matches[0]}`?")
        else:
            typo_hints.append(f"Tham số `{unk}` không tồn tại trong công cụ `{tool_name}`.")
    if typo_hints:
        diagnostics.append("⚠️ SAI TÊN THAM SỐ:\n  " + "\n  ".join(typo_hints))

    # 3. Kiểm tra kiểu dữ liệu hoặc JSON string parse
    type_hints = []
    for k, v in args.items():
        if k in properties:
            pdef = properties[k]
            expected_type = pdef.get("type") if isinstance(pdef, dict) else (pdef[0] if isinstance(pdef, (list, tuple)) else str(pdef))
            if expected_type in ("object", "array") and isinstance(v, str):
                try:
                    json.loads(v)
                except Exception as je:
                    type_hints.append(f"Tham số `{k}` yêu cầu chuỗi JSON hợp lệ ({expected_type}), nhưng JSON bị lỗi cú pháp: {je}")
            elif expected_type == "integer" and not isinstance(v, int):
                type_hints.append(f"Tham số `{k}` yêu cầu kiểu số nguyên (int), nhưng nhận được: `{type(v).__name__}`")
            elif expected_type == "boolean" and not isinstance(v, bool):
                type_hints.append(f"Tham số `{k}` yêu cầu kiểu logic (boolean true/false), nhưng nhận được: `{type(v).__name__}`")
    if type_hints:
        diagnostics.append("⚠️ SAI KIỂU DỮ LIỆU:\n  " + "\n  ".join(type_hints))

    # 4. Cung cấp Schema chuẩn của công cụ
    schema_summary = []
    for k, v in properties.items():
        ptype = v.get("type", "any") if isinstance(v, dict) else (v[0] if isinstance(v, (list, tuple)) else "any")
        pdesc = v.get("description", "") if isinstance(v, dict) else (v[1] if isinstance(v, (list, tuple)) and len(v) > 1 else "")
        req_tag = " (Bắt buộc)" if k in required_params else " (Tùy chọn)"
        schema_summary.append(f"- `{k}` ({ptype}){req_tag}: {pdesc}")

    diagnostics.append("\n📋 CẤU TRÚC THAM SỐ HỢP LỆ:")
    diagnostics.extend(schema_summary[:10])

    # 5. Hướng dẫn tự sửa (Self-Healing Action)
    diagnostics.append(
        "\n💡 HƯỚNG DẪN TỰ SỬA (Self-Healing):\n"
        f"Hãy xem lại thông báo lỗi và danh sách tham số hợp lệ ở trên. "
        f"Điều chỉnh lại các tham số của công cụ `{tool_name}` cho đúng định dạng và gọi lại ngay trong bước này."
    )

    return "\n".join(diagnostics)
