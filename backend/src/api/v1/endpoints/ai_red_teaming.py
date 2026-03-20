"""
AI Red Teaming API Endpoints
Implements FREQ-45, FREQ-46, FREQ-47, FREQ-48: AI Security Testing
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from backend.src.core.database import get_db
from backend.src.api.v1.middlewares.auth import get_current_user
from backend.src.domain.models.user import User
from backend.src.services.ai_red_teaming_service import AIRedTeamingService
from backend.src.domain.models.ai_red_teaming import (
    AIModelType,
    EngagementStatus,
    AIAttackType,
    AIClassification,
    ReportStatus
)
from backend.src.api.v1.schemas.ai_red_teaming import (
    EngagementCreate,
    EngagementResponse,
    TestingEnvironmentCreate,
    TestingEnvironmentResponse,
    VulnerabilityReportCreate,
    VulnerabilityReportResponse,
    FindingClassificationCreate,
    FindingClassificationResponse,
    SecurityReportCreate,
    SecurityReportResponse,
    AssignExpertsRequest,
    ValidateFindingRequest,
    EngagementStatusUpdate
)

router = APIRouter(prefix="/ai-red-teaming", tags=["ai-red-teaming"])


# ============================================
# ENGAGEMENT MANAGEMENT (FREQ-45)
# ============================================

@router.post("/engagements", response_model=EngagementResponse, status_code=status.HTTP_201_CREATED)
def create_engagement(
    data: EngagementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create new AI Red Teaming engagement (FREQ-45)
    
    Requires organization admin role
    """
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User must belong to an organization"
        )
    
    service = AIRedTeamingService(db)
    
    try:
        model_type = AIModelType(data.model_type)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid model type: {data.model_type}"
        )
    
    engagement = service.create_engagement(
        organization_id=current_user.organization_id,
        name=data.name,
        target_ai_system=data.target_ai_system,
        model_type=model_type,
        testing_environment=data.testing_environment,
        ethical_guidelines=data.ethical_guidelines,
        scope_description=data.scope_description,
        allowed_attack_types=data.allowed_attack_types
    )
    
    return engagement


@router.get("/engagements", response_model=List[EngagementResponse])
def list_engagements(
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List AI Red Teaming engagements"""
    service = AIRedTeamingService(db)
    
    status_enum = None
    if status_filter:
        try:
            status_enum = EngagementStatus(status_filter)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {status_filter}"
            )
    
    if current_user.organization_id:
        engagements = service.list_engagements(
            organization_id=current_user.organization_id,
            status=status_enum
        )
    else:
        # Researcher view - only assigned engagements
        engagements = service.list_engagements(status=status_enum)
        # TODO: Filter by assigned researcher
    
    return engagements


@router.get("/engagements/{engagement_id}", response_model=EngagementResponse)
def get_engagement(
    engagement_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get engagement by ID"""
    service = AIRedTeamingService(db)
    engagement = service.get_engagement(engagement_id)
    
    if not engagement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Engagement not found"
        )
    
    # Check access
    if current_user.organization_id:
        if engagement.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    
    return engagement


@router.patch("/engagements/{engagement_id}/status", response_model=EngagementResponse)
def update_engagement_status(
    engagement_id: UUID,
    data: EngagementStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update engagement status"""
    service = AIRedTeamingService(db)
    engagement = service.get_engagement(engagement_id)
    
    if not engagement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Engagement not found"
        )
    
    if engagement.organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    try:
        status_enum = EngagementStatus(data.status)
        engagement = service.update_engagement_status(engagement_id, status_enum)
        return engagement
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/engagements/{engagement_id}/assign-experts", response_model=EngagementResponse)
def assign_experts(
    engagement_id: UUID,
    data: AssignExpertsRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Assign AI security experts to engagement"""
    service = AIRedTeamingService(db)
    engagement = service.get_engagement(engagement_id)
    
    if not engagement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Engagement not found"
        )
    
    if engagement.organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    try:
        engagement = service.assign_experts(engagement_id, data.researcher_ids)
        return engagement
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# ============================================
# TESTING ENVIRONMENT (FREQ-46)
# ============================================

@router.post("/engagements/{engagement_id}/testing-environment", response_model=TestingEnvironmentResponse, status_code=status.HTTP_201_CREATED)
def setup_testing_environment(
    engagement_id: UUID,
    data: TestingEnvironmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Setup AI testing environment (FREQ-46)
    
    Defines scope, sandbox, and ethical guidelines
    """
    service = AIRedTeamingService(db)
    engagement = service.get_engagement(engagement_id)
    
    if not engagement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Engagement not found"
        )
    
    if engagement.organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    try:
        environment = service.setup_testing_environment(
            engagement_id=engagement_id,
            model_type=data.model_type,
            sandbox_url=data.sandbox_url,
            api_endpoint=data.api_endpoint,
            access_token=data.access_token,
            access_controls=data.access_controls,
            rate_limits=data.rate_limits,
            is_isolated=data.is_isolated
        )
        return environment
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/engagements/{engagement_id}/testing-environment", response_model=TestingEnvironmentResponse)
def get_testing_environment(
    engagement_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get testing environment for engagement"""
    service = AIRedTeamingService(db)
    environment = service.get_testing_environment(engagement_id)
    
    if not environment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Testing environment not found"
        )
    
    return environment


