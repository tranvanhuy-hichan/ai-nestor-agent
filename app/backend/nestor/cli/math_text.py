"""Render common LaTeX notation as terminal text inside Markdown."""
import re
from functools import lru_cache
from unicodedata import normalize

from markdown_it import MarkdownIt
from markdown_it.rules_inline import StateInline


_MATH = re.compile(
    r"\$\$(.+?)\$\$|\\\[(.+?)\\\]|\\\(([^\n]+?)\\\)"
    r"|\$(?![\s$])((?:\\[^\n]|[^\\$\n\x60])+?)(?<!\s)\$(?![\d$])",
    re.DOTALL,
)
_SYMBOLS = {
    "times": "×", "cdot": "·", "div": "÷", "pm": "±",
    "le": "≤", "leq": "≤", "ge": "≥", "geq": "≥", "ne": "≠", "neq": "≠",
    "approx": "≈", "sim": "∼", "simeq": "≃", "equiv": "≡", "propto": "∝",
    "infty": "∞", "sum": "∑", "prod": "∏", "int": "∫", "iint": "∬",
    "partial": "∂", "nabla": "∇", "sqrt": "√", "mp": "∓",
    "in": "∈", "notin": "∉", "subset": "⊂", "subseteq": "⊆", "supseteq": "⊇",
    "cup": "∪", "cap": "∩", "emptyset": "∅", "varnothing": "∅",
    "forall": "∀", "exists": "∃", "neg": "¬", "land": "∧", "lor": "∨",
    "to": "→", "rightarrow": "→", "leftarrow": "←", "leftrightarrow": "↔",
    "Rightarrow": "⇒", "Leftarrow": "⇐", "Leftrightarrow": "⇔", "mapsto": "↦",
    "implies": "⇒", "iff": "⇔",
    "ldots": "…", "dots": "…", "cdots": "⋯",
    "langle": "⟨", "rangle": "⟩", "lfloor": "⌊", "rfloor": "⌋",
    "lceil": "⌈", "rceil": "⌉", "Vert": "‖", "mid": "∣",
    "left": "", "right": "", "middle": "", "limits": "", "nolimits": "", "bmod": "mod",
    ",": " ", ":": " ", ";": " ", "!": "", " ": " ", "quad": " ", "qquad": " ",
    **{char: char for char in "%_{}$&#"},
}
_GREEK = dict(zip(
    "alpha beta gamma delta epsilon zeta eta theta iota kappa lambda mu nu xi omicron pi rho sigma tau upsilon phi chi psi omega".split(),
    "αβγδεζηθικλμνξοπρστυφχψω",
))
_SYMBOLS.update(_GREEK)
_SYMBOLS.update({name.title(): _GREEK[name].upper()
                 for name in "gamma delta theta lambda xi pi sigma upsilon phi psi omega".split()})
_SYMBOLS.update(varepsilon="ϵ", vartheta="ϑ", varphi="ϕ", varrho="ϱ", varsigma="ς")
_OPERATORS = frozenset(
    "max min lim limsup liminf sup inf argmax argmin log ln lg exp sin cos tan cot sec csc "
    "arcsin arccos arctan sinh cosh tanh det dim gcd lcm mod ker deg Pr".split()
)
_COMMAND = re.compile(r"\\([A-Za-z]+|[,;: !%_{}$&#])")
_GROUP_BODY = r"((?:[^{}]|[_^]\{[^{}]+\})+)"
_GROUPED = re.compile(
    rf"(?<!\\)\\(?:(?P<pair>[dt]?frac|[dt]?binom)\s*\{{{_GROUP_BODY}\}}\s*\{{{_GROUP_BODY}\}}"
    r"|(?P<root>sqrt)\s*(?:\[([^\[\]{}]+)\]\s*)?\{([^{}]+)\}"
    r"|(?:operatorname\*?|text|mathrm|mathbf|mathit|mathsf|mathtt|boldsymbol|textbf)\s*\{([^{}]+)\}"
    r"|mathbb\s*\{([NZQRCHP])\}"
    r"|hat\s*\{([^{}])\})"
)
_BARE_COMMANDS = {"frac": 2, "dfrac": 2, "tfrac": 2, "hat": 1}
_COMMAND_NAME = re.compile(r"\\([A-Za-z]*)")
_NUMBER_SETS = dict(zip("NZQRCHP", "ℕℤℚℝℂℍℙ"))
_ALIGNMENT = re.compile(
    r"\\begin\{(aligned|gathered|split|cases|[pbBvV]?matrix)\}(.*?)\\end\{\1\}", re.DOTALL
)
_ROW_BREAK = re.compile(r"\\\\(?:\s*\[[^\]\n]+\])?")
_UNESCAPED_AMPERSAND = re.compile(r"(?<!\\)&")
_MATRIX_DELIMITERS = {
    "matrix": ("[", "]"), "pmatrix": ("(", ")"), "bmatrix": ("[", "]"),
    "Bmatrix": ("{", "}"), "vmatrix": ("|", "|"), "Vmatrix": ("‖", "‖"),
}
_SCRIPT = re.compile(r"(?<!\\)([_^])(?:\{([^{}]+)\}|([A-Za-z0-9]))")
_SUPERSCRIPT = str.maketrans("0123456789+-=()in", "⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁼⁽⁾ⁱⁿ")
_SUBSCRIPT = str.maketrans("0123456789+-=()aeioruvx", "₀₁₂₃₄₅₆₇₈₉₊₋₌₍₎ₐₑᵢₒᵣᵤᵥₓ")


