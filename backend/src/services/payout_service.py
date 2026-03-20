"""Payout tracking service - FREQ-20."""
from typing import List, Optional, Dict
from uuid import UUID
from datetime import datetime
from decimal import Decimal

from sqlalchemy.orm import Session
from sqlalchemy import func

from src.domain.models.report import VulnerabilityReport
from src.domain.models.researcher import Researcher
from src.domain.models.organization import Organization


class PayoutService:
    """Service for payout tracking - FREQ-20."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_pending_payouts(
        self,
        organization_id: Optional[UUID] = None,
        researcher_id: Optional[UUID] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict]:
        """Get pending payouts - FREQ-20."""
        query = self.db.query(VulnerabilityReport).filter(
            VulnerabilityReport.bounty_status == "approved",
            VulnerabilityReport.bounty_amount.isnot(None)
        )
        
        if organization_id:
            from src.domain.models.program import BountyProgram
            query = query.join(BountyProgram).filter(
                BountyProgram.organization_id == organization_id
            )
        
        if researcher_id:
            query = query.filter(
                VulnerabilityReport.researcher_id == researcher_id
            )
        
        reports = query.order_by(
            VulnerabilityReport.bounty_approved_at.desc()
        ).limit(limit).offset(offset).all()
        
        return [
            {
                "report_id": str(r.id),
                "report_number": r.report_number,
                "researcher_id": str(r.researcher_id),
                "amount": float(r.bounty_amount),
                "approved_at": r.bounty_approved_at,
                "status": "pending"
            }
            for r in reports
        ]
    
    def get_processed_payouts(
        self,
        organization_id: Optional[UUID] = None,
        researcher_id: Optional[UUID] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict]:
        """Get processed payouts - FREQ-20."""
        query = self.db.query(VulnerabilityReport).filter(
            VulnerabilityReport.bounty_status == "paid",
            VulnerabilityReport.bounty_amount.isnot(None)
        )
        
        if organization_id:
            from src.domain.models.program import BountyProgram
            query = query.join(BountyProgram).filter(
                BountyProgram.organization_id == organization_id
            )
        
        if researcher_id:
            query = query.filter(
                VulnerabilityReport.researcher_id == researcher_id
            )
        
        reports = query.order_by(
            VulnerabilityReport.bounty_approved_at.desc()
        ).limit(limit).offset(offset).all()
        
        return [
            {
                "report_id": str(r.id),
                "report_number": r.report_number,
                "researcher_id": str(r.researcher_id),
                "amount": float(r.bounty_amount),
                "approved_at": r.bounty_approved_at,
                "status": "paid"
            }
            for r in reports
        ]
    
    def get_payout_summary(
        self,
        organization_id: Optional[UUID] = None,
        researcher_id: Optional[UUID] = None
    ) -> Dict:
        """Get payout summary - FREQ-20."""
        from src.domain.models.program import BountyProgram
        
        base_query = self.db.query(VulnerabilityReport).filter(
            VulnerabilityReport.bounty_amount.isnot(None)
        )
        
        if organization_id:
            base_query = base_query.join(BountyProgram).filter(
                BountyProgram.organization_id == organization_id
            )
        
        if researcher_id:
            base_query = base_query.filter(
                VulnerabilityReport.researcher_id == researcher_id
            )
        
        # Pending payouts
        pending_total = base_query.filter(
            VulnerabilityReport.bounty_status == "approved"
        ).with_entities(
            func.sum(VulnerabilityReport.bounty_amount)
        ).scalar() or 0
        
        pending_count = base_query.filter(
            VulnerabilityReport.bounty_status == "approved"
        ).count()
        
        # Processed payouts
        paid_total = base_query.filter(
            VulnerabilityReport.bounty_status == "paid"
        ).with_entities(
            func.sum(VulnerabilityReport.bounty_amount)
        ).scalar() or 0
        
        paid_count = base_query.filter(
            VulnerabilityReport.bounty_status == "paid"
        ).count()
        
        return {
            "pending": {
                "total_amount": float(pending_total),
                "count": pending_count
            },
            "processed": {
                "total_amount": float(paid_total),
                "count": paid_count
            },
            "total": {
                "total_amount": float(pending_total + paid_total),
                "count": pending_count + paid_count
            }
        }
    
    def initiate_payout(
        self,
        report_id: UUID,
        payment_method: str = "manual",
        payment_details: Optional[Dict] = None
    ) -> Dict:
        """
        Initiate payout - FREQ-20.
        
        Placeholder for future payment gateway integration.
        """
        report = self.db.query(VulnerabilityReport).filter(
            VulnerabilityReport.id == report_id
        ).first()
        
        if not report:
            raise ValueError("Report not found")
        
        if report.bounty_status != "approved":
            raise ValueError("Bounty must be approved before payout")
        
        # Placeholder for payment gateway integration
        # TODO: Integrate with Telebirr, bank APIs, etc.
        
        return {
            "report_id": str(report_id),
            "amount": float(report.bounty_amount),
            "payment_method": payment_method,
            "status": "pending",
            "message": "Payout initiated - awaiting payment gateway integration"
        }
    
    def get_researcher_earnings(self, researcher_id: UUID) -> Dict:
        """Get researcher earnings breakdown - FREQ-20."""
        reports = self.db.query(VulnerabilityReport).filter(
            VulnerabilityReport.researcher_id == researcher_id,
            VulnerabilityReport.bounty_amount.isnot(None)
        ).all()
        
        total_earned = sum(float(r.bounty_amount) for r in reports if r.bounty_status == "paid")
        pending = sum(float(r.bounty_amount) for r in reports if r.bounty_status == "approved")
        
        # Earnings by severity
        by_severity = {}
        for report in reports:
            if report.assigned_severity and report.bounty_status == "paid":
                severity = report.assigned_severity
                by_severity[severity] = by_severity.get(severity, 0) + float(report.bounty_amount)
        
        return {
            "total_earned": total_earned,
            "pending": pending,
            "total_reports_paid": len([r for r in reports if r.bounty_status == "paid"]),
            "by_severity": by_severity
        }
