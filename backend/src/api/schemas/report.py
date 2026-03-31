"""
Report API Schemas - Fixed for proper validation
"""

from pydantic import BaseModel, Field, validator
from typing import List, Dict, Optional, Any
from datetime import datetime
from uuid import UUID

class VulnerabilityReportCreate(BaseModel):
    """Schema for creating vulnerability report"""
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=10)
    severity: str = Field(..., regex="^(critical|high|medium|low)$")
    steps_to_reproduce: List[str] = Field(..., min_items=1)
    impact: str = Field(..., min_length=5)
    program_id: UUID = Field(..., description="Program ID")
    
    @validator('steps_to_reproduce')
    def validate_steps(cls, v):
        if not v or len(v) == 0:
            raise ValueError('At least one step to reproduce is required')
        return v
    
    @validator('severity')
    def validate_severity(cls, v):
        allowed = ['critical', 'high', 'medium', 'low']
        if v not in allowed:
            raise ValueError(f'Severity must be one of: {", ".join(allowed)}')
        return v

class FileUpload(BaseModel):
    """Schema for file uploads"""
    filename: str
    content_type: str
    size: int = Field(..., ge=1, le=10485760)  # Max 10MB
    
    @validator('size')
    def validate_size(cls, v):
        if v > 10485760:  # 10MB
            raise ValueError('File size cannot exceed 10MB')
        return v

class ReportSubmission(BaseModel):
    """Complete report submission schema"""
    report: VulnerabilityReportCreate
    files: List[FileUpload] = Field(default_factory=list)
    
    @validator('files')
    def validate_files(cls, v):
        if len(v) > 5:  # Max 5 files
            raise ValueError('Maximum 5 files allowed per report')
        return v
