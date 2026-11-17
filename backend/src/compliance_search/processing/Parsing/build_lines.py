from collections import defaultdict

def build_lines(fragments: list) -> list:
    
    grouped_fragments = defaultdict(list)

    for fragment in fragments:
        line_key = (fragment["page_number"], round(fragment["y"], 3))
        grouped_fragments[line_key].append(fragment)

    lines = []
    for _, line_fragments in grouped_fragments.items():
        line_fragments.sort(key=lambda f: f["x"])
        text = " ".join(fragment["text"] for fragment in line_fragments)
        first_fragment = line_fragments[0]
        lines.append({
            "page_number": first_fragment["page_number"],
            "line_number": 0,
            "x": min(fragment["x"]
                for fragment in line_fragments),
            "y": first_fragment["y"],
            "font": first_fragment["font"],
            "font_size": min(fragment["font_size"]
                for fragment in line_fragments),
            "real_font_size": min(fragment["effective_font_size"]
                for fragment in line_fragments),
            "bold": any(fragment["bold"] for fragment in line_fragments),
            "text": text
        })
    
    lines.sort(key=lambda line: (line["page_number"], -line["y"]))

    current_page = None
    current_line_number = 0
    for line in lines:
        if line["page_number"] != current_page:
            current_page = line["page_number"]
            current_line_number = 1
        else:
            current_line_number += 1

        line["line_number"] = current_line_number
        
        
        
        
    return lines