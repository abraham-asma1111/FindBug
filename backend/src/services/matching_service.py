"""BountyMatch service - FREQ-16 (Basic researcher matching)."""
from typing import List, Optional, Dict
from uuid import UUID
from datetime import datetime, timedelta

from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from src.domain.models.matching import (
    MatchingRequest, MatchResult, MatchingInvitation,
    ResearcherProfile, ResearcherSkill, SkillTag,
    MatchingAlgorithm, MatchingMetrics, MatchingFeedback
)
from src.domain.models.researcher import Researcher
from src.domain.models.program import BountyProgram
from src.domain.models.report import VulnerabilityReport


class MatchingService:
    """Service for researcher matching - FREQ-16."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_matching_request(
        self,
        organization_id: UUID,
        engagement_type: str,
        criteria: Dict,
        required_skills: Optional[List[str]] = None,
        engagement_id: Optional[UUID] = None
    ) -> MatchingRequest:
        """
        Create matching request - FREQ-16.
        
        Args:
            organization_id: Organization requesting match
            engagement_type: bug_bounty, ptaas, code_review, ai_red_teaming
            criteria: Matching criteria (min_reputation, experience_years, etc.)
            required_skills: List of required skills
            engagement_id: Optional specific engagement ID
        """
        request = MatchingRequest(
            organization_id=organization_id,
            engagement_type=engagement_type,
            engagement_id=engagement_id,
            criteria=criteria,
            required_skills=required_skills or [],
            status="pending"
        )
        
        self.db.add(request)
        self.db.commit()
        self.db.refresh(request)
        
        # Create metrics record
        metrics = MatchingMetrics(request_id=request.id)
        self.db.add(metrics)
        self.db.commit()
        
        return request
    
    def match_researchers(
        self,
        request_id: UUID,
        limit: int = 10
    ) -> List[MatchResult]:
        """
        Match researchers to request - FREQ-16.
        
        Uses basic matching algorithm based on:
        - Skills match
        - Past performance (reputation)
        - Program requirements
        """
        request = self.db.query(MatchingRequest).filter(
            MatchingRequest.id == request_id
        ).first()
        
        if not request:
            raise ValueError("Matching request not found")
        
        # Update status
        request.status = "processing"
        self.db.commit()
        
        # Get criteria
        criteria = request.criteria
        min_reputation = criteria.get("min_reputation", 0)
        min_experience = criteria.get("min_experience_years", 0)
        required_skills = request.required_skills or []
        
        # Query researchers
        query = self.db.query(Researcher).join(
            ResearcherProfile,
            Researcher.id == ResearcherProfile.researcher_id
        ).filter(
            Researcher.reputation_score >= min_reputation,
            ResearcherProfile.experience_years >= min_experience
        )
        
        # Filter by skills if specified
        if required_skills:
            query = query.join(
                ResearcherSkill,
                Researcher.id == ResearcherSkill.researcher_id
            ).join(
                SkillTag,
                ResearcherSkill.tag_id == SkillTag.id
            ).filter(
                SkillTag.name.in_(required_skills)
            ).distinct()
        
        researchers = query.all()
        
        # Calculate match scores
        results = []
        for idx, researcher in enumerate(researchers):
            # Calculate skill score
            skill_score = self._calculate_skill_score(
                researcher.id,
                required_skills
            )
            
            # Reputation score (normalized to 0-100)
            reputation_score = min(researcher.reputation_score, 100)
            
            # Overall match score (weighted average)
            match_score = (skill_score * 0.6) + (reputation_score * 0.4)
            
            result = MatchResult(
                request_id=request_id,
                researcher_id=researcher.id,
                match_score=match_score,
                skill_score=skill_score,
                reputation_score=reputation_score,
                rank=idx + 1
            )
            
            results.append(result)
            self.db.add(result)
        
        # Sort by match score
        results.sort(key=lambda x: x.match_score, reverse=True)
        
        # Update ranks
        for idx, result in enumerate(results[:limit]):
            result.rank = idx + 1
        
        # Update request status and metrics
        request.status = "completed"
        
        metrics = self.db.query(MatchingMetrics).filter(
            MatchingMetrics.request_id == request_id
        ).first()
        
        if metrics:
            metrics.total_candidates = len(results)
            if results:
                metrics.average_match_score = sum(r.match_score for r in results) / len(results)
        
        self.db.commit()
        
        return results[:limit]
    
    def _calculate_skill_score(
        self,
        researcher_id: UUID,
        required_skills: List[str]
    ) -> float:
        """Calculate skill match score."""
        if not required_skills:
            return 100.0
        
        # Get researcher skills
        researcher_skills = self.db.query(ResearcherSkill).join(
            SkillTag
        ).filter(
            ResearcherSkill.researcher_id == researcher_id,
            SkillTag.name.in_(required_skills)
        ).all()
        
        if not researcher_skills:
            return 0.0
        
        # Calculate score based on skill level and experience
        total_score = 0
        for skill in researcher_skills:
            level_score = {
                "beginner": 25,
                "intermediate": 50,
                "advanced": 75,
                "expert": 100
            }.get(skill.level, 0)
            
            # Bonus for verified skills
            if skill.verified:
                level_score *= 1.2
            
            total_score += level_score
        
        # Average score
        avg_score = total_score / len(required_skills)
        
        return min(avg_score, 100.0)
    
    def send_invitations(
        self,
        request_id: UUID,
        researcher_ids: List[UUID],
        message: Optional[str] = None,
        expires_in_days: int = 7
    ) -> List[MatchingInvitation]:
        """Send invitations to matched researchers - FREQ-16."""
        request = self.db.query(MatchingRequest).filter(
            MatchingRequest.id == request_id
        ).first()
        
        if not request:
            raise ValueError("Matching request not found")
        
        expires_at = datetime.utcnow() + timedelta(days=expires_in_days)
        
        invitations = []
        for researcher_id in researcher_ids:
            # Get match score
            match_result = self.db.query(MatchResult).filter(
                MatchResult.request_id == request_id,
                MatchResult.researcher_id == researcher_id
            ).first()
            
            match_score = match_result.match_score if match_result else 0.0
            
            invitation = MatchingInvitation(
                request_id=request_id,
                researcher_id=researcher_id,
                engagement_id=request.engagement_id,
                match_score=match_score,
                message=message,
                expires_at=expires_at,
                status="pending"
            )
            
            invitations.append(invitation)
            self.db.add(invitation)
        
        # Update metrics
        metrics = self.db.query(MatchingMetrics).filter(
            MatchingMetrics.request_id == request_id
        ).first()
        
        if metrics:
            metrics.invited_count = len(invitations)
        
        self.db.commit()
        
        # TODO: Send notification to researchers
        
        return invitations
    
    def respond_to_invitation(
        self,
        invitation_id: UUID,
        researcher_id: UUID,
        accept: bool,
        response_note: Optional[str] = None
    ) -> MatchingInvitation:
        """Researcher responds to invitation - FREQ-16."""
        invitation = self.db.query(MatchingInvitation).filter(
            MatchingInvitation.id == invitation_id,
            MatchingInvitation.researcher_id == researcher_id
        ).first()
        
        if not invitation:
            raise ValueError("Invitation not found")
        
        if invitation.status != "pending":
            raise ValueError("Invitation already responded to")
        
        if datetime.utcnow() > invitation.expires_at:
            invitation.status = "expired"
            self.db.commit()
            raise ValueError("Invitation has expired")
        
        invitation.status = "accepted" if accept else "declined"
        invitation.responded_at = datetime.utcnow()
        invitation.response_note = response_note
        
        # Update metrics
        metrics = self.db.query(MatchingMetrics).filter(
            MatchingMetrics.request_id == invitation.request_id
        ).first()
        
        if metrics:
            if accept:
                metrics.accepted_count += 1
            else:
                metrics.declined_count += 1
            
            # Calculate success rate
            total_responses = metrics.accepted_count + metrics.declined_count
            if total_responses > 0:
                metrics.success_rate = (metrics.accepted_count / total_responses) * 100
        
        self.db.commit()
        self.db.refresh(invitation)
        
        return invitation
    
    def get_researcher_invitations(
        self,
        researcher_id: UUID,
        status: Optional[str] = None
    ) -> List[MatchingInvitation]:
        """Get invitations for researcher - FREQ-16."""
        query = self.db.query(MatchingInvitation).filter(
            MatchingInvitation.researcher_id == researcher_id
        )
        
        if status:
            query = query.filter(MatchingInvitation.status == status)
        
        return query.order_by(MatchingInvitation.sent_at.desc()).all()
    
    def get_matching_results(
        self,
        request_id: UUID
    ) -> List[MatchResult]:
        """Get matching results for request."""
        return self.db.query(MatchResult).filter(
            MatchResult.request_id == request_id
        ).order_by(MatchResult.rank).all()
    
    def submit_feedback(
        self,
        request_id: UUID,
        researcher_id: UUID,
        organization_id: UUID,
        rating: int,
        quality_score: int,
        communication_score: int,
        timeliness_score: int,
        would_work_again: bool,
        comments: Optional[str] = None
    ) -> MatchingFeedback:
        """Submit feedback on match - FREQ-16."""
        feedback = MatchingFeedback(
            request_id=request_id,
            researcher_id=researcher_id,
            organization_id=organization_id,
            rating=rating,
            quality_score=quality_score,
            communication_score=communication_score,
            timeliness_score=timeliness_score,
            would_work_again=would_work_again,
            comments=comments
        )
        
        self.db.add(feedback)
        self.db.commit()
        self.db.refresh(feedback)
        
        return feedback
    
    def get_researcher_recommendations(
        self,
        researcher_id: UUID,
        limit: int = 5
    ) -> List[BountyProgram]:
        """
        Get program recommendations for researcher - FREQ-16.
        
        Based on researcher skills and past performance.
        """
        # Get researcher profile
        profile = self.db.query(ResearcherProfile).filter(
            ResearcherProfile.researcher_id == researcher_id
        ).first()
        
        if not profile:
            return []
        
        # Get researcher skills
        skills = profile.skills or []
        
        # Find programs matching researcher skills
        programs = self.db.query(BountyProgram).filter(
            BountyProgram.status == "public",
            BountyProgram.deleted_at.is_(None)
        ).limit(limit * 2).all()
        
        # Score programs based on match
        scored_programs = []
        for program in programs:
            score = self._calculate_program_match_score(
                researcher_id,
                program.id,
                skills
            )
            scored_programs.append((program, score))
        
        # Sort by score and return top matches
        scored_programs.sort(key=lambda x: x[1], reverse=True)
        
        return [p[0] for p in scored_programs[:limit]]
    
    def _calculate_program_match_score(
        self,
        researcher_id: UUID,
        program_id: UUID,
        researcher_skills: List[str]
    ) -> float:
        """Calculate how well a program matches a researcher."""
        score = 50.0  # Base score
        
        # Check past performance in similar programs
        past_reports = self.db.query(VulnerabilityReport).filter(
            VulnerabilityReport.researcher_id == researcher_id,
            VulnerabilityReport.program_id == program_id
        ).count()
        
        if past_reports > 0:
            score += 20.0  # Bonus for past participation
        
        # TODO: Add more sophisticated matching logic
        # - Program scope match with skills
        # - Reward tier match with researcher level
        # - Program difficulty match with experience
        
        return min(score, 100.0)

    
    # FREQ-32: Advanced PTaaS Matching Methods
    
    def match_researchers_for_ptaas(
        self,
        engagement_id: int,
        methodology: str,
        required_skills: List[str],
        compliance_requirements: Optional[List[str]] = None,
        team_size: int = 1,
        limit: int = 20
    ) -> List[Tuple[Researcher, Dict]]:
        """
        Advanced researcher matching for PTaaS engagements - FREQ-32.
        
        Matches based on:
        - Skills match with methodology
        - Reputation score
        - Past PTaaS performance
        - Vulnerability expertise
        - Availability
        
        Returns list of (researcher, match_details) tuples
        """
        # Get all active researchers with profiles
        researchers = self.db.query(Researcher).join(
            ResearcherProfile,
            Researcher.id == ResearcherProfile.researcher_id
        ).filter(
            Researcher.is_active == True
        ).all()
        
        scored_researchers = []
        
        for researcher in researchers:
            # Calculate comprehensive match score
            match_details = self._calculate_ptaas_match_score(
                researcher,
                methodology,
                required_skills,
                compliance_requirements
            )
            
            if match_details['overall_score'] > 0:
                scored_researchers.append((researcher, match_details))
        
        # Sort by overall score
        scored_researchers.sort(key=lambda x: x[1]['overall_score'], reverse=True)
        
        return scored_researchers[:limit]
    
    def _calculate_ptaas_match_score(
        self,
        researcher: Researcher,
        methodology: str,
        required_skills: List[str],
        compliance_requirements: Optional[List[str]] = None
    ) -> Dict:
        """
        Calculate comprehensive PTaaS match score - FREQ-32.
        
        Scoring factors:
        - Skills match (30%)
        - Reputation (20%)
        - Past PTaaS performance (20%)
        - Vulnerability expertise (20%)
        - Availability (10%)
        """
        profile = researcher.profile[0] if researcher.profile else None
        
        if not profile:
            return {
                'overall_score': 0,
                'skill_score': 0,
                'reputation_score': 0,
                'performance_score': 0,
                'expertise_score': 0,
                'availability_score': 0,
                'details': 'No profile found'
            }
        
        # 1. Skills Match Score (30%)
        skill_score = self._calculate_methodology_skill_score(
            researcher.id,
            methodology,
            required_skills
        )
        
        # 2. Reputation Score (20%)
        reputation_score = min(researcher.reputation_score, 100)
        
        # 3. Past PTaaS Performance Score (20%)
        performance_score = self._calculate_ptaas_performance_score(researcher.id)
        
        # 4. Vulnerability Expertise Score (20%)
        expertise_score = self._calculate_vulnerability_expertise_score(
            researcher.id,
            methodology
        )
        
        # 5. Availability Score (10%)
        availability_score = self._calculate_availability_score(profile)
        
        # Calculate weighted overall score
        overall_score = (
            (skill_score * 0.30) +
            (reputation_score * 0.20) +
            (performance_score * 0.20) +
            (expertise_score * 0.20) +
            (availability_score * 0.10)
        )
        
        return {
            'overall_score': round(overall_score, 2),
            'skill_score': round(skill_score, 2),
            'reputation_score': round(reputation_score, 2),
            'performance_score': round(performance_score, 2),
            'expertise_score': round(expertise_score, 2),
            'availability_score': round(availability_score, 2),
            'details': {
                'methodology': methodology,
                'experience_years': profile.experience_years,
                'current_workload': profile.current_workload,
                'timezone': profile.timezone
            }
        }
    
    def _calculate_methodology_skill_score(
        self,
        researcher_id: UUID,
        methodology: str,
        required_skills: List[str]
    ) -> float:
        """
        Calculate skill match score for specific methodology - FREQ-32.
        
        Considers:
        - Methodology-specific skills (OWASP, PTES, etc.)
        - Required technical skills
        - Skill level and verification
        """
        # Methodology skill mapping
        methodology_skills = {
            'OWASP': ['web_security', 'api_security', 'injection', 'xss', 'authentication'],
            'PTES': ['network_security', 'penetration_testing', 'exploitation', 'post_exploitation'],
            'NIST': ['compliance', 'risk_assessment', 'security_controls'],
            'OSSTMM': ['security_testing', 'operational_security', 'trust_analysis'],
            'ISSAF': ['information_security', 'security_assessment', 'vulnerability_analysis']
        }
        
        # Get methodology-specific skills
        methodology_required = methodology_skills.get(methodology, [])
        all_required = list(set(required_skills + methodology_required))
        
        if not all_required:
            return 100.0
        
        # Get researcher skills
        researcher_skills = self.db.query(ResearcherSkill).join(
            SkillTag
        ).filter(
            ResearcherSkill.researcher_id == researcher_id
        ).all()
        
        if not researcher_skills:
            return 0.0
        
        # Create skill map
        skill_map = {}
        for rs in researcher_skills:
            skill_map[rs.skill_tag.name.lower()] = rs
        
        # Calculate match score
        matched_skills = 0
        total_score = 0
        
        for required_skill in all_required:
            skill_key = required_skill.lower()
            if skill_key in skill_map:
                rs = skill_map[skill_key]
                
                # Base score by level
                level_scores = {
                    'beginner': 40,
                    'intermediate': 60,
                    'advanced': 80,
                    'expert': 100
                }
                score = level_scores.get(rs.level, 0)
                
                # Bonus for verification
                if rs.verified:
                    score = min(score * 1.25, 100)
                
                # Bonus for experience
                if rs.years_experience >= 3:
                    score = min(score * 1.15, 100)
                
                total_score += score
                matched_skills += 1
        
        if matched_skills == 0:
            return 0.0
        
        # Calculate percentage of required skills matched
        match_percentage = (matched_skills / len(all_required)) * 100
        avg_skill_score = total_score / matched_skills
        
        # Weighted score: 60% match percentage, 40% skill quality
        final_score = (match_percentage * 0.6) + (avg_skill_score * 0.4)
        
        return min(final_score, 100.0)
    
    def _calculate_ptaas_performance_score(
        self,
        researcher_id: UUID
    ) -> float:
        """
        Calculate past PTaaS performance score - FREQ-32.
        
        Based on:
        - Number of completed PTaaS engagements
        - Quality of findings
        - Feedback ratings
        - Success rate
        """
        # Get past PTaaS engagements
        past_engagements = self.db.query(PTaaSEngagement).filter(
            PTaaSEngagement.assigned_researchers.contains([str(researcher_id)]),
            PTaaSEngagement.status == 'COMPLETED'
        ).all()
        
        if not past_engagements:
            return 50.0  # Neutral score for no history
        
        # Calculate findings quality
        total_findings = 0
        critical_findings = 0
        high_findings = 0
        
        for engagement in past_engagements:
            findings = self.db.query(PTaaSFinding).filter(
                PTaaSFinding.engagement_id == engagement.id,
                PTaaSFinding.discovered_by == researcher_id
            ).all()
            
            total_findings += len(findings)
            for finding in findings:
                if finding.severity == 'Critical':
                    critical_findings += 1
                elif finding.severity == 'High':
                    high_findings += 1
        
        # Base score from engagement count
        engagement_score = min(len(past_engagements) * 10, 40)
        
        # Findings quality score
        if total_findings > 0:
            quality_score = (
                (critical_findings * 10) +
                (high_findings * 5) +
                (total_findings * 2)
            )
            quality_score = min(quality_score, 40)
        else:
            quality_score = 0
        
        # Get feedback ratings
        feedback_records = self.db.query(MatchingFeedback).filter(
            MatchingFeedback.researcher_id == researcher_id
        ).all()
        
        if feedback_records:
            avg_rating = sum(f.rating for f in feedback_records) / len(feedback_records)
            feedback_score = (avg_rating / 5) * 20
        else:
            feedback_score = 10  # Neutral
        
        total_score = engagement_score + quality_score + feedback_score
        
        return min(total_score, 100.0)
    
    def _calculate_vulnerability_expertise_score(
        self,
        researcher_id: UUID,
        methodology: str
    ) -> float:
        """
        Calculate vulnerability expertise score - FREQ-32.
        
        Based on:
        - Types of vulnerabilities found
        - Severity distribution
        - Unique vulnerability types
        - Recent activity
        """
        # Get all vulnerability reports
        reports = self.db.query(VulnerabilityReport).filter(
            VulnerabilityReport.researcher_id == researcher_id,
            VulnerabilityReport.status.in_(['TRIAGED', 'RESOLVED', 'ACCEPTED'])
        ).all()
        
        if not reports:
            return 30.0  # Low score for no history
        
        # Analyze severity distribution
        severity_counts = {
            'Critical': 0,
            'High': 0,
            'Medium': 0,
            'Low': 0
        }
        
        vulnerability_types = set()
        
        for report in reports:
            severity = report.severity
            if severity in severity_counts:
                severity_counts[severity] += 1
            
            # Track unique vulnerability types
            if report.vulnerability_type:
                vulnerability_types.add(report.vulnerability_type)
        
        # Calculate severity score
        severity_score = (
            (severity_counts['Critical'] * 10) +
            (severity_counts['High'] * 5) +
            (severity_counts['Medium'] * 2) +
            (severity_counts['Low'] * 1)
        )
        severity_score = min(severity_score, 50)
        
        # Diversity score (unique vulnerability types)
        diversity_score = min(len(vulnerability_types) * 5, 30)
        
        # Volume score
        volume_score = min(len(reports) * 2, 20)
        
        total_score = severity_score + diversity_score + volume_score
        
        return min(total_score, 100.0)
    
    def _calculate_availability_score(
        self,
        profile: ResearcherProfile
    ) -> float:
        """
        Calculate availability score - FREQ-32.
        
        Based on:
        - Current workload
        - Available hours per week
        - Response time history
        """
        # Workload score (inverse - lower workload = higher score)
        if profile.current_workload == 0:
            workload_score = 100
        elif profile.current_workload <= 2:
            workload_score = 80
        elif profile.current_workload <= 4:
            workload_score = 50
        else:
            workload_score = 20
        
        # Available hours score
        if profile.availability_hours:
            if profile.availability_hours >= 40:
                hours_score = 100
            elif profile.availability_hours >= 20:
                hours_score = 70
            elif profile.availability_hours >= 10:
                hours_score = 40
            else:
                hours_score = 20
        else:
            hours_score = 50  # Neutral if not specified
        
        # Weighted average
        availability_score = (workload_score * 0.6) + (hours_score * 0.4)
        
        return availability_score
    
    def auto_assign_researchers_to_ptaas(
        self,
        engagement_id: int,
        team_size: int,
        auto_invite: bool = False
    ) -> List[Dict]:
        """
        Automatically assign best-matched researchers to PTaaS engagement - FREQ-32.
        
        Args:
            engagement_id: PTaaS engagement ID
            team_size: Number of researchers needed
            auto_invite: Whether to automatically send invitations
        
        Returns:
            List of assigned researcher details with match scores
        """
        # Get engagement details
        engagement = self.db.query(PTaaSEngagement).filter(
            PTaaSEngagement.id == engagement_id
        ).first()
        
        if not engagement:
            raise ValueError("PTaaS engagement not found")
        
        # Extract matching criteria from engagement
        methodology = engagement.testing_methodology
        required_skills = engagement.scope.get('required_skills', []) if engagement.scope else []
        compliance_requirements = engagement.compliance_requirements
        
        # Find best matches
        matches = self.match_researchers_for_ptaas(
            engagement_id=engagement_id,
            methodology=methodology,
            required_skills=required_skills,
            compliance_requirements=compliance_requirements,
            team_size=team_size,
            limit=team_size * 3  # Get more candidates than needed
        )
        
        # Select top matches
        selected_researchers = []
        for researcher, match_details in matches[:team_size]:
            selected_researchers.append({
                'researcher_id': str(researcher.id),
                'researcher_name': f"{researcher.user.first_name} {researcher.user.last_name}",
                'match_score': match_details['overall_score'],
                'skill_score': match_details['skill_score'],
                'reputation_score': match_details['reputation_score'],
                'performance_score': match_details['performance_score'],
                'expertise_score': match_details['expertise_score'],
                'availability_score': match_details['availability_score'],
                'details': match_details['details']
            })
        
        # Update engagement with assigned researchers
        researcher_ids = [r['researcher_id'] for r in selected_researchers]
        engagement.assigned_researchers = researcher_ids
        engagement.team_size = len(researcher_ids)
        self.db.commit()
        
        # Create matching request for tracking
        request = MatchingRequest(
            organization_id=engagement.organization_id,
            engagement_type='ptaas',
            engagement_id=engagement_id,
            criteria={
                'methodology': methodology,
                'team_size': team_size,
                'auto_assigned': True
            },
            required_skills=required_skills,
            status='completed'
        )
        self.db.add(request)
        self.db.commit()
        
        # Send invitations if requested
        if auto_invite:
            self.send_invitations(
                request_id=request.id,
                researcher_ids=[UUID(r['researcher_id']) for r in selected_researchers],
                message=f"You have been matched to PTaaS engagement: {engagement.name}"
            )
        
        return selected_researchers
    
    def get_researcher_ptaas_recommendations(
        self,
        researcher_id: UUID,
        limit: int = 5
    ) -> List[Dict]:
        """
        Get PTaaS engagement recommendations for researcher - FREQ-32.
        
        Recommends engagements based on researcher's skills and experience.
        """
        # Get researcher profile
        researcher = self.db.query(Researcher).filter(
            Researcher.id == researcher_id
        ).first()
        
        if not researcher or not researcher.profile:
            return []
        
        profile = researcher.profile[0]
        
        # Get available PTaaS engagements
        available_engagements = self.db.query(PTaaSEngagement).filter(
            PTaaSEngagement.status.in_(['DRAFT', 'PENDING_APPROVAL', 'ACTIVE']),
            or_(
                PTaaSEngagement.assigned_researchers.is_(None),
                func.jsonb_array_length(PTaaSEngagement.assigned_researchers) < PTaaSEngagement.team_size
            )
        ).all()
        
        # Score each engagement
        scored_engagements = []
        for engagement in available_engagements:
            match_details = self._calculate_ptaas_match_score(
                researcher,
                engagement.testing_methodology,
                engagement.scope.get('required_skills', []) if engagement.scope else [],
                engagement.compliance_requirements
            )
            
            if match_details['overall_score'] >= 50:  # Minimum threshold
                scored_engagements.append({
                    'engagement_id': engagement.id,
                    'engagement_name': engagement.name,
                    'organization_id': engagement.organization_id,
                    'methodology': engagement.testing_methodology,
                    'duration_days': engagement.duration_days,
                    'base_price': float(engagement.base_price),
                    'match_score': match_details['overall_score'],
                    'match_details': match_details
                })
        
        # Sort by match score
        scored_engagements.sort(key=lambda x: x['match_score'], reverse=True)
        
        return scored_engagements[:limit]

    
    # FREQ-33: Configuration and Approval Methods
    
    def create_matching_configuration(
        self,
        organization_id: UUID,
        config_data: Dict
    ) -> 'MatchingConfiguration':
        """
        Create or update matching configuration for organization - FREQ-33.
        
        Allows organizations to customize:
        - Scoring weights
        - Minimum thresholds
        - Approval requirements
        - Preferences
        """
        from src.domain.models.matching import MatchingConfiguration
        
        # Check if configuration exists
        existing = self.db.query(MatchingConfiguration).filter(
            MatchingConfiguration.organization_id == organization_id
        ).first()
        
        if existing:
            # Update existing configuration
            for key, value in config_data.items():
                if hasattr(existing, key):
                    setattr(existing, key, value)
            existing.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(existing)
            return existing
        else:
            # Create new configuration
            config = MatchingConfiguration(
                organization_id=organization_id,
                **config_data
            )
            self.db.add(config)
            self.db.commit()
            self.db.refresh(config)
            return config
    
    def get_matching_configuration(
        self,
        organization_id: UUID
    ) -> Optional['MatchingConfiguration']:
        """Get matching configuration for organization - FREQ-33."""
        from src.domain.models.matching import MatchingConfiguration
        
        return self.db.query(MatchingConfiguration).filter(
            MatchingConfiguration.organization_id == organization_id
        ).first()
    
    def match_with_custom_criteria(
        self,
        organization_id: UUID,
        engagement_id: int,
        methodology: str,
        required_skills: List[str],
        compliance_requirements: Optional[List[str]] = None,
        limit: int = 20
    ) -> List[Tuple[Researcher, Dict]]:
        """
        Match researchers using organization's custom criteria - FREQ-33.
        
        Uses configured weights and thresholds instead of defaults.
        """
        from src.domain.models.matching import MatchingConfiguration
        
        # Get organization configuration
        config = self.get_matching_configuration(organization_id)
        
        if not config:
            # Use default matching if no configuration
            return self.match_researchers_for_ptaas(
                engagement_id=engagement_id,
                methodology=methodology,
                required_skills=required_skills,
                compliance_requirements=compliance_requirements,
                team_size=1,
                limit=limit
            )
        
        # Get all active researchers
        researchers = self.db.query(Researcher).join(
            ResearcherProfile,
            Researcher.id == ResearcherProfile.researcher_id
        ).filter(
            Researcher.is_active == True,
            Researcher.reputation_score >= config.min_reputation
        ).all()
        
        # Apply experience filter
        if config.min_experience_years > 0:
            researchers = [
                r for r in researchers
                if r.profile and r.profile[0].experience_years >= config.min_experience_years
            ]
        
        # Apply exclusions
        if config.excluded_researchers:
            excluded_ids = [UUID(rid) for rid in config.excluded_researchers]
            researchers = [r for r in researchers if r.id not in excluded_ids]
        
        scored_researchers = []
        
        for researcher in researchers:
            # Calculate scores
            match_details = self._calculate_ptaas_match_score(
                researcher,
                methodology,
                required_skills,
                compliance_requirements
            )
            
            # Apply custom weights
            overall_score = (
                (match_details['skill_score'] * float(config.skill_weight)) +
                (match_details['reputation_score'] * float(config.reputation_weight)) +
                (match_details['performance_score'] * float(config.performance_weight)) +
                (match_details['expertise_score'] * float(config.expertise_weight)) +
                (match_details['availability_score'] * float(config.availability_weight))
            )
            
            match_details['overall_score'] = round(overall_score, 2)
            match_details['custom_weights_applied'] = True
            
            # Apply minimum threshold
            if overall_score >= float(config.min_overall_score):
                scored_researchers.append((researcher, match_details))
        
        # Apply preferences (boost preferred researchers)
        if config.preferred_researchers:
            preferred_ids = [UUID(rid) for rid in config.preferred_researchers]
            for i, (researcher, details) in enumerate(scored_researchers):
                if researcher.id in preferred_ids:
                    details['overall_score'] = min(details['overall_score'] * 1.1, 100.0)
                    details['preferred'] = True
        
        # Sort by score
        scored_researchers.sort(key=lambda x: x[1]['overall_score'], reverse=True)
        
        return scored_researchers[:limit]
    
    def propose_researcher_assignment(
        self,
        engagement_id: int,
        engagement_type: str,
        researcher_id: UUID,
        organization_id: UUID,
        match_score: float,
        match_details: Dict,
        proposed_by: Optional[UUID] = None,
        timeout_hours: int = 48
    ) -> 'ResearcherAssignment':
        """
        Propose researcher assignment for approval - FREQ-33.
        
        Creates assignment proposal that requires approval.
        """
        from src.domain.models.matching import ResearcherAssignment, MatchingConfiguration
        
        # Get configuration to check auto-approval
        config = self.get_matching_configuration(organization_id)
        
        # Determine initial status
        if config and config.auto_approve_threshold:
            if match_score >= float(config.auto_approve_threshold):
                status = "approved"
                reviewed_at = datetime.utcnow()
                review_notes = "Auto-approved based on threshold"
            else:
                status = "pending"
                reviewed_at = None
                review_notes = None
        elif config and not config.require_approval:
            status = "approved"
            reviewed_at = datetime.utcnow()
            review_notes = "Auto-approved (approval not required)"
        else:
            status = "pending"
            reviewed_at = None
            review_notes = None
        
        # Create assignment
        assignment = ResearcherAssignment(
            engagement_id=engagement_id,
            engagement_type=engagement_type,
            researcher_id=researcher_id,
            organization_id=organization_id,
            match_score=match_score,
            match_details=match_details,
            status=status,
            proposed_by=proposed_by,
            reviewed_at=reviewed_at,
            review_notes=review_notes,
            expires_at=datetime.utcnow() + timedelta(hours=timeout_hours)
        )
        
        self.db.add(assignment)
        self.db.commit()
        self.db.refresh(assignment)
        
        return assignment
    
    def approve_researcher_assignment(
        self,
        assignment_id: UUID,
        approved_by: UUID,
        notes: Optional[str] = None
    ) -> 'ResearcherAssignment':
        """
        Approve researcher assignment - FREQ-33.
        
        Organization or admin approves proposed assignment.
        """
        from src.domain.models.matching import ResearcherAssignment
        
        assignment = self.db.query(ResearcherAssignment).filter(
            ResearcherAssignment.id == assignment_id
        ).first()
        
        if not assignment:
            raise ValueError("Assignment not found")
        
        if assignment.status != "pending":
            raise ValueError(f"Assignment is not pending (status: {assignment.status})")
        
        if datetime.utcnow() > assignment.expires_at:
            assignment.status = "expired"
            self.db.commit()
            raise ValueError("Assignment has expired")
        
        assignment.status = "approved"
        assignment.reviewed_by = approved_by
        assignment.reviewed_at = datetime.utcnow()
        assignment.review_notes = notes
        
        self.db.commit()
        self.db.refresh(assignment)
        
        # TODO: Trigger actual assignment to engagement
        # TODO: Send notification to researcher
        
        return assignment
    
    def reject_researcher_assignment(
        self,
        assignment_id: UUID,
        rejected_by: UUID,
        reason: str
    ) -> 'ResearcherAssignment':
        """
        Reject researcher assignment - FREQ-33.
        
        Organization or admin rejects proposed assignment.
        """
        from src.domain.models.matching import ResearcherAssignment
        
        assignment = self.db.query(ResearcherAssignment).filter(
            ResearcherAssignment.id == assignment_id
        ).first()
        
        if not assignment:
            raise ValueError("Assignment not found")
        
        if assignment.status != "pending":
            raise ValueError(f"Assignment is not pending (status: {assignment.status})")
        
        assignment.status = "rejected"
        assignment.reviewed_by = rejected_by
        assignment.reviewed_at = datetime.utcnow()
        assignment.review_notes = reason
        
        self.db.commit()
        self.db.refresh(assignment)
        
        return assignment
    
    def get_pending_assignments(
        self,
        organization_id: UUID
    ) -> List['ResearcherAssignment']:
        """
        Get pending assignments for organization - FREQ-33.
        
        Returns assignments awaiting approval.
        """
        from src.domain.models.matching import ResearcherAssignment
        
        return self.db.query(ResearcherAssignment).filter(
            ResearcherAssignment.organization_id == organization_id,
            ResearcherAssignment.status == "pending",
            ResearcherAssignment.expires_at > datetime.utcnow()
        ).order_by(ResearcherAssignment.proposed_at.desc()).all()
    
    def get_assignment_by_id(
        self,
        assignment_id: UUID
    ) -> Optional['ResearcherAssignment']:
        """Get assignment by ID - FREQ-33."""
        from src.domain.models.matching import ResearcherAssignment
        
        return self.db.query(ResearcherAssignment).filter(
            ResearcherAssignment.id == assignment_id
        ).first()
    
    def bulk_approve_assignments(
        self,
        assignment_ids: List[UUID],
        approved_by: UUID,
        notes: Optional[str] = None
    ) -> List['ResearcherAssignment']:
        """
        Bulk approve multiple assignments - FREQ-33.
        
        Useful for approving entire teams at once.
        """
        approved_assignments = []
        
        for assignment_id in assignment_ids:
            try:
                assignment = self.approve_researcher_assignment(
                    assignment_id=assignment_id,
                    approved_by=approved_by,
                    notes=notes
                )
                approved_assignments.append(assignment)
            except ValueError as e:
                # Log error but continue with other assignments
                print(f"Failed to approve {assignment_id}: {str(e)}")
                continue
        
        return approved_assignments
    
    def expire_old_assignments(self) -> int:
        """
        Expire assignments past their timeout - FREQ-33.
        
        Should be run periodically (e.g., via cron job).
        Returns number of expired assignments.
        """
        from src.domain.models.matching import ResearcherAssignment
        
        expired_count = self.db.query(ResearcherAssignment).filter(
            ResearcherAssignment.status == "pending",
            ResearcherAssignment.expires_at <= datetime.utcnow()
        ).update(
            {
                "status": "expired",
                "reviewed_at": datetime.utcnow(),
                "review_notes": "Automatically expired due to timeout"
            },
            synchronize_session=False
        )
        
        self.db.commit()
        
        return expired_count


    # FREQ-39: Personalized Recommendations for Researchers
    
    def get_personalized_recommendations(
        self,
        researcher_id: int,
        include_bug_bounty: bool = True,
        include_ptaas: bool = True,
        limit_per_type: int = 10
    ) -> Dict[str, Any]:
        """
        Get comprehensive personalized recommendations - FREQ-39.
        
        Provides researchers with:
        - Active bug bounty programs matching their profile
        - PTaaS opportunities matching their expertise
        - Personalized match scores and reasons
        """
        recommendations = {
            'researcher_id': researcher_id,
            'generated_at': datetime.utcnow().isoformat(),
            'bug_bounty_programs': [],
            'ptaas_opportunities': [],
            'summary': {}
        }
        
        # Get researcher profile
        researcher = self.db.query(Researcher).filter(
            Researcher.id == researcher_id
        ).first()
        
        if not researcher:
            return recommendations
        
        # Get bug bounty recommendations
        if include_bug_bounty:
            recommendations['bug_bounty_programs'] = self._get_enhanced_program_recommendations(
                researcher,
                limit_per_type
            )
        
        # Get PTaaS recommendations
        if include_ptaas:
            recommendations['ptaas_opportunities'] = self._get_enhanced_ptaas_recommendations(
                researcher,
                limit_per_type
            )
        
        # Generate summary
        recommendations['summary'] = {
            'total_bug_bounty': len(recommendations['bug_bounty_programs']),
            'total_ptaas': len(recommendations['ptaas_opportunities']),
            'high_match_count': len([
                r for r in recommendations['bug_bounty_programs'] + recommendations['ptaas_opportunities']
                if r.get('match_score', 0) >= 80
            ]),
            'researcher_skills': researcher.profile[0].skills if researcher.profile else [],
            'researcher_reputation': researcher.reputation_score
        }
        
        return recommendations
    
    def _get_enhanced_program_recommendations(
        self,
        researcher: Researcher,
        limit: int
    ) -> List[Dict]:
        """Enhanced bug bounty program recommendations - FREQ-39"""
        profile = researcher.profile[0] if researcher.profile else None
        if not profile:
            return []
        
        # Get active public programs
        programs = self.db.query(BountyProgram).filter(
            BountyProgram.status == 'public',
            BountyProgram.deleted_at.is_(None)
        ).all()
        
        scored_programs = []
        for program in programs:
            # Calculate comprehensive match score
            match_details = self._calculate_comprehensive_program_match(
                researcher,
                program
            )
            
            if match_details['overall_score'] >= 40:  # Minimum threshold
                scored_programs.append({
                    'program_id': program.id,
                    'program_name': program.name,
                    'organization_id': program.organization_id,
                    'match_score': match_details['overall_score'],
                    'match_reasons': match_details['reasons'],
                    'reward_range': {
                        'min': float(program.min_bounty) if program.min_bounty else 0,
                        'max': float(program.max_bounty) if program.max_bounty else 0
                    },
                    'scope_summary': program.scope_summary if hasattr(program, 'scope_summary') else None,
                    'difficulty_level': match_details.get('difficulty_level', 'Medium'),
                    'estimated_time': match_details.get('estimated_time', 'Unknown'),
                    'recommendation_type': 'bug_bounty'
                })
        
        # Sort by match score
        scored_programs.sort(key=lambda x: x['match_score'], reverse=True)
        
        return scored_programs[:limit]
    
    def _get_enhanced_ptaas_recommendations(
        self,
        researcher: Researcher,
        limit: int
    ) -> List[Dict]:
        """Enhanced PTaaS opportunity recommendations - FREQ-39"""
        profile = researcher.profile[0] if researcher.profile else None
        if not profile:
            return []
        
        # Get available PTaaS engagements
        from backend.src.domain.models.ptaas import PTaaSEngagement
        
        engagements = self.db.query(PTaaSEngagement).filter(
            PTaaSEngagement.status.in_(['DRAFT', 'PENDING_APPROVAL', 'ACTIVE']),
            or_(
                PTaaSEngagement.assigned_researchers.is_(None),
                func.jsonb_array_length(PTaaSEngagement.assigned_researchers) < PTaaSEngagement.team_size
            )
        ).all()
        
        scored_engagements = []
        for engagement in engagements:
            # Calculate comprehensive match score
            match_details = self._calculate_comprehensive_ptaas_match(
                researcher,
                engagement
            )
            
            if match_details['overall_score'] >= 50:  # Minimum threshold
                scored_engagements.append({
                    'engagement_id': engagement.id,
                    'engagement_name': engagement.name,
                    'organization_id': engagement.organization_id,
                    'methodology': engagement.testing_methodology,
                    'match_score': match_details['overall_score'],
                    'match_reasons': match_details['reasons'],
                    'duration_days': engagement.duration_days,
                    'pricing_model': engagement.pricing_model,
                    'estimated_compensation': float(engagement.base_price / engagement.team_size) if engagement.team_size > 0 else 0,
                    'team_size': engagement.team_size,
                    'start_date': engagement.start_date.isoformat() if engagement.start_date else None,
                    'compliance_requirements': engagement.compliance_requirements,
                    'difficulty_level': match_details.get('difficulty_level', 'Medium'),
                    'recommendation_type': 'ptaas'
                })
        
        # Sort by match score
        scored_engagements.sort(key=lambda x: x['match_score'], reverse=True)
        
        return scored_engagements[:limit]
    
    def _calculate_comprehensive_program_match(
        self,
        researcher: Researcher,
        program: BountyProgram
    ) -> Dict[str, Any]:
        """Calculate comprehensive match score for bug bounty program - FREQ-39"""
        profile = researcher.profile[0] if researcher.profile else None
        if not profile:
            return {'overall_score': 0, 'reasons': []}
        
        score = 0
        reasons = []
        
        # Skills match (30 points)
        researcher_skills = set(profile.skills or [])
        program_skills = set(program.required_skills or [])
        
        if program_skills:
            skill_match = len(researcher_skills & program_skills) / len(program_skills)
            skill_score = skill_match * 30
            score += skill_score
            if skill_score >= 20:
                reasons.append(f"Strong skills match ({int(skill_match * 100)}%)")
        
        # Reputation match (20 points)
        if researcher.reputation_score >= 80:
            score += 20
            reasons.append("High reputation score")
        elif researcher.reputation_score >= 60:
            score += 15
            reasons.append("Good reputation score")
        elif researcher.reputation_score >= 40:
            score += 10
        
        # Past performance (20 points)
        past_reports = self.db.query(VulnerabilityReport).filter(
            VulnerabilityReport.researcher_id == researcher.id,
            VulnerabilityReport.program_id == program.id
        ).count()
        
        if past_reports > 0:
            score += 20
            reasons.append(f"Previous participation ({past_reports} reports)")
        
        # Experience level match (15 points)
        if profile.experience_years >= 5:
            score += 15
            reasons.append("Experienced researcher")
        elif profile.experience_years >= 3:
            score += 10
        elif profile.experience_years >= 1:
            score += 5
        
        # Reward tier match (15 points)
        if program.max_bounty:
            if program.max_bounty >= 10000:
                score += 15 if researcher.reputation_score >= 70 else 5
                if researcher.reputation_score >= 70:
                    reasons.append("High-value program match")
            elif program.max_bounty >= 5000:
                score += 10
            else:
                score += 5
        
        # Determine difficulty level
        difficulty = 'Medium'
        if program.max_bounty and program.max_bounty >= 10000:
            difficulty = 'High'
        elif program.max_bounty and program.max_bounty < 1000:
            difficulty = 'Low'
        
        return {
            'overall_score': min(score, 100),
            'reasons': reasons,
            'difficulty_level': difficulty,
            'estimated_time': '1-2 weeks'
        }
    
    def _calculate_comprehensive_ptaas_match(
        self,
        researcher: Researcher,
        engagement: 'PTaaSEngagement'
    ) -> Dict[str, Any]:
        """Calculate comprehensive match score for PTaaS engagement - FREQ-39"""
        profile = researcher.profile[0] if researcher.profile else None
        if not profile:
            return {'overall_score': 0, 'reasons': []}
        
        score = 0
        reasons = []
        
        # Methodology skills match (30 points)
        methodology_skills = {
            'OWASP': ['web_security', 'api_security', 'authentication', 'authorization'],
            'PTES': ['network_security', 'penetration_testing', 'exploitation'],
            'NIST': ['compliance', 'risk_assessment', 'security_controls']
        }
        
        required_skills = methodology_skills.get(engagement.testing_methodology, [])
        researcher_skills = set(profile.skills or [])
        
        if required_skills:
            skill_match = len(set(required_skills) & researcher_skills) / len(required_skills)
            skill_score = skill_match * 30
            score += skill_score
            if skill_score >= 20:
                reasons.append(f"{engagement.testing_methodology} methodology match")
        
        # Reputation (20 points)
        if researcher.reputation_score >= 80:
            score += 20
            reasons.append("High reputation for PTaaS")
        elif researcher.reputation_score >= 60:
            score += 15
        elif researcher.reputation_score >= 40:
            score += 10
        
        # PTaaS experience (20 points)
        from backend.src.domain.models.ptaas import PTaaSFinding
        past_ptaas = self.db.query(PTaaSFinding).filter(
            PTaaSFinding.discovered_by == researcher.id
        ).count()
        
        if past_ptaas >= 10:
            score += 20
            reasons.append(f"Extensive PTaaS experience ({past_ptaas} findings)")
        elif past_ptaas >= 5:
            score += 15
            reasons.append("Good PTaaS experience")
        elif past_ptaas >= 1:
            score += 10
        
        # Compliance knowledge (15 points)
        if engagement.compliance_requirements:
            compliance_skills = {'pci_dss', 'hipaa', 'gdpr', 'sox', 'iso27001'}
            if compliance_skills & researcher_skills:
                score += 15
                reasons.append("Compliance expertise")
        
        # Availability (15 points)
        if profile.hours_available_per_week >= 20:
            score += 15
            reasons.append("High availability")
        elif profile.hours_available_per_week >= 10:
            score += 10
        elif profile.hours_available_per_week >= 5:
            score += 5
        
        # Determine difficulty
        difficulty = 'Medium'
        if engagement.testing_methodology in ['PTES', 'NIST']:
            difficulty = 'High'
        elif engagement.duration_days and engagement.duration_days > 30:
            difficulty = 'High'
        
        return {
            'overall_score': min(score, 100),
            'reasons': reasons,
            'difficulty_level': difficulty,
            'estimated_time': f"{engagement.duration_days} days" if engagement.duration_days else 'Unknown'
        }


    # FREQ-40: BountyMatch Performance Metrics
    
    def get_matching_performance_metrics(
        self,
        organization_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get comprehensive BountyMatch performance metrics - FREQ-40.
        
        Tracks:
        - Match success rate
        - Researcher acceptance rate
        - Average match score
        - Time to assignment
        - Researcher satisfaction
        """
        from backend.src.domain.models.matching import ResearcherAssignment
        
        # Default to last 30 days if no date range specified
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=30)
        
        # Base query for assignments
        query = self.db.query(ResearcherAssignment).filter(
            ResearcherAssignment.created_at >= start_date,
            ResearcherAssignment.created_at <= end_date
        )
        
        # Filter by organization if specified
        if organization_id:
            query = query.filter(ResearcherAssignment.organization_id == organization_id)
        
        assignments = query.all()
        
        # Calculate metrics
        total_assignments = len(assignments)
        approved_assignments = len([a for a in assignments if a.status == 'APPROVED'])
        rejected_assignments = len([a for a in assignments if a.status == 'REJECTED'])
        pending_assignments = len([a for a in assignments if a.status == 'PROPOSED'])
        
        # Match success rate (approved / total)
        match_success_rate = (approved_assignments / total_assignments * 100) if total_assignments > 0 else 0
        
        # Researcher acceptance rate (approved / (approved + rejected))
        total_decided = approved_assignments + rejected_assignments
        acceptance_rate = (approved_assignments / total_decided * 100) if total_decided > 0 else 0
        
        # Average match score
        match_scores = [a.match_score for a in assignments if a.match_score]
        avg_match_score = sum(match_scores) / len(match_scores) if match_scores else 0
        
        # Time to assignment (from proposed to approved)
        assignment_times = []
        for a in assignments:
            if a.status == 'APPROVED' and a.approved_at and a.created_at:
                time_diff = (a.approved_at - a.created_at).total_seconds() / 3600  # hours
                assignment_times.append(time_diff)
        
        avg_time_to_assignment = sum(assignment_times) / len(assignment_times) if assignment_times else 0
        
        # Assignment type breakdown
        ptaas_assignments = len([a for a in assignments if a.assignment_type == 'PTAAS'])
        program_assignments = len([a for a in assignments if a.assignment_type == 'PROGRAM'])
        
        # Score distribution
        high_score_matches = len([s for s in match_scores if s >= 80])
        medium_score_matches = len([s for s in match_scores if 60 <= s < 80])
        low_score_matches = len([s for s in match_scores if s < 60])
        
        return {
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'days': (end_date - start_date).days
            },
            'overview': {
                'total_assignments': total_assignments,
                'approved': approved_assignments,
                'rejected': rejected_assignments,
                'pending': pending_assignments
            },
            'success_metrics': {
                'match_success_rate': round(match_success_rate, 2),
                'researcher_acceptance_rate': round(acceptance_rate, 2),
                'average_match_score': round(avg_match_score, 2),
                'average_time_to_assignment_hours': round(avg_time_to_assignment, 2)
            },
            'assignment_breakdown': {
                'ptaas_engagements': ptaas_assignments,
                'bug_bounty_programs': program_assignments
            },
            'score_distribution': {
                'high_score_80_plus': high_score_matches,
                'medium_score_60_79': medium_score_matches,
                'low_score_below_60': low_score_matches
            },
            'trends': self._calculate_matching_trends(
                organization_id,
                start_date,
                end_date
            )
        }
    
    def _calculate_matching_trends(
        self,
        organization_id: Optional[int],
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Calculate trending metrics over time - FREQ-40"""
        from backend.src.domain.models.matching import ResearcherAssignment
        
        # Split period into weeks
        weeks = []
        current_date = start_date
        while current_date < end_date:
            week_end = min(current_date + timedelta(days=7), end_date)
            
            query = self.db.query(ResearcherAssignment).filter(
                ResearcherAssignment.created_at >= current_date,
                ResearcherAssignment.created_at < week_end
            )
            
            if organization_id:
                query = query.filter(ResearcherAssignment.organization_id == organization_id)
            
            week_assignments = query.all()
            week_approved = len([a for a in week_assignments if a.status == 'APPROVED'])
            week_total = len(week_assignments)
            
            weeks.append({
                'week_start': current_date.isoformat(),
                'total_assignments': week_total,
                'approved_assignments': week_approved,
                'success_rate': round((week_approved / week_total * 100) if week_total > 0 else 0, 2)
            })
            
            current_date = week_end
        
        return {
            'weekly_data': weeks,
            'trend_direction': self._determine_trend_direction(weeks)
        }
    
    def _determine_trend_direction(self, weekly_data: List[Dict]) -> str:
        """Determine if metrics are improving, declining, or stable"""
        if len(weekly_data) < 2:
            return 'insufficient_data'
        
        # Compare first half to second half
        mid_point = len(weekly_data) // 2
        first_half_avg = sum(w['success_rate'] for w in weekly_data[:mid_point]) / mid_point if mid_point > 0 else 0
        second_half_avg = sum(w['success_rate'] for w in weekly_data[mid_point:]) / (len(weekly_data) - mid_point)
        
        diff = second_half_avg - first_half_avg
        
        if diff > 5:
            return 'improving'
        elif diff < -5:
            return 'declining'
        else:
            return 'stable'
    
    def get_researcher_matching_stats(
        self,
        researcher_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get matching statistics for specific researcher - FREQ-40.
        
        Shows how well the researcher is being matched to opportunities.
        """
        from backend.src.domain.models.matching import ResearcherAssignment
        
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=90)  # Last 90 days
        
        # Get assignments for researcher
        assignments = self.db.query(ResearcherAssignment).filter(
            ResearcherAssignment.researcher_id == researcher_id,
            ResearcherAssignment.created_at >= start_date,
            ResearcherAssignment.created_at <= end_date
        ).all()
        
        total = len(assignments)
        approved = len([a for a in assignments if a.status == 'APPROVED'])
        rejected = len([a for a in assignments if a.status == 'REJECTED'])
        
        # Calculate acceptance rate
        acceptance_rate = (approved / total * 100) if total > 0 else 0
        
        # Average match score for this researcher
        match_scores = [a.match_score for a in assignments if a.match_score]
        avg_score = sum(match_scores) / len(match_scores) if match_scores else 0
        
        return {
            'researcher_id': researcher_id,
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            },
            'assignments': {
                'total_proposed': total,
                'accepted': approved,
                'rejected': rejected,
                'pending': total - approved - rejected
            },
            'performance': {
                'acceptance_rate': round(acceptance_rate, 2),
                'average_match_score': round(avg_score, 2),
                'match_quality': 'excellent' if avg_score >= 80 else 'good' if avg_score >= 60 else 'fair'
            }
        }
    
    def get_organization_matching_stats(
        self,
        organization_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get matching statistics for specific organization - FREQ-40.
        
        Shows how well researchers are being matched to organization's opportunities.
        """
        metrics = self.get_matching_performance_metrics(
            organization_id,
            start_date,
            end_date
        )
        
        # Add organization-specific insights
        from backend.src.domain.models.matching import MatchingConfiguration
        
        config = self.db.query(MatchingConfiguration).filter(
            MatchingConfiguration.organization_id == organization_id
        ).first()
        
        metrics['configuration'] = {
            'has_custom_config': config is not None,
            'auto_approval_threshold': config.auto_approval_threshold if config else None,
            'minimum_score_threshold': config.minimum_score_threshold if config else None
        }
        
        return metrics
