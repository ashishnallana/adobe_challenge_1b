import re
from collections import defaultdict

def detect_headings_and_levels(lines):
    # Detect headings and assign levels using font size, bold, and numbering rules
    size_frequency = defaultdict(int)
    for line in lines:
        size_frequency[line["size"]] += 1
    most_frequent_size = max(size_frequency, key=size_frequency.get) if size_frequency else 12
    headings = []
    for line in lines:
        text = line["text"].strip()
        test_font = line["size"] > most_frequent_size
        test_bold = line["bold"] and all(c.isalpha() or c.isspace() or c in ",.:-()[]{}'\"" for c in text)
        test_numbering = bool(re.match(r'^\d+(\.\d+)+[\.\)\-\s]', text))
        forbidden_endings = (':', '-', '\u2013', '\u2014', '\u2212', '\u2015', '\u2022', '\u25AA', '\u25CF', '\u25A0')
        if any(text.endswith(p) for p in forbidden_endings):
            continue
        if test_font or test_bold or test_numbering:
            headings.append(line)
    # Merge consecutive headings with same properties
    merged_headings = []
    for heading in headings:
        if merged_headings:
            prev = merged_headings[-1]
            if (heading["font"] == prev["font"] and heading["size"] == prev["size"] and heading["bold"] == prev["bold"] and heading["page"] == prev["page"]):
                prev["text"] = prev["text"].rstrip() + " " + heading["text"].lstrip()
                continue
        merged_headings.append(heading)
    headings = merged_headings
    if not headings:
        return None, [], [], most_frequent_size
    title = headings[0]["text"].strip()
    outline = []
    heading_indexes = [i for i, line in enumerate(lines) if line in headings]
    prev_heading_idx = heading_indexes[0] if heading_indexes else None
    prev_size = headings[1]["size"] if len(headings) > 1 else None
    prev_level = 1
    level_stack = [headings[1]["size"]] if len(headings) > 1 else []
    for idx, heading in enumerate(headings[1:]):
        size = heading["size"]
        curr_heading_idx = heading_indexes[idx+1]
        if prev_heading_idx is not None and all(l in headings for l in lines[prev_heading_idx+1:curr_heading_idx]):
            level = 1
            level_stack = [size]
        else:
            if idx == 0:
                level = 1
                level_stack = [size]
            else:
                if size == prev_size:
                    level = prev_level
                elif size < prev_size:
                    if prev_level < 3:
                        level = prev_level + 1
                        level_stack.append(size)
                    else:
                        level = 3
                        if len(level_stack) < 3:
                            level_stack.append(size)
                elif size > prev_size:
                    found = False
                    for l, s in enumerate(level_stack):
                        if size == s:
                            level = l + 1
                            found = True
                            break
                    if not found:
                        level = 1
                        level_stack = [size]
                    else:
                        level_stack = level_stack[:level]
        outline.append({
            "level": f"H{level}",
            "text": heading["text"].strip(),
            "page": heading["page"]
        })
        prev_size = size
        prev_level = level
        prev_heading_idx = curr_heading_idx
    return title, outline, headings, most_frequent_size 