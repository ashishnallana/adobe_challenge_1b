import fitz

def load_pdf_from_path(path):
    """Load a PDF document from a local file path."""
    try:
        return fitz.open(path)
    except Exception as e:
        print(f"Error loading PDF: {e}")
        return None 