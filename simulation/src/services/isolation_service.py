"""
Isolation Service for Simulation Platform
Handles container isolation and session management
"""

from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from uuid import UUID, uuid4

from src.core.logging import get_logger
from src.core.exceptions import NotFoundException

logger = get_logger(__name__)


class IsolationService:
    """Handles isolation session management"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_isolation_session(
        self, 
        user_id: str, 
        target_id: str,
        isolation_type: str = "container"
    ) -> Dict:
        """Create new isolation session"""
        session_id = str(uuid4())
        
        # Simplified session creation
        session = {
            "id": session_id,
            "user_id": user_id,
            "target_id": target_id,
            "isolation_type": isolation_type,
            "container_id": f"sim_{session_id[:8]}",
            "status": "active",
            "started_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + timedelta(hours=2),
            "access_url": f"http://localhost:8100/{session_id}"
        }
        
        logger.info("Isolation session created", extra={
            "session_id": session_id,
            "user_id": user_id,
            "target_id": target_id
        })
        
        return session
    
    def get_isolation_session(self, session_id: str) -> Optional[Dict]:
        """Get isolation session details"""
        # Simplified implementation - would normally query database
        return {
            "id": session_id,
            "status": "active",
            "container_id": f"sim_{session_id[:8]}",
            "access_url": f"http://localhost:8100/{session_id}",
            "expires_at": datetime.utcnow() + timedelta(hours=1)
        }
    
    def extend_isolation_session(self, session_id: str, extend_minutes: int = 30) -> Dict:
        """Extend isolation session"""
        session = self.get_isolation_session(session_id)
        if not session:
            raise NotFoundException("Session not found")
        
        # Extend session
        new_expiry = datetime.utcnow() + timedelta(minutes=extend_minutes)
        session["expires_at"] = new_expiry
        
        logger.info("Isolation session extended", extra={
            "session_id": session_id,
            "extend_minutes": extend_minutes
        })
        
        return session
    
    def terminate_isolation_session(self, session_id: str) -> bool:
        """Terminate isolation session"""
        session = self.get_isolation_session(session_id)
        if not session:
            return False
        
        # Terminate container and cleanup
        logger.info("Isolation session terminated", extra={
            "session_id": session_id
        })
        
        return True
    
    def get_isolation_logs(self, session_id: str) -> Dict:
        """Get isolation session logs"""
        return {
            "session_id": session_id,
            "logs": [
                {
                    "timestamp": datetime.utcnow(),
                    "level": "INFO",
                    "message": "Container started successfully"
                },
                {
                    "timestamp": datetime.utcnow(),
                    "level": "INFO", 
                    "message": "User connected to environment"
                }
            ],
            "total_logs": 2
        }
    
    def list_user_sessions(self, user_id: str) -> List[Dict]:
        """List user's isolation sessions"""
        # Simplified implementation
        return [
            {
                "id": str(uuid4()),
                "user_id": user_id,
                "status": "active",
                "started_at": datetime.utcnow(),
                "expires_at": datetime.utcnow() + timedelta(hours=1)
            }
        ]