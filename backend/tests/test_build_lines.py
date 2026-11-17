from compliance_search.processing.Parsing.build_lines import build_lines


def fragment(x, y, text):
    return {"page_number": 1, "x": x, "y": y, "font": "/Regular",
            "font_size": 1.0, "effective_font_size": 9.6, "bold": False, "text": text}


def test_fragments_with_almost_the_same_y_form_one_line():
    fragments = [
        fragment(x=150, y=100.01, text="Welt"),
        fragment(x=100, y=100.00, text="Hallo"),
        fragment(x=100, y=90.00, text="Nächste Zeile"),
    ]

    lines = build_lines(fragments)

    assert [line["text"] for line in lines] == ["Hallo Welt", "Nächste Zeile"]
