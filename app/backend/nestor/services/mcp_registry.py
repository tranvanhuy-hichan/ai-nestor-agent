"""Tim dich vu MCP trong thu vien MCP chinh thuc (registry.modelcontextprotocol.io) va kho plugin Hermes."""
import json
from pathlib import Path

import httpx

URL = "https://registry.modelcontextprotocol.io/v0/servers"
KINDS = {"streamable-http": "http", "sse": "sse"}
COMMUNITY_PREFIXES = ("io.github.", "ai.smithery/", "app.", "tech.", "dev.", "xyz.", "hermes/")
HERMES_CATALOG_PATHS = (
    Path(__file__).resolve().parent.parent / "data" / "hermes_plugin_catalog.json",
    Path.home() / ".hermes" / "cache" / "plugin-catalog.json",
)


class RegistryError(Exception):
    pass


def _normalize(entry: dict) -> dict | None:
    s = entry.get("server") or {}
    remotes = [r for r in (s.get("remotes") or []) if r.get("type") in KINDS and r.get("url") and "{" not in r["url"]]
    if not remotes:
        return None
    r = remotes[0]
    name = s.get("name", "")
    headers = [h for h in (r.get("headers") or []) if h.get("name")]
    return {"id": name, "name": s.get("title") or name.split("/")[-1], "description": (s.get("description") or "")[:300], "website": s.get("websiteUrl") or "",
            "url": r["url"], "transport": KINDS[r["type"]], "publisher": name.split("/")[0],
            "community": name.startswith(COMMUNITY_PREFIXES), "needs_header": [h["name"] for h in headers if h.get("isRequired") or h.get("isSecret")]}


def _get_hermes_catalog_path() -> Path | None:
    for p in HERMES_CATALOG_PATHS:
        if p.is_file():
            return p
    return None


_CATALOG_CACHE: list[dict] | None = None


def _load_hermes_catalog() -> list[dict]:
    global _CATALOG_CACHE
    if _CATALOG_CACHE is not None:
        return _CATALOG_CACHE
    catalog_path = _get_hermes_catalog_path()
    if not catalog_path:
        return []
    try:
        data = json.loads(catalog_path.read_text(errors="replace"))
        _CATALOG_CACHE = data.get("entries", [])
        return _CATALOG_CACHE
    except Exception:
        return []


def search_hermes(q: str, limit: int = 10) -> list[dict]:
    """Tim kiem trong kho ~2500 plugin va MCP server cua Hermes da co tren may."""
    if not q or len(q.strip()) < 2:
        return []
    entries = _load_hermes_catalog()
    if not entries:
        return []

    ql = q.strip().lower()
    items: list[dict] = []
    for e in entries:
        name = e.get("name") or ""
        title = e.get("title") or name
        desc = e.get("description") or ""
        repo = e.get("repo") or ""
        docs = e.get("docs_url") or repo
        if ql in name.lower() or ql in title.lower() or ql in desc.lower():
            items.append({
                "id": f"hermes/{name}",
                "name": f"{title} (Hermes)",
                "description": desc[:300],
                "website": docs,
                "url": repo or f"https://github.com/nousresearch/hermes-agent/plugins/{name}",
                "transport": "http",
                "publisher": e.get("maintainer") or "Hermes Ecosystem",
                "community": True,
                "needs_header": [],
            })
            if len(items) >= limit:
                break
    return items


