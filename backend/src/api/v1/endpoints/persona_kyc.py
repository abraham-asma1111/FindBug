"""
Persona KYC Integration Endpoints
Handles Persona verification flow for researchers and organizations
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request, Header
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID

from src.core.database import get_db
from src.core.security import SecurityAudit
from src.services.persona_service import PersonaService
from src.domain.models.user import User
from src.domain.models.kyc import KYCVerification
from src.core.dependencies import get_current_user, require_financial
from src.core.logging import get_logger
from datetime import datetime

logger = get_logger(__name__)

router = APIRouter(prefix="/kyc/persona", tags=["Persona KYC"])


@router.post(
    "/start",
    summary="Start Persona Verification",
    description="Initialize Persona verification flow for current user"
)
async def start_persona_verification(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Start Persona verification flow.
    
    Returns inquiry_id and session_token for frontend Persona component.
    """
    try:
        persona_service = PersonaService()
        
        # Determine user role (researcher or organization)
        from src.domain.models.researcher import Researcher
        from src.domain.models.organization import Organization
        
        researcher = db.query(Researcher).filter(Researcher.user_id == current_user.id).first()
        organization = db.query(Organization).filter(Organization.user_id == current_user.id).first()
        
        if researcher:
            user_role = "researcher"
            reference_id = f"researcher_{researcher.id}"
        elif organization:
            user_role = "organization"
            reference_id = f"organization_{organization.id}"
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User must be a researcher or organization"
            )
        
        # Create Persona inquiry
        inquiry_data = await persona_service.create_inquiry(
            user_id=str(current_user.id),
            user_role=user_role,
            reference_id=reference_id
        )
        
        # Create or update KYC record
        kyc = db.query(KYCVerification).filter(
            KYCVerification.user_id == current_user.id
        ).first()
        
        if not kyc:
            kyc = KYCVerification(
                user_id=current_user.id,
                status="pending",
                persona_inquiry_id=inquiry_data["inquiry_id"],
                persona_template_id=inquiry_data["template_id"],
                persona_status="created"
            )
            db.add(kyc)
        else:
            kyc.persona_inquiry_id = inquiry_data["inquiry_id"]
            kyc.persona_template_id = inquiry_data["template_id"]
            kyc.persona_status = "created"
            kyc.status = "pending"
        
        db.commit()
        
        # Log security event
        SecurityAudit.log_security_event(
            "PERSONA_VERIFICATION_STARTED",
            str(current_user.id),
            {
                "inquiry_id": inquiry_data["inquiry_id"],
                "user_role": user_role
            },
            request
        )
        
        return {
            "inquiry_id": inquiry_data["inquiry_id"],
            "template_id": inquiry_data["template_id"],
            "status": inquiry_data["status"],
            "user_role": user_role,
            "session_token": inquiry_data.get("session_token"),
            "one_time_link": inquiry_data.get("one_time_link")
        }
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        # Log the technical error but return user-friendly message
        logger.error(f"Failed to start Persona verification: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to start verification. Please try again or contact support."
        )


@router.post(
    "/verify",
    summary="Verify Persona Inquiry",
    description="Server-side verification of Persona inquiry status"
)
async def verify_persona_inquiry(
    inquiry_id: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Verify Persona inquiry status (server-side validation).
    
    Called after user completes Persona flow in frontend.
    """
    try:
        persona_service = PersonaService()
        
        # Get KYC record
        kyc = db.query(KYCVerification).filter(
            KYCVerification.user_id == current_user.id,
            KYCVerification.persona_inquiry_id == inquiry_id
        ).first()
        
        if not kyc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="KYC verification not found"
            )
        
        # Verify with Persona API
        is_approved = await persona_service.verify_inquiry(inquiry_id)
        
        if is_approved:
            kyc.status = "approved"
            kyc.persona_status = "completed"
            kyc.persona_verified_at = datetime.utcnow()
            kyc.verified_at = datetime.utcnow()
            
            # Log security event
            SecurityAudit.log_security_event(
                "PERSONA_VERIFICATION_APPROVED",
                str(current_user.id),
                {"inquiry_id": inquiry_id},
                request
            )
        else:
            kyc.status = "rejected"
            kyc.persona_status = "failed"
            kyc.rejection_reason = "Persona verification failed"
            
            # Log security event
            SecurityAudit.log_security_event(
                "PERSONA_VERIFICATION_REJECTED",
                str(current_user.id),
                {"inquiry_id": inquiry_id},
                request
            )
        
        db.commit()
        
        return {
            "inquiry_id": inquiry_id,
            "status": kyc.status,
            "persona_status": kyc.persona_status,
            "verified_at": kyc.verified_at.isoformat() if kyc.verified_at else None
        }
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to verify Persona inquiry: {str(e)}"
        )


@router.post(
    "/webhook",
    summary="Persona Webhook Handler",
    description="Handle Persona webhook events"
)
async def persona_webhook(
    request: Request,
    persona_signature: Optional[str] = Header(None, alias="Persona-Signature"),
    db: Session = Depends(get_db)
):
    """
    Handle Persona webhook events.
    
    Persona sends webhooks when inquiry status changes.
    """
    try:
        persona_service = PersonaService()
        
        # Get raw body for signature verification
        body = await request.body()
        
        # Verify webhook signature
        if persona_signature:
            is_valid = persona_service.verify_webhook_signature(body, persona_signature)
            if not is_valid:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid webhook signature"
                )
        
        # Parse webhook payload
        payload = await request.json()
        
        event_type = payload.get("data", {}).get("type")
        inquiry_id = payload.get("data", {}).get("id")
        attributes = payload.get("data", {}).get("attributes", {})
        
        if event_type == "inquiry" and inquiry_id:
            # Find KYC record
            kyc = db.query(KYCVerification).filter(
                KYCVerification.persona_inquiry_id == inquiry_id
            ).first()
            
            if kyc:
                inquiry_status = attributes.get("status")
                decision = attributes.get("decision")
                
                # Update KYC status based on Persona decision
                if inquiry_status == "completed" and decision == "approved":
                    kyc.status = "approved"
                    kyc.persona_status = "completed"
                    kyc.persona_verified_at = datetime.utcnow()
                    kyc.verified_at = datetime.utcnow()
                elif inquiry_status == "completed" and decision in ["declined", "rejected"]:
                    kyc.status = "rejected"
                    kyc.persona_status = "failed"
                    kyc.rejection_reason = f"Persona decision: {decision}"
                else:
                    kyc.persona_status = inquiry_status
                
                db.commit()
        
        return {"status": "success", "message": "Webhook processed"}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Webhook processing failed: {str(e)}"
        )


@router.get(
    "/status",
    summary="Get Persona Verification Status",
    description="Get current Persona verification status for user"
)
async def get_persona_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get Persona verification status for current user."""
    try:
        kyc = db.query(KYCVerification).filter(
            KYCVerification.user_id == current_user.id
        ).first()
        
        if not kyc:
            return {
                "status": "not_started",
                "persona_inquiry_id": None,
                "persona_status": None
            }
        
        return {
            "status": kyc.status,
            "persona_inquiry_id": kyc.persona_inquiry_id,
            "persona_status": kyc.persona_status,
            "persona_verified_at": kyc.persona_verified_at.isoformat() if kyc.persona_verified_at else None,
            "verified_at": kyc.verified_at.isoformat() if kyc.verified_at else None
        }
    
    except Exception as e:
        # Log the technical error but return user-friendly message
        logger.error(f"Failed to get Persona status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to load verification status. Please refresh the page."
        )
