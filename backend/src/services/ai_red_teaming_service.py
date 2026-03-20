"""
AI Red Teaming Service
Implements FREQ-45, FREQ-46, FREQ-47, FREQ-48: AI Security Testing
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from uuid import UUID
from decimal import Decimal

from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from backend.src.domain.models.ai_red_teaming import (
    AIRedTeamingEngagement,
    AITestingEnvironment,
    AIVulnerabilityReport,
    AIFindingClassification,
    AISecurityReport,
    AIModelType,
    EngagementStatus,
    AIAttackType,
    AIClassification,
    ReportStatus
)

logger = logging.getLogger(__name__)


class AIRedTeamingService:
    """Service for managing AI Red Teaming engagements"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # ============================================
    # FREQ-45: Create and Manage AI Red Teaming Engagements
    # ============================================
    
    def create_engagement(
        self,
        organization_id: UUID,
        name: str,
        target_ai_system: str,
        model_type: AIModelType,
        testing_environment: str,
        ethical_guidelines: str,
        scope_description: Optional[str] = None,
        allowed_attack_types: Optional[List[str]] = None
    ) -> AIRedTeamingEngagement:
        """
        Create new AI Red Teaming engagement (FREQ-45)
        
        Args:
            organization_id: Organization UUID
            name: Engagement name
            target_ai_system: Target AI system description
            model_type: Type of AI model
            testing_environment: Testing environment description
            ethical_guidelines: Ethical testing guidelines
            scope_description: Scope description
            allowed_attack_types: List of allowed attack types
            
        Returns:
            Created engagement
        """
        engagement = AIRedTeamingEngagement(
            organization_id=organization_id,
            name=name,
            target_ai_system=target_ai_system,
            model_type=model_type,
            testing_environment=testing_environment,
            ethical_guidelines=ethical_guidelines,
            scope_description=scope_description,
            allowed_attack_types=allowed_attack_types,
            status=EngagementStatus.DRAFT
        )
        
        self.db.add(engagement)
        self.db.commit()
        self.db.refresh(engagement)
        
        logger.info(f"Created AI Red Teaming engagement {engagement.id}")
        return engagement
    
    def get_engagement(self, engagement_id: UUID) -> Optional[AIRedTeamingEngagement]:
        """Get engagement by ID"""
        return self.db.query(AIRedTeamingEngagement).filter(
            AIRedTeamingEngagement.id == engagement_id
        ).first()
    
    def list_engagements(
        self,
        organization_id: Optional[UUID] = None,
        status: Optional[EngagementStatus] = None
    ) -> List[AIRedTeamingEngagement]:
        """List AI Red Teaming engagements"""
        query = self.db.query(AIRedTeamingEngagement)
        
        if organization_id:
            query = query.filter(AIRedTeamingEngagement.organization_id == organization_id)
        
        if status:
            query = query.filter(AIRedTeamingEngagement.status == status)
        
        return query.order_by(AIRedTeamingEngagement.created_at.desc()).all()
    
    def update_engagement_status(
        self,
        engagement_id: UUID,
        status: EngagementStatus
    ) -> AIRedTeamingEngagement:
        """Update engagement status"""
        engagement = self.get_engagement(engagement_id)
        if not engagement:
            raise ValueError(f"Engagement {engagement_id} not found")
        
        engagement.status = status
        engagement.updated_at = datetime.utcnow()
        
        if status == EngagementStatus.ACTIVE and not engagement.start_date:
            engagement.start_date = datetime.utcnow()
        elif status == EngagementStatus.COMPLETED and not engagement.end_date:
            engagement.end_date = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(engagement)
        
        logger.info(f"Updated engagement {engagement_id} status to {status}")
        return engagement
    
    def assign_experts(
        self,
        engagement_id: UUID,
        researcher_ids: List[UUID]
    ) -> AIRedTeamingEngagement:
        """Assign AI security experts to engagement"""
        engagement = self.get_engagement(engagement_id)
        if not engagement:
            raise ValueError(f"Engagement {engagement_id} not found")
        
        engagement.assigned_experts = [str(rid) for rid in researcher_ids]
        engagement.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(engagement)
        
        logger.info(f"Assigned {len(researcher_ids)} experts to engagement {engagement_id}")
        return engagement
    
    # ============================================
    # FREQ-46: Define AI Red Teaming Scope
    # ============================================
    
    def setup_testing_environment(
        self,
        engagement_id: UUID,
        model_type: str,
        sandbox_url: str,
        api_endpoint: str,
        access_token: str,
        access_controls: Dict[str, Any],
        rate_limits: Optional[Dict[str, Any]] = None,
        is_isolated: bool = True
    ) -> AITestingEnvironment:
        """
        Setup AI testing environment (FREQ-46)
        
        Args:
            engagement_id: Engagement UUID
            model_type: Model type
            sandbox_url: Sandbox URL
            api_endpoint: API endpoint
            access_token: Access token (should be encrypted)
            access_controls: Access control configuration
            rate_limits: Rate limit configuration
            is_isolated: Whether environment is isolated
            
        Returns:
            Created testing environment
        """
        # Check if environment already exists
        existing = self.db.query(AITestingEnvironment).filter(
            AITestingEnvironment.engagement_id == engagement_id
        ).first()
        
        if existing:
            raise ValueError(f"Testing environment already exists for engagement {engagement_id}")
        
        environment = AITestingEnvironment(
            engagement_id=engagement_id,
            model_type=model_type,
            sandbox_url=sandbox_url,
            api_endpoint=api_endpoint,
            access_token=access_token,  # TODO: Encrypt this
            access_controls=access_controls,
            rate_limits=rate_limits,
            is_isolated=is_isolated
        )
        
        self.db.add(environment)
        self.db.commit()
        self.db.refresh(environment)
        
        logger.info(f"Setup testing environment for engagement {engagement_id}")
        return environment
    
    def get_testing_environment(
        self,
        engagement_id: UUID
    ) -> Optional[AITestingEnvironment]:
        """Get testing environment for engagement"""
        return self.db.query(AITestingEnvironment).filter(
            AITestingEnvironment.engagement_id == engagement_id
        ).first()
    
    # ============================================
    # FREQ-47: Submit AI-Specific Vulnerability Reports
    # ============================================
    
    def submit_vulnerability_report(
        self,
        engagement_id: UUID,
        researcher_id: UUID,
        title: str,
        input_prompt: str,
        model_response: str,
        attack_type: AIAttackType,
        severity: str,
        impact: str,
        reproduction_steps: str,
        mitigation_recommendation: Optional[str] = None,
        model_version: Optional[str] = None,
        environment_details: Optional[Dict[str, Any]] = None
    ) -> AIVulnerabilityReport:
        """
        Submit AI-specific vulnerability report (FREQ-47)
        
        Args:
            engagement_id: Engagement UUID
            researcher_id: Researcher UUID
            title: Report title
            input_prompt: Input/prompt used
            model_response: Model's response
            attack_type: Type of AI attack
            severity: Severity level
            impact: Impact description
            reproduction_steps: Steps to reproduce
            mitigation_recommendation: Mitigation recommendation
            model_version: Model version tested
            environment_details: Environment details
            
        Returns:
            Created vulnerability report
        """
        # Verify engagement exists and is active
        engagement = self.get_engagement(engagement_id)
        if not engagement:
            raise ValueError(f"Engagement {engagement_id} not found")
        
        if engagement.status != EngagementStatus.ACTIVE:
            raise ValueError("Engagement is not active")
        
        # Verify researcher is assigned
        if engagement.assigned_experts and str(researcher_id) not in engagement.assigned_experts:
            raise ValueError("Researcher is not assigned to this engagement")
        
        report = AIVulnerabilityReport(
            engagement_id=engagement_id,
            researcher_id=researcher_id,
            title=title,
            input_prompt=input_prompt,
            model_response=model_response,
            attack_type=attack_type,
            severity=severity,
            impact=impact,
            reproduction_steps=reproduction_steps,
            mitigation_recommendation=mitigation_recommendation,
            model_version=model_version,
            environment_details=environment_details,
            status=ReportStatus.NEW
        )
        
        self.db.add(report)
        
        # Update engagement metrics
        engagement.total_findings += 1
        if severity == 'critical':
            engagement.critical_findings += 1
        elif severity == 'high':
            engagement.high_findings += 1
        elif severity == 'medium':
            engagement.medium_findings += 1
        elif severity == 'low':
            engagement.low_findings += 1
        
        self.db.commit()
        self.db.refresh(report)
        
        logger.info(f"Submitted AI vulnerability report {report.id} for engagement {engagement_id}")
        return report
    
    def get_vulnerability_report(
        self,
        report_id: UUID
    ) -> Optional[AIVulnerabilityReport]:
        """Get vulnerability report by ID"""
        return self.db.query(AIVulnerabilityReport).filter(
            AIVulnerabilityReport.id == report_id
        ).first()
    
    def list_vulnerability_reports(
        self,
        engagement_id: Optional[UUID] = None,
        researcher_id: Optional[UUID] = None,
        status: Optional[ReportStatus] = None,
        attack_type: Optional[AIAttackType] = None
    ) -> List[AIVulnerabilityReport]:
        """List AI vulnerability reports"""
        query = self.db.query(AIVulnerabilityReport)
        
        if engagement_id:
            query = query.filter(AIVulnerabilityReport.engagement_id == engagement_id)
        
        if researcher_id:
            query = query.filter(AIVulnerabilityReport.researcher_id == researcher_id)
        
        if status:
            query = query.filter(AIVulnerabilityReport.status == status)
        
        if attack_type:
            query = query.filter(AIVulnerabilityReport.attack_type == attack_type)
        
        return query.order_by(AIVulnerabilityReport.submitted_at.desc()).all()
    
    # ============================================
    # FREQ-48: Dedicated Triage Workflow
    # ============================================
    
    def classify_finding(
        self,
        report_id: UUID,
        primary_category: AIClassification,
        risk_score: Decimal,
        confidence_level: Decimal,
        classified_by: UUID,
        justification: str,
        secondary_categories: Optional[List[str]] = None,
        affected_components: Optional[Dict[str, Any]] = None,
        remediation_priority: Optional[str] = None
    ) -> AIFindingClassification:
        """
        Classify AI vulnerability finding (FREQ-48 - Triage)
        
        Args:
            report_id: Report UUID
            primary_category: Primary classification category
            risk_score: Risk score (0-100)
            confidence_level: Confidence level (0-100)
            classified_by: Staff UUID who classified
            justification: Classification justification
            secondary_categories: Additional categories
            affected_components: Affected components
            remediation_priority: Remediation priority
            
        Returns:
            Created classification
        """
        # Verify report exists
        report = self.get_vulnerability_report(report_id)
        if not report:
            raise ValueError(f"Report {report_id} not found")
        
        # Check if already classified
        existing = self.db.query(AIFindingClassification).filter(
            AIFindingClassification.report_id == report_id
        ).first()
        
        if existing:
            raise ValueError(f"Report {report_id} already classified")
        
        classification = AIFindingClassification(
            report_id=report_id,
            primary_category=primary_category,
            secondary_categories=secondary_categories,
            risk_score=risk_score,
            confidence_level=confidence_level,
            classified_by=classified_by,
            justification=justification,
            affected_components=affected_components,
            remediation_priority=remediation_priority
        )
        
        self.db.add(classification)
        
        # Update report
        report.classification = primary_category
        report.status = ReportStatus.TRIAGED
        
        self.db.commit()
        self.db.refresh(classification)
        
        logger.info(f"Classified AI finding {report_id} as {primary_category}")
        return classification
    
    def validate_finding(
        self,
        report_id: UUID,
        is_valid: bool
    ) -> AIVulnerabilityReport:
        """Validate AI vulnerability finding"""
        report = self.get_vulnerability_report(report_id)
        if not report:
            raise ValueError(f"Report {report_id} not found")
        
        report.status = ReportStatus.VALIDATED if is_valid else ReportStatus.INVALID
        report.validated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(report)
        
        logger.info(f"Validated AI finding {report_id}: {is_valid}")
        return report
    
    def generate_security_report(
        self,
        engagement_id: UUID,
        generated_by: UUID,
        report_title: str,
        executive_summary: Optional[str] = None,
        recommendations: Optional[str] = None
    ) -> AISecurityReport:
        """
        Generate AI security summary report (FREQ-48)
        
        Args:
            engagement_id: Engagement UUID
            generated_by: Staff UUID who generated report
            report_title: Report title
            executive_summary: Executive summary
            recommendations: Recommendations
            
        Returns:
            Generated security report
        """
        engagement = self.get_engagement(engagement_id)
        if not engagement:
            raise ValueError(f"Engagement {engagement_id} not found")
        
        # Get all reports for this engagement
        reports = self.list_vulnerability_reports(engagement_id=engagement_id)
        
        # Calculate statistics
        total_findings = len(reports)
        
        # Count by classification
        security_findings = sum(1 for r in reports if r.classification == AIClassification.SECURITY)
        safety_findings = sum(1 for r in reports if r.classification == AIClassification.SAFETY)
        trust_findings = sum(1 for r in reports if r.classification == AIClassification.TRUST)
        privacy_findings = sum(1 for r in reports if r.classification == AIClassification.PRIVACY)
        fairness_findings = sum(1 for r in reports if r.classification == AIClassification.FAIRNESS)
        
        # Count by severity
        critical_count = sum(1 for r in reports if r.severity == 'critical')
        high_count = sum(1 for r in reports if r.severity == 'high')
        medium_count = sum(1 for r in reports if r.severity == 'medium')
        low_count = sum(1 for r in reports if r.severity == 'low')
        
        # Extract key findings
        key_findings = [
            {
                "title": r.title,
                "attack_type": r.attack_type.value,
                "severity": r.severity,
                "classification": r.classification.value if r.classification else None
            }
            for r in reports[:10]  # Top 10 findings
        ]
        
        security_report = AISecurityReport(
            engagement_id=engagement_id,
            report_title=report_title,
            generated_by=generated_by,
            total_findings=total_findings,
            security_findings=security_findings,
            safety_findings=safety_findings,
            trust_findings=trust_findings,
            privacy_findings=privacy_findings,
            fairness_findings=fairness_findings,
            critical_count=critical_count,
            high_count=high_count,
            medium_count=medium_count,
            low_count=low_count,
            executive_summary=executive_summary,
            key_findings=key_findings,
            recommendations=recommendations
        )
        
        self.db.add(security_report)
        self.db.commit()
        self.db.refresh(security_report)
        
        logger.info(f"Generated AI security report for engagement {engagement_id}")
        return security_report
    
    def get_security_reports(
        self,
        engagement_id: UUID
    ) -> List[AISecurityReport]:
        """Get security reports for engagement"""
        return self.db.query(AISecurityReport).filter(
            AISecurityReport.engagement_id == engagement_id
        ).order_by(AISecurityReport.generated_at.desc()).all()
