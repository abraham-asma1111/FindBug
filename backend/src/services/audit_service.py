"""Audit service - FREQ-17."""
from typing import Dict, List, Optional, Type
from uuid import UUID
from datetime import datetime, timedelta

from sqlalchemy.orm import Session
from sqlalchemy import func, or_

from src.domain.models.audit_log import AuditLog


class AuditService:
    """Service for audit logging - FREQ-17."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def log_action(
        self,
        action_type: str,
        action_category: str,
        target_type: str,
        description: str,
        actor_id: Optional[UUID] = None,
        actor_role: Optional[str] = None,
        actor_email: Optional[str] = None,
        target_id: Optional[UUID] = None,
        metadata: Optional[Dict] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        severity: str = "info"
    ) -> AuditLog:
        """
        Log an action to audit trail - FREQ-17.
        
        Args:
            action_type: Type of action (e.g., "report_submitted")
            action_category: Category (report, bounty, user, program, admin, config, security)
            target_type: Type of target (report, user, program, etc.)
            description: Human-readable description
            actor_id: User who performed action
            actor_role: Role of actor
            actor_email: Email of actor
            target_id: ID of affected entity
            metadata: Additional data (old_value, new_value, reason, etc.)
            ip_address: IP address of request
            user_agent: User agent string
            severity: info, warning, critical
        """
        audit_log = AuditLog(
            action_type=action_type,
            action_category=action_category,
            target_type=target_type,
            description=description,
            actor_id=actor_id,
            actor_role=actor_role,
            actor_email=actor_email,
            target_id=target_id,
            audit_metadata=metadata,
            ip_address=ip_address,
            user_agent=user_agent,
            severity=severity,
            created_at=datetime.utcnow()
        )
        
        self.db.add(audit_log)
        self.db.commit()
        self.db.refresh(audit_log)
        
        return audit_log
    
    # Convenience methods for common actions
    
    def log_report_submitted(
        self,
        report_id: UUID,
        researcher_id: UUID,
        researcher_email: str,
        program_name: str,
        ip_address: Optional[str] = None
    ):
        """Log report submission - FREQ-17."""
        return self.log_action(
            action_type="report_submitted",
            action_category="report",
            target_type="report",
            description=f"Report submitted to program: {program_name}",
            actor_id=researcher_id,
            actor_role="researcher",
            actor_email=researcher_email,
            target_id=report_id,
            metadata={"program_name": program_name},
            ip_address=ip_address,
            severity="info"
        )
    
    def log_report_status_changed(
        self,
        report_id: UUID,
        old_status: str,
        new_status: str,
        changed_by_id: UUID,
        changed_by_role: str,
        changed_by_email: str,
        reason: Optional[str] = None
    ):
        """Log report status change - FREQ-17."""
        return self.log_action(
            action_type="report_status_changed",
            action_category="report",
            target_type="report",
            description=f"Report status changed from {old_status} to {new_status}",
            actor_id=changed_by_id,
            actor_role=changed_by_role,
            actor_email=changed_by_email,
            target_id=report_id,
            metadata={
                "old_status": old_status,
                "new_status": new_status,
                "reason": reason
            },
            severity="info"
        )
    
    def log_bounty_approved(
        self,
        report_id: UUID,
        bounty_amount: float,
        approved_by_id: UUID,
        approved_by_email: str,
        researcher_id: UUID
    ):
        """Log bounty approval - FREQ-17."""
        return self.log_action(
            action_type="bounty_approved",
            action_category="bounty",
            target_type="report",
            description=f"Bounty of ${bounty_amount} approved",
            actor_id=approved_by_id,
            actor_role="organization",
            actor_email=approved_by_email,
            target_id=report_id,
            metadata={
                "bounty_amount": bounty_amount,
                "researcher_id": str(researcher_id)
            },
            severity="info"
        )
    
    def log_bounty_paid(
        self,
        report_id: UUID,
        bounty_amount: float,
        researcher_id: UUID,
        payment_method: Optional[str] = None
    ):
        """Log bounty payment - FREQ-17."""
        return self.log_action(
            action_type="bounty_paid",
            action_category="bounty",
            target_type="report",
            description=f"Bounty of ${bounty_amount} paid to researcher",
            actor_id=None,  # System action
            actor_role="system",
            target_id=report_id,
            metadata={
                "bounty_amount": bounty_amount,
                "researcher_id": str(researcher_id),
                "payment_method": payment_method
            },
            severity="info"
        )
    
    def log_user_created(
        self,
        user_id: UUID,
        user_email: str,
        user_role: str,
        created_by_id: Optional[UUID] = None,
        created_by_email: Optional[str] = None
    ):
        """Log user creation - FREQ-17."""
        return self.log_action(
            action_type="user_created",
            action_category="user",
            target_type="user",
            description=f"User created with role: {user_role}",
            actor_id=created_by_id,
            actor_role="admin" if created_by_id else "system",
            actor_email=created_by_email,
            target_id=user_id,
            metadata={
                "user_email": user_email,
                "user_role": user_role
            },
            severity="info"
        )
    
    def log_user_status_changed(
        self,
        user_id: UUID,
        user_email: str,
        is_active: bool,
        changed_by_id: UUID,
        changed_by_email: str,
        reason: Optional[str] = None
    ):
        """Log user status change - FREQ-17."""
        return self.log_action(
            action_type="user_status_changed",
            action_category="user",
            target_type="user",
            description=f"User {'activated' if is_active else 'deactivated'}",
            actor_id=changed_by_id,
            actor_role="admin",
            actor_email=changed_by_email,
            target_id=user_id,
            metadata={
                "user_email": user_email,
                "is_active": is_active,
                "reason": reason
            },
            severity="warning" if not is_active else "info"
        )
    
    def log_program_created(
        self,
        program_id: UUID,
        program_name: str,
        organization_id: UUID,
        organization_email: str
    ):
        """Log program creation - FREQ-17."""
        return self.log_action(
            action_type="program_created",
            action_category="program",
            target_type="program",
            description=f"Program created: {program_name}",
            actor_id=organization_id,
            actor_role="organization",
            actor_email=organization_email,
            target_id=program_id,
            metadata={"program_name": program_name},
            severity="info"
        )
    
    def log_config_updated(
        self,
        config_key: str,
        old_value: any,
        new_value: any,
        updated_by_id: UUID,
        updated_by_email: str
    ):
        """Log configuration update - FREQ-17."""
        return self.log_action(
            action_type="config_updated",
            action_category="config",
            target_type="platform",
            description=f"Configuration updated: {config_key}",
            actor_id=updated_by_id,
            actor_role="admin",
            actor_email=updated_by_email,
            metadata={
                "config_key": config_key,
                "old_value": old_value,
                "new_value": new_value
            },
            severity="warning"
        )
    
    def log_security_event(
        self,
        event_type: str,
        description: str,
        user_id: Optional[UUID] = None,
        user_email: Optional[str] = None,
        ip_address: Optional[str] = None,
        metadata: Optional[Dict] = None
    ):
        """Log security event - FREQ-17."""
        return self.log_action(
            action_type=event_type,
            action_category="security",
            target_type="security",
            description=description,
            actor_id=user_id,
            actor_email=user_email,
            metadata=metadata,
            ip_address=ip_address,
            severity="critical"
        )
    
    # Query methods
    
    def get_audit_logs(
        self,
        action_type: Optional[str] = None,
        action_category: Optional[str] = None,
        actor_id: Optional[UUID] = None,
        target_type: Optional[str] = None,
        target_id: Optional[UUID] = None,
        severity: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[AuditLog]:
        """Get audit logs with filtering - FREQ-17."""
        query = self.db.query(AuditLog)
        
        if action_type:
            query = query.filter(AuditLog.action_type == action_type)
        
        if action_category:
            query = query.filter(AuditLog.action_category == action_category)
        
        if actor_id:
            query = query.filter(AuditLog.actor_id == actor_id)
        
        if target_type:
            query = query.filter(AuditLog.target_type == target_type)
        
        if target_id:
            query = query.filter(AuditLog.target_id == target_id)
        
        if severity:
            query = query.filter(AuditLog.severity == severity)
        
        if start_date:
            query = query.filter(AuditLog.created_at >= start_date)
        
        if end_date:
            query = query.filter(AuditLog.created_at <= end_date)
        
        return query.order_by(
            AuditLog.created_at.desc()
        ).limit(limit).offset(offset).all()
    
    def get_audit_statistics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict:
        """Get audit statistics - FREQ-17."""
        query = self.db.query(AuditLog)
        
        if start_date:
            query = query.filter(AuditLog.created_at >= start_date)
        
        if end_date:
            query = query.filter(AuditLog.created_at <= end_date)
        
        # Total actions
        total_actions = query.count()
        
        # By category
        by_category = dict(
            query.with_entities(
                AuditLog.action_category,
                func.count(AuditLog.id)
            ).group_by(AuditLog.action_category).all()
        )
        
        # By severity
        by_severity = dict(
            query.with_entities(
                AuditLog.severity,
                func.count(AuditLog.id)
            ).group_by(AuditLog.severity).all()
        )
        
        # Recent critical events
        critical_events = query.filter(
            AuditLog.severity == "critical"
        ).order_by(AuditLog.created_at.desc()).limit(10).all()
        
        return {
            "total_actions": total_actions,
            "by_category": by_category,
            "by_severity": by_severity,
            "critical_events_count": len(critical_events),
            "recent_critical_events": [
                {
                    "id": str(e.id),
                    "action_type": e.action_type,
                    "description": e.description,
                    "created_at": e.created_at
                }
                for e in critical_events
            ]
        }
