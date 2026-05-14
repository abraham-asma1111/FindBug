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
