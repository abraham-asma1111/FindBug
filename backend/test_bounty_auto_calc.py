"""Test bounty auto-calculation from reward tiers."""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy.orm import Session
from src.core.database import SessionLocal
from src.domain.models.report import VulnerabilityReport
from src.domain.models.program import RewardTier
from src.services.triage_service import TriageService

def test_bounty_auto_calculation():
    """Test that bounty is auto-calculated when severity is assigned."""
    db: Session = SessionLocal()
    
    try:
        # Get a report that doesn't have bounty set yet
        report = db.query(VulnerabilityReport).filter(
            VulnerabilityReport.bounty_amount.is_(None),
            VulnerabilityReport.program_id.isnot(None)
        ).first()
        
        if not report:
            print("❌ No reports found without bounty")
            return
        
        print(f"\n📋 Testing with Report: {report.report_number}")
        print(f"   Program ID: {report.program_id}")
        print(f"   Current Bounty: {report.bounty_amount}")
        print(f"   Current Severity: {report.assigned_severity}")
        
        # Check if program has reward tiers
        reward_tiers = db.query(RewardTier).filter(
            RewardTier.program_id == report.program_id
        ).all()
        
        if not reward_tiers:
            print(f"\n⚠️  No reward tiers found for program {report.program_id}")
            print("   Creating test reward tiers...")
            
            # Create test reward tiers
            from uuid import uuid4
            from decimal import Decimal
            
            tiers = [
                RewardTier(
                    id=uuid4(),
                    program_id=report.program_id,
                    severity='critical',
                    min_amount=Decimal('5000'),
                    max_amount=Decimal('10000')
                ),
                RewardTier(
                    id=uuid4(),
                    program_id=report.program_id,
                    severity='high',
                    min_amount=Decimal('2000'),
                    max_amount=Decimal('5000')
                ),
                RewardTier(
                    id=uuid4(),
                    program_id=report.program_id,
                    severity='medium',
                    min_amount=Decimal('500'),
                    max_amount=Decimal('2000')
                ),
                RewardTier(
                    id=uuid4(),
                    program_id=report.program_id,
                    severity='low',
                    min_amount=Decimal('100'),
                    max_amount=Decimal('500')
                ),
            ]
            
            for tier in tiers:
                db.add(tier)
            db.commit()
            
            print("   ✅ Test reward tiers created")
            reward_tiers = tiers
        
        print(f"\n💰 Reward Tiers for Program:")
        for tier in reward_tiers:
            print(f"   {tier.severity.upper()}: {tier.min_amount} - {tier.max_amount} ETB")
        
        # Test auto-calculation by assigning severity
        print(f"\n🔧 Assigning severity 'high' to trigger auto-calculation...")
        
        service = TriageService(db)
        
        # Get triage specialist user
        from src.domain.models.user import User
        triage_user = db.query(User).filter(User.role == 'triage_specialist').first()
        
        if not triage_user:
            print("❌ No triage specialist found in database")
            return
        
        print(f"   Using triage specialist: {triage_user.email}")
        
        # Update triage with severity assignment
        # Don't change status if already valid, just update severity
        new_status = None if report.status == 'valid' else 'triaged'
        
        updated_report = service.update_triage(
            report_id=report.id,
            triage_staff_id=None,  # Will be set by the service
            actor_user_id=triage_user.id,
            actor_role='triage_specialist',
            actor_email=triage_user.email,
            assigned_severity='high',
            status=new_status
        )
        
        print(f"\n✅ Report Updated:")
        print(f"   Assigned Severity: {updated_report.assigned_severity}")
        print(f"   Bounty Amount: {updated_report.bounty_amount} ETB")
        print(f"   Bounty Status: {updated_report.bounty_status}")
        
        if updated_report.bounty_amount:
            print(f"\n🎉 SUCCESS! Bounty auto-calculated from reward tier")
            
            # Verify it matches the reward tier
            high_tier = next((t for t in reward_tiers if t.severity == 'high'), None)
            if high_tier and updated_report.bounty_amount == high_tier.max_amount:
                print(f"   ✅ Bounty matches max_amount of 'high' tier: {high_tier.max_amount} ETB")
            else:
                print(f"   ⚠️  Bounty doesn't match expected tier amount")
        else:
            print(f"\n❌ FAILED! Bounty was not auto-calculated")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 60)
    print("BOUNTY AUTO-CALCULATION TEST")
    print("=" * 60)
    test_bounty_auto_calculation()
    print("\n" + "=" * 60)

