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


def search_hermes(q: str, limit: int = 10) -> list[dict]:
    """Tim kiem trong kho ~2500 plugin va MCP server cua Hermes da co tren may."""
    catalog_path = _get_hermes_catalog_path()
    if not q or len(q.strip()) < 2 or not catalog_path:
        return []
    try:
        data = json.loads(catalog_path.read_text(errors="replace"))
        entries = data.get("entries", [])
    except Exception:
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


def search(q: str, cursor: str = "", limit: int = 30) -> dict:
    params = {"search": q.strip(), "limit": max(1, min(limit, 50))}
    if cursor:
        params["cursor"] = cursor
    try:
        r = httpx.get(URL, params=params, timeout=15)
        r.raise_for_status()
        data = r.json()
    except (httpx.HTTPError, ValueError) as e:
        raise RegistryError(f"không truy cập được thư viện MCP: {type(e).__name__}") from e
    seen, items = set(), []
    for entry in data.get("servers", []):
        n = _normalize(entry)
        if n and (n["id"], n["url"]) not in seen:
            seen.add((n["id"], n["url"]))
            items.append(n)
    if not cursor and q.strip():
        for h in search_hermes(q, limit=10):
            if (h["id"], h["url"]) not in seen:
                seen.add((h["id"], h["url"]))
                items.append(h)
    return {"items": items, "next": (data.get("metadata") or {}).get("nextCursor") or ""}
