# invoiceservice/shared/parser_helpers.py

from flask import current_app

from invoiceservice.utils.ReadPdf import pdf_to_jpg
from invoiceservice.utils.scanner import ImageScanner
from invoiceservice.utils.rewe import extract_text_from_pdf  # if REWE-specific logic
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def create_dataframe(pdf_path, filename, month, year, shopname, userid):
    """
    Processes a PDF file, extracts data into a DataFrame, and associates it with a user ID.
    """
    try:
        # 1. Text-based (REWE)
        if shopname.lower() == 'rewe':
            extracted_text = extract_text_from_pdf(filename)
            scanned_object = ImageScanner('', filename, extracted_text, month, year)
        else:
            # 2. Image-based (Kaufland, etc.)
            image_path = pdf_to_jpg(pdf_path, filename, current_app.config['IMAGE_FOLDER'])
            scanned_object = ImageScanner(image_path, filename, '', month, year)

        # 3. Extract text & grocery data
        text = scanned_object.get_text()
        scanned_object.get_grocery_bill()
        df = scanned_object.create_data_frame()

        if df.empty:
            raise ValueError("Failed to extract valid data from the PDF.")

        df['userid'] = userid
        return df

    except Exception as e:
        logger.error(f"Error creating DataFrame from PDF: {str(e)}")
        raise