# ============================================
# VULNERABILITY REPORTS (FREQ-47)
# ============================================

@router.post("/engagements/{engagement_id}/reports", response_model=VulnerabilityReportResponse, status_code=status.HTTP_201_CREATED)
def submit_vulnerability_report(
    engagement_id: UUID,
    data: VulnerabilityReportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Submit AI-specific vulnerability report (FREQ-47)
    
    Includes input/prompt, model response, attack type, and impact
    """
    if not current_user.researcher:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not a researcher"
        )
    
    service = AIRedTeamingService(db)
    
    try:
        attack_type = AIAttackType(data.attack_type)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid attack type: {data.attack_type}"
        )
    
    try:
        report = service.submit_vulnerability_report(
            engagement_id=engagement_id,
            researcher_id=current_user.researcher.id,
            title=data.title,
            input_prompt=data.input_prompt,
            model_response=data.model_response,
            attack_type=attack_type,
            severity=data.severity,
            impact=data.impact,
            reproduction_steps=data.reproduction_steps,
            mitigation_recommendation=data.mitigation_recommendation,
            model_version=data.model_version,
            environment_details=data.environment_details
        )
        return report
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/engagements/{engagement_id}/reports", response_model=List[VulnerabilityReportResponse])
def list_vulnerability_reports(
    engagement_id: UUID,
    status_filter: Optional[str] = None,
    attack_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List AI vulnerability reports for engagement"""
    service = AIRedTeamingService(db)
    
    status_enum = None
    if status_filter:
        try:
            status_enum = ReportStatus(status_filter)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {status_filter}"
            )
    
    attack_type_enum = None
    if attack_type:
        try:
            attack_type_enum = AIAttackType(attack_type)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid attack type: {attack_type}"
            )
    
    reports = service.list_vulnerability_reports(
        engagement_id=engagement_id,
        status=status_enum,
        attack_type=attack_type_enum
    )
    
    return reports


@router.get("/reports/{report_id}", response_model=VulnerabilityReportResponse)
def get_vulnerability_report(
    report_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get vulnerability report by ID"""
    service = AIRedTeamingService(db)
    report = service.get_vulnerability_report(report_id)
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    return report


# ============================================
# TRIAGE WORKFLOW (FREQ-48)
# ============================================

@router.post("/reports/{report_id}/classify", response_model=FindingClassificationResponse, status_code=status.HTTP_201_CREATED)
def classify_finding(
    report_id: UUID,
    data: FindingClassificationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Classify AI vulnerability finding (FREQ-48)
    
    Dedicated triage workflow for AI-specific vulnerabilities
    """
    # TODO: Check if user is triage specialist
    
    service = AIRedTeamingService(db)
    
    try:
        primary_category = AIClassification(data.primary_category)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid classification: {data.primary_category}"
        )
    
    try:
        classification = service.classify_finding(
            report_id=report_id,
            primary_category=primary_category,
            risk_score=data.risk_score,
            confidence_level=data.confidence_level,
            classified_by=current_user.id,
            justification=data.justification,
            secondary_categories=data.secondary_categories,
            affected_components=data.affected_components,
            remediation_priority=data.remediation_priority
        )
        return classification
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/reports/{report_id}/validate", response_model=VulnerabilityReportResponse)
def validate_finding(
    report_id: UUID,
    data: ValidateFindingRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Validate AI vulnerability finding"""
    service = AIRedTeamingService(db)
    
    try:
        report = service.validate_finding(report_id, data.is_valid)
        return report
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# ============================================
# SECURITY REPORTS (FREQ-48)
# ============================================

@router.post("/engagements/{engagement_id}/security-report", response_model=SecurityReportResponse, status_code=status.HTTP_201_CREATED)
def generate_security_report(
    engagement_id: UUID,
    data: SecurityReportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate AI security summary report (FREQ-48)
    
    Includes security, safety, and trust findings
    """
    service = AIRedTeamingService(db)
    engagement = service.get_engagement(engagement_id)
    
    if not engagement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Engagement not found"
        )
    
    if engagement.organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    try:
        report = service.generate_security_report(
            engagement_id=engagement_id,
            generated_by=current_user.id,
            report_title=data.report_title,
            executive_summary=data.executive_summary,
            recommendations=data.recommendations
        )
        return report
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/engagements/{engagement_id}/security-reports", response_model=List[SecurityReportResponse])
def list_security_reports(
    engagement_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List security reports for engagement"""
    service = AIRedTeamingService(db)
    reports = service.get_security_reports(engagement_id)
    
    return reports
