# shared/rewe.py

import fitz  # PyMuPDF

def extract_text_from_pdf(pdf_path):
    """
    Extracts raw text from a PDF using PyMuPDF.
    """
    try:
        doc = fitz.open(pdf_path)
        extracted_text = ""

        for page in doc:
            extracted_text += page.get_text("text") + "\n\n"

        doc.close()
        return " ".join(extracted_text.split())

    except Exception as e:
        print(f"Error extracting text from {pdf_path}: {e}")
        return ""
