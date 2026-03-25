"""
Simulation Service
Business logic for simulation platform
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import List, Optional, Dict
from datetime import datetime

from src.domain.models.simulation import (
    SimulationChallenge,
    SimulationProgress,
    SimulationReport,
    SimulationSolution,
    SimulationLeaderboard
)


class SimulationService:
    """Handles simulation platform business logic"""
    
    async def get_challenges(
        self,
        db: Session,
        difficulty: Optional[str] = None,
        severity: Optional[str] = None,
        category: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[SimulationChallenge]:
        """Get challenges with filters"""
        query = db.query(SimulationChallenge).filter(
            SimulationChallenge.is_active == True,
            SimulationChallenge.is_published == True
        )
        
        if difficulty:
            query = query.filter(SimulationChallenge.difficulty_level == difficulty)
        
        if severity:
            query = query.filter(SimulationChallenge.severity == severity)
        
        if category:
            query = query.filter(SimulationChallenge.category == category)
        
        return query.offset(skip).limit(limit).all()
    
    async def get_challenge_details(
        self,
        db: Session,
        challenge_id: str,
        user_id: Optional[str] = None
    ) -> Dict:
        """Get challenge details with resources and community solutions"""
        challenge = db.query(SimulationChallenge).filter(
            SimulationChallenge.id == challenge_id
        ).first()
        
        if not challenge:
            raise Exception("Challenge not found")
        
        # Get user progress if authenticated
        user_progress = None
        if user_id:
            user_progress = db.query(SimulationProgress).filter(
                SimulationProgress.user_id == user_id,
                SimulationProgress.challenge_id == challenge_id
            ).first()
        
        # Get community solutions (approved only)
        solutions = db.query(SimulationSolution).filter(
            SimulationSolution.challenge_id == challenge_id,
            SimulationSolution.is_approved == True
        ).order_by(SimulationSolution.likes_count.desc()).limit(10).all()
        
        return {
            'challenge': challenge,
            'user_progress': user_progress,
            'community_solutions': solutions
        }
    
    async def submit_report(
        self,
        db: Session,
        user_id: str,
        challenge_id: str,
        report_data: dict
    ) -> Dict:
        """Submit a simulation report and get automated feedback"""
        challenge = db.query(SimulationChallenge).filter(
            SimulationChallenge.id == challenge_id
        ).first()
        
        if not challenge:
            raise Exception("Challenge not found")
        
        # Create report
        report = SimulationReport(
            user_id=user_id,
            challenge_id=challenge_id,
            title=report_data['title'],
            description=report_data['description'],
            steps_to_reproduce=report_data['steps_to_reproduce'],
            impact_assessment=report_data.get('impact_assessment', ''),
            suggested_severity=report_data.get('suggested_severity'),
            proof_of_concept=report_data.get('proof_of_concept', ''),
            submitted_at=datetime.utcnow()
        )
        
        # Validate report and generate feedback
        validation_result = self._validate_report(report, challenge)
        
        report.is_correct = validation_result['is_correct']
        report.feedback = validation_result['feedback']
        report.points_awarded = validation_result['points_awarded']
        report.status = "validated"
        report.validated_at = datetime.utcnow()
        
        db.add(report)
        
        # Update user progress
        progress = db.query(SimulationProgress).filter(
            SimulationProgress.user_id == user_id,
            SimulationProgress.challenge_id == challenge_id
        ).first()
        
        if not progress:
            progress = SimulationProgress(
                user_id=user_id,
                challenge_id=challenge_id,
                status="in_progress"
            )
            db.add(progress)
        
        progress.attempts += 1
        
        if validation_result['is_correct']:
            progress.status = "completed"
            progress.completed_at = datetime.utcnow()
            
            # Update leaderboard
            await self._update_leaderboard(db, user_id, validation_result['points_awarded'])
            
            # Update challenge stats
            challenge.total_completions += 1
        
        challenge.total_attempts += 1
        challenge.success_rate = (challenge.total_completions / challenge.total_attempts) * 100
        
        db.commit()
        
        return {
            'report_id': str(report.id),
            'is_correct': report.is_correct,
            'feedback': report.feedback,
            'points_awarded': report.points_awarded,
            'status': report.status
        }
    
    def _validate_report(
        self,
        report: SimulationReport,
        challenge: SimulationChallenge
    ) -> Dict:
        """Automated report validation"""
        feedback_items = []
        points = 0
        
        # Check vulnerability type
        if challenge.expected_vulnerability_type:
            if challenge.expected_vulnerability_type.lower() in report.description.lower():
                feedback_items.append("✓ Correct vulnerability type identified")
                points += 20
            else:
                feedback_items.append("✗ Vulnerability type not correctly identified")
        
        # Check PoC
        if report.proof_of_concept and len(report.proof_of_concept) > 20:
            feedback_items.append("✓ Proof of concept provided")
            points += 30
        else:
            feedback_items.append("⚠ Consider adding a detailed proof of concept")
        
        # Check severity
        if report.suggested_severity == challenge.expected_severity:
            feedback_items.append("✓ Correct severity assessment")
            points += 20
        else:
            feedback_items.append(f"⚠ Expected severity: {challenge.expected_severity}")
        
        # Check impact assessment
        if report.impact_assessment and len(report.impact_assessment) > 100:
            feedback_items.append("✓ Detailed impact assessment")
            points += 15
        else:
            feedback_items.append("⚠ Impact assessment could be more detailed")
        
        # Check steps to reproduce
        if len(report.steps_to_reproduce) > 50:
            feedback_items.append("✓ Clear reproduction steps")
            points += 15
        else:
            feedback_items.append("⚠ Reproduction steps need more detail")
        
        # Check validation keywords
        if challenge.validation_keywords:
            keywords_found = sum(
                1 for keyword in challenge.validation_keywords
                if keyword.lower() in report.description.lower()
            )
            if keywords_found >= len(challenge.validation_keywords) * 0.5:
                points += 10
        
        # Determine if correct (70% threshold)
        is_correct = points >= (challenge.points * 0.7)
        points_awarded = challenge.points if is_correct else 0
        
        feedback = "\n".join(feedback_items)
        
        return {
            'is_correct': is_correct,
            'points_awarded': points_awarded,
            'feedback': feedback
        }
    
    async def _update_leaderboard(
        self,
        db: Session,
        user_id: str,
        points: int
    ):
        """Update user's leaderboard entry"""
        leaderboard = db.query(SimulationLeaderboard).filter(
            SimulationLeaderboard.user_id == user_id
        ).first()
        
        if not leaderboard:
            leaderboard = SimulationLeaderboard(user_id=user_id)
            db.add(leaderboard)
        
        leaderboard.total_points += points
        leaderboard.challenges_completed += 1
        leaderboard.last_updated = datetime.utcnow()
        
        # Recalculate ranks (simple approach)
        all_entries = db.query(SimulationLeaderboard).order_by(
            SimulationLeaderboard.total_points.desc()
        ).all()
        
        for rank, entry in enumerate(all_entries, start=1):
            entry.rank = rank
        
        db.commit()
    
    async def submit_solution(
        self,
        db: Session,
        user_id: str,
        challenge_id: str,
        solution_data: dict
    ) -> SimulationSolution:
        """Submit a community solution"""
        solution = SimulationSolution(
            challenge_id=challenge_id,
            user_id=user_id,
            title=solution_data['title'],
            content=solution_data['content'],
            video_url=solution_data.get('video_url'),
            is_approved=False  # Requires moderation
        )
        
        db.add(solution)
        db.commit()
        db.refresh(solution)
        
        return solution
    
    async def get_leaderboard(
        self,
        db: Session,
        limit: int = 100
    ) -> List[SimulationLeaderboard]:
        """Get simulation leaderboard"""
        return db.query(SimulationLeaderboard).order_by(
            SimulationLeaderboard.rank
        ).limit(limit).all()
