from compliance_search.processing.chunking.build_chunks import build_chunks
from compliance_search.processing.chunking.group_units import group_units, join_lines
from compliance_search.processing.sections import SectionLine

METADATA = {"id": "32025R0301_EN", "family_id": "32025R0301", "version_date": "2024-10-23",
            "language": "EN", "doc_type": "delegated_regulation", "title": "Delegated Regulation (EU) 2025/301"}


def line(text, section_type="enacting_terms", article=None, recital=None, bold=False, page=2):
    return SectionLine(section_type=section_type, article=article, recital=recital, seq=1, page_number=page,
                       font_size=9.6, font="/Regular", bold=bold, x=68, y=500, text=text)


def chunks(lines):
    return build_chunks(group_units(lines), METADATA)


# Does one article become one chunk with its label, title and text?
def test_article_becomes_one_chunk():
    lines = [line("Article 5", article="5"), line("Time limits", article="5", bold=True),
             line("The initial notification shall", article="5"), line("be submitted.", article="5")]

    [chunk] = chunks(lines)

    assert (chunk.label, chunk.title, chunk.text) == ("Article 5", "Time limits", "The initial notification shall be submitted.")


# Does one recital become one chunk without its "(N)"?
def test_recital_becomes_one_chunk():
    lines = [line("Whereas:", section_type="recitals"),
             line("(1) To ensure harmonisation,", section_type="recitals", recital="1")]

    [chunk] = chunks(lines)

    assert (chunk.label, chunk.text) == ("Recital 1", "To ensure harmonisation,")


# Is a footnote left out without ending the article?
def test_footnote_is_left_out():
    lines = [line("Article 2", article="2"), line("first page", article="2", page=2),
             line("(1) OJ L 333, 27.12.2022, p. 1.", section_type="footnotes", page=2),
             line("second page", article="2", page=3)]

    [chunk] = chunks(lines)

    assert (chunk.text, chunk.page_start, chunk.page_end) == ("first page second page", 2, 3)


# Does the embedding text start with document, chapter and article title?
def test_context_line_names_chapter_and_article():
    lines = [line("CHAPTER I"), line("GENERAL PROVISIONS", bold=True),
             line("Article 1", article="1"), line("Subject matter", article="1", bold=True),
             line("This Regulation lays down", article="1")]

    [chunk] = chunks(lines)

    assert chunk.embedding_text == ("Delegated Regulation (EU) 2025/301 | CHAPTER I GENERAL PROVISIONS | "
                                    "Article 1 – Subject matter\nThis Regulation lays down")


# Does a new chapter clear the section of the chapter before?
def test_new_chapter_clears_the_section():
    lines = [line("CHAPTER I"), line("Section 1"), line("Article 1", article="1"), line("text", article="1"),
             line("CHAPTER II"), line("Article 2", article="2"), line("text", article="2")]

    assert [chunk.headings for chunk in chunks(lines)] == [["CHAPTER I", "Section 1"], ["CHAPTER II"]]


# Is a hyphen at a line end joined into one word, but kept open before "und"?
def test_hyphen_at_line_end():
    assert join_lines(["critical ICT third-", "party provider"]) == "critical ICT third-party provider"
    assert join_lines(["Audit-", "und Aufsichtsrechte"]) == "Audit- und Aufsichtsrechte"
