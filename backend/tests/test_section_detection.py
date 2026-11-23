from compliance_search.processing.parsing.article_detection import detect_articles
from compliance_search.processing.parsing.section_detection import detect_sections
from compliance_search.processing.sections import SectionLine


def line(text):
    return SectionLine(seq=1, page_number=2, font_size=9.6, font="/Regular", bold=False,
                       x=42.5, y=600, text=text)


# Does the binding clause start the final formula, so the last article ends before it?
def test_binding_clause_is_final_formula_not_last_article():
    lines = detect_articles(detect_sections([
        line("HAS ADOPTED THIS REGULATION:"),
        line("Article 13"),
        line("This Regulation shall enter into force on the twentieth day."),
        line("This Regulation shall be binding in its entirety and directly applicable in all Member States."),
        line("Done at Brussels, 13 March 2024."),
    ]))

    assert [(l.section_type, l.article) for l in lines[1:]] == [
        ("enacting_terms", "13"),
        ("enacting_terms", "13"),
        ("final_formula", None),
        ("final_formula", None),
    ]


def test_english_regulation_sections_and_annex_are_detected():
    lines = [
        SectionLine(seq=1, page_number=1, font_size=9.6, font="/Regular", bold=False,
                    x=42.5, y=600, text="REGULATION (EU) 2022/2554"),
        SectionLine(seq=2, page_number=1, font_size=9.6, font="/Regular", bold=False,
                    x=42.5, y=590,
                    text="THE EUROPEAN PARLIAMENT AND THE COUNCIL OF THE EUROPEAN UNION,"),
        SectionLine(seq=3, page_number=1, font_size=9.6, font="/Regular", bold=False,
                    x=42.5, y=580, text="Whereas:"),
        SectionLine(seq=4, page_number=1, font_size=9.6, font="/Regular", bold=False,
                    x=42.5, y=570, text="HAVE ADOPTED THIS REGULATION:"),
        SectionLine(seq=5, page_number=2, font_size=9.6, font="/Regular", bold=False,
                    x=42.5, y=600, text="Article 1"),
        SectionLine(seq=6, page_number=2, font_size=9.6, font="/Regular", bold=False,
                    x=42.5, y=590, text="Subject matter"),
        SectionLine(seq=7, page_number=79, font_size=9.6, font="/Regular", bold=False,
                    x=42.5, y=600, text="Done at Strasbourg, 14 December 2022."),
        SectionLine(seq=8, page_number=80, font_size=9.6, font="/Regular", bold=False,
                    x=42.5, y=600, text="ANNEX I"),
        SectionLine(seq=9, page_number=80, font_size=9.6, font="/Regular", bold=False,
                    x=42.5, y=590, text="Requirements"),
    ]

    detected = detect_articles(
        detect_sections(lines, document_type="regulation")
    )

    assert [line.section_type for line in detected] == [
        "header",
        "citations",
        "recitals",
        "enacting_formula",
        "enacting_terms",
        "enacting_terms",
        "final_formula",
        "annex",
        "annex",
    ]
    assert detected[4].article == "1"
    assert detected[8].article is None


def test_german_regulation_formulas_are_detected():
    lines = [
        SectionLine(seq=1, page_number=1, font_size=9.6, font="/Regular", bold=False,
                    x=42.5, y=600,
                    text="DAS EUROPÄISCHE PARLAMENT UND DER RAT DER EUROPÄISCHEN UNION —"),
        SectionLine(seq=2, page_number=1, font_size=9.6, font="/Regular", bold=False,
                    x=42.5, y=590, text="in Erwägung nachstehender Gründe:"),
        SectionLine(seq=3, page_number=1, font_size=9.6, font="/Regular", bold=False,
                    x=42.5, y=580, text="HABEN FOLGENDE VERORDNUNG ERLASSEN:"),
        SectionLine(seq=4, page_number=2, font_size=9.6, font="/Regular", bold=False,
                    x=42.5, y=600, text="Artikel 1"),
        SectionLine(seq=5, page_number=79, font_size=9.6, font="/Regular", bold=False,
                    x=42.5, y=600, text="Geschehen zu Straßburg am 14. Dezember 2022."),
    ]

    detected = detect_sections(lines, document_type="regulation")

    assert detected[0].section_type == "citations"
    assert detected[1].section_type == "recitals"
    assert detected[2].section_type == "enacting_formula"
    assert detected[3].section_type == "enacting_terms"
    assert detected[4].section_type == "final_formula"
