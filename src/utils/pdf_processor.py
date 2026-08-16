from loguru import logger
from pypdf import PdfReader


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extracts text from a PDF file and returns it as a string.

    Args:
        file_path (str): The path to the PDF file.

    Returns:
        str: The extracted text from the PDF file.

    Raises:
        Exception: If there is an error processing the PDF file.
    """
    try:
        reader = PdfReader(pdf_path)
        full_text = []

        for page in reader.pages:
            text = page.extract_text()
            if text:
                full_text.append(text)

        return "\n".join(full_text)

    except FileNotFoundError:
        logger.error("PDF extraction failed because the file could not be found.")
        return ""
    except Exception:
        logger.exception("PDF extraction failed for an unexpected reason.")
        return ""
