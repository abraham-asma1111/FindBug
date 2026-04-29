"""
Finance Reports Endpoints — API routes for financial reporting
"""
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta
from uuid import UUID
import csv
import io

from src.core.database import get_db
from src.domain.models.user import User
from src.core.dependencies import require_financial
from src.services.payment_service import PaymentService

router = APIRouter(prefix="/finance/reports", tags=["Finance Reports"])


@router.get(
    "/payments",
    summary="Generate Payments Report",
    description="Generate payments report with filters (Admin/Finance Officer only)"
)
async def generate_payments_report(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    status: Optional[str] = None,
    format: str = "json",
    current_user: User = Depends(require_financial),
    db: Session = Depends(get_db)
):
    """
    Generate payments report.
    
    Query params:
    - start_date: Start date (YYYY-MM-DD)
    - end_date: End date (YYYY-MM-DD)
    - status: Filter by status
    - format: json or csv
    """
    try:
        from src.domain.models.bounty_payment import BountyPayment
        from src.domain.models.researcher import Researcher
        from src.domain.models.organization import Organization
        from src.domain.models.report import VulnerabilityReport
        from sqlalchemy import func
        
        # Parse dates
        start = datetime.fromisoformat(start_date) if start_date else datetime.utcnow() - timedelta(days=30)
        end = datetime.fromisoformat(end_date) if end_date else datetime.utcnow()
        
        # Query payments
        query = db.query(
            BountyPayment,
            Researcher.username.label('researcher_name'),
            Organization.name.label('organization_name'),
            VulnerabilityReport.title.label('report_title'),
            VulnerabilityReport.severity.label('severity')
        ).join(
            Researcher, BountyPayment.researcher_id == Researcher.id
        ).join(
            Organization, BountyPayment.organization_id == Organization.id
        ).join(
            VulnerabilityReport, BountyPayment.report_id == VulnerabilityReport.id
        ).filter(
            BountyPayment.created_at >= start,
            BountyPayment.created_at <= end
        )
        
        if status:
            query = query.filter(BountyPayment.status == status)
        
        payments = query.all()
        
        # Format data
        data = [
            {
                'payment_id': str(p.BountyPayment.payment_id),
                'transaction_id': p.BountyPayment.transaction_id,
                'researcher': p.researcher_name,
                'organization': p.organization_name,
                'report_title': p.report_title,
                'severity': p.severity,
                'researcher_amount': float(p.BountyPayment.researcher_amount),
                'commission_amount': float(p.BountyPayment.commission_amount),
                'total_amount': float(p.BountyPayment.total_amount),
                'status': p.BountyPayment.status,
                'payment_method': p.BountyPayment.payment_method,
                'created_at': p.BountyPayment.created_at.isoformat(),
                'completed_at': p.BountyPayment.completed_at.isoformat() if p.BountyPayment.completed_at else None
            }
            for p in payments
        ]
        
        # Calculate summary
        total_payments = len(data)
        total_amount = sum(d['researcher_amount'] for d in data)
        total_commission = sum(d['commission_amount'] for d in data)
        
        if format == 'csv':
            # Generate CSV
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=data[0].keys() if data else [])
            writer.writeheader()
            writer.writerows(data)
            
            return Response(
                content=output.getvalue(),
                media_type='text/csv',
                headers={'Content-Disposition': f'attachment; filename=payments_report_{start.date()}_{end.date()}.csv'}
            )
        
        return {
            'report_type': 'payments',
            'start_date': start.isoformat(),
            'end_date': end.isoformat(),
            'summary': {
                'total_payments': total_payments,
                'total_amount': total_amount,
                'total_commission': total_commission,
                'average_payment': total_amount / total_payments if total_payments > 0 else 0
            },
            'data': data
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate payments report: {str(e)}"
        )


@router.get(
    "/payouts",
    summary="Generate Payouts Report",
    description="Generate payouts report with filters (Admin/Finance Officer only)"
)
async def generate_payouts_report(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    status: Optional[str] = None,
    format: str = "json",
    current_user: User = Depends(require_financial),
    db: Session = Depends(get_db)
):
    """Generate payouts report."""
    try:
        from src.domain.models.payment_extended import PayoutRequest
        from src.domain.models.researcher import Researcher
        
        # Parse dates
        start = datetime.fromisoformat(start_date) if start_date else datetime.utcnow() - timedelta(days=30)
        end = datetime.fromisoformat(end_date) if end_date else datetime.utcnow()
        
        # Query payouts
        query = db.query(
            PayoutRequest,
            Researcher.username.label('researcher_name')
        ).join(
            Researcher, PayoutRequest.researcher_id == Researcher.id
        ).filter(
            PayoutRequest.created_at >= start,
            PayoutRequest.created_at <= end
        )
        
        if status:
            query = query.filter(PayoutRequest.status == status)
        
        payouts = query.all()
        
        # Format data
        data = [
            {
                'payout_id': str(p.PayoutRequest.id),
                'researcher': p.researcher_name,
                'amount': float(p.PayoutRequest.amount),
                'payment_method': p.PayoutRequest.payment_method,
                'status': p.PayoutRequest.status,
                'created_at': p.PayoutRequest.created_at.isoformat(),
                'processed_at': p.PayoutRequest.processed_at.isoformat() if p.PayoutRequest.processed_at else None
            }
            for p in payouts
        ]
        
        # Calculate summary
        total_payouts = len(data)
        total_amount = sum(d['amount'] for d in data)
        
        if format == 'csv':
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=data[0].keys() if data else [])
            writer.writeheader()
            writer.writerows(data)
            
            return Response(
                content=output.getvalue(),
                media_type='text/csv',
                headers={'Content-Disposition': f'attachment; filename=payouts_report_{start.date()}_{end.date()}.csv'}
            )
        
        return {
            'report_type': 'payouts',
            'start_date': start.isoformat(),
            'end_date': end.isoformat(),
            'summary': {
                'total_payouts': total_payouts,
                'total_amount': total_amount,
                'average_payout': total_amount / total_payouts if total_payouts > 0 else 0
            },
            'data': data
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate payouts report: {str(e)}"
        )


