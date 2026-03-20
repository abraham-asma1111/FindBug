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
