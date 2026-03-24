"""
User API Schemas
"""
from typing import Optional, Dict
from pydantic import BaseModel, EmailStr

class ProfileUpdateBase(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None

class ResearcherProfileUpdate(BaseModel):
    bio: Optional[str] = None
    website: Optional[str] = None
    github: Optional[str] = None
    twitter: Optional[str] = None
    linkedin: Optional[str] = None

class OrganizationProfileUpdate(BaseModel):
    company_name: Optional[str] = None
    industry: Optional[str] = None
    website: Optional[str] = None

class UserProfileUpdateRequest(ProfileUpdateBase):
    profile: Optional[Dict] = None  # Will contain ResearcherProfileUpdate or OrganizationProfileUpdate depending on role

class UserProfileResponse(BaseModel):
    id: str
    email: EmailStr
    full_name: Optional[str]
    role: str
    status: str
    email_verified: bool
    created_at: Optional[str]
    last_login_at: Optional[str]
    researcher: Optional[Dict] = None
    organization: Optional[Dict] = None

class PublicProfileResponse(BaseModel):
    id: str
    full_name: Optional[str]
    role: str
    bio: Optional[str] = None
    github: Optional[str] = None
    reputation_score: Optional[float] = None
    rank: Optional[int] = None

class UserListResponse(BaseModel):
    total: int
    skip: int
    limit: int
    users: list[Dict]
