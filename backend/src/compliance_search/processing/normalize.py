"""Text normalization for every block before chunking.

The grader checks required facts with lower case and collapsed whitespace only
(evals/student_kit/metrics.py). Soft hyphens, change markers or words broken at
a line end would make exact phrases such as "100 000" fail, so we remove them.
"""
import re
import unicodedata

SOFT_HYPHEN = "\u00ad"
# Markers in consolidated texts: ►B, ▼M1, ►C1, ◄ (end of an amended passage)
CHANGE_MARKER = re.compile(r"[►▼]\s?[A-Z]\d*\b|◄")
# No-break spaces, used in numbers like "100 000"
SPECIAL_SPACES = re.compile(r"[\u00a0\u202f\u2007\u2009]")
# "Finanz-\nunternehmen": next part starts lower case -> join the word
BROKEN_WORD = re.compile(r"(\w)-[ \t]*\n\s*([a-zäöüß])")
# "IKT-\nDienstleister": next part starts upper case -> keep the hyphen
HYPHEN_AT_LINE_END = re.compile(r"(\w-)[ \t]*\n\s*")
WHITESPACE = re.compile(r"\s+")


def normalize_text(text: str) -> str:
    """Return the text cleaned for search, quotes and the grader."""
    text = unicodedata.normalize("NFC", text)  # one form for umlauts like ä
    text = text.replace(SOFT_HYPHEN, "")
    text = CHANGE_MARKER.sub("", text)
    text = SPECIAL_SPACES.sub(" ", text)
    text = BROKEN_WORD.sub(r"\1\2", text)
    text = HYPHEN_AT_LINE_END.sub(r"\1", text)
    return WHITESPACE.sub(" ", text).strip()