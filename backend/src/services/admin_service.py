"""
Admin service - FREQ-14.
Enhanced with welcome emails and security event logging.
"""
from typing import List, Optional, Dict
from uuid import UUID
from datetime import datetime, timedelta

from sqlalchemy.orm import Session
from sqlalchemy import func, or_

from src.domain.models.user import User, UserRole
from src.domain.models.researcher import Researcher
from src.domain.models.organization import Organization
from src.domain.models.staff import Staff
from src.domain.models.program import BountyProgram
from src.domain.models.report import VulnerabilityReport, ReportStatusHistory
from src.domain.models.security_log import SecurityEvent
from src.services.notification_service import NotificationService
from src.domain.models.notification import NotificationType, NotificationPriority
from src.core.security import get_password_hash
from src.core.logging import get_logger

logger = get_logger(__name__)


class AdminService:
    """
    Service for administrator operations - FREQ-14.
    Enhanced with welcome emails and security event logging.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.notification_service = NotificationService(db)
    
    def send_welcome_email(self, staff_id: UUID):
        """
        Send welcome email to new staff member.
        
        Args:
            staff_id: Staff ID
        """
        staff = self.db.query(Staff).filter(Staff.id == staff_id).first()
        if not staff:
            return
        
        user = self.db.query(User).filter(User.id == staff.user_id).first()
        if not user:
            return
        
        self.notification_service.create_notification(
            user_id=user.id,
            notification_type=NotificationType.ACCOUNT_VERIFIED,
            title="Welcome to FindBug Platform!",
            message=f"Welcome {staff.full_name}! Your staff account has been created. You now have access to platform features.",
            priority=NotificationPriority.HIGH,
            action_url="/admin/dashboard",
            action_text="Go to Dashboard",
            send_email=True
        )
        
        logger.info(f"Sent welcome email to staff {staff_id}")
    
    def log_admin_action_security(
        self,
        admin_id: UUID,
        action: str,
        description: str,
        severity: str = "low",
        ip_address: Optional[str] = None
    ):
        """
        Log admin action as security event.
        
        Args:
            admin_id: Admin user ID
            action: Action type
            description: Action description
            severity: Severity level (low, medium, high, critical)
            ip_address: IP address (optional)
        """
        event = SecurityEvent(
            user_id=admin_id,
            event_type=f"admin_{action}",
            severity=severity,
            description=description,
            ip_address=ip_address,
            is_blocked=False
        )
        
        self.db.add(event)
        self.db.commit()
        
        logger.info(f"Logged admin action: {action}", extra={
            "admin_id": str(admin_id),
            "action": action,
            "severity": severity
        })
    
    # User Management
    
    def get_all_users(
        self,
        role: Optional[str] = None,
        status: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[User]:
        """Get all users with filtering - FREQ-14."""
        query = self.db.query(User)
        
        if role:
            query = query.filter(User.role == role)
        
        if status == "active":
            query = query.filter(User.is_active == True)
        elif status == "inactive":
            query = query.filter(User.is_active == False)
        
        if search:
            query = query.filter(
                User.email.ilike(f"%{search}%")
            )
        
        return query.order_by(User.created_at.desc()).limit(limit).offset(offset).all()
    
    def get_user_details(self, user_id: UUID) -> Optional[Dict]:
        """Get detailed user information - FREQ-14."""
        user = self.db.query(User).filter(User.id == user_id).first()
        
        if not user:
            return None
        
        details = {
            "id": str(user.id),
            "email": user.email,
            "full_name": getattr(user, "full_name", None),
            "role": user.role,
            "is_active": user.is_active,
            "email_verified": bool(getattr(user, "email_verified_at", None)),
            "mfa_enabled": getattr(user, "mfa_enabled", False),
            "created_at": user.created_at,
            "last_login": getattr(user, "last_login_at", None),
            "login_count": 0,
        }
        
        # Add role-specific details
        if user.role == UserRole.RESEARCHER and user.researcher:
            details["researcher"] = {
                "reputation_score": user.researcher.reputation_score,
                "total_reports": user.researcher.total_reports_submitted,
                "valid_reports": user.researcher.valid_reports,
                "total_earnings": float(user.researcher.total_earnings),
                "specializations": user.researcher.specializations
            }
        elif user.role == UserRole.ORGANIZATION and user.organization:
            details["organization"] = {
                "company_name": user.organization.company_name,
                "website": user.organization.website,
                "is_verified": user.organization.is_verified,
                "total_programs": self.db.query(BountyProgram).filter(
                    BountyProgram.organization_id == user.organization.id
                ).count()
            }
        elif user.role in (
            UserRole.TRIAGE_SPECIALIST,
            UserRole.STAFF,
            UserRole.FINANCE_OFFICER,
        ) and user.staff:
            details["staff"] = {
                "department": user.staff.department,
                "position": user.staff.position,
            }
        
        return details
    
    def update_user_status(
        self,
        admin_id: UUID,
        user_id: UUID,
        is_active: bool,
        reason: Optional[str] = None
    ) -> User:
        """Activate or deactivate user - FREQ-14."""
        user = self.db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise ValueError("User not found")
        
        user.is_active = is_active
        self.db.commit()
        self.db.refresh(user)
        
        # Log action
        self._log_admin_action(
            admin_id=admin_id,
            action="user_status_change",
            target_type="user",
            target_id=user_id,
            details={
                "is_active": is_active,
                "reason": reason
            }
        )
        
        return user
    
    def update_user_role(
        self,
        admin_id: UUID,
        user_id: UUID,
        new_role: str
    ) -> User:
        """Update user role - FREQ-14."""
        user = self.db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise ValueError("User not found")
        
        valid_roles = {r.value for r in UserRole}
        if new_role not in valid_roles:
            raise ValueError(f"Invalid role: {new_role}")
        
        old_role = user.role
        user.role = UserRole(new_role)
        self.db.commit()
        self.db.refresh(user)
        
        # Log action
        self._log_admin_action(
            admin_id=admin_id,
            action="user_role_change",
            target_type="user",
            target_id=user_id,
            details={
                "old_role": old_role,
                "new_role": new_role
            }
        )
        
        return user
    
    def delete_user(self, admin_id: UUID, user_id: UUID) -> bool:
        """Soft delete user - FREQ-14."""
        user = self.db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise ValueError("User not found")
        
        # Soft delete
        user.is_active = False
        user.deleted_at = datetime.utcnow()
        self.db.commit()
        
        # Log action
        self._log_admin_action(
            admin_id=admin_id,
            action="user_deleted",
            target_type="user",
            target_id=user_id,
            details={"email": user.email}
        )
        
        return True
    
    # Program Management
    
    def get_all_programs(
        self,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[BountyProgram]:
        """Get all programs - FREQ-14."""
        query = self.db.query(BountyProgram).filter(
            BountyProgram.deleted_at.is_(None)
        )
        
        if status:
            query = query.filter(BountyProgram.status == status)
        
        return query.order_by(BountyProgram.created_at.desc()).limit(limit).offset(offset).all()
    
    def update_program_status(
        self,
        admin_id: UUID,
        program_id: UUID,
        new_status: str,
        reason: Optional[str] = None
    ) -> BountyProgram:
        """Update program status - FREQ-14."""
        program = self.db.query(BountyProgram).filter(
            BountyProgram.id == program_id
        ).first()
        
        if not program:
            raise ValueError("Program not found")
        
        valid_statuses = ["draft", "pending_review", "public", "private", "paused", "archived"]
        if new_status not in valid_statuses:
            raise ValueError(f"Invalid status: {new_status}")
        
        old_status = program.status
        program.status = new_status
        self.db.commit()
        self.db.refresh(program)
        
        # Log action
        self._log_admin_action(
            admin_id=admin_id,
            action="program_status_change",
            target_type="program",
            target_id=program_id,
            details={
                "old_status": old_status,
                "new_status": new_status,
                "reason": reason
            }
        )
        
        return program
    
    def approve_program(self, admin_id: UUID, program_id: UUID) -> BountyProgram:
        """Approve a program that is in pending_review status - FREQ-14."""
        program = self.db.query(BountyProgram).filter(
            BountyProgram.id == program_id
        ).first()
        
        if not program:
            raise ValueError("Program not found")
            
        if program.status != "pending_review":
            raise ValueError(f"Program cannot be approved because it is in status: {program.status}")
            
        old_status = program.status
        program.status = "public"
        program.visibility = "public"
        self.db.commit()
        self.db.refresh(program)
        
        # Log action
        self._log_admin_action(
            admin_id=admin_id,
            action="program_approved",
            target_type="program",
            target_id=program_id,
            details={
                "old_status": old_status,
                "new_status": "public"
            }
        )
        
        return program
        
    def reject_program(self, admin_id: UUID, program_id: UUID, reason: str) -> BountyProgram:
        """Reject a program that is in pending_review status - FREQ-14."""
        program = self.db.query(BountyProgram).filter(
            BountyProgram.id == program_id
        ).first()
        
        if not program:
            raise ValueError("Program not found")
            
        if program.status != "pending_review":
            raise ValueError(f"Program cannot be rejected because it is in status: {program.status}")
            
        old_status = program.status
        program.status = "draft"
        self.db.commit()
        self.db.refresh(program)
        
        # Log action
        self._log_admin_action(
            admin_id=admin_id,
            action="program_rejected",
            target_type="program",
            target_id=program_id,
            details={
                "old_status": old_status,
                "new_status": "draft",
                "reason": reason
            }
        )
        
        return program
    
    def delete_program(self, admin_id: UUID, program_id: UUID) -> bool:
        """Soft delete program - FREQ-14."""
        program = self.db.query(BountyProgram).filter(
            BountyProgram.id == program_id
        ).first()
        
        if not program:
            raise ValueError("Program not found")
        
        program.deleted_at = datetime.utcnow()
        self.db.commit()
        
        # Log action
        self._log_admin_action(
            admin_id=admin_id,
            action="program_deleted",
            target_type="program",
            target_id=program_id,
            details={"program_name": program.name}
        )
        
        return True
    
    # Platform Audits
    
    def get_platform_audit_log(
        self,
        action_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict]:
        """Get unified platform activity log - FREQ-14, FREQ-17.
        
        Sources:
          - AuditLog: triage, bounty, report, ptaas, program, user, admin, config actions
          - LoginHistory: authentication events (success/failure)
          - SecurityEvent: security incidents not covered by AuditLog
        
        Filter categories (action_type param):
          all | report | bounty | user | program | admin | config |
          security | ptaas | auth
        """
        from src.domain.models.security_log import SecurityEvent, LoginHistory
        from src.domain.models.audit_log import AuditLog
        from datetime import datetime as _dt

        events = []
        # fetch more than needed per source so merge+sort+paginate works correctly
        max_fetch = (offset + limit) * 2

        # ── 1. AuditLog (primary source – covers most platform operations) ────
        AUDIT_CATEGORIES = {
            "report", "bounty", "user", "program", "admin", "config", "ptaas"
        }
        # Decide whether to include AuditLog at all for this filter
        include_audit = (
            not action_type
            or action_type == "all"
            or action_type in AUDIT_CATEGORIES
        )
        if include_audit:
            q = self.db.query(AuditLog)
            if action_type and action_type not in ("all",):
                q = q.filter(AuditLog.action_category == action_type)
            if start_date:
                q = q.filter(AuditLog.created_at >= start_date)
            if end_date:
                q = q.filter(AuditLog.created_at <= end_date)
            for a in q.order_by(AuditLog.created_at.desc()).limit(max_fetch).all():
                events.append({
                    "id": str(a.id),
                    "event_type": a.action_type,
                    "category": a.action_category,
                    "description": a.description,
                    "user_id": str(a.actor_id) if a.actor_id else None,
                    "user_email": a.actor_email,
                    "actor_role": a.actor_role,
                    "target_type": a.target_type,
                    "target_id": str(a.target_id) if a.target_id else None,
                    "timestamp": a.created_at,
                    "severity": a.severity or "info",
                    "details": a.audit_metadata or {},
                    "ip_address": a.ip_address,
                })

        # ── 2. LoginHistory (authentication events) ───────────────────────────
        include_auth = (
            not action_type
            or action_type in ("all", "auth", "security")
        )
        if include_auth:
            q_l = self.db.query(LoginHistory)
            if start_date:
                q_l = q_l.filter(LoginHistory.created_at >= start_date)
            if end_date:
                q_l = q_l.filter(LoginHistory.created_at <= end_date)
            for l in q_l.order_by(LoginHistory.created_at.desc()).limit(max_fetch).all():
                events.append({
                    "id": str(l.id),
                    "event_type": "login_success" if l.is_successful else "login_failed",
                    "category": "auth",
                    "description": "Successful login" if l.is_successful else f"Failed login: {l.failure_reason or 'unknown reason'}",
                    "user_id": str(l.user_id),
                    "user_email": None,      # enriched below
                    "actor_role": None,
                    "timestamp": l.created_at,
                    "severity": "info" if l.is_successful else "medium",
                    "details": {
                        "ip_address": l.ip_address,
                        "is_successful": l.is_successful,
                        "failure_reason": l.failure_reason,
                        "mfa_used": l.mfa_used,
                    },
                    "ip_address": l.ip_address,
                })

        # ── 3. SecurityEvent (security incidents: brute_force, lockout, etc.) ─
        # Only include if NOT filtering for a non-security AuditLog category
        include_security = (
            not action_type
            or action_type in ("all", "security", "auth")
        )
        if include_security:
            q_s = self.db.query(SecurityEvent)
            # Exclude admin_ events that come from _log_admin_action (already
            # captured as AuditLog admin category in new code)
            q_s = q_s.filter(~SecurityEvent.event_type.like("admin_%"))
            if start_date:
                q_s = q_s.filter(SecurityEvent.created_at >= start_date)
            if end_date:
                q_s = q_s.filter(SecurityEvent.created_at <= end_date)
            for s in q_s.order_by(SecurityEvent.created_at.desc()).limit(max_fetch).all():
                events.append({
                    "id": str(s.id),
                    "event_type": s.event_type,
                    "category": "security",
                    "description": s.description,
                    "user_id": str(s.user_id) if s.user_id else None,
                    "user_email": None,      # enriched below
                    "actor_role": None,
                    "timestamp": s.created_at,
                    "severity": s.severity,
                    "details": {"is_blocked": s.is_blocked},
                    "ip_address": s.ip_address,
                })

        # ── Sort by timestamp desc ─────────────────────────────────────────────
        def _ts(e):
            t = e["timestamp"]
            if t is None:
                return _dt.min
            return t.replace(tzinfo=None) if t.tzinfo else t

        events.sort(key=_ts, reverse=True)

        # ── Enrich missing user_email from DB ─────────────────────────────────
        needs_email = [e for e in events if e.get("user_id") and not e.get("user_email")]
        if needs_email:
            uids = list({e["user_id"] for e in needs_email})
            rows = self.db.query(User.id, User.email, User.role).filter(User.id.in_(uids)).all()
            uid_map = {str(r[0]): {"email": r[1], "role": str(r[2])} for r in rows}
            for e in events:
                if e.get("user_id") and not e.get("user_email"):
                    info = uid_map.get(e["user_id"], {})
                    e["user_email"] = info.get("email", "Unknown User")
                    if not e.get("actor_role"):
                        e["actor_role"] = info.get("role")
        for e in events:
            if not e.get("user_email"):
                e["user_email"] = "System"

        # ── Enrich with contextual information (organization names, usernames) ─
        from src.domain.models.organization import Organization
        from src.domain.models.program import BountyProgram
        import re
        
        for e in events:
            metadata = e.get("details", {})
            category = e.get("category")
            actor_id = e.get("user_id")  # This is the actor_id from audit log
            actor_role = e.get("actor_role")  # Use the role from audit log, not user's actual role
            description = e.get("description", "")
            
            # For program-related events, show the organization name
            # Use actor_role to determine if this was an organization action
            if category == "program" and actor_role == "organization":
                # Try to get from actor if they have an organization profile
                if actor_id:
                    user = self.db.query(User).filter(User.id == actor_id).first()
                    if user and user.organization:
                        e["organization_name"] = user.organization.company_name
                        e["display_name"] = user.organization.company_name
                
                # Fallback: Extract program name from description and look up organization
                if not e.get("display_name"):
                    # Try to extract program name from description
                    # Patterns: "Program published: NAME" or "Published new Bug Bounty Program: NAME"
                    match = re.search(r'(?:Program published:|Bug Bounty Program:)\s*(.+?)(?:\s*$|\.)', description)
                    if match:
                        program_name = match.group(1).strip()
                        # Look up program by name to get organization
                        program = self.db.query(BountyProgram).filter(
                            BountyProgram.name == program_name
                        ).first()
                        if program and program.organization_id:
                            org = self.db.query(Organization).filter(
                                Organization.id == program.organization_id
                            ).first()
                            if org:
                                e["organization_name"] = org.company_name
                                e["display_name"] = org.company_name
            
            # For user-related events (KYC, etc.), show the researcher username
            # Use actor_role to determine if this was a researcher action
            elif category == "user" and actor_role == "researcher":
                # Try to get from actor if they have a researcher profile
                if actor_id:
                    user = self.db.query(User).filter(User.id == actor_id).first()
                    if user and user.researcher:
                        # Check if researcher has username
                        if user.researcher.username:
                            e["display_name"] = user.researcher.username
                            e["target_username"] = user.researcher.username
                        elif user.researcher.first_name or user.researcher.last_name:
                            # Fallback to full name
                            name_parts = [user.researcher.first_name, user.researcher.last_name]
                            full_name = " ".join([n for n in name_parts if n])
                            e["display_name"] = full_name
                        else:
                            # Fallback to email
                            e["display_name"] = user.email
                        e["target_email"] = user.email
                    else:
                        # No researcher profile, use email
                        e["display_name"] = user.email if user else "Unknown"

        # ── Paginate ──────────────────────────────────────────────────────────
        return events[offset: offset + limit]


    
    def get_platform_statistics(self) -> Dict:
        """Get platform-wide statistics - FREQ-14."""
        # User statistics
        total_users = self.db.query(User).count()
        active_users = self.db.query(User).filter(User.is_active == True).count()
        users_by_role = dict(
            self.db.query(User.role, func.count(User.id))
            .group_by(User.role).all()
        )
        
        # Program statistics
        total_programs = self.db.query(BountyProgram).filter(
            BountyProgram.deleted_at.is_(None)
        ).count()
        active_programs = self.db.query(BountyProgram).filter(
            BountyProgram.status == "public",
            BountyProgram.deleted_at.is_(None)
        ).count()
        
        # Report statistics
        total_reports = self.db.query(VulnerabilityReport).count()
        reports_by_status = dict(
            self.db.query(
                VulnerabilityReport.status,
                func.count(VulnerabilityReport.id)
            ).group_by(VulnerabilityReport.status).all()
        )
        
        # Bounty statistics — use BountyPayment table (same source as finance officer portal)
        from src.domain.models.bounty_payment import BountyPayment
        total_bounties = self.db.query(
            func.sum(BountyPayment.researcher_amount)
        ).filter(
            BountyPayment.status.in_(["completed", "approved"])
        ).scalar() or 0
        
        # Recent activity (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        new_users_30d = self.db.query(User).filter(
            User.created_at >= thirty_days_ago
        ).count()
        new_reports_30d = self.db.query(VulnerabilityReport).filter(
            VulnerabilityReport.submitted_at >= thirty_days_ago
        ).count()
        
        return {
            "users": {
                "total": total_users,
                "active": active_users,
                "by_role": users_by_role,
                "new_last_30d": new_users_30d
            },
            "programs": {
                "total": total_programs,
                "active": active_programs
            },
            "reports": {
                "total": total_reports,
                "by_status": reports_by_status,
                "new_last_30d": new_reports_30d
            },
            "bounties": {
                "total_paid": float(total_bounties)
            }
        }
    
    # Platform Configuration
    
    def get_platform_config(self) -> Dict:
        """Get platform configuration - FREQ-14."""
        # Placeholder for platform configuration
        # In production, this would read from a config table
        return {
            "max_file_size_mb": 50,
            "allowed_file_types": [
                "image/png", "image/jpeg", "video/mp4",
                "application/pdf", "text/plain", "application/zip"
            ],
            "bounty_ranges": {
                "critical": {"min": 1000, "max": 10000},
                "high": {"min": 500, "max": 5000},
                "medium": {"min": 100, "max": 1000},
                "low": {"min": 50, "max": 500}
            },
            "reputation_points": {
                "critical": 50,
                "high": 30,
                "medium": 20,
                "low": 10,
                "invalid": -20,
                "duplicate": -20
            },
            "disclosure_timeline_days": 90,
            "acknowledgment_deadline_hours": 24
        }
    
    def update_platform_config(self, admin_id: UUID, config: Dict) -> Dict:
        """Update platform configuration - FREQ-14."""
        # Placeholder for platform configuration update
        # In production, this would write to a config table
        
        # Log action
        self._log_admin_action(
            admin_id=admin_id,
            action="config_updated",
            target_type="platform",
            target_id=None,
            details=config
        )
        
        return config
    
    # Helper methods
    
    def _log_admin_action(
        self,
        admin_id: UUID,
        action: str,
        target_type: str,
        target_id: Optional[UUID],
        details: Dict
    ):
        """Log admin action for audit trail - FREQ-17."""
        import json
        
        description = f"Admin {action} on {target_type}"
        if target_id:
            description += f" ({target_id})"
            
        def _serialize(obj):
            if hasattr(obj, 'value'): return str(obj.value)
            return str(obj)
            
        description += f" - Details: {json.dumps(details, default=_serialize)}"
        
        event = SecurityEvent(
            user_id=admin_id,
            event_type=f"admin_{action}",
            severity="medium",
            description=description[:1000], # Prevent overflow
            is_blocked=False
        )
        
        self.db.add(event)
        self.db.commit()


    # Reports Management - FREQ-19 (Admin oversight)
    
    def get_all_reports(
        self,
        status: Optional[str] = None,
        severity: Optional[str] = None,
        program_id: Optional[UUID] = None,
        organization_id: Optional[UUID] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[VulnerabilityReport]:
        """Get all reports across platform - FREQ-14, FREQ-19."""
        query = self.db.query(VulnerabilityReport)
        
        if status:
            query = query.filter(VulnerabilityReport.status == status)
        
        if severity:
            query = query.filter(VulnerabilityReport.assigned_severity == severity)
        
        if program_id:
            query = query.filter(VulnerabilityReport.program_id == program_id)
        
        if organization_id:
            query = query.join(BountyProgram).filter(
                BountyProgram.organization_id == organization_id
            )
        
        return query.order_by(
            VulnerabilityReport.submitted_at.desc()
        ).limit(limit).offset(offset).all()
    
    def get_report_statistics_admin(self) -> Dict:
        """Get platform-wide report statistics - FREQ-14."""
        total_reports = self.db.query(VulnerabilityReport).count()
        
        # Reports by status
        status_breakdown = dict(
            self.db.query(
                VulnerabilityReport.status,
                func.count(VulnerabilityReport.id)
            ).group_by(VulnerabilityReport.status).all()
        )
        
        # Reports by severity
        severity_breakdown = dict(
            self.db.query(
                VulnerabilityReport.assigned_severity,
                func.count(VulnerabilityReport.id)
            ).filter(
                VulnerabilityReport.assigned_severity.isnot(None)
            ).group_by(VulnerabilityReport.assigned_severity).all()
        )
        
        # Duplicate detection stats
        duplicate_count = self.db.query(VulnerabilityReport).filter(
            VulnerabilityReport.is_duplicate == True
        ).count()
        
        # Triage stats
        pending_triage = self.db.query(VulnerabilityReport).filter(
            VulnerabilityReport.status == "new"
        ).count()
        
        avg_triage_time = self.db.query(
            func.avg(
                func.extract('epoch', VulnerabilityReport.triaged_at - VulnerabilityReport.submitted_at)
            )
        ).filter(
            VulnerabilityReport.triaged_at.isnot(None)
        ).scalar()
        
        return {
            "total_reports": total_reports,
            "status_breakdown": status_breakdown,
            "severity_breakdown": severity_breakdown,
            "duplicate_count": duplicate_count,
            "duplicate_rate": round((duplicate_count / total_reports * 100) if total_reports > 0 else 0, 2),
            "pending_triage": pending_triage,
            "avg_triage_time_hours": round(avg_triage_time / 3600, 2) if avg_triage_time else None
        }
    
    # Staff Management - FREQ-01, FREQ-14
    
    def get_all_staff(
        self,
        department: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Staff]:
        """Get all staff members - FREQ-14."""
        query = self.db.query(Staff)
        
        if department:
            query = query.filter(Staff.department == department)
        
        return query.order_by(Staff.created_at.desc()).limit(limit).offset(offset).all()
    
    def create_staff_member(
        self,
        admin_id: UUID,
        email: str,
        full_name: str,
        department: str,
        role: str = "triage_specialist"
    ) -> tuple[Staff, str]:
        """Create new staff member - FREQ-01, FREQ-14."""
        role_map = {
            "triage_specialist": UserRole.TRIAGE_SPECIALIST,
            "finance_officer": UserRole.FINANCE_OFFICER,
            "staff": UserRole.STAFF,
            "admin": UserRole.ADMIN,
        }
        user_role = role_map.get(role, UserRole.STAFF)

        # Check if user already exists
        existing_user = self.db.query(User).filter(User.email == email).first()
        if existing_user:
            raise ValueError("User with this email already exists")
        
        # Create user account
        from src.core.security import get_password_hash
        import secrets
        
        temp_password = secrets.token_urlsafe(16)
        
        from datetime import datetime
        user = User(
            email=email,
            password_hash=get_password_hash(temp_password),
            role=user_role,
            is_active=True,
            is_verified=True,
            email_verified_at=datetime.utcnow()
        )
        
        self.db.add(user)
        self.db.flush()
        
        # Create staff profile
        staff = Staff(
            user_id=user.id,
            full_name=full_name,
            department=department,
        )
        
        self.db.add(staff)
        self.db.commit()
        self.db.refresh(staff)
        
        # Log action
        self._log_admin_action(
            admin_id=admin_id,
            action="staff_created",
            target_type="staff",
            target_id=staff.id,
            details={
                "email": email,
                "department": department,
                "role": role
            }
        )
        
        # Send in-app notification
        self.send_welcome_email(staff.id)
        
        # Send actual email with credentials via SMTP
        from src.core.email_service import EmailService
        EmailService.send_staff_welcome_email(
            email=email,
            full_name=full_name,
            role=role,
            temp_password=temp_password
        )
        
        return staff, temp_password
    
    def get_staff_statistics(self) -> Dict:
        """Get staff statistics - FREQ-14."""
        total_staff = self.db.query(Staff).count()
        
        # Staff by department
        by_department = dict(
            self.db.query(Staff.department, func.count(Staff.id))
            .group_by(Staff.department).all()
        )
        
        # Active staff (users with recent activity)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        active_staff = self.db.query(Staff).join(User).filter(
            User.last_login >= thirty_days_ago
        ).count()
        
        # Triage performance (columns not yet migrated — safe defaults)
        avg_triage_time = 0
        total_triaged   = 0
        
        return {
            "total_staff": total_staff,
            "active_staff": active_staff,
            "by_department": by_department,
            "avg_triage_time_hours": round(avg_triage_time, 2),
            "total_reports_triaged": total_triaged
        }
    
    # Researcher Management
    
    def get_all_researchers(
        self,
        search: Optional[str] = None,
        min_reputation: Optional[int] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Researcher]:
        """
        Get all researchers - FREQ-14.
        
        Returns researchers who are:
        - (email_verified AND persona_verified) OR (reputation_score > 0)
        """
        from src.domain.models.kyc import KYCVerification
        
        # Join User and KYC tables
        query = self.db.query(Researcher).join(User)
        query = query.outerjoin(
            KYCVerification,
            KYCVerification.user_id == User.id
        )
        
        # Filter: (email_verified AND persona_verified) OR (reputation_score > 0)
        query = query.filter(
            or_(
                # Fully verified: email AND persona
                (
                    User.email_verified_at.isnot(None) &
                    KYCVerification.persona_verified_at.isnot(None)
                ),
                # OR has reputation
                Researcher.reputation_score > 0
            )
        )
        
        if search:
            query = query.filter(
                or_(
                    User.email.ilike(f"%{search}%"),
                    User.full_name.ilike(f"%{search}%"),
                    Researcher.username.ilike(f"%{search}%")
                )
            )
        
        if min_reputation:
            query = query.filter(Researcher.reputation_score >= min_reputation)
        
        return query.order_by(
            Researcher.reputation_score.desc()
        ).limit(limit).offset(offset).all()
    
    def get_researcher_statistics(self) -> Dict:
        """Get researcher statistics - FREQ-14."""
        total_researchers = self.db.query(Researcher).count()
        
        # Active researchers (submitted report in last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        active_researchers = self.db.query(Researcher).join(
            VulnerabilityReport,
            Researcher.id == VulnerabilityReport.researcher_id
        ).filter(
            VulnerabilityReport.submitted_at >= thirty_days_ago
        ).distinct().count()
        
        # Top performers
        top_performers = self.db.query(Researcher).order_by(
            Researcher.reputation_score.desc()
        ).limit(10).all()
        
        # Average reputation
        avg_reputation = self.db.query(
            func.avg(Researcher.reputation_score)
        ).scalar() or 0
        
        # Total earnings
        total_earnings = self.db.query(
            func.sum(Researcher.total_earnings)
        ).scalar() or 0
        
        return {
            "total_researchers": total_researchers,
            "active_researchers": active_researchers,
            "avg_reputation": round(avg_reputation, 2),
            "total_earnings_paid": float(total_earnings),
            "top_performers": [
                {
                    "id": str(r.id),
                    "reputation_score": r.reputation_score,
                    "total_reports": r.total_reports_submitted,
                    "total_earnings": float(r.total_earnings)
                }
                for r in top_performers
            ]
        }
    
    # Organization Management
    
    def get_all_organizations(
        self,
        verified_only: bool = False,
        limit: int = 50,
        offset: int = 0
    ) -> List[Organization]:
        """Get all organizations - FREQ-14."""
        query = self.db.query(Organization)
        
        if verified_only:
            query = query.filter(Organization.verification_status == "active")
        
        return query.order_by(Organization.created_at.desc()).limit(limit).offset(offset).all()
    
    def verify_organization(
        self,
        organization_id: UUID,
        is_verified: bool
    ) -> Organization:
        """Verify or unverify organization - FREQ-14."""
        org = self.db.query(Organization).filter(
            Organization.id == organization_id
        ).first()
        
        if not org:
            raise ValueError("Organization not found")
        
        org.verification_status = "active" if is_verified else "pending"
        org.domain_verified = bool(is_verified)
        self.db.commit()
        self.db.refresh(org)
        
        # Log action
        self._log_admin_action(
            action="organization_verification",
            target_type="organization",
            target_id=organization_id,
            details={"is_verified": is_verified}
        )
        
        return org
    
    def get_organization_statistics(self) -> Dict:
        """Get organization statistics - FREQ-14."""
        total_orgs = self.db.query(Organization).count()
        verified_orgs = self.db.query(Organization).filter(
            Organization.verification_status == "active"
        ).count()
        
        # Organizations with active programs
        orgs_with_programs = self.db.query(Organization).join(
            BountyProgram
        ).filter(
            BountyProgram.status == "public",
            BountyProgram.deleted_at.is_(None)
        ).distinct().count()
        
        # Total bounties paid by all organizations
        total_bounties = self.db.query(
            func.sum(VulnerabilityReport.bounty_amount)
        ).filter(
            VulnerabilityReport.bounty_status == "paid"
        ).scalar() or 0
        
        return {
            "total_organizations": total_orgs,
            "verified_organizations": verified_orgs,
            "organizations_with_active_programs": orgs_with_programs,
            "total_bounties_paid": float(total_bounties)
        }
    
    # Payment & Commission Tracking - FREQ-20
    
    def get_payment_overview(self) -> Dict:
        """Get payment and commission overview - FREQ-14, FREQ-20."""
        # Total bounties paid
        total_bounties = self.db.query(
            func.sum(VulnerabilityReport.bounty_amount)
        ).filter(
            VulnerabilityReport.bounty_status == "paid"
        ).scalar() or 0
        
        # Pending bounties
        pending_bounties = self.db.query(
            func.sum(VulnerabilityReport.bounty_amount)
        ).filter(
            VulnerabilityReport.bounty_status == "pending"
        ).scalar() or 0
        
        # Platform commission (30%)
        platform_commission = float(total_bounties) * 0.30
        
        # Payment by month (last 12 months)
        twelve_months_ago = datetime.utcnow() - timedelta(days=365)
        monthly_payments = self.db.query(
            func.date_trunc('month', VulnerabilityReport.bounty_approved_at).label('month'),
            func.sum(VulnerabilityReport.bounty_amount).label('total')
        ).filter(
            VulnerabilityReport.bounty_status == "paid",
            VulnerabilityReport.bounty_approved_at >= twelve_months_ago
        ).group_by('month').order_by('month').all()
        
        return {
            "total_bounties_paid": float(total_bounties),
            "pending_bounties": float(pending_bounties),
            "platform_commission": platform_commission,
            "commission_rate": 0.30,
            "monthly_payments": [
                {
                    "month": m[0].isoformat() if m[0] else None,
                    "total": float(m[1]) if m[1] else 0
                }
                for m in monthly_payments
            ]
        }
    
    # VRT Management - FREQ-08
    
    def get_vrt_configuration(self) -> Dict:
        """Get VRT taxonomy configuration - FREQ-14."""
        # Placeholder for VRT configuration
        # In production, this would read from a VRT config table
        return {
            "taxonomy_version": "2.0",
            "last_updated": "2026-03-01",
            "categories": [
                {"id": "xss", "name": "Cross-Site Scripting (XSS)", "severity_range": ["low", "critical"]},
                {"id": "sqli", "name": "SQL Injection", "severity_range": ["medium", "critical"]},
                {"id": "csrf", "name": "Cross-Site Request Forgery", "severity_range": ["low", "high"]},
                {"id": "auth", "name": "Authentication Issues", "severity_range": ["medium", "critical"]},
                {"id": "idor", "name": "Insecure Direct Object Reference", "severity_range": ["low", "high"]}
            ],
            "reward_tiers": {
                "critical": {"min": 1000, "max": 10000},
                "high": {"min": 500, "max": 5000},
                "medium": {"min": 100, "max": 1000},
                "low": {"min": 50, "max": 500}
            }
        }
    
    def update_vrt_configuration(self, config: Dict) -> Dict:
        """Update VRT configuration - FREQ-14."""
        # Placeholder for VRT configuration update
        # In production, this would write to a VRT config table
        
        # Log action
        self._log_admin_action(
            action="vrt_config_updated",
            target_type="platform",
            target_id=None,
            details=config
        )
        
        return config
