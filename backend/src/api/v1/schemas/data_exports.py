"""
Data Export Schemas — Pydantic models for data export management (FREQ-15)
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict


class DataExportRequest(BaseModel):
    """Request schema for data export"""
    export_type: str = Field(..., description="Type of data to export")
    format: str = Field("csv", description="Export format (csv, json, pdf, xlsx)")
    filters: Optional[Dict] = Field(None, description="Optional filters for the export")


class DataExportResponse(BaseModel):
    """Response schema for data export"""
    export_id: str
    export_type: str
    format: str
    filters: Optional[Dict] = None
    status: str
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    created_at: str
    completed_at: Optional[str] = None
    expires_at: Optional[str] = None
    message: Optional[str] = None


class DataExportListItem(BaseModel):
    """Single data export item in list"""
    export_id: str
    export_type: str
    format: str
    status: str
    file_size: Optional[int] = None
    created_at: str
    completed_at: Optional[str] = None
    expires_at: Optional[str] = None


class DataExportListResponse(BaseModel):
    """Response schema for data export list"""
    exports: List[DataExportListItem]
    total: int
    skip: int
    limit: int


class DataExportDownloadResponse(BaseModel):
    """Response schema for download URL"""
    export_id: str
    download_url: str
    file_size: Optional[int] = None
    expires_at: Optional[str] = None


class DataExportDeleteResponse(BaseModel):
    """Response schema for export deletion"""
    export_id: str
    message: str


class DataExportTypesResponse(BaseModel):
    """Response schema for supported export types"""
    export_types: List[str]
    formats: List[str]
