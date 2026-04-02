"""Vulnerability Report repository."""
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, desc

from src.domain.models.report import (
    VulnerabilityReport,
    ReportAttachment,
    ReportComment,
    ReportStatusHistory
)


class ReportRepository:
    """Repository for vulnerability report operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, report: VulnerabilityReport) -> VulnerabilityReport:
        """Create a new vulnerability report."""
        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)
        return report
    
    def get_by_id(self, report_id: UUID) -> Optional[VulnerabilityReport]:
        """Get report by ID with relationships loaded."""
        from src.domain.models.researcher import Researcher
        from src.domain.models.user import User
        
        return self.db.query(VulnerabilityReport).options(
            joinedload(VulnerabilityReport.program),
            joinedload(VulnerabilityReport.researcher).joinedload(Researcher.user),
            joinedload(VulnerabilityReport.attachments)
        ).filter(
            VulnerabilityReport.id == report_id
        ).first()
    
    def get_by_report_number(self, report_number: str) -> Optional[VulnerabilityReport]:
        """Get report by report number."""
        return self.db.query(VulnerabilityReport).filter(
            VulnerabilityReport.report_number == report_number
        ).first()
    
    def get_by_program(
        self,
        program_id: UUID,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[VulnerabilityReport]:
        """Get all reports for a program."""
        query = self.db.query(VulnerabilityReport).filter(
            VulnerabilityReport.program_id == program_id
        )
        
        if status:
            query = query.filter(VulnerabilityReport.status == status)
        
        return query.order_by(desc(VulnerabilityReport.submitted_at)).offset(offset).limit(limit).all()
    
    def get_by_researcher(
        self,
        researcher_id: UUID,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[VulnerabilityReport]:
        """Get all reports by a researcher."""
        query = self.db.query(VulnerabilityReport).filter(
            VulnerabilityReport.researcher_id == researcher_id,
            VulnerabilityReport.deleted_at.is_(None)  # Exclude deleted reports
        )
        
        if status:
            query = query.filter(VulnerabilityReport.status == status)
        
        return query.order_by(desc(VulnerabilityReport.submitted_at)).offset(offset).limit(limit).all()
    
    def get_triage_queue(
        self,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[VulnerabilityReport]:
        """Get reports in triage queue."""
        query = self.db.query(VulnerabilityReport)
        
        if status:
            query = query.filter(VulnerabilityReport.status == status)
        else:
            # Default: show new and triaged reports
            query = query.filter(
                VulnerabilityReport.status.in_(['new', 'triaged'])
            )
        
        return query.order_by(VulnerabilityReport.submitted_at).offset(offset).limit(limit).all()
    
    def search_similar_reports(
        self,
        program_id: UUID,
        title: str,
        description: str,
        limit: int = 10
    ) -> List[VulnerabilityReport]:
        """Search for similar reports (duplicate detection)."""
        # Simple text similarity search
        # In production, use full-text search or ML-based similarity
        search_term = f"%{title}%"
        
        return self.db.query(VulnerabilityReport).filter(
            and_(
                VulnerabilityReport.program_id == program_id,
                or_(
                    VulnerabilityReport.title.ilike(search_term),
                    VulnerabilityReport.description.ilike(search_term)
                ),
                VulnerabilityReport.status != 'invalid'
            )
        ).limit(limit).all()
    
    def update(self, report: VulnerabilityReport) -> VulnerabilityReport:
        """Update a report."""
        self.db.commit()
        self.db.refresh(report)
        return report
    
    def add_attachment(self, attachment: ReportAttachment) -> ReportAttachment:
        """Add attachment to report."""
        self.db.add(attachment)
        self.db.commit()
        self.db.refresh(attachment)
        return attachment
    
    def get_attachments(self, report_id: UUID) -> List[ReportAttachment]:
        """Get all attachments for a report."""
        return self.db.query(ReportAttachment).filter(
            ReportAttachment.report_id == report_id
        ).all()
    
    def add_comment(self, comment: ReportComment) -> ReportComment:
        """Add comment to report."""
        self.db.add(comment)
        self.db.commit()
        self.db.refresh(comment)
        return comment
    
    def get_comments(
        self,
        report_id: UUID,
        include_internal: bool = False
    ) -> List[ReportComment]:
        """Get all comments for a report."""
        query = self.db.query(ReportComment).filter(
            ReportComment.report_id == report_id
        )
        
        if not include_internal:
            query = query.filter(ReportComment.is_internal == False)
        
        return query.order_by(ReportComment.created_at).all()
    
    def add_status_history(self, history: ReportStatusHistory) -> ReportStatusHistory:
        """Add status change to history."""
        self.db.add(history)
        self.db.commit()
        self.db.refresh(history)
        return history
    
    def get_status_history(self, report_id: UUID) -> List[ReportStatusHistory]:
        """Get status history for a report."""
        return self.db.query(ReportStatusHistory).filter(
            ReportStatusHistory.report_id == report_id
        ).order_by(ReportStatusHistory.changed_at).all()
    
    def get_statistics(self, program_id: Optional[UUID] = None) -> dict:
        """Get report statistics."""
        query = self.db.query(VulnerabilityReport)
        
        if program_id:
            query = query.filter(VulnerabilityReport.program_id == program_id)
        
        total = query.count()
        new = query.filter(VulnerabilityReport.status == 'new').count()
        triaged = query.filter(VulnerabilityReport.status == 'triaged').count()
        valid = query.filter(VulnerabilityReport.status == 'valid').count()
        invalid = query.filter(VulnerabilityReport.status == 'invalid').count()
        duplicate = query.filter(VulnerabilityReport.is_duplicate == True).count()
        resolved = query.filter(VulnerabilityReport.status == 'resolved').count()
        
        return {
            'total': total,
            'new': new,
            'triaged': triaged,
            'valid': valid,
            'invalid': invalid,
            'duplicate': duplicate,
            'resolved': resolved
        }
