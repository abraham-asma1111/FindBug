"""Analytics Service - FREQ-15."""
from typing import Dict, List, Optional
from uuid import UUID
from datetime import datetime, timedelta
from decimal import Decimal

from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, extract

from src.domain.models.report import VulnerabilityReport
from src.domain.models.program import BountyProgram, ProgramParticipation
from src.domain.models.researcher import Researcher
from src.domain.models.organization import Organization


class AnalyticsService:
    """Service for analytics reports - FREQ-15."""
    
    def __init__(self, db: Session):
        self.db = db
    
    # Vulnerability Trends Analytics
    
    def get_vulnerability_trends(
        self,
        program_id: Optional[UUID] = None,
        organization_id: Optional[UUID] = None,
        time_period: str = '6months'
    ) -> Dict:
        """
        Get vulnerability trends analytics - FREQ-15.
        
        Shows:
        - Vulnerability submissions over time
        - Severity distribution trends
        - Status progression trends
        - Top vulnerability types
        - Average time to triage/resolve
        """
        # Determine time range
        time_ranges = {
            '7days': 7,
            '30days': 30,
            '3months': 90,
            '6months': 180,
            '1year': 365
        }
        days = time_ranges.get(time_period, 180)
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Build base query
        query = self.db.query(VulnerabilityReport).filter(
            VulnerabilityReport.submitted_at >= start_date
        )

        
        # Filter by program or organization
        if program_id:
            query = query.filter(VulnerabilityReport.program_id == program_id)
        elif organization_id:
            program_ids = [p.id for p in self.db.query(BountyProgram).filter(
                BountyProgram.organization_id == organization_id
            ).all()]
            if program_ids:
                query = query.filter(VulnerabilityReport.program_id.in_(program_ids))
        
        # Total vulnerabilities in period
        total_vulnerabilities = query.count()
        
        # Severity distribution
        severity_distribution = {
            'critical': query.filter(VulnerabilityReport.assigned_severity == 'critical').count(),
            'high': query.filter(VulnerabilityReport.assigned_severity == 'high').count(),
            'medium': query.filter(VulnerabilityReport.assigned_severity == 'medium').count(),
            'low': query.filter(VulnerabilityReport.assigned_severity == 'low').count(),
            'unassigned': query.filter(VulnerabilityReport.assigned_severity.is_(None)).count()
        }
        
        # Status distribution
        status_distribution = {
            'new': query.filter(VulnerabilityReport.status == 'new').count(),
            'triaged': query.filter(VulnerabilityReport.status == 'triaged').count(),
            'valid': query.filter(VulnerabilityReport.status == 'valid').count(),
            'invalid': query.filter(VulnerabilityReport.status == 'invalid').count(),
            'duplicate': query.filter(VulnerabilityReport.status == 'duplicate').count(),
            'resolved': query.filter(VulnerabilityReport.status == 'resolved').count()
        }
        
        # Top vulnerability types
        top_vuln_types = self.db.query(
            VulnerabilityReport.vulnerability_type,
            func.count(VulnerabilityReport.id).label('count')
        ).filter(
            VulnerabilityReport.submitted_at >= start_date,
            VulnerabilityReport.vulnerability_type.isnot(None)
        )
        
        if program_id:
            top_vuln_types = top_vuln_types.filter(VulnerabilityReport.program_id == program_id)
        
        top_vuln_types = top_vuln_types.group_by(
            VulnerabilityReport.vulnerability_type
        ).order_by(desc('count')).limit(10).all()
        
        # Time-series data (submissions over time)
        time_series = self._get_vulnerability_time_series(start_date, program_id, organization_id)
        
        # Average times
        avg_time_to_triage = self._calculate_avg_time_to_triage(query)
        avg_time_to_resolve = self._calculate_avg_time_to_resolve(query)
        
        # Duplicate rate
        duplicate_count = query.filter(VulnerabilityReport.is_duplicate == True).count()
        duplicate_rate = (duplicate_count / total_vulnerabilities * 100) if total_vulnerabilities > 0 else 0
        
        return {
            'period': time_period,
            'start_date': start_date.isoformat(),
            'end_date': datetime.utcnow().isoformat(),
            'total_vulnerabilities': total_vulnerabilities,
            'severity_distribution': severity_distribution,
            'status_distribution': status_distribution,
            'top_vulnerability_types': [
                {'type': vt.vulnerability_type, 'count': vt.count}
                for vt in top_vuln_types
            ],
            'time_series': time_series,
            'metrics': {
                'avg_time_to_triage_hours': avg_time_to_triage,
                'avg_time_to_resolve_days': avg_time_to_resolve,
                'duplicate_rate': round(duplicate_rate, 2)
            }
        }

    
    def _get_vulnerability_time_series(
        self,
        start_date: datetime,
        program_id: Optional[UUID] = None,
        organization_id: Optional[UUID] = None
    ) -> List[Dict]:
        """Get vulnerability submissions over time."""
        # Group by week for better visualization
        query = self.db.query(
            func.date_trunc('week', VulnerabilityReport.submitted_at).label('week'),
            func.count(VulnerabilityReport.id).label('count')
        ).filter(
            VulnerabilityReport.submitted_at >= start_date
        )
        
        if program_id:
            query = query.filter(VulnerabilityReport.program_id == program_id)
        elif organization_id:
            program_ids = [p.id for p in self.db.query(BountyProgram).filter(
                BountyProgram.organization_id == organization_id
            ).all()]
            if program_ids:
                query = query.filter(VulnerabilityReport.program_id.in_(program_ids))
        
        results = query.group_by('week').order_by('week').all()
        
        return [
            {
                'period': r.week.strftime('%Y-%m-%d') if r.week else None,
                'count': r.count
            }
            for r in results
        ]
    
    def _calculate_avg_time_to_triage(self, query) -> float:
        """Calculate average time from submission to triage (in hours)."""
        triaged_reports = query.filter(
            VulnerabilityReport.triaged_at.isnot(None)
        ).all()
        
        if not triaged_reports:
            return 0.0
        
        total_hours = 0
        for report in triaged_reports:
            time_diff = report.triaged_at - report.submitted_at
            total_hours += time_diff.total_seconds() / 3600
        
        return round(total_hours / len(triaged_reports), 2)
    
    def _calculate_avg_time_to_resolve(self, query) -> float:
        """Calculate average time from submission to resolution (in days)."""
        resolved_reports = query.filter(
            VulnerabilityReport.resolved_at.isnot(None)
        ).all()
        
        if not resolved_reports:
            return 0.0
        
        total_days = 0
        for report in resolved_reports:
            time_diff = report.resolved_at - report.submitted_at
            total_days += time_diff.total_seconds() / 86400
        
        return round(total_days / len(resolved_reports), 2)

    
    # Program Effectiveness Analytics
    
    def get_program_effectiveness(
        self,
        program_id: Optional[UUID] = None,
        organization_id: Optional[UUID] = None
    ) -> Dict:
        """
        Get program effectiveness analytics - FREQ-15.
        
        Shows:
        - Program participation metrics
        - Report quality metrics
        - Response time metrics
        - Bounty efficiency
        - Researcher engagement
        """
        # Get programs
        if program_id:
            programs = [self.db.query(BountyProgram).filter(
                BountyProgram.id == program_id
            ).first()]
        elif organization_id:
            programs = self.db.query(BountyProgram).filter(
                BountyProgram.organization_id == organization_id,
                BountyProgram.deleted_at.is_(None)
            ).all()
        else:
            programs = self.db.query(BountyProgram).filter(
                BountyProgram.deleted_at.is_(None)
            ).all()
        
        program_ids = [p.id for p in programs if p]
        
        if not program_ids:
            return {'error': 'No programs found'}
        
        # Participation metrics
        total_participants = self.db.query(ProgramParticipation).filter(
            ProgramParticipation.program_id.in_(program_ids),
            ProgramParticipation.status == 'active'
        ).count()
        
        # Report quality metrics
        total_reports = self.db.query(VulnerabilityReport).filter(
            VulnerabilityReport.program_id.in_(program_ids)
        ).count()
        
        valid_reports = self.db.query(VulnerabilityReport).filter(
            VulnerabilityReport.program_id.in_(program_ids),
            VulnerabilityReport.status.in_(['valid', 'resolved'])
        ).count()
        
        invalid_reports = self.db.query(VulnerabilityReport).filter(
            VulnerabilityReport.program_id.in_(program_ids),
            VulnerabilityReport.status == 'invalid'
        ).count()
        
        duplicate_reports = self.db.query(VulnerabilityReport).filter(
            VulnerabilityReport.program_id.in_(program_ids),
            VulnerabilityReport.is_duplicate == True
        ).count()
        
        # Quality rate
        quality_rate = (valid_reports / total_reports * 100) if total_reports > 0 else 0
        
        # Response time metrics
        avg_acknowledgment_time = self._calculate_avg_acknowledgment_time(program_ids)
        avg_resolution_time = self._calculate_avg_resolution_time(program_ids)
        
        # Bounty efficiency
        total_bounties_paid = self.db.query(
            func.sum(VulnerabilityReport.bounty_amount)
        ).filter(
            VulnerabilityReport.program_id.in_(program_ids),
            VulnerabilityReport.bounty_status == 'paid'
        ).scalar() or Decimal('0')
        
        avg_bounty_per_report = (total_bounties_paid / valid_reports) if valid_reports > 0 else Decimal('0')
        
        # Researcher engagement
        active_researchers = self.db.query(
            func.count(func.distinct(VulnerabilityReport.researcher_id))
        ).filter(
            VulnerabilityReport.program_id.in_(program_ids),
            VulnerabilityReport.submitted_at >= datetime.utcnow() - timedelta(days=30)
        ).scalar() or 0
        
        # Program-specific breakdown
        program_breakdown = []
        for program in programs:
            if not program:
                continue
            
            program_reports = self.db.query(VulnerabilityReport).filter(
                VulnerabilityReport.program_id == program.id
            ).count()
            
            program_valid = self.db.query(VulnerabilityReport).filter(
                VulnerabilityReport.program_id == program.id,
                VulnerabilityReport.status.in_(['valid', 'resolved'])
            ).count()
            
            program_breakdown.append({
                'program_id': str(program.id),
                'program_name': program.name,
                'total_reports': program_reports,
                'valid_reports': program_valid,
                'quality_rate': round((program_valid / program_reports * 100) if program_reports > 0 else 0, 2)
            })
        
        return {
            'participation': {
                'total_participants': total_participants,
                'active_researchers_30d': active_researchers
            },
            'report_quality': {
                'total_reports': total_reports,
                'valid_reports': valid_reports,
                'invalid_reports': invalid_reports,
                'duplicate_reports': duplicate_reports,
                'quality_rate': round(quality_rate, 2)
            },
            'response_times': {
                'avg_acknowledgment_hours': avg_acknowledgment_time,
                'avg_resolution_days': avg_resolution_time
            },
            'bounty_efficiency': {
                'total_paid': float(total_bounties_paid),
                'avg_per_valid_report': float(avg_bounty_per_report)
            },
            'program_breakdown': program_breakdown
        }

    
    # Program Effectiveness Analytics
    
    def get_program_effectiveness(
        self,
        program_id: Optional[UUID] = None,
        organization_id: Optional[UUID] = None,
        time_period: str = '6months'
    ) -> Dict:
        """
        Get program effectiveness analytics - FREQ-15.
        
        Shows:
        - Report volume and quality
        - Response times
        - Resolution rates
        - ROI metrics
        - Researcher engagement
        """
        # Determine time range
        time_ranges = {
            '7days': 7,
            '30days': 30,
            '3months': 90,
            '6months': 180,
            '1year': 365
        }
        days = time_ranges.get(time_period, 180)
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Get programs
        if program_id:
            programs = [self.db.query(BountyProgram).filter(
                BountyProgram.id == program_id
            ).first()]
        elif organization_id:
            programs = self.db.query(BountyProgram).filter(
                BountyProgram.organization_id == organization_id,
                BountyProgram.deleted_at.is_(None)
            ).all()
        else:
            programs = self.db.query(BountyProgram).filter(
                BountyProgram.deleted_at.is_(None)
            ).all()
        
        program_ids = [p.id for p in programs if p]
        
        if not program_ids:
            return {
                'period': time_period,
                'programs': [],
                'summary': {}
            }
        
        # Report metrics
        total_reports = self.db.query(VulnerabilityReport).filter(
            VulnerabilityReport.program_id.in_(program_ids),
            VulnerabilityReport.submitted_at >= start_date
        ).count()
        
        valid_reports = self.db.query(VulnerabilityReport).filter(
            VulnerabilityReport.program_id.in_(program_ids),
            VulnerabilityReport.submitted_at >= start_date,
            VulnerabilityReport.status == 'valid'
        ).count()
        
        resolved_reports = self.db.query(VulnerabilityReport).filter(
            VulnerabilityReport.program_id.in_(program_ids),
            VulnerabilityReport.submitted_at >= start_date,
            VulnerabilityReport.status == 'resolved'
        ).count()
        
        # Quality metrics
        quality_rate = (valid_reports / total_reports * 100) if total_reports > 0 else 0
        resolution_rate = (resolved_reports / valid_reports * 100) if valid_reports > 0 else 0
        
        # Response time metrics
        avg_response_time = self._calculate_avg_response_time(program_ids, start_date)
        avg_resolution_time = self._calculate_avg_resolution_time(program_ids, start_date)
        
        # Financial metrics
        total_paid = self.db.query(
            func.sum(VulnerabilityReport.bounty_amount)
        ).filter(
            VulnerabilityReport.program_id.in_(program_ids),
            VulnerabilityReport.bounty_status == 'paid',
            VulnerabilityReport.bounty_approved_at >= start_date
        ).scalar() or Decimal('0')
        
        # Researcher engagement
        unique_researchers = self.db.query(
            func.count(func.distinct(VulnerabilityReport.researcher_id))
        ).filter(
            VulnerabilityReport.program_id.in_(program_ids),
            VulnerabilityReport.submitted_at >= start_date
        ).scalar() or 0
        
        # Program-by-program breakdown
        program_details = []
        for program in programs:
            if not program:
                continue
                
            prog_reports = self.db.query(VulnerabilityReport).filter(
                VulnerabilityReport.program_id == program.id,
                VulnerabilityReport.submitted_at >= start_date
            ).count()
            
            prog_valid = self.db.query(VulnerabilityReport).filter(
                VulnerabilityReport.program_id == program.id,
                VulnerabilityReport.submitted_at >= start_date,
                VulnerabilityReport.status == 'valid'
            ).count()
            
            program_details.append({
                'program_id': str(program.id),
                'program_name': program.name,
                'total_reports': prog_reports,
                'valid_reports': prog_valid,
                'quality_rate': round((prog_valid / prog_reports * 100) if prog_reports > 0 else 0, 2)
            })
        
        return {
            'period': time_period,
            'start_date': start_date.isoformat(),
            'end_date': datetime.utcnow().isoformat(),
            'summary': {
                'total_programs': len(programs),
                'total_reports': total_reports,
                'valid_reports': valid_reports,
                'resolved_reports': resolved_reports,
                'quality_rate': round(quality_rate, 2),
                'resolution_rate': round(resolution_rate, 2),
                'unique_researchers': unique_researchers,
                'total_paid': float(total_paid),
                'avg_response_time_hours': avg_response_time,
                'avg_resolution_time_days': avg_resolution_time
            },
            'programs': program_details
        }
    
    def _calculate_avg_response_time(
        self,
        program_ids: List[UUID],
        start_date: datetime
    ) -> float:
        """Calculate average time from submission to first response (acknowledgment)."""
        reports = self.db.query(VulnerabilityReport).filter(
            VulnerabilityReport.program_id.in_(program_ids),
            VulnerabilityReport.submitted_at >= start_date,
            VulnerabilityReport.acknowledged_at.isnot(None)
        ).all()
        
        if not reports:
            return 0.0
        
        total_hours = 0
        for report in reports:
            time_diff = report.acknowledged_at - report.submitted_at
            total_hours += time_diff.total_seconds() / 3600
        
        return round(total_hours / len(reports), 2)
    
    def _calculate_avg_resolution_time(
        self,
        program_ids: List[UUID],
        start_date: datetime
    ) -> float:
        """Calculate average time from submission to resolution."""
        reports = self.db.query(VulnerabilityReport).filter(
            VulnerabilityReport.program_id.in_(program_ids),
            VulnerabilityReport.submitted_at >= start_date,
            VulnerabilityReport.resolved_at.isnot(None)
        ).all()
        
        if not reports:
            return 0.0
        
        total_days = 0
        for report in reports:
            time_diff = report.resolved_at - report.submitted_at
            total_days += time_diff.total_seconds() / 86400
        
        return round(total_days / len(reports), 2)
    
    # Researcher Performance Analytics
    
    def get_researcher_performance(
        self,
        researcher_id: Optional[UUID] = None,
        time_period: str = '6months'
    ) -> Dict:
        """
        Get researcher performance analytics - FREQ-15.
        
        Shows:
        - Submission trends
        - Success rates
        - Earnings trends
        - Specialization analysis
        - Comparison to peers
        """
        # Determine time range
        time_ranges = {
            '7days': 7,
            '30days': 30,
            '3months': 90,
            '6months': 180,
            '1year': 365
        }
        days = time_ranges.get(time_period, 180)
        start_date = datetime.utcnow() - timedelta(days=days)
        
        if researcher_id:
            # Single researcher analysis
            researcher = self.db.query(Researcher).filter(
                Researcher.id == researcher_id
            ).first()
            
            if not researcher:
                raise ValueError("Researcher not found")
            
            return self._get_single_researcher_performance(researcher, start_date, time_period)
        else:
            # Top researchers comparison
            return self._get_top_researchers_performance(start_date, time_period)
    
    def _get_single_researcher_performance(
        self,
        researcher: Researcher,
        start_date: datetime,
        time_period: str
    ) -> Dict:
        """Get detailed performance for a single researcher."""
        # Report metrics
        total_reports = self.db.query(VulnerabilityReport).filter(
            VulnerabilityReport.researcher_id == researcher.id,
            VulnerabilityReport.submitted_at >= start_date
        ).count()
        
        valid_reports = self.db.query(VulnerabilityReport).filter(
            VulnerabilityReport.researcher_id == researcher.id,
            VulnerabilityReport.submitted_at >= start_date,
            VulnerabilityReport.status == 'valid'
        ).count()
        
        invalid_reports = self.db.query(VulnerabilityReport).filter(
            VulnerabilityReport.researcher_id == researcher.id,
            VulnerabilityReport.submitted_at >= start_date,
            VulnerabilityReport.status == 'invalid'
        ).count()
        
        # Success rate
        success_rate = (valid_reports / total_reports * 100) if total_reports > 0 else 0
        
        # Earnings in period
        earnings = self.db.query(
            func.sum(VulnerabilityReport.bounty_amount)
        ).filter(
            VulnerabilityReport.researcher_id == researcher.id,
            VulnerabilityReport.bounty_status == 'paid',
            VulnerabilityReport.bounty_approved_at >= start_date
        ).scalar() or Decimal('0')
        
        # Severity distribution
        severity_dist = {
            'critical': self.db.query(VulnerabilityReport).filter(
                VulnerabilityReport.researcher_id == researcher.id,
                VulnerabilityReport.submitted_at >= start_date,
                VulnerabilityReport.assigned_severity == 'critical'
            ).count(),
            'high': self.db.query(VulnerabilityReport).filter(
                VulnerabilityReport.researcher_id == researcher.id,
                VulnerabilityReport.submitted_at >= start_date,
                VulnerabilityReport.assigned_severity == 'high'
            ).count(),
            'medium': self.db.query(VulnerabilityReport).filter(
                VulnerabilityReport.researcher_id == researcher.id,
                VulnerabilityReport.submitted_at >= start_date,
                VulnerabilityReport.assigned_severity == 'medium'
            ).count(),
            'low': self.db.query(VulnerabilityReport).filter(
                VulnerabilityReport.researcher_id == researcher.id,
                VulnerabilityReport.submitted_at >= start_date,
                VulnerabilityReport.assigned_severity == 'low'
            ).count()
        }
        
        # Vulnerability types specialization
        vuln_types = self.db.query(
            VulnerabilityReport.vulnerability_type,
            func.count(VulnerabilityReport.id).label('count')
        ).filter(
            VulnerabilityReport.researcher_id == researcher.id,
            VulnerabilityReport.submitted_at >= start_date,
            VulnerabilityReport.vulnerability_type.isnot(None)
        ).group_by(VulnerabilityReport.vulnerability_type).order_by(desc('count')).limit(5).all()
        
        # Monthly trend
        monthly_trend = self._get_researcher_monthly_performance(researcher.id, start_date)
        
        return {
            'researcher_id': str(researcher.id),
            'period': time_period,
            'start_date': start_date.isoformat(),
            'end_date': datetime.utcnow().isoformat(),
            'metrics': {
                'total_reports': total_reports,
                'valid_reports': valid_reports,
                'invalid_reports': invalid_reports,
                'success_rate': round(success_rate, 2),
                'earnings': float(earnings),
                'reputation_score': float(researcher.reputation_score or 0),
                'rank': researcher.rank
            },
            'severity_distribution': severity_dist,
            'top_vulnerability_types': [
                {'type': vt.vulnerability_type, 'count': vt.count}
                for vt in vuln_types
            ],
            'monthly_trend': monthly_trend
        }
    
    def _get_top_researchers_performance(
        self,
        start_date: datetime,
        time_period: str
    ) -> Dict:
        """Get performance comparison of top researchers."""
        # Get top 10 researchers by reputation
        top_researchers = self.db.query(Researcher).order_by(
            desc(Researcher.reputation_score)
        ).limit(10).all()
        
        researchers_data = []
        for researcher in top_researchers:
            total_reports = self.db.query(VulnerabilityReport).filter(
                VulnerabilityReport.researcher_id == researcher.id,
                VulnerabilityReport.submitted_at >= start_date
            ).count()
            
            valid_reports = self.db.query(VulnerabilityReport).filter(
                VulnerabilityReport.researcher_id == researcher.id,
                VulnerabilityReport.submitted_at >= start_date,
                VulnerabilityReport.status == 'valid'
            ).count()
            
            earnings = self.db.query(
                func.sum(VulnerabilityReport.bounty_amount)
            ).filter(
                VulnerabilityReport.researcher_id == researcher.id,
                VulnerabilityReport.bounty_status == 'paid',
                VulnerabilityReport.bounty_approved_at >= start_date
            ).scalar() or Decimal('0')
            
            researchers_data.append({
                'researcher_id': str(researcher.id),
                'username': researcher.username or 'Anonymous',
                'rank': researcher.rank,
                'reputation_score': float(researcher.reputation_score or 0),
                'total_reports': total_reports,
                'valid_reports': valid_reports,
                'success_rate': round((valid_reports / total_reports * 100) if total_reports > 0 else 0, 2),
                'earnings': float(earnings)
            })
        
        return {
            'period': time_period,
            'start_date': start_date.isoformat(),
            'end_date': datetime.utcnow().isoformat(),
            'top_researchers': researchers_data
        }
    
    def _get_researcher_monthly_performance(
        self,
        researcher_id: UUID,
        start_date: datetime
    ) -> List[Dict]:
        """Get researcher monthly performance trend."""
        months_data = []
        current_date = start_date
        
        while current_date <= datetime.utcnow():
            month_end = current_date + timedelta(days=30)
            
            reports = self.db.query(VulnerabilityReport).filter(
                VulnerabilityReport.researcher_id == researcher_id,
                VulnerabilityReport.submitted_at >= current_date,
                VulnerabilityReport.submitted_at < month_end
            ).count()
            
            valid = self.db.query(VulnerabilityReport).filter(
                VulnerabilityReport.researcher_id == researcher_id,
                VulnerabilityReport.submitted_at >= current_date,
                VulnerabilityReport.submitted_at < month_end,
                VulnerabilityReport.status == 'valid'
            ).count()
            
            earnings = self.db.query(
                func.sum(VulnerabilityReport.bounty_amount)
            ).filter(
                VulnerabilityReport.researcher_id == researcher_id,
                VulnerabilityReport.bounty_status == 'paid',
                VulnerabilityReport.bounty_approved_at >= current_date,
                VulnerabilityReport.bounty_approved_at < month_end
            ).scalar() or Decimal('0')
            
            months_data.append({
                'month': current_date.strftime('%Y-%m'),
                'total_reports': reports,
                'valid_reports': valid,
                'earnings': float(earnings)
            })
            
            current_date = month_end
        
        return months_data
