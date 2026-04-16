"""
PTaaS Finding Assignment Endpoint - Step 8
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from src.core.database import get_db
from src.api.v1.middlewares.auth import get_current_user
from src.services.ptaas_service import PTaaSService
from src.domain.models.user import User
from pydantic import BaseModel
from typing import Optional

router = APIRouter()


class FindingAssignmentRequest(BaseModel):
    assigned_to: UUID
    notes: Optional[str] = None


@router.post("/findings/{finding_id}/assign")
def assign_finding(
    finding_id: UUID,
    assignment: FindingAssignmentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Assign finding to team member - Step 8
    """
    service = PTaaSService(db)
    
    # Get finding
    finding = service.get_finding(finding_id)
    if not finding:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Finding not found"
        )
    
    # Update finding with assignment
    update_data = {
        'assigned_to': assignment.assigned_to,
        'assignment_notes': assignment.notes
    }
    
    updated_finding = service.update_finding(finding_id, update_data, current_user.id)
    
    # TODO: Send notification to assigned user
    
    return updated_finding
