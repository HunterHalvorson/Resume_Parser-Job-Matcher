import pdfplumber

with pdfplumber.open("../data/resumes/Hunter Halvorson - Resume.pdf") as pdf:
  text = "\n".join(page.extract_text() for page in pdf.pages)

print(text)