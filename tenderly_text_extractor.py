import io
from pdfminer.high_level import extract_text
from docx import Document as DocxDocument


def extract_text_from_pdf(file):
    return extract_text(io.BytesIO(file.read()))


def extract_text_from_txt(file):
    return file.read().decode("utf-8", errors="ignore")


def extract_text_from_docx(file):
    document = DocxDocument(io.BytesIO(file.read()))
    return "\n".join(p.text for p in document.paragraphs if p.text.strip())


def extract_text_from_file(uploaded_file):
    name = uploaded_file.name.lower()

    if name.endswith(".pdf"):
        return extract_text_from_pdf(uploaded_file)
    if name.endswith(".txt"):
        return extract_text_from_txt(uploaded_file)
    if name.endswith(".docx"):
        return extract_text_from_docx(uploaded_file)

    raise ValueError(f"Unsupported file type: {uploaded_file.name}")
