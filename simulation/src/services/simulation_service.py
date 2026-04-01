"""
Simulation Service - FREQ-23, FREQ-24, FREQ-25, FREQ-26, FREQ-27, FREQ-28
"""

from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from uuid import UUID

from src.domain.models.simulation import Simulation, SimulationProgress, SimulationResult
from src.core.exceptions import NotFoundException, ForbiddenException
from src.core.logging import get_logger

logger = get_logger(__name__)

class SimulationService:
    """Service for managing simulation sessions and progress"""
    
    def __init__(self, db: Session):
        self.db = db
        
        # Simulation difficulty levels
        self.difficulty_levels = [
            {"level": "beginner", "name": "Beginner", "time_limit": 3600, "max_hints": 3},
            {"level": "intermediate", "name": "Intermediate", "time_limit": 5400, "max_hints": 2},
            {"level": "advanced", "name": "Advanced", "time_limit": 7200, "max_hints": 1},
            {"level": "expert", "name": "Expert", "time_limit": 10800, "max_hints": 0}
        ]
    
    def start_simulation(
        self,
        user_id: str,
        level: str,
        target_id: str
    ) -> Simulation:
        """
        Start a new simulation session
        FREQ-23: Simulation Environment
        """
        # Validate difficulty level
        valid_levels = [d["level"] for d in self.difficulty_levels]
        if level not in valid_levels:
            raise ValueError(f"Invalid difficulty level. Allowed: {', '.join(valid_levels)}")
        
        # Get difficulty settings
        difficulty = next(d for d in self.difficulty_levels if d["level"] == level)
        
        # Create simulation
        simulation = Simulation(
            user_id=UUID(user_id),
            target_id=UUID(target_id),
            level=level,
            status="active",
            started_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(seconds=difficulty["time_limit"]),
            max_hints=difficulty["max_hints"],
            hints_used=0
        )
        
        self.db.add(simulation)
        self.db.commit()
        self.db.refresh(simulation)
        
        logger.info("Simulation started", extra={
            "simulation_id": str(simulation.id),
            "user_id": user_id,
            "level": level,
            "target_id": target_id
        })
        
        return simulation
    
    def get_simulation(self, simulation_id: str) -> Optional[Simulation]:
        """Get simulation by ID"""
        return self.db.query(Simulation).filter(
            Simulation.id == UUID(simulation_id)
        ).first()
    
    def get_user_simulations(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 20
    ) -> List[Simulation]:
        """Get user's simulation history"""
        return self.db.query(Simulation).filter(
            Simulation.user_id == UUID(user_id)
        ).order_by(Simulation.created_at.desc()).offset(skip).limit(limit).all()
    
    def update_progress(
        self,
        simulation_id: str,
        status: str,
        current_step: int,
        time_spent: int
    ) -> SimulationProgress:
        """
        Update simulation progress
        FREQ-24: Simulation Workflow Mirroring
        """
        simulation = self.get_simulation(simulation_id)
        if not simulation:
            raise NotFoundException("Simulation not found")
        
        # Create or update progress
        progress = self.db.query(SimulationProgress).filter(
            SimulationProgress.simulation_id == UUID(simulation_id)
        ).first()
        
        if not progress:
            progress = SimulationProgress(
                simulation_id=UUID(simulation_id),
                status=status,
                current_step=current_step,
                time_spent=time_spent,
                updated_at=datetime.utcnow()
            )
            self.db.add(progress)
        else:
            progress.status = status
            progress.current_step = current_step
            progress.time_spent = time_spent
            progress.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(progress)
        
        return progress
    
    def submit_result(
        self,
        simulation_id: str,
        findings: List[Dict],
        time_taken: int,
        hints_used: int
    ) -> SimulationResult:
        """
        Submit simulation completion result
        FREQ-26: Simulation Reporting
        """
        simulation = self.get_simulation(simulation_id)
        if not simulation:
            raise NotFoundException("Simulation not found")
        
        # Calculate score based on findings and performance
        score = self._calculate_score(simulation.level, findings, time_taken, hints_used)
        
        # Create result
        result = SimulationResult(
            simulation_id=UUID(simulation_id),
            findings=findings,
            time_taken=time_taken,
            hints_used=hints_used,
            score=score["total"],
            accuracy=score["accuracy"],
            severity_accuracy=score["severity_accuracy"],
            completed_at=datetime.utcnow()
        )
        
        # Update simulation status
        simulation.status = "completed"
        simulation.completed_at = datetime.utcnow()
        
        self.db.add(result)
        self.db.commit()
        self.db.refresh(result)
        
        logger.info("Simulation result submitted", extra={
            "simulation_id": simulation_id,
            "score": score["total"],
            "findings_count": len(findings)
        })
        
        return result
    
    def get_feedback(self, simulation_id: str) -> Dict:
        """
        Get simulation feedback and scoring
        FREQ-28: Simulation Feedback
        """
        result = self.db.query(SimulationResult).filter(
            SimulationResult.simulation_id == UUID(simulation_id)
        ).first()
        
        if not result:
            return None
        
        # Generate detailed feedback
        feedback = {
            "simulation_id": simulation_id,
            "score": result.score,
            "accuracy": result.accuracy,
            "severity_accuracy": result.severity_accuracy,
            "time_taken": result.time_taken,
            "hints_used": result.hints_used,
            "findings_count": len(result.findings),
            "feedback_points": self._generate_feedback_points(result),
            "improvement_tips": self._generate_improvement_tips(result)
        }
        
        return feedback
    
    def delete_simulation(self, simulation_id: str) -> bool:
        """Delete simulation session"""
        simulation = self.get_simulation(simulation_id)
        if not simulation:
            return False
        
        self.db.delete(simulation)
        self.db.commit()
        
        logger.info("Simulation deleted", extra={"simulation_id": simulation_id})
        return True
    
    def get_available_levels(self) -> List[Dict]:
        """
        Get available simulation levels
        FREQ-25: Simulation Difficulty Levels
        """
        return self.difficulty_levels
    
    def _calculate_score(
        self,
        level: str,
        findings: List[Dict],
        time_taken: int,
        hints_used: int
    ) -> Dict:
        """Calculate simulation score based on performance"""
        # Base score for difficulty
        difficulty_scores = {
            "beginner": 100,
            "intermediate": 200,
            "advanced": 300,
            "expert": 500
        }
        
        base_score = difficulty_scores.get(level, 100)
        
        # Time bonus/penalty
        time_scores = {
            "beginner": 3600,
            "intermediate": 5400,
            "advanced": 7200,
            "expert": 10800
        }
        target_time = time_scores.get(level, 3600)
        
        time_ratio = time_taken / target_time if target_time > 0 else 1
        time_bonus = max(0, (1 - time_ratio) * 50) if time_ratio < 1 else min(-50, (time_ratio - 1) * -30)
        
        # Hint penalty
        hint_penalty = hints_used * 10
        
        # Findings quality
        valid_findings = [f for f in findings if f.get("valid", False)]
        accuracy = len(valid_findings) / len(findings) if findings else 0
        
        # Severity accuracy
        severity_accuracy = self._calculate_severity_accuracy(findings)
        
        total_score = base_score + time_bonus - hint_penalty + (accuracy * 100)
        
        return {
            "total": max(0, int(total_score)),
            "base_score": base_score,
            "time_bonus": int(time_bonus),
            "hint_penalty": -hint_penalty,
            "accuracy": accuracy,
            "severity_accuracy": severity_accuracy
        }
    
    def _calculate_severity_accuracy(self, findings: List[Dict]) -> float:
        """Calculate severity accuracy for findings"""
        if not findings:
            return 0.0
        
        correct_severity = sum(1 for f in findings if f.get("severity_correct", False))
        return correct_severity / len(findings)
    
    def _generate_feedback_points(self, result: SimulationResult) -> List[str]:
        """Generate feedback points based on performance"""
        feedback = []
        
        if result.accuracy >= 0.9:
            feedback.append("Excellent accuracy! You found most vulnerabilities.")
        elif result.accuracy >= 0.7:
            feedback.append("Good accuracy. Keep practicing to improve.")
        else:
            feedback.append("Work on identifying valid vulnerabilities more accurately.")
        
        if result.severity_accuracy >= 0.8:
            feedback.append("Great severity assessment!")
        else:
            feedback.append("Focus on understanding vulnerability severity levels.")
        
        if result.hints_used == 0:
            feedback.append("Completed without hints - impressive!")
        elif result.hints_used <= 2:
            feedback.append("Good use of hints.")
        else:
            feedback.append("Try to use fewer hints for better scores.")
        
        return feedback
    
    def _generate_improvement_tips(self, result: SimulationResult) -> List[str]:
        """Generate improvement tips based on performance"""
        tips = []
        
        if result.accuracy < 0.8:
            tips.append("Study common vulnerability patterns and false positives.")
        
        if result.severity_accuracy < 0.7:
            tips.append("Review CVSS scoring and vulnerability classification.")
        
        if result.time_taken > 7200:  # 2 hours
            tips.append("Practice systematic testing approaches to improve speed.")
        
        if result.hints_used > 3:
            tips.append("Try to solve challenges independently before using hints.")
        
        return tips
