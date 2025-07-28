# Connecting the Dots Challenge – PDF Intelligence Pipeline

## Overview

This project is a solution for the "Connecting the Dots" Challenge, where the goal is to transform static PDFs into intelligent, interactive documents. The pipeline extracts structured outlines (titles, headings) from PDFs, then uses on-device intelligence to rank and link the most relevant sections based on a user persona and job-to-be-done.

## Challenge Context

- **Round 1A:** Extract a structured outline (Title, H1, H2, H3) from a PDF, outputting a clean JSON hierarchy.
- **Round 1B:** Given a collection of PDFs, a persona, and a job-to-be-done, extract and rank the most relevant sections across all documents, outputting a comprehensive JSON with metadata, extracted sections, and sub-section analysis.

## Solution Approach

- **PDF Parsing:** Uses PyMuPDF to extract text lines and their properties (font size, boldness, etc.).
- **Heading Detection:** Applies heuristics (font size, bold, numbering) to identify headings and assign levels (H1, H2, H3).
- **Section Extraction:** For each PDF, extracts all headings/sections and saves a structured outline as a JSON file.
- **Embedding & Ranking:** Uses Sentence Transformers to embed both the persona/job prompt and all extracted headings/sections, then ranks them by semantic similarity.
- **Summarization:** For each top-ranked section, extracts the full section text and summarizes it using a transformer-based summarization model.
- **Output:**
  - Per-PDF outline JSONs (in a dedicated `outlines/` folder inside the input directory)
  - A final `challenge1b_output.json` with metadata, top-ranked sections, and sub-section analysis (in the input directory)

## Directory Structure

```
project_root/
│
├── Collection1/                  # Example input/output directory
│   ├── challenge1b_input.json     # Input persona/job JSON
│   ├── PDFs/                     # All input PDFs go here
│   ├── outlines/                 # Per-PDF outline JSONs (output)
│   └── challenge1b_output.json   # Final output JSON
│
├── src/
│   ├── main_local.py             # Main pipeline (run this)
│   └── tools/                    # PDF loading, text extraction, heading detection
│
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

## How to Run Locally (No Docker Required)

1. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

2. **Prepare your input directory:**

   - Place all your PDF files in `<your_input_dir>/PDFs/`
   - Place your `challenge1b_input.json` in `<your_input_dir>/`

3. **Run the pipeline:**

   ```bash
   cd src
   python3 main_local.py ../<your_input_dir>
   ```

   - For example, if your input directory is `Collection1`, run:
     ```bash
     python3 main_local.py ../Collection1
     ```

4. **Check your outputs:**
   - Per-PDF outline JSONs: `<your_input_dir>/outlines/AEE UNIT-1.json`, etc.
   - Final output: `<your_input_dir>/challenge1b_output.json`

## How to Run with Docker

You can run the pipeline using Docker, which ensures all dependencies are pre-installed and avoids repeated package installations.

### 1. Build the Docker Image

```bash
docker build -t pdf-intelligence-pipeline .
```

### 2. Prepare Your Input Directory

- Place all your PDF files in `<your_input_dir>/PDFs/`
- Place your `challenge1b_input.json` in `<your_input_dir>/`

### 3. Run the Pipeline

Mount your input directory as a volume and run the container:

```bash
docker run --rm -v /absolute/path/to/your/input:/input pdf-intelligence-pipeline /input
```

- Replace `/absolute/path/to/your/input` with the full path to your input directory on your machine.
- The outputs will be written to the same mounted directory.

### Notes

- All Python dependencies are installed at build time, so running the container is fast and does not reinstall packages.
- You can still run the pipeline locally as described above if you prefer.

## Input/Output Format

- **Input:**
  - PDFs: Any number of PDF files in `<input_dir>/PDFs/`
  - `challenge1b_input.json`:
    ```json
    {
      "persona": { "role": "Accounting examing tutor" },
      "job_to_be_done": { "task": "what is Managerial Economics" }
    }
    ```
- **Output:**
  - Per-PDF outline JSONs (one for each PDF) in `<input_dir>/outlines/`
  - `challenge1b_output.json` in `<input_dir>/`:
    ```json
    {
      "metadata": { ... },
      "extracted_sections": [ ... ],
      "subsection_analysis": [ ... ]
    }
    ```

## Notes

- The pipeline does **not** use the pre-generated `text_chunks.json` for ranking; it extracts and ranks headings/sections live from the PDFs.
- All processing is CPU-only and offline.
- The script now takes the input directory as a command-line argument and writes all outputs to that directory.

## Customization

- To change the number of top sections ranked, edit the `TOP_K` variable in `main_local.py`.
- To improve heading detection, modify the logic in `src/tools/heading_detection.py`.

## Contact

For questions or improvements, please open an issue or contact the author.
