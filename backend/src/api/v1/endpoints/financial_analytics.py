"""Financial Analytics API Endpoints"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional

from src.core.database import get_db
from src.core.dependencies import require_financial
from src.domain.models.user import User
from src.services.financial_analytics_service import FinancialAnalyticsService

router = APIRouter(prefix="/finance/analytics", tags=["Financial Analytics"])


@router.get("/executive-kpis")
def get_executive_kpis(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_financial)
):
    """
    Get executive-level KPIs:
    - Total Revenue
    - Net Profit
    - Gross Margin
    - Cash Balance
    - Revenue Growth
    - Total Payouts
    - Pending Payouts
    - Active Programs
    """
    service = FinancialAnalyticsService(db)
    return service.get_executive_kpis(start_date, end_date)


@router.get("/revenue")
def get_revenue_analytics(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_financial)
):
    """
    Get comprehensive revenue analytics:
    - Monthly revenue trend
    - Revenue by customer
    - Annual Recurring Revenue (ARR)
    - Revenue per customer
    """
    service = FinancialAnalyticsService(db)
    return service.get_revenue_analytics(start_date, end_date)


@router.get("/bounty-economics")
def get_bounty_economics(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_financial)
):
    """
    Get bounty economics:
    - Total payouts
    - Average bounty by severity
    - Payout distribution
    - Top researchers
    """
    service = FinancialAnalyticsService(db)
    return service.get_bounty_economics(start_date, end_date)


@router.get("/program-economics")
def get_program_economics(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_financial)
):
    """
    Get program-level economics:
    - Program ROI
    - Cost per vulnerability
    - Profitability by program
    - Revenue vs bounty cost
    """
    service = FinancialAnalyticsService(db)
    return service.get_program_economics(start_date, end_date)


@router.get("/cash-flow")
def get_cash_flow_analysis(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_financial)
):
    """
    Get cash flow analysis:
    - Monthly cash flow trend
    - Current cash position
    - Pending obligations
    - Net cash available
    """
    service = FinancialAnalyticsService(db)
    return service.get_cash_flow_analysis(start_date, end_date)


@router.get("/recent-payments")
def get_recent_payments(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_financial)
):
    """
    Get recent bounty payments enriched with researcher, report, and program info.
    Used for the Finance Dashboard recent payouts table.
    """
    service = FinancialAnalyticsService(db)
    payments = service.get_recent_payments(limit=limit)
    return {
        "payments": payments,
        "total": len(payments)
    }


@router.get("/top-programs-by-reports")
def get_top_programs_by_reports(
    limit: int = Query(5, ge=1, le=20),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_financial)
):
    """
    Get top programs ranked by number of vulnerability reports submitted.
    Returns every program that has at least one report, regardless of payment status.
    Used for the Finance Dashboard 'Top Programs by Reports' card.
    """
    from sqlalchemy import func
    from src.domain.models.program import BountyProgram
    from src.domain.models.report import VulnerabilityReport

    results = (
        db.query(
            BountyProgram.id,
            BountyProgram.name,
            func.count(VulnerabilityReport.id).label("report_count"),
        )
        .outerjoin(VulnerabilityReport, VulnerabilityReport.program_id == BountyProgram.id)
        .group_by(BountyProgram.id, BountyProgram.name)
        .having(func.count(VulnerabilityReport.id) > 0)
        .order_by(func.count(VulnerabilityReport.id).desc())
        .limit(limit)
        .all()
    )

    return {
        "programs": [
            {
                "program_id": str(r.id),
                "program_name": r.name,
                "report_count": r.report_count,
            }
            for r in results
        ],
        "total": len(results),
    }


@router.get("/recent-reports")
def get_recent_reports(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_financial)
):
    """
    Get the most recently submitted vulnerability reports platform-wide.
    Used for the Finance Dashboard 'Recent Reports' card.
    """
    from src.domain.models.report import VulnerabilityReport
    from src.domain.models.program import BountyProgram
    from sqlalchemy import desc

    reports = (
        db.query(VulnerabilityReport)
        .order_by(desc(VulnerabilityReport.submitted_at))
        .limit(limit)
        .all()
    )

    result = []
    for r in reports:
        program = db.query(BountyProgram).filter(BountyProgram.id == r.program_id).first() if r.program_id else None
        result.append({
            "id": str(r.id),
            "report_number": r.report_number,
            "title": r.title,
            "status": r.status,
            "assigned_severity": r.assigned_severity,
            "program_name": program.name if program else "Unknown Program",
            "submitted_at": r.submitted_at.isoformat() if r.submitted_at else None,
        })

    return {"reports": result, "total": len(result)}
