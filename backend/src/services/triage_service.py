"""Triage Service - FREQ-07, FREQ-08."""
from typing import List, Optional
from uuid import UUID
from datetime import datetime, timedelta
from decimal import Decimal

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from src.domain.models.report import (
    VulnerabilityReport,
    ReportStatusHistory
)
from src.domain.repositories.report_repository import ReportRepository


class TriageService:
    """Service for triage specialist operations."""
    
    def __init__(self, db: Session):
        self.db = db
        self.report_repo = ReportRepository(db)
        
        # Initialize audit service
        from src.services.audit_service import AuditService
        self.audit_service = AuditService(db)
    
    def get_triage_queue(
        self,
        status: Optional[str] = None,
        severity: Optional[str] = None,
        program_id: Optional[UUID] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[VulnerabilityReport]:
        """
        Get triage queue - FREQ-07.
        
        Default: shows new and triaged reports.
        """
        query = self.db.query(VulnerabilityReport)
        
        # Filter by status
        if status:
            query = query.filter(VulnerabilityReport.status == status)
        else:
            # Default: show reports needing attention
            query = query.filter(
                VulnerabilityReport.status.in_(['new', 'triaged'])
            )
        
        # Filter by severity
        if severity:
            query = query.filter(VulnerabilityReport.assigned_severity == severity)
        
        # Filter by program
        if program_id:
            query = query.filter(VulnerabilityReport.program_id == program_id)
        
        # Order by priority: critical first, then by submission date
        query = query.order_by(
            VulnerabilityReport.suggested_severity.desc(),
            VulnerabilityReport.submitted_at.asc()
        )
        
        return query.offset(offset).limit(limit).all()
    
    def update_triage(
        self,
        report_id: UUID,
        triage_staff_id: Optional[UUID],
        actor_user_id: UUID,
        actor_role: str,
        actor_email: str,
        status: Optional[str] = None,
        assigned_severity: Optional[str] = None,
        cvss_score: Optional[Decimal] = None,
        vrt_category: Optional[str] = None,
        triage_notes: Optional[str] = None,
        is_duplicate: Optional[bool] = None,
        duplicate_of: Optional[UUID] = None
    ) -> VulnerabilityReport:
        """
        Update report triage information - FREQ-07, FREQ-08.
        
        Validates status transitions and applies business rules.
        """
        report = self.report_repo.get_by_id(report_id)
        
        if not report:
            raise ValueError("Report not found")
        
        # Track old status for history
        old_status = report.status
        
        # Update status if provided
        if status:
            # Validate status transition
            valid_transitions = {
                'new': ['triaged', 'invalid'],
                'triaged': ['valid', 'invalid', 'duplicate'],
                'valid': ['resolved', 'closed'],
                'invalid': [],  # Terminal state
                'duplicate': [],  # Terminal state
                'resolved': ['closed'],
                'closed': []  # Terminal state
            }
            
            if status not in valid_transitions.get(report.status, []):
                raise ValueError(f"Invalid status transition from {report.status} to {status}")
            
            report.status = status
        
        # Update severity - FREQ-08
        if assigned_severity:
            if assigned_severity not in ['critical', 'high', 'medium', 'low']:
                raise ValueError("Invalid severity. Must be: critical, high, medium, or low")
            report.assigned_severity = assigned_severity
        
        # Update CVSS score
        if cvss_score is not None:
            if cvss_score < 0 or cvss_score > 10:
                raise ValueError("CVSS score must be between 0.0 and 10.0")
            report.cvss_score = cvss_score
        
        # Update VRT category
        if vrt_category:
            report.vrt_category = vrt_category
        
        # Update triage notes
        if triage_notes:
            report.triage_notes = triage_notes
        
        # Mark as duplicate
        if is_duplicate is not None:
            report.is_duplicate = is_duplicate
            if is_duplicate and duplicate_of:
                # Verify original report exists
                original = self.report_repo.get_by_id(duplicate_of)
                if not original:
                    raise ValueError("Original report not found")
                report.duplicate_of = duplicate_of
                report.duplicate_detected_at = datetime.utcnow()
                report.status = 'duplicate'
        
        # Set triage information (triaged_by -> staff.id; optional if admin has no staff row)
        if triage_staff_id is not None:
            report.triaged_by = triage_staff_id
            report.triaged_at = datetime.utcnow()
        report.updated_at = datetime.utcnow()
        report.last_activity_at = datetime.utcnow()
        
        # Save changes
        report = self.report_repo.update(report)
        
        # Add to status history if status changed
        if status and status != old_status:
            self.report_repo.add_status_history(
                ReportStatusHistory(
                    report_id=report_id,
                    from_status=old_status,
                    to_status=status,
                    change_reason=triage_notes or f"Status changed by triage specialist",
                    changed_by=actor_user_id,
                )
            )
            
            # Send notification to researcher (FREQ-12)
            from src.services.notification_service import NotificationService
            notification_service = NotificationService(self.db)
            notification_service.notify_report_status_changed(
                report=report,
                old_status=old_status,
                new_status=status
            )
            
            # Log audit trail (FREQ-17)
            self.audit_service.log_report_status_changed(
                report_id=report_id,
                old_status=old_status,
                new_status=status,
                changed_by_id=actor_user_id,
                changed_by_role=actor_role,
                changed_by_email=actor_email,
                reason=triage_notes,
            )
        
        return report
    
    def mark_as_duplicate(
        self,
        report_id: UUID,
        original_report_id: UUID,
        triage_staff_id: Optional[UUID],
        actor_user_id: UUID,
    ) -> VulnerabilityReport:
        """
        Mark report as duplicate - BR-07.
        
        Applies business rule:
        - First valid report receives full bounty
        - Duplicate reports receive 50% if submitted within 24 hours
        - Otherwise, no reward
        """
        report = self.report_repo.get_by_id(report_id)
        original = self.report_repo.get_by_id(original_report_id)
        
        if not report:
            raise ValueError("Report not found")
        if not original:
            raise ValueError("Original report not found")
        
        # Check if reports are for the same program
        if report.program_id != original.program_id:
            raise ValueError("Reports must be from the same program")
        
        # Calculate time difference
        time_diff = report.submitted_at - original.submitted_at
        within_24_hours = time_diff.total_seconds() <= 86400  # 24 hours in seconds
        
        # Update report
        report.is_duplicate = True
        report.duplicate_of = original_report_id
        report.duplicate_detected_at = datetime.utcnow()
        report.status = 'duplicate'
        if triage_staff_id is not None:
            report.triaged_by = triage_staff_id
            report.triaged_at = datetime.utcnow()
        
        # Add note about duplicate bounty eligibility
        if within_24_hours:
            report.triage_notes = f"Duplicate of {original.report_number}. Eligible for 50% bounty (submitted within 24 hours)."
        else:
            report.triage_notes = f"Duplicate of {original.report_number}. Not eligible for bounty (submitted after 24 hours)."
        
        report = self.report_repo.update(report)
        
        # Add to history
        self.report_repo.add_status_history(
            ReportStatusHistory(
                report_id=report_id,
                from_status=report.status,
                to_status='duplicate',
                change_reason=f"Marked as duplicate of {original.report_number}",
                changed_by=actor_user_id,
            )
        )
        
        return report
    
    def find_similar_reports(
        self,
        report_id: UUID,
        limit: int = 10
    ) -> List[VulnerabilityReport]:
        """
        Find similar reports for duplicate detection - FREQ-07.
        
        Uses title and description similarity.
        """
        report = self.report_repo.get_by_id(report_id)
        
        if not report:
            raise ValueError("Report not found")
        
        return self.report_repo.search_similar_reports(
            program_id=report.program_id,
            title=report.title,
            description=report.description,
            limit=limit
        )
    
    def acknowledge_report(
        self,
        report_id: UUID,
        acknowledged_by: UUID
    ) -> VulnerabilityReport:
        """
        Acknowledge report - BR-10.
        
        Organizations must acknowledge within 24 hours.
        Sets 90-day remediation deadline.
        """
        report = self.report_repo.get_by_id(report_id)
        
        if not report:
            raise ValueError("Report not found")
        
        if report.acknowledged_at:
            raise ValueError("Report already acknowledged")
        
        now = datetime.utcnow()
        
        # Check if acknowledged within 24 hours
        time_since_submission = now - report.submitted_at
        if time_since_submission.total_seconds() > 86400:  # 24 hours
            # Log warning but still allow acknowledgment
            pass
        
        # Set acknowledgment and deadline
        report.acknowledged_at = now
        report.remediation_deadline = now + timedelta(days=90)  # BR-10: 90 days
        report.updated_at = now
        report.last_activity_at = now
        
        report = self.report_repo.update(report)
        
        # Add to history
        self.report_repo.add_status_history(
            ReportStatusHistory(
                report_id=report_id,
                from_status=report.status,
                to_status=report.status,
                change_reason="Report acknowledged",
                changed_by=acknowledged_by
            )
        )
        
        # Send notification to researcher (FREQ-12)
        from src.services.notification_service import NotificationService
        notification_service = NotificationService(self.db)
        notification_service.notify_report_acknowledged(report=report)
        
        return report
    
    def resolve_report(
        self,
        report_id: UUID,
        resolved_by: UUID,
        resolution_notes: Optional[str] = None
    ) -> VulnerabilityReport:
        """
        Mark report as resolved - FREQ-07.
        
        Indicates vulnerability has been fixed.
        """
        report = self.report_repo.get_by_id(report_id)
        
        if not report:
            raise ValueError("Report not found")
        
        if report.status not in ['valid', 'triaged']:
            raise ValueError("Only valid or triaged reports can be resolved")
        
        old_status = report.status
        
        # Update report
        report.status = 'resolved'
        report.resolved_at = datetime.utcnow()
        report.updated_at = datetime.utcnow()
        report.last_activity_at = datetime.utcnow()
        
        if resolution_notes:
            report.triage_notes = (report.triage_notes or "") + f"\n\nResolution: {resolution_notes}"
        
        report = self.report_repo.update(report)
        
        # Add to history
        self.report_repo.add_status_history(
            ReportStatusHistory(
                report_id=report_id,
                from_status=old_status,
                to_status='resolved',
                change_reason=resolution_notes or "Vulnerability fixed",
                changed_by=resolved_by
            )
        )
        
        return report
    
    def get_statistics(
        self,
        program_id: Optional[UUID] = None
    ) -> dict:
        """Get triage statistics - FREQ-15."""
        stats = self.report_repo.get_statistics(program_id=program_id)
        
        # Add severity breakdown
        query = self.db.query(VulnerabilityReport)
        if program_id:
            query = query.filter(VulnerabilityReport.program_id == program_id)
        
        severity_stats = {
            'critical': query.filter(VulnerabilityReport.assigned_severity == 'critical').count(),
            'high': query.filter(VulnerabilityReport.assigned_severity == 'high').count(),
            'medium': query.filter(VulnerabilityReport.assigned_severity == 'medium').count(),
            'low': query.filter(VulnerabilityReport.assigned_severity == 'low').count(),
        }
        
        stats['by_severity'] = severity_stats
        
        return stats
    
    def get_report_history(
        self,
        report_id: UUID
    ) -> List[ReportStatusHistory]:
        """Get report status history - FREQ-17."""
        report = self.report_repo.get_by_id(report_id)
        
        if not report:
            raise ValueError("Report not found")
        
        return self.report_repo.get_status_history(report_id)
