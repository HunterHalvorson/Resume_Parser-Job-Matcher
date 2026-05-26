# import to reduce the complexity of working with pdf format
import pdfplumber

"""
    Function Name: extract_pdf
    Function Parameter: pdf_path (str), a path to the resume we want to extract
    Function Return: A string containing the text contents of the resume
"""
def extract_pdf(pdf_path: str) -> str:
    # context manager to close file
    with pdfplumber.open(pdf_path) as pdf:
        # return the pages combined via a new line character
        return "\n".join(page.extract_text() or "" for page in pdf.pages)