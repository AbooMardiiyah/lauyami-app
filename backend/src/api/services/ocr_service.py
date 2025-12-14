"""OCR service for extracting text from PDF and image files.

Supports:
- PDF files (using pypdf)
- Image files (JPG, PNG) - using EasyOCR or pdf2image + OCR
"""

import io
import easyocr
import numpy as np
import tempfile
from pathlib import Path

from fastapi import UploadFile
from PIL import Image

from src.pipelines.tasks.extract_pdf import extract_pdf_text
from src.utils.logger_util import setup_logging

logger = setup_logging()


async def extract_text_from_file(file: UploadFile) -> str:
    """Extract text from uploaded file (PDF or image).

    Args:
        file (UploadFile): FastAPI uploaded file (PDF or image).

    Returns:
        str: Extracted text content.

    Raises:
        ValueError: If file type is not supported.
        Exception: For extraction errors.

    """
    content_type = file.content_type or ""
    filename = file.filename or ""

    file_bytes = await file.read()

    try:
        if "pdf" in content_type.lower() or filename.lower().endswith(".pdf"):
            logger.info(f"Extracting text from PDF: {filename}")

            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                tmp_file.write(file_bytes)
                tmp_path = tmp_file.name

            try:
                text = extract_pdf_text(tmp_path)
                return text
            finally:
                Path(tmp_path).unlink(missing_ok=True)

        elif any(
            img_type in content_type.lower()
            for img_type in ["image/jpeg", "image/jpg", "image/png"]
        ) or any(filename.lower().endswith(ext) for ext in [".jpg", ".jpeg", ".png"]):
            logger.info(f"Extracting text from image: {filename}")
            return await _extract_text_from_image(file_bytes)

        else:
            raise ValueError(
                f"Unsupported file type: {content_type}. "
                "Supported: PDF, JPG, PNG"
            )

    except Exception as e:
        logger.error(f"Error extracting text from file {filename}: {e}")
        raise


async def _extract_text_from_image(image_bytes: bytes) -> str:
    """Extract text from image bytes using EasyOCR.

    Args:
        image_bytes (bytes): Image file bytes.

    Returns:
        str: Extracted text.

    Raises:
        ImportError: If EasyOCR is not installed.
        Exception: For OCR errors.

    """
    try:
        
        reader = easyocr.Reader(["en"], gpu=True)

        image = Image.open(io.BytesIO(image_bytes))
        if image.mode != "RGB":
            image = image.convert("RGB")

        img_array = np.array(image)

        results = reader.readtext(img_array)

        text_lines = [result[1] for result in results]  # result[1] is the text
        extracted_text = "\n".join(text_lines)

        logger.info(f"OCR extracted {len(extracted_text)} characters from image")
        return extracted_text

    except ImportError:
        logger.error("EasyOCR not installed. Install with: pip install easyocr")
        raise ImportError(
            "EasyOCR is required for image OCR. Install with: pip install easyocr"
        )
    except Exception as e:
        logger.error(f"Error during OCR: {e}")
        raise

