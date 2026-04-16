"""
PTaaS Report Generation Service - Step 12
Generates PDF reports for PTaaS engagements
"""
from sqlalchemy.orm import Session
from typing import Dict, Optional
from uuid import UUID
from datetime import datetime
from src.domain.models.ptaas import PTaaSEngagement, PTaaSFinding
from src.services.ptaas_analytics_service import PTaaSAnalyticsService
import json


class PTaaSReportService:
    def __init__(self, db: Session):
        self.db = db
        self.analytics_service = PTaaSAnalyticsService(db)
    
    def generate_executive_summary(self, engagement_id: UUID) -> Dict:
        """Generate executive summary report"""
        engagement = self.db.query(PTaaSEngagement).filter(
            PTaaSEngagement.id == engagement_id
        ).first()
        
        if not engagement:
            raise ValueError("Engagement not found")
        
        # Get findings summary
        findings = self.db.query(PTaaSFinding).filter(
            PTaaSFinding.engagement_id == engagement_id
        ).all()
        
        findings_by_severity = {
            'critical': len([f for f in findings if f.severity == 'CRITICAL']),
            'high': len([f for f in findings if f.severity == 'HIGH']),
            'medium': len([f for f in findings if f.severity == 'MEDIUM']),
            'low': len([f for f in findings if f.severity == 'LOW']),
            'info': len([f for f in findings if f.severity == 'INFO']),
        }
        
        # Get analytics
        analytics = self.analytics_service.get_engagement_analytics(engagement_id)
        
        return {
            'engagement': {
                'id': str(engagement.id),
                'name': engagement.engagement_name,
                'type': engagement.engagement_type,
                'status': engagement.status,
                'start_date': engagement.start_date.isoformat() if engagement.start_date else None,
                'end_date': engagement.end_date.isoformat() if engagement.end_date else None,
                'methodology': engagement.testing_methodology,
            },
            'summary': {
                'total_findings': len(findings),
                'findings_by_severity': findings_by_severity,
                'risk_score': analytics['risk_score'],
                'compliance_status': analytics['compliance_status'],
            },
            'findings': [
                {
                    'id': str(f.id),
                    'title': f.title,
                    'severity': f.severity,
                    'status': f.status,
                    'cvss_score': f.cvss_score,
                    'description': f.description[:200] + '...' if len(f.description) > 200 else f.description,
                }
                for f in findings
            ],
            'recommendations': self._generate_recommendations(findings_by_severity, analytics),
            'generated_at': datetime.utcnow().isoformat(),
        }
    
    def generate_technical_report(self, engagement_id: UUID) -> Dict:
        """Generate detailed technical report"""
        engagement = self.db.query(PTaaSEngagement).filter(
            PTaaSEngagement.id == engagement_id
        ).first()
        
        if not engagement:
            raise ValueError("Engagement not found")
        
        findings = self.db.query(PTaaSFinding).filter(
            PTaaSFinding.engagement_id == engagement_id
        ).all()
        
        return {
            'engagement': {
                'id': str(engagement.id),
                'name': engagement.engagement_name,
                'type': engagement.engagement_type,
                'methodology': engagement.testing_methodology,
                'scope': engagement.scope_description,
                'targets': engagement.in_scope_targets,
            },
            'findings': [
                {
                    'id': str(f.id),
                    'title': f.title,
                    'severity': f.severity,
                    'status': f.status,
                    'cvss_score': f.cvss_score,
                    'cvss_vector': f.cvss_vector,
                    'description': f.description,
                    'impact': f.impact,
                    'affected_components': f.affected_components,
                    'reproduction_steps': f.reproduction_steps,
                    'remediation': f.remediation_recommendation,
                    'references': f.references,
                    'submitted_by': str(f.submitted_by),
                    'created_at': f.created_at.isoformat(),
                }
                for f in findings
            ],
            'generated_at': datetime.utcnow().isoformat(),
        }
    
    def generate_compliance_report(self, engagement_id: UUID, framework: str = 'PCI_DSS') -> Dict:
        """Generate compliance-specific report"""
        engagement = self.db.query(PTaaSEngagement).filter(
            PTaaSEngagement.id == engagement_id
        ).first()
        
        if not engagement:
            raise ValueError("Engagement not found")
        
        analytics = self.analytics_service.get_engagement_analytics(engagement_id)
        findings = self.db.query(PTaaSFinding).filter(
            PTaaSFinding.engagement_id == engagement_id
        ).all()
        
        # Map findings to compliance requirements
        compliance_mapping = self._map_findings_to_compliance(findings, framework)
        
        return {
            'engagement': {
                'id': str(engagement.id),
                'name': engagement.engagement_name,
            },
            'framework': framework,
            'compliance_status': analytics['compliance_status'],
            'requirements': compliance_mapping,
            'summary': {
                'total_requirements': len(compliance_mapping),
                'passed': len([r for r in compliance_mapping if r['status'] == 'passed']),
                'failed': len([r for r in compliance_mapping if r['status'] == 'failed']),
            },
            'generated_at': datetime.utcnow().isoformat(),
        }
    
    def _generate_recommendations(self, findings_by_severity: Dict, analytics: Dict) -> list:
        """Generate recommendations based on findings"""
        recommendations = []
        
        if findings_by_severity['critical'] > 0:
            recommendations.append({
                'priority': 'CRITICAL',
                'title': 'Address Critical Vulnerabilities Immediately',
                'description': f'There are {findings_by_severity["critical"]} critical vulnerabilities that require immediate attention.',
            })
        
        if findings_by_severity['high'] > 3:
            recommendations.append({
                'priority': 'HIGH',
                'title': 'Implement Security Hardening',
                'description': 'Multiple high-severity findings indicate need for comprehensive security hardening.',
            })
        
        if analytics['risk_score'] > 7:
            recommendations.append({
                'priority': 'HIGH',
                'title': 'Reduce Overall Risk Score',
                'description': f'Current risk score of {analytics["risk_score"]} is above acceptable threshold.',
            })
        
        return recommendations
    
    def _map_findings_to_compliance(self, findings: list, framework: str) -> list:
        """Map findings to compliance framework requirements"""
        # Simplified mapping - in production, this would be more comprehensive
        requirements = []
        
        if framework == 'PCI_DSS':
            requirements = [
                {
                    'requirement': '6.5.1 - Injection Flaws',
                    'status': 'passed' if not any(f.title.lower().find('injection') != -1 for f in findings) else 'failed',
                    'findings': [str(f.id) for f in findings if 'injection' in f.title.lower()],
                },
                {
                    'requirement': '6.5.3 - Insecure Cryptographic Storage',
                    'status': 'passed' if not any('crypto' in f.title.lower() for f in findings) else 'failed',
                    'findings': [str(f.id) for f in findings if 'crypto' in f.title.lower()],
                },
                {
                    'requirement': '6.5.7 - Cross-Site Scripting (XSS)',
                    'status': 'passed' if not any('xss' in f.title.lower() for f in findings) else 'failed',
                    'findings': [str(f.id) for f in findings if 'xss' in f.title.lower()],
                },
            ]
        
        return requirements
    
    def export_to_json(self, report_data: Dict, filename: str) -> str:
        """Export report to JSON file"""
        # In production, save to file storage service
        return json.dumps(report_data, indent=2)
    
    def export_to_pdf(self, report_data: Dict, filename: str) -> str:
        """Export report to PDF (placeholder for PDF generation)"""
        # In production, use ReportLab or WeasyPrint
        # For now, return a placeholder
        return f"PDF generation for {filename} - would use ReportLab/WeasyPrint in production"
