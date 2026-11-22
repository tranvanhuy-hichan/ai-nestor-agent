"""Render common LaTeX notation as terminal text inside Markdown."""
import re
from functools import lru_cache

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
    "approx": "≈", "infty": "∞", "sum": "∑", "prod": "∏", "sqrt": "√",
    "alpha": "α", "beta": "β", "gamma": "γ", "delta": "δ", "theta": "θ",
    "lambda": "λ", "mu": "μ", "pi": "π", "sigma": "σ", "omega": "ω",
    "in": "∈", "notin": "∉", "to": "→", "rightarrow": "→",
    ",": " ", ";": " ", "!": "", "quad": " ", "qquad": "  ",
    **{char: char for char in "%_{}$"},
}
_COMMAND = re.compile(r"\\([A-Za-z]+|[,;!%_{}$])")


def _math_inline(state: StateInline, silent: bool) -> bool:
    match = _MATH.match(state.src, state.pos, state.posMax)
    if match is None or (match[4] and state.pos and state.src[state.pos - 1] == "$"):
        return False
    if not silent:
        source = next(group for group in match.groups() if group is not None)
        rendered = _COMMAND.sub(lambda command: _SYMBOLS.get(command[1], command[0]), source)
        state.push("text", "", 0).content = " ".join(rendered.split())
    state.pos = match.end()
    return True


@lru_cache(maxsize=1)
def math_markdown_parser() -> MarkdownIt:
    parser = MarkdownIt().enable("strikethrough").enable("table")
    parser.inline.ruler.before("escape", "terminal_math", _math_inline)
    return parser
