"""
Payment Methods API Endpoints - Fix for missing 404 endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict
from uuid import UUID

from src.core.database import get_db
from src.services.payment_service import PaymentService
from ..schemas.payment import PaymentMethodCreate, PaymentMethodResponse

router = APIRouter(prefix="/payment-methods", tags=["Payment Methods"])

# Finance Officer Endpoints - Must come BEFORE /{user_id} route
@router.get("/all")
async def get_all_payment_methods(
    db: Session = Depends(get_db)
):
    """
    Get ALL payment methods (pending, approved, rejected) for finance officer.
    Returns payment methods with researcher info and KYC status.
    """
    try:
        from src.domain.models.payment_extended import PaymentMethod
        from src.domain.models.researcher import Researcher
        from src.domain.models.user import User
        from src.domain.models.kyc import KYCVerification
        from sqlalchemy import func, and_
        
        # Subquery to get the latest KYC record per user
        latest_kyc_subquery = db.query(
            KYCVerification.user_id,
            func.max(KYCVerification.created_at).label('max_created_at')
        ).group_by(
            KYCVerification.user_id
        ).subquery()
        
        # Query ALL payment methods with researcher and latest KYC info
        results = db.query(
            PaymentMethod,
            User.email,
            Researcher.username,
            KYCVerification.status.label('kyc_status'),
            KYCVerification.email_verified,
            KYCVerification.persona_verified_at
        ).join(
            User, PaymentMethod.user_id == User.id
        ).outerjoin(
            Researcher, User.id == Researcher.user_id
        ).outerjoin(
            latest_kyc_subquery,
            User.id == latest_kyc_subquery.c.user_id
        ).outerjoin(
            KYCVerification,
            and_(
                User.id == KYCVerification.user_id,
                KYCVerification.created_at == latest_kyc_subquery.c.max_created_at
            )
        ).order_by(
            PaymentMethod.created_at.desc()
        ).all()
        
        payment_methods = []
        for pm, email, username, kyc_status, email_verified, persona_verified_at in results:
            # Ensure consistent boolean conversion for persona_verified
            persona_verified = bool(persona_verified_at) if persona_verified_at else False
            
            payment_methods.append({
                "id": str(pm.id),
                "user_id": str(pm.user_id),
                "method_type": pm.method_type,
                "account_name": pm.account_name,
                "account_number": pm.account_number,
                "bank_name": pm.bank_name,
                "phone_number": pm.phone_number,
                "is_default": pm.is_default,
                "is_verified": pm.is_verified,
                "status": "approved" if pm.is_verified else "pending",  # Add status field
                "created_at": pm.created_at.isoformat() if pm.created_at else None,
                "researcher": {
                    "email": email,
                    "full_name": username or email.split('@')[0],
                    "username": username
                },
                "kyc": {
                    "status": kyc_status,
                    "email_verified": bool(email_verified) if email_verified is not None else False,
                    "persona_verified": persona_verified
                } if kyc_status else None
            })
        
        return payment_methods
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch payment methods: {str(e)}"
        )


@router.get("/status/pending")
async def get_pending_payment_methods(
    db: Session = Depends(get_db)
):
    """
    Get pending payment methods (status='pending').
    Returns payment methods with researcher info and KYC status.
    """
    try:
        from src.domain.models.payment_extended import PaymentMethod
        from src.domain.models.researcher import Researcher
        from src.domain.models.user import User
        from src.domain.models.kyc import KYCVerification
        from sqlalchemy import func, and_, text
        
        # Query pending payment methods using status column
        results = db.execute(text("""
            SELECT 
                pm.id, pm.user_id, pm.method_type, pm.account_name, pm.account_number,
                pm.bank_name, pm.phone_number, pm.is_default, pm.is_verified,
                pm.created_at,
                u.email, r.username,
                k.status as kyc_status, k.email_verified, k.persona_verified_at
            FROM payment_methods pm
            JOIN users u ON pm.user_id = u.id
            LEFT JOIN researchers r ON u.id = r.user_id
            LEFT JOIN (
                SELECT user_id, MAX(created_at) as max_created_at
                FROM kyc_verifications
                GROUP BY user_id
            ) latest_kyc ON u.id = latest_kyc.user_id
            LEFT JOIN kyc_verifications k ON u.id = k.user_id 
                AND k.created_at = latest_kyc.max_created_at
            WHERE pm.status = 'pending'
            ORDER BY pm.created_at DESC
        """)).fetchall()
        
        payment_methods = []
        for row in results:
            persona_verified = bool(row.persona_verified_at) if row.persona_verified_at else False
            
            payment_methods.append({
                "id": str(row.id),
                "user_id": str(row.user_id),
                "method_type": row.method_type,
                "account_name": row.account_name,
                "account_number": row.account_number,
                "bank_name": row.bank_name,
                "phone_number": row.phone_number,
                "is_default": row.is_default,
                "is_verified": row.is_verified,
                "status": "pending",
                "created_at": row.created_at.isoformat() if row.created_at else None,
                "researcher": {
                    "email": row.email,
                    "full_name": row.username or row.email.split('@')[0],
                    "username": row.username
                },
                "kyc": {
                    "status": row.kyc_status,
                    "email_verified": bool(row.email_verified) if row.email_verified is not None else False,
                    "persona_verified": persona_verified
                } if row.kyc_status else None
            })
        
        return payment_methods
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch pending payment methods: {str(e)}"
        )


@router.get("/status/approved")
async def get_approved_payment_methods(
    db: Session = Depends(get_db)
):
    """
    Get approved payment methods (status='approved').
    Returns payment methods with researcher info and KYC status.
    """
    try:
        from src.domain.models.payment_extended import PaymentMethod
        from src.domain.models.researcher import Researcher
        from src.domain.models.user import User
        from src.domain.models.kyc import KYCVerification
        from sqlalchemy import func, and_, text
        
        # Query approved payment methods using status column
        results = db.execute(text("""
            SELECT 
                pm.id, pm.user_id, pm.method_type, pm.account_name, pm.account_number,
                pm.bank_name, pm.phone_number, pm.is_default, pm.is_verified,
                pm.created_at,
                u.email, r.username,
                k.status as kyc_status, k.email_verified, k.persona_verified_at
            FROM payment_methods pm
            JOIN users u ON pm.user_id = u.id
            LEFT JOIN researchers r ON u.id = r.user_id
            LEFT JOIN (
                SELECT user_id, MAX(created_at) as max_created_at
                FROM kyc_verifications
                GROUP BY user_id
            ) latest_kyc ON u.id = latest_kyc.user_id
            LEFT JOIN kyc_verifications k ON u.id = k.user_id 
                AND k.created_at = latest_kyc.max_created_at
            WHERE pm.status = 'approved'
            ORDER BY pm.created_at DESC
        """)).fetchall()
        
        payment_methods = []
        for row in results:
            persona_verified = bool(row.persona_verified_at) if row.persona_verified_at else False
            
            payment_methods.append({
                "id": str(row.id),
                "user_id": str(row.user_id),
                "method_type": row.method_type,
                "account_name": row.account_name,
                "account_number": row.account_number,
                "bank_name": row.bank_name,
                "phone_number": row.phone_number,
                "is_default": row.is_default,
                "is_verified": row.is_verified,
                "status": "approved",
                "created_at": row.created_at.isoformat() if row.created_at else None,
                "researcher": {
                    "email": row.email,
                    "full_name": row.username or row.email.split('@')[0],
                    "username": row.username
                },
                "kyc": {
                    "status": row.kyc_status,
                    "email_verified": bool(row.email_verified) if row.email_verified is not None else False,
                    "persona_verified": persona_verified
                } if row.kyc_status else None
            })
        
        return payment_methods
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch approved payment methods: {str(e)}"
        )


@router.get("/status/rejected")
async def get_rejected_payment_methods(
    db: Session = Depends(get_db)
):
    """
    Get rejected payment methods (status='rejected').
    Returns payment methods with researcher info, KYC status, and rejection details.
    """
    try:
        from src.domain.models.payment_extended import PaymentMethod
        from src.domain.models.researcher import Researcher
        from src.domain.models.user import User
        from src.domain.models.kyc import KYCVerification
        from sqlalchemy import func, and_, text
        
        latest_kyc_subquery = db.query(
            KYCVerification.user_id,
            func.max(KYCVerification.created_at).label('max_created_at')
        ).group_by(
            KYCVerification.user_id
        ).subquery()
        
        # Query rejected payment methods
        results = db.execute(text("""
            SELECT 
                pm.id, pm.user_id, pm.method_type, pm.account_name, pm.account_number,
                pm.bank_name, pm.phone_number, pm.is_default, pm.is_verified,
                pm.created_at, pm.rejection_reason, pm.rejected_at,
                u.email, r.username,
                k.status as kyc_status, k.email_verified, k.persona_verified_at
            FROM payment_methods pm
            JOIN users u ON pm.user_id = u.id
            LEFT JOIN researchers r ON u.id = r.user_id
            LEFT JOIN (
                SELECT user_id, MAX(created_at) as max_created_at
                FROM kyc_verifications
                GROUP BY user_id
            ) latest_kyc ON u.id = latest_kyc.user_id
            LEFT JOIN kyc_verifications k ON u.id = k.user_id 
                AND k.created_at = latest_kyc.max_created_at
            WHERE pm.status = 'rejected'
            ORDER BY pm.rejected_at DESC
        """)).fetchall()
        
        payment_methods = []
        for row in results:
            persona_verified = bool(row.persona_verified_at) if row.persona_verified_at else False
            
            payment_methods.append({
                "id": str(row.id),
                "user_id": str(row.user_id),
                "method_type": row.method_type,
                "account_name": row.account_name,
                "account_number": row.account_number,
                "bank_name": row.bank_name,
                "phone_number": row.phone_number,
                "is_default": row.is_default,
                "is_verified": row.is_verified,
                "status": "rejected",
                "rejection_reason": row.rejection_reason,
                "rejected_at": row.rejected_at.isoformat() if row.rejected_at else None,
                "created_at": row.created_at.isoformat() if row.created_at else None,
                "researcher": {
                    "email": row.email,
                    "full_name": row.username or row.email.split('@')[0],
                    "username": row.username
                },
                "kyc": {
                    "status": row.kyc_status,
                    "email_verified": bool(row.email_verified) if row.email_verified is not None else False,
                    "persona_verified": persona_verified
                } if row.kyc_status else None
            })
        
        return payment_methods
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch rejected payment methods: {str(e)}"
        )


# Action routes - Must come BEFORE generic /{method_id} routes
@router.post("/{method_id}/approve")
async def approve_payment_method(
    method_id: UUID,
    db: Session = Depends(get_db)
):
    """Approve payment method (Finance Officer only)"""
    try:
        from src.domain.models.payment_extended import PaymentMethod
        from datetime import datetime
        from sqlalchemy import text
        
        method = db.query(PaymentMethod).filter(
            PaymentMethod.id == method_id
        ).first()
        
        if not method:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment method not found"
            )
        
        # Update verification status and set status to 'approved'
        db.execute(text("""
            UPDATE payment_methods 
            SET is_verified = true,
                status = 'approved',
                updated_at = :updated_at
            WHERE id = :method_id
        """), {
            "updated_at": datetime.utcnow(),
            "method_id": str(method_id)
        })
        
        db.commit()
        
        return {
            "message": "Payment method approved successfully",
            "method_id": str(method_id),
            "is_verified": True,
            "status": "approved"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to approve payment method: {str(e)}"
        )


@router.post("/{method_id}/reject")
async def reject_payment_method(
    method_id: UUID,
    request_data: Dict,
    db: Session = Depends(get_db)
):
    """Reject payment method (Finance Officer only)"""
    try:
        from src.domain.models.payment_extended import PaymentMethod
        from datetime import datetime
        
        method = db.query(PaymentMethod).filter(
            PaymentMethod.id == method_id
        ).first()
        
        if not method:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment method not found"
            )
        
        reason = request_data.get("reason", "No reason provided")
        
        # Mark as rejected instead of deleting (for audit trail and researcher notification)
        from sqlalchemy import text
        db.execute(text("""
            UPDATE payment_methods 
            SET status = 'rejected',
                rejection_reason = :reason,
                rejected_at = :rejected_at,
                updated_at = :updated_at
            WHERE id = :method_id
        """), {
            "reason": reason,
            "rejected_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "method_id": str(method_id)
        })
        
        db.commit()
        
        return {
            "message": "Payment method rejected",
            "method_id": str(method_id),
            "reason": reason
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reject payment method: {str(e)}"
        )


@router.post("/{method_id}/set-default")
async def set_default_payment_method(
    method_id: UUID,
    request_data: Dict,
    db: Session = Depends(get_db)
):
    """Set default payment method"""
    try:
        service = PaymentService(db)
        user_id = request_data.get("user_id")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="user_id is required"
            )
        success = service.set_default_payment_method(str(method_id), str(user_id))
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment method not found"
            )
        return {"message": "Default payment method updated successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# Detail route - Must come BEFORE generic /{user_id} route
@router.get("/details/{method_id}")
async def get_payment_method_details(
    method_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific payment method.
    Returns payment method with researcher info and KYC status.
    """
    try:
        from src.domain.models.payment_extended import PaymentMethod
        from src.domain.models.researcher import Researcher
        from src.domain.models.user import User
        from src.domain.models.kyc import KYCVerification
        from sqlalchemy import func, and_, text
        
        # Query payment method with researcher and latest KYC info
        result = db.execute(text("""
            SELECT 
                pm.id, pm.user_id, pm.method_type, pm.account_name, pm.account_number,
                pm.bank_name, pm.phone_number, pm.is_default, pm.is_verified,
                pm.status, pm.rejection_reason, pm.rejected_at, pm.created_at, pm.updated_at,
                u.email, r.username,
                k.status as kyc_status, k.email_verified, k.persona_verified_at
            FROM payment_methods pm
            JOIN users u ON pm.user_id = u.id
            LEFT JOIN researchers r ON u.id = r.user_id
            LEFT JOIN (
                SELECT user_id, MAX(created_at) as max_created_at
                FROM kyc_verifications
                GROUP BY user_id
            ) latest_kyc ON u.id = latest_kyc.user_id
            LEFT JOIN kyc_verifications k ON u.id = k.user_id 
                AND k.created_at = latest_kyc.max_created_at
            WHERE pm.id = :method_id
        """), {"method_id": str(method_id)}).fetchone()
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment method not found"
            )
        
        persona_verified = bool(result.persona_verified_at) if result.persona_verified_at else False
        
        payment_method = {
            "id": str(result.id),
            "user_id": str(result.user_id),
            "method_type": result.method_type,
            "account_name": result.account_name,
            "account_number": result.account_number,
            "bank_name": result.bank_name,
            "phone_number": result.phone_number,
            "is_default": result.is_default,
            "is_verified": result.is_verified,
            "status": result.status,
            "rejection_reason": result.rejection_reason,
            "rejected_at": result.rejected_at.isoformat() if result.rejected_at else None,
            "created_at": result.created_at.isoformat() if result.created_at else None,
            "updated_at": result.updated_at.isoformat() if result.updated_at else None,
            "researcher": {
                "email": result.email,
                "full_name": result.username or result.email.split('@')[0],
                "username": result.username
            },
            "kyc": {
                "status": result.kyc_status,
                "email_verified": bool(result.email_verified) if result.email_verified is not None else False,
                "persona_verified": persona_verified
            } if result.kyc_status else None
        }
        
        return payment_method
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch payment method details: {str(e)}"
        )


