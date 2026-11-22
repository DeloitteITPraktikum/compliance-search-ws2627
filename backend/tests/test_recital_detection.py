from compliance_search.processing.parsing.recital_detection import detect_recitals
from compliance_search.processing.sections import SectionLine


def line(text, section_type="recitals"):
    return SectionLine(section_type=section_type, seq=1, page_number=1, font_size=9.6,
                       font="/Regular", bold=False, x=68, y=500, text=text)


def recitals(lines):
    return [l.recital for l in detect_recitals(lines)]


# Does a "(1) ..." line label itself and the lines after it?
def test_recital_line_starts_the_recital():
    lines = [line("(1) Regulation (EU) 2022/2554 lays down"), line("rules on ICT risk.")]

    assert recitals(lines) == ["1", "1"]


# Does the introduction line before recital 1 stay None?
def test_introduction_line_stays_none():
    assert recitals([line("Whereas:"), line("(1) The first recital")]) == [None, "1"]


# Does a recital run on past a footnote at a page break?
def test_recital_runs_on_past_a_footnote():
    lines = [line("(2) The second recital"), line("(1) OJ L 333, 27.12.2022, p. 1.", section_type="footnotes"),
             line("continued on the next page")]

    assert recitals(lines) == ["2", None, "2"]


# Does a "(3)" inside the running text leave the recital unchanged?
def test_number_inside_running_text_is_no_recital_start():
    lines = [line("(2) The second recital"), line("as referred to in point (3) of Article 1")]

    assert recitals(lines) == ["2", "2"]


# Do lines outside recitals stay None?
def test_lines_outside_recitals_stay_none():
    assert recitals([line("(1) The first recital", section_type="enacting_terms")]) == [None]
