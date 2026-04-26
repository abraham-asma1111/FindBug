"""Vulnerability Report service - FREQ-06 (Researcher perspective)."""
from typing import List, Optional
from uuid import UUID
from datetime import datetime, timedelta

from sqlalchemy.orm import Session
from sqlalchemy import func

from src.domain.models.report import (
    VulnerabilityReport,
    ReportAttachment,
    ReportComment,
    ReportStatusHistory
)
from src.domain.models.program import BountyProgram, ProgramParticipation
from src.domain.models.user import UserRole, User
from src.core.role_access import role_from_str
from src.domain.repositories.report_repository import ReportRepository
from src.core.logging import get_logger

logger = get_logger(__name__)


class ReportService:
    """Service for vulnerability report operations."""
    
    def __init__(self, db: Session):
        self.db = db
        self.report_repo = ReportRepository(db)
        
        # Initialize file storage service
        from src.core.file_storage import FileStorageService
        self.file_storage = FileStorageService()
        
        # Initialize audit service
        from src.services.audit_service import AuditService
        self.audit_service = AuditService(db)
    
    def generate_report_number(self) -> str:
        """Generate unique report number."""
        from datetime import datetime
        
        # Get count of reports for current year
        current_year = datetime.utcnow().year
        count = self.db.query(VulnerabilityReport).filter(
            func.extract('year', VulnerabilityReport.submitted_at) == current_year
        ).count()
        
        # Format: REP-YYYY-NNNN
        return f"REP-{current_year}-{count + 1:04d}"
    
    def submit_report(
        self,
        researcher_id: UUID,
        user_id: UUID,  # User ID for status history
        program_id: UUID,
        title: str,
        description: str,
        steps_to_reproduce: str,
        impact_assessment: str,
        suggested_severity: str,
        affected_asset: Optional[str] = None,
        vulnerability_type: Optional[str] = None
    ) -> VulnerabilityReport:
        """
        Submit a vulnerability report - FREQ-06.
        
        Pre-condition: Researcher must have joined the program (UC-02).
        """
        # Verify program exists and is active
        program = self.db.query(BountyProgram).filter(
            BountyProgram.id == program_id,
            BountyProgram.status == "public",
            BountyProgram.deleted_at.is_(None)
        ).first()
        
        if not program:
            raise ValueError("Program not found or not active")
        
        # Verify researcher has joined the program
        participation = self.db.query(ProgramParticipation).filter(
            ProgramParticipation.program_id == program_id,
            ProgramParticipation.researcher_id == researcher_id,
            ProgramParticipation.status == "active"
        ).first()
        
        if not participation:
            raise ValueError("You must join the program before submitting reports")
        
        # Check for potential duplicates (BR-07)
        similar_reports = self.report_repo.search_similar_reports(
            program_id=program_id,
            title=title,
            description=description,
            limit=5
        )
        
        try:
            # Create report
            report = VulnerabilityReport(
                report_number=self.generate_report_number(),
                program_id=program_id,
                researcher_id=researcher_id,
                title=title,
                description=description,
                steps_to_reproduce=steps_to_reproduce,
                impact_assessment=impact_assessment,
                suggested_severity=suggested_severity,
                affected_asset=affected_asset,
                vulnerability_type=vulnerability_type,
                status="new",
                submitted_at=datetime.utcnow(),
                last_activity_at=datetime.utcnow()
            )
            
            report = self.report_repo.create(report)
            
            # Add status history
            self.report_repo.add_status_history(
                ReportStatusHistory(
                    report_id=report.id,
                    from_status=None,
                    to_status="new",
                    change_reason="Report submitted",
                    changed_by=user_id  # Use user_id instead of researcher_id
                )
            )
            
            # Send notification to organization (FREQ-12)
            from src.services.notification_service import NotificationService
            notification_service = NotificationService(self.db)
            notification_service.notify_report_submitted(
                report=report,
                organization_user_id=program.organization.user_id
            )
            
            # Log audit trail (FREQ-17)
            from src.domain.models.researcher import Researcher
            researcher = self.db.query(Researcher).filter(Researcher.id == researcher_id).first()
            researcher_email = researcher.user.email if researcher and researcher.user else "unknown"
            
            self.audit_service.log_report_submitted(
                report_id=report.id,
                researcher_id=researcher_id,
                researcher_email=researcher_email,
                program_name=program.name
            )
            
            # Commit transaction
            self.db.commit()
            self.db.refresh(report)
            
            return report
            
        except Exception as e:
            # Rollback transaction on any error
            self.db.rollback()
            logger.error(f"Failed to submit report: {str(e)}", extra={
                "researcher_id": str(researcher_id),
                "program_id": str(program_id),
                "title": title
            })
            raise
    
    def get_researcher_reports(
        self,
        researcher_id: UUID,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[VulnerabilityReport]:
        """Get all reports submitted by a researcher - FREQ-18."""
        return self.report_repo.get_by_researcher(
            researcher_id=researcher_id,
            status=status,
            limit=limit,
            offset=offset
        )
    
    def get_report_by_id(
        self,
        report_id: UUID,
        user_id: UUID,
        user_role: str
    ) -> Optional[VulnerabilityReport]:
        """
        Get report by ID with access control.
        
        - Researcher can view their own reports
        - Organization can view reports for their programs
        - Triage specialists can view all reports
        """
        from src.domain.models.researcher import Researcher
        
        report = self.report_repo.get_by_id(report_id)
        
        if not report:
            return None
        
        # Access control
        r = role_from_str(user_role)
        if r == UserRole.RESEARCHER:
            # Get researcher ID from user
            researcher = self.db.query(Researcher).filter(Researcher.user_id == user_id).first()
            if not researcher:
                raise PermissionError("Researcher profile not found")
            if str(report.researcher_id) != str(researcher.id):
                raise PermissionError("You can only view your own reports")
        elif r == UserRole.ORGANIZATION:
            # Get organization ID from user
            from src.domain.models.organization import Organization
            organization = self.db.query(Organization).filter(Organization.user_id == user_id).first()
            if not organization:
                raise PermissionError("Organization profile not found")
            
            # Check if report belongs to organization's program
            program = self.db.query(BountyProgram).filter(
                BountyProgram.id == report.program_id
            ).first()
            if not program or str(program.organization_id) != str(organization.id):
                raise PermissionError("You can only view reports for your programs")
        elif r not in (
            UserRole.TRIAGE_SPECIALIST,
            UserRole.STAFF,
            UserRole.ADMIN,
            UserRole.SUPER_ADMIN,
        ):
            raise PermissionError("Unauthorized access")
        
        return report
    
    def add_comment(
        self,
        report_id: UUID,
        user_id: UUID,
        user_role: str,
        comment_text: str,
        comment_type: str = "comment",
        is_internal: bool = False
    ) -> ReportComment:
        """Add comment to report - FREQ-09."""
        report = self.report_repo.get_by_id(report_id)
        
        if not report:
            raise ValueError("Report not found")
        
        # Researchers cannot create internal notes
        if role_from_str(user_role) == UserRole.RESEARCHER and is_internal:
            raise PermissionError("Researchers cannot create internal notes")
        
        comment = ReportComment(
            report_id=report_id,
            comment_text=comment_text,
            comment_type=comment_type,
            is_internal=is_internal,
            author_id=user_id,
            author_role=user_role,
            created_at=datetime.utcnow()
        )
        
        comment = self.report_repo.add_comment(comment)
        
        # Update last activity
        report.last_activity_at = datetime.utcnow()
        self.report_repo.update(report)
        
        return comment
    
    def get_comments(
        self,
        report_id: UUID,
        user_role: str
    ) -> List[ReportComment]:
        """Get comments for a report - FREQ-09."""
        # Researchers cannot see internal notes
        r = role_from_str(user_role)
        include_internal = r in (
            UserRole.TRIAGE_SPECIALIST,
            UserRole.ORGANIZATION,
            UserRole.ADMIN,
            UserRole.SUPER_ADMIN,
            UserRole.STAFF,
        )
        
        return self.report_repo.get_comments(
            report_id=report_id,
            include_internal=include_internal
        )
    
    def get_program_reports(
        self,
        program_id: UUID,
        organization_id: UUID,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[VulnerabilityReport]:
        """Get all reports for a program - FREQ-19 (Organization view)."""
        # Verify organization owns the program
        program = self.db.query(BountyProgram).filter(
            BountyProgram.id == program_id,
            BountyProgram.organization_id == organization_id
        ).first()
        
        if not program:
            raise PermissionError("You can only view reports for your programs")
        
        return self.report_repo.get_by_program(
            program_id=program_id,
            status=status,
            limit=limit,
            offset=offset
        )
    
    def get_organization_reports(
        self,
        organization_id: UUID,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[VulnerabilityReport]:
        """Get all reports across all organization programs."""
        # Get all programs for this organization
        programs = self.db.query(BountyProgram).filter(
            BountyProgram.organization_id == organization_id
        ).all()
        
        if not programs:
            return []
        
        program_ids = [p.id for p in programs]
        
        # Get reports for all programs
        query = self.db.query(VulnerabilityReport).filter(
            VulnerabilityReport.program_id.in_(program_ids)
        )
        
        if status:
            query = query.filter(VulnerabilityReport.status == status)
        
        query = query.order_by(VulnerabilityReport.submitted_at.desc())
        query = query.limit(limit).offset(offset)
        
        return query.all()
    
    def get_report_statistics(
        self,
        program_id: Optional[UUID] = None
    ) -> dict:
        """Get report statistics."""
        return self.report_repo.get_statistics(program_id=program_id)

    def upload_attachment(
        self,
        report_id: UUID,
        file,
        user_id: UUID
    ) -> ReportAttachment:
        """
        Upload attachment to report - FREQ-21.
        
        Args:
            report_id: Report ID
            file: Uploaded file
            user_id: User uploading the file
            
        Returns:
            ReportAttachment instance
        """
        # Verify report exists
        report = self.report_repo.get_by_id(report_id)
        if not report:
            raise ValueError("Report not found")
        
        # Save file to storage
        file_metadata = self.file_storage.save_file(
            file=file,
            report_id=report_id,
            subfolder="reports"
        )
        
        # Get file path for virus scanning
        file_path = self.file_storage.get_file_path(file_metadata["storage_path"])
        
        # Scan file for viruses - FREQ-21
        is_safe = True
        scan_result = "Not scanned"
        
        if file_path:
            is_safe, scan_result = self.file_storage.scan_file_for_viruses(file_path)
            
            # If malware detected, delete file and raise error
            if not is_safe:
                self.file_storage.delete_file(file_metadata["storage_path"])
                raise ValueError(f"Malware detected in file: {scan_result}")
        
        # Create attachment record
        attachment = ReportAttachment(
            report_id=report_id,
            filename=file_metadata["filename"],
            original_filename=file_metadata["original_filename"],
            file_type=file_metadata["file_type"],
            file_size=file_metadata["file_size"],
            storage_path=file_metadata["storage_path"],
            uploaded_by=user_id,
            uploaded_at=file_metadata["uploaded_at"],
            is_safe=is_safe,
            scanned_at=datetime.utcnow()
        )
        self.db.add(attachment)
        self.db.commit()
        self.db.refresh(attachment)
        
        return attachment
    
    def get_attachments(self, report_id: UUID) -> List[ReportAttachment]:
        """Get all attachments for a report - FREQ-21."""
        return self.db.query(ReportAttachment).filter(
            ReportAttachment.report_id == report_id
        ).all()
    
    def delete_attachment(
        self,
        attachment_id: UUID,
        user_id: UUID,
        user_role: str
    ) -> bool:
        """
        Delete attachment - FREQ-21.
        
        Only report owner or admin can delete attachments.
        """
        attachment = self.db.query(ReportAttachment).filter(
            ReportAttachment.id == attachment_id
        ).first()
        
        if not attachment:
            raise ValueError("Attachment not found")
        
        # Check permissions
        report = self.report_repo.get_by_id(attachment.report_id)
        if role_from_str(user_role) == UserRole.RESEARCHER and str(report.researcher_id) != str(user_id):
            raise PermissionError("You can only delete your own attachments")
        
        # Delete file from storage
        self.file_storage.delete_file(attachment.storage_path)
        
        # Delete database record
        self.db.delete(attachment)
        self.db.commit()
        
        return True
    
    def get_report_tracking_info(self, report_id: UUID) -> dict:
        """
        Get detailed tracking information for a report - FREQ-18.
        
        Returns timeline, status history, and current state.
        """
        report = self.report_repo.get_by_id(report_id)
        if not report:
            raise ValueError("Report not found")
        
        # Get status history
        status_history = self.db.query(ReportStatusHistory).filter(
            ReportStatusHistory.report_id == report_id
        ).order_by(ReportStatusHistory.changed_at.desc()).all()
        
        # Calculate time in each status
        status_durations = {}
        for i, history in enumerate(status_history):
            if i < len(status_history) - 1:
                duration = (status_history[i].changed_at - status_history[i + 1].changed_at).total_seconds()
                status_durations[history.to_status] = duration
        
        # Build timeline
        timeline = []
        
        # Submission
        timeline.append({
            "event": "submitted",
            "timestamp": report.submitted_at,
            "description": "Report submitted"
        })
        
        # Acknowledgment
        if report.acknowledged_at:
            timeline.append({
                "event": "acknowledged",
                "timestamp": report.acknowledged_at,
                "description": "Report acknowledged by organization"
            })
        
        # Triage
        if report.triaged_at:
            timeline.append({
                "event": "triaged",
                "timestamp": report.triaged_at,
                "description": f"Report triaged - Severity: {report.assigned_severity}"
            })
        
        # Bounty approval
        if report.bounty_approved_at:
            timeline.append({
                "event": "bounty_approved",
                "timestamp": report.bounty_approved_at,
                "description": f"Bounty approved: ${report.bounty_amount}"
            })
        
        # Resolution
        if report.resolved_at:
            timeline.append({
                "event": "resolved",
                "timestamp": report.resolved_at,
                "description": "Vulnerability resolved"
            })
        
        # Closure
        if report.closed_at:
            timeline.append({
                "event": "closed",
                "timestamp": report.closed_at,
                "description": "Report closed"
            })
        
        # Sort timeline by timestamp
        timeline.sort(key=lambda x: x["timestamp"])
        
        return {
            "report_id": report.id,
            "report_number": report.report_number,
            "current_status": report.status,
            "submitted_at": report.submitted_at,
            "last_activity_at": report.last_activity_at,
            "timeline": timeline,
            "status_history": [
                {
                    "from_status": h.from_status,
                    "to_status": h.to_status,
                    "changed_at": h.changed_at,
                    "change_reason": h.change_reason
                }
                for h in status_history
            ],
            "bounty_status": report.bounty_status,
            "bounty_amount": float(report.bounty_amount) if report.bounty_amount else None,
            "is_duplicate": report.is_duplicate,
            "duplicate_of": report.duplicate_of
        }
    
    def get_organization_report_summary(
        self,
        organization_id: UUID,
        program_id: Optional[UUID] = None
    ) -> dict:
        """
        Get report summary for organization - FREQ-19.
        
        Provides overview of all reports across programs.
        """
        from sqlalchemy import func
        from src.domain.models.program import BountyProgram
        
        # Base query
        query = self.db.query(VulnerabilityReport).join(
            BountyProgram,
            VulnerabilityReport.program_id == BountyProgram.id
        ).filter(
            BountyProgram.organization_id == organization_id
        )
        
        # Filter by program if specified
        if program_id:
            query = query.filter(VulnerabilityReport.program_id == program_id)
        
        # Total reports
        total_reports = query.count()
        
        # Reports by status
        status_counts = dict(
            query.with_entities(
                VulnerabilityReport.status,
                func.count(VulnerabilityReport.id)
            ).group_by(VulnerabilityReport.status).all()
        )
        
        # Reports by severity
        severity_counts = dict(
            query.filter(
                VulnerabilityReport.assigned_severity.isnot(None)
            ).with_entities(
                VulnerabilityReport.assigned_severity,
                func.count(VulnerabilityReport.id)
            ).group_by(VulnerabilityReport.assigned_severity).all()
        )
        
        # Total bounties
        total_bounties = query.filter(
            VulnerabilityReport.bounty_amount.isnot(None)
        ).with_entities(
            func.sum(VulnerabilityReport.bounty_amount)
        ).scalar() or 0
        
        # Recent reports (last 7 days)
        from datetime import timedelta
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        recent_reports = query.filter(
            VulnerabilityReport.submitted_at >= seven_days_ago
        ).count()
        
        # Average time to triage
        avg_triage_time = self.db.query(
            func.avg(
                func.extract('epoch', VulnerabilityReport.triaged_at - VulnerabilityReport.submitted_at)
            )
        ).filter(
            VulnerabilityReport.program_id == BountyProgram.id,
            BountyProgram.organization_id == organization_id,
            VulnerabilityReport.triaged_at.isnot(None)
        ).scalar()
        
        return {
            "total_reports": total_reports,
            "status_breakdown": status_counts,
            "severity_breakdown": severity_counts,
            "total_bounties_paid": float(total_bounties),
            "recent_reports_7d": recent_reports,
            "avg_triage_time_hours": round(avg_triage_time / 3600, 2) if avg_triage_time else None
        }
