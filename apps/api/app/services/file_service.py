import os
import aiofiles
from typing import Optional
from pypdf import PdfReader
from docx import Document
import io
from app.core.logging import get_logger

logger = get_logger(__name__)

class FileService:
    @staticmethod
    async def save_file(file_content: bytes, upload_dir: str, filename: str) -> str:
        """Saves file to local storage and returns the relative path"""
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir, exist_ok=True)
            
        file_path = os.path.join(upload_dir, filename)
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(file_content)
            
        return file_path

    @staticmethod
    def extract_text(file_path: str, mime_type: str) -> Optional[str]:
        """Extracts text content from various file types"""
        try:
            if mime_type == "application/pdf":
                return FileService._extract_from_pdf(file_path)
            elif mime_type in ["application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/msword"]:
                return FileService._extract_from_docx(file_path)
            elif mime_type in ["text/plain", "text/markdown", "application/octet-stream"]:
                return FileService._extract_from_text(file_path)
            else:
                logger.warning(f"Unsupported mime type for extraction: {mime_type}")
                return None
        except Exception as e:
            logger.error(f"Error extracting text from {file_path}: {str(e)}")
            return None

    @staticmethod
    def _extract_from_pdf(file_path: str) -> str:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n\n"
        return text.strip()

    @staticmethod
    def _extract_from_docx(file_path: str) -> str:
        doc = Document(file_path)
        return "\n".join([para.text for para in doc.paragraphs]).strip()

    @staticmethod
    def _extract_from_text(file_path: str) -> str:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read().strip()

