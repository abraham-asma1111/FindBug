"""Vulnerability Report service - FREQ-06 (Researcher perspective)."""
from typing import List, Optional
from uuid import UUID
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from src.domain.models.report import (
    VulnerabilityReport,
    ReportAttachment,
    ReportComment,
    ReportStatusHistory
)
from src.domain.models.program import BountyProgram, ProgramParticipation
from src.domain.repositories.report_repository import ReportRepository


class ReportService:
    """Service for vulnerability report operations."""
    
    def __init__(self, db: Session):
        self.db = db
        self.report_repo = ReportRepository(db)
    
    def generate_report_number(self) -> str:
        """Generate unique report number."""
        from datetime import datetime
        
        # Get count of reports today
        today = datetime.utcnow().date()
        count = self.db.query(VulnerabilityReport).filter(
            VulnerabilityReport.submitted_at >= today
        ).count()
        
        # Format: REP-YYYY-NNNN
        return f"REP-{datetime.utcnow().year}-{count + 1:04d}"
    
    def submit_report(
        self,
        researcher_id: UUID,
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
                changed_by=researcher_id
            )
        )
        
        # Send notification to organization (FREQ-12)
        from src.services.notification_service import NotificationService
        notification_service = NotificationService(self.db)
        notification_service.notify_report_submitted(
            report=report,
            organization_user_id=program.organization.user_id
        )
        
        return report
    
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
        report = self.report_repo.get_by_id(report_id)
        
        if not report:
            return None
        
        # Access control
        if user_role == "researcher":
            if str(report.researcher_id) != str(user_id):
                raise PermissionError("You can only view your own reports")
        elif user_role == "organization":
            # Check if report belongs to organization's program
            program = self.db.query(BountyProgram).filter(
                BountyProgram.id == report.program_id
            ).first()
            if not program or str(program.organization_id) != str(user_id):
                raise PermissionError("You can only view reports for your programs")
        elif user_role not in ["triage_specialist", "admin"]:
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
        if user_role == "researcher" and is_internal:
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
        include_internal = user_role in ["triage_specialist", "organization", "admin"]
        
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
    
    def get_report_statistics(
        self,
        program_id: Optional[UUID] = None
    ) -> dict:
        """Get report statistics."""
        return self.report_repo.get_statistics(program_id=program_id)
