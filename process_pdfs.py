import fitz  # PyMuPDF
import json
import os
import re
from collections import defaultdict

from tools.pdf_loader import load_pdf_from_path
from tools.text_extraction import extract_text_lines
from tools.heading_detection import detect_headings_and_levels
from tools.io_utils import save_json_output

# Default path - will be overridden by command line arguments
# PDF_PATH = r"C:\Users\ashis\Desktop\file03.pdf"


def process_pdfs(pdf_path):
    doc = load_pdf_from_path(pdf_path)
    if not doc:
        print("Failed to load document. Exiting.")
        return

    lines = extract_text_lines(doc)
    title, outline, headings, most_frequent_size = detect_headings_and_levels(
        lines)

    outline_data = {"title": title if title else "", "outline": outline}
    output_dir = os.path.join(os.path.dirname(__file__), "../output")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "extracted_sections.json")
    save_json_output(outline_data, output_path)

    # headings_data = {"total_headings": len(
    #     headings), "most_frequent_font_size": most_frequent_size, "headings": headings}
    # save_json_output(headings_data, "output2.json")

    # all_lines_data = {"total_lines": len(
    #     lines), "most_frequent_font_size": most_frequent_size, "lines": lines}
    # save_json_output(all_lines_data, "output3.json")
