"""
Extractor Module

Responsible for:
1. Identifying file type (PDF or DOCX) based on extension.
2. Validating that the file exists and is not corrupt.
3. Extracting raw text from PDFs using pypdf.
4. Extracting raw text from DOCX files using python-docx.
5. Returning the raw text as a clean string.
"""

def extract_text(file_path: str) -> str:
    """
    Extracts raw text from the given resume PDF or DOCX file.
    
    TODO:
    - Check if the file exists.
    - Check file extension (.pdf or .docx).
    - If .pdf, call extract_text_from_pdf.
    - If .docx, call extract_text_from_docx.
    - Raise ValueError for unsupported formats.
    """
    # TODO: Implement file verification and selection logic
    pass

def extract_text_from_pdf(file_path: str) -> str:
    """
    Extracts text from a PDF file.
    
    TODO:
    - Open file in binary mode.
    - Use pypdf.PdfReader to extract text page by page.
    - Concatenate and return cleaned text.
    """
    # TODO: Implement PDF text extraction
    pass

def extract_text_from_docx(file_path: str) -> str:
    """
    Extracts text from a DOCX file.
    
    TODO:
    - Use docx.Document to load the document.
    - Iterate through paragraphs and extract text.
    - Concatenate and return cleaned text.
    """
    # TODO: Implement DOCX text extraction
    pass
