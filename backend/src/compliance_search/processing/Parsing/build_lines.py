def build_lines(fragments: list) -> list:

    # 1. Sort: page by page, then from top to bottom
    sorted_fragments = sorted(fragments, key=lambda f: (f["page_number"], -f["y"]))

    # 2. Group: a fragment belongs to the current line if it is on the same page
    #    and at most half its font size away from the line's first fragment
    grouped_fragments = []
    for fragment in sorted_fragments:
        if grouped_fragments:
            first_fragment = grouped_fragments[-1][0]
            tolerance = fragment["font_size"] / 2
            if (fragment["page_number"] == first_fragment["page_number"]
                    and abs(fragment["y"] - first_fragment["y"]) <= tolerance):
                grouped_fragments[-1].append(fragment)
                continue
        grouped_fragments.append([fragment])

    # 3. Build the lines: fragments left to right, numbered per page
    lines = []
    current_page = None
    current_line_number = 0
    for line_fragments in grouped_fragments:
        line_fragments.sort(key=lambda f: f["x"])
        first_fragment = line_fragments[0]

        if first_fragment["page_number"] != current_page:
            current_page = first_fragment["page_number"]
            current_line_number = 0
        current_line_number += 1

        lines.append({
            "page_number": first_fragment["page_number"],
            "line_number": current_line_number,
            "x": first_fragment["x"],
            "y": first_fragment["y"],
            "font": first_fragment["font"],
            "font_size": min(fragment["font_size"] for fragment in line_fragments),
            "bold": any(fragment["bold"] for fragment in line_fragments),
            # Join without a separator (spaces come from the PDF), then
            # collapse runs of whitespace and trim the ends
            "text": " ".join("".join(fragment["text"] for fragment in line_fragments).split())
        })

    return lines
