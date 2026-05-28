"""
File processing and storage service
"""
import os
import uuid
import hashlib
from pathlib import Path
from typing import Optional, Tuple, Dict, Any
import aiofiles
from fastapi import UploadFile, HTTPException
import PyPDF2
import pdfplumber
from io import BytesIO

from config import settings

class FileService:
    """Service for handling file uploads and processing"""
    
    def __init__(self):
        self.upload_dir = Path(settings.upload_dir)
        self.upload_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        (self.upload_dir / "resumes").mkdir(exist_ok=True)
        (self.upload_dir / "temp").mkdir(exist_ok=True)
    
    async def validate_file(self, file: UploadFile) -> Dict[str, Any]:
        """Validate uploaded file"""
        validation_result = {
            "valid": False,
            "errors": [],
            "warnings": [],
            "file_info": {}
        }
        
        # Check file size
        if hasattr(file, 'size') and file.size:
            if file.size > settings.max_file_size:
                validation_result["errors"].append(
                    f"File size ({file.size:,} bytes) exceeds maximum allowed size ({settings.max_file_size:,} bytes)"
                )
        
        # Check file extension
        if file.filename:
            file_ext = Path(file.filename).suffix.lower()
            if file_ext not in settings.allowed_file_types:
                validation_result["errors"].append(
                    f"File type '{file_ext}' not allowed. Allowed types: {', '.join(settings.allowed_file_types)}"
                )
            
            validation_result["file_info"]["extension"] = file_ext
            validation_result["file_info"]["filename"] = file.filename
        else:
            validation_result["errors"].append("No filename provided")
        
        # Check content type
        if file.content_type:
            validation_result["file_info"]["content_type"] = file.content_type
            
            # Validate content type matches extension
            expected_types = {
                ".pdf": ["application/pdf"],
                ".txt": ["text/plain"],
                ".doc": ["application/msword"],
                ".docx": ["application/vnd.openxmlformats-officedocument.wordprocessingml.document"]
            }
            
            if file_ext in expected_types:
                if file.content_type not in expected_types[file_ext]:
                    validation_result["warnings"].append(
                        f"Content type '{file.content_type}' doesn't match expected type for '{file_ext}'"
                    )
        
        # If no errors, mark as valid
        validation_result["valid"] = len(validation_result["errors"]) == 0
        
        return validation_result
    
    async def save_file(self, file: UploadFile, subfolder: str = "resumes") -> Tuple[str, str]:
        """Save uploaded file and return file path and hash"""
        # Generate unique filename
        file_id = str(uuid.uuid4())
        file_ext = Path(file.filename).suffix.lower() if file.filename else ""
        filename = f"{file_id}{file_ext}"
        
        # Create file path
        file_path = self.upload_dir / subfolder / filename
        
        # Read file content
        content = await file.read()
        
        # Calculate file hash
        file_hash = hashlib.sha256(content).hexdigest()
        
        # Save file
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(content)
        
        # Reset file position for further processing
        await file.seek(0)
        
        return str(file_path), file_hash
    
    async def extract_text_from_pdf(self, file_path: str) -> Tuple[str, Dict[str, Any]]:
        """Extract text from PDF file"""
        extraction_info = {
            "method": None,
            "pages": 0,
            "success": False,
            "errors": []
        }
        
        try:
            # Try pdfplumber first (better for complex layouts)
            with pdfplumber.open(file_path) as pdf:
                text_parts = []
                extraction_info["pages"] = len(pdf.pages)
                extraction_info["method"] = "pdfplumber"
                
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
                
                if text_parts:
                    extracted_text = "\n\n".join(text_parts)
                    extraction_info["success"] = True
                    return extracted_text, extraction_info
        
        except Exception as e:
            extraction_info["errors"].append(f"pdfplumber failed: {str(e)}")
        
        try:
            # Fallback to PyPDF2
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text_parts = []
                extraction_info["pages"] = len(pdf_reader.pages)
                extraction_info["method"] = "PyPDF2"
                
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
                
                if text_parts:
                    extracted_text = "\n\n".join(text_parts)
                    extraction_info["success"] = True
                    return extracted_text, extraction_info
        
        except Exception as e:
            extraction_info["errors"].append(f"PyPDF2 failed: {str(e)}")
        
        # If both methods fail
        extraction_info["success"] = False
        return "", extraction_info
    
    async def extract_text_from_file(self, file_path: str) -> Tuple[str, Dict[str, Any]]:
        """Extract text from various file types"""
        file_ext = Path(file_path).suffix.lower()
        
        if file_ext == ".pdf":
            return await self.extract_text_from_pdf(file_path)
        
        elif file_ext == ".txt":
            try:
                async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                    content = await f.read()
                return content, {"method": "direct", "success": True, "errors": []}
            except UnicodeDecodeError:
                # Try different encodings
                for encoding in ['latin-1', 'cp1252', 'iso-8859-1']:
                    try:
                        async with aiofiles.open(file_path, 'r', encoding=encoding) as f:
                            content = await f.read()
                        return content, {"method": f"direct-{encoding}", "success": True, "errors": []}
                    except UnicodeDecodeError:
                        continue
                
                return "", {"method": "direct", "success": False, "errors": ["Unable to decode text file"]}
        
        elif file_ext in [".doc", ".docx"]:
            # For now, return empty text with a note
            # In a full implementation, you'd use python-docx or similar
            return "", {
                "method": "unsupported", 
                "success": False, 
                "errors": [f"Text extraction for {file_ext} files not yet implemented"]
            }
        
        else:
            return "", {
                "method": "unknown", 
                "success": False, 
                "errors": [f"Unsupported file type: {file_ext}"]
            }
    
    async def process_resume_file(self, file: UploadFile) -> Dict[str, Any]:
        """Complete resume file processing pipeline"""
        result = {
            "success": False,
            "file_path": None,
            "file_hash": None,
            "extracted_text": "",
            "file_info": {},
            "extraction_info": {},
            "validation": {},
            "errors": []
        }
        
        try:
            # Validate file
            validation = await self.validate_file(file)
            result["validation"] = validation
            
            if not validation["valid"]:
                result["errors"].extend(validation["errors"])
                return result
            
            # Save file
            file_path, file_hash = await self.save_file(file, "resumes")
            result["file_path"] = file_path
            result["file_hash"] = file_hash
            result["file_info"] = validation["file_info"]
            result["file_info"]["size"] = os.path.getsize(file_path)
            
            # Extract text
            extracted_text, extraction_info = await self.extract_text_from_file(file_path)
            result["extracted_text"] = extracted_text
            result["extraction_info"] = extraction_info
            
            if not extraction_info["success"]:
                result["errors"].extend(extraction_info["errors"])
                # Don't return here - file is saved even if text extraction fails
            
            result["success"] = True
            return result
            
        except Exception as e:
            result["errors"].append(f"Unexpected error during file processing: {str(e)}")
            return result
    
    def delete_file(self, file_path: str) -> bool:
        """Delete a file"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception:
            return False
    
    def get_file_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Get file information"""
        if not os.path.exists(file_path):
            return None
        
        stat = os.stat(file_path)
        return {
            "path": file_path,
            "size": stat.st_size,
            "created": stat.st_ctime,
            "modified": stat.st_mtime,
            "extension": Path(file_path).suffix.lower()
        }