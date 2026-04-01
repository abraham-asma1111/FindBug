"""
Isolation API Endpoints - FREQ-27: Simulation Data Isolation
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from uuid import UUID

from src.core.database import get_db
from src.services.isolation_service import IsolationService
from src.api.schemas.isolation import IsolationSessionResponse

router = APIRouter(prefix="/isolation", tags=["Isolation"])

@router.post("/sessions")
async def create_isolation_session(
    session_data: Dict,
    db: Session = Depends(get_db)
):
    """Create isolated simulation environment"""
    try:
        service = IsolationService(db)
        session = service.create_isolation_session(
            user_id=session_data.get("user_id"),
            target_id=session_data.get("target_id"),
            isolation_type=session_data.get("isolation_type", "container")
        )
        return session
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/sessions/{session_id}")
async def get_isolation_session(
    session_id: UUID,
    db: Session = Depends(get_db)
):
    """Get isolation session details"""
    try:
        service = IsolationService(db)
        session = service.get_isolation_session(str(session_id))
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Isolation session not found"
            )
        return session
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/sessions/{session_id}/extend")
async def extend_isolation_session(
    session_id: UUID,
    extension_data: Dict,
    db: Session = Depends(get_db)
):
    """Extend isolation session duration"""
    try:
        service = IsolationService(db)
        session = service.extend_isolation_session(
            str(session_id),
            extension_data.get("extend_minutes", 30)
        )
        return {
            "session_id": str(session_id),
            "message": "Isolation session extended",
            "new_expires_at": session["expires_at"]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.delete("/sessions/{session_id}")
async def terminate_isolation_session(
    session_id: UUID,
    db: Session = Depends(get_db)
):
    """Terminate isolation session"""
    try:
        service = IsolationService(db)
        success = service.terminate_isolation_session(str(session_id))
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Isolation session not found"
            )
        return {"message": "Isolation session terminated successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/sessions/{session_id}/logs")
async def get_isolation_logs(
    session_id: UUID,
    db: Session = Depends(get_db)
):
    """Get isolation session logs"""
    try:
        service = IsolationService(db)
        logs = service.get_isolation_logs(str(session_id))
        return logs
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
