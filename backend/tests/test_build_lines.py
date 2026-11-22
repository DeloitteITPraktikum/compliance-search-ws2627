from compliance_search.processing.parsing.build_lines import build_lines
from compliance_search.processing.sections import TextFragment


def fragment(x, y, text):
    return TextFragment(page_number=1, x=x, y=y, font="/Regular",
                        font_size=9.6, bold=False, text=text)


def test_fragments_with_almost_the_same_y_form_one_line():
    fragments = [
        fragment(x=150, y=100.01, text="Welt"),
        fragment(x=100, y=100.00, text="Hallo "),
        fragment(x=100, y=90.00, text="Nächste Zeile"),
    ]

    lines = build_lines(fragments)

    assert [line.text for line in lines] == ["Hallo Welt", "Nächste Zeile"]


def test_spaces_come_only_from_the_fragments():
    fragments = [
        fragment(x=100, y=100, text="2016/1011 "),
        fragment(x=140, y=100, text="("),
        fragment(x=143, y=100, text="1"),
        fragment(x=146, y=100, text=")"),
        fragment(x=149, y=100, text=", in"),
    ]

    lines = build_lines(fragments)

    assert lines[0].text == "2016/1011 (1), in"
