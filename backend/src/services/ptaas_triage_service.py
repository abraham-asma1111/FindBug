"""
PTaaS Triage Service - FREQ-36
Triage specialist validation, prioritization, and reporting
"""
from typing import List, Dict, Optional, Any
from sqlalchemy.orm import Session
from datetime import datetime
from backend.src.domain.models.ptaas_triage import (
    PTaaSFindingTriage, PTaaSExecutiveReport, PTaaSFindingPrioritization
)
from backend.src.domain.models.ptaas import PTaaSEngagement, PTaaSFinding
from backend.src.services.audit_service import AuditService


class PTaaSTriageService:
    """Service for PTaaS triage operations - FREQ-36"""
    
    def __init__(self, db: Session):
        self.db = db
        self.audit_service = AuditService(db)
    
    # Triage Validation
    def triage_finding(
        self,
        finding_id: int,
        triaged_by: int,
        triage_data: Dict[str, Any]
    ) -> PTaaSFindingTriage:
        """
        Triage and validate a finding - FREQ-36
        Platform triage specialists validate findings and assess risk
        """
        # Check if triage already exists
        existing_triage = self.db.query(PTaaSFindingTriage).filter(
            PTaaSFindingTriage.finding_id == finding_id
        ).first()
        
        if existing_triage:
            # Update existing triage
            for key, value in triage_data.items():
                setattr(existing_triage, key, value)
            existing_triage.triaged_by = triaged_by
            existing_triage.triaged_at = datetime.utcnow()
            existing_triage.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(existing_triage)
            triage = existing_triage
        else:
            # Create new triage
            triage_dict = {
                'finding_id': finding_id,
                'triaged_by': triaged_by,
                **triage_data
            }
            triage = PTaaSFindingTriage(**triage_dict)
            self.db.add(triage)
            self.db.commit()
            self.db.refresh(triage)
        
        # Audit log
        self.audit_service.log_action(
            user_id=triaged_by,
            action="TRIAGE_PTAAS_FINDING",
            resource_type="PTaaSFindingTriage",
            resource_id=triage.id,
            details={
                "finding_id": finding_id,
                "triage_status": triage.triage_status,
                "priority_level": triage.priority_level,
                "risk_rating": triage.risk_rating
            }
        )
        
        return triage
    
    def get_finding_triage(self, finding_id: int) -> Optional[PTaaSFindingTriage]:
        """Get triage record for finding"""
        return self.db.query(PTaaSFindingTriage).filter(
            PTaaSFindingTriage.finding_id == finding_id
        ).first()
    
    def get_pending_triage(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get findings pending triage"""
        # Find findings without triage or with PENDING status
        findings = self.db.query(PTaaSFinding).outerjoin(PTaaSFindingTriage).filter(
            (PTaaSFindingTriage.id == None) | 
            (PTaaSFindingTriage.triage_status == "PENDING")
        ).limit(limit).all()
        
        return [
            {
                'finding_id': f.id,
                'engagement_id': f.engagement_id,
                'title': f.title,
                'severity': f.severity,
                'discovered_at': f.discovered_at,
                'has_triage': hasattr(f, 'triage') and f.triage is not None
            }
            for f in findings
        ]
    
    # Prioritization
    def prioritize_finding(
        self,
        finding_id: int,
        prioritized_by: int,
        new_priority: str,
        reason: str,
        factors: Optional[List[str]] = None
    ) -> PTaaSFindingPrioritization:
        """
        Prioritize a finding - FREQ-36
        Track prioritization changes with justification
        """
        # Get current priority from triage
        triage = self.get_finding_triage(finding_id)
        old_priority = triage.priority_level if triage else None
        
        # Create prioritization record
        prioritization = PTaaSFindingPrioritization(
            finding_id=finding_id,
            prioritized_by=prioritized_by,
            old_priority=old_priority,
            new_priority=new_priority,
            reason=reason,
            factors_considered=factors or []
        )
        self.db.add(prioritization)
        
        # Update triage priority if exists
        if triage:
            triage.priority_level = new_priority
            triage.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(prioritization)
        
        # Audit log
        self.audit_service.log_action(
            user_id=prioritized_by,
            action="PRIORITIZE_PTAAS_FINDING",
            resource_type="PTaaSFindingPrioritization",
            resource_id=prioritization.id,
            details={
                "finding_id": finding_id,
                "old_priority": old_priority,
                "new_priority": new_priority
            }
        )
        
        return prioritization
    
    def calculate_priority_score(
        self,
        severity: str,
        exploitability: int,
        impact: int,
        compliance_impact: bool = False
    ) -> int:
        """
        Calculate priority score (1-100) - FREQ-36
        Based on severity, exploitability, impact, and compliance
        """
        severity_weights = {
            'Critical': 40,
            'High': 30,
            'Medium': 20,
            'Low': 10,
            'Info': 5
        }
        
        base_score = severity_weights.get(severity, 10)
        exploitability_score = exploitability * 3  # 0-30
        impact_score = impact * 2  # 0-20
        compliance_bonus = 10 if compliance_impact else 0
        
        total = base_score + exploitability_score + impact_score + compliance_bonus
        return min(100, total)
    
    # Executive Report Generation
    def generate_executive_report(
        self,
        engagement_id: int,
        generated_by: int,
        report_data: Optional[Dict[str, Any]] = None
    ) -> PTaaSExecutiveReport:
        """
        Generate compliance-ready executive report - FREQ-36
        Includes risk ratings, evidence, and recommendations
        """
        engagement = self.db.query(PTaaSEngagement).filter(
            PTaaSEngagement.id == engagement_id
        ).first()
        
        if not engagement:
            raise ValueError("Engagement not found")
        
        # Get all findings for engagement
        findings = self.db.query(PTaaSFinding).filter(
            PTaaSFinding.engagement_id == engagement_id
        ).all()
        
        # Get triage data for findings
        triaged_findings = []
        for finding in findings:
            triage = self.get_finding_triage(finding.id)
            triaged_findings.append({
                'finding': finding,
                'triage': triage
            })
        
        # Calculate statistics
        stats = self._calculate_report_statistics(triaged_findings)
        
        # Generate executive summary
        executive_summary = self._generate_executive_summary(
            engagement, triaged_findings, stats
        )
        
        # Identify key findings
        key_findings = self._identify_key_findings(triaged_findings)
        
        # Calculate overall risk
        overall_risk = self._calculate_overall_risk(triaged_findings)
        
        # Generate compliance status
        compliance_status = self._generate_compliance_status(triaged_findings)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(triaged_findings, stats)
        
        # Create report
        report_dict = {
            'engagement_id': engagement_id,
            'report_title': report_data.get('report_title') if report_data else f"Executive Report - {engagement.name}",
            'report_type': report_data.get('report_type', 'EXECUTIVE') if report_data else 'EXECUTIVE',
            'generated_by': generated_by,
            'report_period_start': engagement.start_date,
            'report_period_end': engagement.end_date,
            'executive_summary': executive_summary,
            'key_findings': key_findings,
            'overall_risk_rating': overall_risk['rating'],
            'total_findings': stats['total'],
            'critical_findings': stats['critical'],
            'high_findings': stats['high'],
            'medium_findings': stats['medium'],
            'low_findings': stats['low'],
            'risk_score': overall_risk['score'],
            'risk_trend': overall_risk['trend'],
            'compliance_status': compliance_status['status'],
            'compliance_gaps': compliance_status['gaps'],
            'compliance_recommendations': compliance_status['recommendations'],
            'immediate_actions': recommendations['immediate'],
            'short_term_actions': recommendations['short_term'],
            'long_term_actions': recommendations['long_term'],
            'evidence_summary': self._generate_evidence_summary(triaged_findings)
        }
        
        report = PTaaSExecutiveReport(**report_dict)
        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)
        
        # Audit log
        self.audit_service.log_action(
            user_id=generated_by,
            action="GENERATE_EXECUTIVE_REPORT",
            resource_type="PTaaSExecutiveReport",
            resource_id=report.id,
            details={
                "engagement_id": engagement_id,
                "total_findings": stats['total'],
                "overall_risk": overall_risk['rating']
            }
        )
        
        return report
    
    def get_executive_report(self, report_id: int) -> Optional[PTaaSExecutiveReport]:
        """Get executive report by ID"""
        return self.db.query(PTaaSExecutiveReport).filter(
            PTaaSExecutiveReport.id == report_id
        ).first()
    
    def get_engagement_reports(self, engagement_id: int) -> List[PTaaSExecutiveReport]:
        """Get all reports for engagement"""
        return self.db.query(PTaaSExecutiveReport).filter(
            PTaaSExecutiveReport.engagement_id == engagement_id
        ).order_by(PTaaSExecutiveReport.generated_at.desc()).all()
    
    def approve_report(
        self,
        report_id: int,
        approved_by: int
    ) -> PTaaSExecutiveReport:
        """Approve executive report"""
        report = self.get_executive_report(report_id)
        if report:
            report.approved = True
            report.approved_by = approved_by
            report.approved_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(report)
            
            self.audit_service.log_action(
                user_id=approved_by,
                action="APPROVE_EXECUTIVE_REPORT",
                resource_type="PTaaSExecutiveReport",
                resource_id=report_id,
                details={"engagement_id": report.engagement_id}
            )
        
        return report
    
    # Helper methods
    def _calculate_report_statistics(self, triaged_findings: List[Dict]) -> Dict[str, int]:
        """Calculate finding statistics"""
        stats = {
            'total': len(triaged_findings),
            'critical': 0,
            'high': 0,
            'medium': 0,
            'low': 0,
            'info': 0
        }
        
        for item in triaged_findings:
            severity = item['finding'].severity.lower()
            if severity in stats:
                stats[severity] += 1
        
        return stats
    
    def _generate_executive_summary(
        self,
        engagement: PTaaSEngagement,
        triaged_findings: List[Dict],
        stats: Dict[str, int]
    ) -> str:
        """Generate executive summary text"""
        summary = f"Executive Summary for {engagement.name}\n\n"
        summary += f"Testing Period: {engagement.start_date.strftime('%Y-%m-%d')} to {engagement.end_date.strftime('%Y-%m-%d')}\n"
        summary += f"Methodology: {engagement.testing_methodology}\n\n"
        summary += f"Total Findings: {stats['total']}\n"
        summary += f"- Critical: {stats['critical']}\n"
        summary += f"- High: {stats['high']}\n"
        summary += f"- Medium: {stats['medium']}\n"
        summary += f"- Low: {stats['low']}\n\n"
        
        if stats['critical'] > 0:
            summary += f"CRITICAL: {stats['critical']} critical vulnerabilities require immediate attention.\n"
        
        return summary
    
    def _identify_key_findings(self, triaged_findings: List[Dict]) -> List[Dict]:
        """Identify key findings for executive report"""
        key_findings = []
        
        for item in triaged_findings:
            finding = item['finding']
            triage = item['triage']
            
            # Include critical and high severity with validated triage
            if finding.severity in ['Critical', 'High'] and triage and triage.triage_status == 'VALIDATED':
                key_findings.append({
                    'id': finding.id,
                    'title': finding.title,
                    'severity': finding.severity,
                    'risk_rating': triage.risk_rating if triage else 'UNKNOWN',
                    'priority': triage.priority_level if triage else 'UNKNOWN',
                    'executive_summary': triage.executive_summary if triage else finding.description[:200]
                })
        
        # Sort by priority and limit to top 10
        return sorted(key_findings, key=lambda x: x['severity'], reverse=True)[:10]
    
    def _calculate_overall_risk(self, triaged_findings: List[Dict]) -> Dict[str, Any]:
        """Calculate overall risk rating"""
        if not triaged_findings:
            return {'rating': 'LOW', 'score': 0, 'trend': 'STABLE'}
        
        total_score = 0
        count = 0
        
        for item in triaged_findings:
            triage = item['triage']
            if triage and triage.priority_score:
                total_score += triage.priority_score
                count += 1
        
        avg_score = total_score / count if count > 0 else 0
        
        if avg_score >= 80:
            rating = 'CRITICAL'
        elif avg_score >= 60:
            rating = 'HIGH'
        elif avg_score >= 40:
            rating = 'MEDIUM'
        else:
            rating = 'LOW'
        
        return {
            'rating': rating,
            'score': round(avg_score, 2),
            'trend': 'STABLE'  # Could be calculated from historical data
        }
    
    def _generate_compliance_status(self, triaged_findings: List[Dict]) -> Dict[str, Any]:
        """Generate compliance status"""
        frameworks = set()
        gaps = []
        
        for item in triaged_findings:
            triage = item['triage']
            if triage and triage.compliance_frameworks:
                frameworks.update(triage.compliance_frameworks)
                if triage.compliance_controls:
                    gaps.extend(triage.compliance_controls)
        
        status = {framework: 'NON_COMPLIANT' if gaps else 'COMPLIANT' for framework in frameworks}
        
        return {
            'status': status,
            'gaps': list(set(gaps)),
            'recommendations': "Address identified compliance gaps to achieve full compliance."
        }
    
    def _generate_recommendations(
        self,
        triaged_findings: List[Dict],
        stats: Dict[str, int]
    ) -> Dict[str, List[str]]:
        """Generate actionable recommendations"""
        immediate = []
        short_term = []
        long_term = []
        
        if stats['critical'] > 0:
            immediate.append(f"Address {stats['critical']} critical vulnerabilities immediately")
        
        if stats['high'] > 0:
            immediate.append(f"Remediate {stats['high']} high-severity findings within 30 days")
        
        if stats['medium'] > 0:
            short_term.append(f"Plan remediation for {stats['medium']} medium-severity findings")
        
        long_term.append("Implement continuous security testing")
        long_term.append("Enhance security awareness training")
        
        return {
            'immediate': immediate,
            'short_term': short_term,
            'long_term': long_term
        }
    
    def _generate_evidence_summary(self, triaged_findings: List[Dict]) -> Dict[str, Any]:
        """Generate evidence summary"""
        total_evidence = 0
        validated_evidence = 0
        
        for item in triaged_findings:
            finding = item['finding']
            triage = item['triage']
            
            if finding.proof_of_exploit:
                total_evidence += 1
                if triage and triage.evidence_validated:
                    validated_evidence += 1
        
        return {
            'total_findings_with_evidence': total_evidence,
            'validated_evidence': validated_evidence,
            'validation_rate': round((validated_evidence / total_evidence * 100) if total_evidence > 0 else 0, 2)
        }
