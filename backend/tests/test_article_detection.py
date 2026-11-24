from compliance_search.processing.parsing.article_detection import detect_articles
from compliance_search.processing.sections import SectionLine


def line(text, section_type="enacting_terms"):
    return SectionLine(section_type=section_type, seq=1, page_number=2, font_size=9.6,
                       font="/Regular", bold=False, x=42.5, y=500, text=text)


def articles(lines):
    return [l.article for l in detect_articles(lines)]


# Does an "Article 1" line label itself and the lines after it?
def test_article_line_starts_the_article():
    lines = [line("Article 1"), line("Subject matter"), line("This Regulation lays down")]

    assert articles(lines) == ["1", "1", "1"]


# Does the German "Artikel 2" work the same way?
def test_german_article_line_starts_the_article():
    assert articles([line("Artikel 2"), line("Begriffsbestimmungen")]) == ["2", "2"]


# Does a "CHAPTER II" line end the article before it?
def test_chapter_heading_ends_the_article():
    lines = [line("Article 3"), line("last sentence."), line("CHAPTER II"), line("GOVERNANCE"),
             line("Article 4")]

    assert articles(lines) == ["3", "3", None, None, "4"]


# Does an article run on past a footnote at a page break?
def test_article_runs_on_past_a_footnote():
    lines = [line("Article 5"), line("(1) OJ L 333, 27.12.2022, p. 1.", section_type="footnotes"),
             line("continued on the next page")]

    assert articles(lines) == ["5", None, "5"]


# Does a reference to an article in running text leave the article unchanged?
def test_reference_in_running_text_is_no_article_heading():
    lines = [line("Article 6"), line("Article 8(1) of Regulation (EU) 2022/2554")]

    assert articles(lines) == ["6", "6"]


# Do lines outside enacting_terms stay None?
def test_lines_outside_enacting_terms_stay_none():
    assert articles([line("Article 1", section_type="recitals")]) == [None]
