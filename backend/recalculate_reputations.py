#!/usr/bin/env python3
"""
Recalculate reputation scores for all researchers based on their existing reports.
Run this after updating the reputation system to backfill scores.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from src.core.database import SessionLocal
from src.domain.models.researcher import Researcher
from src.domain.models.report import VulnerabilityReport
from src.services.reputation_service import ReputationService


def recalculate_all_reputations():
    """Recalculate reputation for all researchers based on their reports."""
    db: Session = SessionLocal()
    
    try:
        reputation_service = ReputationService(db)
        
        # Get all researchers
        researchers = db.query(Researcher).all()
        
        print(f"Found {len(researchers)} researchers")
        print("=" * 80)
        
        for researcher in researchers:
            print(f"\nProcessing: {researcher.username} ({researcher.user.email})")
            
            # Reset reputation to 0
            researcher.reputation_score = 0
            
            # Get all reports for this researcher
            reports = db.query(VulnerabilityReport).filter(
                VulnerabilityReport.researcher_id == researcher.id
            ).all()
            
            print(f"  Found {len(reports)} reports")
            
            total_points = 0
            
            # Calculate points for each report
            for report in reports:
                points = reputation_service.calculate_points_for_report(report)
                if points != 0:
                    print(f"    {report.report_number}: {report.status} / {report.assigned_severity or report.suggested_severity} = {points} pts")
                total_points += points
            
            # Update reputation
            researcher.reputation_score = max(0, total_points)
            print(f"  Total reputation: {researcher.reputation_score}")
        
        # Commit all changes
        db.commit()
        
        # Update rankings
        print("\n" + "=" * 80)
        print("Updating rankings...")
        reputation_service._update_rankings()
        
        print("\n" + "=" * 80)
        print("FINAL RESULTS:")
        print("=" * 80)
        
        # Show final leaderboard
        researchers = db.query(Researcher).order_by(
            Researcher.reputation_score.desc()
        ).all()
        
        for researcher in researchers:
            print(f"Rank {researcher.rank}: {researcher.username} - {researcher.reputation_score} pts")
        
        print("\n✅ Reputation recalculation complete!")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    recalculate_all_reputations()