# Generic routes - MUST come AFTER specific action routes
@router.get("/{user_id}", response_model=List[PaymentMethodResponse])
async def get_payment_methods(
    user_id: UUID,
    db: Session = Depends(get_db)
):
    """Get user's payment methods"""
    try:
        service = PaymentService(db)
        methods = service.get_user_payment_methods(str(user_id))
        return [PaymentMethodResponse.from_orm(method) for method in methods]
    except HTTPException:
        # Re-raise HTTP exceptions (like 403 for KYC) without wrapping
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/{user_id}", response_model=PaymentMethodResponse)
async def add_payment_method(
    user_id: UUID,
    method_data: PaymentMethodCreate,
    db: Session = Depends(get_db)
):
    """Add new payment method"""
    try:
        service = PaymentService(db)
        method = service.add_payment_method(str(user_id), method_data.dict())
        return PaymentMethodResponse.from_orm(method)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.put("/{method_id}")
async def update_payment_method(
    method_id: UUID,
    method_data: Dict,
    db: Session = Depends(get_db)
):
    """Update payment method"""
    try:
        service = PaymentService(db)
        method = service.update_payment_method(str(method_id), method_data)
        if not method:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment method not found"
            )
        return PaymentMethodResponse.from_orm(method)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.delete("/{method_id}")
async def delete_payment_method(
    method_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete payment method"""
    try:
        service = PaymentService(db)
        success = service.delete_payment_method(str(method_id))
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment method not found"
            )
        return {"message": "Payment method deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
