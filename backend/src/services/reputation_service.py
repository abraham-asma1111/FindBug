"""Reputation Service - FREQ-11, BR-09."""
from typing import List, Optional
from uuid import UUID
from decimal import Decimal

from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from src.domain.models.researcher import Researcher
from src.domain.models.report import VulnerabilityReport
from src.domain.repositories.researcher_repository import ResearcherRepository


class ReputationService:
    """Service for researcher reputation and leaderboard operations."""
    
    def __init__(self, db: Session):
        self.db = db
        self.researcher_repo = ResearcherRepository(db)
    
    # BR-09: Reputation scoring rules
    REPUTATION_POINTS = {
        'critical': 50,  # Critical severity
        'high': 30,      # High severity
        'medium': 20,    # Medium severity
        'low': 10,       # Low severity
        'invalid': -20,  # Invalid report penalty
        'duplicate': -20 # Duplicate report penalty (after 24h)
    }
    
    def calculate_points_for_report(
        self,
        report: VulnerabilityReport
    ) -> int:
        """
        Calculate reputation points for a report - BR-09.
        
        Rules:
        - Valid reports: 10-50 points based on severity
        - Invalid reports: -20 points
        - Duplicate reports: -20 points (if after 24 hours)
        """
        # Invalid reports
        if report.status == 'invalid':
            return self.REPUTATION_POINTS['invalid']
        
        # Duplicate reports
        if report.is_duplicate:
            # Check if within 24 hours (gets 50% bounty but no penalty)
            if report.duplicate_of:
                original = self.db.query(VulnerabilityReport).filter(
                    VulnerabilityReport.id == report.duplicate_of
                ).first()
                
                if original:
                    time_diff = report.submitted_at - original.submitted_at
                    within_24_hours = time_diff.total_seconds() <= 86400
                    
                    if within_24_hours:
                        # No penalty for duplicates within 24h
                        return 0
            
            # Penalty for duplicates after 24h
            return self.REPUTATION_POINTS['duplicate']
        
        # Valid reports - points based on assigned severity
        if report.status in ['valid', 'resolved'] and report.assigned_severity:
            return self.REPUTATION_POINTS.get(report.assigned_severity, 0)
        
        # No points for other statuses (new, triaged)
        return 0
    
    def update_reputation(
        self,
        researcher_id: UUID,
        report: VulnerabilityReport
    ) -> Researcher:
        """
        Update researcher reputation based on report - BR-09.
        
        Called when report status changes to valid/invalid/duplicate.
        """
        researcher = self.researcher_repo.get_by_id(researcher_id)
        
        if not researcher:
            raise ValueError("Researcher not found")
        
        # Calculate points
        points = self.calculate_points_for_report(report)
        
        # Update reputation score
        current_score = researcher.reputation_score or Decimal('0')
        new_score = current_score + Decimal(str(points))
        
        # Ensure score doesn't go below 0
        researcher.reputation_score = max(Decimal('0'), new_score)
        
        # Update total earnings if bounty was paid
        if report.bounty_status == 'paid' and report.bounty_amount:
            current_earnings = researcher.total_earnings or Decimal('0')
            researcher.total_earnings = current_earnings + report.bounty_amount
        
        self.db.commit()
        self.db.refresh(researcher)
        
        # Update rankings
        self._update_rankings()
        
        return researcher
    
    def _update_rankings(self):
        """
        Update researcher rankings based on reputation scores.
        
        Ranks all researchers by reputation score (highest first).
        """
        # Get all researchers ordered by reputation
        researchers = self.db.query(Researcher).order_by(
            desc(Researcher.reputation_score)
        ).all()
        
        # Assign ranks
        for rank, researcher in enumerate(researchers, start=1):
            researcher.rank = rank
        
        self.db.commit()
    
    def get_leaderboard(
        self,
        limit: int = 10,
        offset: int = 0
    ) -> List[dict]:
        """
        Get public leaderboard - FREQ-11, BR-09.
        
        Shows top researchers by reputation score.
        Default: Top 10 researchers.
        """
        researchers = self.db.query(Researcher).order_by(
            desc(Researcher.reputation_score)
        ).offset(offset).limit(limit).all()
        
        leaderboard = []
        for researcher in researchers:
            # Get statistics
            stats = self._get_researcher_stats(researcher.id)
            
            leaderboard.append({
                'rank': researcher.rank,
                'researcher_id': str(researcher.id),
                'username': researcher.username or 'Anonymous',
                'reputation_score': float(researcher.reputation_score or 0),
                'total_earnings': float(researcher.total_earnings or 0),
                'stats': stats
            })
        
        return leaderboard
    
    def get_researcher_profile(
        self,
        researcher_id: UUID
    ) -> dict:
        """
        Get researcher public profile with reputation - FREQ-11.
        
        Shows reputation, rank, earnings, and statistics.
        """
        researcher = self.researcher_repo.get_by_id(researcher_id)
        
        if not researcher:
            raise ValueError("Researcher not found")
        
        stats = self._get_researcher_stats(researcher_id)
        
        return {
            'researcher_id': str(researcher.id),
            'username': researcher.username or 'Anonymous',
            'bio': researcher.bio,
            'reputation_score': float(researcher.reputation_score or 0),
            'rank': researcher.rank,
            'total_earnings': float(researcher.total_earnings or 0),
            'stats': stats,
            'social': {
                'website': researcher.website,
                'github': researcher.github,
                'twitter': researcher.twitter,
                'linkedin': researcher.linkedin
            }
        }
    
    def _get_researcher_stats(
        self,
        researcher_id: UUID
    ) -> dict:
        """Get researcher statistics."""
        # Total reports
        total_reports = self.db.query(VulnerabilityReport).filter(
            VulnerabilityReport.researcher_id == researcher_id
        ).count()
        
        # Valid reports
        valid_reports = self.db.query(VulnerabilityReport).filter(
            VulnerabilityReport.researcher_id == researcher_id,
            VulnerabilityReport.status.in_(['valid', 'resolved'])
        ).count()
        
        # Invalid reports
        invalid_reports = self.db.query(VulnerabilityReport).filter(
            VulnerabilityReport.researcher_id == researcher_id,
            VulnerabilityReport.status == 'invalid'
        ).count()
        
        # Duplicate reports
        duplicate_reports = self.db.query(VulnerabilityReport).filter(
            VulnerabilityReport.researcher_id == researcher_id,
            VulnerabilityReport.is_duplicate == True
        ).count()
        
        # Reports by severity
        critical = self.db.query(VulnerabilityReport).filter(
            VulnerabilityReport.researcher_id == researcher_id,
            VulnerabilityReport.assigned_severity == 'critical'
        ).count()
        
        high = self.db.query(VulnerabilityReport).filter(
            VulnerabilityReport.researcher_id == researcher_id,
            VulnerabilityReport.assigned_severity == 'high'
        ).count()
        
        medium = self.db.query(VulnerabilityReport).filter(
            VulnerabilityReport.researcher_id == researcher_id,
            VulnerabilityReport.assigned_severity == 'medium'
        ).count()
        
        low = self.db.query(VulnerabilityReport).filter(
            VulnerabilityReport.researcher_id == researcher_id,
            VulnerabilityReport.assigned_severity == 'low'
        ).count()
        
        # Calculate success rate
        success_rate = (valid_reports / total_reports * 100) if total_reports > 0 else 0
        
        return {
            'total_reports': total_reports,
            'valid_reports': valid_reports,
            'invalid_reports': invalid_reports,
            'duplicate_reports': duplicate_reports,
            'success_rate': round(success_rate, 2),
            'by_severity': {
                'critical': critical,
                'high': high,
                'medium': medium,
                'low': low
            }
        }
    
    def get_researcher_rank(
        self,
        researcher_id: UUID
    ) -> dict:
        """
        Get researcher's current rank and percentile.
        """
        researcher = self.researcher_repo.get_by_id(researcher_id)
        
        if not researcher:
            raise ValueError("Researcher not found")
        
        # Total researchers
        total_researchers = self.db.query(Researcher).count()
        
        # Calculate percentile
        percentile = 0
        if researcher.rank and total_researchers > 0:
            percentile = ((total_researchers - researcher.rank + 1) / total_researchers) * 100
        
        return {
            'rank': researcher.rank,
            'total_researchers': total_researchers,
            'percentile': round(percentile, 2),
            'reputation_score': float(researcher.reputation_score or 0)
        }
    
    def get_top_earners(
        self,
        limit: int = 10
    ) -> List[dict]:
        """
        Get top earners leaderboard.
        
        Alternative leaderboard based on total earnings.
        """
        researchers = self.db.query(Researcher).order_by(
            desc(Researcher.total_earnings)
        ).limit(limit).all()
        
        return [
            {
                'rank': idx + 1,
                'researcher_id': str(r.id),
                'username': r.username or 'Anonymous',
                'total_earnings': float(r.total_earnings or 0),
                'reputation_score': float(r.reputation_score or 0)
            }
            for idx, r in enumerate(researchers)
        ]
