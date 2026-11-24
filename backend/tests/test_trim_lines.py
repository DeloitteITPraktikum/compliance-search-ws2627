from compliance_search.processing.parsing.trim_lines import trim_lines
from compliance_search.processing.sections import SectionLine


def line(y, text):
    return SectionLine(seq=1, page_number=2, font_size=9.6, font="/Regular",
                       bold=False, x=42.5, y=y, text=text)


# Are the running header and the ELI footer removed?
def test_running_header_and_footer_are_removed():
    lines = [
        line(y=783.6, text="EN OJ L, 20.2.2025"),
        line(y=744.8, text="(6) Since significant cyber threats are to be notified"),
        line(y=22.5, text="2/5 ELI: http://data.europa.eu/eli/reg_del/2025/301/oj"),
    ]

    assert [l.text for l in trim_lines(lines)] == [
        "(6) Since significant cyber threats are to be notified",
    ]


# Is the old-layout running header removed as well?
def test_old_layout_running_header_is_removed():
    lines = [line(y=784.4, text="28.1.2016 L 21/3 Official Journal of the European Union EN")]

    assert trim_lines(lines) == []


# Is the longer running header on page 1 removed as well?
def test_page_1_running_header_is_removed():
    lines = [
        line(y=795.3, text="Official Journal EN"),
        line(y=784.7, text="of the European Union L series"),
    ]

    assert trim_lines(lines) == []
