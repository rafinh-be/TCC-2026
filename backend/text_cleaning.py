import re

MATH_SPAN_PATTERN = re.compile(r"\$([^$]+)\$")
TEXT_COMMAND_PATTERN = re.compile(r"\\text\{([^}]*)\}")
REPEATED_SPACES_PATTERN = re.compile(r" {2,}")
SYMBOL_REPLACEMENTS = (
    (re.compile(r"\^\\circ(?![a-zA-Z])"), "°"),
    (re.compile(r"\\ge(?![a-zA-Z])"), ">="),
    (re.compile(r"\\le(?![a-zA-Z])"), "<="),
    (re.compile(r"\\mu(?![a-zA-Z])"), "µ"),
)


def _clean_math_span(match):
    span = TEXT_COMMAND_PATTERN.sub(r"\1", match.group(1))
    for pattern, replacement in SYMBOL_REPLACEMENTS:
        span = pattern.sub(replacement, span)
    return REPEATED_SPACES_PATTERN.sub(" ", span)


def clean_latex_math(text):
    if not text:
        return text
    return MATH_SPAN_PATTERN.sub(_clean_math_span, text)
