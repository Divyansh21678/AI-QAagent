from pypdf import PdfReader
from docx import Document


def extract_text(uploaded_file):

    if uploaded_file.name.endswith(".pdf"):

        pdf = PdfReader(uploaded_file)

        text = ""

        for page in pdf.pages:
            if page.extract_text():
                text += page.extract_text()

        return text

    elif uploaded_file.name.endswith(".docx"):

        doc = Document(uploaded_file)

        return "\n".join(
            para.text
            for para in doc.paragraphs
        )

    elif uploaded_file.name.endswith(".txt"):

        return uploaded_file.read().decode("utf-8")

    return ""