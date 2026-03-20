"""
Code Review Service
Implements FREQ-41: Expert Code Review System
"""
from typing import List, Optional, Dict
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.src.domain.models.code_review import (
    CodeReviewEngagement,
    CodeReviewFinding,
    ReviewStatus,
    ReviewType,
    FindingSeverity,
    FindingStatus,
    IssueType
)
from backend.src.services.matching_service import MatchingService


class CodeReviewService:
    """Service for managing code review engagements"""

    def __init__(self, db: Session):
        self.db = db
        self.matching_service = MatchingService(db)

    def create_engagement(
        self,
        organization_id: UUID,
        title: str,
        repository_url: str,
        review_type: ReviewType
    ) -> CodeReviewEngagement:
        """Create a new code review engagement"""
        engagement = CodeReviewEngagement(
            organization_id=organization_id,
            title=title,
            repository_url=repository_url,
            review_type=review_type,
            status=ReviewStatus.PENDING
        )
        
        self.db.add(engagement)
        self.db.commit()
        self.db.refresh(engagement)
        
        return engagement

    def assign_reviewer(self, engagement_id: UUID, reviewer_id: UUID) -> CodeReviewEngagement:
        """Assign a reviewer to an engagement"""
        engagement = self.db.query(CodeReviewEngagement).filter(
            CodeReviewEngagement.id == engagement_id
        ).first()
        
        if not engagement:
            raise ValueError("Engagement not found")
        
        engagement.reviewer_id = reviewer_id
        engagement.status = ReviewStatus.ASSIGNED
        
        self.db.commit()
        self.db.refresh(engagement)
        
        return engagement

    def start_review(self, engagement_id: UUID) -> CodeReviewEngagement:
        """Start a code review"""
        engagement = self.db.query(CodeReviewEngagement).filter(
            CodeReviewEngagement.id == engagement_id
        ).first()
        
        if not engagement:
            raise ValueError("Engagement not found")
        
        if engagement.status != ReviewStatus.ASSIGNED:
            raise ValueError("Engagement must be assigned before starting")
        
        engagement.status = ReviewStatus.IN_PROGRESS
        
        self.db.commit()
        self.db.refresh(engagement)
        
        return engagement

    def add_finding(
        self,
        engagement_id: UUID,
        title: str,
        description: str,
        severity: FindingSeverity,
        issue_type: IssueType,
        file_path: Optional[str] = None,
        line_number: Optional[int] = None
    ) -> CodeReviewFinding:
        """Add a finding to a code review"""
        engagement = self.db.query(CodeReviewEngagement).filter(
            CodeReviewEngagement.id == engagement_id
        ).first()
        
        if not engagement:
            raise ValueError("Engagement not found")
        
        finding = CodeReviewFinding(
            engagement_id=engagement_id,
            title=title,
            description=description,
            severity=severity,
            issue_type=issue_type,
            file_path=file_path,
            line_number=line_number,
            status=FindingStatus.OPEN
        )
        
        self.db.add(finding)
        
        # Update findings count
        engagement.findings_count = self.db.query(func.count(CodeReviewFinding.id)).filter(
            CodeReviewFinding.engagement_id == engagement_id
        ).scalar() + 1
        
        self.db.commit()
        self.db.refresh(finding)
        
        return finding

    def update_finding_status(
        self,
        finding_id: UUID,
        status: FindingStatus
    ) -> CodeReviewFinding:
        """Update finding status"""
        finding = self.db.query(CodeReviewFinding).filter(
            CodeReviewFinding.id == finding_id
        ).first()
        
        if not finding:
            raise ValueError("Finding not found")
        
        finding.status = status
        
        self.db.commit()
        self.db.refresh(finding)
        
        return finding

    def submit_report(self, engagement_id: UUID) -> CodeReviewEngagement:
        """Submit code review report"""
        engagement = self.db.query(CodeReviewEngagement).filter(
            CodeReviewEngagement.id == engagement_id
        ).first()
        
        if not engagement:
            raise ValueError("Engagement not found")
        
        engagement.status = ReviewStatus.COMPLETED
        engagement.report_submitted_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(engagement)
        
        return engagement

    def get_engagement(self, engagement_id: UUID) -> Optional[CodeReviewEngagement]:
        """Get engagement by ID"""
        return self.db.query(CodeReviewEngagement).filter(
            CodeReviewEngagement.id == engagement_id
        ).first()

    def get_organization_engagements(
        self,
        organization_id: UUID,
        status: Optional[ReviewStatus] = None
    ) -> List[CodeReviewEngagement]:
        """Get all engagements for an organization"""
        query = self.db.query(CodeReviewEngagement).filter(
            CodeReviewEngagement.organization_id == organization_id
        )
        
        if status:
            query = query.filter(CodeReviewEngagement.status == status)
        
        return query.order_by(CodeReviewEngagement.created_at.desc()).all()

    def get_reviewer_engagements(
        self,
        reviewer_id: UUID,
        status: Optional[ReviewStatus] = None
    ) -> List[CodeReviewEngagement]:
        """Get all engagements for a reviewer"""
        query = self.db.query(CodeReviewEngagement).filter(
            CodeReviewEngagement.reviewer_id == reviewer_id
        )
        
        if status:
            query = query.filter(CodeReviewEngagement.status == status)
        
        return query.order_by(CodeReviewEngagement.created_at.desc()).all()

    def get_engagement_findings(
        self,
        engagement_id: UUID,
        severity: Optional[FindingSeverity] = None,
        status: Optional[FindingStatus] = None
    ) -> List[CodeReviewFinding]:
        """Get findings for an engagement"""
        query = self.db.query(CodeReviewFinding).filter(
            CodeReviewFinding.engagement_id == engagement_id
        )
        
        if severity:
            query = query.filter(CodeReviewFinding.severity == severity)
        
        if status:
            query = query.filter(CodeReviewFinding.status == status)
        
        return query.order_by(CodeReviewFinding.severity.desc(), CodeReviewFinding.created_at.desc()).all()

    def get_engagement_stats(self, engagement_id: UUID) -> Dict:
        """Get statistics for an engagement"""
        findings = self.db.query(CodeReviewFinding).filter(
            CodeReviewFinding.engagement_id == engagement_id
        ).all()
        
        stats = {
            "total_findings": len(findings),
            "by_severity": {
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0,
                "info": 0
            },
            "by_status": {
                "open": 0,
                "acknowledged": 0,
                "fixed": 0,
                "wont_fix": 0,
                "false_positive": 0
            },
            "by_issue_type": {}
        }
        
        for finding in findings:
            stats["by_severity"][finding.severity.value] += 1
            stats["by_status"][finding.status.value] += 1
            
            issue_type = finding.issue_type.value
            stats["by_issue_type"][issue_type] = stats["by_issue_type"].get(issue_type, 0) + 1
        
        return stats
