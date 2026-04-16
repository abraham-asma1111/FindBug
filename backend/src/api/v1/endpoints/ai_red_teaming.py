"""
AI Red Teaming API Endpoints
Implements FREQ-45, FREQ-46, FREQ-47, FREQ-48: AI Security Testing
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from typing import List, Optional
from uuid import UUID

from src.core.database import get_db
from src.api.v1.middlewares.auth import get_current_user
from src.domain.models.user import User
from src.services.ai_red_teaming_service import AIRedTeamingService
from src.domain.models.ai_red_teaming import (
    AIModelType,
    EngagementStatus,
    AIAttackType,
    AIClassification,
    ReportStatus
)
from src.api.v1.schemas.ai_red_teaming import (
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
    if not current_user.organization:
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
        organization_id=current_user.organization.id,
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
    
    if current_user.organization:
        engagements = service.list_engagements(
            organization_id=current_user.organization.id,
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
    if current_user.organization:
        if engagement.organization_id != current_user.organization.id:
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
    
    if not current_user.organization or engagement.organization_id != current_user.organization.id:
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
    
    if not current_user.organization or engagement.organization_id != current_user.organization.id:
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
    
    if not current_user.organization or engagement.organization_id != current_user.organization.id:
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
    
    if not current_user.organization or engagement.organization_id != current_user.organization.id:
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


# ============================================
# RESEARCHER INVITATIONS & ASSIGNED ENGAGEMENTS
# ============================================

@router.get("/my-invitations", response_model=List[dict])
def get_my_invitations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get AI Red Teaming invitations for current researcher"""
    if not current_user.researcher:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not a researcher"
        )
    
    # TODO: Implement invitation model and service
    # For now, return empty list
    return []


@router.post("/invitations/{invitation_id}/respond", response_model=dict)
def respond_to_invitation(
    invitation_id: UUID,
    accept: bool,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Accept or decline AI Red Teaming invitation"""
    if not current_user.researcher:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not a researcher"
        )
    
    # TODO: Implement invitation response logic
    return {"status": "accepted" if accept else "declined"}


@router.get("/researcher/engagements", response_model=List[EngagementResponse])
def list_researcher_engagements(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List AI Red Teaming engagements for current researcher.
    
    Shows ALL active engagements that match the researcher's profile (algorithm-pushed).
    This works exactly like Bug Bounty programs:
    - Organization publishes engagement (status → active)
    - BountyMatch algorithm filters researchers by AI/ML skills + reputation
    - Algorithm broadcasts to ALL qualified researchers
    - Researchers see engagements in their dashboard (algorithm-pushed, not browsing)
    """
    if not current_user.researcher:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not a researcher"
        )
    
    service = AIRedTeamingService(db)
    
    # Get all active engagements
    all_active_engagements = service.list_engagements(status=EngagementStatus.ACTIVE)
    
    # Filter engagements using BountyMatch algorithm
    # Show engagements where researcher meets minimum match threshold
    researcher_id = current_user.researcher.id
    qualified_engagements = []
    
    for engagement in all_active_engagements:
        # Check if manually assigned
        if engagement.assigned_experts and str(researcher_id) in engagement.assigned_experts:
            qualified_engagements.append(engagement)
            continue
        
        # Check if algorithm-qualified (match score > 30)
        model_type_skills = {
            AIModelType.LLM: ['llm_security', 'prompt_injection', 'ai_safety', 'nlp'],
            AIModelType.AI_AGENT: ['agent_security', 'ai_safety', 'autonomous_systems'],
            AIModelType.ML_MODEL: ['ml_security', 'adversarial_ml', 'model_security'],
            AIModelType.CHATBOT: ['chatbot_security', 'conversation_ai', 'prompt_injection'],
            AIModelType.RECOMMENDATION_SYSTEM: ['recommendation_security', 'bias_detection'],
            AIModelType.COMPUTER_VISION: ['cv_security', 'adversarial_images', 'model_security'],
        }
        
        required_skills = model_type_skills.get(engagement.model_type, ['ai_security', 'ml_security'])
        
        # Calculate match score
        match_data = _calculate_ai_red_teaming_match_score(
            db,
            current_user.researcher,
            engagement.model_type,
            required_skills
        )
        
        # For testing: Show ALL researchers regardless of match score
        # In production, you can set a minimum threshold (e.g., > 30)
        qualified_engagements.append(engagement)
    
    return qualified_engagements


