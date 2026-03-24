"""
Security Service — Security event logging and audit trail (FREQ-17)
"""
from typing import Optional, List, Dict
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from uuid import UUID

from src.domain.models.security_log import SecurityEvent, LoginHistory
from src.domain.models.user import User
from src.core.exceptions import NotFoundException
from src.core.logging import get_logger

logger = get_logger(__name__)


class SecurityService:
    """Service for security event logging and audit trail management"""
    
    def __init__(self, db: Session):
        self.db = db
        
        # Event severity levels
        self.severity_levels = ["low", "medium", "high", "critical"]
        
        # Common event types
        self.event_types = [
            "brute_force",
            "account_lockout",
            "suspicious_ip",
            "mfa_bypass_attempt",
            "rate_limit_exceeded",
            "ssrf_attempt",
            "xss_attempt",
            "sql_injection_attempt",
            "unauthorized_access",
            "privilege_escalation",
            "data_exfiltration",
            "password_reset",
            "email_verified",
            "mfa_enabled",
            "mfa_disabled",
            "kyc_submitted",
            "kyc_reviewed",
            "user_registration",
            "login_success",
            "login_failure",
            "logout"
        ]
    
    def log_security_event(
        self,
        event_type: str,
        description: str,
        user_id: Optional[str] = None,
        severity: str = "medium",
        ip_address: Optional[str] = None,
        is_blocked: bool = False
    ) -> Dict:
        """
        Log a security event.
        
        Args:
            event_type: Type of security event
            description: Detailed description
            user_id: User ID (optional)
            severity: Event severity (low, medium, high, critical)
            ip_address: IP address (optional)
            is_blocked: Whether the action was blocked
            
        Returns:
            Security event details
        """
        # Validate severity
        if severity not in self.severity_levels:
            severity = "medium"
        
        # Create security event
        event = SecurityEvent(
            user_id=UUID(user_id) if user_id else None,
            event_type=event_type,
            severity=severity,
            description=description,
            ip_address=ip_address,
            is_blocked=is_blocked
        )
        
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        
        logger.info("Security event logged", extra={
            "event_id": str(event.id),
            "event_type": event_type,
            "severity": severity,
            "user_id": user_id
        })
        
        return {
            "event_id": str(event.id),
            "event_type": event.event_type,
            "severity": event.severity,
            "description": event.description,
            "user_id": str(event.user_id) if event.user_id else None,
            "ip_address": event.ip_address,
            "is_blocked": event.is_blocked,
            "created_at": event.created_at.isoformat()
        }
    
    def log_login_attempt(
        self,
        user_id: str,
        is_successful: bool,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        failure_reason: Optional[str] = None,
        mfa_used: bool = False
    ) -> Dict:
        """
        Log a login attempt.
        
        Args:
            user_id: User ID
            is_successful: Whether login was successful
            ip_address: IP address (optional)
            user_agent: User agent string (optional)
            failure_reason: Reason for failure (optional)
            mfa_used: Whether MFA was used
            
        Returns:
            Login history details
        """
        # Create login history record
        login = LoginHistory(
            user_id=UUID(user_id),
            ip_address=ip_address,
            user_agent=user_agent,
            is_successful=is_successful,
            failure_reason=failure_reason,
            mfa_used=mfa_used
        )
        
        self.db.add(login)
        self.db.commit()
        self.db.refresh(login)
        
        logger.info("Login attempt logged", extra={
            "login_id": str(login.id),
            "user_id": user_id,
            "is_successful": is_successful
        })
        
        return {
            "login_id": str(login.id),
            "user_id": str(login.user_id),
            "is_successful": login.is_successful,
            "failure_reason": login.failure_reason,
            "mfa_used": login.mfa_used,
            "ip_address": login.ip_address,
            "created_at": login.created_at.isoformat()
        }
    
    def get_security_events(
        self,
        user_id: Optional[str] = None,
        event_type: Optional[str] = None,
        severity: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 50
    ) -> Dict:
        """
        Get security events with filters.
        
        Args:
            user_id: Filter by user ID (optional)
            event_type: Filter by event type (optional)
            severity: Filter by severity (optional)
            start_date: Filter by start date (optional)
            end_date: Filter by end date (optional)
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of security events
        """
        query = self.db.query(SecurityEvent)
        
        if user_id:
            query = query.filter(SecurityEvent.user_id == UUID(user_id))
        
        if event_type:
            query = query.filter(SecurityEvent.event_type == event_type)
        
        if severity:
            query = query.filter(SecurityEvent.severity == severity)
        
        if start_date:
            query = query.filter(SecurityEvent.created_at >= start_date)
        
        if end_date:
            query = query.filter(SecurityEvent.created_at <= end_date)
        
        query = query.order_by(SecurityEvent.created_at.desc())
        
        total = query.count()
        events = query.offset(skip).limit(limit).all()
        
        return {
            "events": [
                {
                    "event_id": str(event.id),
                    "user_id": str(event.user_id) if event.user_id else None,
                    "user_email": event.user.email if event.user else None,
                    "event_type": event.event_type,
                    "severity": event.severity,
                    "description": event.description,
                    "ip_address": event.ip_address,
                    "is_blocked": event.is_blocked,
                    "created_at": event.created_at.isoformat()
                }
                for event in events
            ],
            "total": total,
            "skip": skip,
            "limit": limit
        }
    
    def get_login_history(
        self,
        user_id: Optional[str] = None,
        is_successful: Optional[bool] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 50
    ) -> Dict:
        """
        Get login history with filters.
        
        Args:
            user_id: Filter by user ID (optional)
            is_successful: Filter by success status (optional)
            start_date: Filter by start date (optional)
            end_date: Filter by end date (optional)
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of login attempts
        """
        query = self.db.query(LoginHistory)
        
        if user_id:
            query = query.filter(LoginHistory.user_id == UUID(user_id))
        
        if is_successful is not None:
            query = query.filter(LoginHistory.is_successful == is_successful)
        
        if start_date:
            query = query.filter(LoginHistory.created_at >= start_date)
        
        if end_date:
            query = query.filter(LoginHistory.created_at <= end_date)
        
        query = query.order_by(LoginHistory.created_at.desc())
        
        total = query.count()
        logins = query.offset(skip).limit(limit).all()
        
        return {
            "logins": [
                {
                    "login_id": str(login.id),
                    "user_id": str(login.user_id),
                    "user_email": login.user.email if login.user else None,
                    "is_successful": login.is_successful,
                    "failure_reason": login.failure_reason,
                    "mfa_used": login.mfa_used,
                    "ip_address": login.ip_address,
                    "user_agent": login.user_agent,
                    "created_at": login.created_at.isoformat()
                }
                for login in logins
            ],
            "total": total,
            "skip": skip,
            "limit": limit
        }
    
    def get_audit_trail(
        self,
        user_id: str,
        days: int = 30,
        skip: int = 0,
        limit: int = 100
    ) -> Dict:
        """
        Get comprehensive audit trail for a user (security events + login history).
        
        Args:
            user_id: User ID
            days: Number of days to look back
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            Combined audit trail
        """
        # Validate user exists
        user = self.db.query(User).filter(User.id == UUID(user_id)).first()
        if not user:
            raise NotFoundException("User not found.")
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Get security events
        security_events = self.db.query(SecurityEvent).filter(
            SecurityEvent.user_id == UUID(user_id),
            SecurityEvent.created_at >= start_date
        ).order_by(SecurityEvent.created_at.desc()).all()
        
        # Get login history
        login_history = self.db.query(LoginHistory).filter(
            LoginHistory.user_id == UUID(user_id),
            LoginHistory.created_at >= start_date
        ).order_by(LoginHistory.created_at.desc()).all()
        
        # Combine and sort by timestamp
        audit_trail = []
        
        for event in security_events:
            audit_trail.append({
                "type": "security_event",
                "id": str(event.id),
                "event_type": event.event_type,
                "severity": event.severity,
                "description": event.description,
                "ip_address": event.ip_address,
                "is_blocked": event.is_blocked,
                "timestamp": event.created_at.isoformat()
            })
        
        for login in login_history:
            audit_trail.append({
                "type": "login_attempt",
                "id": str(login.id),
                "is_successful": login.is_successful,
                "failure_reason": login.failure_reason,
                "mfa_used": login.mfa_used,
                "ip_address": login.ip_address,
                "user_agent": login.user_agent,
                "timestamp": login.created_at.isoformat()
            })
        
        # Sort by timestamp (most recent first)
        audit_trail.sort(key=lambda x: x["timestamp"], reverse=True)
        
        # Apply pagination
        total = len(audit_trail)
        audit_trail = audit_trail[skip:skip + limit]
        
        return {
            "user_id": user_id,
            "user_email": user.email,
            "audit_trail": audit_trail,
            "total": total,
            "skip": skip,
            "limit": limit,
            "days": days
        }
    
    def report_incident(
        self,
        user_id: str,
        incident_type: str,
        description: str,
        severity: str = "high"
    ) -> Dict:
        """
        Report a security incident.
        
        Args:
            user_id: User ID reporting the incident
            incident_type: Type of incident
            description: Detailed description
            severity: Incident severity
            
        Returns:
            Incident report details
        """
        # Log as security event
        event = self.log_security_event(
            event_type=f"incident_reported_{incident_type}",
            description=f"User reported incident: {description}",
            user_id=user_id,
            severity=severity,
            is_blocked=False
        )
        
        logger.warning("Security incident reported", extra={
            "user_id": user_id,
            "incident_type": incident_type,
            "severity": severity
        })
        
        # TODO: Send notification to security team
        
        return {
            "incident_id": event["event_id"],
            "incident_type": incident_type,
            "severity": severity,
            "status": "reported",
            "message": "Security incident reported successfully. Our team will investigate."
        }
    
    def get_security_statistics(
        self,
        days: int = 30
    ) -> Dict:
        """
        Get security statistics for the platform.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Security statistics
        """
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Total security events
        total_events = self.db.query(SecurityEvent).filter(
            SecurityEvent.created_at >= start_date
        ).count()
        
        # Events by severity
        critical_events = self.db.query(SecurityEvent).filter(
            SecurityEvent.created_at >= start_date,
            SecurityEvent.severity == "critical"
        ).count()
        
        high_events = self.db.query(SecurityEvent).filter(
            SecurityEvent.created_at >= start_date,
            SecurityEvent.severity == "high"
        ).count()
        
        # Blocked events
        blocked_events = self.db.query(SecurityEvent).filter(
            SecurityEvent.created_at >= start_date,
            SecurityEvent.is_blocked == True
        ).count()
        
        # Login statistics
        total_logins = self.db.query(LoginHistory).filter(
            LoginHistory.created_at >= start_date
        ).count()
        
        successful_logins = self.db.query(LoginHistory).filter(
            LoginHistory.created_at >= start_date,
            LoginHistory.is_successful == True
        ).count()
        
        failed_logins = self.db.query(LoginHistory).filter(
            LoginHistory.created_at >= start_date,
            LoginHistory.is_successful == False
        ).count()
        
        mfa_logins = self.db.query(LoginHistory).filter(
            LoginHistory.created_at >= start_date,
            LoginHistory.mfa_used == True
        ).count()
        
        return {
            "period_days": days,
            "security_events": {
                "total": total_events,
                "critical": critical_events,
                "high": high_events,
                "blocked": blocked_events
            },
            "login_attempts": {
                "total": total_logins,
                "successful": successful_logins,
                "failed": failed_logins,
                "mfa_used": mfa_logins,
                "success_rate": round((successful_logins / total_logins * 100) if total_logins > 0 else 0, 2)
            }
        }
