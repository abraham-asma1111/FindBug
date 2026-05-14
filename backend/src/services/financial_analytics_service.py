"""
Financial Analytics Service - Industry-Standard Financial Intelligence
Provides comprehensive financial metrics for bug bounty platform operations
"""
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, extract
from uuid import UUID

from src.domain.models.bounty_payment import BountyPayment
from src.domain.models.organization import Organization
from src.domain.models.researcher import Researcher
from src.domain.models.report import VulnerabilityReport
from src.domain.models.program import BountyProgram


class FinancialAnalyticsService:
    """
    Comprehensive financial analytics service for bug bounty platform.
    Provides metrics for revenue, expenses, profitability, cash flow, and forecasting.
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    # ==================== EXECUTIVE KPIs ====================
    
    def get_executive_kpis(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get executive-level KPIs for dashboard.
        Returns: Total Revenue, Net Profit, Gross Margin, Cash Balance, Growth Rate
        """
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=30)
        if not end_date:
            end_date = datetime.utcnow()
        
        # Calculate current period metrics
        current_metrics = self._calculate_period_metrics(start_date, end_date)
        
        # Calculate previous period for comparison
        period_length = (end_date - start_date).days
        prev_start = start_date - timedelta(days=period_length)
        prev_end = start_date
        previous_metrics = self._calculate_period_metrics(prev_start, prev_end)
        
        # Calculate growth rates
        revenue_growth = self._calculate_growth_rate(
            previous_metrics['total_revenue'],
            current_metrics['total_revenue']
        )
        
        return {
            'total_revenue': float(current_metrics['total_revenue']),
            'net_profit': float(current_metrics['net_profit']),
            'gross_margin': float(current_metrics['gross_margin']),
            'cash_balance': float(current_metrics['cash_balance']),
            'revenue_growth': revenue_growth,
            'total_payouts': float(current_metrics['total_payouts']),
            'pending_payouts': float(current_metrics['pending_payouts']),
            'active_programs': current_metrics['active_programs'],
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            }
        }
    
    def _calculate_period_metrics(self, start_date: datetime, end_date: datetime) -> Dict:
        """Calculate financial metrics for a specific period"""
        
        # Total Revenue (sum of all payments - this represents platform revenue)
        revenue_query = self.db.query(
            func.sum(BountyPayment.total_amount).label('total_revenue'),
            func.sum(BountyPayment.commission_amount).label('platform_commission'),
            func.sum(BountyPayment.researcher_amount).label('researcher_payouts')
        ).filter(
            BountyPayment.created_at >= start_date,
            BountyPayment.created_at <= end_date,
            BountyPayment.status.in_(['completed', 'approved'])
        ).first()
        
        total_revenue = revenue_query.total_revenue or Decimal('0')
        platform_commission = revenue_query.platform_commission or Decimal('0')
        researcher_payouts = revenue_query.researcher_payouts or Decimal('0')
        
        # Pending payouts
        pending_query = self.db.query(
            func.sum(BountyPayment.researcher_amount)
        ).filter(
            BountyPayment.status == 'pending'
        ).scalar()
        
        pending_payouts = pending_query or Decimal('0')
        
        # Active programs count
        active_programs = self.db.query(func.count(BountyProgram.id)).filter(
            BountyProgram.status == 'active'
        ).scalar() or 0
        
        # Calculate profitability
        # Net Profit = Platform Commission (our revenue) - Operational Costs
        # For now, we'll use platform commission as gross profit
        # In a real system, you'd subtract operational costs
        net_profit = platform_commission
        
        # Gross Margin = (Platform Commission / Total Revenue) * 100
        gross_margin = (platform_commission / total_revenue * 100) if total_revenue > 0 else Decimal('0')
        
        # Cash Balance = Total Revenue - Total Payouts
        cash_balance = total_revenue - researcher_payouts
        
        return {
            'total_revenue': total_revenue,
            'platform_commission': platform_commission,
            'researcher_payouts': researcher_payouts,
            'total_payouts': researcher_payouts,
            'pending_payouts': pending_payouts,
            'net_profit': net_profit,
            'gross_margin': gross_margin,
            'cash_balance': cash_balance,
            'active_programs': active_programs
        }
    
    def _calculate_growth_rate(self, previous: Decimal, current: Decimal) -> float:
        """Calculate percentage growth rate"""
        if previous == 0:
            return 100.0 if current > 0 else 0.0
        return float((current - previous) / previous * 100)
    
    # ==================== REVENUE ANALYTICS ====================
    
    def get_revenue_analytics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Comprehensive revenue analytics including trends, segmentation, and ARR
        """
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=365)
        if not end_date:
            end_date = datetime.utcnow()
        
        # Monthly revenue trend
        monthly_revenue = self._get_monthly_revenue_trend(start_date, end_date)
        
        # Revenue by organization
        revenue_by_customer = self._get_revenue_by_customer(start_date, end_date)
        
        # Calculate ARR (Annual Recurring Revenue)
        arr = self._calculate_arr()
        
        # Revenue per customer
        revenue_per_customer = self._calculate_revenue_per_customer(start_date, end_date)
        
        return {
            'monthly_revenue_trend': monthly_revenue,
            'revenue_by_customer': revenue_by_customer,
            'annual_recurring_revenue': arr,
            'revenue_per_customer': revenue_per_customer,
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            }
        }
    
    def _get_monthly_revenue_trend(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Get monthly revenue trend"""
        results = self.db.query(
            extract('year', BountyPayment.created_at).label('year'),
            extract('month', BountyPayment.created_at).label('month'),
            func.sum(BountyPayment.total_amount).label('revenue'),
            func.sum(BountyPayment.commission_amount).label('commission'),
            func.count(BountyPayment.payment_id).label('payment_count')
        ).filter(
            BountyPayment.created_at >= start_date,
            BountyPayment.created_at <= end_date,
            BountyPayment.status.in_(['completed', 'approved'])
        ).group_by('year', 'month').order_by('year', 'month').all()
        
        return [
            {
                'year': int(r.year),
                'month': int(r.month),
                'revenue': float(r.revenue or 0),
                'commission': float(r.commission or 0),
                'payment_count': r.payment_count
            }
            for r in results
        ]
    
    def _get_revenue_by_customer(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Get revenue breakdown by customer/organization"""
        results = self.db.query(
            Organization.id,
            Organization.company_name,
            func.sum(BountyPayment.total_amount).label('total_revenue'),
            func.sum(BountyPayment.commission_amount).label('platform_revenue'),
            func.count(BountyPayment.payment_id).label('payment_count')
        ).join(
            BountyPayment, BountyPayment.organization_id == Organization.id
        ).filter(
            BountyPayment.created_at >= start_date,
            BountyPayment.created_at <= end_date,
            BountyPayment.status.in_(['completed', 'approved'])
        ).group_by(Organization.id, Organization.company_name).order_by(
            func.sum(BountyPayment.total_amount).desc()
        ).limit(20).all()
        
        return [
            {
                'organization_id': str(r.id),
                'organization_name': r.company_name,
                'total_revenue': float(r.total_revenue or 0),
                'platform_revenue': float(r.platform_revenue or 0),
                'payment_count': r.payment_count
            }
            for r in results
        ]
    
    def _calculate_arr(self) -> float:
        """Calculate Annual Recurring Revenue (last 30 days * 12)"""
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        monthly_revenue = self.db.query(
            func.sum(BountyPayment.commission_amount)
        ).filter(
            BountyPayment.created_at >= thirty_days_ago,
            BountyPayment.status.in_(['completed', 'approved'])
        ).scalar() or Decimal('0')
        
        return float(monthly_revenue * 12)
    
    def _calculate_revenue_per_customer(self, start_date: datetime, end_date: datetime) -> float:
        """Calculate average revenue per customer"""
        total_revenue = self.db.query(
            func.sum(BountyPayment.total_amount)
        ).filter(
            BountyPayment.created_at >= start_date,
            BountyPayment.created_at <= end_date,
            BountyPayment.status.in_(['completed', 'approved'])
        ).scalar() or Decimal('0')
        
        customer_count = self.db.query(
            func.count(func.distinct(BountyPayment.organization_id))
        ).filter(
            BountyPayment.created_at >= start_date,
            BountyPayment.created_at <= end_date
        ).scalar() or 1
        
        return float(total_revenue / customer_count) if customer_count > 0 else 0.0
    
    # ==================== BOUNTY ECONOMICS ====================
    
    def get_bounty_economics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Bounty economics: payouts, severity distribution, top researchers
        """
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=90)
        if not end_date:
            end_date = datetime.utcnow()
        
        # Average bounty by severity
        bounty_by_severity = self._get_average_bounty_by_severity(start_date, end_date)
        
        # Payout distribution
        payout_distribution = self._get_payout_distribution(start_date, end_date)
        
        # Top researchers
        top_researchers = self._get_top_researchers(start_date, end_date)
        
        # Total payouts
        total_payouts = self.db.query(
            func.sum(BountyPayment.researcher_amount)
        ).filter(
            BountyPayment.created_at >= start_date,
            BountyPayment.created_at <= end_date,
            BountyPayment.status.in_(['completed', 'approved'])
        ).scalar() or Decimal('0')
        
        return {
            'total_payouts': float(total_payouts),
            'average_bounty_by_severity': bounty_by_severity,
            'payout_distribution': payout_distribution,
            'top_researchers': top_researchers,
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            }
        }
    
    def _get_average_bounty_by_severity(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Get average bounty amount by vulnerability severity"""
        results = self.db.query(
            VulnerabilityReport.assigned_severity,
            func.avg(BountyPayment.researcher_amount).label('avg_bounty'),
            func.count(BountyPayment.payment_id).label('count'),
            func.sum(BountyPayment.researcher_amount).label('total')
        ).join(
            BountyPayment, BountyPayment.report_id == VulnerabilityReport.id
        ).filter(
            BountyPayment.created_at >= start_date,
            BountyPayment.created_at <= end_date,
            BountyPayment.status.in_(['completed', 'approved']),
            VulnerabilityReport.assigned_severity.isnot(None)
        ).group_by(VulnerabilityReport.assigned_severity).all()
        
        return [
            {
                'severity': r.assigned_severity,
                'average_bounty': float(r.avg_bounty or 0),
                'count': r.count,
                'total': float(r.total or 0)
            }
            for r in results
        ]
    
    def _get_payout_distribution(self, start_date: datetime, end_date: datetime) -> Dict[str, int]:
        """Get distribution of payouts by amount ranges"""
        # Define ranges
        ranges = [
            ('$0-$100', 0, 100),
            ('$100-$500', 100, 500),
            ('$500-$1000', 500, 1000),
            ('$1000-$5000', 1000, 5000),
            ('$5000+', 5000, float('inf'))
        ]
        
        distribution = {}
        for label, min_amount, max_amount in ranges:
            if max_amount == float('inf'):
                count = self.db.query(func.count(BountyPayment.payment_id)).filter(
                    BountyPayment.created_at >= start_date,
                    BountyPayment.created_at <= end_date,
                    BountyPayment.researcher_amount >= min_amount,
                    BountyPayment.status.in_(['completed', 'approved'])
                ).scalar() or 0
            else:
                count = self.db.query(func.count(BountyPayment.payment_id)).filter(
                    BountyPayment.created_at >= start_date,
                    BountyPayment.created_at <= end_date,
                    BountyPayment.researcher_amount >= min_amount,
                    BountyPayment.researcher_amount < max_amount,
                    BountyPayment.status.in_(['completed', 'approved'])
                ).scalar() or 0
            
            distribution[label] = count
        
        return distribution
    
    def _get_top_researchers(self, start_date: datetime, end_date: datetime, limit: int = 10) -> List[Dict]:
        """Get top earning researchers"""
        results = self.db.query(
            Researcher.id,
            Researcher.username,
            func.sum(BountyPayment.researcher_amount).label('total_earned'),
            func.count(BountyPayment.payment_id).label('payment_count'),
            func.avg(BountyPayment.researcher_amount).label('avg_bounty')
        ).join(
            BountyPayment, BountyPayment.researcher_id == Researcher.id
        ).filter(
            BountyPayment.created_at >= start_date,
            BountyPayment.created_at <= end_date,
            BountyPayment.status.in_(['completed', 'approved'])
        ).group_by(Researcher.id, Researcher.username).order_by(
            func.sum(BountyPayment.researcher_amount).desc()
        ).limit(limit).all()
        
        return [
            {
                'researcher_id': str(r.id),
                'researcher_name': r.username or 'Unknown',
                'total_earned': float(r.total_earned or 0),
                'payment_count': r.payment_count,
                'average_bounty': float(r.avg_bounty or 0)
            }
            for r in results
        ]
    
    # ==================== PROGRAM ECONOMICS ====================
    
    def get_program_economics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Program-level economics: ROI, cost per vulnerability, profitability
        """
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=90)
        if not end_date:
            end_date = datetime.utcnow()
        
        results = self.db.query(
            BountyProgram.id,
            BountyProgram.name,
            Organization.company_name,
            func.sum(BountyPayment.total_amount).label('total_revenue'),
            func.sum(BountyPayment.researcher_amount).label('bounty_cost'),
            func.sum(BountyPayment.commission_amount).label('profit'),
            func.count(func.distinct(VulnerabilityReport.id)).label('vulnerability_count'),
            func.count(BountyPayment.payment_id).label('payment_count')
        ).join(
            Organization, BountyProgram.organization_id == Organization.id
        ).join(
            VulnerabilityReport, VulnerabilityReport.program_id == BountyProgram.id
        ).join(
            BountyPayment, BountyPayment.report_id == VulnerabilityReport.id
        ).filter(
            BountyPayment.created_at >= start_date,
            BountyPayment.created_at <= end_date,
            BountyPayment.status.in_(['completed', 'approved'])
        ).group_by(
            BountyProgram.id, BountyProgram.name, Organization.company_name
        ).all()
        
        programs = []
        for r in results:
            total_revenue = float(r.total_revenue or 0)
            bounty_cost = float(r.bounty_cost or 0)
            profit = float(r.profit or 0)
            vuln_count = r.vulnerability_count or 1
            
            # Calculate metrics
            roi = (profit / bounty_cost * 100) if bounty_cost > 0 else 0
            cost_per_vuln = bounty_cost / vuln_count if vuln_count > 0 else 0
            
            programs.append({
                'program_id': str(r.id),
                'program_name': r.name,
                'organization': r.company_name,
                'total_revenue': total_revenue,
                'bounty_cost': bounty_cost,
                'profit': profit,
                'roi_percentage': roi,
                'vulnerability_count': vuln_count,
                'cost_per_vulnerability': cost_per_vuln,
                'payment_count': r.payment_count
            })
        
        return {
            'programs': programs,
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            }
        }
    
    # ==================== CASH FLOW ====================
    
    def get_cash_flow_analysis(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Cash flow analysis: incoming vs outgoing, monthly position
        """
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=180)
        if not end_date:
            end_date = datetime.utcnow()
        
        # Monthly cash flow
        monthly_flow = self.db.query(
            extract('year', BountyPayment.created_at).label('year'),
            extract('month', BountyPayment.created_at).label('month'),
            func.sum(BountyPayment.total_amount).label('incoming'),
            func.sum(BountyPayment.researcher_amount).label('outgoing'),
            func.sum(BountyPayment.commission_amount).label('net_flow')
        ).filter(
            BountyPayment.created_at >= start_date,
            BountyPayment.created_at <= end_date,
            BountyPayment.status.in_(['completed', 'approved'])
        ).group_by('year', 'month').order_by('year', 'month').all()
        
        cash_flow_trend = [
            {
                'year': int(r.year),
                'month': int(r.month),
                'incoming': float(r.incoming or 0),
                'outgoing': float(r.outgoing or 0),
                'net_flow': float(r.net_flow or 0)
            }
            for r in monthly_flow
        ]
        
        # Current cash position
        total_incoming = sum(m['incoming'] for m in cash_flow_trend)
        total_outgoing = sum(m['outgoing'] for m in cash_flow_trend)
        current_position = total_incoming - total_outgoing
        
        # Pending obligations
        pending_payouts = self.db.query(
            func.sum(BountyPayment.researcher_amount)
        ).filter(
            BountyPayment.status == 'pending'
        ).scalar() or Decimal('0')
        
        return {
            'monthly_cash_flow': cash_flow_trend,
            'current_cash_position': current_position,
            'pending_obligations': float(pending_payouts),
            'net_cash_available': current_position - float(pending_payouts),
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            }
        }