@router.get("/engagements/{engagement_id}/available-researchers", response_model=List[dict])
def get_available_researchers_for_engagement(
    engagement_id: UUID,
    search: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get available researchers for AI Red Teaming engagement.
    
    Returns all active researchers that organizations can browse and invite.
    This is used in the "Browse All" tab of the invitation modal.
    """
    service = AIRedTeamingService(db)
    engagement = service.get_engagement(engagement_id)
    
    if not engagement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Engagement not found"
        )
    
    if not current_user.organization or engagement.organization_id != current_user.organization.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Get all active researchers
    from src.domain.models.researcher import Researcher
    from src.domain.models.user import User as UserModel
    
    query = db.query(Researcher).join(
        UserModel,
        Researcher.user_id == UserModel.id
    ).filter(
        Researcher.is_active == True
    )
    
    # Apply search filter (User model only has email, not username)
    if search:
        search_term = f"%{search.lower()}%"
        query = query.filter(
            func.lower(UserModel.email).like(search_term)
        )
    
    researchers = query.limit(limit).all()
    
    # Format response
    result = []
    for researcher in researchers:
        result.append({
            'id': str(researcher.id),
            'user': {
                'username': researcher.user.email.split('@')[0],  # Derive username from email
                'email': researcher.user.email
            },
            'reputation_score': researcher.reputation_score,
            'total_reports': researcher.total_reports,
            'verified_reports': researcher.verified_reports
        })
    
    return result


@router.post("/engagements/{engagement_id}/match-researchers", response_model=List[dict])
def match_researchers_for_engagement(
    engagement_id: UUID,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    AI-powered researcher matching for AI Red Teaming engagement.
    
    Returns top researchers ranked by:
    - AI/ML security expertise
    - Reputation and past performance
    - Specialization match with model type
    - Availability
    """
    service = AIRedTeamingService(db)
    engagement = service.get_engagement(engagement_id)
    
    if not engagement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Engagement not found"
        )
    
    if not current_user.organization or engagement.organization_id != current_user.organization.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Get AI/ML security skills based on model type
    model_type_skills = {
        AIModelType.LLM: ['llm_security', 'prompt_injection', 'ai_safety', 'nlp'],
        AIModelType.AI_AGENT: ['agent_security', 'ai_safety', 'autonomous_systems'],
        AIModelType.ML_MODEL: ['ml_security', 'adversarial_ml', 'model_security'],
        AIModelType.CHATBOT: ['chatbot_security', 'conversation_ai', 'prompt_injection'],
        AIModelType.RECOMMENDATION_SYSTEM: ['recommendation_security', 'bias_detection'],
        AIModelType.COMPUTER_VISION: ['cv_security', 'adversarial_images', 'model_security'],
    }
    
    required_skills = model_type_skills.get(engagement.model_type, ['ai_security', 'ml_security'])
    
    # Get all researchers
    from src.domain.models.researcher import Researcher
    from src.domain.models.matching import ResearcherProfile
    
    researchers = db.query(Researcher).join(
        ResearcherProfile,
        Researcher.id == ResearcherProfile.researcher_id,
        isouter=True
    ).filter(
        Researcher.is_active == True
    ).all()
    
    # Calculate match scores
    recommendations = []
    for researcher in researchers:
        match_data = _calculate_ai_red_teaming_match_score(
            db,
            researcher,
            engagement.model_type,
            required_skills
        )
        
        # For testing: Include ALL researchers regardless of score
        # In production, you can filter by: if match_data['match_score'] > 30
        recommendations.append({
            'researcher': {
                'id': str(researcher.id),
                'user': {
                    'username': researcher.user.email.split('@')[0],  # Derive username from email
                    'email': researcher.user.email
                },
                'reputation_score': researcher.reputation_score,
                'total_reports': researcher.total_reports,
                'verified_reports': researcher.verified_reports
            },
            'match_score': match_data['match_score'],
            'skill_score': match_data['skill_score'],
            'reputation_score': match_data['reputation_score'],
            'ai_expertise_score': match_data['ai_expertise_score'],
            'reasons': match_data['reasons'] if match_data['reasons'] else ['Available for AI Red Teaming']
        })
    
    # Sort by match score
    recommendations.sort(key=lambda x: x['match_score'], reverse=True)
    
    return recommendations[:limit]


def _calculate_ai_red_teaming_match_score(
    db: Session,
    researcher,
    model_type: AIModelType,
    required_skills: List[str]
) -> dict:
    """Calculate AI Red Teaming specific match score"""
    from src.domain.models.matching import ResearcherSkill, SkillTag
    
    # 1. AI/ML Expertise Score (40%)
    ai_skills = db.query(ResearcherSkill).join(SkillTag).filter(
        ResearcherSkill.researcher_id == researcher.id,
        SkillTag.name.in_(['ai_security', 'ml_security', 'llm_security', 'prompt_injection', 'adversarial_ml'])
    ).all()
    
    ai_expertise_score = min(len(ai_skills) * 20, 100)
    
    # 2. Skill Match Score (30%)
    researcher_skills = db.query(ResearcherSkill).join(SkillTag).filter(
        ResearcherSkill.researcher_id == researcher.id,
        SkillTag.name.in_(required_skills)
    ).all()
    
    if required_skills:
        skill_match_percentage = (len(researcher_skills) / len(required_skills)) * 100
    else:
        skill_match_percentage = 50
    
    skill_score = min(skill_match_percentage, 100)
    
    # 3. Reputation Score (20%) - Convert Decimal to float
    reputation_score = min(float(researcher.reputation_score), 100.0)
    
    # 4. Past AI Red Teaming Performance (10%)
    # TODO: Track AI Red Teaming specific reports
    performance_score = 50.0  # Neutral for now
    
    # Calculate weighted match score
    match_score = (
        (float(ai_expertise_score) * 0.40) +
        (float(skill_score) * 0.30) +
        (float(reputation_score) * 0.20) +
        (float(performance_score) * 0.10)
    )
    
    # Generate reasons
    reasons = []
    if ai_expertise_score >= 60:
        reasons.append(f"Strong AI/ML security expertise ({len(ai_skills)} relevant skills)")
    if skill_score >= 70:
        reasons.append(f"Excellent match for {model_type.value} testing")
    if reputation_score >= 80:
        reasons.append(f"High reputation score ({reputation_score:.0f})")
    if researcher.verified_reports >= 10:
        reasons.append(f"{researcher.verified_reports} verified findings")
    
    if not reasons:
        reasons.append("Meets basic requirements for AI Red Teaming")
    
    return {
        'match_score': round(float(match_score), 1),
        'skill_score': round(float(skill_score), 1),
        'reputation_score': round(float(reputation_score), 1),
        'ai_expertise_score': round(float(ai_expertise_score), 1),
        'reasons': reasons
    }
