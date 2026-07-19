from pypdf import PdfReader
from docx import Document


def read_pdf(file):
    reader = PdfReader(file)
    text = ""

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"

    return text


def read_docx(file):
    doc = Document(file)
    text = ""

    for para in doc.paragraphs:
        text += para.text + "\n"

    return text


def read_txt(file):
    return file.read().decode("utf-8")


def extract_text(uploaded_file):

    if uploaded_file is None:
        return ""

    if uploaded_file.name.endswith(".pdf"):
        return read_pdf(uploaded_file)

    elif uploaded_file.name.endswith(".docx"):
        return read_docx(uploaded_file)

    elif uploaded_file.name.endswith(".txt"):
        return read_txt(uploaded_file)

    else:
        return ""