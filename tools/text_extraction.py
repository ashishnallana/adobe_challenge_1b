import re
from collections import defaultdict

def is_complete_text_line(text, spans):
    if not text or len(text.strip()) < 2:
        return False
    if len(text.strip()) < 3:
        return False
    letters = sum(c.isalpha() for c in text)
    total_chars = len(text.replace(' ', ''))
    if total_chars > 0 and letters / total_chars < 0.3:
        return False
    symbols = sum(c in '.,()[]{}|+-*/:;$%@#&' for c in text)
    if total_chars > 0 and symbols / total_chars > 0.4:
        return False
    if len(spans) > 12:
        return False
    words = text.split()
    meaningful_words = [w for w in words if len(w) > 1]
    if len(words) > 2 and len(meaningful_words) / len(words) < 0.3:
        return False
    return True

def extract_text_lines(doc):
    lines = []
    total_pages = len(doc)
    for page_num, page in enumerate(doc, start=1):
        page_width = page.rect.width
        page_lines = []
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            block_type = block.get("type", 0)
            if block_type != 0:
                continue
            if "lines" in block:
                for line in block["lines"]:
                    if line["spans"]:
                        line_text = "".join(span["text"] for span in line["spans"]).strip()
                        if not is_complete_text_line(line_text, line["spans"]):
                            continue
                        first_span = line["spans"][0]
                        line_left = min(span["origin"][0] for span in line["spans"])
                        line_top = first_span["origin"][1]
                        line_bbox = line["bbox"]
                        left_space = line_left
                        right_space = page_width - line_bbox[2]
                        is_bold = all("Bold" in span["font"] or "bold" in span["font"] for span in line["spans"])
                        sizes = [span["size"] for span in line["spans"]]
                        line_size = max(set(sizes), key=sizes.count)
                        fonts = [span["font"] for span in line["spans"]]
                        line_font = max(set(fonts), key=fonts.count)
                        has_numbering = bool(re.match(r'^(\d+(\.\d+)*[\.\)\-]|\([a-zA-Z0-9]\)|\•|\-|\*)\s+', line_text))
                        numbering = re.match(r'^(\d+(\.\d+)*[\.\)\-]|\([a-zA-Z0-9]\)|\•|\-|\*)\s+', line_text)
                        numbering_text = numbering.group(0) if numbering else None
                        page_lines.append({
                            "text": line_text,
                            "size": line_size,
                            "font": line_font,
                            "bold": is_bold,
                            "page": page_num,
                            "top": line_top,
                            "left": line_left,
                            "left_space": left_space,
                            "right_space": right_space,
                            "has_numbering": has_numbering,
                            "numbering": numbering_text,
                            "bbox": line_bbox
                        })
        lines.extend(page_lines)
    return lines 