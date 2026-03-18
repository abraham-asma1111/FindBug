"""Bounty Service - FREQ-10."""
from typing import List, Optional
from uuid import UUID
from datetime import datetime, timedelta
from decimal import Decimal

from sqlalchemy.orm import Session

from src.domain.models.report import VulnerabilityReport
from src.domain.models.program import BountyProgram, RewardTier
from src.domain.repositories.report_repository import ReportRepository


class BountyService:
    """Service for bounty approval and payout operations."""
    
    def __init__(self, db: Session):
        self.db = db
        self.report_repo = ReportRepository(db)
    
    def calculate_bounty_amount(
        self,
        report_id: UUID
    ) -> dict:
        """
        Calculate bounty amount based on severity and reward tiers - BR-05.
        
        Returns suggested min/max amounts from reward tier.
        """
        report = self.report_repo.get_by_id(report_id)
        
        if not report:
            raise ValueError("Report not found")
        
        if not report.assigned_severity:
            raise ValueError("Report must have assigned severity before calculating bounty")
        
        # Get program reward tiers
        reward_tier = self.db.query(RewardTier).filter(
            RewardTier.program_id == report.program_id,
            RewardTier.severity == report.assigned_severity
        ).first()
        
        if not reward_tier:
            raise ValueError(f"No reward tier defined for {report.assigned_severity} severity")
        
        # Calculate platform commission (30%) - BR-06
        commission_rate = Decimal('0.30')
        
        return {
            'severity': report.assigned_severity,
            'min_amount': reward_tier.min_amount,
            'max_amount': reward_tier.max_amount,
            'suggested_amount': reward_tier.max_amount,  # Default to max
            'commission_rate': commission_rate,
            'commission_amount': reward_tier.max_amount * commission_rate,
            'total_cost': reward_tier.max_amount * (1 + commission_rate)
        }
    
    def approve_bounty(
        self,
        report_id: UUID,
        approved_by: UUID,
        bounty_amount: Decimal,
        notes: Optional[str] = None
    ) -> VulnerabilityReport:
        """
        Approve bounty for a validated report - FREQ-10, BR-05.
        
        Pre-condition: Report status must be 'valid'
        Post-condition: Bounty approved, payout status set to 'pending'
        """
        report = self.report_repo.get_by_id(report_id)
        
        if not report:
            raise ValueError("Report not found")
        
        # Validate report status
        if report.status != 'valid':
            raise ValueError("Only valid reports can receive bounty approval")
        
        if not report.assigned_severity:
            raise ValueError("Report must have assigned severity")
        
        # Validate bounty amount against reward tier - BR-05
        reward_tier = self.db.query(RewardTier).filter(
            RewardTier.program_id == report.program_id,
            RewardTier.severity == report.assigned_severity
        ).first()
        
        if not reward_tier:
            raise ValueError(f"No reward tier defined for {report.assigned_severity} severity")
        
        if bounty_amount < reward_tier.min_amount or bounty_amount > reward_tier.max_amount:
            raise ValueError(
                f"Bounty amount must be between {reward_tier.min_amount} and {reward_tier.max_amount}"
            )
        
        # Handle duplicate reports - BR-07
        if report.is_duplicate and report.duplicate_of:
            original = self.report_repo.get_by_id(report.duplicate_of)
            if original:
                # Check if submitted within 24 hours
                time_diff = report.submitted_at - original.submitted_at
                within_24_hours = time_diff.total_seconds() <= 86400
                
                if within_24_hours:
                    # 50% bounty for duplicates within 24 hours
                    bounty_amount = bounty_amount * Decimal('0.50')
                else:
                    raise ValueError("Duplicate reports submitted after 24 hours are not eligible for bounty")
        
        # Update report
        report.bounty_amount = bounty_amount
        report.bounty_status = 'approved'
        report.bounty_approved_by = approved_by
        report.bounty_approved_at = datetime.utcnow()
        report.updated_at = datetime.utcnow()
        report.last_activity_at = datetime.utcnow()
        
        if notes:
            report.triage_notes = (report.triage_notes or "") + f"\n\nBounty Approval: {notes}"
        
        report = self.report_repo.update(report)
        
        # Update researcher reputation (FREQ-11, BR-09)
        from src.services.reputation_service import ReputationService
        reputation_service = ReputationService(self.db)
        reputation_service.update_reputation(
            researcher_id=report.researcher_id,
            report=report
        )
        
        # Send notification to researcher (FREQ-12)
        from src.services.notification_service import NotificationService
        notification_service = NotificationService(self.db)
        notification_service.notify_bounty_approved(report=report)
        
        return report
    
    def reject_bounty(
        self,
        report_id: UUID,
        rejected_by: UUID,
        reason: str
    ) -> VulnerabilityReport:
        """
        Reject bounty for a report - FREQ-10.
        
        Used when report doesn't meet bounty criteria.
        """
        report = self.report_repo.get_by_id(report_id)
        
        if not report:
            raise ValueError("Report not found")
        
        if report.bounty_status == 'paid':
            raise ValueError("Cannot reject bounty that has already been paid")
        
        # Update report
        report.bounty_status = 'rejected'
        report.bounty_approved_by = rejected_by
        report.bounty_approved_at = datetime.utcnow()
        report.updated_at = datetime.utcnow()
        report.last_activity_at = datetime.utcnow()
        report.triage_notes = (report.triage_notes or "") + f"\n\nBounty Rejected: {reason}"
        
        report = self.report_repo.update(report)
        
        # Update researcher reputation for rejected bounty (FREQ-11, BR-09)
        from src.services.reputation_service import ReputationService
        reputation_service = ReputationService(self.db)
        reputation_service.update_reputation(
            researcher_id=report.researcher_id,
            report=report
        )
        
        # Send notification to researcher (FREQ-12)
        from src.services.notification_service import NotificationService
        notification_service = NotificationService(self.db)
        notification_service.notify_bounty_rejected(report=report, reason=reason)
        
        return report
    
    def mark_as_paid(
        self,
        report_id: UUID,
        paid_by: UUID,
        transaction_reference: Optional[str] = None
    ) -> VulnerabilityReport:
        """
        Mark bounty as paid - FREQ-10, FREQ-20.
        
        Called after payment is processed through payment gateway.
        """
        report = self.report_repo.get_by_id(report_id)
        
        if not report:
            raise ValueError("Report not found")
        
        if report.bounty_status != 'approved':
            raise ValueError("Only approved bounties can be marked as paid")
        
        # Update report
        report.bounty_status = 'paid'
        report.updated_at = datetime.utcnow()
        report.last_activity_at = datetime.utcnow()
        
        if transaction_reference:
            report.triage_notes = (report.triage_notes or "") + f"\n\nPayment Reference: {transaction_reference}"
        
        report = self.report_repo.update(report)
        
        # Update researcher earnings (FREQ-11)
        from src.services.reputation_service import ReputationService
        reputation_service = ReputationService(self.db)
        reputation_service.update_reputation(
            researcher_id=report.researcher_id,
            report=report
        )
        
        # Send payment confirmation notification (FREQ-12)
        from src.services.notification_service import NotificationService
        notification_service = NotificationService(self.db)
        notification_service.notify_bounty_paid(report=report)
        
        return report
    
    def get_pending_payouts(
        self,
        program_id: Optional[UUID] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[VulnerabilityReport]:
        """
        Get all reports with pending payouts - FREQ-20.
        
        Used by finance officers to process payments.
        """
        query = self.db.query(VulnerabilityReport).filter(
            VulnerabilityReport.bounty_status == 'approved'
        )
        
        if program_id:
            query = query.filter(VulnerabilityReport.program_id == program_id)
        
        # Order by approval date (oldest first) - BR-08: 30-day processing timeline
        query = query.order_by(VulnerabilityReport.bounty_approved_at.asc())
        
        return query.offset(offset).limit(limit).all()
    
    def get_overdue_payouts(
        self,
        days: int = 30
    ) -> List[VulnerabilityReport]:
        """
        Get overdue payouts - BR-08.
        
        Bounties must be processed within 30 days.
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        return self.db.query(VulnerabilityReport).filter(
            VulnerabilityReport.bounty_status == 'approved',
            VulnerabilityReport.bounty_approved_at < cutoff_date
        ).all()
    
    def get_payout_statistics(
        self,
        program_id: Optional[UUID] = None
    ) -> dict:
        """
        Get payout statistics - FREQ-15, FREQ-20.
        
        Shows total paid, pending, and rejected bounties.
        """
        query = self.db.query(VulnerabilityReport)
        
        if program_id:
            query = query.filter(VulnerabilityReport.program_id == program_id)
        
        # Count by status
        approved = query.filter(VulnerabilityReport.bounty_status == 'approved').count()
        paid = query.filter(VulnerabilityReport.bounty_status == 'paid').count()
        rejected = query.filter(VulnerabilityReport.bounty_status == 'rejected').count()
        
        # Calculate amounts
        total_approved = self.db.query(
            self.db.func.sum(VulnerabilityReport.bounty_amount)
        ).filter(
            VulnerabilityReport.bounty_status == 'approved'
        )
        if program_id:
            total_approved = total_approved.filter(VulnerabilityReport.program_id == program_id)
        total_approved = total_approved.scalar() or Decimal('0')
        
        total_paid = self.db.query(
            self.db.func.sum(VulnerabilityReport.bounty_amount)
        ).filter(
            VulnerabilityReport.bounty_status == 'paid'
        )
        if program_id:
            total_paid = total_paid.filter(VulnerabilityReport.program_id == program_id)
        total_paid = total_paid.scalar() or Decimal('0')
        
        # Calculate commission (30%) - BR-06
        commission_rate = Decimal('0.30')
        total_commission = total_paid * commission_rate
        
        return {
            'counts': {
                'approved': approved,
                'paid': paid,
                'rejected': rejected
            },
            'amounts': {
                'total_approved': float(total_approved),
                'total_paid': float(total_paid),
                'total_commission': float(total_commission),
                'total_cost': float(total_paid * (1 + commission_rate))
            }
        }
