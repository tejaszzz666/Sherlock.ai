"""
Sherlock.ai - Security & Validation
File validation, size checks, and security utilities
"""

import os
import magic
from pathlib import Path
from typing import Tuple, Optional
from fastapi import UploadFile, HTTPException

from .logging import get_logger

logger = get_logger(__name__)


class FileValidator:
    """Validates uploaded files for security and size constraints"""
    
    def __init__(
        self,
        max_size_bytes: int,
        allowed_mime_types: list[str]
    ):
        self.max_size_bytes = max_size_bytes
        self.allowed_mime_types = allowed_mime_types
    
    async def validate_file(
        self,
        file: UploadFile,
        check_magic: bool = True
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate uploaded file
        
        Args:
            file: FastAPI UploadFile object
            check_magic: Whether to check file magic numbers (recommended)
            
        Returns:
            (is_valid, error_message)
        """
        
        # Check file size
        file.file.seek(0, 2)  # Seek to end
        file_size = file.file.tell()
        file.file.seek(0)  # Reset to start
        
        if file_size > self.max_size_bytes:
            size_mb = self.max_size_bytes / (1024 * 1024)
            return False, f"File too large. Maximum size: {size_mb:.1f}MB"
        
        if file_size == 0:
            return False, "File is empty"
        
        # Check MIME type from header
        content_type = file.content_type
        if content_type not in self.allowed_mime_types:
            return False, f"Invalid file type: {content_type}. Allowed: {', '.join(self.allowed_mime_types)}"
        
        # Check magic numbers (file signature)
        if check_magic:
            try:
                file_bytes = await file.read(8192)  # Read first 8KB
                await file.seek(0)  # Reset
                
                mime = magic.from_buffer(file_bytes, mime=True)
                
                if mime not in self.allowed_mime_types:
                    logger.warning(
                        f"Magic number mismatch: Content-Type={content_type}, "
                        f"Magic={mime}, File={file.filename}"
                    )
                    return False, f"File type mismatch. Expected {content_type}, got {mime}"
                    
            except Exception as e:
                logger.error(f"Magic number check failed: {e}")
                # Don't fail validation, just log warning
                pass
        
        return True, None
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitize filename to prevent directory traversal attacks
        
        Args:
            filename: Original filename
            
        Returns:
            Sanitized filename
        """
        # Remove path components
        filename = os.path.basename(filename)
        
        # Remove dangerous characters
        dangerous_chars = ['..', '/', '\\', '\0', ':', '*', '?', '"', '<', '>', '|']
        for char in dangerous_chars:
            filename = filename.replace(char, '_')
        
        # Ensure it has an extension
        if '.' not in filename:
            filename += '.tmp'
        
        return filename
    
    @staticmethod
    async def save_upload_file(
        file: UploadFile,
        destination: Path,
        chunk_size: int = 1024 * 1024  # 1MB chunks
    ) -> Path:
        """
        Safely save uploaded file in chunks
        
        Args:
            file: FastAPI UploadFile
            destination: Destination path
            chunk_size: Size of chunks to read/write
            
        Returns:
            Path to saved file
        """
        try:
            with open(destination, 'wb') as f:
                while chunk := await file.read(chunk_size):
                    f.write(chunk)
            
            logger.info(f"Saved file: {destination.name} ({destination.stat().st_size} bytes)")
            return destination
            
        except Exception as e:
            logger.error(f"Failed to save file {file.filename}: {e}")
            if destination.exists():
                destination.unlink()
            raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")


def create_image_validator(max_size_mb: int, allowed_types: list[str]) -> FileValidator:
    """Create validator for image files"""
    return FileValidator(
        max_size_bytes=max_size_mb * 1024 * 1024,
        allowed_mime_types=allowed_types
    )


def create_video_validator(max_size_mb: int, allowed_types: list[str]) -> FileValidator:
    """Create validator for video files"""
    return FileValidator(
        max_size_bytes=max_size_mb * 1024 * 1024,
        allowed_mime_types=allowed_types
    )