def _script(match: re.Match) -> str:
    marker, group, single = match.groups()
    value = group if group is not None else single
    table = _SUPERSCRIPT if marker == "^" else _SUBSCRIPT
    if all(ord(character) in table for character in value):
        return value.translate(table)
    return f"{marker}({value})" if group is not None else match[0]


def _grouped(match: re.Match) -> str:
    pair, first, second, root, index, radicand, text, number_set, hat = match.groups()
    if pair:
        return f"({first})/({second})" if pair.endswith("frac") else f"({first} choose {second})"
    if root:
        return f"√[{index}]({radicand})" if index else f"√({radicand})"
    if hat is not None:
        return normalize("NFC", hat + "\u0302")
    return text if text is not None else _NUMBER_SETS[number_set]


def _command(match: re.Match) -> str:
    name = match[1]
    return name if name in _OPERATORS else _SYMBOLS.get(name, match[0])


def _alignment(match: re.Match) -> str:
    environment, body = match.groups()
    rows = _ROW_BREAK.split(body)
    if environment in _MATRIX_DELIMITERS:
        left, right = _MATRIX_DELIMITERS[environment]
        content = "; ".join(", ".join(cell.strip() for cell in _UNESCAPED_AMPERSAND.split(row))
                            for row in rows if row.strip())
        return f"{left}{content}{right}"
    content = "; ".join(_UNESCAPED_AMPERSAND.sub(" ", row).strip() for row in rows if row.strip())
    return f"{{{content}}}" if environment == "cases" else content


def _render_math(match: re.Match) -> str:
    source = next(group for group in match.groups() if group is not None)
    return _render_source(source)


def _render_source(source: str) -> str:
    source = _ALIGNMENT.sub(_alignment, source)
    source = re.sub(r"\\(?:left|right)\s*\.", "", source)
    while _GROUPED.search(source):
        source = _GROUPED.sub(_grouped, source)
    rendered = _COMMAND.sub(_command, _SCRIPT.sub(_script, source))
    return " ".join(rendered.split())


def _bare_math_end(source: str, start: int, end: int) -> int:
    """Return the end of a bare math command, start if invalid, or -1 if incomplete."""
    command = _COMMAND_NAME.match(source, start, end)
    name = command[1]
    pos = command.end()
    if pos == end and any(candidate.startswith(name) for candidate in _BARE_COMMANDS):
        return -1
    for _ in range(_BARE_COMMANDS.get(name, 0)):
        while pos < end and source[pos] in " \t":
            pos += 1
        if pos == end:
            return -1
        if source[pos] != "{":
            return start
        group_start = pos + 1
        depth = 1
        pos += 1
        while pos < end and depth:
            char = source[pos]
            if char in "\n\x60":
                return start
            if char == "\\" and pos + 1 < end and source[pos + 1] in "{}":
                pos += 2
                continue
            depth += (char == "{") - (char == "}")
            pos += 1
        if depth:
            return -1
        if pos == group_start + 1 or (name == "hat" and pos != group_start + 2):
            return start
    return pos if name in _BARE_COMMANDS else start


