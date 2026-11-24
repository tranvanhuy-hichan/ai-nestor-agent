"""Render CommonMark as balanced chunks of Telegram-compatible HTML."""
from html import escape
from html.parser import HTMLParser

from markdown_it import MarkdownIt

_MARKDOWN = MarkdownIt("commonmark", {"html": False}).enable(("strikethrough", "table"))
_INLINE = {"strong": "b", "em": "i", "s": "s", "code": "code", "pre": "pre",
           **{f"h{level}": "b" for level in range(1, 7)}}


class _TelegramHTML(HTMLParser):
    def __init__(self, limit: int):
        super().__init__()
        self.limit = limit
        self.parts: list[tuple[str, str]] = []
        self.tags: list[tuple[str, str, str]] = []
        self.lists: list[int | None] = []
        self.formatted: list[str] = []
        self.plain: list[str] = []
        self.size = 0

    def flush(self):
        plain = "".join(self.plain)
        if plain.strip():
            self.parts.append(("".join(self.formatted) + "".join(close for _, _, close in reversed(self.tags)), plain))
        self.formatted = [opening for _, opening, _ in self.tags]
        self.plain = []
        self.size = 0

    def handle_data(self, data):
        while data:
            segment = data[: (self.limit - self.size) // 2]
            if not segment:
                self.flush()
                continue
            self.plain.append(segment)
            self.formatted.append(escape(segment, quote=False))
            self.size += len(segment.encode("utf-16-le")) // 2
            data = data[len(segment):]

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        mapped = _INLINE.get(tag)
        opening = f"<{mapped}>" if mapped else ""
        if tag == "code" and self.tags and self.tags[-1][0] == "pre":
            language = attrs.get("class", "")
            if language.startswith("language-") and language[9:].replace("-", "").replace("_", "").isalnum():
                opening = f'<code class="{escape(language, quote=True)}">'
        if tag == "a":
            href = attrs.get("href", "")
            if href.startswith(("https://", "http://", "mailto:")):
                opening, mapped = f'<a href="{escape(href, quote=True)}">', "a"
        if opening:
            self.formatted.append(opening)
            self.tags.append((tag, opening, f"</{mapped}>"))
        elif tag == "br":
            self.handle_data("\n")
        elif tag == "img":
            self.handle_data(attrs.get("alt", ""))
        elif tag in ("ul", "ol"):
            self.lists.append(int(attrs.get("start", "1")) if tag == "ol" else None)
        elif tag == "li" and self.lists:
            index = self.lists[-1]
            self.handle_data("  " * (len(self.lists) - 1) + ("• " if index is None else f"{index}. "))
            if index is not None:
                self.lists[-1] += 1
        elif tag == "blockquote":
            self.handle_data("▎ ")
        elif tag == "hr":
            self.handle_data("────────\n")

    def handle_endtag(self, tag):
        if self.tags and self.tags[-1][0] == tag:
            self.formatted.append(self.tags.pop()[2])
        if tag in ("ul", "ol"):
            self.lists.pop()
        elif tag in ("td", "th"):
            self.handle_data(" │ ")
        elif tag == "p" or (tag.startswith("h") and tag[1:].isdigit()):
            self.handle_data("\n")
        # The Markdown renderer already emits line breaks after block and list elements.

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)


def formatted_chunks(text: str, limit: int = 4000) -> list[tuple[str, str]]:
    parser = _TelegramHTML(limit)
    parser.feed(_MARKDOWN.render(text))
    parser.close()
    parser.flush()
    return parser.parts
