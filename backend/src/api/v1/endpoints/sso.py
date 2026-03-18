"""
SSO (Single Sign-On) Endpoints for Organizations
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel

from src.core.database import get_db
from src.core.security import SecurityAudit, TokenSecurity
from src.core.sso_service import SAMLService
from src.domain.models.user import User
from src.domain.repositories import OrganizationRepository, UserRepository
from src.api.v1.middlewares import get_current_organization

router = APIRouter(prefix="/sso", tags=["SSO"])


class ConfigureSSORequest(BaseModel):
    """Request to configure SSO"""
    sso_provider: str  # okta, microsoft, google, onelogin, auth0, custom
    sso_metadata_url: str


class SSOLoginRequest(BaseModel):
    """Request to initiate SSO login"""
    organization_domain: str


@router.post(
    "/configure",
    response_model=dict,
    summary="Configure SSO",
    description="Configure SSO for organization (admin only)"
)
@router.get(
    "/configure",
    response_model=dict,
    summary="Configure SSO (GET)",
    description="Configure SSO for organization (admin only) (GET method)"
)
async def configure_sso(
    data: ConfigureSSORequest = None,
    request: Request = None,
    current_user: User = Depends(get_current_organization),
    db: Session = Depends(get_db)
):
    """
    Configure SSO for organization
    
    Steps:
    1. Organization admin provides IdP metadata URL
    2. System fetches and validates metadata
    3. Stores SSO configuration
    4. Enables SSO for organization
    """
    # Handle GET requests without data
    if data is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="SSO configuration data required"
        )
    
    organization_repo = OrganizationRepository(db)
    organization = organization_repo.get_by_user_id(str(current_user.id))
    
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    # Fetch and validate IdP metadata
    metadata = await SAMLService.fetch_idp_metadata(data.sso_metadata_url)
    
    if not metadata.get("valid"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=metadata.get("error", "Invalid IdP metadata")
        )
    
    # Update organization SSO configuration
    organization.sso_enabled = True
    organization.sso_provider = data.sso_provider
    organization.sso_metadata_url = data.sso_metadata_url
    db.commit()
    
    # Log security event
    SecurityAudit.log_event(
        user_id=str(current_user.id),
        event_type="sso_configured",
        ip_address=request.client.host,
        details={"provider": data.sso_provider}
    )
    
    return {
        "success": True,
        "message": "SSO configured successfully",
        "sso_provider": data.sso_provider,
        "sso_url": metadata["sso_url"]
    }


@router.post(
    "/login",
    summary="Initiate SSO Login",
    description="Initiate SSO login flow for organization"
)
@router.get(
    "/login",
    summary="Initiate SSO Login (GET)",
    description="Initiate SSO login flow for organization (GET method)"
)
async def sso_login(
    data: SSOLoginRequest = None,
    db: Session = Depends(get_db)
):
    """
    Initiate SSO login
    
    Flow:
    1. User enters organization domain
    2. System looks up organization SSO config
    3. Redirects to IdP SSO URL with SAML request
    """
    # Handle GET requests without data
    if data is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization domain required"
        )
    
    organization_repo = OrganizationRepository(db)
    
    # Find organization by domain
    organizations = db.query(organization_repo.model).all()
    organization = None
    
    for org in organizations:
        if org.verified_domains and data.organization_domain in org.verified_domains:
            organization = org
            break
    
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found or SSO not configured"
        )
    
    if not organization.sso_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="SSO not enabled for this organization"
        )
    
    # Fetch IdP metadata
    metadata = await SAMLService.fetch_idp_metadata(organization.sso_metadata_url)
    
    if not metadata.get("valid"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="SSO configuration error"
        )
    
    # Generate SAML request
    saml_request = SAMLService.generate_saml_request(
        str(organization.id),
        metadata["sso_url"]
    )
    
    # Redirect to IdP with SAML request
    redirect_url = f"{metadata['sso_url']}?SAMLRequest={saml_request}"
    
    return RedirectResponse(url=redirect_url, status_code=status.HTTP_302_FOUND)


@router.post(
    "/callback",
    response_model=dict,
    summary="SSO Callback",
    description="Handle SAML response from IdP"
)
async def sso_callback(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    SSO callback endpoint
    
    IdP sends SAML response here after authentication
    """
    # Get SAML response from form data
    form_data = await request.form()
    saml_response = form_data.get("SAMLResponse")
    
    if not saml_response:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing SAML response"
        )
    
    # Parse SAML response
    user_data = SAMLService.parse_saml_response(saml_response)
    
    if not user_data.get("valid"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=user_data.get("error", "Invalid SAML response")
        )
    
    # Find or create user
    user_repo = UserRepository(db)
    organization_repo = OrganizationRepository(db)
    
    user = user_repo.get_by_email(user_data["email"])
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found. Please contact your organization admin."
        )
    
    # Verify user belongs to organization with SSO enabled
    if user.role != "organization":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="SSO is only for organization users"
        )
    
    organization = organization_repo.get_by_user_id(str(user.id))
    if not organization or not organization.sso_enabled:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="SSO not enabled for this organization"
        )
    
    # Generate JWT tokens
    token_data = {
        "sub": user.email,
        "user_id": str(user.id),
        "role": user.role.value
    }
    access_token = TokenSecurity.create_access_token(token_data)
    refresh_token = TokenSecurity.create_refresh_token()
    
    # Update user
    user.last_login_at = datetime.utcnow()
    user_repo.update(user)
    
    # Log security event
    SecurityAudit.log_event(
        user_id=str(user.id),
        event_type="sso_login",
        ip_address=request.client.host,
        details={"provider": organization.sso_provider}
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user_id": str(user.id),
        "email": user.email,
        "role": user.role,
        "sso_provider": organization.sso_provider
    }


@router.get(
    "/status",
    response_model=dict,
    summary="Get SSO Status",
    description="Get SSO configuration status for organization"
)
async def get_sso_status(
    current_user: User = Depends(get_current_organization),
    db: Session = Depends(get_db)
):
    """Get SSO configuration status"""
    organization_repo = OrganizationRepository(db)
    organization = organization_repo.get_by_user_id(str(current_user.id))
    
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    return {
        "sso_enabled": organization.sso_enabled,
        "sso_provider": organization.sso_provider,
        "sso_configured": organization.sso_metadata_url is not None
    }


@router.post(
    "/disable",
    response_model=dict,
    summary="Disable SSO",
    description="Disable SSO for organization"
)
@router.get(
    "/disable",
    response_model=dict,
    summary="Disable SSO (GET)",
    description="Disable SSO for organization (GET method)"
)
async def disable_sso(
    request: Request = None,
    current_user: User = Depends(get_current_organization),
    db: Session = Depends(get_db)
):
    """Disable SSO"""
    organization_repo = OrganizationRepository(db)
    organization = organization_repo.get_by_user_id(str(current_user.id))
    
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    organization.sso_enabled = False
    db.commit()
    
    # Log security event
    SecurityAudit.log_event(
        user_id=str(current_user.id),
        event_type="sso_disabled",
        ip_address=request.client.host,
        details={}
    )
    
    return {
        "success": True,
        "message": "SSO disabled successfully"
    }
