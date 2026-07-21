"""
PTaaS Analytics Service - Step 11
Provides analytics and reporting metrics for PTaaS engagements
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import Dict, List, Optional
from uuid import UUID
from datetime import datetime, timedelta
from src.domain.models.ptaas import PTaaSEngagement, PTaaSFinding


class PTaaSAnalyticsService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_vulnerability_trends(
        self,
        engagement_id: UUID,
        days: int = 30
    ) -> List[Dict]:
        """Get vulnerability discovery trends over time"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Query findings grouped by date and severity
        findings = self.db.query(
            func.date(PTaaSFinding.created_at).label('date'),
            PTaaSFinding.severity,
            func.count(PTaaSFinding.id).label('count')
        ).filter(
            PTaaSFinding.engagement_id == engagement_id,
            PTaaSFinding.created_at >= start_date
        ).group_by(
            func.date(PTaaSFinding.created_at),
            PTaaSFinding.severity
        ).all()
        
        # Organize by date
        trends = {}
        for finding in findings:
            date_str = finding.date.strftime('%Y-%m-%d')
            if date_str not in trends:
                trends[date_str] = {
                    'date': date_str,
                    'critical': 0,
                    'high': 0,
                    'medium': 0,
                    'low': 0,
                    'info': 0
                }
            trends[date_str][finding.severity.lower()] = finding.count
        
        return sorted(trends.values(), key=lambda x: x['date'])
    
    def calculate_time_to_fix(self, engagement_id: UUID) -> Dict:
        """Calculate average time to fix by severity"""
        findings = self.db.query(PTaaSFinding).filter(
            PTaaSFinding.engagement_id == engagement_id,
            PTaaSFinding.status.in_(['FIXED', 'CLOSED']),
            PTaaSFinding.fixed_at.isnot(None)
        ).all()
        
        time_by_severity = {
            'critical': [],
            'high': [],
            'medium': [],
            'low': [],
            'info': []
        }
        
        for finding in findings:
            if finding.fixed_at and finding.created_at:
                days = (finding.fixed_at - finding.created_at).days
                severity = finding.severity.lower()
                if severity in time_by_severity:
                    time_by_severity[severity].append(days)
        
        # Calculate averages
        result = {}
        for severity, times in time_by_severity.items():
            if times:
                result[f'{severity}_avg_days'] = round(sum(times) / len(times), 1)
                result[f'{severity}_min_days'] = min(times)
                result[f'{severity}_max_days'] = max(times)
            else:
                result[f'{severity}_avg_days'] = 0
                result[f'{severity}_min_days'] = 0
                result[f'{severity}_max_days'] = 0
        
        return result
    
    def calculate_risk_score(self, engagement_id: UUID) -> float:
        """Calculate overall risk score (0-10 scale)"""
        findings = self.db.query(PTaaSFinding).filter(
            PTaaSFinding.engagement_id == engagement_id,
            PTaaSFinding.status.notin_(['CLOSED', 'REJECTED'])
        ).all()
        
        # Weight by severity
        severity_weights = {
            'CRITICAL': 10,
            'HIGH': 7,
            'MEDIUM': 4,
            'LOW': 2,
            'INFO': 0.5
        }
        
        total_score = 0
        for finding in findings:
            weight = severity_weights.get(finding.severity, 0)
            total_score += weight
        
        # Normalize to 0-10 scale (assuming max 50 findings)
        risk_score = min(total_score / 5, 10)
        
        return round(risk_score, 1)
    
    def get_compliance_status(self, engagement_id: UUID) -> Dict:
        """Get compliance status for various standards"""
        engagement = self.db.query(PTaaSEngagement).filter(
            PTaaSEngagement.id == engagement_id
        ).first()
        
        if not engagement:
            return {}
        
        findings = self.db.query(PTaaSFinding).filter(
            PTaaSFinding.engagement_id == engagement_id
        ).all()
        
        # Count critical/high findings
        critical_count = sum(1 for f in findings if f.severity == 'CRITICAL' and f.status not in ['FIXED', 'CLOSED'])
        high_count = sum(1 for f in findings if f.severity == 'HIGH' and f.status not in ['FIXED', 'CLOSED'])
        
        # Determine compliance status
        pci_dss = 'compliant' if critical_count == 0 and high_count == 0 else 'non_compliant'
        owasp_top_10 = 'compliant' if critical_count == 0 else 'partial' if high_count < 3 else 'non_compliant'
        iso_27001 = 'compliant' if critical_count == 0 and high_count < 2 else 'non_compliant'
        
        return {
            'pci_dss': pci_dss,
            'owasp_top_10': owasp_top_10,
            'iso_27001': iso_27001,
            'critical_findings': critical_count,
            'high_findings': high_count
        }
    
    def get_engagement_analytics(self, engagement_id: UUID) -> Dict:
        """Get comprehensive analytics for engagement"""
        return {
            'vulnerability_trends': self.get_vulnerability_trends(engagement_id),
            'time_to_fix': self.calculate_time_to_fix(engagement_id),
            'risk_score': self.calculate_risk_score(engagement_id),
            'compliance_status': self.get_compliance_status(engagement_id)
        }
    
    def get_researcher_performance(self, engagement_id: UUID) -> List[Dict]:
        """Get performance metrics for researchers"""
        findings = self.db.query(
            PTaaSFinding.submitted_by,
            func.count(PTaaSFinding.id).label('total_findings'),
            func.sum(func.case(
                (PTaaSFinding.severity == 'CRITICAL', 1),
                else_=0
            )).label('critical_count'),
            func.sum(func.case(
                (PTaaSFinding.severity == 'HIGH', 1),
                else_=0
            )).label('high_count')
        ).filter(
            PTaaSFinding.engagement_id == engagement_id
        ).group_by(
            PTaaSFinding.submitted_by
        ).all()
        
        return [
            {
                'researcher_id': str(f.submitted_by),
                'total_findings': f.total_findings,
                'critical_findings': f.critical_count or 0,
                'high_findings': f.high_count or 0
            }
            for f in findings
        ]
