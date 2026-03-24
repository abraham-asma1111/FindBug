"""
VRT API Schemas
"""
from typing import List, Optional
from pydantic import BaseModel


class VRTEntryBase(BaseModel):
    name: str
    slug: str
    subcategory: Optional[str] = None
    description: Optional[str] = None
    cvss_min: float
    cvss_max: float
    priority: str
    remediation: Optional[str] = None
    references: List[str] = []


class VRTEntryResponse(VRTEntryBase):
    id: str
    category_id: str
    is_active: bool
    created_at: Optional[str] = None


class VRTCategoryBase(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    icon: Optional[str] = None


class VRTCategoryResponse(VRTCategoryBase):
    id: str
    is_active: bool
    created_at: Optional[str] = None


class VRTCategoryWithEntriesResponse(VRTCategoryResponse):
    entries: List[VRTEntryResponse] = []


class VRTSearchResponse(BaseModel):
    entries: List[VRTEntryResponse]
