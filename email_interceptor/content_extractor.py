"""Content extraction from email attachments using Apache Tika."""
import logging
import requests
import tempfile
import os
from pathlib import Path
from typing import Optional, Dict, List
import zipfile
import tarfile

logger = logging.getLogger(__name__)

class ContentExtractor:
    """Extract text content from various file types using Apache Tika."""
    
    def __init__(self, tika_server_url: str = "http://localhost:9998"):
        """Initialize content extractor."""
        self.tika_server_url = tika_server_url.rstrip('/')
        self.tika_text_endpoint = f"{self.tika_server_url}/tika"
        self.tika_meta_endpoint = f"{self.tika_server_url}/meta"
    
    def extract_text(self, file_path: str, max_size_mb: int = 50) -> Optional[str]:
        """
        Extract text from a file using Tika.
        
        Args:
            file_path: Path to the file
            max_size_mb: Maximum file size in MB
            
        Returns:
            Extracted text or None if extraction fails
        """
        try:
            # Check file size
            file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
            if file_size > max_size_mb:
                logger.warning(f"File {file_path} exceeds size limit ({file_size:.2f}MB > {max_size_mb}MB)")
                return None
            
            with open(file_path, 'rb') as f:
                response = requests.put(
                    self.tika_text_endpoint,
                    data=f,
                    headers={'Accept': 'text/plain'},
                    timeout=30
                )
                
                if response.status_code == 200:
                    return response.text
                else:
                    logger.error(f"Tika extraction failed: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error extracting text from {file_path}: {e}")
            return None
    
    def extract_from_archive(self, archive_path: str, max_depth: int = 2, 
                            current_depth: int = 0) -> Dict[str, str]:
        """
        Extract text from all files in an archive (simplified - no nested archives).
        
        Args:
            archive_path: Path to archive file
            max_depth: Maximum recursion depth (simplified to 2)
            current_depth: Current recursion depth
            
        Returns:
            Dictionary mapping file paths to extracted text
        """
        extracted = {}
        
        if current_depth >= max_depth:
            logger.warning(f"Maximum archive depth ({max_depth}) reached")
            return extracted
        
        try:
            # Only handle ZIP files (simplified)
            if zipfile.is_zipfile(archive_path):
                with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                    for member in zip_ref.namelist():
                        if member.endswith('/'):
                            continue
                        
                        # Extract to temp file
                        with tempfile.NamedTemporaryFile(delete=False) as tmp:
                            tmp.write(zip_ref.read(member))
                            tmp_path = tmp.name
                        
                        try:
                            text = self.extract_text(tmp_path)
                            if text:
                                extracted[member] = text
                        finally:
                            if os.path.exists(tmp_path):
                                os.unlink(tmp_path)
        
        except Exception as e:
            logger.error(f"Error extracting from archive {archive_path}: {e}")
        
        return extracted
    
    def get_file_metadata(self, file_path: str) -> Dict[str, str]:
        """Get file metadata using Tika."""
        try:
            with open(file_path, 'rb') as f:
                response = requests.put(
                    self.tika_meta_endpoint,
                    data=f,
                    headers={'Accept': 'application/json'},
                    timeout=30
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    return {}
        except Exception as e:
            logger.error(f"Error getting metadata for {file_path}: {e}")
            return {}
    
    def is_tika_available(self) -> bool:
        """Check if Tika server is available."""
        try:
            response = requests.get(f"{self.tika_server_url}/tika", timeout=5)
            return response.status_code == 200
        except Exception:
            return False

