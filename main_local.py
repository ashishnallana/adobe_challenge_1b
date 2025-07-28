import os
import json
import sys
from datetime import datetime
from tools.pdf_loader import load_pdf_from_path
from tools.text_extraction import extract_text_lines
from tools.heading_detection import detect_headings_and_levels
from tools.io_utils import save_json_output
from sentence_transformers import SentenceTransformer, util
from transformers import pipeline

# Summarization pipeline
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")

TOP_K = 5  # Number of top sections to extract
MODEL_NAME = "all-MiniLM-L6-v2"

def load_persona_task(input_json_path):
    with open(input_json_path, "r") as f:
        data = json.load(f)
    role = data["persona"]["role"]
    task = data["job_to_be_done"]["task"]
    prompt = f"You are a {role}. Your task is: {task} "
    return prompt, role, task

def process_pdf(pdf_path):
    doc = load_pdf_from_path(pdf_path)
    if not doc:
        print(f"Failed to load {pdf_path}. Skipping.")
        return None, None, None, None
    lines = extract_text_lines(doc)
    title, outline, headings, _ = detect_headings_and_levels(lines)
    text_chunks = []
    for h in headings:
        text_chunks.append({
            "document": os.path.basename(pdf_path),
            "page": h["page"],
            "text": h["text"]
        })
    return title, outline, text_chunks, lines

def extract_section_text(lines, heading_idx, heading_page, all_headings):
    start_idx = None
    for i, line in enumerate(lines):
        if line["page"] == heading_page and line["text"].strip() == all_headings[heading_idx]["text"].strip():
            start_idx = i
            break
    if start_idx is None:
        return all_headings[heading_idx]["text"]
    curr_level = int(all_headings[heading_idx]["level"][1]) if "level" in all_headings[heading_idx] else 1
    for j in range(start_idx + 1, len(lines)):
        for h in all_headings[heading_idx+1:]:
            if lines[j]["page"] == h["page"] and lines[j]["text"].strip() == h["text"].strip():
                next_level = int(h["level"][1]) if "level" in h else 1
                if next_level <= curr_level:
                    return " ".join(line["text"] for line in lines[start_idx:j])
    return " ".join(line["text"] for line in lines[start_idx:])

def summarize_text(text):
    trimmed = text[:2048]
    try:
        summary = summarizer(trimmed, max_length=100, min_length=30, do_sample=False)[0]["summary_text"]
        return summary.strip()
    except Exception as e:
        print(f"⚠️ Summarization failed: {e}")
        return text[:300] + "..."

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 main_local.py <input_directory>")
        sys.exit(1)
    BASE_INPUT_DIR = sys.argv[1]
    INPUT_DIR = os.path.abspath(BASE_INPUT_DIR)
    PDFS_DIR = os.path.join(INPUT_DIR, "PDFs")
    OUTPUT_DIR = INPUT_DIR  # Write outputs to the same directory
    OUTLINES_DIR = os.path.join(INPUT_DIR, "outlines")
    os.makedirs(OUTLINES_DIR, exist_ok=True)
    input_json_path = os.path.join(INPUT_DIR, "challenge1b_input.json")
    if not os.path.exists(input_json_path):
        print(f"Input JSON not found at {input_json_path}")
        sys.exit(1)
    prompt, persona, job = load_persona_task(input_json_path)

    pdf_files = [f for f in os.listdir(PDFS_DIR) if f.lower().endswith(".pdf")]
    if not pdf_files:
        print(f"No PDFs found in {PDFS_DIR}")
        sys.exit(1)

    all_text_chunks = []
    outlines = {}
    all_lines_map = {}
    all_headings_map = {}
    for pdf_file in pdf_files:
        pdf_path = os.path.join(PDFS_DIR, pdf_file)
        title, outline, text_chunks, lines = process_pdf(pdf_path)
        if outline:
            outlines[pdf_file] = {"title": title, "outline": outline}
        if text_chunks:
            all_text_chunks.extend([dict(chunk, **{"pdf_file": pdf_file}) for chunk in text_chunks])
        if lines:
            all_lines_map[pdf_file] = lines
        if outline:
            all_headings_map[pdf_file] = outline

    for pdf_file, outline_data in outlines.items():
        out_path = os.path.join(OUTLINES_DIR, pdf_file.replace(".pdf", ".json"))
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(outline_data, f, indent=2, ensure_ascii=False)

    print("Loading embedding model...")
    model = SentenceTransformer(MODEL_NAME)
    query_embedding = model.encode(prompt, convert_to_tensor=True)
    chunk_texts = [chunk["text"] for chunk in all_text_chunks]
    chunk_embeddings = model.encode(chunk_texts, convert_to_tensor=True)
    similarities = util.pytorch_cos_sim(query_embedding, chunk_embeddings)[0]
    ranked = sorted(
        zip(similarities, all_text_chunks),
        key=lambda x: x[0],
        reverse=True
    )[:TOP_K]

    extracted_sections = []
    subsection_analysis = []
    for i, (score, chunk) in enumerate(ranked, 1):
        pdf_file = chunk["pdf_file"]
        headings = all_headings_map.get(pdf_file, [])
        heading_idx = None
        for idx, h in enumerate(headings):
            if h["text"].strip() == chunk["text"].strip() and h["page"] == chunk["page"]:
                heading_idx = idx
                break
        section_text = chunk["text"]
        if heading_idx is not None:
            lines = all_lines_map.get(pdf_file, [])
            section_text = extract_section_text(lines, heading_idx, chunk["page"], headings)
        summary = summarize_text(section_text)
        extracted_sections.append({
            "document": chunk["document"],
            "section_title": chunk["text"],
            "importance_rank": i,
            "page_number": chunk["page"]
        })
        subsection_analysis.append({
            "document": chunk["document"],
            "refined_text": summary,
            "page_number": chunk["page"]
        })

    final_output = {
        "metadata": {
            "input_documents": pdf_files,
            "persona": persona,
            "job_to_be_done": job,
            "processing_timestamp": datetime.utcnow().isoformat(),
        },
        "extracted_sections": extracted_sections,
        "subsection_analysis": subsection_analysis
    }
    final_output_path = os.path.join(OUTPUT_DIR, "challenge1b_output.json")
    with open(final_output_path, "w", encoding="utf-8") as f:
        json.dump(final_output, f, indent=2, ensure_ascii=False)
    print(f"✅ Output written to {final_output_path}")
    print(f"📁 Per-PDF outlines written to {OUTLINES_DIR}/")

if __name__ == "__main__":
    main() 