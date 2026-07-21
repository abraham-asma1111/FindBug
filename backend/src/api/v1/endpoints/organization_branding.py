"""Organization Branding Configuration API Endpoints."""
import json
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from pydantic import BaseModel

from src.core.database import get_db
from src.api.v1.middlewares.auth import get_current_user
from src.domain.models.user import User, UserRole
from src.domain.models.organization import Organization
from src.services.file_storage_service import FileStorageService

router = APIRouter(prefix="/organization/branding", tags=["organization-branding"])


class BrandingUpdateRequest(BaseModel):
    """Request model for updating branding settings."""
    brand_color: Optional[str] = None
    theme_settings: Optional[dict] = None


@router.get("/")
def get_organization_branding(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current organization's branding configuration.
    
    Requires: Organization role
    """
    # Check if user is organization
    if current_user.role.lower() not in ["organization"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organizations can access branding settings"
        )
    
    # Get organization
    organization = db.query(Organization).filter(
        Organization.user_id == current_user.id
    ).first()
    
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    return {
        "logo_url": organization.logo_url,
        "cover_image_url": organization.cover_image_url,
        "brand_color": organization.brand_color,
        "theme_settings": json.loads(organization.theme_settings) if organization.theme_settings else None,
    }


@router.post("/upload-logo")
async def upload_logo(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload organization logo.
    
    Requires: Organization role
    """
    # Check if user is organization
    if current_user.role.lower() not in ["organization"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organizations can upload logos"
        )
    
    # Get organization
    organization = db.query(Organization).filter(
        Organization.user_id == current_user.id
    ).first()
    
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    # Validate file type
    import os
    file_extension = os.path.splitext(file.filename)[1].lower()
    if file_extension not in ['.jpg', '.jpeg', '.png', '.gif', '.svg']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only image files are allowed (jpg, jpeg, png, gif, svg)"
        )
    
    # Check file size
    content = await file.read()
    if len(content) > 5 * 1024 * 1024:  # 5MB limit
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds 5MB limit"
        )
    
    # Reset file pointer
    await file.seek(0)
    
    # Upload file
    storage_service = FileStorageService(db)
    file_metadata = await storage_service.upload_file(
        file=file,
        user_id=current_user.id,
        file_type="logo"
    )
    
    # Update organization logo URL
    organization.logo_url = file_metadata["storage_key"]
    db.commit()
    db.refresh(organization)
    
    return {
        "logo_url": organization.logo_url,
        "message": "Logo uploaded successfully"
    }


@router.post("/upload-cover")
async def upload_cover_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload organization cover/background image.
    
    Requires: Organization role
    """
    # Check if user is organization
    if current_user.role.lower() not in ["organization"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organizations can upload cover images"
        )
    
    # Get organization
    organization = db.query(Organization).filter(
        Organization.user_id == current_user.id
    ).first()
    
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    # Validate file type
    import os
    file_extension = os.path.splitext(file.filename)[1].lower()
    if file_extension not in ['.jpg', '.jpeg', '.png', '.gif']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only image files are allowed (jpg, jpeg, png, gif)"
        )
    
    # Check file size
    content = await file.read()
    if len(content) > 10 * 1024 * 1024:  # 10MB limit
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds 10MB limit"
        )
    
    # Reset file pointer
    await file.seek(0)
    
    # Upload file
    storage_service = FileStorageService(db)
    file_metadata = await storage_service.upload_file(
        file=file,
        user_id=current_user.id,
        file_type="cover"
    )
    
    # Update organization cover image URL
    organization.cover_image_url = file_metadata["storage_key"]
    db.commit()
    db.refresh(organization)
    
    return {
        "cover_image_url": organization.cover_image_url,
        "message": "Cover image uploaded successfully"
    }


@router.put("/settings")
def update_branding_settings(
    request: BrandingUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update organization branding settings (colors, theme).
    
    Requires: Organization role
    """
    # Check if user is organization
    if current_user.role.lower() not in ["organization"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organizations can update branding settings"
        )
    
    # Get organization
    organization = db.query(Organization).filter(
        Organization.user_id == current_user.id
    ).first()
    
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    # Validate brand color format (hex color)
    if request.brand_color:
        import re
        if not re.match(r'^#[0-9A-Fa-f]{6}$', request.brand_color):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid brand color format. Use hex format (e.g., #3B82F6)"
            )
        organization.brand_color = request.brand_color
    
    # Update theme settings
    if request.theme_settings:
        organization.theme_settings = json.dumps(request.theme_settings)
    
    db.commit()
    db.refresh(organization)
    
    return {
        "brand_color": organization.brand_color,
        "theme_settings": json.loads(organization.theme_settings) if organization.theme_settings else None,
        "message": "Branding settings updated successfully"
    }


@router.delete("/logo")
def delete_logo(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Remove organization logo.
    
    Requires: Organization role
    """
    # Check if user is organization
    if current_user.role.lower() not in ["organization"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organizations can delete logos"
        )
    
    # Get organization
    organization = db.query(Organization).filter(
        Organization.user_id == current_user.id
    ).first()
    
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    organization.logo_url = None
    db.commit()
    
    return {
        "message": "Logo removed successfully"
    }


@router.delete("/cover")
def delete_cover_image(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Remove organization cover image.
    
    Requires: Organization role
    """
    # Check if user is organization
    if current_user.role.lower() not in ["organization"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organizations can delete cover images"
        )
    
    # Get organization
    organization = db.query(Organization).filter(
        Organization.user_id == current_user.id
    ).first()
    
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    organization.cover_image_url = None
    db.commit()
    
    return {
        "message": "Cover image removed successfully"
    }