@router.get(
    "/financial-summary",
    summary="Generate Financial Summary Report",
    description="Generate comprehensive financial summary (Admin/Finance Officer only)"
)
async def generate_financial_summary(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: User = Depends(require_financial),
    db: Session = Depends(get_db)
):
    """Generate comprehensive financial summary."""
    try:
        from src.domain.models.bounty_payment import BountyPayment
        from src.domain.models.payment_extended import PayoutRequest
        from src.domain.models.organization import Organization
        from sqlalchemy import func
        
        # Parse dates
        start = datetime.fromisoformat(start_date) if start_date else datetime.utcnow() - timedelta(days=30)
        end = datetime.fromisoformat(end_date) if end_date else datetime.utcnow()
        
        # Payments summary
        payments = db.query(
            func.count(BountyPayment.payment_id).label('count'),
            func.sum(BountyPayment.researcher_amount).label('researcher_total'),
            func.sum(BountyPayment.commission_amount).label('commission_total'),
            func.sum(BountyPayment.total_amount).label('total')
        ).filter(
            BountyPayment.created_at >= start,
            BountyPayment.created_at <= end
        ).first()
        
        # Payouts summary
        payouts = db.query(
            func.count(PayoutRequest.id).label('count'),
            func.sum(PayoutRequest.amount).label('total')
        ).filter(
            PayoutRequest.created_at >= start,
            PayoutRequest.created_at <= end
        ).first()
        
        # Revenue by organization
        org_revenue = db.query(
            Organization.name,
            func.sum(BountyPayment.total_amount).label('revenue')
        ).join(
            BountyPayment, BountyPayment.organization_id == Organization.id
        ).filter(
            BountyPayment.created_at >= start,
            BountyPayment.created_at <= end
        ).group_by(Organization.name).all()
        
        return {
            'report_type': 'financial_summary',
            'period': {
                'start_date': start.isoformat(),
                'end_date': end.isoformat()
            },
            'payments': {
                'count': payments.count or 0,
                'researcher_total': float(payments.researcher_total or 0),
                'commission_total': float(payments.commission_total or 0),
                'total': float(payments.total or 0)
            },
            'payouts': {
                'count': payouts.count or 0,
                'total': float(payouts.total or 0)
            },
            'revenue_by_organization': [
                {'organization': r.name, 'revenue': float(r.revenue)}
                for r in org_revenue
            ],
            'net_revenue': float(payments.commission_total or 0)
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate financial summary: {str(e)}"
        )


@router.get(
    "/tax",
    summary="Generate Tax Report",
    description="Generate tax report for compliance (Admin/Finance Officer only)"
)
async def generate_tax_report(
    year: int,
    quarter: Optional[int] = None,
    format: str = "json",
    current_user: User = Depends(require_financial),
    db: Session = Depends(get_db)
):
    """Generate tax report."""
    try:
        from src.domain.models.bounty_payment import BountyPayment
        from src.domain.models.researcher import Researcher
        from sqlalchemy import func, extract
        
        # Calculate date range
        if quarter:
            start_month = (quarter - 1) * 3 + 1
            end_month = start_month + 2
            start = datetime(year, start_month, 1)
            end = datetime(year, end_month, 28) + timedelta(days=4)
            end = end - timedelta(days=end.day)
        else:
            start = datetime(year, 1, 1)
            end = datetime(year, 12, 31)
        
        # Query payments
        payments = db.query(
            Researcher.username,
            Researcher.user_id,
            func.sum(BountyPayment.researcher_amount).label('total_paid'),
            func.count(BountyPayment.payment_id).label('payment_count')
        ).join(
            BountyPayment, BountyPayment.researcher_id == Researcher.id
        ).filter(
            BountyPayment.created_at >= start,
            BountyPayment.created_at <= end,
            BountyPayment.status == 'completed'
        ).group_by(
            Researcher.id, Researcher.username, Researcher.user_id
        ).all()
        
        data = [
            {
                'researcher': p.username,
                'user_id': str(p.user_id),
                'total_paid': float(p.total_paid),
                'payment_count': p.payment_count,
                'tax_year': year,
                'quarter': quarter
            }
            for p in payments
        ]
        
        if format == 'csv':
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=data[0].keys() if data else [])
            writer.writeheader()
            writer.writerows(data)
            
            return Response(
                content=output.getvalue(),
                media_type='text/csv',
                headers={'Content-Disposition': f'attachment; filename=tax_report_{year}_Q{quarter or "ALL"}.csv'}
            )
        
        return {
            'report_type': 'tax',
            'year': year,
            'quarter': quarter,
            'period': {
                'start_date': start.isoformat(),
                'end_date': end.isoformat()
            },
            'data': data,
            'summary': {
                'total_researchers': len(data),
                'total_paid': sum(d['total_paid'] for d in data)
            }
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate tax report: {str(e)}"
        )
