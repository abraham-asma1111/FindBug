"""
Code Review Service
Implements FREQ-41: Expert Code Review System
"""
from typing import List, Optional, Dict
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func, or_

from src.domain.models.code_review import (
    CodeReviewEngagement,
    CodeReviewFinding,
    ReviewStatus,
    ReviewType,
    FindingSeverity,
    FindingStatus,
    IssueType
)
from src.services.matching_service import MatchingService
from src.services.notification_service import NotificationService
from src.domain.models.notification import NotificationType, NotificationPriority
from src.domain.models.organization import Organization
from src.services.notification_service import NotificationService
from src.domain.models.notification import NotificationType, NotificationPriority
from src.domain.models.organization import Organization


class CodeReviewService:
    """Service for managing code review engagements"""

    def __init__(self, db: Session):
        self.db = db
        self.matching_service = MatchingService(db)
        self.notification_service = NotificationService(db)
        self.notification_service = NotificationService(db)

    def _notify_organization(
        self,
        organization_id: UUID,
        title: str,
        message: str,
        engagement_id: UUID,
        priority: NotificationPriority = NotificationPriority.MEDIUM,
    ) -> None:
        org = self.db.query(Organization).filter(Organization.id == organization_id).first()
        if not org:
            return
        self.notification_service.create_notification(
            user_id=org.user_id,
            notification_type=NotificationType.REPORT_STATUS_CHANGED,
            title=title,
            message=message,
            priority=priority,
            related_entity_type="code_review_engagement",
            related_entity_id=engagement_id,
            action_url="/organization/services/code-review",
            action_text="View code review report",
        )

    @staticmethod
    def assigned_reviewer_ids_for(engagement: CodeReviewEngagement) -> List[str]:
        """All reviewer IDs on an engagement (JSON list + legacy reviewer_id)."""
        ids: List[str] = []
        raw = engagement.assigned_reviewer_ids
        if isinstance(raw, list):
            ids = [str(x) for x in raw]
        if engagement.reviewer_id:
            primary = str(engagement.reviewer_id)
            if primary not in ids:
                ids.append(primary)
        return ids

    @staticmethod
    def is_reviewer_assigned(engagement: CodeReviewEngagement, reviewer_id: UUID) -> bool:
        return str(reviewer_id) in CodeReviewService.assigned_reviewer_ids_for(engagement)

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
        """Assign a single reviewer (legacy)."""
        return self.assign_reviewers(engagement_id, [reviewer_id])

    def assign_reviewers(
        self, engagement_id: UUID, reviewer_ids: List[UUID]
    ) -> CodeReviewEngagement:
        """Assign one or more reviewers; merges with existing team."""
        engagement = self.db.query(CodeReviewEngagement).filter(
            CodeReviewEngagement.id == engagement_id
        ).first()

        if not engagement:
            raise ValueError("Engagement not found")

        if not reviewer_ids:
            raise ValueError("At least one reviewer is required")

        existing = self.assigned_reviewer_ids_for(engagement)
        merged: List[str] = existing.copy()
        for rid in reviewer_ids:
            sid = str(rid)
            if sid not in merged:
                merged.append(sid)

        engagement.assigned_reviewer_ids = merged
        engagement.reviewer_id = UUID(merged[0])
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
        
        self.db.flush()
        engagement.findings_count = self.db.query(func.count(CodeReviewFinding.id)).filter(
            CodeReviewFinding.engagement_id == engagement_id
        ).scalar() or 0

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

        self._notify_organization_report_submitted(engagement)

        return engagement

    def _notify_organization_report_submitted(self, engagement: CodeReviewEngagement) -> None:
        """Notify the organization when a code review report is submitted."""
        org = self.db.query(Organization).filter(
            Organization.id == engagement.organization_id
        ).first()
        if not org:
            return

        findings_count = engagement.findings_count or 0
        self.notification_service.create_notification(
            user_id=org.user_id,
            notification_type=NotificationType.REPORT_SUBMITTED,
            title=f"Code review report delivered: {engagement.title}",
            message=(
                f"The researcher submitted the final code review report with "
                f"{findings_count} finding(s). Open the report to review and triage."
            ),
            priority=NotificationPriority.HIGH,
            related_entity_type="code_review_engagement",
            related_entity_id=engagement.id,
            action_url=f"/organization/services/code-review?engagement={engagement.id}",
            action_text="View report",
        )

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
        rid = str(reviewer_id)
        query = self.db.query(CodeReviewEngagement).filter(
            or_(
                CodeReviewEngagement.reviewer_id == reviewer_id,
                CodeReviewEngagement.assigned_reviewer_ids.contains([rid]),
            )
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
