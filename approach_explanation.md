# Approach Explanation – Connecting the Dots Challenge

## Overview
Our solution for the "Connecting the Dots" Challenge is designed to transform static PDF documents into intelligent, interactive resources. The pipeline extracts structured outlines from PDFs, understands document sections, and ranks the most relevant content for a given persona and job-to-be-done. The approach is modular, efficient, and fully offline, making it robust and extensible for future enhancements.

## Methodology

### 1. PDF Parsing and Text Extraction
We use PyMuPDF to parse each PDF and extract text lines along with their properties, such as font size, font name, boldness, and page number. This granular extraction is crucial for accurately identifying headings and understanding document structure, especially since PDFs often lack explicit semantic markup.

### 2. Heading Detection and Outline Construction
To build a structured outline, we apply a set of heuristics to the extracted lines:
- **Font Size:** Larger font sizes often indicate higher-level headings.
- **Boldness:** Bold text is more likely to be a heading.
- **Numbering Patterns:** Numbered or bulleted lines are considered as potential headings.
- **Textual Heuristics:** We filter out lines that are too short, too symbolic, or end with certain punctuation that is unlikely for headings.

Detected headings are assigned levels (H1, H2, H3) based on their relative font sizes and document context. The result is a hierarchical outline for each PDF, which is saved as a JSON file in a dedicated `outlines/` folder.

### 3. Section Extraction
For each detected heading, we extract the full section text—defined as all content from the heading until the next heading of the same or higher level, or the end of the document. This ensures that the context for each section is preserved, which is essential for meaningful summarization and ranking.

### 4. Persona-Driven Semantic Ranking
The core of the "Connecting the Dots" challenge is to surface the most relevant sections for a specific persona and job-to-be-done. We:
- Combine the persona and job into a single prompt.
- Use a Sentence Transformer (all-MiniLM-L6-v2) to embed both the prompt and all extracted section headings.
- Compute cosine similarity between the prompt and each section, ranking them by semantic relevance.
- Select the top-K most relevant sections for further analysis.

### 5. Section Summarization
For each top-ranked section, we use a transformer-based summarization model (DistilBART) to generate a concise summary of the section’s content. This summary is included as `refined_text` in the final output, providing a quick, context-aware overview for the user.

### 6. Output Generation
The pipeline produces:
- Per-PDF outline JSONs in `<input_dir>/outlines/`.
- A final `challenge1b_output.json` in the input directory, containing metadata, extracted sections, and subsection analyses.

### 7. Modularity and Compliance
The solution is fully modular, with separate components for PDF loading, text extraction, heading detection, embedding/ranking, and summarization. All processing is CPU-only and offline, ensuring compliance with challenge constraints. The pipeline is easily extensible for new document types, additional languages, or improved heuristics.

## Conclusion
This approach enables a robust, context-aware understanding of PDF documents, making them searchable, explorable, and tailored to user needs. By combining structural analysis with semantic intelligence, our solution lays the foundation for the next generation of interactive document experiences. 