def list_hermes_plugins(q: str = "", category: str = "all", page: int = 0, limit: int = 24) -> dict:
    """Liet ke kho 2.500+ plugin Hermes voi day du thong tin, dem danh muc va phan trang."""
    entries = _load_hermes_catalog()
    total_all = len(entries)
    cat_counts: dict[str, int] = {"all": total_all}
    for e in entries:
        c = e.get("category") or "other"
        cat_counts[c] = cat_counts.get(c, 0) + 1

    categories = [
        {"id": "all", "label": {"vi": "Tất cả", "en": "All"}, "count": cat_counts.get("all", 0)},
        {"id": "tools", "label": {"vi": "Công cụ & Tiện ích", "en": "Tools & Utilities"}, "count": cat_counts.get("tools", 0)},
        {"id": "desktop", "label": {"vi": "Máy tính & Ứng dụng", "en": "Desktop & Apps"}, "count": cat_counts.get("desktop", 0)},
        {"id": "automation", "label": {"vi": "Tự động hóa", "en": "Automation"}, "count": cat_counts.get("automation", 0)},
        {"id": "models", "label": {"vi": "Mô hình & AI", "en": "Models & AI"}, "count": cat_counts.get("models", 0)},
        {"id": "memory", "label": {"vi": "Bộ nhớ & Dữ liệu", "en": "Memory & Storage"}, "count": cat_counts.get("memory", 0)},
        {"id": "general", "label": {"vi": "Chung", "en": "General"}, "count": cat_counts.get("general", 0)},
        {"id": "platform", "label": {"vi": "Nền tảng & Hệ thống", "en": "Platforms"}, "count": cat_counts.get("platform", 0)},
        {"id": "web", "label": {"vi": "Web & Trình duyệt", "en": "Web & Browser"}, "count": cat_counts.get("web", 0)},
        {"id": "voice", "label": {"vi": "Âm thanh & Voice", "en": "Audio & Voice"}, "count": cat_counts.get("voice", 0)},
        {"id": "other", "label": {"vi": "Khác", "en": "Other"}, "count": cat_counts.get("other", 0)},
    ]
    filtered = []
    ql = q.strip().lower()
    for e in entries:
        c = e.get("category") or "other"
        if category != "all" and c != category:
            continue
        if ql:
            name = e.get("name") or ""
            title = e.get("title") or name
            desc = e.get("description") or ""
            maintainer = e.get("maintainer") or ""
            if ql not in name.lower() and ql not in title.lower() and ql not in desc.lower() and ql not in maintainer.lower():
                continue
        filtered.append(e)

    start = max(0, page) * max(1, limit)
    paged = filtered[start:start + limit]
    return {
        "items": paged,
        "total": len(filtered),
        "page": page,
        "limit": limit,
        "total_pages": (len(filtered) + limit - 1) // limit if limit else 1,
        "categories": categories,
    }


def get_hermes_plugin(name: str) -> dict | None:
    """Tra ve chi tiet mot plugin trong kho Hermes."""
    entries = _load_hermes_catalog()
    clean_name = name.removeprefix("hermes/").strip().lower()
    for e in entries:
        if (e.get("name") or "").lower() == clean_name:
            return e
    return None


def search(q: str, cursor: str = "", limit: int = 30) -> dict:
    """Tra ve ket qua tu kho offline Hermes (uu tien, luon co du mang hay khong) ghep voi
    registry chinh thuc qua mang (best-effort: loi mang khong duoc xoa mat phan offline)."""
    seen, items = set(), []
    if not cursor and q.strip():
        for h in search_hermes(q, limit=max(1, min(limit, 50))):
            if (h["id"], h["url"]) not in seen:
                seen.add((h["id"], h["url"]))
                items.append(h)
    params = {"search": q.strip(), "limit": max(1, min(limit, 50))}
    if cursor:
        params["cursor"] = cursor
    next_cursor = ""
    try:
        r = httpx.get(URL, params=params, timeout=15)
        r.raise_for_status()
        data = r.json()
    except (httpx.HTTPError, ValueError) as e:
        if not items:
            raise RegistryError(f"không truy cập được thư viện MCP: {type(e).__name__}") from e
        data = None
    if data:
        for entry in data.get("servers", []):
            n = _normalize(entry)
            if n and (n["id"], n["url"]) not in seen:
                seen.add((n["id"], n["url"]))
                items.append(n)
        next_cursor = (data.get("metadata") or {}).get("nextCursor") or ""
    return {"items": items, "next": next_cursor}
