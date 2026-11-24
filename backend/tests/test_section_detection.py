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
