"""File storage service - FREQ-21."""
import os
import hashlib
import mimetypes
import time
import requests
from pathlib import Path
from typing import Optional, BinaryIO
from uuid import UUID, uuid4
from datetime import datetime

from fastapi import UploadFile


class FileStorageService:
    """Service for secure file storage - FREQ-21."""
    
    def __init__(self, base_path: str = "data/uploads", virustotal_api_key: Optional[str] = None):
        """
        Initialize file storage service.
        
        Args:
            base_path: Base directory for file uploads
            virustotal_api_key: VirusTotal API key for malware scanning
        """
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.virustotal_api_key = virustotal_api_key or os.getenv("VIRUSTOTAL_API_KEY")
        
        # Allowed file types - FREQ-21
        self.allowed_types = {
            'image/png', 'image/jpeg', 'image/jpg', 'image/gif',
            'video/mp4', 'video/avi', 'video/quicktime',
            'application/pdf', 'text/plain',
            'application/zip', 'application/x-zip-compressed'
        }
        
        # Max file size: 50MB
        self.max_file_size = 50 * 1024 * 1024
    
    def validate_file(self, file: UploadFile) -> tuple[bool, Optional[str]]:
        """
        Validate file type and size.
        
        Returns:
            (is_valid, error_message)
        """
        # Check file type
        if file.content_type not in self.allowed_types:
            return False, f"File type {file.content_type} not allowed"
        
        # Check file size
        file.file.seek(0, 2)  # Seek to end
        file_size = file.file.tell()
        file.file.seek(0)  # Reset to beginning
        
        if file_size > self.max_file_size:
            return False, f"File size {file_size} exceeds 50MB limit"
        
        if file_size == 0:
            return False, "File is empty"
        
        return True, None
    
    def generate_safe_filename(self, original_filename: str, report_id: UUID) -> str:
        """
        Generate safe filename with UUID prefix.
        
        Args:
            original_filename: Original filename from upload
            report_id: Report ID for organization
            
        Returns:
            Safe filename
        """
        # Get file extension
        _, ext = os.path.splitext(original_filename)
        
        # Generate unique filename
        unique_id = uuid4()
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        
        return f"{report_id}_{timestamp}_{unique_id}{ext}"
    
    def calculate_file_hash(self, file_content: bytes) -> str:
        """Calculate SHA-256 hash of file content."""
        return hashlib.sha256(file_content).hexdigest()
    
    def save_file(
        self,
        file: UploadFile,
        report_id: UUID,
        subfolder: str = "reports"
    ) -> dict:
        """
        Save uploaded file to storage.
        
        Args:
            file: Uploaded file
            report_id: Report ID
            subfolder: Subfolder within base_path
            
        Returns:
            File metadata dict
        """
        # Validate file
        is_valid, error = self.validate_file(file)
        if not is_valid:
            raise ValueError(error)
        
        # Create subfolder
        storage_dir = self.base_path / subfolder / str(report_id)
        storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate safe filename
        safe_filename = self.generate_safe_filename(file.filename, report_id)
        file_path = storage_dir / safe_filename
        
        # Read file content
        file_content = file.file.read()
        file.file.seek(0)  # Reset for potential re-reading
        
        # Calculate hash
        file_hash = self.calculate_file_hash(file_content)
        
        # Save file
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        # Get file size
        file_size = len(file_content)
        
        # Return metadata
        return {
            "filename": safe_filename,
            "original_filename": file.filename,
            "file_type": file.content_type,
            "file_size": file_size,
            "storage_path": str(file_path.relative_to(self.base_path)),
            "file_hash": file_hash,
            "uploaded_at": datetime.utcnow()
        }
    
    def delete_file(self, storage_path: str) -> bool:
        """
        Delete file from storage.
        
        Args:
            storage_path: Relative path to file
            
        Returns:
            True if deleted, False if not found
        """
        file_path = self.base_path / storage_path
        
        if file_path.exists():
            file_path.unlink()
            return True
        
        return False
    
    def get_file_path(self, storage_path: str) -> Optional[Path]:
        """
        Get absolute file path.
        
        Args:
            storage_path: Relative path to file
            
        Returns:
            Absolute path if exists, None otherwise
        """
        file_path = self.base_path / storage_path
        
        if file_path.exists():
            return file_path
        
        return None
    
    def scan_file_for_viruses(self, file_path: Path) -> tuple[bool, Optional[str]]:
        """
        Scan file for viruses using VirusTotal API.
        
        Args:
            file_path: Path to file
            
        Returns:
            (is_safe, scan_result)
        """
        if not self.virustotal_api_key:
            # No API key - perform basic checks only
            return self._basic_malware_check(file_path)
        
        try:
            # Calculate file hash
            with open(file_path, "rb") as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()
            
            # Check if file hash already exists in VirusTotal
            is_safe, result = self._check_virustotal_hash(file_hash)
            
            if result != "not_found":
                return is_safe, result
            
            # File not in database - upload for scanning
            return self._upload_to_virustotal(file_path)
            
        except Exception as e:
            # On error, fall back to basic checks
            return self._basic_malware_check(file_path)
    
    def _check_virustotal_hash(self, file_hash: str) -> tuple[bool, str]:
        """
        Check if file hash exists in VirusTotal database.
        
        Args:
            file_hash: SHA-256 hash of file
            
        Returns:
            (is_safe, result_message)
        """
        url = f"https://www.virustotal.com/api/v3/files/{file_hash}"
        headers = {
            "x-apikey": self.virustotal_api_key
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 404:
                return True, "not_found"
            
            if response.status_code != 200:
                return True, f"VirusTotal API error: {response.status_code}"
            
            data = response.json()
            stats = data.get("data", {}).get("attributes", {}).get("last_analysis_stats", {})
            
            malicious = stats.get("malicious", 0)
            suspicious = stats.get("suspicious", 0)
            
            if malicious > 0 or suspicious > 2:
                return False, f"Malware detected: {malicious} malicious, {suspicious} suspicious"
            
            return True, f"Clean: {stats.get('harmless', 0)} engines marked as safe"
            
        except Exception as e:
            return True, f"Hash check error: {str(e)}"
    
    def _upload_to_virustotal(self, file_path: Path) -> tuple[bool, str]:
        """
        Upload file to VirusTotal for scanning.
        
        Args:
            file_path: Path to file
            
        Returns:
            (is_safe, result_message)
        """
        url = "https://www.virustotal.com/api/v3/files"
        headers = {
            "x-apikey": self.virustotal_api_key
        }
        
        try:
            # Upload file
            with open(file_path, "rb") as f:
                files = {"file": (file_path.name, f)}
                response = requests.post(url, headers=headers, files=files, timeout=30)
            
            if response.status_code != 200:
                return True, f"Upload failed: {response.status_code}"
            
            data = response.json()
            analysis_id = data.get("data", {}).get("id")
            
            if not analysis_id:
                return True, "No analysis ID returned"
            
            # Wait for analysis (max 60 seconds)
            return self._wait_for_analysis(analysis_id)
            
        except Exception as e:
            return True, f"Upload error: {str(e)}"
    
    def _wait_for_analysis(self, analysis_id: str, max_wait: int = 60) -> tuple[bool, str]:
        """
        Wait for VirusTotal analysis to complete.
        
        Args:
            analysis_id: Analysis ID from upload
            max_wait: Maximum seconds to wait
            
        Returns:
            (is_safe, result_message)
        """
        url = f"https://www.virustotal.com/api/v3/analyses/{analysis_id}"
        headers = {
            "x-apikey": self.virustotal_api_key
        }
        
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            try:
                response = requests.get(url, headers=headers, timeout=10)
                
                if response.status_code != 200:
                    return True, f"Analysis check failed: {response.status_code}"
                
                data = response.json()
                status = data.get("data", {}).get("attributes", {}).get("status")
                
                if status == "completed":
                    stats = data.get("data", {}).get("attributes", {}).get("stats", {})
                    malicious = stats.get("malicious", 0)
                    suspicious = stats.get("suspicious", 0)
                    
                    if malicious > 0 or suspicious > 2:
                        return False, f"Malware detected: {malicious} malicious, {suspicious} suspicious"
                    
                    return True, f"Clean: {stats.get('harmless', 0)} engines marked as safe"
                
                # Wait before next check
                time.sleep(3)
                
            except Exception as e:
                return True, f"Analysis wait error: {str(e)}"
        
        # Timeout - assume safe but flag for manual review
        return True, "Analysis timeout - manual review recommended"
    
    def _basic_malware_check(self, file_path: Path) -> tuple[bool, str]:
        """
        Perform basic malware checks without external API.
        
        Args:
            file_path: Path to file
            
        Returns:
            (is_safe, result_message)
        """
        try:
            # Check file size (suspicious if too small or too large)
            file_size = file_path.stat().st_size
            
            if file_size < 10:
                return False, "File too small - suspicious"
            
            # Read first 1KB for signature checks
            with open(file_path, "rb") as f:
                header = f.read(1024)
            
            # Check for common malware signatures
            suspicious_patterns = [
                b"eval(", b"exec(", b"system(",
                b"<script", b"javascript:",
                b"cmd.exe", b"powershell",
                b"\x4d\x5a\x90",  # PE executable header
            ]
            
            for pattern in suspicious_patterns:
                if pattern in header:
                    return False, f"Suspicious pattern detected: {pattern[:20]}"
            
            return True, "Basic checks passed - VirusTotal API not configured"
            
        except Exception as e:
            return True, f"Basic check error: {str(e)}"
