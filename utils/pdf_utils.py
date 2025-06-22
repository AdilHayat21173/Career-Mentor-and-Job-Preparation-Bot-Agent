
import fitz  # PyMuPDF
from io import BytesIO

def extract_text_from_pdf(uploaded_file):
    """
    Extract text from uploaded PDF file
    """
    try:
        # Read the uploaded file
        pdf_bytes = uploaded_file.read()
        
        # Open PDF from bytes
        pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
        
        text = ""
        for page_num in range(pdf_document.page_count):
            page = pdf_document[page_num]
            text += page.get_text()
        
        pdf_document.close()
        return text
        
    except Exception as e:
        raise Exception(f"Error extracting text from PDF: {str(e)}")