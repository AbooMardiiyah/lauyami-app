import os
from pathlib import Path

from pypdf import PdfReader
from pypdf.errors import PdfReadError

from src.models.article_models import ArticleItem
from src.utils.logger_util import setup_logging

logger = setup_logging()


def extract_pdf_text(pdf_path: str | Path) -> str:
    """Extract all text from a PDF file.

    Args:
        pdf_path (str | Path): Path to the PDF file.

    Returns:
        str: Extracted text content from the PDF.

    Raises:
        FileNotFoundError: If the PDF file does not exist.
        PdfReadError: If the PDF cannot be read or is corrupted.
        Exception: For unexpected errors during extraction.
    """
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    logger.info(f"Extracting text from PDF: {pdf_path}")
    try:
        reader = PdfReader(pdf_path)
        text_parts = []

        for page_num, page in enumerate(reader.pages, start=1):
            try:
                text = page.extract_text()
                if text.strip():
                    text_parts.append(text)
                    logger.debug(f"Extracted {len(text)} characters from page {page_num}")
            except Exception as e:
                logger.warning(f"Error extracting text from page {page_num}: {e}")
                continue

        full_text = "\n\n".join(text_parts)
        logger.info(f"Successfully extracted {len(full_text)} characters from {len(reader.pages)} pages")
        return full_text

    except PdfReadError as e:
        logger.error(f"Failed to read PDF file: {e}")
        raise PdfReadError(f"Cannot read PDF file: {pdf_path}") from e
    except Exception as e:
        logger.error(f"Unexpected error extracting PDF text: {e}")
        raise


def create_document_items_from_pdf(
    pdf_path: str | Path,
    document_title: str,
    jurisdiction: str,
    document_id: str | None = None,
    effective_date: str | None = None,
) -> list[ArticleItem]:
    """Extract text from PDF and create ArticleItem objects for ingestion.

    This function extracts text from a PDF and creates ArticleItem objects
    that can be ingested into the database. The text is kept as one large
    content block - chunking will be done during embedding ingestion.

    Args:
        pdf_path (str | Path): Path to the PDF file.
        document_title (str): Title of the legal document (e.g., "Lagos State Tenancy Law 2011").
        jurisdiction (str): Jurisdiction of the document (e.g., "Lagos State").
        document_id (str | None, optional): Unique identifier for the document.
            If None, uses the PDF filename without extension. Defaults to None.
        effective_date (str | None, optional): Effective or issued date of the document.
            Defaults to None.

    Returns:
        list[ArticleItem]: List of ArticleItem objects ready for ingestion.
            Currently returns a single item with the full extracted text.

    Raises:
        FileNotFoundError: If the PDF file does not exist.
        Exception: For unexpected errors during extraction.
    """
    pdf_path = Path(pdf_path)

    if document_id is None:
        document_id = pdf_path.stem

    try:
        content = extract_pdf_text(pdf_path)

        if not content.strip():
            logger.warning(f"PDF extracted but content is empty: {pdf_path}")
            return []

        document_item = ArticleItem(
            document_title=document_title,
            jurisdiction=jurisdiction,
            section_title=document_title,  
            document_id=document_id,
            content=content,
            document_type=[], 
            effective_date=effective_date,
        )

        logger.info(
            f"Created document item: title='{document_title}', "
            f"jurisdiction='{jurisdiction}', content_length={len(content)}"
        )

        return [document_item]

    except Exception as e:
        logger.error(f"Failed to create document items from PDF: {e}")
        raise

