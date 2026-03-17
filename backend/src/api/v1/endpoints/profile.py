"""
Profile Management Endpoints - User profile and settings
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.domain.models.user import User
from src.domain.repositories import ResearcherRepository, OrganizationRepository
from src.api.v1.middlewares import get_current_user, get_current_researcher, get_current_organization

router = APIRouter(prefix="/profile", tags=["Profile"])


@router.get(
    "",
    response_model=dict,
    summary="Get User Profile",
    description="Get current user profile information"
)
async def get_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user profile"""
    researcher_repo = ResearcherRepository(db)
    organization_repo = OrganizationRepository(db)
    
    profile_data = {
        "user_id": str(current_user.id),
        "email": current_user.email,
        "role": current_user.role,
        "is_verified": current_user.is_verified,
        "mfa_enabled": current_user.mfa_enabled,
        "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
        "last_login_at": current_user.last_login_at.isoformat() if current_user.last_login_at else None
    }
    
    # Add role-specific data
    if current_user.role == "researcher":
        researcher = researcher_repo.get_by_user_id(str(current_user.id))
        if researcher:
            profile_data["researcher"] = {
                "researcher_id": str(researcher.id),
                "first_name": researcher.first_name,
                "last_name": researcher.last_name,
                "username": researcher.username,
                "ninja_email": researcher.ninja_email,
                "bio": researcher.bio,
                "website": researcher.website,
                "github": researcher.github,
                "twitter": researcher.twitter,
                "linkedin": researcher.linkedin,
                "reputation_score": researcher.reputation_score,
                "rank": researcher.rank,
                "kyc_status": researcher.kyc_status,
                "skills": researcher.skills
            }
    
    elif current_user.role == "organization":
        organization = organization_repo.get_by_user_id(str(current_user.id))
        if organization:
            profile_data["organization"] = {
                "organization_id": str(organization.id),
                "company_name": organization.company_name,
                "industry": organization.industry,
                "website": organization.website,
                "subscription_type": organization.subscription_type,
                "domain_verified": organization.domain_verified,
                "verification_status": organization.verification_status,
                "sso_enabled": organization.sso_enabled
            }
    
    return profile_data
