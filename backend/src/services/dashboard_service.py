"""Dashboard Service - FREQ-13."""
from typing import Dict, List, Optional
from uuid import UUID
from datetime import datetime, timedelta
from decimal import Decimal

from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_

from src.domain.models.report import VulnerabilityReport
from src.domain.models.program import BountyProgram, ProgramParticipation
from src.domain.models.researcher import Researcher
from src.domain.models.organization import Organization
from src.domain.models.user import User


class DashboardService:
    """Service for role-specific dashboard data - FREQ-13."""
    
    def __init__(self, db: Session):
        self.db = db
    
    # Researcher Dashboard
    
    def get_researcher_dashboard(
        self,
        researcher_id: UUID
    ) -> Dict:
        """
        Get researcher dashboard - FREQ-13.
        
        Shows:
        - Submissions overview
        - Earnings summary
        - Rankings and reputation
        - Recent activity
        - Program participation
        """
        researcher = self.db.query(Researcher).filter(
            Researcher.id == researcher_id
        ).first()
        
        if not researcher:
            raise ValueError("Researcher not found")
        
        # Submissions overview
        total_submissions = self.db.query(VulnerabilityReport).filter(
            VulnerabilityReport.researcher_id == researcher_id
        ).count()

        
        submissions_by_status = {
            'new': self.db.query(VulnerabilityReport).filter(
                VulnerabilityReport.researcher_id == researcher_id,
                VulnerabilityReport.status == 'new'
            ).count(),
            'triaged': self.db.query(VulnerabilityReport).filter(
                VulnerabilityReport.researcher_id == researcher_id,
                VulnerabilityReport.status == 'triaged'
            ).count(),
            'valid': self.db.query(VulnerabilityReport).filter(
                VulnerabilityReport.researcher_id == researcher_id,
                VulnerabilityReport.status == 'valid'
            ).count(),
            'invalid': self.db.query(VulnerabilityReport).filter(
                VulnerabilityReport.researcher_id == researcher_id,
                VulnerabilityReport.status == 'invalid'
            ).count(),
            'resolved': self.db.query(VulnerabilityReport).filter(
                VulnerabilityReport.researcher_id == researcher_id,
                VulnerabilityReport.status == 'resolved'
            ).count()
        }
        
        # Earnings summary
        total_earnings = researcher.total_earnings or Decimal('0')
        
        pending_earnings = self.db.query(
            func.sum(VulnerabilityReport.bounty_amount)
        ).filter(
            VulnerabilityReport.researcher_id == researcher_id,
            VulnerabilityReport.bounty_status == 'approved'
        ).scalar() or Decimal('0')
        
        paid_earnings = self.db.query(
            func.sum(VulnerabilityReport.bounty_amount)
        ).filter(
            VulnerabilityReport.researcher_id == researcher_id,
            VulnerabilityReport.bounty_status == 'paid'
        ).scalar() or Decimal('0')
        
        # Rankings and reputation
        reputation_score = researcher.reputation_score or Decimal('0')
        rank = researcher.rank or 0
        
        total_researchers = self.db.query(Researcher).count()
        percentile = 0
        if rank and total_researchers > 0:
            percentile = ((total_researchers - rank + 1) / total_researchers) * 100
        
        # Submission pipeline feed (latest 25) with program info
        recent_submissions_query = self.db.query(VulnerabilityReport).filter(
            VulnerabilityReport.researcher_id == researcher_id
        ).order_by(desc(VulnerabilityReport.submitted_at)).limit(25).all()
        
        # Format submissions with program name
        recent_submissions = []
        for report in recent_submissions_query:
            submission_data = {
                'id': str(report.id),
                'report_number': report.report_number,
                'title': report.title,
                'status': report.status,
                'assigned_severity': report.assigned_severity,
                'cvss_score': float(report.cvss_score) if report.cvss_score else None,
                'submitted_at': report.submitted_at.isoformat() if report.submitted_at else None,
                'bounty_amount': float(report.bounty_amount) if report.bounty_amount else None,
                'program_name': report.program.name if report.program else None
            }
            recent_submissions.append(submission_data)
        
        # Program participation
        active_programs = self.db.query(ProgramParticipation).filter(
            ProgramParticipation.researcher_id == researcher_id,
            ProgramParticipation.status == 'active'
        ).count()
        
        # Monthly trend (last 12 months)
        monthly_trend = self._get_researcher_monthly_trend(researcher_id, months=12)
        
        return {
            'overview': {
                'total_submissions': total_submissions,
                'submissions_by_status': submissions_by_status,
                'active_programs': active_programs
            },
            'earnings': {
                'total_earnings': float(total_earnings),
                'pending_earnings': float(pending_earnings),
                'paid_earnings': float(paid_earnings)
            },
            'reputation': {
                'score': float(reputation_score),
                'rank': rank,
                'total_researchers': total_researchers,
                'percentile': round(percentile, 2)
            },
            'recent_submissions': recent_submissions,
            'monthly_trend': monthly_trend
        }

    
    def _get_researcher_monthly_trend(
        self,
        researcher_id: UUID,
        months: int = 12
    ) -> List[Dict]:
        """Get researcher monthly submission and earnings trend."""
        trend = []
        
        for i in range(months - 1, -1, -1):
            month_start = self._get_month_start(months_ago=i)
            month_end = self._get_next_month_start(month_start)
            
            submissions = self.db.query(VulnerabilityReport).filter(
                VulnerabilityReport.researcher_id == researcher_id,
                VulnerabilityReport.submitted_at >= month_start,
                VulnerabilityReport.submitted_at < month_end
            ).count()
            
            earnings = self.db.query(
                func.sum(VulnerabilityReport.bounty_amount)
            ).filter(
                VulnerabilityReport.researcher_id == researcher_id,
                VulnerabilityReport.bounty_status == 'paid',
                VulnerabilityReport.bounty_approved_at >= month_start,
                VulnerabilityReport.bounty_approved_at < month_end
            ).scalar() or Decimal('0')
            
            trend.append({
                'month': month_start.strftime('%Y-%m'),
                'label': month_start.strftime('%b'),
                'submissions': submissions,
                'earnings': float(earnings)
            })
        
        return trend

    def _get_month_start(self, months_ago: int = 0) -> datetime:
        """Get the first day of a month relative to the current UTC month."""
        now = datetime.utcnow()
        month_index = (now.year * 12 + now.month - 1) - months_ago
        year = month_index // 12
        month = month_index % 12 + 1
        return datetime(year, month, 1)

    def _get_next_month_start(self, month_start: datetime) -> datetime:
        """Get the first day of the month after month_start."""
        if month_start.month == 12:
            return datetime(month_start.year + 1, 1, 1)
        return datetime(month_start.year, month_start.month + 1, 1)
    
    # Organization Dashboard
    
    def get_organization_dashboard(
        self,
        organization_id: UUID
    ) -> Dict:
        """
        Get organization dashboard - FREQ-13.
        
        Shows:
        - Program performance
        - Reports overview
        - Trends and analytics
        - Bounty spending
        """
        organization = self.db.query(Organization).filter(
            Organization.id == organization_id
        ).first()
        
        if not organization:
            raise ValueError("Organization not found")
        
        # Get organization's programs
        programs = self.db.query(BountyProgram).filter(
            BountyProgram.organization_id == organization_id,
            BountyProgram.deleted_at.is_(None)
        ).all()
        
        program_ids = [p.id for p in programs]

        
        # Program performance
        total_programs = len(programs)
        active_programs = len([p for p in programs if p.status == 'public'])
        
        # Reports overview
        total_reports = self.db.query(VulnerabilityReport).filter(
            VulnerabilityReport.program_id.in_(program_ids)
        ).count() if program_ids else 0
        
        reports_by_status = {}
        if program_ids:
            reports_by_status = {
                'new': self.db.query(VulnerabilityReport).filter(
                    VulnerabilityReport.program_id.in_(program_ids),
                    VulnerabilityReport.status == 'new'
                ).count(),
                'triaged': self.db.query(VulnerabilityReport).filter(
                    VulnerabilityReport.program_id.in_(program_ids),
                    VulnerabilityReport.status == 'triaged'
                ).count(),
                'valid': self.db.query(VulnerabilityReport).filter(
                    VulnerabilityReport.program_id.in_(program_ids),
                    VulnerabilityReport.status == 'valid'
                ).count(),
                'resolved': self.db.query(VulnerabilityReport).filter(
                    VulnerabilityReport.program_id.in_(program_ids),
                    VulnerabilityReport.status == 'resolved'
                ).count()
            }
        
        # Severity breakdown
        severity_breakdown = {}
        if program_ids:
            severity_breakdown = {
                'critical': self.db.query(VulnerabilityReport).filter(
                    VulnerabilityReport.program_id.in_(program_ids),
                    VulnerabilityReport.assigned_severity == 'critical'
                ).count(),
                'high': self.db.query(VulnerabilityReport).filter(
                    VulnerabilityReport.program_id.in_(program_ids),
                    VulnerabilityReport.assigned_severity == 'high'
                ).count(),
                'medium': self.db.query(VulnerabilityReport).filter(
                    VulnerabilityReport.program_id.in_(program_ids),
                    VulnerabilityReport.assigned_severity == 'medium'
                ).count(),
                'low': self.db.query(VulnerabilityReport).filter(
                    VulnerabilityReport.program_id.in_(program_ids),
                    VulnerabilityReport.assigned_severity == 'low'
                ).count()
            }
        
        # Bounty spending
        total_paid = Decimal('0')
        total_pending = Decimal('0')
        
        if program_ids:
            total_paid = self.db.query(
                func.sum(VulnerabilityReport.bounty_amount)
            ).filter(
                VulnerabilityReport.program_id.in_(program_ids),
                VulnerabilityReport.bounty_status == 'paid'
            ).scalar() or Decimal('0')
            
            total_pending = self.db.query(
                func.sum(VulnerabilityReport.bounty_amount)
            ).filter(
                VulnerabilityReport.program_id.in_(program_ids),
                VulnerabilityReport.bounty_status == 'approved'
            ).scalar() or Decimal('0')
        
        # Platform commission (30%)
        commission_rate = Decimal('0.30')
        total_commission = total_paid * commission_rate
        
        # Recent reports (last 10) with program info
        recent_reports = []
        if program_ids:
            recent_reports_query = self.db.query(VulnerabilityReport).filter(
                VulnerabilityReport.program_id.in_(program_ids)
            ).order_by(desc(VulnerabilityReport.submitted_at)).limit(10).all()
            
            # Format reports with program name
            for report in recent_reports_query:
                report_data = {
                    'id': str(report.id),
                    'report_number': report.report_number,
                    'title': report.title,
                    'status': report.status,
                    'assigned_severity': report.assigned_severity,
                    'submitted_at': report.submitted_at.isoformat() if report.submitted_at else None,
                    'program_name': report.program.name if report.program else None
                }
                recent_reports.append(report_data)
        
        # Monthly trend
        monthly_trend = self._get_organization_monthly_trend(program_ids)
        
        # Top programs by reports
        top_programs = self._get_top_programs_by_reports(program_ids)
        
        return {
            'programs': {
                'total': total_programs,
                'active': active_programs,
                'top_programs': top_programs
            },
            'reports': {
                'total': total_reports,
                'by_status': reports_by_status,
                'by_severity': severity_breakdown
            },
            'bounties': {
                'total_paid': float(total_paid),
                'total_pending': float(total_pending),
                'total_commission': float(total_commission),
                'total_cost': float(total_paid * (1 + commission_rate))
            },
            'recent_reports': recent_reports,
            'monthly_trend': monthly_trend
        }

    
    def _get_organization_monthly_trend(
        self,
        program_ids: List[UUID],
        months: int = 6
    ) -> List[Dict]:
        """Get organization monthly reports and spending trend."""
        if not program_ids:
            return []
        
        trend = []
        
        for i in range(months - 1, -1, -1):
            month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            month_start = month_start - timedelta(days=30 * i)
            month_end = month_start + timedelta(days=30)
            
            reports = self.db.query(VulnerabilityReport).filter(
                VulnerabilityReport.program_id.in_(program_ids),
                VulnerabilityReport.submitted_at >= month_start,
                VulnerabilityReport.submitted_at < month_end
            ).count()
            
            spending = self.db.query(
                func.sum(VulnerabilityReport.bounty_amount)
            ).filter(
                VulnerabilityReport.program_id.in_(program_ids),
                VulnerabilityReport.bounty_status == 'paid',
                VulnerabilityReport.bounty_approved_at >= month_start,
                VulnerabilityReport.bounty_approved_at < month_end
            ).scalar() or Decimal('0')
            
            trend.append({
                'month': month_start.strftime('%Y-%m'),
                'reports': reports,
                'spending': float(spending)
            })
        
        return trend
    
    def _get_top_programs_by_reports(
        self,
        program_ids: List[UUID],
        limit: int = 5
    ) -> List[Dict]:
        """Get top programs by report count."""
        if not program_ids:
            return []
        
        results = self.db.query(
            BountyProgram.id,
            BountyProgram.name,
            func.count(VulnerabilityReport.id).label('report_count')
        ).outerjoin(
            VulnerabilityReport,
            VulnerabilityReport.program_id == BountyProgram.id
        ).filter(
            BountyProgram.id.in_(program_ids)
        ).group_by(
            BountyProgram.id,
            BountyProgram.name
        ).order_by(
            desc('report_count')
        ).limit(limit).all()
        
        return [
            {
                'program_id': str(r.id),
                'program_name': r.name,
                'report_count': r.report_count
            }
            for r in results
        ]
    
    # Staff/Triage Dashboard
    
    def get_staff_dashboard(self) -> Dict:
        """
        Get staff/triage specialist dashboard - FREQ-13.
        
        Shows:
        - Triage queue
        - Workload statistics
        - Priority reports
        - Recent activity
        """
        # Triage queue counts
        new_reports = self.db.query(VulnerabilityReport).filter(
            VulnerabilityReport.status == 'new'
        ).count()
        
        triaged_reports = self.db.query(VulnerabilityReport).filter(
            VulnerabilityReport.status == 'triaged'
        ).count()
        
        # Priority reports (critical and high severity suggestions)
        critical_reports = self.db.query(VulnerabilityReport).filter(
            VulnerabilityReport.status.in_(['new', 'triaged']),
            VulnerabilityReport.suggested_severity == 'critical'
        ).count()
        
        high_priority_reports = self.db.query(VulnerabilityReport).filter(
            VulnerabilityReport.status.in_(['new', 'triaged']),
            VulnerabilityReport.suggested_severity == 'high'
        ).count()

        
        # Unacknowledged reports (over 24 hours)
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        unacknowledged = self.db.query(VulnerabilityReport).filter(
            VulnerabilityReport.acknowledged_at.is_(None),
            VulnerabilityReport.submitted_at < cutoff_time
        ).count()
        
        # Reports by status
        status_breakdown = {
            'new': new_reports,
            'triaged': triaged_reports,
            'valid': self.db.query(VulnerabilityReport).filter(
                VulnerabilityReport.status == 'valid'
            ).count(),
            'invalid': self.db.query(VulnerabilityReport).filter(
                VulnerabilityReport.status == 'invalid'
            ).count(),
            'resolved': self.db.query(VulnerabilityReport).filter(
                VulnerabilityReport.status == 'resolved'
            ).count()
        }
        
        # Recent triage activity (last 10 triaged reports)
        recent_activity = self.db.query(VulnerabilityReport).filter(
            VulnerabilityReport.triaged_at.isnot(None)
        ).order_by(desc(VulnerabilityReport.triaged_at)).limit(10).all()
        
        # Oldest pending reports (need attention)
        oldest_pending = self.db.query(VulnerabilityReport).filter(
            VulnerabilityReport.status.in_(['new', 'triaged'])
        ).order_by(VulnerabilityReport.submitted_at.asc()).limit(10).all()
        
        # Daily triage stats (last 7 days)
        daily_stats = self._get_daily_triage_stats()
        
        return {
            'queue': {
                'new_reports': new_reports,
                'triaged_reports': triaged_reports,
                'total_pending': new_reports + triaged_reports
            },
            'priority': {
                'critical': critical_reports,
                'high': high_priority_reports,
                'unacknowledged': unacknowledged
            },
            'status_breakdown': status_breakdown,
            'recent_activity': recent_activity,
            'oldest_pending': oldest_pending,
            'daily_stats': daily_stats
        }
    
    def _get_daily_triage_stats(self, days: int = 7) -> List[Dict]:
        """Get daily triage statistics."""
        stats = []
        
        for i in range(days - 1, -1, -1):
            day_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            day_start = day_start - timedelta(days=i)
            day_end = day_start + timedelta(days=1)
            
            triaged = self.db.query(VulnerabilityReport).filter(
                VulnerabilityReport.triaged_at >= day_start,
                VulnerabilityReport.triaged_at < day_end
            ).count()
            
            submitted = self.db.query(VulnerabilityReport).filter(
                VulnerabilityReport.submitted_at >= day_start,
                VulnerabilityReport.submitted_at < day_end
            ).count()
            
            stats.append({
                'date': day_start.strftime('%Y-%m-%d'),
                'submitted': submitted,
                'triaged': triaged
            })
        
        return stats
    
    # Admin Dashboard
    
    def get_admin_dashboard(self) -> Dict:
        """
        Get admin platform overview dashboard - FREQ-13.
        
        Shows:
        - Platform-wide statistics
        - User growth
        - Program activity
        - Financial overview
        - System health
        """
        # User statistics
        total_users = self.db.query(User).count()
        total_researchers = self.db.query(Researcher).count()
        total_organizations = self.db.query(Organization).count()
        
        # Active users (logged in last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        active_users = self.db.query(User).filter(
            User.last_login_at >= thirty_days_ago
        ).count()
        
        # Program statistics
        total_programs = self.db.query(BountyProgram).filter(
            BountyProgram.deleted_at.is_(None)
        ).count()
        
        active_programs = self.db.query(BountyProgram).filter(
            BountyProgram.status == 'public',
            BountyProgram.deleted_at.is_(None)
        ).count()
        
        # Report statistics
        total_reports = self.db.query(VulnerabilityReport).count()
        
        reports_by_status = {
            'new': self.db.query(VulnerabilityReport).filter(
                VulnerabilityReport.status == 'new'
            ).count(),
            'triaged': self.db.query(VulnerabilityReport).filter(
                VulnerabilityReport.status == 'triaged'
            ).count(),
            'valid': self.db.query(VulnerabilityReport).filter(
                VulnerabilityReport.status == 'valid'
            ).count(),
            'resolved': self.db.query(VulnerabilityReport).filter(
                VulnerabilityReport.status == 'resolved'
            ).count()
        }

        
        # Financial overview
        total_bounties_paid = self.db.query(
            func.sum(VulnerabilityReport.bounty_amount)
        ).filter(
            VulnerabilityReport.bounty_status == 'paid'
        ).scalar() or Decimal('0')
        
        total_bounties_pending = self.db.query(
            func.sum(VulnerabilityReport.bounty_amount)
        ).filter(
            VulnerabilityReport.bounty_status == 'approved'
        ).scalar() or Decimal('0')
        
        # Platform commission (30%)
        commission_rate = Decimal('0.30')
        platform_revenue = total_bounties_paid * commission_rate
        
        # Growth metrics (last 30 days)
        new_users_30d = self.db.query(User).filter(
            User.created_at >= thirty_days_ago
        ).count()
        
        new_reports_30d = self.db.query(VulnerabilityReport).filter(
            VulnerabilityReport.submitted_at >= thirty_days_ago
        ).count()
        
        new_programs_30d = self.db.query(BountyProgram).filter(
            BountyProgram.created_at >= thirty_days_ago
        ).count()
        
        # Top researchers
        top_researchers = self.db.query(Researcher).order_by(
            desc(Researcher.reputation_score)
        ).limit(5).all()
        
        # Top organizations by programs
        top_organizations = self.db.query(
            Organization.id,
            Organization.company_name,
            func.count(BountyProgram.id).label('program_count')
        ).outerjoin(
            BountyProgram,
            BountyProgram.organization_id == Organization.id
        ).group_by(
            Organization.id,
            Organization.company_name
        ).order_by(
            desc('program_count')
        ).limit(5).all()
        
        # Platform health
        pending_triage = self.db.query(VulnerabilityReport).filter(
            VulnerabilityReport.status == 'new'
        ).count()
        
        overdue_payouts = self.db.query(VulnerabilityReport).filter(
            VulnerabilityReport.bounty_status == 'approved',
            VulnerabilityReport.bounty_approved_at < datetime.utcnow() - timedelta(days=30)
        ).count()
        
        # Monthly growth trend
        monthly_growth = self._get_platform_monthly_growth()
        
        return {
            'users': {
                'total': total_users,
                'researchers': total_researchers,
                'organizations': total_organizations,
                'active_30d': active_users,
                'new_30d': new_users_30d
            },
            'programs': {
                'total': total_programs,
                'active': active_programs,
                'new_30d': new_programs_30d
            },
            'reports': {
                'total': total_reports,
                'by_status': reports_by_status,
                'new_30d': new_reports_30d
            },
            'financials': {
                'total_paid': float(total_bounties_paid),
                'total_pending': float(total_bounties_pending),
                'platform_revenue': float(platform_revenue),
                'commission_rate': float(commission_rate)
            },
            'top_performers': {
                'researchers': [
                    {
                        'id': str(r.id),
                        'username': r.username,
                        'reputation': float(r.reputation_score or 0),
                        'rank': r.rank
                    }
                    for r in top_researchers
                ],
                'organizations': [
                    {
                        'id': str(o.id),
                        'name': o.company_name,
                        'program_count': o.program_count
                    }
                    for o in top_organizations
                ]
            },
            'health': {
                'pending_triage': pending_triage,
                'overdue_payouts': overdue_payouts
            },
            'monthly_growth': monthly_growth
        }
    
    def _get_platform_monthly_growth(self, months: int = 6) -> List[Dict]:
        """Get platform monthly growth metrics."""
        growth = []
        
        for i in range(months - 1, -1, -1):
            month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            month_start = month_start - timedelta(days=30 * i)
            month_end = month_start + timedelta(days=30)
            
            new_users = self.db.query(User).filter(
                User.created_at >= month_start,
                User.created_at < month_end
            ).count()
            
            new_reports = self.db.query(VulnerabilityReport).filter(
                VulnerabilityReport.submitted_at >= month_start,
                VulnerabilityReport.submitted_at < month_end
            ).count()
            
            new_programs = self.db.query(BountyProgram).filter(
                BountyProgram.created_at >= month_start,
                BountyProgram.created_at < month_end
            ).count()
            
            revenue = self.db.query(
                func.sum(VulnerabilityReport.bounty_amount)
            ).filter(
                VulnerabilityReport.bounty_status == 'paid',
                VulnerabilityReport.bounty_approved_at >= month_start,
                VulnerabilityReport.bounty_approved_at < month_end
            ).scalar() or Decimal('0')
            
            # Platform commission (30%)
            platform_revenue = revenue * Decimal('0.30')
            
            growth.append({
                'month': month_start.strftime('%Y-%m'),
                'new_users': new_users,
                'new_reports': new_reports,
                'new_programs': new_programs,
                'revenue': float(platform_revenue)
            })
        
        return growth