_STREAM_SPECIAL = re.compile(r"[\x60\\$\n]")
_FENCE = re.compile(r" {0,3}(~{3,}|\x60{3,})")
_FENCE_PREFIX = re.compile(r" {0,3}(?:~{0,2}|\x60{0,2})")
_INDENTED = re.compile(r" {4}| {0,3}\t")


class MathStream:
    """Format complete math spans as they arrive, preserving Markdown source elsewhere."""

    def __init__(self):
        self.pending = ""
        self.line_start = True
        self.fence = ""
        self.fence_partial: str | None = None
        self.code = ""

    def feed(self, text: str, *, final: bool = False) -> str:
        source = self.pending + text
        output = []
        pos = 0
        while pos < len(source):
            end = self._next(source, pos, final)
            if end is None:
                break
            stop, rendered = end
            output.append(rendered)
            self.line_start = source[stop - 1] == "\n"
            pos = stop
        self.pending = source[pos:]
        return "".join(output)

    def _next(self, source: str, pos: int, final: bool) -> tuple[int, str] | None:
        if self.fence or (self.line_start and not self.code):
            line_end = source.find("\n", pos)
            stop = len(source) if line_end < 0 else line_end + 1
            line = source[pos:stop]
            if self.fence:
                full_line = (self.fence_partial or "") + line
                if line_end < 0 and not final:
                    self.fence_partial = full_line
                    return stop, line
                self.fence_partial = None
                marker = _FENCE.match(full_line)
                if marker and marker[1].startswith(self.fence) and not full_line[marker.end():].strip():
                    self.fence = ""
                return stop, line
            marker = _FENCE.match(line)
            if marker:
                if line_end < 0 and not final:
                    return None
                self.fence = marker[1]
                return stop, line
            if _INDENTED.match(line):
                return (stop, line) if line_end >= 0 or final else None
            if line_end < 0 and not final and _FENCE_PREFIX.fullmatch(line):
                return None

        special = _STREAM_SPECIAL.search(source, pos)
        if special is None or special.start() > pos:
            stop = special.start() if special else len(source)
            return stop, source[pos:stop]

        char = source[pos]
        if char == "\x60":
            stop = pos + 1
            while stop < len(source) and source[stop] == char:
                stop += 1
            if stop == len(source) and not final:
                return None
            marker = source[pos:stop]
            if not self.code:
                self.code = marker
            elif self.code == marker:
                self.code = ""
            return stop, marker
        if self.code or char == "\n":
            return pos + 1, char

        if char == "\\" and not source.startswith(("\\(", "\\["), pos):
            end = _bare_math_end(source, pos, len(source))
            if end > pos:
                return end, _render_source(source[pos:end])
            if end == -1 and not final and len(source) - pos < 4096:
                return None
            stop = min(pos + 2, len(source))
            return stop, source[pos:stop]

        match = _MATH.match(source, pos)
        if match and (not match[4] or pos == 0 or source[pos - 1] != "$"):
            if match[4] and match.end() == len(source) and not final:
                return None
            return match.end(), _render_math(match)
        display = source.startswith(("$$", "\\["), pos)
        if not final and len(source) - pos < 4096:
            if display or (re.search(r"[\n\x60]", source[pos:]) is None and
                           not (char == "$" and source[pos + 1:pos + 2].isspace())):
                return None
        return pos + 1, char


def _math_inline(state: StateInline, silent: bool) -> bool:
    match = _MATH.match(state.src, state.pos, state.posMax)
    if match and (not match[4] or not state.pos or state.src[state.pos - 1] != "$"):
        end, rendered = match.end(), _render_math(match)
    elif state.src[state.pos] == "\\":
        end = _bare_math_end(state.src, state.pos, state.posMax)
        if end <= state.pos:
            return False
        rendered = _render_source(state.src[state.pos:end])
    else:
        return False
    if not silent:
        state.push("text", "", 0).content = rendered
    state.pos = end
    return True


@lru_cache(maxsize=1)
def math_markdown_parser() -> MarkdownIt:
    parser = MarkdownIt().enable("strikethrough").enable("table")
    parser.inline.ruler.before("escape", "terminal_math", _math_inline)
    return parser
