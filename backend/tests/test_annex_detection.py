from compliance_search.processing.parsing.annex_detection import detect_annexes
from compliance_search.processing.sections import SectionLine


def line(text: str) -> SectionLine:
    return SectionLine(
        section_type="annex",
        seq=1,
        page_number=1,
        font_size=9.6,
        font="/Regular",
        bold=False,
        x=42.5,
        y=600,
        text=text,
    )


def test_english_annexes_are_numbered_until_the_next_annex():
    lines = detect_annexes(
        [
            line("ANNEX I"),
            line("Requirements for high-risk systems"),
            line("ANNEX II"),
            line("Union legislation"),
        ]
    )

    assert [item.annex for item in lines] == ["I", "I", "II", "II"]


def test_german_and_arabic_annexes_are_numbered():
    lines = detect_annexes(
        [
            line("ANHANG 1"),
            line("Technische Dokumentation"),
        ]
    )

    assert [item.annex for item in lines] == ["1", "1"]
