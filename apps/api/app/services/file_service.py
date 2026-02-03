import os
import aiofiles
import aioboto3
import httpx
from typing import Optional, Union
from pypdf import PdfReader
from docx import Document
import io
from app.core.logging import get_logger
from app.core.config import settings

logger = get_logger(__name__)

class FileService:
    @staticmethod
    def sanitize_text(text: Optional[str]) -> Optional[str]:
        """Remove invalid unicode (surrogates) and null bytes before storage."""
        if text is None:
            return None
        if not isinstance(text, str):
            text = str(text)
        # Drop surrogate code points and other invalid UTF-8 sequences
        cleaned = text.encode("utf-8", "ignore").decode("utf-8", "ignore")
        # Remove null bytes which can break DB inserts
        if "\x00" in cleaned:
            cleaned = cleaned.replace("\x00", "")
        return cleaned

    @staticmethod
    async def save_file(file_content: bytes, upload_dir: str, filename: str) -> str:
        """Saves file to S3-compatible storage (like DigitalOcean Spaces) if configured"""
        
        # Check if S3 is configured
        if settings.S3_ACCESS_KEY_ID and settings.S3_SECRET_ACCESS_KEY:
            try:
                # Normalize key path for S3
                s3_key = f"{upload_dir}/{filename}".replace("\\", "/")
                
                session = aioboto3.Session()
                async with session.client(
                    's3',
                    endpoint_url=settings.S3_ENDPOINT_URL,
                    aws_access_key_id=settings.S3_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.S3_SECRET_ACCESS_KEY,
                    region_name=settings.S3_REGION
                ) as s3:
                    await s3.put_object(
                        Bucket=settings.S3_BUCKET_NAME,
                        Key=s3_key,
                        Body=file_content
                    )
                
                # If a public URL is configured, return the full URL, otherwise return the key
                if settings.S3_PUBLIC_URL:
                    return f"{settings.S3_PUBLIC_URL.rstrip('/')}/{s3_key}"
                return s3_key
                
            except Exception as e:
                logger.error(f"Failed to upload to S3: {str(e)}. Falling back to local storage.")

        # Fallback to local storage
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir, exist_ok=True)
            
        file_path = os.path.join(upload_dir, filename)
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(file_content)
            
        return file_path

    @staticmethod
    async def delete_file(file_path: str) -> bool:
        """Deletes a file from either S3-compatible storage or local storage"""
        
        # 1. Try S3 deletion if configured
        if settings.S3_ACCESS_KEY_ID and settings.S3_SECRET_ACCESS_KEY:
            try:
                s3_key = None
                
                # If it's a full public URL, extract the key
                if settings.S3_PUBLIC_URL and file_path.startswith(settings.S3_PUBLIC_URL):
                    s3_key = file_path.replace(settings.S3_PUBLIC_URL.rstrip("/") + "/", "")
                # If it's a URL but doesn't start with S3_PUBLIC_URL, it might still be an S3 URL 
                # or it might be just the key if S3_PUBLIC_URL was not set during upload
                elif file_path.startswith("http"):
                    # Extract key from URL (everything after the bucket name in a standard Supabase/S3 URL)
                    # For Supabase: https://[project].supabase.co/storage/v1/object/public/[bucket]/[key]
                    # We try to find the bucket name in the path
                    if settings.S3_BUCKET_NAME in file_path:
                        parts = file_path.split(f"{settings.S3_BUCKET_NAME}/")
                        if len(parts) > 1:
                            s3_key = parts[1]
                # If it doesn't look like an absolute local path and doesn't exist locally,
                # it might be an S3 key
                elif not os.path.isabs(file_path) and not os.path.exists(file_path):
                    s3_key = file_path

                if s3_key:
                    logger.info(f"Attempting to delete from S3: {s3_key}")
                    session = aioboto3.Session()
                    async with session.client(
                        's3',
                        endpoint_url=settings.S3_ENDPOINT_URL,
                        aws_access_key_id=settings.S3_ACCESS_KEY_ID,
                        aws_secret_access_key=settings.S3_SECRET_ACCESS_KEY,
                        region_name=settings.S3_REGION
                    ) as s3:
                        await s3.delete_object(
                            Bucket=settings.S3_BUCKET_NAME,
                            Key=s3_key
                        )
                        logger.success(f"Successfully deleted file from S3: {s3_key}")
                        return True
            except Exception as e:
                logger.error(f"Failed to delete from S3: {str(e)}")

        # 2. Try local deletion
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Deleted file from local storage: {file_path}")
                return True
        except Exception as e:
            logger.error(f"Failed to delete file from disk: {file_path} - {e}")
            
        return False

    @staticmethod
    async def extract_text(file_path_or_content: Union[str, bytes], mime_type: str) -> Optional[str]:
        """Extracts text content from various file types (supports local paths, URLs, and raw bytes)"""
        try:
            # Handle raw bytes
            if isinstance(file_path_or_content, bytes):
                file_content = io.BytesIO(file_path_or_content)
                source_name = "raw_bytes"
            # Handle URLs
            elif file_path_or_content.startswith(('http://', 'https://')):
                source_name = file_path_or_content
                async with httpx.AsyncClient() as client:
                    response = await client.get(file_path_or_content)
                    response.raise_for_status()
                    file_content = io.BytesIO(response.content)
            else:
                # Handle local files
                source_name = file_path_or_content
                if not os.path.exists(file_path_or_content):
                    logger.error(f"File not found: {file_path_or_content}")
                    return None
                with open(file_path_or_content, 'rb') as f:
                    file_content = io.BytesIO(f.read())

            if mime_type == "application/pdf":
                extracted = FileService._extract_from_pdf(file_content)
            elif mime_type in ["application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/msword"]:
                extracted = FileService._extract_from_docx(file_content)
            elif mime_type in ["text/plain", "text/markdown", "application/octet-stream"]:
                extracted = FileService._extract_from_text(file_content)
            else:
                logger.warning(f"Unsupported mime type for extraction: {mime_type}")
                return None
            return FileService.sanitize_text(extracted)
        except Exception as e:
            logger.error(f"Error extracting text from {source_name}: {str(e)}")
            return None

    @staticmethod
    def _extract_from_pdf(file_stream: io.BytesIO) -> str:
        reader = PdfReader(file_stream)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n\n"
        return text.strip()

    @staticmethod
    def _extract_from_docx(file_stream: io.BytesIO) -> str:
        doc = Document(file_stream)
        return "\n".join([para.text for para in doc.paragraphs]).strip()

    @staticmethod
    def _extract_from_text(file_stream: io.BytesIO) -> str:
        return file_stream.getvalue().decode('utf-8', errors='ignore').strip()

